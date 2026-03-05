import hashlib
from playwright.async_api import async_playwright
from .base_scraper import BaseScraper, EditalBruto
from datetime import datetime
from typing import Optional
import re


class SecultEsScraper(BaseScraper):
    """Scraper para editais da Secretaria de Cultura do ES (Secult).

    A pagina usa Bootstrap 4 com data-toggle="collapse".
    Cada edital tem um h4 com [data-toggle="collapse"] e uma
    tabela .table com links de PDF dentro do painel colapsavel.
    """

    BASE_URL = "https://secult.es.gov.br/edital-2025"

    async def listar_editais(self) -> list[EditalBruto]:
        editais = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto(self.BASE_URL, wait_until="networkidle", timeout=30000)
            except Exception as e:
                print(f"[SECULT-ES] Erro ao acessar {self.BASE_URL}: {e}")
                await browser.close()
                return editais

            # Aguarda os h4 carregarem
            try:
                await page.wait_for_selector("h4", timeout=10000)
            except Exception:
                print("[SECULT-ES] Nenhum edital encontrado na pagina.")
                await browser.close()
                return editais

            # Extrai todos os dados de uma vez via JavaScript
            dados = await page.evaluate(
                """
                () => {
                    // Pega h4 que sao toggles de collapse (editais)
                    let toggles = document.querySelectorAll('h4[data-toggle="collapse"]');

                    // Fallback: h4 cujo texto comeca com "Edital"
                    if (toggles.length === 0) {
                        toggles = Array.from(document.querySelectorAll('h4'))
                            .filter(h => h.textContent.trim().match(/^Edital\\s/i));
                    }

                    return Array.from(toggles).map(h4 => {
                        const titulo = h4.textContent.trim();

                        // Busca o painel de collapse associado (proximo irmao div.collapse)
                        let panel = h4.nextElementSibling;
                        while (panel && !panel.classList.contains('collapse')) {
                            panel = panel.nextElementSibling;
                        }

                        // Combina h4 + painel para conteudo completo
                        const pdfLinks = [];
                        let texto = titulo;
                        let html = h4.outerHTML;

                        if (panel) {
                            const allLinks = Array.from(panel.querySelectorAll('a'));
                            for (const a of allLinks) {
                                if (a.href && a.href.toLowerCase().includes('.pdf')) {
                                    pdfLinks.push(a.href);
                                }
                            }
                            texto += ' ' + panel.textContent;
                            html += panel.innerHTML;
                        }

                        return { titulo, pdfLinks, texto, html };
                    });
                }
            """
            )

            print(f"[SECULT-ES] {len(dados)} editais encontrados na pagina.")

            for item in dados:
                try:
                    titulo = item["titulo"]
                    pdf_urls = item["pdfLinks"]
                    texto = item["texto"]
                    html = item["html"]

                    # Normaliza URLs de PDF
                    pdfs_normalizados = []
                    for pdf in pdf_urls:
                        if not pdf.startswith("http"):
                            pdf = f"https://secult.es.gov.br{pdf}"
                        pdfs_normalizados.append(pdf)

                    hash_c = hashlib.sha256(html.encode()).hexdigest()
                    data_enc = self._extrair_data(texto)

                    edital = EditalBruto(
                        fonte="secult_es",
                        titulo=titulo,
                        url_origem=self.BASE_URL,
                        data_publicacao=None,
                        data_encerramento=data_enc,
                        conteudo_html=html,
                        url_pdf=pdfs_normalizados[0] if pdfs_normalizados else None,
                        pdf_bytes=None,
                        hash_conteudo=hash_c,
                    )

                    # Baixa o primeiro PDF se disponivel
                    if edital.url_pdf:
                        edital.pdf_bytes = await self.baixar_pdf(edital.url_pdf)

                    editais.append(edital)
                    print(f"  [OK] {titulo[:80]}")
                except Exception as e:
                    print(f"[SECULT-ES] Erro ao processar item: {e}")
                    continue

            await browser.close()

        return editais

    def _extrair_data(self, texto: str) -> Optional[datetime]:
        """Extrai a ultima data no formato DD/MM/AAAA encontrada no texto."""
        padrao = r"\d{2}/\d{2}/\d{4}"
        datas = re.findall(padrao, texto)
        if datas:
            try:
                return datetime.strptime(datas[-1], "%d/%m/%Y")
            except ValueError:
                return None
        return None
