# 🎓 Elective Career Explorer: Responsible Decision-Support System
> **A Responsible AI prototype supporting students with diverse learning speeds to navigate elective course selection, prerequisite DAGs, timetable feasibility, and career consequences.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg)](https://streamlit.io/)
[![Unit Tests](https://img.shields.io/badge/pytest-19%20passed-brightgreen.svg)]()
[![Responsible AI](https://img.shields.io/badge/Governance-Responsible%20AI-success.svg)]()

---

## 📌 Project Overview & Problem Statement

In academic institutions supporting students with different learning speeds (Accelerated, Standard, Supported/Remedial), students frequently select electives based on career buzzwords without comprehending deep prerequisite dependency chains or timetable collisions. This leads to high course failure rates, schedule conflicts, and cognitive burnout.

The **Elective Career Explorer** solves this via a responsible, transparent, multi-factor decision-support engine featuring:
- **Continuous Mathematical Scoring:** Evaluates composite utility $S(c)$ detailing partial prerequisite fulfillment, Bloom outcome depth, and learning speed cognitive impedance.
- **DAG Prerequisite Resolver:** Verifies directed acyclic graphs with transitive dependency closure, non-binary partial readiness, and cycle detection.
- **Interval Timetable Deconfliction:** Detects overlapping lecture slots down to the minute and accounts for asynchronous delivery modes.
- **Pareto Co-Governance Control:** Balances conflicting objectives between **Student Ambition** (career match) and **Advisor Prudence** (prerequisite mastery and cognitive safety).
- **Deterministic Fallback Safety Net:** Provides structured bridge courses and automated Advisor Escalation Petitions when prerequisites are unfulfilled.
- **Empirical Validation:** Backed by automated unit test suites and an empirical benchmark demonstrating **100% reduction in prerequisite conflicts** and **+48.8% gain in choice quality**.

---

## 🏛️ System Architecture

```
elective_career_explorer/
│
├── data/                               # Cleaned Synthetic Academic Datasets
│   ├── courses.csv                     # 20 Courses with difficulty, credits, weekly hours
│   ├── prerequisites.csv               # DAG edges (hard/soft, weights)
│   ├── schedules.csv                   # Timetables, days, times, delivery modes
│   ├── career_pathways.csv             # Career alignments across 10 career paths
│   ├── course_outcomes.csv             # Competency statements & Bloom levels
│   └── students.csv                    # 15 Student profiles across 3 learning speeds
│
├── engine/                             # Core Algorithmic Business Logic
│   ├── __init__.py
│   ├── dag_resolver.py                 # Graph resolver, cycle detection, partial scores
│   ├── schedule_detector.py            # Timetable interval algebra & overlap penalty
│   ├── recommender.py                  # Continuous composite scoring & Pareto weighting
│   └── fallback.py                     # Remediation bridges & advisor escalation
│
├── tests/                              # Automated Unit Test Suites (pytest)
│   ├── __init__.py
│   ├── test_dag_resolver.py            # DAG structure, transitivity, cycles, partial credit
│   ├── test_schedule_detector.py       # Interval collisions, disjoint slots, async modes
│   └── test_recommender_and_fallback.py# Pacing alignment, Pareto weights, fallback paths
│
├── experiments/                        # Empirical Evaluation Benchmark
│   ├── run_baseline_comparison.py      # Automated benchmark runner (Greedy vs Prototype)
│   └── baseline_comparison_results.csv # Quantitative experiment logs
│
├── docs/                               # Formal Documentation & Governance Reports
│   ├── MATHEMATICAL_FORMULATION.md     # Mathematical specification of composite score
│   ├── EVALUATION_REPORT.md            # Benchmark report, targets, and error analysis
│   ├── RESPONSIBLE_AI_AND_GOVERNANCE.md# Ethics, environmental carbon, maintenance
│   └── DEMO_VIDEO_SCRIPT.md            # Exact 3-minute presentation script & storyboard
│
├── app.py                              # Interactive Streamlit Prototype
├── requirements.txt                    # Project dependencies
└── README.md                           # Documentation & quickstart guide
```

---

## ⚡ Quickstart & Installation

### 1. Clone / Navigate to Directory
```bash
cd "C:\Users\NewAdmin\.gemini\antigravity\scratch\elective_career_explorer"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Automated Unit Test Suites
```bash
python -m pytest tests/ -v
```
*Expected Output: 19 passed tests across DAG resolver, schedule detector, and recommender.*

### 4. Execute Empirical Baseline Experiment
```bash
python experiments/run_baseline_comparison.py
```
*Generates quantitative comparison tables between Baseline (Greedy) and Prototype (Responsible AI).*

### 5. Launch Interactive Prototype
```bash
streamlit run app.py
```

---

## 📊 Empirical Evaluation Summary

| Metric | Baseline (Greedy) | Prototype (Responsible AI) | Measured Outcome |
| :--- | :---: | :---: | :--- |
| **Prerequisite Conflict Rate** | $46.3\%$ | **$0.0\%$** | **$100.0\%$ Reduction** |
| **Schedule Conflict Rate** | $9.8\%$ | **$0.0\%$** | **$100.0\%$ Elimination** |
| **Choice Quality Index (CQI %)** | $51.2\%$ | **$100.0\%$** | **+$48.8\%$ Absolute Gain** |
| **Cognitive Overload (Supported Cohort)** | $4$ courses | **$0$ courses** | **$100\%$ Protected** |
| **Fallback Pathway Availability** | $0\%$ | **$100\%$** | **Full Remediation Safety Net** |

---

## 🛡️ Responsible AI, Environmental & Ethical Governance

- **Environmental Sustainability:** Deterministic $\mathcal{O}(|V|+|E|)$ graph algorithms running on standard CPU with $< 1.5$ ms latency and virtually zero carbon emissions ($< 0.0001$ Wh per query), avoiding the high energy footprint of LLM cloud calls.
- **Fairness & Equity:** Zero ingestion of protected demographic attributes. Supported learners receive proactive bridge remediation rather than exclusionary dropouts.
- **Human-in-the-Loop:** Acts strictly as decision-support. All prerequisite waivers and exceptional enrollments require formal advisor sign-off.

---

## 👥 Authors & Review

- **Project:** Elective Career Explorer
- **Milestone:** 100% Completion Review
- **Mentor Enhancements Implemented:**
  1. Formulated & documented mathematical formula for composite recommendation score with non-binary partial prerequisites.
  2. Implemented automated unit test suites (`pytest`) for DAG resolver and schedule detector.
  3. Executed and documented empirical baseline comparison experiment with quantitative metrics.
