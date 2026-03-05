from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime
from enum import Enum


class AreaCultural(str, Enum):
    MUSICA = "musica"
    TEATRO = "teatro"
    DANCA = "danca"
    AUDIOVISUAL = "audiovisual"
    ARTES_VISUAIS = "artes_visuais"
    LITERATURA = "literatura"
    PATRIMONIO = "patrimonio"
    CIRCO = "circo"
    CULTURA_POPULAR = "cultura_popular"
    DIVERSA = "diversa"  # edital multi-area


class NaturezaJuridica(str, Enum):
    PESSOA_FISICA = "pessoa_fisica"
    PESSOA_JURIDICA = "pessoa_juridica"
    AMBOS = "ambos"
    OSC = "osc"  # Org. da Soc. Civil exclusivamente


class EditalEstruturado(BaseModel):
    # Identificacao
    id_bruto: int                           # FK para editais_brutos.id
    titulo: str
    orgao_financiador: str                  # "Secult-ES", "PMV", etc.
    url_origem: str

    # Elegibilidade — base da logica de filtragem
    areas_culturais: list[AreaCultural]
    natureza_juridica: NaturezaJuridica
    exige_cnpj: bool
    exige_sede_es: bool
    exige_historico_projetos: bool          # Exige experiencia comprovada anterior
    permite_estreante: bool

    # Financeiro
    valor_minimo: Optional[float] = None    # Em R$
    valor_maximo: Optional[float] = None
    valor_tipico: Optional[float] = None    # Valor medio historico aprovado
    exige_contrapartida: bool
    percentual_contrapartida: Optional[float] = None  # 0-100

    # Prazos
    data_encerramento: Optional[datetime] = None
    vigencia_projeto_meses: Optional[int] = None  # Duracao maxima do projeto

    # Documentacao
    documentos_exigidos: list[str]          # Lista resumida

    # Dificuldade estimada
    dificuldade: Literal["baixa", "media", "alta"]
    justificativa_dificuldade: str

    # Trilha — perguntas especificas geradas para este edital
    perguntas_qualificadoras: list[dict] = []

    # Metadados
    data_processamento: datetime
    confianca_extracao: float               # 0-1; indica qualidade da extracao
