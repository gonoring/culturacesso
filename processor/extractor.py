import anthropic
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from .schema import EditalEstruturado, AreaCultural, NaturezaJuridica

load_dotenv()

client = anthropic.Anthropic()  # usa ANTHROPIC_API_KEY do ambiente

PROMPT_TEMPLATE = Path(__file__).parent.joinpath("prompts", "extract_edital.txt").read_text(encoding="utf-8")


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
        data = json.loads(raw)

        # Normaliza enums
        data["areas_culturais"] = [AreaCultural(a) for a in data.get("areas_culturais", [])]
        data["natureza_juridica"] = NaturezaJuridica(data.get("natureza_juridica", "ambos"))
        data["id_bruto"] = id_bruto
        data["url_origem"] = url_origem
        data["data_processamento"] = datetime.now()
        data["perguntas_qualificadoras"] = []  # preenchido pelo trail_builder

        return EditalEstruturado(**data)

    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"[ERRO] Falha ao processar edital {id_bruto}: {e}")
        return None
    except anthropic.APIError as e:
        print(f"[ERRO API] Falha na chamada Claude para edital {id_bruto}: {e}")
        return None
