"""
Unit tests for PrerequisiteDAGResolver.
Tests DAG structure, cycle detection, transitive prerequisites,
non-binary partial fulfillment scores, and boundary edge cases.
"""
import unittest
import pandas as pd
from engine.dag_resolver import PrerequisiteDAGResolver


class TestPrerequisiteDAGResolver(unittest.TestCase):
    def setUp(self):
        self.courses_df = pd.DataFrame([
            {"course_id": "C01", "course_name": "Python Programming", "difficulty": "Easy", "credits": 3},
            {"course_id": "C02", "course_name": "Advanced Python", "difficulty": "Medium", "credits": 3},
            {"course_id": "C03", "course_name": "Data Structures", "difficulty": "Medium", "credits": 4},
            {"course_id": "C07", "course_name": "Statistics", "difficulty": "Easy", "credits": 3},
            {"course_id": "C08", "course_name": "Machine Learning", "difficulty": "Hard", "credits": 4},
            {"course_id": "C09", "course_name": "Deep Learning", "difficulty": "Hard", "credits": 4},
            {"course_id": "C20", "course_name": "Project Management", "difficulty": "Easy", "credits": 2},
        ])
        
        self.prereqs_df = pd.DataFrame([
            {"course_id": "C02", "prerequisite": "C01", "is_hard": 1, "prereq_weight": 1.0},
            {"course_id": "C03", "prerequisite": "C01", "is_hard": 1, "prereq_weight": 1.0},
            {"course_id": "C08", "prerequisite": "C01", "is_hard": 1, "prereq_weight": 0.4},
            {"course_id": "C08", "prerequisite": "C07", "is_hard": 1, "prereq_weight": 0.6},
            {"course_id": "C09", "prerequisite": "C08", "is_hard": 1, "prereq_weight": 0.7},
            {"course_id": "C09", "prerequisite": "C02", "is_hard": 0, "prereq_weight": 0.3},
            {"course_id": "C20", "prerequisite": "None", "is_hard": 0, "prereq_weight": 0.0}
        ])
        self.resolver = PrerequisiteDAGResolver(self.courses_df, self.prereqs_df)

    def test_no_prerequisite_course(self):
        """Course with no prerequisites should immediately have 100% readiness and valid=True."""
        res = self.resolver.check_prerequisites("C01", completed_courses=[])
        self.assertTrue(res["valid"])
        self.assertEqual(res["readiness_score"], 100.0)
        self.assertEqual(len(res["hard_missing"]), 0)

        res20 = self.resolver.check_prerequisites("C20", completed_courses=[])
        self.assertTrue(res20["valid"])
        self.assertEqual(res20["readiness_score"], 100.0)

    def test_single_direct_prerequisite_satisfied(self):
        """Advanced Python should be valid when Python is completed."""
        res = self.resolver.check_prerequisites("C02", completed_courses=["C01"])
        self.assertTrue(res["valid"])
        self.assertEqual(res["readiness_score"], 100.0)
        self.assertIn("Python Programming", res["satisfied"])

    def test_single_direct_prerequisite_missing(self):
        """Advanced Python should fail when Python is not completed."""
        res = self.resolver.check_prerequisites("C02", completed_courses=[])
        self.assertFalse(res["valid"])
        self.assertEqual(res["readiness_score"], 0.0)
        self.assertIn("C01", res["hard_missing"])

    def test_partial_prerequisites_quantification(self):
        """
        Machine Learning requires C01 (hard) and C07 (hard).
        When student completed only C01:
        Readiness must be non-binary (50% raw, capped at 20-40% per academic policy).
        """
        res_partial = self.resolver.check_prerequisites("C08", completed_courses=["C01"])
        self.assertFalse(res_partial["valid"])
        self.assertGreater(res_partial["readiness_score"], 0.0)
        self.assertLessEqual(res_partial["readiness_score"], 40.0)
        self.assertIn("C07", res_partial["hard_missing"])
        self.assertIn("Python Programming", res_partial["satisfied"])

    def test_soft_prerequisite_satisfaction(self):
        """
        Deep Learning has hard prereq C08 and soft prereq C02.
        If C08 is completed but C02 is missing:
        Valid should be True, with soft_missing recorded.
        """
        res = self.resolver.check_prerequisites("C09", completed_courses=["C08"])
        self.assertTrue(res["valid"])
        self.assertIn("C02", res["soft_missing"])
        self.assertIn("Conditionally Satisfied", res["status"])

    def test_transitive_prerequisites_resolution(self):
        """C09 depends on C08 which depends on C01 and C07. Transitive set must contain C01, C07, C08."""
        transitive = self.resolver.get_transitive_prerequisites("C09")
        self.assertIn("C08", transitive)
        self.assertIn("C01", transitive)
        self.assertIn("C07", transitive)

    def test_natural_dag_is_acyclic(self):
        """The valid curriculum DAG must contain zero cycles."""
        cycles = self.resolver.detect_cycles()
        self.assertEqual(len(cycles), 0)

    def test_cycle_detection_on_injected_cyclic_data(self):
        """Injected circular dependencies (e.g. A -> B -> C -> A) must be detected."""
        cyclic_prereqs = pd.DataFrame([
            {"course_id": "C01", "prerequisite": "C03", "is_hard": 1},
            {"course_id": "C02", "prerequisite": "C01", "is_hard": 1},
            {"course_id": "C03", "prerequisite": "C02", "is_hard": 1}
        ])
        cyclic_resolver = PrerequisiteDAGResolver(self.courses_df, cyclic_prereqs)
        cycles = cyclic_resolver.detect_cycles()
        self.assertGreater(len(cycles), 0)


if __name__ == "__main__":
    unittest.main()
