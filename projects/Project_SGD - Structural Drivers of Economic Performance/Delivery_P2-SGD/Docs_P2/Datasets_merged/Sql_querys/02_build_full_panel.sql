-- ============================================================================
-- 02_build_full_panel.sql
--
-- Este script preenche a tabela “panel” com todos os country–years de GDP per
-- capita (2011–2021), fazendo LEFT JOIN em todas as demais tabelas sem filtrar
-- os valores ausentes em GII. Assim, mantemos todos os anos disponíveis para
-- cada país, mesmo que alguns não tenham pontuação de inovação (GII).
-- ============================================================================

-- Passo 1: criar a tabela vazia “panel” -- já feito na 01_query

-- Passo 2: inserir dados na tabela “panel”
-- A base do JOIN é a tabela “gdp” (todos os country–years onde há PIB).
-- Em seguida, fazemos LEFT JOIN em cada tabela de indicador. Se não existir
-- valor para algum country–year em uma dessas tabelas, a coluna respectiva
-- ficará NULL, mas a linha de GDP será mantida.

INSERT INTO panel (
  country,
  year,
  gdp_pc_usd,
  manufacturing_pct_gdp,
  resource_rents_pct_gdp,
  tertiary_enrolment_pct,
  gii_score,
  population_density,
  age1564_pct
)
SELECT
  g.country,                   -- país (ISO-3) da tabela gdp
  g.year,                      -- ano (2011–2021) da tabela gdp
  g.gdp_pc_usd,                -- valor de GDP per capita em USD

  m.manufacturing_pct_gdp,     -- valor de manufatura (% PIB) ou NULL se faltar em manufacturing
  r.resource_rents_pct_gdp,    -- valor de resource rents (% PIB) ou NULL se faltar em resource_rents
  t.tertiary_enrolment_pct,    -- valor de matrícula terciária (% gross) ou NULL se faltar em tertiary_enrolment

  gi.gii_score,                -- valor de GII (0–100) ou NULL se faltar em gii
  d.population_density,        -- densidade populacional (hab/km²) ou NULL se faltar em population_density
  a.age1564_pct                -- % da população 15–64 anos ou NULL se faltar em age1564

FROM gdp AS g
  -- LEFT JOIN em manufatura; mantém a linha mesmo sem manufatura disponível
  LEFT JOIN manufacturing AS m
    ON m.country = g.country
   AND m.year    = g.year

  -- LEFT JOIN em resource_rents; mantém a linha mesmo sem resource rents disponível
  LEFT JOIN resource_rents AS r
    ON r.country = g.country
   AND r.year    = g.year

  -- LEFT JOIN em tertiary_enrolment; mantém a linha mesmo sem tertiary enrolment disponível
  LEFT JOIN tertiary_enrolment AS t
    ON t.country = g.country
   AND t.year    = g.year

  -- LEFT JOIN em gii; mantém a linha mesmo sem GII disponível
  LEFT JOIN gii AS gi
    ON gi.country = g.country
   AND gi.year    = g.year

  -- LEFT JOIN em population_density; mantém a linha mesmo sem population density disponível
  LEFT JOIN population_density AS d
    ON d.country = g.country
   AND d.year    = g.year

  -- LEFT JOIN em age1564; mantém a linha mesmo sem age1564 disponível
  LEFT JOIN age1564 AS a
    ON a.country = g.country
   AND a.year    = g.year;

-- Ao final desta operação, a tabela “panel” conterá uma linha para cada
-- combinação (country, year) presente em “gdp” (2011–2021), com valores
-- NULL nos campos em que faltar algum indicador. Essa estrutura permite
-- manter o painel completo antes de decidir como tratar os NULLs, em especial
-- os de gii_score, diretamente no Python para a modelagem.
