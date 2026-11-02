# ==============================================================================
# PROJETO APLICADO I - SCHULZ S.A. - GRUPO 23
# ENTREGA 03 (MVP - PARTE 1): SCRIPT PRINCIPAL DE DEMONSTRAÇÃO
# ==============================================================================

# ---------- PARTE 1: importar as classes do grupo ----------
import os
from importlib import import_module

classes = import_module("04_classes")   # o nome do arquivo começa com número
Tecnico = classes.Tecnico
Equipamento = classes.Equipamento
Medicao = classes.Medicao
BancoDados = classes.BancoDados
ErroBanco = classes.ErroBanco

# ---------- PARTE 2: dados de teste  ----------
# Dados do técnico: nome, matrícula, setor
dados_tecnico = ("Jose Alcides Rosa Junior", "16858-0", "Metrologia")

# Dados do equipamento: código TAG, descrição, fabricante, modelo
dados_equipamento = ("703.1208", "Dispositivo de controle", "Não consta", "Não se aplica")
# Medições: parâmetro, valor nominal, tolerância mínima, tolerância máxima, valor obtido
resultados = [
    ('PLANICIDADE_REF',    0.000,  0.000, 0.050,  0.002),
    ('ENTRE CENTROS_REF',  0.000,  0.000, 0.040,  0.027),
    ('62P_DIÂMETRO 1',     6.075, -0.010, 0.010,  6.079),
    ('62P_POSIÇÃO 1',      0.000,  0.000, 0.100,  0.430),
    ('62P_DIÂMETRO 2',     6.075, -0.010, 0.010,  6.078),
    ('62P_POSIÇÃO 2',      0.000,  0.000, 0.100,  0.245),
    ('13P_DIÂMETRO 1',    16.964, -0.010, 0.010, 16.968),
    ('13P_POSIÇÃO 1',      0.000,  0.000, 0.100,  0.959),
    ('13P_DIÂMETRO 2',    16.964, -0.010, 0.010, 16.970),
    ('13P_POSIÇÃO 2',      0.000,  0.000, 0.100,  0.236),
    ('106P_DIÂMETRO 1',    6.345, -0.010, 0.010,  6.346),
    ('106P_POSIÇÃO 1',     0.000,  0.000, 0.100,  0.132),
    ('106P_DIÂMETRO 2',    6.345, -0.010, 0.010,  6.349),
    ('106P_POSIÇÃO 2',     0.000,  0.000, 0.100,  0.868),
]

# ---------- PARTE 3: criar o banco e gravar técnico e equipamento ----------
if os.path.exists("schulz_mvp.db"):
    os.remove("schulz_mvp.db")

banco = BancoDados("schulz_mvp.db")

nome, matricula, setor = dados_tecnico
tecnico = Tecnico(matricula, nome, setor)
id_tecnico = banco.inserir_tecnico(tecnico)

codigo_tag, descricao, fabricante, modelo = dados_equipamento
equipamento = Equipamento(codigo_tag, descricao, fabricante, modelo)
id_equipamento = banco.inserir_equipamento(equipamento)

print("Técnico gravado com id", id_tecnico)
print("Equipamento gravado com id", id_equipamento)

# Grava cada medição no banco (o status é calculado pela classe Medicao)
for parametro, nominal, tol_min, tol_max, obtido in resultados:
    medicao = Medicao(id_tecnico, id_equipamento, parametro,
                      nominal, tol_min, tol_max, obtido)
    banco.registrar_medicao(medicao, "2026-08-26")

print("Medições gravadas:", len(banco.listar_medicoes()))

# ---------- PARTE 4: relatório vindo do banco (consulta com JOIN) ----------
linhas = banco.relatorio_calibracoes("703.1208")

print("=" * 78)
print("RELATÓRIO DE CALIBRAÇÃO")
print("=" * 78)
print("Técnico:", linhas[0]["tecnico"])
print("Equipamento:", linhas[0]["codigo_tag"], "-", linhas[0]["equipamento"])
print("-" * 78)
print(f"{'Parâmetro':<20}{'Lim.Inf':>9}{'Lim.Sup':>9}{'Obtido':>9}  Status")
print("-" * 78)

aprovados = 0
reprovados = 0
for linha in linhas:
    limite_inf = linha["valor_nominal"] + linha["tolerancia_min"]
    limite_sup = linha["valor_nominal"] + linha["tolerancia_max"]
    print(f"{linha['parametro_medido']:<20}{limite_inf:>9.3f}{limite_sup:>9.3f}"
          f"{linha['valor_obtido']:>9.3f}  {linha['status']}")
    if linha["status"] == "APROVADO":
        aprovados += 1
    else:
        reprovados += 1

print("-" * 78)
print(f"Resumo: {aprovados} aprovado(s) / {reprovados} reprovado(s)")

# ---------- PARTE 5: atualização (UPDATE) ----------
print()
print("ATUALIZAÇÃO")
antes = banco.buscar_medicao(4)
print("Antes: ", antes["parametro_medido"], antes["valor_obtido"], antes["status_resultado"])
banco.atualizar_valor_obtido(4, 0.080)   # remedição dentro da tolerância
depois = banco.buscar_medicao(4)
print("Depois:", depois["parametro_medido"], depois["valor_obtido"], depois["status_resultado"])

# ---------- PARTE 6: tratamento de erros ----------
print()
print("TRATAMENTO DE ERROS")
try:
    banco.inserir_tecnico(Tecnico("16858-0", "Outro Nome", "Metrologia"))
except ErroBanco as erro:
    print("Matrícula duplicada ->", erro)

try:
    Tecnico("", "", "")
except ValueError as erro:
    print("Dados vazios ->", erro)