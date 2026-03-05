import hashlib
from playwright.async_api import async_playwright
from .base_scraper import BaseScraper, EditalBruto
from datetime import datetime
from typing import Optional
import re


class PrefeituraVitoriaScraper(BaseScraper):
    """Scraper para editais da Secretaria de Cultura de Vitoria (SEMC).

    O portal de editais (vitoria.es.gov.br/editais-semc) redireciona para
    sistemas.vitoria.es.gov.br/docOficial/?tp=template3&c=78, que carrega
    os editais via AJAX no container #dvContainer.
    """

    # URL final apos redirect
    BASE_URL = "https://sistemas.vitoria.es.gov.br/docOficial/?tp=template3&c=78"
    DOMAIN = "https://sistemas.vitoria.es.gov.br"

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

            # Aguarda o container AJAX carregar com conteudo
            try:
                await page.wait_for_selector("#dvContainer", timeout=10000)
                # Espera adicional para o AJAX popular o container
                await page.wait_for_function(
                    """() => {
                        const c = document.querySelector('#dvContainer');
                        return c && c.innerHTML.trim().length > 50;
                    }""",
                    timeout=15000,
                )
            except Exception:
                print("[PMV] Container de editais vazio ou nao carregou.")
                # Tenta clicar no ano mais recente para forcar carregamento
                try:
                    ano_btn = await page.query_selector(".fAno:first-child, a[onclick*='2026'], a[onclick*='2025']")
                    if ano_btn:
                        await ano_btn.click()
                        await page.wait_for_timeout(3000)
                except Exception:
                    pass

            # Tenta extrair novamente apos possivel clique
            try:
                await page.wait_for_function(
                    """() => {
                        const c = document.querySelector('#dvContainer');
                        return c && c.children.length > 0;
                    }""",
                    timeout=10000,
                )
            except Exception:
                print("[PMV] Nenhum edital encontrado apos espera.")
                await browser.close()
                return editais

            # Extrai dados via JavaScript
            dados = await page.evaluate("""
                () => {
                    const container = document.querySelector('#dvContainer');
                    if (!container) return [];

                    // Busca links para documentos/editais
                    const links = container.querySelectorAll('a[href]');
                    const resultados = [];
                    const visitados = new Set();

                    for (const link of links) {
                        const url = link.href;
                        const titulo = link.textContent.trim();

                        if (!titulo || titulo.length < 5 || visitados.has(url)) continue;
                        visitados.add(url);

                        // Pega o elemento pai para contexto (data, descricao)
                        const row = link.closest('tr') || link.closest('div') || link.parentElement;
                        const contexto = row ? row.textContent.trim() : '';

                        resultados.push({
                            titulo: titulo,
                            url: url,
                            contexto: contexto,
                            html: row ? row.innerHTML : link.outerHTML,
                            isPdf: url.toLowerCase().endsWith('.pdf')
                        });
                    }

                    // Se nao encontrou links, tenta pegar todo o texto do container
                    if (resultados.length === 0) {
                        const textos = container.querySelectorAll('div, p, li, tr');
                        for (const el of textos) {
                            const texto = el.textContent.trim();
                            if (texto.length > 20) {
                                resultados.push({
                                    titulo: texto.substring(0, 200),
                                    url: window.location.href,
                                    contexto: texto,
                                    html: el.innerHTML,
                                    isPdf: false
                                });
                            }
                        }
                    }

                    return resultados;
                }
            """)

            print(f"[PMV] {len(dados)} itens encontrados no container.")

            for item in dados:
                try:
                    titulo = item["titulo"]
                    url = item["url"]
                    contexto = item["contexto"]
                    html = item["html"]
                    is_pdf = item["isPdf"]

                    if not url.startswith("http"):
                        url = f"{self.DOMAIN}{url}"

                    # Usa URL + titulo como base do hash (evita colisao quando
                    # vários itens compartilham o mesmo container HTML)
                    hash_source = f"{url}|{titulo}"
                    hash_c = hashlib.sha256(hash_source.encode()).hexdigest()
                    data_enc = self._extrair_data(contexto)

                    edital = EditalBruto(
                        fonte="prefeitura_vitoria",
                        titulo=titulo[:200],
                        url_origem=url,
                        data_publicacao=None,
                        data_encerramento=data_enc,
                        conteudo_html=html,
                        url_pdf=url if is_pdf else None,
                        pdf_bytes=None,
                        hash_conteudo=hash_c,
                    )

                    # Baixa o PDF se o link for direto para PDF
                    if edital.url_pdf:
                        edital.pdf_bytes = await self.baixar_pdf(edital.url_pdf)

                    editais.append(edital)
                    print(f"  [OK] {titulo[:80]}")
                except Exception as e:
                    print(f"[PMV] Erro ao processar item: {e}")
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
