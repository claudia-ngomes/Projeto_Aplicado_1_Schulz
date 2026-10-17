# ==============================================================================
# SCRIPT PYTHON PARA CONECTAR AO SQLITE E EXECUTAR O ARQUIVO 03_banco.sql
# PROJETO APLICADO I - SCHULZ S.A. - GRUPO 23
# ==============================================================================
import sqlite3
import os

NOME_BANCO = "schulz_calibracao.db"
ARQUIVO_SQL = "03_banco.sql"

conexao = None
try:
    conexao = sqlite3.connect(NOME_BANCO)
    cursor = conexao.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    with open(ARQUIVO_SQL, "r", encoding="utf-8") as f:
        script_sql = f.read()

    cursor.executescript(script_sql)
    conexao.commit()

    print("=" * 60)
    print(f"SUCESSO: Banco de dados '{NOME_BANCO}' gerado com sucesso!")
    print("As tabelas 'tecnico', 'equipamento' e 'medicao' foram criadas.")
    print("=" * 60)

    # Verificação rápida: lista as tabelas criadas e a contagem de linhas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tabelas = [t[0] for t in cursor.fetchall() if not t[0].startswith("sqlite_")]
    print(f"Tabelas encontradas no banco: {tabelas}")
    for tabela in tabelas:
        cursor.execute(f"SELECT COUNT(*) FROM {tabela};")
        total = cursor.fetchone()[0]
        print(f"  - {tabela}: {total} registro(s)")

except Exception as e:
    print(f"ERRO ao executar o script DDL: {e}")
finally:
    if conexao:
        conexao.close()
