-- ==============================================
-- TALENT MATCH ENGINE SQL (FINAL, PARAMETERIZED)
-- ==============================================

-- 1️⃣ BENCHMARK PARAMETER (role-based OR fallback)
WITH benchmark_param AS (
  SELECT unnest(selected_talent_ids) AS employee_id
  FROM talent_benchmarks
  WHERE job_vacancy_id = :job_vacancy_id
),

selected_benchmark AS (
  SELECT e.employee_id
  FROM employees e
  WHERE e.employee_id IN (SELECT employee_id FROM benchmark_param)
     OR e.employee_id IN (
        SELECT employee_id 
        FROM performance_yearly p
        WHERE p.rating = 5
     )
),

-- 2️⃣ BASELINE MEDIAN PER TV
benchmark_profile AS (
  -- Competency
  SELECT 'Competency' AS variable_type,
         dp.pillar_label AS variable_name,
         percentile_cont(0.5) WITHIN GROUP (ORDER BY c.score) AS baseline_score
  FROM competencies_yearly c
  JOIN dim_competency_pillars dp USING(pillar_code)
  JOIN selected_benchmark sb USING(employee_id)
  GROUP BY dp.pillar_label

  UNION ALL
  -- Psychometric
  SELECT 'Psychometric','IQ',
         percentile_cont(0.5) WITHIN GROUP (ORDER BY pf.iq)
  FROM profiles_psych pf JOIN selected_benchmark sb USING(employee_id)

  UNION ALL
  SELECT 'Psychometric','GTQ',
         percentile_cont(0.5) WITHIN GROUP (ORDER BY pf.gtq)
  FROM profiles_psych pf JOIN selected_benchmark sb USING(employee_id)

  UNION ALL
  -- Behavioral
  SELECT 'Behavioral', s.theme,
         100.0 AS baseline_score
  FROM strengths s
  JOIN selected_benchmark sb USING(employee_id)
  WHERE s.rank <= 5
),

-- 3️⃣ CANDIDATE PROFILE
candidate_profile AS (
  SELECT e.employee_id, dp.pillar_label, AVG(c.score) AS score
  FROM competencies_yearly c
  JOIN dim_competency_pillars dp USING(pillar_code)
  JOIN employees e USING(employee_id)
  GROUP BY e.employee_id, dp.pillar_label
),

-- 4️⃣ COMBINE COMPETENCY + PSYCHOMETRIC + BEHAVIORAL
candidate_profile_pivot AS (
  SELECT 
    cp.employee_id,
    cp.pillar_label,
    AVG(cp.score) AS score,
    AVG(ps.iq) AS iq,
    AVG(ps.gtq) AS gtq,
    COUNT(DISTINCT s.theme) FILTER (WHERE s.rank <= 5) AS strength_count
  FROM candidate_profile cp
  LEFT JOIN profiles_psych ps USING(employee_id)
  LEFT JOIN strengths s USING(employee_id)
  GROUP BY cp.employee_id, cp.pillar_label
),

-- 5️⃣ UNPIVOT KE LEVEL TV
candidate_tv AS (
  SELECT employee_id, variable_type, variable_name, user_score
  FROM candidate_profile_pivot cpp,
  LATERAL (
    VALUES
      ('Competency', cpp.pillar_label, cpp.score),
      ('Psychometric','IQ', cpp.iq),
      ('Psychometric','GTQ', cpp.gtq),
      ('Behavioral','Strength Count', cpp.strength_count)
  ) v(variable_type, variable_name, user_score)
),

-- 6️⃣ MATCH RATE PER TV (0–100%)
tv_match AS (
  SELECT ct.employee_id, ct.variable_type, ct.variable_name,
         bp.baseline_score, ct.user_score,
         ROUND(LEAST((ct.user_score / NULLIF(bp.baseline_score,0))*100,100)::numeric,2) AS tv_match_rate
  FROM candidate_tv ct
  LEFT JOIN benchmark_profile bp USING(variable_name)
),

-- 7️⃣ MATCH RATE PER TGV
tgv_match AS (
  SELECT employee_id, variable_type,
         ROUND(AVG(tv_match_rate)::numeric,2) AS tgv_match_rate
  FROM tv_match WHERE tv_match_rate IS NOT NULL
  GROUP BY employee_id, variable_type
),

-- 8️⃣ SUCCESS INDEX (IQ/GTQ)
success_index AS (
  SELECT employee_id,
         ROUND(((0.6*COALESCE(iq,0)) + (0.4*COALESCE(gtq,0)))::numeric,2) AS raw_score
  FROM profiles_psych
),
success_scaled AS (
  SELECT employee_id,
         ROUND(100*(raw_score - MIN(raw_score) OVER()) /
               NULLIF(MAX(raw_score) OVER() - MIN(raw_score) OVER(),0),2) AS success_scaled
  FROM success_index
),

-- 9️⃣ FINAL WEIGHTED MATCH (0–100%) + CATEGORY
final_match AS (
  SELECT 
    t.employee_id,
    ROUND(LEAST((COALESCE(AVG(t.tgv_match_rate),0)*0.7 +
                 COALESCE(s.success_scaled,0)*0.3),100)::numeric,2) AS final_match_rate,
    CASE 
      WHEN (COALESCE(AVG(t.tgv_match_rate),0)*0.7 + COALESCE(s.success_scaled,0)*0.3) > 100 THEN 'Exceptional'
      WHEN (COALESCE(AVG(t.tgv_match_rate),0)*0.7 + COALESCE(s.success_scaled,0)*0.3) >= 80 THEN 'High Match'
      WHEN (COALESCE(AVG(t.tgv_match_rate),0)*0.7 + COALESCE(s.success_scaled,0)*0.3) >= 60 THEN 'Moderate Match'
      ELSE 'Low Match'
    END AS match_category
  FROM tgv_match t
  LEFT JOIN success_scaled s USING(employee_id)
  GROUP BY t.employee_id, s.success_scaled
)

-- 🔟 FINAL OUTPUT (include TGV level)
SELECT 
  e.employee_id,
  e.fullname,
  t.variable_type AS tgv_name,             -- ✅ tambahkan kolom TGV
  t.tgv_match_rate,                        -- ✅ tambahkan rata-rata match TGV
  dir.name AS directorate,
  pos.name AS position,
  grd.name AS grade,
  f.final_match_rate,
  f.match_category
FROM final_match f
LEFT JOIN tgv_match t USING (employee_id)
JOIN employees e USING (employee_id)
LEFT JOIN dim_positions pos ON e.position_id = pos.position_id
LEFT JOIN dim_grades grd ON e.grade_id = grd.grade_id
LEFT JOIN dim_directorates dir ON e.directorate_id = dir.directorate_id
ORDER BY f.final_match_rate DESC;

