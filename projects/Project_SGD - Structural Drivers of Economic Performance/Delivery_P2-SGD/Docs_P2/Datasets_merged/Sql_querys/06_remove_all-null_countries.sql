-- ============================================================================
-- 06_remove_all-null_countries.sql
--
-- Este script remove de “panel_model” exatamente os países que, em 05_list_all-null_countries.sql,
-- foram identificados como sem NENHUM valor válido em manufacturing_pct_gdp, tertiary_enrolment_pct
-- ou population_density. 
-- ============================================================================

-- 1) Remover países sem NENHUM valor de manufacturing_pct_gdp:
DELETE FROM panel_model
WHERE country IN (
  SELECT country
  FROM panel_model
  GROUP BY country
  HAVING COUNT(manufacturing_pct_gdp) = 0
);

-- 2) Remover países sem NENHUM valor de tertiary_enrolment_pct:
DELETE FROM panel_model
WHERE country IN (
  SELECT country
  FROM panel_model
  GROUP BY country
  HAVING COUNT(tertiary_enrolment_pct) = 0
);

-- 3) Remover países sem NENHUM valor de population_density:
DELETE FROM panel_model
WHERE country IN (
  SELECT country
  FROM panel_model
  GROUP BY country
  HAVING COUNT(population_density) = 0
);

-- (Opcional) Verificar quantas linhas restaram:
SELECT COUNT(*) AS rows_model_pruned
FROM panel_model;