import hashlib
from playwright.async_api import async_playwright
from .base_scraper import BaseScraper, EditalBruto
from datetime import datetime
from typing import Optional
import re


class FunculturaScraper(BaseScraper):
    BASE_URL = "https://funcultura.es.gov.br"

    async def listar_editais(self) -> list[EditalBruto]:
        editais = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto(self.BASE_URL, wait_until="networkidle", timeout=30000)
            except Exception as e:
                print(f"[FUNCULTURA] Erro ao acessar {self.BASE_URL}: {e}")
                await browser.close()
                return editais

            # Tenta encontrar secao de editais
            try:
                await page.wait_for_selector(
                    "article, .edital-item, .post-item, .list-group-item, a[href*='edital']",
                    timeout=10000
                )
            except Exception:
                print("[FUNCULTURA] Nenhum container de editais encontrado.")
                await browser.close()
                return editais

            # Busca links que contenham "edital" na URL ou no texto
            links = await page.query_selector_all(
                "a[href*='edital'], a[href*='chamada'], a[href*='selecao']"
            )

            visited_urls = set()
            for link in links:
                try:
                    url = await link.get_attribute("href")
                    titulo = await link.inner_text()

                    if not url or url in visited_urls:
                        continue
                    visited_urls.add(url)

                    # Normaliza URL
                    if not url.startswith("http"):
                        url = f"{self.BASE_URL}{url}"

                    hash_c = hashlib.sha256(url.encode()).hexdigest()

                    edital = EditalBruto(
                        fonte="funcultura",
                        titulo=titulo.strip() or "Edital Funcultura",
                        url_origem=url,
                        data_publicacao=None,
                        data_encerramento=None,
                        conteudo_html=None,
                        url_pdf=None,
                        pdf_bytes=None,
                        hash_conteudo=hash_c,
                    )

                    # Acessa pagina interna
                    try:
                        await page.goto(url, wait_until="networkidle", timeout=15000)
                        conteudo = await page.content()
                        edital.conteudo_html = conteudo
                        edital.hash_conteudo = hashlib.sha256(
                            conteudo.encode()
                        ).hexdigest()

                        texto = await page.inner_text("body")
                        edital.data_encerramento = self._extrair_data(texto)

                        # Busca PDF
                        pdf_link = await page.query_selector("a[href$='.pdf']")
                        if pdf_link:
                            pdf_url = await pdf_link.get_attribute("href")
                            if pdf_url and not pdf_url.startswith("http"):
                                pdf_url = f"{self.BASE_URL}{pdf_url}"
                            edital.url_pdf = pdf_url
                            edital.pdf_bytes = await self.baixar_pdf(pdf_url)

                        await page.go_back(wait_until="networkidle", timeout=10000)
                    except Exception as e:
                        print(f"[FUNCULTURA] Erro na pagina interna {url}: {e}")

                    editais.append(edital)
                except Exception as e:
                    print(f"[FUNCULTURA] Erro ao processar link: {e}")
                    continue

            await browser.close()

        return editais

    def _extrair_data(self, texto: str) -> Optional[datetime]:
        padrao = r"\d{2}/\d{2}/\d{4}"
        match = re.search(padrao, texto)
        if match:
            try:
                return datetime.strptime(match.group(), "%d/%m/%Y")
            except ValueError:
                return None
        return None
