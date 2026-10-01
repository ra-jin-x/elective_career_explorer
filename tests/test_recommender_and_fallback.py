"""
Unit tests for CourseRecommender and FallbackWorkflowHandler.
Tests multi-stakeholder Pareto weighting, learning speed pacing adaptation,
composite scoring edge cases, and advisor fallback escalation.
"""
import unittest
import pandas as pd
from engine.dag_resolver import PrerequisiteDAGResolver
from engine.schedule_detector import ScheduleConflictDetector
from engine.recommender import CourseRecommender
from engine.fallback import FallbackWorkflowHandler


class TestRecommenderAndFallback(unittest.TestCase):
    def setUp(self):
        self.courses_df = pd.read_csv("data/courses.csv")
        self.prereqs_df = pd.read_csv("data/prerequisites.csv")
        self.schedules_df = pd.read_csv("data/schedules.csv")
        self.career_df = pd.read_csv("data/career_pathways.csv")
        self.outcomes_df = pd.read_csv("data/course_outcomes.csv")

        self.dag = PrerequisiteDAGResolver(self.courses_df, self.prereqs_df)
        self.scheduler = ScheduleConflictDetector(self.schedules_df, self.courses_df)
        self.recommender = CourseRecommender(
            self.courses_df, self.career_df, self.outcomes_df, self.dag, self.scheduler
        )
        self.fallback = FallbackWorkflowHandler(self.dag, self.scheduler, self.courses_df)

    def test_learning_speed_adaptation_pacing_scores(self):
        """
        Verify that learning speed appropriately weights difficulty:
        - Accelerated learner taking Hard course (C08) gets pacing score 100
        - Supported learner taking Hard course (C08) gets pacing score 40
        """
        score_acc = self.recommender.calculate_composite_score(
            course_id="C08", career_goal="AI Engineer", completed_courses=["C01", "C07"], learning_speed="accelerated"
        )
        score_sup = self.recommender.calculate_composite_score(
            course_id="C08", career_goal="AI Engineer", completed_courses=["C01", "C07"], learning_speed="supported"
        )
        self.assertEqual(score_acc["components"]["L_pace"], 100.0)
        self.assertEqual(score_sup["components"]["L_pace"], 40.0)
        self.assertGreater(score_acc["final_score"], score_sup["final_score"])

    def test_stakeholder_trade_off_weights(self):
        """
        Verify Pareto slider weights:
        - theta=0.0 (Student Career Ambition) yields w_career=0.50, w_prereq=0.20
        - theta=1.0 (Advisor Academic Prudence) yields w_career=0.15, w_prereq=0.45
        """
        w_student = self.recommender.compute_stakeholder_weights(trade_off_ratio=0.0)
        self.assertEqual(w_student["w_career"], 0.50)
        self.assertEqual(w_student["w_prereq"], 0.20)

        w_advisor = self.recommender.compute_stakeholder_weights(trade_off_ratio=1.0)
        self.assertEqual(w_advisor["w_career"], 0.15)
        self.assertEqual(w_advisor["w_prereq"], 0.45)

    def test_schedule_conflict_penalty_suppresses_rank(self):
        """A course with an active schedule clash should receive Pi_conflict = 100 and status 'Schedule Conflict'."""
        eval_clash = self.recommender.calculate_composite_score(
            course_id="C03",  # Monday 09:00 - 10:30
            career_goal="Software Developer",
            completed_courses=["C01"],
            learning_speed="standard",
            selected_courses=["C01"]  # Also Monday 09:00 - 10:30
        )
        self.assertEqual(eval_clash["components"]["Pi_conflict"], 100.0)
        self.assertEqual(eval_clash["final_score"], 0.0)
        self.assertEqual(eval_clash["status"], "Schedule Conflict")

    def test_fallback_generates_actionable_bridge(self):
        """When a student attempts to take C08 without C01 and C07, fallback should identify bridge courses."""
        fallback_res = self.fallback.resolve_prerequisite_deficit(
            target_course_id="C08", completed_courses=[], gpa=3.0, learning_speed="standard"
        )
        self.assertEqual(fallback_res["status"], "Prerequisite Roadblock")
        self.assertTrue(len(fallback_res["recommended_bridge_courses"]) > 0)

    def test_fallback_accelerated_waiver_escalation(self):
        """High GPA accelerated student with partial prerequisites should trigger waiver review."""
        fallback_res = self.fallback.resolve_prerequisite_deficit(
            target_course_id="C08", completed_courses=["C01"], gpa=3.9, learning_speed="accelerated"
        )
        self.assertEqual(fallback_res["status"], "Escalated to Academic Dean")
        self.assertTrue(fallback_res["requires_advisor_signoff"])


if __name__ == "__main__":
    unittest.main()
