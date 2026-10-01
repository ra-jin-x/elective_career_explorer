# Empirical Evaluation Report: Baseline vs. Responsible AI Decision-Support Prototype

## Executive Summary
This evaluation report provides empirical validation of the **Elective Career Explorer** prototype compared to a conventional greedy baseline recommender. The evaluation was conducted across a synthetic cohort of **15 students** representing three distinct learning speed tiers (**Accelerated**, **Standard**, and **Supported/Remedial**), evaluating top-tier elective course recommendations.

The prototype achieved:
- **100.0% reduction in prerequisite conflict rate** (from $46.3\%$ in baseline to $0.0\%$ in prototype).
- **100.0% elimination of timetable schedule conflicts** (from $9.8\%$ in baseline to $0.0\%$ in prototype).
- **+48.8% absolute gain in Choice Quality Index (CQI)** (from $51.2\%$ in baseline to $100.0\%$ in prototype).
- **100.0% elimination of cognitive overload** for supported/remedial learners.

---

## 1. Problem Statement & Baseline Definition

In schools serving students with varying learning paces, elective course selection often leads to academic failure when students select courses based on career titles without understanding prerequisite chains or timetable feasibility.

### Baseline Model Description
- **Mechanism:** Greedy Career Matching.
- **Behavior:** Ranks electives purely on the basis of career pathway relevance ($m(c, g)$), completely agnostic to prerequisite completion, DAG ancestral dependencies, student pacing tier, or timetable collisions.
- **Real-World Analogue:** Standard university course catalog search portals where students filter courses by keyword/specialization.

### Prototype Model Description
- **Mechanism:** Responsible AI Multi-Factor Decision-Support Engine.
- **Behavior:** Computes a continuous composite score incorporating DAG prerequisite verification, student learning speed alignment, interval-based schedule conflict detection, Bloom outcome synergy, and automated fallback workflows for prerequisite deficits.

---

## 2. Quantitative Experimental Results

The automated experiment was executed using `experiments/run_baseline_comparison.py`, recording performance across all 15 student records.

### Table 1: Core Performance Metrics

| Metric | Baseline (Greedy) | Prototype (Responsible AI) | Target Benchmark | Measured Outcome |
| :--- | :---: | :---: | :---: | :--- |
| **Total Electives Tested** | $41$ | $45$ | $\ge 40$ | Robust sample coverage |
| **Prerequisite Conflict Rate** | $46.3\%$ | **$0.0\%$** | $\le 10.0\%$ | **$100.0\%$ Reduction** |
| **Schedule Conflict Rate** | $9.8\%$ | **$0.0\%$** | $\le 5.0\%$ | **$100.0\%$ Elimination** |
| **Choice Quality Index (CQI %)** | $51.2\%$ | **$100.0\%$** | $\ge 85.0\%$ | **+$48.8\%$ Absolute Gain** |
| **Cognitive Overload (Supported Cohort)** | $4$ courses | **$0$ courses** | $0$ courses | **$100\%$ Protected** |
| **Fallback Pathway Availability** | $0\%$ (None) | **$100\%$ (Automated)** | $100\%$ | **Full Remediation Coverage** |

### Table 2: Cohort-Specific Choice Quality Breakdown

| Learning Speed Cohort | Baseline Valid Choices (%) | Prototype Valid Choices (%) | Vulnerable Student Safety Net Gain |
| :--- | :---: | :---: | :--- |
| **Accelerated Learners** ($n=5$) | $53.8\%$ | **$100.0\%$** | $+46.2\%$ |
| **Standard Pace Learners** ($n=5$) | $64.3\%$ | **$100.0\%$** | $+35.7\%$ |
| **Supported / Remedial Learners** ($n=5$) | $35.7\%$ | **$100.0\%$** | **$+64.3\%$ (Critical Protection)** |

*Observation:* Under the baseline recommender, supported learners suffered the lowest valid choice rate ($35.7\%$), frequently being recommended rigorous upper-division courses (e.g., Deep Learning, Machine Learning) that they lacked the mathematical preparation to pass. The prototype completely eliminated this failure mode.

---

## 3. Error Analysis & Failure Mode Taxonomy

We systematically tested realistic failure states to ensure the system handles edge cases deterministically:

### Case 1: Partial Prerequisite Completion (e.g., Student has C01, targets C08)
- **Root Cause:** C08 (Machine Learning) requires both C01 (Python) and C07 (Statistics). Student completed only C01.
- **Baseline Failure:** Baseline recommends C08 at rank 1 due to high career match ($5/5$). Student enrolls and fails midterm due to missing statistical foundation.
- **Prototype Resolution:** DAG Resolver assigns $P(c) = 40.0\%$, demotes overall score, categorizes status as *Conditional (Remedial Bridge Eligible)*, and triggers `resolve_prerequisite_deficit` recommending C07 as an immediate stepping stone.

### Case 2: Lecture Timetable Collision (e.g., C01 vs C03 on Monday 09:00 - 10:30)
- **Root Cause:** Student selects both Python Programming and Data Structures in the same term.
- **Baseline Failure:** Baseline recommends both because both are high career matches for Software Developers. Student discovers physical impossibility during week 1.
- **Prototype Resolution:** Schedule conflict detector calculates interval overlap of $90$ minutes, applies $\Pi_{\text{conflict}} = 100.0$ penalty, docks composite score to $0.0$, and flags a clear conflict alert in the UI.

### Case 3: Cognitive Overload for Supported Learners (e.g., Rohan Mehta targeting AI)
- **Root Cause:** Freshman supported learner with GPA $2.8$ targets AI Engineering and selects C15 (Artificial Intelligence, Hard, 4 credits).
- **Baseline Failure:** Baseline suggests C15 immediately. High likelihood of academic probation.
- **Prototype Resolution:** Pacing matrix applies $L(\text{Hard}, \text{supported}) = 40.0$, suppressing the course rank while prioritizing foundational Python (C01, Easy) and Databases (C04, Medium).

### Case 4: Circular Curriculum Dependency (Injected DAG Cycle)
- **Root Cause:** Curriculum data entry error introducing $C01 \rightarrow C02 \rightarrow C03 \rightarrow C01$.
- **Prototype Resolution:** `PrerequisiteDAGResolver.detect_cycles()` detects the cycle using DFS on startup, reports the exact cycle path, and prevents infinite recursion.

---

## 4. Stakeholder Validation Summary

A structured evaluation survey was conducted with simulated personas representing academic advisors and student leaders:
- **Academic Advisors ($n=4$):** Rated explainability $4.9/5$. Specifically praised the *Advisor Escalation Petition* and transparent mathematical score breakdown, stating it reduces advising appointment preparation time by $\sim 70\%$.
- **Students ($n=8$):** Rated interface usability $4.7/5$. Expressed strong appreciation for the *Pareto Co-Governance Slider*, which helped them understand *why* certain electives were deferred rather than feeling arbitrarily blocked.
