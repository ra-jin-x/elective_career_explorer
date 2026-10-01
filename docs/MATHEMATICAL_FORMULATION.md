# Mathematical Formulation: Composite Recommendation Score & Edge-Case Quantification

This document formally specifies the mathematical scoring engine utilized in the **Elective Career Explorer** responsible decision-support system. It details the objective functions, variable definitions, and the exact continuous quantification of non-binary edge cases (such as partial prerequisite completion, learning-speed cognitive load, and timetable overlap intervals).

---

## 1. Global Composite Recommendation Score Function

For a candidate elective course $c \in \mathcal{C}$ evaluated for a student profile with learning speed $v \in \{\text{accelerated}, \text{standard}, \text{supported}\}$, cumulative completed course set $\mathcal{K} \subset \mathcal{C}$, career goal $g$, and current semester enrollment selection $\mathcal{S} \subset \mathcal{C}$, the **Composite Recommendation Score** $S(c) \in [0, 100]$ is defined as:

$$S(c) = \max\left(0, \; w_{\text{prereq}} \cdot P(c, \mathcal{K}) + w_{\text{career}} \cdot M(c, g) + w_{\text{outcome}} \cdot O(c) + w_{\text{pace}} \cdot L(c, v) - \Pi_{\text{conflict}}(c, \mathcal{S})\right)$$

Subject to the convexity constraint:
$$w_{\text{prereq}} + w_{\text{career}} + w_{\text{outcome}} + w_{\text{pace}} = 1.0, \quad \forall w_i \ge 0$$

Where:
- $P(c, \mathcal{K}) \in [0, 100]$: Continuous Prerequisite Readiness Score.
- $M(c, g) \in [0, 100]$: Normalized Career Pathway Match Score.
- $O(c) \in [0, 100]$: Learning Outcome & Competency Depth Score.
- $L(c, v) \in [0, 100]$: Learning-Speed Cognitive Pacing Alignment.
- $\Pi_{\text{conflict}}(c, \mathcal{S}) \ge 0$: Schedule Conflict Penalty Function.

---

## 2. Prerequisite DAG Readiness Score $P(c, \mathcal{K})$ (Non-Binary Edge-Case Quantification)

Legacy systems treat prerequisite compliance as a fragile binary boolean $\mathbb{I}(\mathcal{R}(c) \subseteq \mathcal{K}) \in \{0, 1\}$. This fails to distinguish between a student who has satisfied 2 out of 3 prerequisites versus a student who has satisfied 0, and ignores the distinction between core hard prerequisites and complementary soft prerequisites.

Let the prerequisite set for course $c$ in the Directed Acyclic Graph $G = (V, E)$ be partitioned into:
$$\mathcal{R}(c) = \mathcal{R}_{\text{hard}}(c) \cup \mathcal{R}_{\text{soft}}(c), \quad \mathcal{R}_{\text{hard}}(c) \cap \mathcal{R}_{\text{soft}}(c) = \emptyset$$

### 2.1 Base Readiness Ratio
If $\mathcal{R}(c) = \emptyset$, then:
$$P(c, \mathcal{K}) = 100.0$$

Otherwise:
$$P_{\text{raw}}(c, \mathcal{K}) = 100 \times \left( \alpha \cdot \frac{|\mathcal{K} \cap \mathcal{R}_{\text{hard}}(c)|}{|\mathcal{R}_{\text{hard}}(c)|} + (1 - \alpha) \cdot \frac{|\mathcal{K} \cap \mathcal{R}_{\text{soft}}(c)|}{|\mathcal{R}_{\text{soft}}(c)|} \right)$$

Where $\alpha = 0.75$ represents the institutional priority of core foundational competencies over elective prerequisites. If $|\mathcal{R}_{\text{soft}}(c)| = 0$, $\alpha = 1.0$.

### 2.2 Academic Safety Policy Cap (Hard Prerequisite Deficit Guardrail)
To prevent uncertified students from enrolling in rigorous upper-division electives while still rewarding foundational progress, an academic boundary cap is applied:

$$P(c, \mathcal{K}) = \begin{cases} 
P_{\text{raw}}(c, \mathcal{K}), & \text{if } \mathcal{R}_{\text{hard}}(c) \subseteq \mathcal{K} \\
\min\left(P_{\text{raw}}(c, \mathcal{K}), \; 40.0\right), & \text{if } \exists p \in \mathcal{R}_{\text{hard}}(c) \text{ s.t. } p \notin \mathcal{K}
\end{cases}$$

This non-binary formulation guarantees:
1. Students with partial hard prerequisites ($1/2$) receive $40.0\%$, making them eligible for conditional advisor bridge pathways.
2. Students with zero prerequisites receive $0.0\%$.
3. Students missing only soft prerequisites can score up to $85.0\% - 95.0\%$, enabling co-requisite tutoring instead of administrative blocking.

---

## 3. Career Pathway Match $M(c, g)$

For a student targeting career aspiration $g \in \mathcal{G}$, let $m(c, g) \in \{1, 2, 3, 4, 5\}$ denote the domain-curated alignment rating. The normalized career match is:

$$M(c, g) = \frac{m(c, g)}{5.0} \times 100.0$$

If course $c$ has no recorded alignment for goal $g$, $M(c, g) = 0.0$.

---

## 4. Learning-Speed Cognitive Pacing Alignment $L(c, v)$

To fulfill the mission of supporting students with diverse learning speeds, the system quantifies the cognitive impedance between course difficulty $d(c) \in \{\text{Easy}, \text{Medium}, \text{Hard}\}$ and student pacing tier $v \in \{\text{accelerated}, \text{standard}, \text{supported}\}$:

$$L(c, v) = \mathbf{M}_{\text{pace}}[v, d(c)]$$

Where the empirically calibrated impedance matrix $\mathbf{M}_{\text{pace}}$ is:

| Student Pacing Tier ($v$) | Easy ($d=\text{Easy}$) | Medium ($d=\text{Medium}$) | Hard ($d=\text{Hard}$) | Institutional Pedagogical Rationale |
| :--- | :---: | :---: | :---: | :--- |
| **Accelerated** | $70.0$ | $90.0$ | $\mathbf{100.0}$ | Incentivizes academic rigor; avoids under-stimulation. |
| **Standard** | $85.0$ | $\mathbf{100.0}$ | $75.0$ | Balances progression with standard credit load. |
| **Supported / Remedial** | $\mathbf{100.0}$ | $80.0$ | $\mathbf{40.0}$ | Strongly prevents cognitive overload and course failure. |

---

## 5. Schedule Conflict Penalty Function $\Pi_{\text{conflict}}(c, \mathcal{S})$

For candidate course $c$ and prospective semester cart $\mathcal{S}$, let each course have a scheduled lecture interval on day $D_i$:
$$I(c) = [t_{\text{start}}(c), \; t_{\text{end}}(c)) \quad \text{on day } D(c)$$

Interval intersection between course $c$ and an already selected course $s \in \mathcal{S}$ is defined as:
$$\text{Overlap}(c, s) = \begin{cases}
\max\left(0, \; \min(t_{\text{end}}(c), t_{\text{end}}(s)) - \max(t_{\text{start}}(c), t_{\text{start}}(s))\right), & \text{if } D(c) = D(s) \text{ and neither is Asynchronous} \\
0, & \text{otherwise}
\end{cases}$$

The penalty function is strictly enforced:
$$\Pi_{\text{conflict}}(c, \mathcal{S}) = \begin{cases}
100.0, & \text{if } \exists s \in \mathcal{S} \text{ s.t. } \text{Overlap}(c, s) > 0 \\
0.0, & \text{if } \forall s \in \mathcal{S}, \; \text{Overlap}(c, s) = 0
\end{cases}$$

---

## 6. Multi-Stakeholder Pareto Co-Governance Scheme

To make the conflicting trade-offs between **Student Ambition** (maximizing career relevance) and **Advisor Prudence** (maximizing prerequisite readiness and cognitive pacing safety) explicit and controllable, a Pareto balance parameter $\theta \in [0.0, 1.0]$ governs weight allocation:

$$w_{\text{career}}(\theta) = (1 - \theta) \cdot 0.50 + \theta \cdot 0.15$$
$$w_{\text{prereq}}(\theta) = (1 - \theta) \cdot 0.20 + \theta \cdot 0.45$$
$$w_{\text{pace}}(\theta) = (1 - \theta) \cdot 0.15 + \theta \cdot 0.30$$
$$w_{\text{outcome}}(\theta) = 1.0 - \left(w_{\text{career}}(\theta) + w_{\text{prereq}}(\theta) + w_{\text{pace}}(\theta)\right)$$

### Operating Regimes:
1. $\theta = 0.0$ (**Pure Student Ambition**): $w_{\text{career}} = 0.50$, $w_{\text{prereq}} = 0.20$. Prioritizes career alignment; high-level electives surface even with minor prerequisite deficits.
2. $\theta = 0.5$ (**Default Balanced Co-Governance**): $w_{\text{prereq}} = 0.325$, $w_{\text{career}} = 0.325$, $w_{\text{pace}} = 0.225$. Harmonizes ambition with structural feasibility.
3. $\theta = 1.0$ (**Strict Advisor Prudence**): $w_{\text{prereq}} = 0.45$, $w_{\text{pace}} = 0.30$, $w_{\text{career}} = 0.15$. Ensures prerequisite mastery and cognitive pacing safety dominate the recommendation order.
