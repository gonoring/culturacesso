import anthropic
import json
import re
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from .schema import EditalEstruturado, AreaCultural, NaturezaJuridica

load_dotenv()

client = anthropic.Anthropic()  # usa ANTHROPIC_API_KEY do ambiente

PROMPT_TEMPLATE = Path(__file__).parent.joinpath("prompts", "extract_edital.txt").read_text(encoding="utf-8")


def _limpar_json(raw: str) -> str:
    """Remove markdown code fences e texto extra ao redor do JSON."""
    # Remove ```json ... ``` ou ``` ... ```
    match = re.search(r'```(?:json)?\s*\n?(.*?)\n?\s*```', raw, re.DOTALL)
    if match:
        raw = match.group(1).strip()

    # Se nao comeca com {, encontra o primeiro {
    if not raw.startswith('{'):
        idx = raw.find('{')
        if idx != -1:
            raw = raw[idx:]

    # Se nao termina com }, encontra o ultimo }
    if not raw.endswith('}'):
        idx = raw.rfind('}')
        if idx != -1:
            raw = raw[:idx + 1]

    return raw.strip()


def extrair_atributos(conteudo: str, id_bruto: int, url_origem: str) -> EditalEstruturado | None:
    """
    Chama Claude para extrair atributos estruturados de um edital.
    Retorna EditalEstruturado ou None em caso de falha.
    """
    prompt = PROMPT_TEMPLATE.replace("{conteudo}", conteudo[:12000])  # limita tokens

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        raw = response.content[0].text.strip()
        clean = _limpar_json(raw)
        data = json.loads(clean)

        # --- Normaliza enums com fallback seguro para None ---

        # areas_culturais: data.get() retorna None quando chave existe com valor null
        areas_raw = data.get("areas_culturais") or []
        data["areas_culturais"] = []
        for a in areas_raw:
            try:
                data["areas_culturais"].append(AreaCultural(a))
            except ValueError:
                print(f"  [WARN] Area cultural desconhecida ignorada: {a}")

        # natureza_juridica: mesmo problema com None
        nat_raw = data.get("natureza_juridica") or "ambos"
        try:
            data["natureza_juridica"] = NaturezaJuridica(nat_raw)
        except ValueError:
            data["natureza_juridica"] = NaturezaJuridica.AMBOS

        # --- Garante booleanos com default False ---
        for campo_bool in [
            "exige_cnpj", "exige_sede_es", "exige_historico_projetos",
            "permite_estreante", "exige_contrapartida"
        ]:
            if data.get(campo_bool) is None:
                data[campo_bool] = False

        # --- Garante listas nao-None ---
        if data.get("documentos_exigidos") is None:
            data["documentos_exigidos"] = []

        # --- Garante strings obrigatorias ---
        if not data.get("dificuldade"):
            data["dificuldade"] = "media"
        if not data.get("justificativa_dificuldade"):
            data["justificativa_dificuldade"] = "Nao foi possivel avaliar com as informacoes disponiveis."
        if not data.get("orgao_financiador"):
            data["orgao_financiador"] = "Nao identificado"
        if not data.get("titulo"):
            data["titulo"] = "Edital sem titulo"

        # --- Garante confianca_extracao ---
        if data.get("confianca_extracao") is None:
            data["confianca_extracao"] = 0.5

        # --- Campos internos ---
        data["id_bruto"] = id_bruto
        data["url_origem"] = url_origem
        data["data_processamento"] = datetime.now()
        data["perguntas_qualificadoras"] = []  # preenchido pelo trail_builder

        return EditalEstruturado(**data)

    except (json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
        print(f"[ERRO] Falha ao processar edital {id_bruto}: {e}")
        if 'raw' in locals():
            print(f"  [DEBUG] Resposta bruta (primeiros 300 chars): {raw[:300]}")
        return None
    except anthropic.APIError as e:
        print(f"[ERRO API] Falha na chamada Claude para edital {id_bruto}: {e}")
        return None
