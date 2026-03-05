import hashlib
from playwright.async_api import async_playwright
from .base_scraper import BaseScraper, EditalBruto
from datetime import datetime
from typing import Optional
import re


class GovernoEsScraper(BaseScraper):
    """Scraper para noticias sobre editais culturais no portal do Governo do ES.

    O site es.gov.br publica noticias sobre lancamento de editais de cultura.
    Este scraper busca as noticias mais recentes com palavras-chave relevantes
    e extrai links para editais completos.
    """

    URLS = [
        "https://www.es.gov.br/Noticias",
    ]

    PALAVRAS_CHAVE = ["edital", "editais", "cultura", "funcultura", "secult", "pnab"]

    async def listar_editais(self) -> list[EditalBruto]:
        editais = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto(self.URLS[0], wait_until="networkidle", timeout=30000)
            except Exception as e:
                print(f"[GOVERNO-ES] Erro ao acessar {self.URLS[0]}: {e}")
                await browser.close()
                return editais

            # Aguarda links de noticias carregarem
            try:
                await page.wait_for_selector("a[href*='/Noticia/']", timeout=10000)
            except Exception:
                print("[GOVERNO-ES] Nenhuma noticia encontrada.")
                await browser.close()
                return editais

            # Extrai todos os links de noticias via JavaScript
            # Requer AMBAS: uma palavra de "edital" E uma de "cultura"
            dados = await page.evaluate("""
                () => {
                    const links = document.querySelectorAll('a[href*="/Noticia/"]');
                    const resultados = [];
                    const visitados = new Set();

                    const termos_edital = ['edital', 'editais', 'chamamento', 'selecao'];
                    const termos_cultura = [
                        'cultura', 'cultural', 'funcultura', 'secult',
                        'pnab', 'aldir blanc', 'paulo gustavo', 'rubem braga',
                        'artista', 'musica', 'teatro', 'audiovisual', 'arte'
                    ];

                    for (const link of links) {
                        const url = link.href;
                        const titulo = link.textContent.trim();

                        if (!titulo || titulo.length < 10 || visitados.has(url)) continue;
                        visitados.add(url);

                        const textoLower = (titulo + ' ' + url).toLowerCase();

                        // Deve conter pelo menos um termo de edital E um de cultura
                        const temEdital = termos_edital.some(t => textoLower.includes(t));
                        const temCultura = termos_cultura.some(t => textoLower.includes(t));

                        if (temEdital && temCultura) {
                            resultados.push({ titulo, url });
                        }
                    }
                    return resultados;
                }
            """)

            print(f"[GOVERNO-ES] {len(dados)} noticias relevantes encontradas.")

            for item in dados:
                try:
                    titulo = item["titulo"]
                    url = item["url"]

                    if not url.startswith("http"):
                        url = f"https://www.es.gov.br{url}"

                    # Acessa a pagina da noticia para pegar conteudo completo
                    conteudo_html = ""
                    pdf_url = None
                    data_enc = None

                    try:
                        await page.goto(url, wait_until="networkidle", timeout=15000)
                        conteudo_html = await page.evaluate("""
                            () => {
                                const main = document.querySelector(
                                    'article, .noticia-conteudo, .content, main, .post-content'
                                );
                                return main ? main.innerHTML : document.body.innerHTML;
                            }
                        """)

                        # Busca link de PDF na pagina
                        pdf_link_href = await page.evaluate("""
                            () => {
                                const pdfLink = document.querySelector('a[href$=".pdf"]');
                                return pdfLink ? pdfLink.href : null;
                            }
                        """)
                        pdf_url = pdf_link_href

                        texto = await page.evaluate("() => document.body.innerText")
                        data_enc = self._extrair_data(texto)

                    except Exception as e:
                        print(f"[GOVERNO-ES] Erro na pagina interna {url}: {e}")
                        conteudo_html = titulo

                    hash_c = hashlib.sha256(
                        (conteudo_html or titulo).encode()
                    ).hexdigest()

                    edital = EditalBruto(
                        fonte="governo_es",
                        titulo=titulo,
                        url_origem=url,
                        data_publicacao=None,
                        data_encerramento=data_enc,
                        conteudo_html=conteudo_html,
                        url_pdf=pdf_url,
                        pdf_bytes=None,
                        hash_conteudo=hash_c,
                    )

                    if edital.url_pdf:
                        edital.pdf_bytes = await self.baixar_pdf(edital.url_pdf)

                    editais.append(edital)
                    print(f"  [OK] {titulo[:80]}")
                except Exception as e:
                    print(f"[GOVERNO-ES] Erro ao processar noticia: {e}")
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
