import io
from scraper.storage import ScraperStorage
from .extractor import extrair_atributos
from datetime import datetime
import sqlite3

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False
    print("[WARN] pdfplumber nao instalado. PDFs nao serao extraidos.")


def extrair_texto_pdf(pdf_bytes: bytes) -> str:
    """Extrai texto de um PDF usando pdfplumber."""
    if not HAS_PDFPLUMBER or not pdf_bytes:
        return ""
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            textos = []
            for page in pdf.pages:
                texto = page.extract_text()
                if texto:
                    textos.append(texto)
            return "\n\n".join(textos)
    except Exception as e:
        print(f"  [WARN] Falha ao extrair PDF: {e}")
        return ""


def processar_pendentes():
    scraper_storage = ScraperStorage()
    conn = sqlite3.connect("culturacesso.db")

    # Tabela de editais estruturados
    conn.execute("""
        CREATE TABLE IF NOT EXISTS editais_estruturados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_bruto INTEGER UNIQUE,
            dados_json TEXT NOT NULL,
            data_processamento TEXT NOT NULL,
            confianca_extracao REAL
        )
    """)
    conn.commit()

    pendentes = scraper_storage.listar_nao_processados()
    print(f"{len(pendentes)} editais aguardando processamento.")

    ok_count = 0
    fail_count = 0
    skip_count = 0

    for i, edital_bruto in enumerate(pendentes, 1):
        conteudo_html = edital_bruto.get("conteudo_html") or ""
        pdf_bytes = edital_bruto.get("pdf_bytes")

        # Extrai texto do PDF se disponivel
        texto_pdf = ""
        if pdf_bytes:
            texto_pdf = extrair_texto_pdf(pdf_bytes)
            if texto_pdf:
                print(f"  [PDF] Extraido {len(texto_pdf)} chars do PDF")

        # Combina HTML + texto do PDF para conteudo maximo
        conteudo = conteudo_html
        if texto_pdf:
            conteudo = f"{conteudo_html}\n\n--- CONTEUDO EXTRAIDO DO PDF DO EDITAL ---\n\n{texto_pdf}"

        if not conteudo or len(conteudo.strip()) < 20:
            print(f"[SKIP] Edital {edital_bruto['id']} sem conteudo (HTML nem PDF).")
            skip_count += 1
            continue

        print(f"\n[{i}/{len(pendentes)}] Processando: {edital_bruto['titulo'][:60]}...")
        print(f"  Conteudo: {len(conteudo_html)} chars HTML + {len(texto_pdf)} chars PDF = {len(conteudo)} total")

        try:
            estruturado = extrair_atributos(
                conteudo=conteudo,
                id_bruto=edital_bruto["id"],
                url_origem=edital_bruto["url_origem"] or ""
            )

            if estruturado:
                conn.execute("""
                    INSERT OR REPLACE INTO editais_estruturados
                    (id_bruto, dados_json, data_processamento, confianca_extracao)
                    VALUES (?, ?, ?, ?)
                """, (
                    estruturado.id_bruto,
                    estruturado.model_dump_json(),
                    datetime.now().isoformat(),
                    estruturado.confianca_extracao
                ))
                conn.commit()
                scraper_storage.marcar_processado(edital_bruto["id"])
                print(f"  [OK] {estruturado.titulo} (confianca: {estruturado.confianca_extracao:.0%})")
                ok_count += 1
            else:
                print(f"  [FALHA] Edital {edital_bruto['id']}: {edital_bruto['titulo'][:60]}")
                fail_count += 1
        except Exception as e:
            print(f"  [ERRO INESPERADO] Edital {edital_bruto['id']}: {e}")
            fail_count += 1
            continue

    conn.close()
    print(f"\n=== Resumo: {ok_count} processados | {fail_count} falhas | {skip_count} ignorados ===")


if __name__ == "__main__":
    processar_pendentes()
