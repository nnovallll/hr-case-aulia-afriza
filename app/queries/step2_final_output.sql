-- ================================================
-- STEP 2: Talent Variable & Group Matching (Streamlit Ready)
-- Version: v4 | PostgreSQL Compatible | Final Output: final_output_step2
-- ================================================

WITH
-- 1️⃣ High performer benchmark
selected_benchmark AS (
  SELECT DISTINCT employee_id, year AS perf_year
  FROM performance_yearly
  WHERE rating = 5
),

-- 2️⃣ Year reference
max_year_perf AS (
  SELECT employee_id, MAX(year) AS max_year
  FROM performance_yearly
  GROUP BY employee_id
),

-- 3️⃣ Benchmark profile (median baseline)
benchmark_profile AS (
  SELECT
    'Competency' AS variable_type,
    dp.pillar_label AS variable_name,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY c.score) AS baseline_score
  FROM competencies_yearly c
  JOIN dim_competency_pillars dp ON c.pillar_code = dp.pillar_code
  JOIN selected_benchmark sb ON sb.employee_id = c.employee_id AND sb.perf_year = c.year
  WHERE c.score BETWEEN 1 AND 5
  GROUP BY dp.pillar_label

  UNION ALL

  SELECT
    'Psychometric', 'IQ',
    percentile_cont(0.5) WITHIN GROUP (ORDER BY pf.iq)
  FROM profiles_psych pf
  WHERE pf.employee_id IN (SELECT employee_id FROM selected_benchmark)

  UNION ALL

  SELECT
    'Psychometric', 'GTQ',
    percentile_cont(0.5) WITHIN GROUP (ORDER BY pf.gtq)
  FROM profiles_psych pf
  WHERE pf.employee_id IN (SELECT employee_id FROM selected_benchmark)
),

-- 4️⃣ Candidate competency profile
candidate_profile AS (
  SELECT DISTINCT c.employee_id, c.year,
    MAX(CASE WHEN dp.pillar_label = 'Commercial Savvy & Impact' THEN c.score END) AS commercial_savvy,
    MAX(CASE WHEN dp.pillar_label = 'Curiosity & Experimentation' THEN c.score END) AS curiosity,
    MAX(CASE WHEN dp.pillar_label = 'Forward Thinking & Clarity' THEN c.score END) AS forward_thinking,
    MAX(CASE WHEN dp.pillar_label = 'Growth Drive & Resilience' THEN c.score END) AS growth_drive,
    MAX(CASE WHEN dp.pillar_label = 'Insight & Decision Sharpness' THEN c.score END) AS insight_decision,
    MAX(CASE WHEN dp.pillar_label = 'Lead, Inspire & Empower' THEN c.score END) AS leadership,
    MAX(CASE WHEN dp.pillar_label = 'Quality Delivery Discipline' THEN c.score END) AS quality_discipline,
    MAX(CASE WHEN dp.pillar_label = 'Social Empathy & Awareness' THEN c.score END) AS empathy,
    MAX(CASE WHEN dp.pillar_label = 'Synergy & Team Orientation' THEN c.score END) AS teamwork,
    MAX(CASE WHEN dp.pillar_label = 'Value Creation for Users' THEN c.score END) AS value_creation
  FROM competencies_yearly c
  JOIN dim_competency_pillars dp ON dp.pillar_code = c.pillar_code
  JOIN max_year_perf m ON m.employee_id = c.employee_id AND m.max_year = c.year
  GROUP BY c.employee_id, c.year
),

-- 5️⃣ Merge psychometric + competency
candidate_profile_pivot AS (
  SELECT
    cp.employee_id,
    cp.commercial_savvy, cp.curiosity, cp.forward_thinking, cp.growth_drive,
    cp.insight_decision, cp.leadership, cp.quality_discipline, cp.empathy,
    cp.teamwork, cp.value_creation,
    ps.iq, ps.gtq,
    e.directorate_id, e.position_id, e.grade_id
  FROM candidate_profile cp
  LEFT JOIN profiles_psych ps ON ps.employee_id = cp.employee_id
  LEFT JOIN employees e ON e.employee_id = cp.employee_id
),

-- 6️⃣ Unpivot to Talent Variable (TV) Level
candidate_tv AS (
  SELECT
    cpp.employee_id,
    v.variable_type,
    v.variable_name,
    v.user_score
  FROM candidate_profile_pivot cpp
  CROSS JOIN LATERAL (
    VALUES
      ('Competency','Commercial Savvy & Impact', cpp.commercial_savvy),
      ('Competency','Curiosity & Experimentation', cpp.curiosity),
      ('Competency','Forward Thinking & Clarity', cpp.forward_thinking),
      ('Competency','Growth Drive & Resilience', cpp.growth_drive),
      ('Competency','Insight & Decision Sharpness', cpp.insight_decision),
      ('Competency','Lead, Inspire & Empower', cpp.leadership),
      ('Competency','Quality Delivery Discipline', cpp.quality_discipline),
      ('Competency','Social Empathy & Awareness', cpp.empathy),
      ('Competency','Synergy & Team Orientation', cpp.teamwork),
      ('Competency','Value Creation for Users', cpp.value_creation),
      ('Psychometric','IQ', cpp.iq),
      ('Psychometric','GTQ', cpp.gtq)
  ) AS v(variable_type, variable_name, user_score)
),

-- 7️⃣ Compute TV match rate
tv_match AS (
  SELECT
    ct.employee_id,
    ct.variable_type,
    ct.variable_name,
    bp.baseline_score,
    ct.user_score,
    CASE
      WHEN ct.user_score IS NULL OR bp.baseline_score IS NULL THEN NULL
      WHEN bp.baseline_score = 0 THEN NULL
      ELSE ROUND(LEAST((ct.user_score / bp.baseline_score) * 100, 200)::numeric, 2)
    END AS tv_match_rate
  FROM candidate_tv ct
  LEFT JOIN benchmark_profile bp ON bp.variable_name = ct.variable_name
),

-- 8️⃣ Aggregate TGV match
tgv_match AS (
  SELECT
    employee_id,
    variable_type AS tgv_name,
    ROUND(AVG(tv_match_rate)::numeric, 2) AS tgv_match_rate
  FROM tv_match
  WHERE tv_match_rate IS NOT NULL
  GROUP BY employee_id, variable_type
),

-- 9️⃣ Success Index (scaled 0–100)
success_index AS (
  SELECT
    employee_id,
    ROUND(((0.6 * COALESCE(iq,0)) + (0.4 * COALESCE(gtq,0)))::numeric, 2) AS raw_success,
    MIN(ROUND(((0.6 * COALESCE(iq,0)) + (0.4 * COALESCE(gtq,0)))::numeric, 2)) OVER () AS min_succ,
    MAX(ROUND(((0.6 * COALESCE(iq,0)) + (0.4 * COALESCE(gtq,0)))::numeric, 2)) OVER () AS max_succ
  FROM profiles_psych
),
success_index_scaled AS (
  SELECT
    employee_id,
    ROUND((100 * (raw_success - min_succ) / NULLIF(max_succ - min_succ,0))::numeric, 2) AS success_score_scaled
  FROM success_index
),

-- 🔟 Final Match Rate
final_match AS (
  SELECT
    tm.employee_id,
    ROUND(AVG(tm.tgv_match_rate)::numeric,2) AS avg_tgv_match_rate,
    ROUND(
      (COALESCE(AVG(tm.tgv_match_rate),0) * 0.7 +
       COALESCE(si.success_score_scaled,0) * 0.3)::numeric,
      4
    ) AS final_match_rate
  FROM tgv_match tm
  LEFT JOIN success_index_scaled si USING(employee_id)
  GROUP BY tm.employee_id, si.success_score_scaled
),

-- 11️⃣ Final Output Step 2
final_output_step2 AS (
  SELECT
    e.employee_id AS candidate_id,
    d.name AS directorate,
    p.name AS position_title,
    g.name AS grade,
    tv.variable_type AS tgv_name,
    tv.variable_name AS tv_name,
    tv.baseline_score,
    tv.user_score,
    tv.tv_match_rate,
    tgv.tgv_match_rate,
    fm.final_match_rate
  FROM tv_match tv
  LEFT JOIN tgv_match tgv ON tv.employee_id = tgv.employee_id AND tv.variable_type = tgv.tgv_name
  LEFT JOIN final_match fm ON tv.employee_id = fm.employee_id
  LEFT JOIN employees e ON tv.employee_id = e.employee_id
  LEFT JOIN dim_directorates d ON e.directorate_id = d.directorate_id
  LEFT JOIN dim_positions p ON e.position_id = p.position_id
  LEFT JOIN dim_grades g ON e.grade_id = g.grade_id
)

-- FINAL SELECT
SELECT * FROM final_output_step2
ORDER BY final_match_rate DESC, tgv_match_rate DESC;
