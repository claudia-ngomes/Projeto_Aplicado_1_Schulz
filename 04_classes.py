"""
AV 03 - MVP Parte 1 | Schulz S.A.
Arquivo: 04_classes.py

Implementa as classes de domínio e a camada de persistência SQLite.
O modelo de dados segue a Entrega 02 (tabelas tecnico, equipamento e medicao,
com tolerância mínima e máxima em cada medição).
Bibliotecas utilizadas: somente recursos nativos do Python.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime


class ErroBanco(Exception):
    """Erro próprio do sistema para falhas de acesso ao banco SQLite."""


def _texto_obrigatorio(valor, campo):
    valor = "" if valor is None else str(valor).strip()
    if not valor:
        raise ValueError(f"O campo {campo} é obrigatório.")
    return valor


class Tecnico:
    """Representa o profissional responsável pela calibração."""

    def __init__(self, matricula, nome, setor, email="Não informado"):
        self.matricula = _texto_obrigatorio(matricula, "matrícula")
        self.nome = _texto_obrigatorio(nome, "nome")
        self.setor = _texto_obrigatorio(setor, "setor")
        self.email = _texto_obrigatorio(email, "email")


class Equipamento:
    """Representa um instrumento de medição."""

    def __init__(self, codigo_tag, descricao, fabricante, modelo):
        self.codigo_tag = _texto_obrigatorio(codigo_tag, "código TAG")
        self.descricao = _texto_obrigatorio(descricao, "descrição")
        self.fabricante = _texto_obrigatorio(fabricante, "fabricante")
        self.modelo = _texto_obrigatorio(modelo, "modelo")


class Medicao:
    """Encapsula uma calibração (uma característica medida) e determina seu resultado.

    Cada medição traz a sua própria tolerância, como no certificado da Schulz:
    limite inferior = valor_nominal + tolerancia_min
    limite superior = valor_nominal + tolerancia_max
    """

    def __init__(self, id_tecnico, id_equipamento, parametro_medido,
                 valor_nominal, tolerancia_min, tolerancia_max, valor_obtido):
        self.id_tecnico = int(id_tecnico)
        self.id_equipamento = int(id_equipamento)
        self.parametro_medido = _texto_obrigatorio(parametro_medido, "parâmetro medido")
        self.valor_nominal = float(valor_nominal)
        self.tolerancia_min = float(tolerancia_min)
        self.tolerancia_max = float(tolerancia_max)
        self.valor_obtido = float(valor_obtido)

        if self.tolerancia_min > self.tolerancia_max:
            raise ValueError("A tolerância mínima não pode ser maior que a máxima.")

    def limite_inferior(self):
        return self.valor_nominal + self.tolerancia_min

    def limite_superior(self):
        return self.valor_nominal + self.tolerancia_max

    def calcular_desvio(self):
        """Retorna a diferença entre o valor obtido e o valor nominal."""
        return self.valor_obtido - self.valor_nominal

    def validar_status(self):
        """
        Aprova quando o valor obtido está entre o limite inferior e o superior
        (inclusive). Caso contrário, reprova.
        O round evita erro de ponto flutuante (ex.: 6.075 + 0.010).
        """
        obtido = round(self.valor_obtido, 6)
        if round(self.limite_inferior(), 6) <= obtido <= round(self.limite_superior(), 6):
            return "APROVADO"
        return "REPROVADO"


class BancoDados:
    """Gerencia a conexão SQLite, a criação das tabelas e as operações CRUD."""

    def __init__(self, caminho="schulz_mvp.db"):
        self.caminho = caminho
        self._criar_tabelas()

    @contextmanager
    def conectar(self):
        """Abre a conexão, confirma (commit) se der certo, desfaz (rollback) se falhar
        e sempre fecha. Os erros do sqlite3 viram ErroBanco."""
        try:
            conexao = sqlite3.connect(self.caminho)
            conexao.row_factory = sqlite3.Row
            conexao.execute("PRAGMA foreign_keys = ON")
        except sqlite3.Error as e:
            raise ErroBanco(f"Não foi possível conectar ao banco: {e}") from e
        try:
            yield conexao
            conexao.commit()
        except sqlite3.IntegrityError as e:
            conexao.rollback()
            raise ErroBanco(f"Violação de integridade: {e}") from e
        except sqlite3.Error as e:
            conexao.rollback()
            raise ErroBanco(f"Erro SQL: {e}") from e
        finally:
            conexao.close()

    def _criar_tabelas(self):
        comandos = [
            """
            CREATE TABLE IF NOT EXISTS tecnico (
                id_tecnico INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_tecnico TEXT NOT NULL,
                matricula TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL,
                setor TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS equipamento (
                id_equipamento INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_tag TEXT NOT NULL UNIQUE,
                nome_equipamento TEXT NOT NULL,
                fabricante TEXT NOT NULL,
                modelo TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS medicao (
                id_medicao INTEGER PRIMARY KEY AUTOINCREMENT,
                id_equipamento INTEGER NOT NULL,
                id_tecnico INTEGER NOT NULL,
                parametro_medido TEXT NOT NULL,
                valor_nominal REAL NOT NULL,
                tolerancia_min REAL NOT NULL,
                tolerancia_max REAL NOT NULL,
                valor_obtido REAL NOT NULL,
                status_resultado TEXT NOT NULL
                    CHECK (status_resultado IN ('APROVADO', 'REPROVADO')),
                data_medicao DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_equipamento) REFERENCES equipamento (id_equipamento)
                    ON DELETE RESTRICT ON UPDATE CASCADE,
                FOREIGN KEY (id_tecnico) REFERENCES tecnico (id_tecnico)
                    ON DELETE RESTRICT ON UPDATE CASCADE
            )
            """
        ]
        with self.conectar() as conexao:
            for comando in comandos:
                conexao.execute(comando)

    # ------------------------- TECNICO (CRUD) -------------------------

    def inserir_tecnico(self, tecnico):
        with self.conectar() as conexao:
            cursor = conexao.execute(
                "INSERT INTO tecnico (nome_tecnico, matricula, email, setor) "
                "VALUES (?, ?, ?, ?)",
                (tecnico.nome, tecnico.matricula, tecnico.email, tecnico.setor)
            )
            return cursor.lastrowid

    def buscar_tecnico_por_matricula(self, matricula):
        with self.conectar() as conexao:
            return conexao.execute(
                "SELECT * FROM tecnico WHERE matricula = ?", (matricula,)
            ).fetchone()

    def buscar_tecnico_por_id(self, id_tecnico):
        with self.conectar() as conexao:
            return conexao.execute(
                "SELECT * FROM tecnico WHERE id_tecnico = ?", (id_tecnico,)
            ).fetchone()

    def listar_tecnicos(self):
        with self.conectar() as conexao:
            return conexao.execute(
                "SELECT * FROM tecnico ORDER BY nome_tecnico"
            ).fetchall()

    def atualizar_setor_tecnico(self, id_tecnico, novo_setor):
        novo_setor = _texto_obrigatorio(novo_setor, "setor")
        with self.conectar() as conexao:
            cursor = conexao.execute(
                "UPDATE tecnico SET setor = ? WHERE id_tecnico = ?",
                (novo_setor, id_tecnico)
            )
            return cursor.rowcount

    # ----------------------- EQUIPAMENTO (CRUD) -----------------------

    def inserir_equipamento(self, equipamento):
        with self.conectar() as conexao:
            cursor = conexao.execute(
                "INSERT INTO equipamento (codigo_tag, nome_equipamento, fabricante, modelo) "
                "VALUES (?, ?, ?, ?)",
                (equipamento.codigo_tag, equipamento.descricao,
                 equipamento.fabricante, equipamento.modelo)
            )
            return cursor.lastrowid

    def buscar_equipamento_por_tag(self, codigo_tag):
        with self.conectar() as conexao:
            return conexao.execute(
                "SELECT * FROM equipamento WHERE codigo_tag = ?", (codigo_tag,)
            ).fetchone()

    def buscar_equipamento_por_id(self, id_equipamento):
        with self.conectar() as conexao:
            return conexao.execute(
                "SELECT * FROM equipamento WHERE id_equipamento = ?", (id_equipamento,)
            ).fetchone()

    def listar_equipamentos(self):
        with self.conectar() as conexao:
            return conexao.execute(
                "SELECT * FROM equipamento ORDER BY codigo_tag"
            ).fetchall()

    def atualizar_modelo_equipamento(self, id_equipamento, novo_modelo):
        novo_modelo = _texto_obrigatorio(novo_modelo, "modelo")
        with self.conectar() as conexao:
            cursor = conexao.execute(
                "UPDATE equipamento SET modelo = ? WHERE id_equipamento = ?",
                (novo_modelo, id_equipamento)
            )
            return cursor.rowcount

    # ------------------------- MEDICAO (CRUD) -------------------------

    def registrar_medicao(self, medicao, data_medicao=None):
        """Insere a medição. O status é sempre calculado pela classe Medicao."""
        if self.buscar_equipamento_por_id(medicao.id_equipamento) is None:
            raise ValueError("Equipamento não encontrado.")
        if self.buscar_tecnico_por_id(medicao.id_tecnico) is None:
            raise ValueError("Técnico não encontrado.")

        status = medicao.validar_status()
        if data_medicao is None:
            data_medicao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with self.conectar() as conexao:
            cursor = conexao.execute(
                """INSERT INTO medicao
                   (id_equipamento, id_tecnico, parametro_medido, valor_nominal,
                    tolerancia_min, tolerancia_max, valor_obtido,
                    status_resultado, data_medicao)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (medicao.id_equipamento, medicao.id_tecnico, medicao.parametro_medido,
                 medicao.valor_nominal, medicao.tolerancia_min, medicao.tolerancia_max,
                 medicao.valor_obtido, status, data_medicao)
            )
            return cursor.lastrowid

    def buscar_medicao(self, id_medicao):
        with self.conectar() as conexao:
            return conexao.execute(
                "SELECT * FROM medicao WHERE id_medicao = ?", (id_medicao,)
            ).fetchone()

    def listar_medicoes(self):
        with self.conectar() as conexao:
            return conexao.execute(
                "SELECT * FROM medicao ORDER BY id_medicao"
            ).fetchall()

    def atualizar_valor_obtido(self, id_medicao, novo_valor):
        """Corrige o valor medido e recalcula o status pela regra de negócio."""
        atual = self.buscar_medicao(id_medicao)
        if atual is None:
            raise ValueError("Medição não encontrada.")
        medicao = Medicao(atual["id_tecnico"], atual["id_equipamento"],
                          atual["parametro_medido"], atual["valor_nominal"],
                          atual["tolerancia_min"], atual["tolerancia_max"], novo_valor)
        with self.conectar() as conexao:
            cursor = conexao.execute(
                "UPDATE medicao SET valor_obtido = ?, status_resultado = ? "
                "WHERE id_medicao = ?",
                (medicao.valor_obtido, medicao.validar_status(), id_medicao)
            )
            return cursor.rowcount

    def relatorio_calibracoes(self, codigo_tag=None):
        """Consulta relacional com JOIN entre as três tabelas."""
        consulta = """
            SELECT
                m.id_medicao,
                t.nome_tecnico AS tecnico,
                t.matricula,
                e.codigo_tag,
                e.nome_equipamento AS equipamento,
                m.parametro_medido,
                m.valor_nominal,
                m.tolerancia_min,
                m.tolerancia_max,
                m.valor_obtido,
                m.status_resultado AS status,
                m.data_medicao
            FROM medicao m
            INNER JOIN tecnico t ON t.id_tecnico = m.id_tecnico
            INNER JOIN equipamento e ON e.id_equipamento = m.id_equipamento
        """
        parametros = ()
        if codigo_tag is not None:
            consulta += " WHERE e.codigo_tag = ?"
            parametros = (codigo_tag,)
        consulta += " ORDER BY m.id_medicao"
        with self.conectar() as conexao:
            return conexao.execute(consulta, parametros).fetchall()
