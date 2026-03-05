import sqlite3
import os
from contextlib import contextmanager

DATABASE_PATH = os.getenv("DATABASE_PATH", "culturacesso.db")


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
