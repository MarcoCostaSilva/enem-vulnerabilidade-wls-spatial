# =============================================================
# agente.py — Agente Consultor Estratégico White Cube
#
# Projeto: Vulnerabilidade Socioeconômica e Desempenho no ENEM 2025
# Lógica de negócio: alocação de recursos em duas camadas
#   1) ONDE priorizar   -> região (Norte/Nordeste) + intensidade
#      relativa da vulnerabilidade do município frente à sua região
#      (proxy simples para a lógica de cluster territorial
#      identificada pelo Índice de Moran no notebook original).
#   2) O QUE priorizar  -> componente de vulnerabilidade dominante
#      no município, mapeado para um tipo de investimento
#      (conectividade, tutoria, equipamento, parceria com rede
#      pública ou apoio financeiro), com base na análise de
#      ablação do notebook, que mostrou que os componentes
#      individuais carregam mais informação preditiva do que o
#      índice agregado.
#
# Lê os dados diretamente de tabela_municipio_final.csv (a mesma
# tabela final hospedada no Azure SQL e usada no Power BI) e
# consulta a API gratuita da NVIDIA NIM (compatível com o SDK
# da OpenAI) para redigir a recomendação em linguagem natural.
# =============================================================

import os
import warnings
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

warnings.filterwarnings("ignore", category=UserWarning)

# ------------------------------------------------------------------
# Constantes de negócio
# ------------------------------------------------------------------

REGIOES_PRIORITARIAS = {"Norte", "Nordeste"}

# Componentes de vulnerabilidade -> tipo de investimento recomendado.
# A ordem de checagem prioriza os componentes com menor sobreposição
# (VIF mais baixo no notebook: pct_sem_internet, pct_escola_publica,
# pct_pais_baixa_escolaridade) antes dos dois componentes que
# apresentaram VIF mais alto e maior colinearidade entre si
# (pct_sem_computador VIF=7,07 e pct_sem_renda_familiar VIF=5,04),
# para os quais o agente inclui um alerta de cautela na resposta.

MAPA_COMPONENTE_INVESTIMENTO = {
    "pct_sem_internet": {
        "rotulo": "Ausência de internet em casa",
        "investimento": "Conectividade e material didático offline",
        "alerta_colinearidade": False,
    },
    "pct_escola_publica": {
        "rotulo": "Ensino médio integralmente em escola pública",
        "investimento": "Parceria com a rede pública local e reforço de material didático",
        "alerta_colinearidade": False,
    },
    "pct_pais_baixa_escolaridade": {
        "rotulo": "Baixa escolaridade dos pais",
        "investimento": "Tutoria e acompanhamento pedagógico do aluno",
        "alerta_colinearidade": False,
    },
    "pct_sem_computador": {
        "rotulo": "Ausência de computador em casa",
        "investimento": "Doação ou comodato de equipamento (notebook/tablet)",
        "alerta_colinearidade": True,
    },
    "pct_sem_renda_familiar": {
        "rotulo": "Ausência de renda familiar declarada",
        "investimento": "Bolsas de apoio financeiro e auxílio-permanência",
        "alerta_colinearidade": True,
    },
}

_GUARDRAIL_MIN_CHARS = 10

_PALAVRAS_ESCOPO = {
    # Vocabulário original do projeto
    "escola", "ensino", "educação", "educacional", "aluno", "município",
    "municipio", "vulnerabilidade", "score", "índice", "indice", "perfil",
    "renda", "internet", "investimento", "gestor", "instituição", "instituicao",
    "enem", "socioeconômico", "socioeconomico", "aprendizagem", "estratégia",
    "estrategia", "recomend", "indicador", "dados", "análise", "analise",
    "regional", "região", "regiao", "brasil", "público", "publico", "privado",
    "infraestrutura", "metodolog", "suporte", "conteúdo", "conteudo",
    "capital cultural", "capital humano", "cultural", "familiar", "escolaridade",
    "pai", "mãe", "mae", "estrutura", "resultado", "desempenho", "formação",
    "formacao",
    # Vocabulário específico da lógica White Cube (região/cluster/componente)
    "moran", "cluster", "clusters", "spillover", "vizinhança", "vizinhanca",
    "vizinho", "alocação", "alocacao", "priorizar", "priorização", "priorizacao",
    "conectividade", "tutoria", "tutor", "professor", "equipamento", "computador",
    "notebook", "tablet", "bolsa", "bolsas", "auxílio", "auxilio", "wls", "ridge",
    "lasso", "random forest", "ablação", "ablacao", "r2", "r²", "correlação",
    "correlacao", "pearson", "spearman", "componente", "componentes",
    # Nomes de região e alguns estados/capitais mais citados
    "norte", "nordeste", "sudeste", "sul", "centro-oeste", "centro oeste",
    "recife", "salvador", "fortaleza", "são paulo", "sao paulo", "rio",
    "minas", "bahia", "ceará", "ceara", "pernambuco", "amazonas", "pará", "para",
}

_MSG_FORA_DE_ESCOPO = (
    "⚠️  Essa pergunta está fora do escopo desta consultoria.\n\n"
    "Estou aqui para ajudar com:\n"
    "  • Onde priorizar investimento (região e intensidade da vulnerabilidade)\n"
    "  • Que tipo de investimento priorizar em cada município (conectividade, "
    "tutoria, equipamento, parceria com rede pública ou apoio financeiro)\n"
    "  • Interpretação dos indicadores socioeconômicos e de desempenho no ENEM\n\n"
    "Como posso te ajudar nesse contexto?"
)


def _esta_no_escopo(pergunta: str) -> bool:
    if len(pergunta.strip()) < _GUARDRAIL_MIN_CHARS:
        return True
    pergunta_lower = pergunta.lower()
    return any(palavra in pergunta_lower for palavra in _PALAVRAS_ESCOPO)


# ------------------------------------------------------------------
# Leitura da tabela municipal final (mesma fonte do Power BI)
# ------------------------------------------------------------------

_COLUNAS_COMPONENTES = list(MAPA_COMPONENTE_INVESTIMENTO.keys())


def _para_percentual(valor: float) -> float:
    """Normaliza um percentual que pode vir como fração (0-1) ou já
    como percentual (0-100), devolvendo sempre em escala 0-100."""
    valor = float(valor or 0)
    return valor if valor > 1.0 else valor * 100.0


def _componente_dominante(linha: pd.Series) -> dict:
    """Identifica, entre os 5 componentes de vulnerabilidade, aquele
    com maior percentual no município, e retorna o investimento
    recomendado correspondente."""
    valores = {
        col: _para_percentual(linha.get(col, 0)) for col in _COLUNAS_COMPONENTES
    }
    componente_top = max(valores, key=valores.get)
    info = MAPA_COMPONENTE_INVESTIMENTO[componente_top]

    return {
        "componente": componente_top,
        "rotulo": info["rotulo"],
        "valor_pct": round(valores[componente_top], 2),
        "investimento_sugerido": info["investimento"],
        "alerta_colinearidade": info["alerta_colinearidade"],
        "todos_componentes_pct": {k: round(v, 2) for k, v in valores.items()},
    }


def buscar_perfil_no_csv(
    nome_municipio: str,
    caminho_csv: str = "dados/tratado/tabela_municipio_final.csv",
) -> dict:
    """Lê o perfil de um município na tabela final e monta o pacote de
    contexto que o agente usa para justificar a recomendação: região,
    posição relativa de vulnerabilidade dentro da própria região
    (proxy de cluster) e componente de vulnerabilidade dominante."""

    if not os.path.exists(caminho_csv):
        raise FileNotFoundError(f"Erro: o arquivo '{caminho_csv}' precisa estar nesta pasta.")

    # A tabela final do projeto (exportada em pt-BR) usa ';' como separador
    # e ',' como separador decimal. Se o arquivo já vier no padrão
    # internacional (',' e '.'), o parser abaixo também funciona, pois
    # cai automaticamente no fallback.
    try:
        df = pd.read_csv(caminho_csv, sep=";", decimal=",", encoding="utf-8-sig")
        if "nome_municipio" not in df.columns:
            raise ValueError("Formato pt-BR não reconhecido, tentando padrão internacional.")
    except Exception:
        df = pd.read_csv(caminho_csv)

    resultado = df[df["nome_municipio"].str.strip().str.lower() == nome_municipio.strip().lower()]
    if resultado.empty:
        raise ValueError(f"Município '{nome_municipio}' não foi encontrado na base de dados do ENEM.")

    linha = resultado.iloc[0]
    regiao = str(linha.get("regiao", "N/D"))

    # Índice de vulnerabilidade: escala real é 0 a 5 (ver README/notebook).
    # Aqui reportamos o valor bruto, sem forçar conversão para 0-100.
    indice_bruto = float(linha.get("indice_vulnerabilidade_medio", 0))

    # Média do índice na própria região, para dar noção de posição
    # relativa do município dentro da região (proxy simples de
    # "está num cluster de alta vulnerabilidade?" sem recalcular o
    # Índice de Moran em tempo real, que já foi validado no notebook).
    media_regiao = float(
        df.loc[df["regiao"] == regiao, "indice_vulnerabilidade_medio"].mean()
    )
    acima_da_media_regional = indice_bruto > media_regiao

    componente_info = _componente_dominante(linha)

    return {
        "municipio": str(linha["nome_municipio"]),
        "uf": str(linha.get("uf", "UF")),
        "regiao": regiao,
        "regiao_prioritaria": regiao in REGIOES_PRIORITARIAS,
        "indice_vulnerabilidade": round(indice_bruto, 2),
        "media_indice_regiao": round(media_regiao, 2),
        "acima_da_media_regional": acima_da_media_regional,
        "componente_dominante": componente_info["rotulo"],
        "componente_dominante_pct": componente_info["valor_pct"],
        "investimento_sugerido": componente_info["investimento_sugerido"],
        "alerta_colinearidade": componente_info["alerta_colinearidade"],
        "componentes_detalhados_pct": componente_info["todos_componentes_pct"],
        "n_alunos": int(linha.get("qtd_inscritos", linha.get("n_efetivo_nota", 0)) or 0),
        "nota_enem_geral": round(float(linha.get("nota_media_geral", 0)), 1),
        "nota_redacao": round(float(linha.get("nota_media_redacao", 0)), 1),
    }


# ------------------------------------------------------------------
# Prompt do sistema
# ------------------------------------------------------------------

_SYSTEM_PROMPT = """Você é o Agente Consultor Estratégico da White Cube, uma consultoria de dados
contratada para orientar a alocação de recursos educacionais com base em um
estudo ecológico municipal sobre vulnerabilidade socioeconômica e desempenho
no ENEM 2025 (1.805 municípios, regressão WLS com erros-padrão robustos,
teste de autocorrelação espacial via Índice de Moran, e comparação com
modelos de Machine Learning).

Seu papel é traduzir os indicadores de um município em uma recomendação de
alocação de recursos em DUAS perguntas, nesta ordem:

  1) ONDE priorizar investimento
  2) O QUE priorizar dentro desse investimento

REGRA DE NEGÓCIO — ONDE PRIORIZAR:

- Regiões Norte e Nordeste concentram, de forma desproporcional, os
  municípios com maior vulnerabilidade e menor desempenho médio. Elas são
  a primeira camada de priorização geográfica.
- Dentro de qualquer região, o estudo identificou autocorrelação espacial
  estatisticamente significativa nos resíduos do modelo (Índice de Moran
  entre 0,459 e 0,535, robusto a diferentes definições de vizinhança,
  p = 0,001 no teste de permutação). Isso significa que a vulnerabilidade
  não se distribui ao acaso no território: ela forma agrupamentos
  regionais. Por isso, um município cujo índice de vulnerabilidade está
  ACIMA da média da sua própria região tem maior probabilidade de estar
  dentro de um desses agrupamentos, e investir nele tende a ter efeito de
  contágio positivo (spillover) sobre municípios vizinhos, ao contrário de
  investir num município isolado com o mesmo índice.
- Você recebe no contexto se o município está numa região prioritária
  (Norte/Nordeste) e se seu índice está acima da média da própria região.
  Use os dois sinais juntos para justificar o grau de prioridade
  geográfica, mas nunca afirme causalidade territorial: fale em termos de
  "maior probabilidade", "indício" ou "padrão observado".

REGRA DE NEGÓCIO — O QUE PRIORIZAR:

- Uma análise de ablação no notebook mostrou que os cinco componentes
  individuais de vulnerabilidade (ausência de computador, ausência de
  internet, ensino médio só em escola pública, ausência de renda familiar,
  baixa escolaridade dos pais) têm, juntos, maior capacidade preditiva do
  desempenho municipal do que o índice agregado que os resume em um único
  número. Ou seja: olhar cada componente separadamente é mais informativo
  para decidir o tipo de investimento do que olhar só o índice agregado.
- Por isso, a recomendação de investimento deve ser baseada no componente
  de vulnerabilidade com maior percentual no município (o "componente
  dominante"), e não apenas no índice agregado.
- Mapeamento padrão componente → tipo de investimento:
    - Ausência de internet em casa → conectividade e material didático offline
    - Ensino médio só em escola pública → parceria com a rede pública local
      e reforço de material didático
    - Baixa escolaridade dos pais → tutoria e acompanhamento pedagógico do aluno
    - Ausência de computador em casa → doação ou comodato de equipamento
    - Ausência de renda familiar → bolsas de apoio financeiro
- Atenção: os componentes "ausência de computador" e "ausência de renda
  familiar" apresentaram multicolinearidade moderada a alta no diagnóstico
  de VIF do estudo (7,07 e 5,04, respectivamente), ou seja, tendem a
  variar juntos com outros componentes. Quando o componente dominante for
  um destes dois, mencione essa ressalva ao gestor: o sinal pode estar
  parcialmente sobreposto a outro componente, e não deve ser lido como
  causa isolada.

REGRAS GERAIS DE HONESTIDADE ESTATÍSTICA (não negociáveis):

- Este é um estudo observacional e ecológico (dados agregados por
  município, não por aluno). NUNCA apresente a recomendação como prova de
  causa e efeito. Use expressões como "os dados sugerem", "o padrão
  observado indica" ou "dentro da regra de negócio adotada pelo projeto".
- O índice de vulnerabilidade foi construído especificamente para este
  estudo, com pesos iguais entre os cinco componentes, por opção de
  simplicidade metodológica. Não é um indicador oficial do INEP e não foi
  validado externamente. Mencione isso quando relevante.
- Nunca invente valores, percentuais ou estatísticas que não estejam no
  contexto fornecido. Se um dado necessário não estiver disponível, diga
  isso explicitamente em vez de estimar.
- Não compare o município com médias nacionais ou de outras regiões que
  não estejam explicitamente presentes no contexto fornecido.

FORMATO DA RESPOSTA:

1. DIAGNÓSTICO DO MUNICÍPIO
   Resuma objetivamente o que os dados mostram: região, índice de
   vulnerabilidade, posição frente à média regional, nota média no ENEM.

2. ONDE PRIORIZAR
   Diga se este município se enquadra como prioridade geográfica alta,
   média ou baixa, explicando com os dois sinais (região + posição frente
   à média regional).

3. O QUE PRIORIZAR
   Aponte o componente de vulnerabilidade dominante e o tipo de
   investimento recomendado, incluindo o alerta de colinearidade quando
   aplicável.

4. LIMITAÇÕES DA ANÁLISE
   Lembre o gestor de que a recomendação é uma regra de negócio baseada em
   associação estatística, não uma prova de causalidade, e que o índice é
   exploratório.

5. AÇÕES ESTRATÉGICAS SUGERIDAS
   Até 3 ações concretas, coerentes apenas com os dados fornecidos.

Nunca apresente números que não possam ser calculados diretamente a partir
dos dados fornecidos no contexto.
"""


def _resumo_perfil(perfil: dict) -> str:
    linhas_componentes = "\n".join(
        f"  - {MAPA_COMPONENTE_INVESTIMENTO[c]['rotulo']}: {v}%"
        for c, v in perfil["componentes_detalhados_pct"].items()
    )

    return (
        f"Município: {perfil['municipio']} ({perfil['uf']}) — Região: {perfil['regiao']}\n"
        f"Região prioritária (Norte/Nordeste)? {'Sim' if perfil['regiao_prioritaria'] else 'Não'}\n"
        f"Índice de vulnerabilidade do município: {perfil['indice_vulnerabilidade']} "
        f"(escala 0 a 5)\n"
        f"Média do índice de vulnerabilidade na região {perfil['regiao']}: "
        f"{perfil['media_indice_regiao']}\n"
        f"Município está acima da média da própria região? "
        f"{'Sim' if perfil['acima_da_media_regional'] else 'Não'}\n"
        f"Componente de vulnerabilidade dominante: {perfil['componente_dominante']} "
        f"({perfil['componente_dominante_pct']}%)\n"
        f"Investimento sugerido pela regra de negócio: {perfil['investimento_sugerido']}\n"
        f"Alerta de colinearidade neste componente? "
        f"{'Sim' if perfil['alerta_colinearidade'] else 'Não'}\n"
        f"Percentuais de todos os componentes:\n{linhas_componentes}\n"
        f"Nota média geral do município no ENEM: {perfil.get('nota_enem_geral', 'N/A')} pts\n"
        f"Nota média da redação: {perfil.get('nota_redacao', 'N/A')} pts\n"
        f"Total de alunos analisados: {perfil['n_alunos']}"
    )


# ------------------------------------------------------------------
# Classe principal do agente (NVIDIA NIM — camada gratuita)
# ------------------------------------------------------------------

class AgenteConsultor:
    def __init__(self):
        load_dotenv()
        self._api_key = os.getenv("NVIDIA_API_KEY")
        if not self._api_key:
            raise EnvironmentError("Chave NVIDIA_API_KEY não encontrada no arquivo .env.")

        # Endpoint compatível com o SDK da OpenAI, hospedado pela NVIDIA
        # (build.nvidia.com). Camada gratuita: sem cartão de crédito,
        # limite de requisições por minuto em vez de créditos fixos.
        self._client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=self._api_key,
        )
        self._historico = []
        self._perfil_ativo = None
        self._model_id = "openai/gpt-oss-20b"

    def iniciar_sessao(self, nome_municipio: str, caminho_csv: str = "dados/tratado/tabela_municipio_final.csv"):
        perfil_mapeado = buscar_perfil_no_csv(nome_municipio, caminho_csv=caminho_csv)
        self._perfil_ativo = perfil_mapeado

        resumo = _resumo_perfil(perfil_mapeado)
        self._historico = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "system", "content": f"Contexto atual do município selecionado:\n{resumo}"},
        ]
        return resumo

    def chat(self, pergunta: str) -> str:
        if not self._perfil_ativo:
            return "⚠️ Nenhuma sessão ativa. Inicie a sessão informando o município primeiro."

        if not _esta_no_escopo(pergunta):
            return _MSG_FORA_DE_ESCOPO

        self._historico.append({"role": "user", "content": pergunta})

        try:
            completion = self._client.chat.completions.create(
                model=self._model_id,
                messages=self._historico,
                temperature=0.2,
                max_tokens=1024,
            )
            resposta_texto = completion.choices[0].message.content.strip()
            self._historico.append({"role": "assistant", "content": resposta_texto})
            return resposta_texto

        except Exception as e:
            return f"❌ Erro na comunicação com o endpoint da NVIDIA NIM: {e}"

    def limpar_historico(self):
        self._historico = []
        self._perfil_ativo = None


# ------------------------------------------------------------------
# Teste rápido (execução direta)
# ------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    municipio_teste = sys.argv[1] if len(sys.argv) > 1 else "São Paulo"
    caminho_csv_teste = sys.argv[2] if len(sys.argv) > 2 else "dados/tratado/tabela_municipio_final.csv"

    agente = AgenteConsultor()
    resumo = agente.iniciar_sessao(municipio_teste, caminho_csv=caminho_csv_teste)

    print("=" * 70)
    print("CONTEXTO CARREGADO")
    print("=" * 70)
    print(resumo)

    print("\n" + "=" * 70)
    print("RECOMENDAÇÃO DO AGENTE")
    print("=" * 70)
    resposta = agente.chat(
        "Onde e no que devemos priorizar investimento neste município?"
    )
    print(resposta)
