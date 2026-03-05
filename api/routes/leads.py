from fastapi import APIRouter
from api.models import Lead
from api.database import get_db
from datetime import datetime
import json

router = APIRouter()


@router.post("/")
def registrar_lead(lead: Lead):
    """Registra um lead (potencial cliente)."""
    with get_db() as conn:
        conn.execute("""
            INSERT INTO leads (nome, email, telefone, projeto_descricao, editais_interesse, data_cadastro)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            lead.nome, lead.email, lead.telefone, lead.projeto_descricao,
            json.dumps(lead.editais_interesse), datetime.now().isoformat()
        ))
        conn.commit()

    return {"status": "ok", "mensagem": "Lead registrado. Nossa equipe entrará em contato em até 24h."}
