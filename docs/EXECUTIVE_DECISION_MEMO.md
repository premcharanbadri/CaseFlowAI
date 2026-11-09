# CaseFlow AI — Executive Investment Decision (Synthetic Case)

**Decision request:** Approve a limited, human-in-the-loop classification pilot, *not* enterprise-wide automation or customer-impacting autonomous action.

## Situation and central insight

A fabricated 15,300-case history shows first-route errors, incomplete intake fields, and delayed cases. The measured relationship is **observational within synthetic data**. It does not prove that routing is the source of all delays. Before purchasing AI capabilities, improve intake completeness and standardize routing definitions.

## Alternatives

| Option | Advantages | Key limitation | Recommendation |
|---|---|---|---|
| A. Manual + structured intake | Low risk and immediate process standardization | Limited classification automation | Implement regardless |
| B. Transparent keyword rules | Cheap, auditable, no ML operations | Ambiguity creates wrong routes | Maintain as comparator/fallback |
| C. Confidence-gated ML suggestions | Better selective accuracy/coverage in this synthetic experiment | Model errors, QA expense, drift | Pilot with human supervision |
| D. LLM/agent-based routing | Potentially better for highly ambiguous narratives | Cost, privacy, inconsistency, governance overhead | Only consider after evidence of incremental value |

## Decision guardrails

- Only Standard-priority high-confidence cases receive auto-suggestions.
- High/Critical, low-confidence, or sensitive requests stay with human reviewers.
- Minimum 97% routed precision on validation and no evidence of worse service quality in pilot.
- Track category/channel heterogeneity and unexpected types of service requests.
- Stop rollout immediately after severe misroute, repeat privacy issue, or guardrail breach.

## Pilot design

- Instrument a pre-period, verify baseline workflows and case mix.
- Randomize **eligible** cases at intake to current workflow vs recommendations. If workforce contamination is material, randomize at shift/team clusters and adjust inference for clustering.
- Primary KPI: minutes of actual staff work per case, inclusive of QA and rework.
- Secondary outcomes: correct first-route percentage, 90th percentile elapsed resolution time, SLA breaches, customer feedback.
- Safeguards: no material rise in escalation or reopens; pre-register sample size from real workflow variance and expected effect.
- Report intent-to-treat effect; avoid examining only cases where staff accepted the suggestion.

## What management should approve now

1. A 2-week diagnostic of intake completeness, routing definitions, and capacity by queue.
2. A 4-week **shadow mode** (model makes predictions, humans continue current workflow) to assess error patterns and distribution shift.
3. A small human-in-the-loop controlled pilot if minimum precision and workflow safety standards pass.
4. Finance-reviewed ROI based on real minutes and avoided costs, followed by a scale / refine / stop decision.

## Critical caveats

The synthetic experiment cannot establish real-world model performance, process improvement, or saved dollars. The dollar model represents **released-capacity value** and excludes potential implementation impacts that vary by client (vendor fees, governance/security reviews, integration, training, quality evaluation, change management).

## Reproducible synthetic outputs

- Cases simulated: **15,300**; held-out out-of-time test: **2,772**.
- Average handling time: **12.64 min**; rerouted cases: **10.1%**.
- AI full-coverage accuracy: **86.3%**; macro F1: **0.864**.
- Confidence-gated AI suggestions: **62.9%** of all cases and **99.94%** routed precision on held-out cases.
- Rules baseline: **57.6%** of all cases and **82.2%** routed precision.
- Modeled release of **42.4 hours/month**, **$12,728** annual capacity value and **$2,928** Year-1 net value at assumed prices; **NOT measured cash savings**.

**Go / no-go:** proceed only to *shadow mode* and small supervised trial; verify the accuracy, economics, and actual effect on service time using live, approved operational records.
