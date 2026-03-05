"""
Exporta editais_estruturados do banco local para data/seed.json.
Esse JSON eh carregado automaticamente no deploy se o banco estiver vazio.
"""
import sqlite3
import json
import os

db = sqlite3.connect("culturacesso.db")
db.row_factory = sqlite3.Row

# Verifica editais estruturados
rows = db.execute("SELECT * FROM editais_estruturados").fetchall()
print(f"Editais estruturados encontrados: {len(rows)}")

if len(rows) == 0:
    # Tenta exportar editais brutos para pelo menos ter algo
    brutos = db.execute("SELECT * FROM editais_brutos").fetchall()
    print(f"Editais brutos encontrados: {brutos and len(brutos) or 0}")
    if brutos:
        print("\nOs editais brutos existem mas nao foram processados ainda.")
        print("Rode primeiro: python reset_e_processar.py")
        print("Depois rode: python export_seed.py")
    else:
        print("Banco vazio. Rode o scraper primeiro: python -m scraper.main")
    db.close()
    exit(1)

# Exporta
seed_data = []
for row in rows:
    seed_data.append({
        "id_bruto": row["id_bruto"],
        "dados_json": row["dados_json"],
        "data_processamento": row["data_processamento"],
        "confianca_extracao": row["confianca_extracao"],
    })

os.makedirs("data", exist_ok=True)
with open("data/seed.json", "w", encoding="utf-8") as f:
    json.dump(seed_data, f, ensure_ascii=False, indent=2)

print(f"\nExportado {len(seed_data)} editais para data/seed.json")
db.close()
