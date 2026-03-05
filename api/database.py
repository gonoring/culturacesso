import sqlite3
import json
import os
from pathlib import Path
from contextlib import contextmanager

DATABASE_PATH = os.getenv("DATABASE_PATH", "culturacesso.db")

# Caminho do seed relativo a raiz do projeto
SEED_PATH = Path(__file__).parent.parent / "data" / "seed.json"


def init_db():
    """Cria tabelas necessarias se nao existirem."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS editais_brutos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fonte TEXT NOT NULL,
            titulo TEXT NOT NULL,
            url_origem TEXT,
            data_publicacao TEXT,
            data_encerramento TEXT,
            conteudo_html TEXT,
            url_pdf TEXT,
            pdf_bytes BLOB,
            hash_conteudo TEXT UNIQUE,
            data_coleta TEXT NOT NULL,
            processado INTEGER DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS editais_estruturados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_bruto INTEGER UNIQUE,
            dados_json TEXT NOT NULL,
            data_processamento TEXT NOT NULL,
            confianca_extracao REAL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            email TEXT,
            telefone TEXT,
            projeto_descricao TEXT,
            editais_interesse TEXT,
            data_cadastro TEXT
        )
    """)
    conn.commit()

    # Auto-seed: se a tabela editais_estruturados estiver vazia e existir seed.json, carrega
    count = conn.execute("SELECT COUNT(*) FROM editais_estruturados").fetchone()[0]
    if count == 0 and SEED_PATH.exists():
        print(f"[SEED] Banco vazio. Carregando {SEED_PATH}...")
        try:
            seed_data = json.loads(SEED_PATH.read_text(encoding="utf-8"))
            for item in seed_data:
                conn.execute("""
                    INSERT OR IGNORE INTO editais_estruturados
                    (id_bruto, dados_json, data_processamento, confianca_extracao)
                    VALUES (?, ?, ?, ?)
                """, (
                    item["id_bruto"],
                    item["dados_json"],
                    item["data_processamento"],
                    item["confianca_extracao"],
                ))
            conn.commit()
            print(f"[SEED] {len(seed_data)} editais carregados do seed.")
        except Exception as e:
            print(f"[SEED] Erro ao carregar seed: {e}")

    conn.close()


@contextmanager
def get_db():
    """Context manager para conexao com o banco."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
