# CulturaAcesso

Web app (PWA) que conecta produtores culturais do Espirito Santo aos editais de fomento compativeis com seus projetos.

## Como funciona

1. **Scraper** coleta editais culturais de fontes publicas do ES
2. **Processador** extrai atributos estruturados via Claude API
3. **Frontend** apresenta trilha de qualificacao que revela editais compativeis

## Stack

- **Scraping:** Python + Playwright + BeautifulSoup
- **Processamento:** Python + Claude API
- **Backend:** FastAPI + SQLite
- **Frontend:** Next.js 14 + Tailwind CSS

## Setup

```bash
# Backend
python -m venv venv
source venv/Scripts/activate  # Windows
pip install -r requirements.txt
pip install -e .
python -m playwright install chromium

# Frontend
cd frontend
npm install
npm run dev
```

## Executar

```bash
# Scraping
python -m scraper.main

# Processamento
python -m processor.main

# API
uvicorn api.main:app --reload --port 8000

# Frontend
cd frontend && npm run dev
```
