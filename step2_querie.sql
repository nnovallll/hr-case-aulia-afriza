-- =============================================
-- STEP 2: TALENT MATCHING ENGINE (Final Version)
-- PostgreSQL, Parameterized & Modular
-- =============================================

WITH 
-- 1️⃣ Benchmark Employees
selected_benchmark AS (
  SELECT DISTINCT e.employee_id
  FROM performance_yearly p
  JOIN employees e USING(employee_id)
  WHERE p.rating = 5
),



-- 2️⃣ Baseline Median per TV
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
  -- Behavioral (contoh 5 top strengths)
  SELECT 'Behavioral', s.theme,
         100.0 AS baseline_score
  FROM strengths s
  JOIN selected_benchmark sb USING(employee_id)
  WHERE s.rank <= 5
),

-- 3️⃣ Candidate Profile
candidate_profile AS (
  SELECT e.employee_id,
         dp.pillar_label, AVG(c.score) AS score
  FROM competencies_yearly c
  JOIN dim_competency_pillars dp USING(pillar_code)
  JOIN employees e USING(employee_id)
  GROUP BY e.employee_id, dp.pillar_label
),

-- 4️⃣ Combine Competency + Psychometric + Behavioral
candidate_profile_pivot AS (
  SELECT 
    cp.employee_id,
    cp.pillar_label,
    AVG(cp.score) AS score, -- ✅ perbaikan di sini
    AVG(ps.iq) AS iq,
    AVG(ps.gtq) AS gtq,
    COUNT(DISTINCT s.theme) FILTER (WHERE s.rank <= 5) AS strength_count
  FROM candidate_profile cp
  LEFT JOIN profiles_psych ps USING(employee_id)
  LEFT JOIN strengths s USING(employee_id)
  GROUP BY cp.employee_id, cp.pillar_label
),


-- 5️⃣ Unpivot ke level TV
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

-- 6️⃣ Match Rate per TV
tv_match AS (
  SELECT ct.employee_id, ct.variable_type, ct.variable_name,
         bp.baseline_score, ct.user_score,
         CASE WHEN ct.user_score IS NULL OR bp.baseline_score IS NULL THEN NULL
              ELSE ROUND(LEAST((ct.user_score / bp.baseline_score)*100,200)::numeric,2)
         END AS tv_match_rate
  FROM candidate_tv ct
  LEFT JOIN benchmark_profile bp USING(variable_name)
),

-- 7️⃣ Match Rate per TGV
tgv_match AS (
  SELECT employee_id, variable_type,
         ROUND(AVG(tv_match_rate)::numeric,2) AS tgv_match_rate
  FROM tv_match WHERE tv_match_rate IS NOT NULL
  GROUP BY employee_id, variable_type
),

-- 8️⃣ Success Index (Scaled)
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

-- 9️⃣ Final Weighted Match
final_match AS (
  SELECT 
    t.employee_id,
    ROUND(LEAST((COALESCE(AVG(t.tgv_match_rate),0)*0.7 +
                 COALESCE(s.success_scaled,0)*0.3), 100)::numeric,2) AS final_match_rate,
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


SELECT e.employee_id AS "Candidate ID",
       dir.name AS "Directorate",
       pos.name AS "Position",
       grd.name AS "Grade",
       tv.variable_type AS "TGV",
       tv.variable_name AS "TV",
       ROUND(tv.baseline_score::numeric,2) AS "Baseline (TV)",
       ROUND(tv.user_score::numeric,2) AS "Candidate (TV)",
       ROUND(tv.tv_match_rate::numeric,2) AS "TV Match %",
       ROUND(tgv.tgv_match_rate::numeric,2) AS "TGV Avg %",
       ROUND(f.final_match_rate::numeric,2) AS "Final Match %"
FROM tv_match tv
LEFT JOIN tgv_match tgv USING(employee_id,variable_type)
LEFT JOIN final_match f USING(employee_id)
LEFT JOIN employees e USING(employee_id)
LEFT JOIN dim_positions pos ON e.position_id=pos.position_id
LEFT JOIN dim_grades grd ON e.grade_id=grd.grade_id
LEFT JOIN dim_directorates dir ON e.directorate_id=dir.directorate_id
ORDER BY "Final Match %" DESC;

