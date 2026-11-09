# Synthetic data dictionary

| Variable | Definition / source |
|---|---|
| case_id | synthetic unique case identifier |
| created_at / resolved_at | fabricated ticket creation and completion timestamps |
| channel | fabricated Portal / Email / CRM / Phone source |
| priority | Standard / High / Critical; pre-decision metadata |
| description | fabricated free-text support description; may be incomplete or misleading |
| correct_queue | synthetic gold-standard queue (classification target) |
| initial_queue | synthetic initial manually determined queue |
| missing_fields | simulated indicator for missing intake data |
| rerouted | 1 if first queue differs from correct queue; simulated |
| handle_minutes | invented human handling work, NOT end-to-end waiting |
| wait_hours | invented queue waiting / delay, not automatically AI-reducible |
| sla_breached | simulated breach against per-priority deadline |
| sla_limit_hours | synthetic 8/24/48 hour deadline by priority |
| ai_prediction | most probable ML category on held-out test cases |
| confidence | estimated class probability, not necessarily calibrated probability |
| ai_route | suggested queue OR human-review fallback after policy constraints |
| rule_route | baseline keyword route OR human-review fallback |

### Measurement integrity

- `average handle minutes` and `end-to-end wait hours` differ substantially. Do not claim routing saves **waiting time** without live causal measurement.
- `rerouted` and `missing_fields` are outcomes/observations for root-cause analysis; they are **not** features supplied to the classification model at decision time.
- Case resolution outcome `correct_queue` is a label only, never a prediction feature.
- Artificial text templates repeat over time and are not realistic representations of privacy, seasonality, slang, drift, or long-tail incident handling.
- Precision and coverage are evaluated on separate validation/test datasets; the threshold is selected on validation and locked before testing.
