import pandas as pd

# Ler o CSV bruto, pulando as 4 linhas de cabeçalho e as 6 de rodapé
df_raw = pd.read_csv(
    "a8d50533-5f41-42b8-87cb-2126a3ec15dd_Data.csv",    # MUDAR AQUI FICHEIRO PARA LIMPEZA
    skipfooter=6,
    engine="python",      
    na_values=".."
)

#  Manter apenas Country Code e os anos 2011–2021
#    – as colunas de anos geralmente vêm como "2011 [YR2011]", "2012 [YR2012]", etc.
cols_to_keep = ["Country Code"] + [str(y) + " [YR" + str(y) + "]" for y in range(2011, 2022)]
df = df_raw[cols_to_keep].copy()

# “Derreter” (melt) para formato longo
df_long = df.melt(
    id_vars=["Country Code"],
    var_name="year_label",
    value_name="age1564_pct"       # MUDAR NOME DA COLUNA QUE SE QUER
)

# Extrair somente o ano numérico, removendo o texto " [YRXXXX]"
df_long["year"] = df_long["year_label"].str.extract(r"(\d{4})").astype(int)

# Filtrar apenas 2011–2021 (caso o arquivo traga colunas além desse intervalo)
df_long = df_long[(df_long["year"] >= 2011) & (df_long["year"] <= 2021)]

# 6) Renomear “Country Code”  e reorganizar colunas
df_long = df_long.rename(columns={"Country Code": "country"})
df_long = df_long[["country", "year", "age1564_pct"]]                   # MUDAR NOME DA COLUNA QUE SE QUER

# Ordena primeiro por “country” e depois por “year”
df_long = df_long.sort_values(by=["country", "year"])

# Salvar o CSV final
df_long.to_csv("age1564_pct_long.csv", index=False)   # ESCOLHER AQUI O NOME RESULTANTE DO FICHEIRO DE OUTPUT
