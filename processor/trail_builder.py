"""
Estrategia de montagem da trilha:

A trilha nao e gerada por edital individualmente — ela e gerada globalmente
a partir de TODOS os editais ativos, de modo que uma mesma pergunta filtre
multiplos editais simultaneamente. Isso evita repeticao e torna o fluxo fluido.

Estrutura da trilha:
  Bloco 1 — Natureza juridica e localizacao (filtros eliminatorios duros)
  Bloco 2 — Area cultural (filtragem por segmento)
  Bloco 3 — Estagio do projeto (estreante vs. experiente)
  Bloco 4 — Capacidade financeira (contrapartida)
  Bloco 5 — Prazo (editais com prazo proximo ou abertos)
  Resultado — Editais compativeis, valores e dificuldade
"""

from .schema import EditalEstruturado

PERGUNTAS_FIXAS = [
    {
        "id": "natureza_juridica",
        "bloco": 1,
        "texto": "Como você vai inscrever seu projeto?",
        "tipo": "single_choice",
        "opcoes": [
            {"valor": "pessoa_fisica", "label": "Como pessoa física (CPF)"},
            {"valor": "pessoa_juridica", "label": "Como pessoa jurídica (CNPJ)"},
            {"valor": "osc", "label": "Como organização da sociedade civil (OSC/associação)"},
        ]
    },
    {
        "id": "sede_es",
        "bloco": 1,
        "texto": "Seu projeto tem sede ou atuação principal no Espírito Santo?",
        "tipo": "boolean",
        "opcoes": [
            {"valor": True, "label": "Sim"},
            {"valor": False, "label": "Não"},
        ]
    },
    {
        "id": "areas_culturais",
        "bloco": 2,
        "texto": "Em que área cultural se enquadra o seu projeto? (pode marcar mais de uma)",
        "tipo": "multi_choice",
        "opcoes": [
            {"valor": "musica", "label": "Música"},
            {"valor": "teatro", "label": "Teatro"},
            {"valor": "danca", "label": "Dança"},
            {"valor": "audiovisual", "label": "Audiovisual (cinema, vídeo, podcast)"},
            {"valor": "artes_visuais", "label": "Artes visuais"},
            {"valor": "literatura", "label": "Literatura"},
            {"valor": "patrimonio", "label": "Patrimônio cultural"},
            {"valor": "circo", "label": "Circo"},
            {"valor": "cultura_popular", "label": "Cultura popular / folclore"},
        ]
    },
    {
        "id": "historico_projetos",
        "bloco": 3,
        "texto": "Você ou sua organização já executaram projetos culturais com financiamento público antes?",
        "tipo": "boolean",
        "opcoes": [
            {"valor": True, "label": "Sim, temos histórico comprovado"},
            {"valor": False, "label": "Não, é nossa primeira vez"},
        ]
    },
    {
        "id": "contrapartida",
        "bloco": 4,
        "texto": "Você tem capacidade de oferecer contrapartida financeira ao projeto (recursos próprios)?",
        "tipo": "single_choice",
        "opcoes": [
            {"valor": "nenhuma", "label": "Não tenho recursos próprios para contrapartida"},
            {"valor": "ate_20", "label": "Posso oferecer até 20% de contrapartida"},
            {"valor": "mais_20", "label": "Posso oferecer mais de 20% de contrapartida"},
        ]
    },
    {
        "id": "valor_esperado",
        "bloco": 4,
        "texto": "Qual o valor aproximado que você precisa captar para seu projeto?",
        "tipo": "single_choice",
        "opcoes": [
            {"valor": "ate_30k", "label": "Até R$ 30.000"},
            {"valor": "30k_100k", "label": "Entre R$ 30.000 e R$ 100.000"},
            {"valor": "100k_300k", "label": "Entre R$ 100.000 e R$ 300.000"},
            {"valor": "acima_300k", "label": "Acima de R$ 300.000"},
        ]
    },
]


def filtrar_editais(respostas: dict, editais: list[EditalEstruturado]) -> list[EditalEstruturado]:
    """
    Aplica as respostas da trilha para filtrar editais compativeis.

    respostas = {
        "natureza_juridica": "pessoa_fisica",
        "sede_es": True,
        "areas_culturais": ["musica", "audiovisual"],
        "historico_projetos": False,
        "contrapartida": "nenhuma",
        "valor_esperado": "ate_30k"
    }
    """
    compativeis = []

    for edital in editais:
        # Filtro 1: Natureza juridica
        nj = respostas.get("natureza_juridica")
        if nj == "pessoa_fisica" and edital.exige_cnpj:
            continue
        if nj in ("pessoa_juridica", "osc") and edital.natureza_juridica == "pessoa_fisica":
            continue

        # Filtro 2: Sede no ES
        if not respostas.get("sede_es") and edital.exige_sede_es:
            continue

        # Filtro 3: Area cultural
        areas_usuario = set(respostas.get("areas_culturais", []))
        areas_edital = set(a.value if hasattr(a, "value") else a for a in edital.areas_culturais)
        if "diversa" not in areas_edital and not areas_usuario.intersection(areas_edital):
            continue

        # Filtro 4: Historico
        if not respostas.get("historico_projetos") and edital.exige_historico_projetos:
            continue

        # Filtro 5: Contrapartida
        contra = respostas.get("contrapartida", "nenhuma")
        if edital.exige_contrapartida and contra == "nenhuma":
            continue

        # Filtro 6: Valor
        valor_map = {
            "ate_30k": 30000,
            "30k_100k": 100000,
            "100k_300k": 300000,
            "acima_300k": 9999999,
        }
        valor_max_usuario = valor_map.get(respostas.get("valor_esperado", "acima_300k"), 9999999)
        if edital.valor_minimo and edital.valor_minimo > valor_max_usuario:
            continue

        compativeis.append(edital)

    return compativeis
