"""
DAG Resolver for Course Prerequisites.
Handles directed acyclic graph construction, cycle detection,
transitive prerequisite resolution, and non-binary partial fulfillment scoring.
"""
from typing import Dict, List, Set, Tuple, Optional
import pandas as pd


class PrerequisiteDAGResolver:
    def __init__(self, courses_df: pd.DataFrame, prerequisites_df: pd.DataFrame):
        self.courses_df = courses_df.copy()
        self.prerequisites_df = prerequisites_df.copy()
        
        # Course lookup mappings
        self.course_names: Dict[str, str] = dict(
            zip(self.courses_df["course_id"], self.courses_df["course_name"])
        )
        self.all_course_ids: Set[str] = set(self.courses_df["course_id"].unique())
        
        # Build adjacency graph: course_id -> list of prerequisite course_ids
        self.adj_list: Dict[str, List[Dict]] = {cid: [] for cid in self.all_course_ids}
        self._build_graph()

    def _build_graph(self):
        for _, row in self.prerequisites_df.iterrows():
            cid = str(row["course_id"]).strip()
            prereq = str(row["prerequisite"]).strip()
            is_hard = bool(int(row.get("is_hard", 1))) if str(row.get("is_hard", "1")).isdigit() else True
            weight = float(row.get("prereq_weight", 1.0)) if "prereq_weight" in row else 1.0
            
            if cid in self.adj_list and prereq.lower() not in ["", "none", "nan", "no prerequisite"]:
                self.adj_list[cid].append({
                    "prereq_id": prereq,
                    "is_hard": is_hard,
                    "weight": weight
                })

    def get_course_name(self, course_id: str) -> str:
        return self.course_names.get(course_id, course_id)

    def detect_cycles(self) -> List[List[str]]:
        """
        Detects if there are cycles in the prerequisite graph using DFS.
        Returns a list of cycle paths if any exist.
        """
        visited: Dict[str, int] = {cid: 0 for cid in self.all_course_ids}  # 0: unvisited, 1: visiting, 2: visited
        cycles: List[List[str]] = []
        path: List[str] = []

        def dfs(node: str):
            visited[node] = 1
            path.append(node)
            for edge in self.adj_list.get(node, []):
                neighbor = edge["prereq_id"]
                if neighbor in self.all_course_ids:
                    if visited[neighbor] == 1:
                        # Cycle detected
                        cycle_start = path.index(neighbor)
                        cycles.append(path[cycle_start:] + [neighbor])
                    elif visited[neighbor] == 0:
                        dfs(neighbor)
            path.pop()
            visited[node] = 2

        for cid in self.all_course_ids:
            if visited[cid] == 0:
                dfs(cid)
        return cycles

    def get_direct_prerequisites(self, course_id: str) -> List[Dict]:
        return self.adj_list.get(course_id, [])

    def get_transitive_prerequisites(self, course_id: str) -> Set[str]:
        """
        Recursively traverses DAG to return all upstream prerequisites.
        """
        transitive: Set[str] = set()
        queue = [edge["prereq_id"] for edge in self.get_direct_prerequisites(course_id)]
        
        while queue:
            curr = queue.pop(0)
            if curr in self.all_course_ids and curr not in transitive:
                transitive.add(curr)
                for edge in self.get_direct_prerequisites(curr):
                    queue.append(edge["prereq_id"])
        return transitive

    def check_prerequisites(self, course_id: str, completed_courses: List[str]) -> Dict:
        """
        Non-binary prerequisite evaluation.
        Quantifies readiness score P(c) in [0, 100], accounting for hard vs soft requirements,
        partial completions, and transitive gaps.
        """
        completed_set = set(str(c).strip() for c in completed_courses if str(c).strip())
        edges = self.get_direct_prerequisites(course_id)
        
        if not edges:
            return {
                "valid": True,
                "readiness_score": 100.0,
                "hard_missing": [],
                "hard_missing_names": [],
                "soft_missing": [],
                "soft_missing_names": [],
                "satisfied": [],
                "all_required": [],
                "transitive_missing": [],
                "status": "Satisfied (No Prerequisites)"
            }

        hard_prereqs = [e for e in edges if e["is_hard"]]
        soft_prereqs = [e for e in edges if not e["is_hard"]]

        hard_satisfied = [e["prereq_id"] for e in hard_prereqs if e["prereq_id"] in completed_set]
        hard_missing = [e["prereq_id"] for e in hard_prereqs if e["prereq_id"] not in completed_set]

        soft_satisfied = [e["prereq_id"] for e in soft_prereqs if e["prereq_id"] in completed_set]
        soft_missing = [e["prereq_id"] for e in soft_prereqs if e["prereq_id"] not in completed_set]

        # Calculate partial fulfillment score
        # Hard weight = 0.75, Soft weight = 0.25
        alpha = 0.75
        if hard_prereqs and soft_prereqs:
            hard_ratio = len(hard_satisfied) / len(hard_prereqs)
            soft_ratio = len(soft_satisfied) / len(soft_prereqs)
            readiness = (alpha * hard_ratio + (1 - alpha) * soft_ratio) * 100.0
        elif hard_prereqs and not soft_prereqs:
            hard_ratio = len(hard_satisfied) / len(hard_prereqs)
            readiness = hard_ratio * 100.0
        elif soft_prereqs and not hard_prereqs:
            soft_ratio = len(soft_satisfied) / len(soft_prereqs)
            readiness = soft_ratio * 100.0
        else:
            readiness = 100.0

        # Academic policy guardrail: If any hard prerequisite is missing,
        # readiness cannot exceed 40.0 (prevents unqualified enrollment while rewarding partial foundation)
        if hard_missing and readiness > 40.0:
            readiness = 40.0

        # Transitive check
        all_transitive = self.get_transitive_prerequisites(course_id)
        transitive_missing = [t for t in all_transitive if t not in completed_set and t not in hard_missing and t not in soft_missing]

        is_valid = len(hard_missing) == 0

        status = "Satisfied"
        if not is_valid:
            if readiness >= 25.0:
                status = "Partial Prerequisite Deficit (Remedial Eligible)"
            else:
                status = "Prerequisite Blocked (Severe Deficit)"
        elif soft_missing:
            status = "Conditionally Satisfied (Recommended Elective Prep Missing)"

        return {
            "valid": is_valid,
            "readiness_score": round(readiness, 1),
            "hard_missing": hard_missing,
            "hard_missing_names": [self.get_course_name(cid) for cid in hard_missing],
            "soft_missing": soft_missing,
            "soft_missing_names": [self.get_course_name(cid) for cid in soft_missing],
            "satisfied": [self.get_course_name(cid) for cid in (hard_satisfied + soft_satisfied)],
            "all_required": [self.get_course_name(e["prereq_id"]) for e in edges],
            "transitive_missing": [self.get_course_name(cid) for cid in transitive_missing],
            "status": status
        }
