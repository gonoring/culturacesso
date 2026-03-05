"""
Script completo: reseta editais processados com dados pobres,
re-processa usando PDF + HTML melhorado, e exporta novo seed.json.

Uso:
  python reset_e_processar.py           # re-processa todos
  python reset_e_processar.py --scrape  # re-faz scraping antes
"""
import sys
import sqlite3
import json
from pathlib import Path


def diagnostico(db):
    """Mostra estado atual do banco."""
    brutos = db.execute("SELECT COUNT(*) FROM editais_brutos").fetchone()[0]
    processados = db.execute("SELECT COUNT(*) FROM editais_brutos WHERE processado = 1").fetchone()[0]
    estruturados = db.execute("SELECT COUNT(*) FROM editais_estruturados").fetchone()[0]

    # Verifica quantos tem PDF
    com_pdf = db.execute("SELECT COUNT(*) FROM editais_brutos WHERE pdf_bytes IS NOT NULL").fetchone()[0]

    # Verifica qualidade dos editais estruturados
    if estruturados > 0:
        sem_valor = db.execute("""
            SELECT COUNT(*) FROM editais_estruturados
            WHERE json_extract(dados_json, '$.valor_maximo') IS NULL
        """).fetchone()[0]
        baixa_confianca = db.execute("""
            SELECT COUNT(*) FROM editais_estruturados WHERE confianca_extracao < 0.5
        """).fetchone()[0]
    else:
        sem_valor = 0
        baixa_confianca = 0

    print(f"=== DIAGNOSTICO ===")
    print(f"  Editais brutos:        {brutos}")
    print(f"  Ja processados:        {processados}")
    print(f"  Com PDF armazenado:    {com_pdf}")
    print(f"  Editais estruturados:  {estruturados}")
    print(f"  Sem valor (null):      {sem_valor}")
    print(f"  Baixa confianca (<50%): {baixa_confianca}")
    print()


def resetar_para_reprocessamento(db):
    """Reseta todos os editais para reprocessamento."""
    # Remove editais estruturados existentes (vamos recriar todos)
    db.execute("DELETE FROM editais_estruturados")
    # Reseta flag de processado
    resetados = db.execute("UPDATE editais_brutos SET processado = 0").rowcount
    db.commit()
    print(f"Resetados {resetados} editais para reprocessamento.")
    return resetados


def exportar_seed(db):
    """Exporta editais estruturados para data/seed.json."""
    rows = db.execute(
        "SELECT id_bruto, dados_json, confianca_extracao FROM editais_estruturados"
    ).fetchall()

    seed_data = []
    for row in rows:
        seed_data.append({
            "id_bruto": row[0],
            "dados_json": row[1],
            "confianca_extracao": row[2],
        })

    seed_path = Path("data/seed.json")
    seed_path.parent.mkdir(exist_ok=True)
    seed_path.write_text(json.dumps(seed_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nExportados {len(seed_data)} editais para {seed_path}")

    # Mostra resumo de qualidade
    com_valor = sum(1 for s in seed_data if '"valor_maximo": null' not in s["dados_json"]
                    or '"valor_minimo": null' not in s["dados_json"])
    alta_conf = sum(1 for s in seed_data if (s["confianca_extracao"] or 0) >= 0.5)
    print(f"  Com valores preenchidos: {com_valor}/{len(seed_data)}")
    print(f"  Confianca >= 50%: {alta_conf}/{len(seed_data)}")


def main():
    do_scrape = "--scrape" in sys.argv

    db = sqlite3.connect("culturacesso.db")

    print("\n" + "=" * 60)
    print("CULTURACESSO — Re-processamento Completo")
    print("=" * 60 + "\n")

    diagnostico(db)

    # Passo 1: Re-scraping (opcional)
    if do_scrape:
        print("\n--- PASSO 1: Re-scraping ---\n")
        db.close()

        import asyncio
        from scraper.main import executar_scraping
        asyncio.run(executar_scraping())

        db = sqlite3.connect("culturacesso.db")
        print("\nApos scraping:")
        diagnostico(db)

    # Passo 2: Resetar processamento
    print("\n--- PASSO 2: Resetar para reprocessamento ---\n")
    resetar_para_reprocessamento(db)
    db.close()

    # Passo 3: Reprocessar (agora com suporte a PDF)
    print("\n--- PASSO 3: Processando editais (HTML + PDF) ---\n")
    from processor.main import processar_pendentes
    processar_pendentes()

    # Passo 4: Exportar seed
    print("\n--- PASSO 4: Exportando seed.json ---\n")
    db = sqlite3.connect("culturacesso.db")
    exportar_seed(db)
    diagnostico(db)
    db.close()

    print("\n" + "=" * 60)
    print("Concluido! Proximo passo: git add data/seed.json && git push")
    print("=" * 60)


if __name__ == "__main__":
    main()
