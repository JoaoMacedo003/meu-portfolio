# === Importação das bibliotecas ===
import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import statsmodels.formula.api as smf
from sklearn.model_selection import cross_val_score


# === Criar diretório para guardar gráficos ===
os.makedirs("plots", exist_ok=True)


# === Carregar o dataset e verificar log_gdp ===
def carregar_dados():
    df = pd.read_csv("panel_model_final.csv")
    if "log_gdp" not in df.columns:
        df["log_gdp"] = np.log(df["gdp_pc_usd"])
    return df


# === Verificar cobertura de anos por país e filtrar ===
def verificar_cobertura(df, min_anos=3):
    cobertura = df["country"].value_counts()
    print(f"\n=== Estatísticas de cobertura por país (mínimo {min_anos} anos) ===")
    print(cobertura.describe())

    poucos_anos = cobertura[cobertura < min_anos]
    if not poucos_anos.empty:
        print(f"\nPaíses com menos de {min_anos} anos (serão excluídos):")
        print(poucos_anos)

    df_filtrado = df[df["country"].isin(cobertura[cobertura >= min_anos].index)]
    print(f"\nTotal de países após filtragem: {df_filtrado['country'].nunique()} (de {len(cobertura)})")
    print("\n=====================================================")
    print("\n=====================================================\n\n")
    return df_filtrado


# === Gráficos de distribuição do PIB antes e depois do log ===
def graficos_distribuicao(df):
    plt.figure()
    sns.histplot(df["gdp_pc_usd"], bins=50, kde=True)
    plt.title("Distribuição do PIB per capita (USD)")
    plt.savefig("plots/hist_gdp_pc_usd.png")
    plt.close()

    plt.figure()
    sns.histplot(df["log_gdp"], bins=50, kde=True)
    plt.title("Distribuição do log do PIB per capita")
    plt.savefig("plots/hist_log_gdp.png")
    plt.close()


# === Gráficos de evolução para os países com maior e menor PIB per capita médio ===
def evolucao_top_bottom(df, X_cols, top_n=5):
    # Garantir que 'year' é tratado como número inteiro (para ordenação correta no eixo X)
    df["year"] = df["year"].astype(int)

    # Calcular o PIB per capita médio de cada país ao longo dos anos
    media_pib = df.groupby("country")["gdp_pc_usd"].mean()

    # Selecionar os 'top_n' países com maior PIB médio
    top_paises = media_pib.nlargest(top_n).index

    # Selecionar os 'top_n' países com menor PIB médio
    bottom_paises = media_pib.nsmallest(top_n).index

    # Para cada variável explicativa...
    for col in X_cols:
        # === Gráfico para os países com maior PIB médio ===
        plt.figure(figsize=(12, 5))
        for country in top_paises:
            subset = df[df["country"] == country]
            plt.plot(subset["year"], subset[col], label=country)
        plt.title(f"TOP {top_n}: Evolução de {col} (maior PIB médio)")
        plt.xlabel("Ano")
        plt.ylabel(col)
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"plots/evolucao_top_{top_n}_{col}.png")
        plt.close()

        # === Gráfico para os países com menor PIB médio ===
        plt.figure(figsize=(12, 5))
        for country in bottom_paises:
            subset = df[df["country"] == country]
            plt.plot(subset["year"], subset[col], label=country)
        plt.title(f"BOTTOM {top_n}: Evolução de {col} (menor PIB médio)")
        plt.xlabel("Ano")
        plt.ylabel(col)
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"plots/evolucao_bottom_{top_n}_{col}.png")
        plt.close()


# === Análise Exploratória (EDA) ===
def eda(df, X_cols):
    import matplotlib.ticker as ticker

    # Dicionário com descrições legíveis para os nomes das variáveis
    descricoes = {
        "manufacturing_pct_gdp": "Indústria (% do PIB)",
        "resource_rents_pct_gdp": "Rendas de recursos naturais (% do PIB)",
        "tertiary_enrolment_pct": "Matrícula bruta no ensino superior (% GER)",
        "gii_score": "Índice Global de Inovação (0–100)",
        "population_density": "Densidade populacional (pessoas/km²)",
        "age1564_pct": "População entre 15–64 anos (%)",
        "log_gdp": "Logaritmo do PIB per capita (USD)"
    }

    # Matriz de correlação com melhoria visual
    corr = df[["log_gdp"] + X_cols].corr()
    plt.figure(figsize=(14, 12))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", annot_kws={"size": 10})
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.title("Matriz de Correlação")
    plt.tight_layout()
    plt.savefig("plots/heatmap_corr.png")
    plt.close()

    # Scatterplots com descrições legíveis nos eixos
    for col in X_cols:
        plt.figure(figsize=(8, 6))
        sns.regplot(
            data=df,
            x=col,
            y="log_gdp",
            scatter_kws={'alpha': 0.5},
            line_kws={"color": "red"}
        )
        plt.title(f"{descricoes.get(col, col)} vs {descricoes['log_gdp']}")
        plt.xlabel(descricoes.get(col, col))
        plt.ylabel(descricoes["log_gdp"])
        plt.tight_layout()
        plt.savefig(f"plots/scatter_{col}.png")
        plt.close()
    
    # === 1. Tabela estatística descritiva ===
    descr_stats = df[X_cols + ['log_gdp']].describe().round(2)
    print("\n=== Descriptive Statistics ===")
    print(descr_stats)
    descr_stats.to_csv("plots/describe_table.csv")  # salva como CSV

    # === 2. KDE plots (densidade suave) ===
    plt.figure()
    sns.kdeplot(df["gdp_pc_usd"], fill=True)
    plt.title("Densidade do PIB per capita (USD)")
    plt.xlabel("PIB per capita")
    plt.tight_layout()
    plt.savefig("plots/kde_gdp_pc_usd.png")
    plt.close()

    plt.figure()
    sns.kdeplot(df["log_gdp"], fill=True)
    plt.title("Densidade do log do PIB per capita")
    plt.xlabel("log(PIB per capita)")
    plt.tight_layout()
    plt.savefig("plots/kde_log_gdp.png")
    plt.close()
    print("\n=====================================================")
    print("\n=====================================================\n\n")
        

# === Regressão OLS com normalização e erros clusterizados ===
def regressao_ols(df, X_cols):
    # Normalização das variáveis explicativas
    scaler = StandardScaler()
    df_scaled = df.copy()
    df_scaled[X_cols] = scaler.fit_transform(df[X_cols])

    # Formula da regressão (ex: log_gdp ~ x1 + x2 + ...)
    formula = "log_gdp ~ " + " + ".join(X_cols)

    # Regressão OLS com erros clusterizados por país
    model = smf.ols(formula, data=df_scaled).fit(cov_type="cluster", cov_kwds={"groups": df["country"]})

    print("\n=== OLS COMPLETO (com variáveis normalizadas) ===")
    print(model.summary())

    # Exportar coeficientes para CSV
    coef_table = model.summary2().tables[1]
    coef_table.to_csv("plots/ols_coefficients_normalized.csv")

    # Preparar dados para o gráfico
    coef_table = coef_table.reset_index().rename(columns={"index": "Variable"})
    coef_table = coef_table[coef_table["Variable"] != "Intercept"]
    coef_table["Coef"] = coef_table["Coef."]
    coef_table["Lower"] = coef_table["[0.025"]
    coef_table["Upper"] = coef_table["0.975]"]
    coef_table["abs_coef"] = coef_table["Coef"].abs()
    coef_table = coef_table.sort_values("abs_coef", ascending=True)

    # Gráfico de barras com intervalos de confiança
    plt.figure(figsize=(10, 6))
    sns.pointplot(x="Coef", y="Variable", data=coef_table, color="blue", linestyle='none')
    for i, row in coef_table.iterrows():
        plt.plot([row["Lower"], row["Upper"]], [i, i], color="gray", lw=2)
    plt.axvline(0, color="red", linestyle="--")
    plt.title("Coeficientes da Regressão OLS (com variáveis normalizadas)")
    plt.xlabel("Coeficiente estimado")
    plt.ylabel("Variável explicativa")
    plt.tight_layout()
    plt.savefig("plots/ols_coef_normalized.png")
    plt.close()


# === Gráfico dos coeficientes com intervalos de confiança ===
def plot_ols_model(model, nome_figura):
    # Extração dos coeficientes e intervalos de confiança
    coef_table = model.summary2().tables[1].reset_index().rename(columns={"index": "Variable"})
    coef_table = coef_table[coef_table["Variable"] != "Intercept"]
    coef_table["Coef"] = coef_table["Coef."]
    coef_table["Lower"] = coef_table["[0.025"]
    coef_table["Upper"] = coef_table["0.975]"]
    coef_table["abs_coef"] = coef_table["Coef"].abs()
    coef_table = coef_table.sort_values("abs_coef", ascending=True)

    # Gráfico com ponto e barra de intervalo
    plt.figure(figsize=(10, 6))
    sns.pointplot(x="Coef", y="Variable", data=coef_table, color="blue", linestyle='none')
    for i, row in coef_table.iterrows():
        plt.plot([row["Lower"], row["Upper"]], [i, i], color="gray", lw=2)
    plt.axvline(0, color="red", linestyle="--")
    plt.title(f"Coeficientes da {nome_figura} (95% IC)")
    plt.xlabel("Coeficiente estimado")
    plt.ylabel("Variável explicativa")
    plt.tight_layout()
    plt.savefig(f"plots/ols_coef_{nome_figura.lower().replace(' ', '_')}.png")
    plt.close()


# === Regressões hierárquicas com normalização ===
def regressao_hierarquica(df):
    # Selecionar variáveis a normalizar
    scaler = StandardScaler()
    cols = [
        "manufacturing_pct_gdp",
        "resource_rents_pct_gdp",
        "gii_score",
        "tertiary_enrolment_pct"
    ]
    df_scaled = df.copy()
    df_scaled[cols] = scaler.fit_transform(df[cols])

    # Modelo 1: indústria + recursos
    m1 = smf.ols(
        "log_gdp ~ manufacturing_pct_gdp + resource_rents_pct_gdp",
        data=df_scaled
    ).fit(cov_type="cluster", cov_kwds={"groups": df["country"]})

    # Modelo 2: + inovação
    m2 = smf.ols(
        "log_gdp ~ manufacturing_pct_gdp + resource_rents_pct_gdp + gii_score",
        data=df_scaled
    ).fit(cov_type="cluster", cov_kwds={"groups": df["country"]})

    # Modelo 3: + inovação + educação
    m3 = smf.ols(
        "log_gdp ~ manufacturing_pct_gdp + resource_rents_pct_gdp + gii_score + tertiary_enrolment_pct",
        data=df_scaled
    ).fit(cov_type="cluster", cov_kwds={"groups": df["country"]})

    # Mostrar os resultados dos modelos
    print("\n=== MODELO 1: Indústria + Recursos ===")
    print(m1.summary())
    print("\n=== MODELO 2: + Inovação (sem educação) ===")
    print(m2.summary())
    print("\n=== MODELO 3: + Inovação + Educação ===")
    print(m3.summary())

    # Gráficos dos coeficientes
    plot_ols_model(m1, "Modelo 1 - Indústria + Recursos")
    plot_ols_model(m2, "Modelo 2 - + Inovação")
    plot_ols_model(m3, "Modelo 3 - + Inovação + Educação")

    print("\n=====================================================")
    print("\n=====================================================\n\n")


# === Random Forest com ranking e validação cruzada ===
def random_forest(df, X_cols):
    # 1. Treinar o modelo com 200 árvores
    rf = RandomForestRegressor(n_estimators=200, random_state=42)
    rf.fit(df[X_cols], df["log_gdp"])

    # 2. Score no treino (R² otimista)
    score = rf.score(df[X_cols], df["log_gdp"])
    print(f"\nRandom Forest R² (treino): {score:.3f}")

    # 3. Cross-Validation (5-fold)
    cv_scores = cross_val_score(rf, df[X_cols], df["log_gdp"], cv=5, scoring="r2")
    print(f"Random Forest R² (cross-val médio): {cv_scores.mean():.3f}")
    print(f"Desvio padrão (cross-val): {cv_scores.std():.3f}")

    # 4. Importância das variáveis
    importances = pd.Series(rf.feature_importances_, index=X_cols).sort_values(ascending=True)

    print("\n=== Importância (Random Forest) ===")
    print(importances.sort_values(ascending=False))

    # 5. Gráfico da importância das variáveis
    plt.figure(figsize=(10, 6))
    sns.barplot(x=importances.values, y=importances.index, color="steelblue")
    plt.title("Importância das Variáveis (Random Forest)")
    plt.xlabel("Importância relativa (soma = 1)")
    plt.ylabel("Variável explicativa")
    plt.tight_layout()
    plt.savefig("plots/random_forest_importance.png")
    plt.close()

    print("\n=====================================================")
    print("\n=====================================================\n\n")


# === Clustering com KMeans, radar plots normalizados e exportação ===
def clustering(df, X_cols, k=3):
    # 1. Média por país
    country_means = df.groupby("country")[X_cols].mean().reset_index()

    # 2. Escalar os dados (z-score)
    scaler = StandardScaler()
    country_scaled = country_means.copy()
    country_scaled[X_cols] = scaler.fit_transform(country_means[X_cols])

    # 3. Método do cotovelo
    distortions = []
    for i in range(2, 8):
        km = KMeans(n_clusters=i, random_state=42)
        km.fit(country_scaled[X_cols])
        distortions.append(km.inertia_)

    plt.figure()
    plt.plot(range(2, 8), distortions, marker="o")
    plt.title("Método do Cotovelo")
    plt.xlabel("Número de Clusters (k)")
    plt.ylabel("Distortion")
    plt.savefig("plots/elbow_method.png")
    plt.close()

    # 4. Clustering final com k clusters
    kmeans = KMeans(n_clusters=k, random_state=42)
    country_scaled["cluster_label"] = kmeans.fit_predict(country_scaled[X_cols])
    country_means["cluster_label"] = country_scaled["cluster_label"]

    # 5. Exportar cluster assignment
    country_means.to_csv("plots/country_clusters.csv", index=False)

    # 6. Resumo dos clusters com dados originais (para leitura)
    cluster_summary = country_means.groupby("cluster_label")[X_cols].mean().round(2)
    print("\n=== Cluster Summary ===")
    print(cluster_summary)
    print("\n=====================================================\n")

    # 7. Gerar radar plots com dados normalizados
    scaled_summary = country_scaled.groupby("cluster_label")[X_cols].mean()

    def radar_plot(df_scaled, features, cluster_id):
        angles = np.linspace(0, 2 * np.pi, len(features), endpoint=False).tolist()
        values = df_scaled.loc[cluster_id, features].tolist()
        values += values[:1]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.plot(angles, values, 'o-', linewidth=2)
        ax.fill(angles, values, alpha=0.25)
        ax.set_thetagrids(np.degrees(angles[:-1]), features)
        ax.set_title(f"Cluster {cluster_id}")
        ax.grid(True)
        plt.savefig(f"plots/radar_cluster_{cluster_id}.png")
        plt.close()

    for cid in scaled_summary.index:
        radar_plot(scaled_summary, X_cols, cid)


# === Execução principal ===
def main():
    X_cols = [
        "manufacturing_pct_gdp",
        "resource_rents_pct_gdp",
        "tertiary_enrolment_pct",
        "gii_score",
        "population_density",
        "age1564_pct"
    ]

    # DEFINIÇÃO DO MÍNIMO DE ANOS REQUERIDOS POR PAÍS
    min_anos = 5  # <= Podes alterar para 5 se quiseres média temporal mais robusta

    # Pipeline completo
    df = carregar_dados()
    df = verificar_cobertura(df, min_anos=min_anos)
    graficos_distribuicao(df)
    evolucao_top_bottom(df, X_cols, top_n=5)
    eda(df, X_cols)
    regressao_ols(df, X_cols)
    regressao_hierarquica(df)
    random_forest(df, X_cols)
    clustering(df, X_cols, k=3)

if __name__ == "__main__":
    main()
