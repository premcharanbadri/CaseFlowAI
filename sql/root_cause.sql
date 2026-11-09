-- Works in SQLite 3.25+ / DuckDB with only syntactic changes to timestamp casting.
-- Business question: is misrouting or incomplete intake associated with higher handling time?
SELECT correct_queue,
       COUNT(*) AS cases,
       ROUND(AVG(handle_minutes),2) AS avg_handle_min,
       ROUND(AVG(rerouted)*100,1) AS reroute_pct,
       ROUND(AVG(missing_fields)*100,1) AS missing_fields_pct,
       ROUND(AVG(sla_breached)*100,1) AS sla_breach_pct
FROM cases
GROUP BY correct_queue
ORDER BY cases DESC;

-- Paired operational comparison (observational, NOT causal).
SELECT rerouted, COUNT(*) AS cases,
       ROUND(AVG(handle_minutes),2) AS average_handle_min,
       ROUND(AVG(wait_hours),2) AS average_wait_hours,
       ROUND(AVG(sla_breached)*100,2) AS sla_breach_pct
FROM cases
GROUP BY rerouted;

-- Monthly trend; use calendar-stable cohorts.
SELECT SUBSTR(created_at,1,7) AS month,
       COUNT(*) AS n_cases,
       ROUND(AVG(rerouted)*100,2) AS reroute_pct,
       ROUND(AVG(sla_breached)*100,2) AS sla_breach_pct,
       ROUND(AVG(handle_minutes),2) AS avg_handle_min
FROM cases
GROUP BY SUBSTR(created_at,1,7)
ORDER BY month;
