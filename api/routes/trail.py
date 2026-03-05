from datetime import datetime, date
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

    hoje = date.today()
    resultados = []
    for e in compativeis:
        # Calcula dias restantes
        dias_restantes = None
        enc_iso = None
        if e.data_encerramento:
            enc = e.data_encerramento
            if isinstance(enc, datetime):
                enc_date = enc.date()
                enc_iso = enc.isoformat()
            elif isinstance(enc, str):
                try:
                    enc_date = datetime.fromisoformat(enc).date()
                    enc_iso = enc
                except ValueError:
                    enc_date = None
                    enc_iso = enc
            else:
                enc_date = enc
                enc_iso = str(enc)
            if enc_date:
                dias_restantes = (enc_date - hoje).days

        resultados.append(EditalResultado(
            titulo=e.titulo,
            orgao=e.orgao_financiador,
            valor_minimo=e.valor_minimo,
            valor_maximo=e.valor_maximo,
            dificuldade=e.dificuldade,
            data_encerramento=enc_iso,
            dias_restantes=dias_restantes,
            url=e.url_origem,
            areas=[a.value if hasattr(a, "value") else a for a in e.areas_culturais],
        ))

    return ResultadoTrilha(
        total=len(resultados),
        editais=resultados,
        valor_potencial_total=sum(e.valor_maximo or 0 for e in compativeis),
    )
