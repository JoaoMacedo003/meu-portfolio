import pandas as pd

# Ler o ficheiro TSV (tab-separated)
gii = pd.read_csv("GII_score.tsv", sep="\t")

# manter só o que interessa
gii = gii[["Country", "Year", "Score"]]          

gii = gii.rename(columns={"Country": "country",
                          "Year":    "year",
                          "Score":   "gii_score"})   

# Converter -1 (missing) em NaN
gii["gii_score"] = gii["gii_score"].replace(-1, pd.NA)

# Guardar em CSV separado por vírgula
gii.to_csv("GII_score_long.csv", index=False)