# Three-Minute Demonstration Video Script & Storyboard

**Title:** Elective Career Explorer: Responsible Decision-Support for Diverse Learning Speeds  
**Target Duration:** 3 minutes (180 seconds)  
**Tone:** Professional, clear, academic, and engaging  

---

## Storyboard & Timing Breakdown

| Time Code | Section | Screen Display / Visual Action | Spoken Narration (Voiceover) |
| :--- | :--- | :--- | :--- |
| **0:00 - 0:25** (25s) | **The Problem & Objective** | Title banner. Show split-screen: Confused student choosing electives vs. Advisor dealing with dropouts. Transition to Elective Career Explorer UI. | *"In modern schools supporting students with different learning speeds, choosing electives is fraught with risk. Students pick high-level courses based on career buzzwords, only to fail due to missing mathematical foundations or impossible timetable clashes. Welcome to Elective Career Explorer—a responsible AI decision-support system engineered to provide transparent, multi-speed course guidance."* |
| **0:25 - 0:55** (30s) | **Multi-Stakeholder Trade-off & Pacing** | Sidebar interaction. Select 'S01 - Aarav Sharma (Accelerated)' then 'S03 - Rohan Mehta (Supported)'. Move the **Co-Governance Slider** from 0.0 to 1.0. | *"Notice our sidebar: we explicitly model student learning speeds—accelerated, standard, and supported. More importantly, we resolve a core institutional conflict: student career ambition versus advisor academic prudence. Moving our Pareto Co-Governance Slider dynamically shifts mathematical weights in real time, making the trade-off visible rather than hiding it behind an opaque black box."* |
| **0:55 - 1:30** (35s) | **Mathematical Scoring & Explanation Layer** | Click on Tab 1. Expand the 'Mathematical Score Breakdown' card for Machine Learning (`C08`). Show the equation and component values. | *"Unlike binary check portals, our prototype employs a continuous composite recommendation formula. It quantifies prerequisite readiness P(c) via a Directed Acyclic Graph, career utility M(c), Bloom outcome depth O(c), and cognitive pacing capacity L(c). Non-binary partial prerequisites are rewarded, while academic safety caps prevent cognitive overload for vulnerable learners."* |
| **1:30 - 2:05** (35s) | **DAG Resolver & Schedule Collision** | Click on Tab 2 (Prerequisite DAG Explorer). Show upstream dependency chain for C09. Then click Tab 3 (Timetable Checker) and show collision between C01 and C03 on Monday morning. | *"In Tab 2, our DAG Resolver traces the full transitive prerequisite chain with built-in cycle detection. In Tab 3, interval algebra catches timetable collisions down to the minute. If an elective clashes with an enrolled course, our system immediately applies a 100-point penalty and suppresses the course, eliminating registration errors before they happen."* |
| **2:05 - 2:35** (30s) | **Fallback Workflow & Remediation** | Click Tab 4 (Fallback Remediation Workflow). Select C08 for a student without Statistics. Show the automated stepping-stone bridge and Advisor Escalation Petition. | *"When a student lacks prerequisites, our system never gives a dead-end rejection. Our fallback workflow generates an actionable stepping-stone pathway, recommending immediate bridge courses or drafting an automated Advisor Escalation Petition for accelerated students."* |
| **2:35 - 3:00** (25s) | **Empirical Benchmark & Conclusion** | Click Tab 5 (Empirical Evaluation). Highlight the 100% prerequisite reduction and 100% choice quality metrics. Show test suite execution in terminal. | *"In our empirical benchmark against a greedy baseline across 15 diverse student profiles, our prototype achieved a 100% reduction in prerequisite conflicts, a 48.8% gain in choice quality, and complete elimination of cognitive overload for supported students—all validated by automated unit test suites. Responsible, transparent, and computationally green. Thank you."* |

---

## Production & Recording Checklist
1. **Resolution:** 1080p (1920x1080) at 60 FPS.
2. **Audio:** High-clarity microphone, normalized to -14 LUFS.
3. **Cursor:** Smooth pointer highlighting with click rings enabled.
4. **App Execution Command:** `streamlit run app.py`
5. **Terminal Split:** Run `pytest tests/ -v` briefly in the final segment to demonstrate automated verification.
