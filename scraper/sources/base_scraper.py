from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import asyncio
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
    # Subclasses podem sobrescrever esses valores
    REQUEST_DELAY: float = 1.0       # segundos entre requisicoes sequenciais
    MAX_RETRIES: int = 3
    RETRY_BACKOFF: float = 2.0       # multiplicador de backoff exponencial

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30,
            headers={"User-Agent": "CulturaAcesso/1.0 (+https://github.com/gonoring/culturacesso)"},
            follow_redirects=True,
        )

    @abstractmethod
    async def listar_editais(self) -> list[EditalBruto]:
        """Retorna lista de editais encontrados na fonte."""
        pass

    async def baixar_pdf(self, url: str) -> Optional[bytes]:
        try:
            resp = await self._request_with_retry("GET", url)
            return resp.content if resp and resp.status_code == 200 else None
        except Exception:
            return None

    async def _request_with_retry(
        self, method: str, url: str, **kwargs
    ) -> Optional[httpx.Response]:
        """Requisicao HTTP com retry e backoff exponencial."""
        for attempt in range(self.MAX_RETRIES):
            try:
                resp = await self.client.request(method, url, **kwargs)
                if resp.status_code == 429:
                    retry_after = int(resp.headers.get("Retry-After", 5))
                    print(f"  [RATE-LIMIT] Aguardando {retry_after}s...")
                    await asyncio.sleep(retry_after)
                    continue
                return resp
            except (httpx.TimeoutException, httpx.ConnectError) as e:
                wait = self.RETRY_BACKOFF ** attempt
                print(f"  [RETRY {attempt + 1}/{self.MAX_RETRIES}] {e}. Aguardando {wait:.0f}s...")
                await asyncio.sleep(wait)
        return None

    async def _polite_delay(self):
        """Espera entre requisicoes para respeitar o servidor."""
        await asyncio.sleep(self.REQUEST_DELAY)

    async def close(self):
        await self.client.aclose()
