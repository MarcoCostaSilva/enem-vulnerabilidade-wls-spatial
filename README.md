# 📊 enem-vulnerabilidade-wls-spatial

Estudo ecológico sobre vulnerabilidade socioeconômica e desempenho no ENEM 2025 por município — regressão ponderada (WLS) com erros-padrão robustos, análise de autocorrelação espacial (Índice de Moran) e comparação com modelos de Machine Learning (Ridge, Lasso, Random Forest).

*An ecological study on socioeconomic vulnerability and ENEM 2025 performance across Brazilian municipalities — weighted least squares (WLS) with robust standard errors, spatial autocorrelation testing (Moran's I), and benchmarking against Ridge, Lasso, and Random Forest models.*

---

🇧🇷 [Português](#-português) · 🇬🇧 [English](#-english)

---

## 🇧🇷 Português

### Sobre o projeto

Este projeto investiga a relação entre a situação socioeconômica dos candidatos do ENEM e o desempenho obtido na prova, no recorte por município. Ele parte de um problema real enfrentado por redes de escolas e empresas de tecnologia educacional: a dificuldade de direcionar recursos de investimento, reforço escolar ou expansão de forma estratégica, frequentemente tomada sem um critério objetivo baseado em dados.

**Pergunta de pesquisa:** municípios com maior vulnerabilidade socioeconômica entre os participantes apresentam, em média, desempenho mais baixo na prova? Quão forte é essa relação, e ela é estatisticamente significativa, ou pode ser explicada por acaso amostral?

**Resposta:** sim. Os dados analisados apresentam uma associação negativa forte e estatisticamente significativa entre vulnerabilidade socioeconômica e desempenho médio municipal, consistente em diferentes especificações do índice, modelos preditivos, recortes territoriais e testes de robustez — mas não interpretável como relação causal, dado o desenho observacional e agregado do estudo.

### Fonte dos dados

Microdados oficiais do ENEM 2025, disponibilizados publicamente pelo Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira (INEP).

> INSTITUTO NACIONAL DE ESTUDOS E PESQUISAS EDUCACIONAIS ANÍSIO TEIXEIRA. **Microdados do Enem 2025**. Brasília: Inep, 2026. Disponível em: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem.

**Desenho ecológico:** este é um estudo de desenho ecológico — as variáveis são medidas e analisadas no nível agregado do município, não no nível individual. As bases oficiais de participantes e de resultados do ENEM não possuem uma chave de ligação entre si, uma decisão deliberada do INEP em conformidade com a Lei Geral de Proteção de Dados (LGPD).

### Metodologia

O estudo é conduzido em duas camadas complementares, ambas no nível municipal:

**Camada 1 — Inferência estatística** (base completa, 1.805 municípios)
- Índice exploratório de vulnerabilidade socioeconômica (0 a 5 pontos), construído a partir de 5 componentes binários do questionário socioeconômico: ausência de renda familiar, ausência de computador, ausência de internet, Ensino Médio integralmente em escola pública, e pais com baixa escolaridade.
- Regressão linear ponderada (WLS), com peso estatístico dado pelo número efetivo de participantes com nota válida por município, e erros-padrão robustos à heterocedasticidade (HC3).
- Diagnóstico de multicolinearidade (VIF) e teste formal de heterocedasticidade (Breusch-Pagan).
- Verificação de robustez com erros-padrão clusterizados por região, como correção parcial à dependência espacial identificada.

**Camada 2 — Modelagem preditiva** (divisão treino/teste estratificada por UF)
- Comparação entre WLS (baseline), Ridge, Lasso e Random Forest.
- Análise de ablação: componentes individuais de vulnerabilidade vs. índice agregado como especificação de variáveis.
- Teste de estabilidade com múltiplas seeds e comparação formal seed a seed entre modelos.

**Testes de robustez adicionais**
- Correlação de Pearson vs. Spearman, com intervalo de confiança de 95% (transformação de Fisher).
- Diagnóstico de resíduos: gráfico resíduo × previsto, QQ-plot, teste formal de normalidade (Shapiro-Wilk).
- Leverage e distância de Cook, para identificação de pontos de alta influência.
- Robustez por tamanho de município, por região e por Unidade da Federação.
- Teste de autocorrelação espacial dos resíduos (Índice de Moran), com sensibilidade à definição de vizinhança (k = 5, 8 e 15 vizinhos mais próximos) e teste de significância por permutação (999 repetições).

### Principais resultados

| Métrica | Resultado |
|---|---|
| Coeficiente padronizado do índice de vulnerabilidade (WLS, HC3) | −21,47 (IC 95%: −25,10 a −17,85; p < 0,001) |
| R² do modelo inferencial (Camada 1) | 0,866 |
| Correlação de Pearson (% sem computador × nota média) | −0,877 (IC 95%: −0,888 a −0,866) |
| Correlação de Spearman | −0,888 |
| Índice de Moran dos resíduos (k = 5 a 15) | 0,459 a 0,535 (p = 0,001) |
| Erro-padrão clusterizado por região | dobra em relação ao HC3, mas coeficiente permanece significativo (p < 0,0001) |
| R² fora da amostra (WLS/Ridge/Lasso, especificação final) | ≈ 0,83–0,85 |
| Vantagem do Random Forest sobre WLS (seed a seed) | superou em 4 de 5 divisões, diferença pequena e não uniforme |

### Limitações

1. **Natureza observacional** — não permite estabelecer causalidade.
2. **Nível de agregação** — resultados são associações entre médias municipais, não inferências sobre indivíduos.
3. **Índice exploratório** — construído especificamente para este estudo, com pesos iguais entre componentes; não é um indicador oficial do INEP nem foi validado externamente.
4. **Estrutura espacial** — autocorrelação espacial significativa nos resíduos indica dependência territorial não plenamente capturada pelas variáveis do modelo.
5. **Municípios pequenos** — maior dispersão e viés nas previsões para municípios com menor número de participantes.
6. **Generalização temporal** — resultados referem-se especificamente à edição 2025 do exame.
7. **Variáveis não observadas** — o modelo não contempla aspectos institucionais, de infraestrutura escolar ou políticas educacionais.

### Stack técnica

`Python 3.12` · `pandas` · `numpy` · `scipy` · `statsmodels` · `scikit-learn` · `matplotlib` · `requests` / `gdown` (aquisição de dados)

### Estrutura sugerida do repositório

```
enem-vulnerabilidade-wls-spatial/
├── README.md
├── notebooks/
│   └── enem_vulnerabilidade_wls_spatial.ipynb
├── outputs/
│   └── tabela_municipio_final.csv   # tabela agregada, pronta para BigQuery/Looker
└── docs/
    └── melhorias_e_revisoes.md      # histórico de revisões metodológicas
```

> Os dados brutos não são versionados no repositório — são baixados diretamente do portal oficial do INEP pelo próprio notebook, com verificação de integridade por hash SHA-256 para o arquivo de resultados (mantido em cópia estável devido a uma divergência pontual identificada no pacote oficial).

### Como executar

1. Clone o repositório e abra o notebook em um ambiente com acesso à internet (o notebook foi desenvolvido para o ambiente Kaggle, com caminhos em `/kaggle/working/`).
2. Execute todas as células em ordem (Run All). O notebook baixa, audita, limpa e agrega os dados automaticamente.
3. A célula final exporta a tabela municipal consolidada (`tabela_municipio_final.csv`), pronta para upload no BigQuery e conexão com um dashboard no Looker Studio.

### Autores — Grupo 02

- Joao Lucas Ikezaki
- Jullyane Freitas de Lima Magalhães
- Marco Aurélio Costa da Silva
- Rogério Sá de Macedo
- Wendson Ferreira Santos Fernandes

---

## 🇬🇧 English

### About the project

This project investigates the relationship between the socioeconomic profile of ENEM candidates and their exam performance, at the municipal level. It addresses a real-world problem faced by school networks and education technology companies: the difficulty of strategically directing investment, tutoring, or expansion resources without an objective, data-driven criterion.

**Research question:** do municipalities with higher socioeconomic vulnerability among their participants show, on average, lower exam performance? How strong is this relationship, and is it statistically significant or explainable by sampling chance?

**Answer:** yes. The data show a strong, statistically significant negative association between socioeconomic vulnerability and average municipal performance, consistent across index specifications, predictive models, territorial cuts, and robustness checks — though it cannot be interpreted as causal, given the study's observational, aggregated design.

### Data source

Official ENEM 2025 microdata, publicly released by Brazil's National Institute for Educational Studies and Research (INEP).

> INSTITUTO NACIONAL DE ESTUDOS E PESQUISAS EDUCACIONAIS ANÍSIO TEIXEIRA. **Microdados do Enem 2025**. Brasília: Inep, 2026. Available at: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem.

**Ecological design:** this is an ecological study — variables are measured and analyzed at the aggregated municipal level, not the individual level. The official participant and results datasets have no linking key between them, a deliberate INEP decision in compliance with Brazil's General Data Protection Law (LGPD).

### Methodology

The study is conducted in two complementary layers, both at the municipal level:

**Layer 1 — Statistical inference** (full sample, 1,805 municipalities)
- Exploratory socioeconomic vulnerability index (0–5 points), built from 5 binary components of the socioeconomic questionnaire: lack of family income, lack of a computer, lack of internet access, public-school-only high school education, and low parental education.
- Weighted least squares (WLS) regression, weighted by the effective number of participants with a valid score per municipality, with heteroscedasticity-robust standard errors (HC3).
- Multicollinearity diagnostics (VIF) and a formal heteroscedasticity test (Breusch-Pagan).
- Robustness check using region-clustered standard errors, as a partial correction for the spatial dependence identified later in the study.

**Layer 2 — Predictive modeling** (train/test split, stratified by state)
- Comparison of WLS (baseline), Ridge, Lasso, and Random Forest.
- Ablation analysis: individual vulnerability components vs. the aggregated index as the feature specification.
- Multi-seed stability testing and formal seed-by-seed model comparison.

**Additional robustness checks**
- Pearson vs. Spearman correlation, with a 95% confidence interval (Fisher transformation).
- Residual diagnostics: residuals-vs-fitted plot, Q–Q plot, formal normality test (Shapiro-Wilk).
- Leverage and Cook's distance, to flag high-influence points.
- Robustness across municipality size, region, and state.
- Spatial autocorrelation test on residuals (Moran's I), with sensitivity to the neighborhood definition (k = 5, 8, and 15 nearest neighbors) and permutation-based significance testing (999 repetitions).

### Key results

| Metric | Result |
|---|---|
| Standardized vulnerability index coefficient (WLS, HC3) | −21.47 (95% CI: −25.10 to −17.85; p < 0.001) |
| Inferential model R² (Layer 1) | 0.866 |
| Pearson correlation (% without a computer × average score) | −0.877 (95% CI: −0.888 to −0.866) |
| Spearman correlation | −0.888 |
| Moran's I on residuals (k = 5 to 15) | 0.459 to 0.535 (p = 0.001) |
| Region-clustered standard error | roughly doubles vs. HC3, coefficient remains significant (p < 0.0001) |
| Out-of-sample R² (WLS/Ridge/Lasso, final specification) | ≈ 0.83–0.85 |
| Random Forest advantage over WLS (seed-by-seed) | outperformed in 4 of 5 splits, small and non-uniform difference |

### Limitations

1. **Observational nature** — does not support causal claims.
2. **Aggregation level** — results reflect associations between municipal averages, not individual-level inference.
3. **Exploratory index** — built specifically for this study with equal component weights; not an official INEP indicator and not externally validated.
4. **Spatial structure** — significant spatial autocorrelation in the residuals indicates territorial dependence not fully captured by the model's variables.
5. **Small municipalities** — greater prediction dispersion and bias for municipalities with fewer participants.
6. **Temporal generalization** — results are specific to the 2025 exam edition.
7. **Unobserved variables** — the model does not include institutional factors, school infrastructure, or education policy variables.

### Tech stack

`Python 3.12` · `pandas` · `numpy` · `scipy` · `statsmodels` · `scikit-learn` · `matplotlib` · `requests` / `gdown` (data acquisition)

### Suggested repository structure

```
enem-vulnerabilidade-wls-spatial/
├── README.md
├── notebooks/
│   └── enem_vulnerabilidade_wls_spatial.ipynb
├── outputs/
│   └── tabela_municipio_final.csv   # aggregated table, ready for BigQuery/Looker
└── docs/
    └── melhorias_e_revisoes.md      # methodological revision history
```

> Raw data is not versioned in the repository — it is downloaded directly from the official INEP portal by the notebook itself, with SHA-256 hash verification for the results file (kept as a stable mirrored copy due to a discrepancy found in the official package).

### How to run

1. Clone the repository and open the notebook in an internet-connected environment (developed for Kaggle, with paths under `/kaggle/working/`).
2. Run all cells in order (Run All). The notebook automatically downloads, audits, cleans, and aggregates the data.
3. The final cell exports the consolidated municipal table (`tabela_municipio_final.csv`), ready for upload to BigQuery and connection to a Looker Studio dashboard.

### Authors — Group 02

- Joao Lucas Ikezaki
- Jullyane Freitas de Lima Magalhães
- Marco Aurélio Costa da Silva
- Rogério Sá de Macedo
- Wendson Ferreira Santos Fernandes
