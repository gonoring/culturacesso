import asyncio
from .sources.secult_es import SecultEsScraper
from .sources.funcultura import FunculturaScraper
from .sources.prefeitura_vitoria import PrefeituraVitoriaScraper
from .storage import ScraperStorage

SCRAPERS = [
    SecultEsScraper,
    FunculturaScraper,
    PrefeituraVitoriaScraper,
]


async def executar_scraping():
    storage = ScraperStorage()
    total_novos = 0

    for ScraperClass in SCRAPERS:
        scraper = ScraperClass()
        nome = ScraperClass.__name__
        print(f"\n--- Executando {nome} ---")
        try:
            editais = await scraper.listar_editais()
            print(f"[{nome}] {len(editais)} editais encontrados.")
            for edital in editais:
                inserido = storage.salvar(edital)
                if inserido:
                    total_novos += 1
                    print(f"  [NOVO] {edital.fonte}: {edital.titulo[:80]}")
                else:
                    print(f"  [JA EXISTE] {edital.titulo[:80]}")
        except Exception as e:
            print(f"  [ERRO] {nome}: {e}")
        finally:
            await scraper.close()

    print(f"\nScraping concluido. {total_novos} novos editais coletados.")


if __name__ == "__main__":
    asyncio.run(executar_scraping())
