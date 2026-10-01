"""
Unit tests for ScheduleConflictDetector.
Tests interval algebra, disjoint time slots, partial/full collisions,
day boundaries, asynchronous delivery modes, and friction penalty calculations.
"""
import unittest
import pandas as pd
from engine.schedule_detector import ScheduleConflictDetector


class TestScheduleConflictDetector(unittest.TestCase):
    def setUp(self):
        self.courses_df = pd.DataFrame([
            {"course_id": "C01", "course_name": "Python Programming"},
            {"course_id": "C02", "course_name": "Advanced Python"},
            {"course_id": "C03", "course_name": "Data Structures"},
            {"course_id": "C08", "course_name": "Machine Learning"},
            {"course_id": "C09", "course_name": "Deep Learning"},
            {"course_id": "C20", "course_name": "Project Management"}
        ])
        
        self.schedules_df = pd.DataFrame([
            # C01 and C03 exact conflict: Monday 09:00 - 10:30
            {"course_id": "C01", "day": "Monday", "start_time": "09:00", "end_time": "10:30", "room": "Lab-101", "delivery_mode": "In-Person"},
            {"course_id": "C02", "day": "Monday", "start_time": "11:00", "end_time": "12:30", "room": "Lab-101", "delivery_mode": "In-Person"},
            {"course_id": "C03", "day": "Monday", "start_time": "09:00", "end_time": "10:30", "room": "Room-204", "delivery_mode": "In-Person"},
            # C08 and C09 partial overlap: Thursday 09:00-11:00 vs 10:00-12:00
            {"course_id": "C08", "day": "Thursday", "start_time": "09:00", "end_time": "11:00", "room": "AI-Lab", "delivery_mode": "In-Person"},
            {"course_id": "C09", "day": "Thursday", "start_time": "10:00", "end_time": "12:00", "room": "AI-Lab", "delivery_mode": "In-Person"},
            # C20 is Asynchronous Online
            {"course_id": "C20", "day": "Online", "start_time": "00:00", "end_time": "00:00", "room": "Virtual", "delivery_mode": "Asynchronous"},
        ])
        
        self.detector = ScheduleConflictDetector(self.schedules_df, self.courses_df)

    def test_disjoint_intervals_no_conflict(self):
        """C01 (Mon 9-10:30) and C02 (Mon 11-12:30) should not conflict."""
        has_conflict, details = self.detector.check_conflict_pair("C01", "C02")
        self.assertFalse(has_conflict)
        self.assertIsNone(details)

    def test_exact_time_overlap_detected(self):
        """C01 (Mon 9-10:30) and C03 (Mon 9-10:30) must flag a hard collision."""
        has_conflict, details = self.detector.check_conflict_pair("C01", "C03")
        self.assertTrue(has_conflict)
        self.assertIsNotNone(details)
        self.assertEqual(details["overlap_minutes"], 90)
        self.assertEqual(details["day"], "Monday")

    def test_partial_time_overlap_detected(self):
        """C08 (Thu 9-11) and C09 (Thu 10-12) overlap from 10:00 to 11:00 (60 minutes)."""
        has_conflict, details = self.detector.check_conflict_pair("C08", "C09")
        self.assertTrue(has_conflict)
        self.assertEqual(details["overlap_minutes"], 60)

    def test_different_days_never_conflict(self):
        """C01 (Monday) and C08 (Thursday) should never conflict."""
        has_conflict, details = self.detector.check_conflict_pair("C01", "C08")
        self.assertFalse(has_conflict)

    def test_asynchronous_online_never_conflicts(self):
        """C20 is Asynchronous online; should never conflict with any course."""
        for cid in ["C01", "C02", "C03", "C08", "C09"]:
            has_conflict, _ = self.detector.check_conflict_pair("C20", cid)
            self.assertFalse(has_conflict, f"C20 falsely conflicted with {cid}")

    def test_schedule_penalty_calculation(self):
        """Course with conflict gets 100.0 penalty; without conflict gets 0.0."""
        penalty_clash = self.detector.calculate_schedule_penalty("C03", ["C01"])
        self.assertEqual(penalty_clash, 100.0)

        penalty_ok = self.detector.calculate_schedule_penalty("C02", ["C01"])
        self.assertEqual(penalty_ok, 0.0)


if __name__ == "__main__":
    unittest.main()
