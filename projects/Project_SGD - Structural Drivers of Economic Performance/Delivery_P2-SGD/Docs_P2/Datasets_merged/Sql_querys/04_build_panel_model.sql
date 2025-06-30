-- ============================================================================
-- 04_build_panel_model.sql
--
-- Este script gera a tabela “panel_model” a partir de “panel”, removendo apenas
-- registros que não têm valores de GDP per capita ou GII. Esses registros não podem
-- ser usados na modelagem, pois “gii_score” e “gdp_pc_usd” são variáveis consideradas essenciais neste estudo.
-- ============================================================================


-- ======================================================================================
-- 1) Criar (se não existir) a tabela “panel_model” com a mesma estrutura de “panel”:
--    Armazena country–year completos somente com GDP e GII válidos.
-- ======================================================================================
DROP TABLE IF EXISTS panel_model;
CREATE TABLE panel_model AS
SELECT *
FROM panel
WHERE gdp_pc_usd IS NOT NULL    -- Garante que o target (PIB per capita) não esteja ausente
  AND gii_score  IS NOT NULL;   -- Garante que a variável-chave (inovação) não esteja ausente


-- ======================================================================================
-- 2) Verificar quantas linhas restaram em “panel_model” após a remoção de missings
--    Mostra o total de observações disponíveis para regressão (sem NULL em GDP ou GII).
-- ======================================================================================
SELECT 
  COUNT(*) AS rows_model 
FROM panel_model;


-- ======================================================================================
-- 3) Contar quantos registros ainda têm missing em cada uma das demais variáveis
--    (manufatura, recursos, educação superior, densidade e estrutura etária).
--    Ajuda a decidir se é necessário imputar ou descartar outros missings antes do modelo.
-- ======================================================================================
SELECT
  SUM(CASE WHEN manufacturing_pct_gdp   IS NULL THEN 1 ELSE 0 END) AS missing_manuf_after,
  SUM(CASE WHEN resource_rents_pct_gdp  IS NULL THEN 1 ELSE 0 END) AS missing_rents_after,
  SUM(CASE WHEN tertiary_enrolment_pct  IS NULL THEN 1 ELSE 0 END) AS missing_tertiary_after,
  SUM(CASE WHEN population_density      IS NULL THEN 1 ELSE 0 END) AS missing_density_after,
  SUM(CASE WHEN age1564_pct             IS NULL THEN 1 ELSE 0 END) AS missing_age1564_after
FROM panel_model;