from fastapi import APIRouter
from api.models import RespostasUsuario, ResultadoTrilha, EditalResultado
from api.database import get_db
from processor.trail_builder import PERGUNTAS_FIXAS, filtrar_editais
from processor.schema import EditalEstruturado
import json

router = APIRouter()


@router.get("/perguntas")
def obter_perguntas():
    """Retorna a trilha de perguntas para o frontend."""
    return {"perguntas": PERGUNTAS_FIXAS}


@router.post("/resultado", response_model=ResultadoTrilha)
def calcular_resultado(respostas: RespostasUsuario):
    """Recebe as respostas e retorna os editais compativeis."""
    with get_db() as conn:
        rows = conn.execute("SELECT dados_json FROM editais_estruturados").fetchall()

    editais = []
    for r in rows:
        try:
            editais.append(EditalEstruturado(**json.loads(r["dados_json"])))
        except Exception:
            continue

    compativeis = filtrar_editais(respostas.model_dump(), editais)

    # Ordena: primeiro os de maior valor maximo, depois por dificuldade
    compativeis.sort(key=lambda e: (-(e.valor_maximo or 0), e.dificuldade))

    return ResultadoTrilha(
        total=len(compativeis),
        editais=[
            EditalResultado(
                titulo=e.titulo,
                orgao=e.orgao_financiador,
                valor_maximo=e.valor_maximo,
                dificuldade=e.dificuldade,
                data_encerramento=e.data_encerramento.isoformat() if e.data_encerramento else None,
                url=e.url_origem,
                areas=[a.value for a in e.areas_culturais],
            )
            for e in compativeis
        ],
        valor_potencial_total=sum(e.valor_maximo or 0 for e in compativeis),
    )
