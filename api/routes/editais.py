from fastapi import APIRouter
from api.database import get_db
import json

router = APIRouter()


@router.get("/")
def listar_editais():
    """Lista todos os editais processados."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id_bruto, dados_json, confianca_extracao FROM editais_estruturados"
        ).fetchall()

    editais = []
    for row in rows:
        try:
            dados = json.loads(row["dados_json"])
            editais.append({
                "id": row["id_bruto"],
                "titulo": dados.get("titulo"),
                "orgao": dados.get("orgao_financiador"),
                "areas": dados.get("areas_culturais", []),
                "valor_maximo": dados.get("valor_maximo"),
                "dificuldade": dados.get("dificuldade"),
                "confianca": row["confianca_extracao"],
            })
        except json.JSONDecodeError:
            continue

    return {"total": len(editais), "editais": editais}
