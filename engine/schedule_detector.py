"""
Schedule Conflict Detector.
Handles timetable interval algebra, overlap detection, room constraints,
delivery mode exceptions (e.g. Asynchronous Online), and schedule friction penalties.
"""
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pandas as pd


class ScheduleConflictDetector:
    def __init__(self, schedules_df: pd.DataFrame, courses_df: pd.DataFrame):
        self.schedules_df = schedules_df.copy()
        self.courses_df = courses_df.copy()
        self.course_names = dict(zip(self.courses_df["course_id"], self.courses_df["course_name"]))
        
        # Build lookup table by course_id
        self.schedule_lookup: Dict[str, Dict] = {}
        for _, row in self.schedules_df.iterrows():
            cid = str(row["course_id"]).strip()
            self.schedule_lookup[cid] = {
                "course_id": cid,
                "day": str(row.get("day", "")).strip(),
                "start_time": str(row.get("start_time", "")).strip(),
                "end_time": str(row.get("end_time", "")).strip(),
                "room": str(row.get("room", "")).strip(),
                "delivery_mode": str(row.get("delivery_mode", "In-Person")).strip()
            }

    def get_course_name(self, course_id: str) -> str:
        return self.course_names.get(course_id, course_id)

    def get_schedule(self, course_id: str) -> Optional[Dict]:
        return self.schedule_lookup.get(course_id)

    def is_asynchronous(self, course_id: str) -> bool:
        sched = self.get_schedule(course_id)
        if not sched:
            return True
        return sched["delivery_mode"].lower() == "asynchronous" or sched["day"].lower() == "online"

    def check_conflict_pair(self, course_a: str, course_b: str) -> Tuple[bool, Optional[Dict]]:
        """
        Interval comparison between two courses.
        Returns (has_conflict, conflict_details).
        """
        if course_a == course_b:
            return False, None

        sched_a = self.get_schedule(course_a)
        sched_b = self.get_schedule(course_b)

        if not sched_a or not sched_b:
            return False, None

        # Asynchronous or online courses do not conflict with anything
        if self.is_asynchronous(course_a) or self.is_asynchronous(course_b):
            return False, None

        # Different days cannot conflict
        if sched_a["day"].lower() != sched_b["day"].lower():
            return False, None

        try:
            start_a = datetime.strptime(sched_a["start_time"], "%H:%M")
            end_a = datetime.strptime(sched_a["end_time"], "%H:%M")
            start_b = datetime.strptime(sched_b["start_time"], "%H:%M")
            end_b = datetime.strptime(sched_b["end_time"], "%H:%M")

            # Overlap occurs iff start_a < end_b and start_b < end_a
            if start_a < end_b and start_b < end_a:
                overlap_start = max(start_a, start_b)
                overlap_end = min(end_a, end_b)
                overlap_minutes = int((overlap_end - overlap_start).total_seconds() / 60)

                return True, {
                    "course_1_id": course_a,
                    "course_1_name": self.get_course_name(course_a),
                    "course_2_id": course_b,
                    "course_2_name": self.get_course_name(course_b),
                    "day": sched_a["day"],
                    "time_a": f"{sched_a['start_time']} - {sched_a['end_time']}",
                    "time_b": f"{sched_b['start_time']} - {sched_b['end_time']}",
                    "overlap_minutes": overlap_minutes
                }
        except Exception:
            return False, None

        return False, None

    def find_conflicts_for_course(self, target_course: str, selected_courses: List[str]) -> List[Dict]:
        """
        Checks if target_course conflicts with any already selected course.
        """
        conflicts = []
        for selected in selected_courses:
            if selected == target_course:
                continue
            has_conflict, details = self.check_conflict_pair(target_course, selected)
            if has_conflict and details:
                conflicts.append(details)
        return conflicts

    def find_all_pairwise_conflicts(self, course_list: List[str]) -> List[Dict]:
        """
        Checks all pairwise conflicts within a course list.
        """
        all_conflicts = []
        n = len(course_list)
        for i in range(n):
            for j in range(i + 1, n):
                has_conflict, details = self.check_conflict_pair(course_list[i], course_list[j])
                if has_conflict and details:
                    all_conflicts.append(details)
        return all_conflicts

    def calculate_schedule_penalty(self, target_course: str, selected_courses: List[str]) -> float:
        """
        Returns schedule conflict penalty Pi_conflict(c).
        100.0 for direct hard time collision, 0.0 for conflict-free.
        """
        conflicts = self.find_conflicts_for_course(target_course, selected_courses)
        if conflicts:
            return 100.0
        return 0.0
