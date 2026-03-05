from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import httpx


@dataclass
class EditalBruto:
    fonte: str                    # "secult_es", "funcultura", etc.
    titulo: str
    url_origem: str
    data_publicacao: Optional[datetime]
    data_encerramento: Optional[datetime]
    conteudo_html: Optional[str]
    url_pdf: Optional[str]
    pdf_bytes: Optional[bytes]
    hash_conteudo: str            # SHA256 do conteudo — evita reprocessamento


class BaseScraper(ABC):
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30)

    @abstractmethod
    async def listar_editais(self) -> list[EditalBruto]:
        """Retorna lista de editais encontrados na fonte."""
        pass

    async def baixar_pdf(self, url: str) -> Optional[bytes]:
        try:
            resp = await self.client.get(url)
            return resp.content if resp.status_code == 200 else None
        except Exception:
            return None

    async def close(self):
        await self.client.aclose()
