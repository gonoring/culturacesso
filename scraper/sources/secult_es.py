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

            # Expande todos os paineis colapsaveis antes de extrair
            try:
                await page.evaluate("""
                    () => {
                        const panels = document.querySelectorAll('.collapse, .panel-collapse');
                        for (const p of panels) {
                            p.classList.add('show', 'in');
                            p.style.display = 'block';
                            p.style.height = 'auto';
                        }
                    }
                """)
                await page.wait_for_timeout(1000)
            except Exception:
                pass

            # Extrai dados via JavaScript — CORRIGIDO:
            # O data-toggle="collapse" esta no <a> PAI do h4, nao no h4.
            # O painel e referenciado pelo href do <a> (ex: #collapse-37447).
            dados = await page.evaluate(
                """
                () => {
                    // Busca os <a> com data-toggle="collapse" que contem um h4
                    const toggleLinks = document.querySelectorAll('a[data-toggle="collapse"]');
                    const results = [];
                    const seen = new Set();

                    for (const a of toggleLinks) {
                        const h4 = a.querySelector('h4');
                        if (!h4) continue;

                        const titulo = h4.textContent.trim();
                        if (!titulo.match(/^Edital\\s/i)) continue;
                        if (seen.has(titulo)) continue;
                        seen.add(titulo);

                        // Busca o painel pelo ID referenciado no href
                        const target = a.getAttribute('href') || a.getAttribute('data-target');
                        let panel = null;
                        if (target && target.startsWith('#')) {
                            panel = document.querySelector(target);
                        }

                        const pdfLinks = [];
                        let texto = titulo;
                        let html = a.outerHTML;

                        if (panel) {
                            // Texto completo do painel
                            texto += '\\n\\n' + panel.innerText;
                            html = a.outerHTML + '\\n' + panel.outerHTML;

                            // Links de PDF (sem duplicatas)
                            const seenPdfs = new Set();
                            const allLinks = panel.querySelectorAll('a[href]');
                            for (const link of allLinks) {
                                const href = link.href || '';
                                if (href.toLowerCase().includes('.pdf') && !seenPdfs.has(href)) {
                                    seenPdfs.add(href);
                                    pdfLinks.push(href);
                                }
                            }
                        }

                        results.push({ titulo, pdfLinks, texto, html });
                    }
                    return results;
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
