-- ============================================================================
-- 05_list_all-null_countries.sql
--
-- Este script lista, em uma ÚNICA TABELA de saída, os países que não têm
-- nenhum valor não-NULL em cada uma das três colunas:
--   • manufacturing_pct_gdp
--   • tertiary_enrolment_pct
--   • population_density
--
-- O resultado terá três colunas:
--   missing_manuf       → países sem NENHUM valor de manufacturing_pct_gdp
--   missing_tertiary    → países sem NENHUM valor de tertiary_enrolment_pct
--   missing_density     → países sem NENHUM valor de population_density
--
-- ============================================================================

WITH
  -- 1) Países sem NENHUM valor para manufacturing_pct_gdp
  cte_manuf AS (
    SELECT 
      country,
      ROW_NUMBER() OVER (ORDER BY country) AS rn
    FROM panel_model
    GROUP BY country
    HAVING COUNT(manufacturing_pct_gdp) = 0
  ),

  -- 2) Países sem NENHUM valor para tertiary_enrolment_pct
  cte_tertiary AS (
    SELECT 
      country,
      ROW_NUMBER() OVER (ORDER BY country) AS rn
    FROM panel_model
    GROUP BY country
    HAVING COUNT(tertiary_enrolment_pct) = 0
  ),

  -- 3) Países sem NENHUM valor para population_density
  cte_density AS (
    SELECT 
      country,
      ROW_NUMBER() OVER (ORDER BY country) AS rn
    FROM panel_model
    GROUP BY country
    HAVING COUNT(population_density) = 0
  )

-- 4) “Empilhar” (FULL JOIN) as três CTEs pelo número de linha (rn),
--    para produzir uma única tabela com 3 colunas de saída
SELECT
  m.country AS missing_manuf,
  t.country AS missing_tertiary,
  d.country AS missing_density
FROM cte_manuf AS m
FULL JOIN cte_tertiary AS t ON t.rn = m.rn
FULL JOIN cte_density AS d   ON d.rn = COALESCE(m.rn, t.rn)
ORDER BY COALESCE(m.rn, t.rn, d.rn);