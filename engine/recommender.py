"""
Recommendation Engine with Continuous Mathematical Composite Scoring,
Learning-Speed Adaptation, and Multi-Stakeholder Trade-off Weighting.
"""
from typing import Dict, List, Optional, Tuple
import pandas as pd
from engine.dag_resolver import PrerequisiteDAGResolver
from engine.schedule_detector import ScheduleConflictDetector


class CourseRecommender:
    def __init__(
        self,
        courses_df: pd.DataFrame,
        career_pathways_df: pd.DataFrame,
        course_outcomes_df: pd.DataFrame,
        dag_resolver: PrerequisiteDAGResolver,
        schedule_detector: ScheduleConflictDetector
    ):
        self.courses_df = courses_df.copy()
        self.career_pathways_df = career_pathways_df.copy()
        self.course_outcomes_df = course_outcomes_df.copy()
        self.dag = dag_resolver
        self.scheduler = schedule_detector

        # Map outcomes for fast lookup
        self.outcomes_map: Dict[str, Dict] = {}
        for _, row in self.course_outcomes_df.iterrows():
            cid = str(row["course_id"]).strip()
            self.outcomes_map[cid] = {
                "learning_outcome": str(row.get("learning_outcome", "General competency")),
                "skills": str(row.get("skills", "General")),
                "bloom_level": str(row.get("bloom_level", "Apply"))
            }

        # Difficulty pacing alignment matrix L(difficulty, learning_speed)
        self.pacing_matrix = {
            "accelerated": {"Hard": 100.0, "Medium": 90.0, "Easy": 70.0},
            "standard":    {"Hard": 75.0,  "Medium": 100.0, "Easy": 85.0},
            "supported":   {"Hard": 40.0,  "Medium": 80.0,  "Easy": 100.0}
        }

        # Bloom taxonomy multiplier for outcome depth O(c)
        self.bloom_multipliers = {
            "Create": 100.0,
            "Evaluate": 95.0,
            "Analyze": 90.0,
            "Apply": 85.0,
            "Understand": 75.0,
            "Remember": 70.0
        }

    def get_career_match_score(self, career_goal: str, course_id: str) -> float:
        """Returns raw match score (1 to 5) or 0.0 if not listed."""
        subset = self.career_pathways_df[
            (self.career_pathways_df["career_goal"].str.lower() == career_goal.lower()) &
            (self.career_pathways_df["course_id"] == course_id)
        ]
        if subset.empty:
            return 0.0
        try:
            return float(subset.iloc[0]["match_score"])
        except Exception:
            return 0.0

    def compute_stakeholder_weights(self, trade_off_ratio: float = 0.5) -> Dict[str, float]:
        """
        Calculates weights between:
        trade_off_ratio = 0.0 -> Maximum Student Career Ambition
        trade_off_ratio = 0.5 -> Balanced Co-Governance (Default)
        trade_off_ratio = 1.0 -> Maximum Advisor Academic Prudence
        """
        # Interpolate between endpoints
        w_career = (1.0 - trade_off_ratio) * 0.50 + trade_off_ratio * 0.15
        w_prereq = (1.0 - trade_off_ratio) * 0.20 + trade_off_ratio * 0.45
        w_pace   = (1.0 - trade_off_ratio) * 0.15 + trade_off_ratio * 0.30
        w_outcome = 1.0 - (w_career + w_prereq + w_pace)

        return {
            "w_career": round(w_career, 3),
            "w_prereq": round(w_prereq, 3),
            "w_pace": round(w_pace, 3),
            "w_outcome": round(w_outcome, 3)
        }

    def calculate_composite_score(
        self,
        course_id: str,
        career_goal: str,
        completed_courses: List[str],
        learning_speed: str = "standard",
        selected_courses: Optional[List[str]] = None,
        trade_off_ratio: float = 0.5
    ) -> Dict:
        """
        Evaluates the full continuous mathematical composite score S(c):
        S(c) = max(0, w_prereq * P(c) + w_career * M(c) + w_outcome * O(c) + w_pace * L(c) - Pi_conflict(c))
        """
        if selected_courses is None:
            selected_courses = []

        # 1. Prerequisite Readiness P(c) via DAG Resolver
        prereq_eval = self.dag.check_prerequisites(course_id, completed_courses)
        p_score = prereq_eval["readiness_score"]

        # 2. Career Pathway Match M(c)
        raw_career = self.get_career_match_score(career_goal, course_id)
        m_score = min((raw_career / 5.0) * 100.0, 100.0)

        # 3. Outcome / Competency Score O(c)
        outcome_info = self.outcomes_map.get(course_id, {})
        bloom = outcome_info.get("bloom_level", "Apply")
        o_score = self.bloom_multipliers.get(bloom, 85.0)

        # 4. Learning Speed Adaptation Score L(c, speed)
        course_row = self.courses_df[self.courses_df["course_id"] == course_id]
        difficulty = str(course_row.iloc[0]["difficulty"]).capitalize() if not course_row.empty else "Medium"
        speed_key = learning_speed.lower() if learning_speed.lower() in self.pacing_matrix else "standard"
        l_score = self.pacing_matrix[speed_key].get(difficulty, 80.0)

        # 5. Schedule Conflict Penalty Pi_conflict(c)
        conflicts = self.scheduler.find_conflicts_for_course(course_id, selected_courses)
        pi_conflict = 100.0 if len(conflicts) > 0 else 0.0

        # Weights
        weights = self.compute_stakeholder_weights(trade_off_ratio)

        raw_composite = (
            weights["w_prereq"] * p_score +
            weights["w_career"] * m_score +
            weights["w_outcome"] * o_score +
            weights["w_pace"] * l_score -
            pi_conflict
        )
        final_score = max(0.0, min(100.0, round(raw_composite, 1)))

        # Status categorization
        if pi_conflict > 0:
            status = "Schedule Conflict"
        elif not prereq_eval["valid"]:
            if p_score >= 25.0:
                status = "Conditional (Remedial Bridge Eligible)"
            else:
                status = "Prerequisite Blocked"
        elif speed_key == "supported" and difficulty == "Hard":
            status = "Review (Cognitive Overload Risk)"
        else:
            status = "Recommended"

        return {
            "course_id": course_id,
            "final_score": final_score,
            "components": {
                "P_prereq": p_score,
                "M_career": round(m_score, 1),
                "O_outcome": round(o_score, 1),
                "L_pace": round(l_score, 1),
                "Pi_conflict": pi_conflict
            },
            "weights": weights,
            "status": status,
            "prereq_eval": prereq_eval,
            "conflicts": conflicts,
            "difficulty": difficulty,
            "credits": int(course_row.iloc[0]["credits"]) if not course_row.empty else 3,
            "outcome": outcome_info
        }

    def recommend(
        self,
        career_goal: str,
        completed_courses: List[str],
        learning_speed: str = "standard",
        selected_courses: Optional[List[str]] = None,
        trade_off_ratio: float = 0.5
    ) -> pd.DataFrame:
        """Generates ranked dataframe of all available electives with explanations."""
        if selected_courses is None:
            selected_courses = []

        completed_set = set(str(c).strip() for c in completed_courses)
        records = []

        for _, row in self.courses_df.iterrows():
            cid = str(row["course_id"]).strip()
            if cid in completed_set:
                continue

            eval_res = self.calculate_composite_score(
                course_id=cid,
                career_goal=career_goal,
                completed_courses=completed_courses,
                learning_speed=learning_speed,
                selected_courses=selected_courses,
                trade_off_ratio=trade_off_ratio
            )

            c_name = row["course_name"]
            records.append({
                "Course ID": cid,
                "Course": c_name,
                "Difficulty": eval_res["difficulty"],
                "Credits": eval_res["credits"],
                "Score": eval_res["final_score"],
                "Status": eval_res["status"],
                "Prereq Readiness": f"{eval_res['components']['P_prereq']}%",
                "Career Match (1-5)": round(eval_res['components']['M_career'] / 20.0, 1),
                "Pacing Score": f"{eval_res['components']['L_pace']}%",
                "Missing Prereqs": ", ".join(eval_res["prereq_eval"]["hard_missing_names"]) if eval_res["prereq_eval"]["hard_missing_names"] else "None",
                "Schedule Conflicts": ", ".join([c["course_2_name"] for c in eval_res["conflicts"]]) if eval_res["conflicts"] else "None",
                "Learning Outcome": eval_res["outcome"].get("learning_outcome", "N/A"),
                "Skills": eval_res["outcome"].get("skills", "N/A")
            })

        df_res = pd.DataFrame(records)
        if not df_res.empty:
            df_res = df_res.sort_values(by="Score", ascending=False).reset_index(drop=True)
        return df_res
