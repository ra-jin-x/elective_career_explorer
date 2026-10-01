"""
Fallback Workflow Engine.
Provides deterministic, structured remediation paths and advisor escalation protocols
when a student faces unmet prerequisites, scheduling bottlenecks, or pacing mismatches.
"""
from typing import Dict, List, Optional
import pandas as pd
from engine.dag_resolver import PrerequisiteDAGResolver
from engine.schedule_detector import ScheduleConflictDetector


class FallbackWorkflowHandler:
    def __init__(
        self,
        dag_resolver: PrerequisiteDAGResolver,
        schedule_detector: ScheduleConflictDetector,
        courses_df: pd.DataFrame
    ):
        self.dag = dag_resolver
        self.scheduler = schedule_detector
        self.courses_df = courses_df.copy()
        self.course_names = dict(zip(self.courses_df["course_id"], self.courses_df["course_name"]))

    def resolve_prerequisite_deficit(
        self,
        target_course_id: str,
        completed_courses: List[str],
        gpa: float = 3.0,
        learning_speed: str = "standard"
    ) -> Dict:
        """
        Determines the appropriate fallback action for unfulfilled prerequisites.
        Outcomes:
        1. Direct Bridge Pathway: Suggests immediate ancestral prerequisite courses to take first.
        2. Accelerated Waiver Option: If student has high GPA (>= 3.7) and >= 50% partial readiness.
        3. Supported Co-Requisite Tutoring: For supported learners with soft prerequisites missing.
        """
        eval_res = self.dag.check_prerequisites(target_course_id, completed_courses)
        course_name = self.dag.get_course_name(target_course_id)
        
        hard_missing = eval_res["hard_missing"]
        soft_missing = eval_res["soft_missing"]
        readiness = eval_res["readiness_score"]

        # If already fully valid
        if eval_res["valid"] and not soft_missing:
            return {
                "action": "Proceed with Standard Enrollment",
                "target_course": f"{target_course_id} - {course_name}",
                "status": "Ready",
                "remediation_plan": "No fallback required; prerequisites satisfied.",
                "requires_advisor_signoff": False
            }

        # Case 1: Waiver Review for high performers with partial prerequisites
        if readiness >= 35.0 and gpa >= 3.7 and learning_speed == "accelerated":
            return {
                "action": "Prerequisite Waiver Expedited Review",
                "target_course": f"{target_course_id} - {course_name}",
                "status": "Escalated to Academic Dean",
                "remediation_plan": (
                    f"Student has GPA {gpa} and partial prerequisite readiness ({readiness}%). "
                    f"Eligible to request concurrent independent study waiver for missing courses: "
                    f"{', '.join(eval_res['hard_missing_names'])}."
                ),
                "requires_advisor_signoff": True,
                "recommended_bridge_courses": eval_res["hard_missing_names"]
            }

        # Case 2: Co-requisite Academic Support
        if eval_res["valid"] and soft_missing:
            return {
                "action": "Enroll with Co-Requisite Tutoring Module",
                "target_course": f"{target_course_id} - {course_name}",
                "status": "Conditional Approval",
                "remediation_plan": (
                    f"Hard prerequisites are met, but recommended background courses are missing: "
                    f"{', '.join(eval_res['soft_missing_names'])}. Assign weekly 2-hour lab support."
                ),
                "requires_advisor_signoff": False,
                "recommended_bridge_courses": eval_res["soft_missing_names"]
            }

        # Case 3: Bridge Pathway (Standard Fallback)
        # Find the immediate prerequisite course that the student CAN take right now
        bridge_candidates = []
        for m_cid in hard_missing:
            sub_eval = self.dag.check_prerequisites(m_cid, completed_courses)
            bridge_candidates.append({
                "course_id": m_cid,
                "course_name": self.dag.get_course_name(m_cid),
                "ready_now": sub_eval["valid"]
            })

        immediate_action = [b["course_name"] for b in bridge_candidates if b["ready_now"]]
        if not immediate_action:
            immediate_action = [b["course_name"] for b in bridge_candidates]

        return {
            "action": "Prerequisite Staging Fallback",
            "target_course": f"{target_course_id} - {course_name}",
            "status": "Prerequisite Roadblock",
            "remediation_plan": (
                f"Course requires foundational competencies. Take prerequisite "
                f"course '{immediate_action[0]}' in the upcoming semester before taking {course_name}."
            ),
            "requires_advisor_signoff": False,
            "recommended_bridge_courses": immediate_action
        }

    def resolve_schedule_conflict(
        self,
        target_course_id: str,
        selected_courses: List[str]
    ) -> Dict:
        """
        Determines schedule resolution options:
        1. Alternative section check (or asynchronous equivalent).
        2. Trade-off prioritization between conflicting courses.
        """
        conflicts = self.scheduler.find_conflicts_for_course(target_course_id, selected_courses)
        course_name = self.dag.get_course_name(target_course_id)

        if not conflicts:
            return {
                "action": "Schedule Compatible",
                "target_course": f"{target_course_id} - {course_name}",
                "conflicts": [],
                "resolution": "No timetable collision detected."
            }

        conflicting_names = [c["course_2_name"] for c in conflicts]
        return {
            "action": "Timetable Deconfliction Workflow",
            "target_course": f"{target_course_id} - {course_name}",
            "conflicts": conflicting_names,
            "resolution": (
                f"Direct conflict on {conflicts[0]['day']} ({conflicts[0]['overlap_minutes']} min overlap) "
                f"with {', '.join(conflicting_names)}. Fallback option: Shift '{conflicting_names[0]}' "
                f"to next term or select asynchronous course C20 (Project Management) to maintain credit pace."
            )
        }
