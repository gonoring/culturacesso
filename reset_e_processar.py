"""
Script auxiliar: reseta editais que foram marcados como processados
(na tentativa anterior com erro) e roda o processador novamente.
"""
import sqlite3

db = sqlite3.connect("culturacesso.db")

# Verifica estado atual
antes = db.execute("SELECT processado, COUNT(*) FROM editais_brutos GROUP BY processado").fetchall()
print(f"Estado atual: {antes}")

# Verifica quantos editais estruturados existem
estruturados = db.execute("SELECT COUNT(*) FROM editais_estruturados").fetchone()
print(f"Editais estruturados no banco: {estruturados[0]}")

# Se tem editais marcados como processados mas sem entrada em editais_estruturados,
# reseta eles
resetados = db.execute("""
    UPDATE editais_brutos SET processado = 0
    WHERE processado = 1
    AND id NOT IN (SELECT id_bruto FROM editais_estruturados)
""").rowcount
db.commit()
print(f"Editais resetados (marcados sem resultado): {resetados}")

depois = db.execute("SELECT processado, COUNT(*) FROM editais_brutos GROUP BY processado").fetchall()
print(f"Estado apos reset: {depois}")

db.close()

# Agora roda o processador
print("\n" + "="*60)
print("Iniciando processamento...")
print("="*60 + "\n")

from processor.main import processar_pendentes
processar_pendentes()
