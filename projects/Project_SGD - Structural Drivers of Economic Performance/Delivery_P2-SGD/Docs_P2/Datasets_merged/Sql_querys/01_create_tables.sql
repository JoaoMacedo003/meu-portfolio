-- 1) Tabela de GDP per capita
CREATE TABLE gdp (
  country       TEXT,
  year          INT,
  gdp_pc_usd    FLOAT
);

-- 2) Tabela de Manufatura
CREATE TABLE manufacturing (
  country                 TEXT,
  year                    INT,
  manufacturing_pct_gdp   FLOAT
);

-- 3) Tabela de Rendas de Recursos Naturais
CREATE TABLE resource_rents (
  country                  TEXT,
  year                     INT,
  resource_rents_pct_gdp   FLOAT
);

-- 4) Tabela de Matrícula no Ensino Superior
CREATE TABLE tertiary_enrolment (
  country                  TEXT,
  year                     INT,
  tertiary_enrolment_pct   FLOAT
);

-- 5) Tabela de Densidade Populacional
CREATE TABLE population_density (
  country            TEXT,
  year               INT,
  population_density FLOAT
);

-- 6) Tabela de População 15–64 anos
CREATE TABLE age1564 (
  country      TEXT,
  year         INT,
  age1564_pct  FLOAT
);

-- 7) Tabela do Global Innovation Index
CREATE TABLE gii (
  country    TEXT,
  year       INT,
  gii_score  FLOAT
);

-- 8) Tabela painel unificada, ficará vazia até o join

CREATE TABLE panel (
  country                 TEXT,
  year                    INT,
  gdp_pc_usd              FLOAT,
  manufacturing_pct_gdp   FLOAT,
  resource_rents_pct_gdp  FLOAT,
  tertiary_enrolment_pct  FLOAT,
  gii_score               FLOAT,
  population_density      FLOAT,
  age1564_pct             FLOAT
);