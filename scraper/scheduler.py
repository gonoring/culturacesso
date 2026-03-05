"""
Executa o scraping toda segunda-feira as 8h.
Deploy: Railway Cron Job ou crontab no servidor.
"""

import schedule
import time
import asyncio
from .main import executar_scraping


schedule.every().monday.at("08:00").do(lambda: asyncio.run(executar_scraping()))

if __name__ == "__main__":
    # Executa uma vez ao iniciar
    print("Executando scraping inicial...")
    asyncio.run(executar_scraping())

    print("\nScheduler iniciado. Proxima execucao: segunda-feira as 08:00.")
    while True:
        schedule.run_pending()
        time.sleep(60)
