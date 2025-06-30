#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
impute_panel_model.py

Script para ler "panel_model.csv", imputar os valores NULL nas colunas
manufacturing_pct_gdp e tertiary_enrolment_pct e salvar um novo CSV
"panel_model_final.csv" sem quaisquer valores faltantes nessas colunas.
"""

import pandas as pd
import numpy as np

def main():
    # 1) Carrega o CSV exportado do pgAdmin
    panel_model = pd.read_csv("panel_model.csv")
    
    # 2) Checa quantos valores faltam nas duas colunas a imputar
    missing_before = panel_model[[
        "manufacturing_pct_gdp",
        "tertiary_enrolment_pct"
    ]].isna().sum().sum()
    print(f"Total de valores faltantes antes da imputação: {missing_before}")

    # 3) Imputar por média do país para cada coluna
    def impute_country_mean(df, column):
        """
        Para cada país, preenche os NaN de 'column' pela média de 'column' naquele país.
        """
        return df.groupby("country")[column].transform(lambda grp: grp.fillna(grp.mean()))

    for col in ["manufacturing_pct_gdp", "tertiary_enrolment_pct"]:
        panel_model[col] = impute_country_mean(panel_model, col)

    # 4) Verifica quantos faltam após a imputação por país
    missing_mid = panel_model[[
        "manufacturing_pct_gdp",
        "tertiary_enrolment_pct"
    ]].isna().sum().sum()
    print(f"Faltantes após imputação por país: {missing_mid}")

    # 5) Imputar o “fallback” (média global) para os que ainda estiverem NaN
    for col in ["manufacturing_pct_gdp", "tertiary_enrolment_pct"]:
        global_mean = panel_model[col].mean(skipna=True)
        panel_model[col] = panel_model[col].fillna(global_mean)

    # 6) Conferir que não há mais nenhum NaN nessas colunas
    missing_after = panel_model[[
        "manufacturing_pct_gdp",
        "tertiary_enrolment_pct"
    ]].isna().sum().sum()
    print(f"Valores faltantes após imputação global: {missing_after}")

    # 7) (Opcional) criar log do PIB
    panel_model["log_gdp"] = np.log(panel_model["gdp_pc_usd"])

    # 8) Salvar o DataFrame imputado para uso posterior
    panel_model.to_csv("panel_model_final.csv", index=False)
    print("Arquivo 'panel_model_final.csv' salvo com sucesso.")

if __name__ == "__main__":
    main()