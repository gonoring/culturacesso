import sqlite3
from .sources.base_scraper import EditalBruto
from datetime import datetime


class ScraperStorage:
    def __init__(self, db_path: str = "culturacesso.db"):
        self.conn = sqlite3.connect(db_path)
        self._criar_tabelas()

    def _criar_tabelas(self):
        self.conn.execute("""
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
        self.conn.commit()

    def salvar(self, edital: EditalBruto) -> bool:
        """Retorna True se inserido, False se ja existia (hash duplicado)."""
        try:
            self.conn.execute("""
                INSERT INTO editais_brutos
                (fonte, titulo, url_origem, data_publicacao, data_encerramento,
                 conteudo_html, url_pdf, pdf_bytes, hash_conteudo, data_coleta)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                edital.fonte, edital.titulo, edital.url_origem,
                edital.data_publicacao.isoformat() if edital.data_publicacao else None,
                edital.data_encerramento.isoformat() if edital.data_encerramento else None,
                edital.conteudo_html, edital.url_pdf, edital.pdf_bytes,
                edital.hash_conteudo, datetime.now().isoformat()
            ))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Hash duplicado — edital ja existe

    def listar_nao_processados(self) -> list[dict]:
        cursor = self.conn.execute(
            "SELECT * FROM editais_brutos WHERE processado = 0"
        )
        cols = [d[0] for d in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]

    def marcar_processado(self, edital_id: int):
        self.conn.execute(
            "UPDATE editais_brutos SET processado = 1 WHERE id = ?", (edital_id,)
        )
        self.conn.commit()
