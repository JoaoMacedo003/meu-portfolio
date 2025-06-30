-- ============================================================================
-- 03_check_coverage_and_missing.sql
--
-- Consultas para verificar cobertura de dados e valores faltantes na tabela “panel”.
-- Inclui contagens e percentuais corrigidos para evitar erro de mistura de agregados.
-- ============================================================================


-- ======================================================================================
-- 1) Contar quantas linhas totais existem na tabela “panel”
--    Mostra o número total de country–years disponíveis (base: todos os registros de GDP).
-- ======================================================================================
SELECT 
  COUNT(*) AS total_rows
FROM panel;


-- ======================================================================================
-- 2) Contar quantos registros têm valor NULL em cada coluna-chave 
--    Ajuda a entender a proporção de missing por variável no painel completo.
-- ======================================================================================
SELECT
  SUM(CASE WHEN gdp_pc_usd              IS NULL THEN 1 ELSE 0 END) AS missing_gdp_pc,
  SUM(CASE WHEN manufacturing_pct_gdp   IS NULL THEN 1 ELSE 0 END) AS missing_manuf,
  SUM(CASE WHEN resource_rents_pct_gdp  IS NULL THEN 1 ELSE 0 END) AS missing_rents,
  SUM(CASE WHEN tertiary_enrolment_pct  IS NULL THEN 1 ELSE 0 END) AS missing_tertiary,
  SUM(CASE WHEN gii_score               IS NULL THEN 1 ELSE 0 END) AS missing_gii,
  SUM(CASE WHEN population_density      IS NULL THEN 1 ELSE 0 END) AS missing_density,
  SUM(CASE WHEN age1564_pct             IS NULL THEN 1 ELSE 0 END) AS missing_age1564
FROM panel;


-- ======================================================================================
-- 3) Calcular o percentual de registros faltantes em cada coluna (em relação ao total)
--    Usamos subconsultas agregadas para evitar o erro de misturar colunas não agregadas.
-- ======================================================================================
WITH
  totals AS (
    SELECT COUNT(*) AS total_rows
    FROM panel
  ),
  misses AS (
    SELECT
      SUM(CASE WHEN gdp_pc_usd              IS NULL THEN 1 ELSE 0 END) AS missing_gdp_pc,
      SUM(CASE WHEN manufacturing_pct_gdp   IS NULL THEN 1 ELSE 0 END) AS missing_manuf,
      SUM(CASE WHEN resource_rents_pct_gdp  IS NULL THEN 1 ELSE 0 END) AS missing_rents,
      SUM(CASE WHEN tertiary_enrolment_pct  IS NULL THEN 1 ELSE 0 END) AS missing_tertiary,
      SUM(CASE WHEN gii_score               IS NULL THEN 1 ELSE 0 END) AS missing_gii,
      SUM(CASE WHEN population_density      IS NULL THEN 1 ELSE 0 END) AS missing_density,
      SUM(CASE WHEN age1564_pct             IS NULL THEN 1 ELSE 0 END) AS missing_age1564
    FROM panel
  )
SELECT
  ROUND(100.0 * misses.missing_gdp_pc             / totals.total_rows, 2) AS pct_missing_gdp_pc,
  ROUND(100.0 * misses.missing_manuf              / totals.total_rows, 2) AS pct_missing_manuf,
  ROUND(100.0 * misses.missing_rents              / totals.total_rows, 2) AS pct_missing_rents,
  ROUND(100.0 * misses.missing_tertiary            / totals.total_rows, 2) AS pct_missing_tertiary,
  ROUND(100.0 * misses.missing_gii                / totals.total_rows, 2) AS pct_missing_gii,
  ROUND(100.0 * misses.missing_density            / totals.total_rows, 2) AS pct_missing_density,
  ROUND(100.0 * misses.missing_age1564            / totals.total_rows, 2) AS pct_missing_age1564
FROM totals
CROSS JOIN misses;