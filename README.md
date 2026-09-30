# 📊 White Cube | RadarEduca: Vulnerabilidade Socioeconômica e Desempenho no ENEM 2025

Projeto completo de análise de dados educacionais que combina um estudo estatístico e de Machine Learning sobre vulnerabilidade socioeconômica e desempenho no ENEM 2025, um banco de dados hospedado na nuvem, um dashboard interativo em Power BI e um agente consultor baseado em IA.

*A complete educational data project combining a statistical and Machine Learning study on socioeconomic vulnerability and ENEM 2025 performance, a cloud hosted database, an interactive Power BI dashboard and an AI based consultant agent.*

---

🇧🇷 [Português](#-português) · 🇬🇧 [English](#-english)

---

## 🇧🇷 Português

### Sobre o projeto

Este projeto simula uma consultoria de dados, a White Cube, contratada para orientar a alocação de recursos educacionais em todo o Brasil. Ele parte de um problema real enfrentado por redes de escolas, empresas de tecnologia educacional e órgãos públicos: a dificuldade de direcionar investimento, reforço escolar ou expansão de forma estratégica, muitas vezes tomada sem um critério objetivo baseado em dados.

A trilha escolhida pelo grupo foi Machine Learning, entregue integralmente no notebook de análise. Como valor adicional, o projeto também entrega o pipeline completo de dados até a camada de decisão: uma tabela municipal tratada e hospedada em banco de dados na nuvem, um dashboard executivo em Power BI e um agente de IA generativa que traduz os indicadores em recomendação prática para o gestor.

**Pergunta de negócio:** onde priorizar investimento e, dentro de cada território, que tipo de investimento faz mais sentido?

Essa pergunta é respondida em duas camadas:

1. **Onde investir:** qual a prioridade geográfica de um município, considerando a região em que está e sua posição de vulnerabilidade frente à própria região.
2. **O que investir:** qual componente específico de vulnerabilidade domina naquele município (conectividade, escolaridade dos pais, equipamento, tipo de escola ou renda familiar), e que tipo de ação essa informação sugere.

**Pergunta de pesquisa (base estatística do notebook):** municípios com maior vulnerabilidade socioeconômica entre os participantes apresentam, em média, desempenho mais baixo na prova? Quão forte é essa relação, e ela é estatisticamente significativa, ou pode ser explicada por acaso amostral?

**Resposta:** sim. Os dados analisados apresentam uma associação negativa forte e estatisticamente significativa entre vulnerabilidade socioeconômica e desempenho médio municipal, consistente em diferentes especificações do índice, modelos preditivos, recortes territoriais e testes de robustez, mas não interpretável como relação causal, dado o desenho observacional e agregado do estudo.

### Fonte dos dados

Microdados oficiais do ENEM 2025, disponibilizados publicamente pelo Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira (INEP).

> INSTITUTO NACIONAL DE ESTUDOS E PESQUISAS EDUCACIONAIS ANÍSIO TEIXEIRA. **Microdados do Enem 2025**. Brasília: Inep, 2026. Disponível em: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem.

**Desenho ecológico:** este é um estudo de desenho ecológico, as variáveis são medidas e analisadas no nível agregado do município, não no nível individual. As bases oficiais de participantes e de resultados do ENEM não possuem uma chave de ligação entre si, uma decisão deliberada do INEP em conformidade com a Lei Geral de Proteção de Dados (LGPD).

### Arquitetura da solução

```
MICRODADOS ENEM 2025
        │
        ▼
NOTEBOOK PYTHON (tratamento, estatística e Machine Learning)
        │
        ▼
TABELA MUNICIPAL FINAL (1.805 municípios, 25 variáveis)
        │
        ▼
AZURE SQL DATABASE (fonte única na nuvem)
        │
        ├──────────────┐
        ▼              ▼
   POWER BI        AGENTE DE IA
 (5 dashboards)   (consultor de bolso)
```

A mesma inteligência analítica alimenta duas formas diferentes de acesso: uma visual e exploratória, para quem quer navegar pelos dados livremente, e uma conversacional, para quem quer uma recomendação pronta em linguagem natural.

### Metodologia do notebook (trilha de Machine Learning)

O estudo estatístico é conduzido em duas camadas complementares, ambas no nível municipal.

**Camada 1, Inferência estatística** (base completa, 1.805 municípios)

* Índice exploratório de vulnerabilidade socioeconômica (0 a 5 pontos), construído a partir de 5 componentes binários do questionário socioeconômico: ausência de renda familiar, ausência de computador, ausência de internet, Ensino Médio integralmente em escola pública, e pais com baixa escolaridade.
* Regressão linear ponderada (WLS), com peso estatístico dado pelo número efetivo de participantes com nota válida por município, e erros padrão robustos à heterocedasticidade (HC3).
* Diagnóstico de multicolinearidade (VIF) e teste formal de heterocedasticidade (Breusch Pagan).
* Verificação de robustez com erros padrão clusterizados por região, como correção parcial à dependência espacial identificada.

**Camada 2, Modelagem preditiva** (divisão treino e teste estratificada por UF)

* Comparação entre WLS (baseline), Ridge, Lasso e Random Forest.
* Análise de ablação: componentes individuais de vulnerabilidade contra índice agregado como especificação de variáveis. Os componentes individuais mostraram maior capacidade preditiva do que o índice agregado, o que embasa a recomendação por tipo de investimento descrita adiante.
* Teste de estabilidade com múltiplas seeds e comparação formal seed a seed entre modelos.

**Testes de robustez adicionais**

* Correlação de Pearson e de Spearman, com intervalo de confiança de 95% (transformação de Fisher).
* Diagnóstico de resíduos: gráfico resíduo por previsto, QQ plot, teste formal de normalidade (Shapiro Wilk).
* Leverage e distância de Cook, para identificação de pontos de alta influência.
* Robustez por tamanho de município, por região e por Unidade da Federação.
* Teste de autocorrelação espacial dos resíduos (Índice de Moran), com sensibilidade à definição de vizinhança (k igual a 5, 8 e 15 vizinhos mais próximos) e teste de significância por permutação (999 repetições).

### Principais resultados

| Métrica | Resultado |
|---|---|
| Coeficiente padronizado do índice de vulnerabilidade (WLS, HC3) | 21,47 negativo (IC 95%: 25,10 a 17,85 negativos; p menor que 0,001) |
| R² do modelo inferencial (Camada 1) | 0,866 |
| Correlação de Pearson (percentual sem computador contra nota média) | 0,877 negativo (IC 95%: 0,888 a 0,866 negativos) |
| Correlação de Spearman | 0,888 negativo |
| Índice de Moran dos resíduos (k de 5 a 15) | 0,459 a 0,535 (p = 0,001) |
| Erro padrão clusterizado por região | dobra em relação ao HC3, mas o coeficiente permanece significativo (p menor que 0,0001) |
| R² fora da amostra (WLS, Ridge e Lasso, especificação final) | aproximadamente 0,83 a 0,85 |
| Vantagem do Random Forest sobre o WLS (seed a seed) | superou em 4 de 5 divisões, diferença pequena e não uniforme |

### Da evidência à recomendação de negócio

O estudo estatístico sustenta duas regras de decisão, aplicadas tanto no dashboard quanto no agente de IA.

**Onde priorizar (camada geográfica)**

As regiões Norte e Nordeste concentram, de forma desproporcional, os municípios com maior vulnerabilidade e menor desempenho médio. Essa é a primeira camada de priorização. Dentro de qualquer região, a autocorrelação espacial identificada pelo Índice de Moran mostra que a vulnerabilidade não se distribui ao acaso no território, ela forma agrupamentos regionais. Por isso, um município com índice de vulnerabilidade acima da média da própria região tem maior probabilidade de estar dentro de um desses agrupamentos, e investir nele tende a ter efeito de contágio positivo sobre municípios vizinhos, ao contrário de investir num município isolado com o mesmo índice.

**O que priorizar (camada de componente)**

A análise de ablação mostrou que olhar os cinco componentes de vulnerabilidade separadamente é mais informativo do que olhar apenas o índice agregado. Por isso, a recomendação de investimento é baseada no componente dominante de cada município:

| Componente dominante | Investimento sugerido |
|---|---|
| Ausência de internet em casa | Conectividade e material didático offline |
| Ensino médio integralmente em escola pública | Parceria com a rede pública local e reforço de material didático |
| Baixa escolaridade dos pais | Tutoria e acompanhamento pedagógico do aluno |
| Ausência de computador em casa | Doação ou comodato de equipamento |
| Ausência de renda familiar declarada | Bolsas de apoio financeiro |

Os componentes de ausência de computador e ausência de renda familiar apresentaram multicolinearidade moderada a alta no diagnóstico de VIF, por isso a recomendação para esses dois componentes sempre inclui um alerta de cautela sobre sobreposição com outros sinais.

Essas recomendações são orientadas por associação estatística e não representam efeito causal estimado.

### Limitações

1. **Natureza observacional**, não permite estabelecer causalidade.
2. **Nível de agregação**, os resultados são associações entre médias municipais, não inferências sobre indivíduos.
3. **Índice exploratório**, construído especificamente para este estudo, com pesos iguais entre componentes, não é um indicador oficial do INEP nem foi validado externamente.
4. **Estrutura espacial**, a autocorrelação espacial significativa nos resíduos indica dependência territorial não plenamente capturada pelas variáveis do modelo.
5. **Municípios pequenos**, maior dispersão e viés nas previsões para municípios com menor número de participantes.
6. **Generalização temporal**, os resultados referem se especificamente à edição 2025 do exame.
7. **Variáveis não observadas**, o modelo não contempla aspectos institucionais, de infraestrutura escolar ou políticas educacionais.

### Entrega de Valor 01: banco de dados na nuvem

A tabela municipal final, com 1.805 municípios e 25 variáveis, é hospedada em um Azure SQL Database, servindo como fonte única de dados para o dashboard e para o agente. Isso garante que qualquer atualização futura da base seja refletida automaticamente nos dois pontos de acesso, sem duplicidade de dados.

### Entrega de Valor 02: dashboard em Power BI

Dashboard executivo com 5 páginas:

1. **Visão Executiva**, indicadores gerais e o gráfico de dispersão entre vulnerabilidade e desempenho, com destaque por região.
2. **Mapa do Brasil**, mapa coroplético da vulnerabilidade por estado, com filtro por região.
3. **Componentes da Vulnerabilidade**, comparação entre os cinco componentes que formam o índice.
4. **Ranking de Municípios**, os dez municípios mais e menos vulneráveis do país, com filtro por UF.
5. **Metodologia**, principais métricas estatísticas do estudo e as limitações da análise, resumidas para um público não técnico.

### Entrega de Valor 03: agente consultor de IA

Um agente conversacional que lê o perfil de qualquer um dos 1.805 municípios diretamente da tabela final e gera, em linguagem natural, um diagnóstico completo. O agente aplica as mesmas duas regras de negócio do estudo, região mais posição relativa de vulnerabilidade para responder onde investir, e componente dominante para responder o que investir, sempre reforçando que a recomendação é uma regra de negócio baseada em associação estatística, não uma prova de causalidade.

O agente também aplica um guardrail de escopo, respondendo apenas a perguntas relacionadas ao contexto educacional e socioeconômico do projeto, e utiliza a camada gratuita da API da NVIDIA NIM (compatível com o padrão da OpenAI) para geração de texto.

### Stack técnica

`Python 3.12` · `pandas` · `numpy` · `scipy` · `statsmodels` · `scikit learn` · `matplotlib` · `requests` e `gdown` (aquisição de dados) · `Azure SQL Database` · `Power BI Desktop` · `OpenAI SDK` com endpoint `NVIDIA NIM`

### Estrutura sugerida do repositório

```
white-cube-radareduca-enem/
├── README.md
├── notebooks/
│   └── enem_vulnerabilidade_wls_spatial.ipynb
├── outputs/
│   └── tabela_municipio_final.csv
├── bi/
│   └── white_cube_projeto.pbix
├── agente/
│   ├── agente.py
│   └── env.example
└── docs/
    └── melhorias_e_revisoes.md
```

> Os dados brutos não são versionados no repositório, são baixados diretamente do portal oficial do INEP pelo próprio notebook, com verificação de integridade por hash SHA-256 para o arquivo de resultados (mantido em cópia estável devido a uma divergência pontual identificada no pacote oficial).

### Como executar

1. Clone o repositório e abra o notebook em um ambiente com acesso à internet (o notebook foi desenvolvido para o ambiente Kaggle, com caminhos em `/kaggle/working/`).
2. Execute todas as células em ordem (Run All). O notebook baixa, audita, limpa e agrega os dados automaticamente.
3. A célula final exporta a tabela municipal consolidada (`tabela_municipio_final.csv`), pronta para upload no Azure SQL Database.
4. Conecte o Power BI Desktop ao Azure SQL Database usando o modo de importação para abrir o dashboard.
5. Para rodar o agente, crie um arquivo `.env` com sua chave gratuita `NVIDIA_API_KEY` (obtida em build.nvidia.com), instale as dependências de `requirements.txt`, e execute `python agente.py "Nome do Município"`.

### Autores, Grupo 02

* Joao Lucas Ikezaki
* Jullyane Freitas de Lima Magalhães
* Marco Aurélio Costa da Silva
* Rogério Sá de Macedo
* Wendson Ferreira Santos Fernandes

Orientadores: Edmar Junyor Bevilaqua e Felipe André Bech Alves.

---

## 🇬🇧 English

### About the project

This project simulates a data consultancy, White Cube, hired to guide educational resource allocation across Brazil. It addresses a real world problem faced by school networks, education technology companies and public agencies: the difficulty of strategically directing investment, tutoring or expansion resources without an objective, data driven criterion.

The track chosen by the group was Machine Learning, delivered in full in the analysis notebook. As additional value, the project also delivers the complete data pipeline up to the decision layer: a cleaned municipal table hosted in a cloud database, an executive dashboard in Power BI, and a generative AI agent that translates the indicators into a practical recommendation for the manager.

**Business question:** where should investment be prioritized, and within each territory, what type of investment makes the most sense?

This question is answered in two layers:

1. **Where to invest:** the geographic priority of a municipality, considering the region it belongs to and its vulnerability position relative to that region.
2. **What to invest in:** the specific vulnerability component that dominates in that municipality (connectivity, parental education, equipment, school type or family income), and what type of action that information suggests.

**Research question (the notebook's statistical foundation):** do municipalities with higher socioeconomic vulnerability among their participants show, on average, lower exam performance? How strong is this relationship, and is it statistically significant or explainable by sampling chance?

**Answer:** yes. The data show a strong, statistically significant negative association between socioeconomic vulnerability and average municipal performance, consistent across index specifications, predictive models, territorial cuts and robustness checks, though it cannot be interpreted as causal, given the study's observational, aggregated design.

### Data source

Official ENEM 2025 microdata, publicly released by Brazil's National Institute for Educational Studies and Research (INEP).

> INSTITUTO NACIONAL DE ESTUDOS E PESQUISAS EDUCACIONAIS ANÍSIO TEIXEIRA. **Microdados do Enem 2025**. Brasília: Inep, 2026. Available at: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem.

**Ecological design:** this is an ecological study, variables are measured and analyzed at the aggregated municipal level, not the individual level. The official participant and results datasets have no linking key between them, a deliberate INEP decision in compliance with Brazil's General Data Protection Law (LGPD).

### Solution architecture

```
ENEM 2025 MICRODATA
        │
        ▼
PYTHON NOTEBOOK (cleaning, statistics and Machine Learning)
        │
        ▼
FINAL MUNICIPAL TABLE (1,805 municipalities, 25 variables)
        │
        ▼
AZURE SQL DATABASE (single cloud source)
        │
        ├──────────────┐
        ▼              ▼
   POWER BI         AI AGENT
 (5 dashboards)  (pocket consultant)
```

The same analytical intelligence feeds two different access channels: a visual and exploratory one, for those who want to freely browse the data, and a conversational one, for those who want a ready made recommendation in natural language.

### Notebook methodology (Machine Learning track)

The statistical study is conducted in two complementary layers, both at the municipal level.

**Layer 1, Statistical inference** (full sample, 1,805 municipalities)

* Exploratory socioeconomic vulnerability index (0 to 5 points), built from 5 binary components of the socioeconomic questionnaire: lack of family income, lack of a computer, lack of internet access, public school only high school education, and low parental education.
* Weighted least squares (WLS) regression, weighted by the effective number of participants with a valid score per municipality, with heteroscedasticity robust standard errors (HC3).
* Multicollinearity diagnostics (VIF) and a formal heteroscedasticity test (Breusch Pagan).
* Robustness check using region clustered standard errors, as a partial correction for the spatial dependence identified later in the study.

**Layer 2, Predictive modeling** (train and test split, stratified by state)

* Comparison of WLS (baseline), Ridge, Lasso and Random Forest.
* Ablation analysis: individual vulnerability components against the aggregated index as the feature specification. Individual components showed greater predictive power than the aggregated index, which supports the investment type recommendation described further below.
* Multi seed stability testing and formal seed by seed model comparison.

**Additional robustness checks**

* Pearson and Spearman correlation, with a 95 percent confidence interval (Fisher transformation).
* Residual diagnostics: residuals versus fitted plot, QQ plot, formal normality test (Shapiro Wilk).
* Leverage and Cook's distance, to flag high influence points.
* Robustness across municipality size, region and state.
* Spatial autocorrelation test on residuals (Moran's I), with sensitivity to the neighborhood definition (k equal to 5, 8 and 15 nearest neighbors) and permutation based significance testing (999 repetitions).

### Key results

| Metric | Result |
|---|---|
| Standardized vulnerability index coefficient (WLS, HC3) | negative 21.47 (95% CI: negative 25.10 to negative 17.85; p less than 0.001) |
| Inferential model R² (Layer 1) | 0.866 |
| Pearson correlation (percentage without a computer against average score) | negative 0.877 (95% CI: negative 0.888 to negative 0.866) |
| Spearman correlation | negative 0.888 |
| Moran's I on residuals (k from 5 to 15) | 0.459 to 0.535 (p = 0.001) |
| Region clustered standard error | roughly doubles compared to HC3, coefficient remains significant (p less than 0.0001) |
| Out of sample R² (WLS, Ridge and Lasso, final specification) | approximately 0.83 to 0.85 |
| Random Forest advantage over WLS (seed by seed) | outperformed in 4 of 5 splits, small and non uniform difference |

### From evidence to business recommendation

The statistical study supports two decision rules, applied both in the dashboard and in the AI agent.

**Where to prioritize (geographic layer)**

The North and Northeast regions disproportionately concentrate municipalities with higher vulnerability and lower average performance. This is the first layer of prioritization. Within any region, the spatial autocorrelation identified by Moran's I shows that vulnerability is not randomly distributed across the territory, it forms regional clusters. Because of this, a municipality with a vulnerability index above its own region's average is more likely to sit inside one of these clusters, and investing in it tends to have a positive spillover effect on neighboring municipalities, unlike investing in an isolated municipality with the same index.

**What to prioritize (component layer)**

The ablation analysis showed that looking at the five vulnerability components separately is more informative than looking only at the aggregated index. Because of this, the investment recommendation is based on each municipality's dominant component:

| Dominant component | Suggested investment |
|---|---|
| Lack of internet at home | Connectivity and offline learning material |
| Public school only high school | Partnership with the local public school network and learning material support |
| Low parental education | Tutoring and student support |
| Lack of a computer at home | Equipment donation or loan |
| Lack of declared family income | Financial support grants |

The lack of a computer and lack of family income components showed moderate to high multicollinearity in the VIF diagnostic, so the recommendation for these two components always includes a caution note about overlap with other signals.

These recommendations are guided by statistical association and do not represent an estimated causal effect.

### Limitations

1. **Observational nature**, does not support causal claims.
2. **Aggregation level**, results reflect associations between municipal averages, not individual level inference.
3. **Exploratory index**, built specifically for this study with equal component weights, not an official INEP indicator and not externally validated.
4. **Spatial structure**, significant spatial autocorrelation in the residuals indicates territorial dependence not fully captured by the model's variables.
5. **Small municipalities**, greater prediction dispersion and bias for municipalities with fewer participants.
6. **Temporal generalization**, results are specific to the 2025 exam edition.
7. **Unobserved variables**, the model does not include institutional factors, school infrastructure or education policy variables.

### Value Delivery 01: cloud database

The final municipal table, with 1,805 municipalities and 25 variables, is hosted in an Azure SQL Database, serving as the single data source for both the dashboard and the agent. This ensures that any future update to the base is automatically reflected in both access points, without data duplication.

### Value Delivery 02: Power BI dashboard

Executive dashboard with 5 pages:

1. **Executive Overview**, general indicators and the scatter plot between vulnerability and performance, highlighted by region.
2. **Map of Brazil**, choropleth map of vulnerability by state, with a region filter.
3. **Vulnerability Components**, comparison across the five components that make up the index.
4. **Municipality Ranking**, the ten most and least vulnerable municipalities in the country, with a state filter.
5. **Methodology**, the study's main statistical metrics and its limitations, summarized for a non technical audience.

### Value Delivery 03: AI consultant agent

A conversational agent that reads the profile of any of the 1,805 municipalities directly from the final table and generates a complete diagnosis in natural language. The agent applies the same two business rules from the study, region plus relative vulnerability position to answer where to invest, and dominant component to answer what to invest in, always reinforcing that the recommendation is a business rule based on statistical association, not proof of causality.

The agent also applies a scope guardrail, answering only questions related to the project's educational and socioeconomic context, and uses the free tier of the NVIDIA NIM API (compatible with the OpenAI standard) for text generation.

### Tech stack

`Python 3.12` · `pandas` · `numpy` · `scipy` · `statsmodels` · `scikit learn` · `matplotlib` · `requests` and `gdown` (data acquisition) · `Azure SQL Database` · `Power BI Desktop` · `OpenAI SDK` with the `NVIDIA NIM` endpoint

### Suggested repository structure

```
white-cube-radareduca-enem/
├── README.md
├── notebooks/
│   └── enem_vulnerabilidade_wls_spatial.ipynb
├── outputs/
│   └── tabela_municipio_final.csv
├── bi/
│   └── white_cube_projeto.pbix
├── agente/
│   ├── agente.py
│   └── env.example
└── docs/
    └── melhorias_e_revisoes.md
```

> Raw data is not versioned in the repository, it is downloaded directly from the official INEP portal by the notebook itself, with SHA-256 hash verification for the results file (kept as a stable mirrored copy due to a discrepancy found in the official package).

### How to run

1. Clone the repository and open the notebook in an internet connected environment (developed for Kaggle, with paths under `/kaggle/working/`).
2. Run all cells in order (Run All). The notebook automatically downloads, audits, cleans and aggregates the data.
3. The final cell exports the consolidated municipal table (`tabela_municipio_final.csv`), ready for upload to Azure SQL Database.
4. Connect Power BI Desktop to the Azure SQL Database using import mode to open the dashboard.
5. To run the agent, create a `.env` file with your free `NVIDIA_API_KEY` (obtained at build.nvidia.com), install the dependencies from `requirements.txt`, and run `python agente.py "Municipality Name"`.

### Authors, Group 02

* Joao Lucas Ikezaki
* Jullyane Freitas de Lima Magalhães
* Marco Aurélio Costa da Silva
* Rogério Sá de Macedo
* Wendson Ferreira Santos Fernandes

Advisors: Edmar Junyor Bevilaqua and Felipe André Bech Alves.
