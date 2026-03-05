from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Optional


class RespostasUsuario(BaseModel):
    natureza_juridica: Literal["pessoa_fisica", "mei", "pessoa_juridica", "osc"]
    sede_es: bool
    areas_culturais: list[Literal[
        "musica", "teatro", "danca", "audiovisual", "artes_visuais",
        "literatura", "patrimonio", "circo", "cultura_popular"
    ]] = Field(..., max_length=9)
    historico_projetos: bool
    contrapartida: Literal["nenhuma", "ate_20", "mais_20"]
    valor_esperado: Literal["ate_30k", "30k_100k", "100k_300k", "acima_300k"]


class EditalResultado(BaseModel):
    titulo: str
    orgao: str
    valor_maximo: Optional[float] = None
    dificuldade: str
    data_encerramento: Optional[str] = None
    url: str
    areas: list[str]


class ResultadoTrilha(BaseModel):
    total: int
    editais: list[EditalResultado]
    valor_potencial_total: float


class Lead(BaseModel):
    nome: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    telefone: str = Field(..., min_length=8, max_length=20, pattern=r'^[\d\s\(\)\+\-]+$')
    projeto_descricao: str = Field(..., min_length=1, max_length=2000)
    editais_interesse: list[str] = Field(..., max_length=50)
