import hashlib
from playwright.async_api import async_playwright
from .base_scraper import BaseScraper, EditalBruto
from datetime import datetime
from typing import Optional
import re


class PrefeituraVitoriaScraper(BaseScraper):
    BASE_URL = "https://cultura.vitoria.es.gov.br/editais"

    async def listar_editais(self) -> list[EditalBruto]:
        editais = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto(self.BASE_URL, wait_until="networkidle", timeout=30000)
            except Exception as e:
                print(f"[PMV] Erro ao acessar {self.BASE_URL}: {e}")
                await browser.close()
                return editais

            try:
                await page.wait_for_selector(
                    "article, .edital-item, .post-item, .list-group-item",
                    timeout=10000
                )
            except Exception:
                print("[PMV] Nenhum container de editais encontrado.")
                await browser.close()
                return editais

            items = await page.query_selector_all(
                "article, .edital-item, .list-group-item, .post-item"
            )

            for item in items:
                try:
                    titulo_el = await item.query_selector("h2, h3, .titulo, a")
                    titulo = await titulo_el.inner_text() if titulo_el else "Sem titulo"

                    link_el = await item.query_selector("a")
                    url = await link_el.get_attribute("href") if link_el else None

                    if url and not url.startswith("http"):
                        url = f"https://cultura.vitoria.es.gov.br{url}"

                    texto = await item.inner_text()
                    data_enc = self._extrair_data(texto)

                    conteudo_html = await item.inner_html()
                    hash_c = hashlib.sha256(conteudo_html.encode()).hexdigest()

                    edital = EditalBruto(
                        fonte="prefeitura_vitoria",
                        titulo=titulo.strip(),
                        url_origem=url or self.BASE_URL,
                        data_publicacao=None,
                        data_encerramento=data_enc,
                        conteudo_html=conteudo_html,
                        url_pdf=None,
                        pdf_bytes=None,
                        hash_conteudo=hash_c,
                    )

                    # Acessa pagina interna
                    if url and not url.endswith(".pdf"):
                        try:
                            await page.goto(url, wait_until="networkidle", timeout=15000)
                            pdf_link = await page.query_selector("a[href$='.pdf']")
                            if pdf_link:
                                pdf_url = await pdf_link.get_attribute("href")
                                if pdf_url and not pdf_url.startswith("http"):
                                    pdf_url = f"https://cultura.vitoria.es.gov.br{pdf_url}"
                                edital.url_pdf = pdf_url
                                edital.pdf_bytes = await self.baixar_pdf(pdf_url)
                            edital.conteudo_html = await page.content()
                            edital.hash_conteudo = hashlib.sha256(
                                edital.conteudo_html.encode()
                            ).hexdigest()
                            await page.go_back(wait_until="networkidle", timeout=10000)
                        except Exception as e:
                            print(f"[PMV] Erro na pagina interna: {e}")
                    elif url and url.endswith(".pdf"):
                        edital.url_pdf = url
                        edital.pdf_bytes = await self.baixar_pdf(url)

                    editais.append(edital)
                except Exception as e:
                    print(f"[PMV] Erro ao processar item: {e}")
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
