# 06_mvp_parte1.md — Documentação Técnica do MVP (Parte 1)

**Unidade Curricular:** Projeto Aplicado I
**Empresa parceira:** Schulz S.A. — Laboratório de Metrologia
**Entrega:** AV 03 (Tema 03) — Construção do MVP, Parte 1
**Grupo:** 23
**Linguagem:** Python 3, usando somente a biblioteca padrão (`sqlite3`, `contextlib`, `datetime`)

---

## 1. Objetivo

Transformar o modelo relacional da Entrega 02 (tabelas `tecnico`, `equipamento` e `medicao`) em código orientado a objetos. O MVP cadastra técnicos e equipamentos, registra medições de calibração, **valida automaticamente se cada medição está APROVADA ou REPROVADA** e emite o relatório de calibração no terminal por meio de uma consulta com JOIN.

| Arquivo | Função |
| :--- | :--- |
| `04_classes.py` | Classes de domínio (`Tecnico`, `Equipamento`, `Medicao`), classe de persistência (`BancoDados`) e exceção `ErroBanco`. |
| `05_main.py` | Script de demonstração: insere dados reais, grava as medições, emite o relatório com JOIN, faz um UPDATE e testa erros. |
| `06_mvp_parte1.md` | Este documento. |

**Como executar** (na pasta do projeto): `python 05_main.py`. O script apaga e recria o arquivo `schulz_mvp.db` a cada execução, então o resultado é sempre o mesmo.

---

## 2. Padrões de POO utilizados

- **Classes de domínio com validação no construtor:** `Tecnico`, `Equipamento` e `Medicao` não aceitam dados inválidos. Texto vazio gera `ValueError`, e uma medição com tolerância mínima maior que a máxima também. A função auxiliar `_texto_obrigatorio` (nome iniciado por `_`, de uso interno) evita repetir a mesma verificação em cada classe.
- **Encapsulamento da persistência:** só a classe `BancoDados` conhece o SQLite. O restante do sistema chama métodos como `inserir_tecnico()` e `registrar_medicao()` e não escreve SQL. O método `_criar_tabelas()` é interno, pelo mesmo padrão de nomenclatura.
- **Separação de responsabilidades:** as classes de domínio guardam os dados e as regras de negócio; `BancoDados` cuida do armazenamento; `05_main.py` apenas orquestra o fluxo.
- **Regra de negócio dentro da classe certa:** o status (APROVADO/REPROVADO) **nunca é digitado**. Quem decide é `Medicao.validar_status()`, e `BancoDados.registrar_medicao()` grava o que ela devolve.
- **Gerenciador de contexto:** o método `conectar()` usa `@contextmanager` e é chamado com `with`. Ele faz *commit* se tudo der certo, *rollback* se falhar e **sempre fecha a conexão**.
- **Exceção própria (`ErroBanco`):** os erros do `sqlite3` são traduzidos para uma exceção do sistema, com mensagem clara.
- **Consultas parametrizadas:** todo SQL usa `?` no lugar de concatenar texto, o que evita SQL Injection.

> Observação: os atributos das classes de domínio são públicos (`tecnico.nome`, `medicao.valor_obtido`), como é comum em Python. A proteção dos dados é feita pela validação no construtor.

### Regra de validação (`Medicao`)

```
limite_inferior = valor_nominal + tolerancia_min
limite_superior = valor_nominal + tolerancia_max
APROVADO   se  limite_inferior <= valor_obtido <= limite_superior
REPROVADO  caso contrário
```

Cada medição traz a sua **própria tolerância**, como no certificado da Schulz. Exemplo: `62P_DIÂMETRO 1` tem nominal 6,075 e tolerâncias -0,010 e +0,010, ou seja, faixa de 6,065 a 6,085. O valor obtido 6,079 está dentro, então o resultado é **APROVADO**. Já `62P_POSIÇÃO 1` tem faixa de 0,000 a 0,100 e valor obtido 0,430, então é **REPROVADO**.

Os valores são arredondados em 6 casas antes da comparação, para evitar erro de ponto flutuante (por exemplo, 6,075 + 0,010).

> O certificado da Schulz não informa o parecer de aprovação. Essa regra foi definida pelo grupo, a mesma da Entrega 02.

---

## 3. Diagrama textual das classes (UML)

```
+------------------------+        +---------------------------+
|        Tecnico         |        |        Equipamento        |
+------------------------+        +---------------------------+
| + matricula : str      |        | + codigo_tag : str        |
| + nome : str           |        | + descricao : str         |
| + setor : str          |        | + fabricante : str        |
| + email : str          |        | + modelo : str            |
+------------------------+        +---------------------------+
           | 1                                  | 1
           |                                    |
           | realiza                    recebe  |
           | N                                  | N
           v                                    v
   +--------------------------------------------------+
   |                      Medicao                     |
   +--------------------------------------------------+
   | + id_tecnico : int          (FK -> tecnico)      |
   | + id_equipamento : int      (FK -> equipamento)  |
   | + parametro_medido : str                         |
   | + valor_nominal : float                          |
   | + tolerancia_min : float                         |
   | + tolerancia_max : float                         |
   | + valor_obtido : float                           |
   +--------------------------------------------------+
   | + limite_inferior() : float                      |
   | + limite_superior() : float                      |
   | + calcular_desvio() : float                      |
   | + validar_status() : str   "APROVADO"/"REPROVADO"|
   +--------------------------------------------------+

   +--------------------------------------------------+
   |                    BancoDados                    |
   +--------------------------------------------------+
   | + caminho : str                                  |
   +--------------------------------------------------+
   | + conectar()            (gerenciador de contexto)|
   | - _criar_tabelas()                               |
   | + inserir_tecnico(t)                             |
   | + buscar_tecnico_por_matricula(matricula)        |
   | + buscar_tecnico_por_id(id)                      |
   | + listar_tecnicos()                              |
   | + atualizar_setor_tecnico(id, setor)             |
   | + inserir_equipamento(e)                         |
   | + buscar_equipamento_por_tag(tag)                |
   | + buscar_equipamento_por_id(id)                  |
   | + listar_equipamentos()                          |
   | + atualizar_modelo_equipamento(id, modelo)       |
   | + registrar_medicao(m, data)                     |
   | + buscar_medicao(id)  /  listar_medicoes()       |
   | + atualizar_valor_obtido(id, valor)              |
   | + relatorio_calibracoes(tag)   <- JOIN           |
   +--------------------------------------------------+
        usa (dependência) -> Tecnico, Equipamento, Medicao

   +------------------------------+
   |   ErroBanco (Exception)      |   levantada por BancoDados
   +------------------------------+
```

**Correspondência com o banco (Entrega 02):** `Tecnico.nome` ↔ coluna `nome_tecnico`; `Equipamento.descricao` ↔ coluna `nome_equipamento`. Os demais atributos têm o mesmo nome da coluna. A coluna `status_resultado` da tabela `medicao` recebe o valor calculado por `validar_status()`.

---

## 4. Operações CRUD implementadas

| Operação | Métodos de `BancoDados` | SQL |
| :--- | :--- | :--- |
| Create | `inserir_tecnico`, `inserir_equipamento`, `registrar_medicao` | `INSERT` |
| Read | `buscar_tecnico_por_matricula`, `buscar_tecnico_por_id`, `listar_tecnicos`, `buscar_equipamento_por_tag`, `buscar_equipamento_por_id`, `listar_equipamentos`, `buscar_medicao`, `listar_medicoes` | `SELECT ... WHERE` / `ORDER BY` |
| Read (relatório) | `relatorio_calibracoes` | `SELECT ... INNER JOIN` das 3 tabelas |
| Update | `atualizar_setor_tecnico`, `atualizar_modelo_equipamento`, `atualizar_valor_obtido` | `UPDATE` |

O `DELETE` não foi implementado de propósito: o roteiro pede INSERT, SELECT e UPDATE, e as chaves estrangeiras usam `ON DELETE RESTRICT`, o que preserva o histórico de calibrações.

O método `atualizar_valor_obtido` corrige o valor medido e **recalcula o status** pela mesma regra de negócio. Não existe método para alterar o status à mão, para que o parecer nunca contradiga os números.

---

## 5. Tratamento de erros SQL

Toda operação com o banco passa por `conectar()`, que faz *commit* em caso de sucesso, *rollback* em caso de falha e fecha a conexão no final. Os erros do `sqlite3` são convertidos em `ErroBanco`:

| Situação | Erro capturado | Resultado |
| :--- | :--- | :--- |
| Matrícula ou código TAG já cadastrado | `sqlite3.IntegrityError` (UNIQUE) | `ErroBanco`: "Violação de integridade: UNIQUE constraint failed: tecnico.matricula" |
| Medição para técnico/equipamento inexistente | Verificação em `registrar_medicao` e chave estrangeira do banco | `ValueError` ("Equipamento não encontrado.") ou `ErroBanco` |
| Qualquer outro erro do SQLite | `sqlite3.Error` | `ErroBanco`: "Erro SQL: ..." |
| Dado obrigatório vazio | Validação da classe | `ValueError`: "O campo matrícula é obrigatório." |
| Tolerância mínima maior que a máxima | Validação de `Medicao` | `ValueError` |

A integridade referencial depende de `PRAGMA foreign_keys = ON`, executado em toda conexão.

---

## 6. Validação do fluxo funcional

O `05_main.py` executa o fluxo abaixo, e o resultado foi conferido no terminal.

1. **Importação e preparação:** carrega as classes do `04_classes.py`, recria o banco `schulz_mvp.db` e define os dados de teste (certificado de calibração nº 00091/2026, equipamento 703.1208, técnico Jose Alcides Rosa Junior).
2. **Gravação:** 1 técnico, 1 equipamento e **14 medições** (`Medições gravadas: 14`). O status de cada uma é calculado por `Medicao.validar_status()`.
3. **Relatório com JOIN:** `relatorio_calibracoes("703.1208")` junta `medicao`, `tecnico` e `equipamento` e devolve nome do técnico, equipamento, parâmetro, tolerâncias, valor obtido e status. O terminal mostra a faixa permitida (limites inferior e superior) de cada característica.
4. **Resumo:** `8 aprovado(s) / 6 reprovado(s)`. As 6 reprovadas são características de POSIÇÃO, com valores acima de 0,100. O resultado é idêntico ao da Entrega 02.
5. **UPDATE:** a medição `62P_POSIÇÃO 1` é corrigida de 0,430 para 0,080 e o status passa de REPROVADO para **APROVADO** automaticamente.
6. **Erros:** uma matrícula duplicada é bloqueada pelo banco (mensagem `UNIQUE constraint failed: tecnico.matricula`) e dados vazios são bloqueados pela classe (`O campo matrícula é obrigatório.`).

Trecho da saída do relatório:

```
Parâmetro             Lim.Inf  Lim.Sup   Obtido  Status
PLANICIDADE_REF         0.000    0.050    0.002  APROVADO
62P_DIÂMETRO 1          6.065    6.085    6.079  APROVADO
62P_POSIÇÃO 1           0.000    0.100    0.430  REPROVADO
...
Resumo: 8 aprovado(s) / 6 reprovado(s)
```

### Observações

- O banco do MVP (`schulz_mvp.db`) é independente do banco da Entrega 02 (`schulz_calibracao.db`) e tem a mesma estrutura de tabelas.
- O e-mail do técnico não consta nas planilhas da Schulz e é gravado como "Não informado".
- Próximos passos (Parte 2 do MVP): leitura automática dos dados das planilhas (ETL), geração do certificado e interface para o usuário.
