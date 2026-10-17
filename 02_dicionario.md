# 02_dicionario.md — Dicionário de Dados do Sistema

**Unidade Curricular:** Projeto Aplicado I
**Empresa Parceira:** Schulz S.A.
**Tema 02:** Modelagem e Implementação de Banco de Dados (SQLite)
**Grupo:** 23

---

## 1. Mapeamento das Tabelas e Campos

Os campos abaixo foram extraídos diretamente da análise das planilhas reais da
Schulz (`Planilha_do_Software_com_a_Calibração_do_Dispositivo.xlsx` e
`Registro_MMC.xlsx`), feita na Entrega 01, e condensados nas 3 entidades do
modelo conceitual simplificado.

### 1.1. Tabela: `tecnico` (Técnicos / Solicitantes)

| Nome do Campo | Tipo (SQLite) | Restrições / Chaves | Descrição / Regra de Negócio |
| :--- | :--- | :--- | :--- |
| `id_tecnico` | Inteiro | PRIMARY KEY AUTOINCREMENT | Identificador único do técnico. |
| `nome_tecnico` | Texto | NOT NULL | Nome completo do profissional (ex.: variações como "Jose Alcides Rosa Junior" / "José A. Rosa Jr" devem apontar para um único cadastro). |
| `matricula` | Texto | NOT NULL, UNIQUE | Matrícula do colaborador na Schulz. |
| `email` | Texto | NOT NULL | E-mail de contato do técnico/metrologista. |
| `setor` | Texto | NOT NULL | Setor de atuação (ex.: "Metrologia", espelhando a aba "BANCO DE DADOS"). |

### 1.2. Tabela: `equipamento` (Instrumentos e Dispositivos de Controle)

| Nome do Campo | Tipo (SQLite) | Restrições / Chaves | Descrição / Regra de Negócio |
| :--- | :--- | :--- | :--- |
| `id_equipamento` | Inteiro | PRIMARY KEY AUTOINCREMENT | Identificador único do equipamento no banco. |
| `codigo_tag` | Texto | NOT NULL, UNIQUE | Código do instrumento no padrão da Schulz (ex.: "703.1208"). |
| `nome_equipamento` | Texto | NOT NULL | Denominação do instrumento (ex.: dispositivo de controle). |
| `fabricante` | Texto | NOT NULL | Fabricante do instrumento calibrado. |
| `modelo` | Texto | NOT NULL | Modelo comercial ou especificação técnica do instrumento. |

### 1.3. Tabela: `medicao` (Registro das Calibrações)

| Nome do Campo | Tipo (SQLite) | Restrições / Chaves | Descrição / Regra de Negócio |
| :--- | :--- | :--- | :--- |
| `id_medicao` | Inteiro | PRIMARY KEY AUTOINCREMENT | Identificador único do evento de medição. |
| `id_equipamento` | Inteiro | FOREIGN KEY (equipamento) | Vínculo com o equipamento avaliado. |
| `id_tecnico` | Inteiro | FOREIGN KEY (tecnico) | Vínculo com o técnico responsável pela calibração. |
| `parametro_medido` | Texto | NOT NULL | Característica geométrica avaliada (ex.: "PLANICIDADE_REF", "62P_DIÂMETRO 1"). |
| `valor_nominal` | Real | NOT NULL | Valor de referência/projeto para a característica medida. |
| `tolerancia_min` | Real | NOT NULL | Limite inferior aceitável (tolerância negativa). |
| `tolerancia_max` | Real | NOT NULL | Limite superior aceitável (tolerância positiva). |
| `valor_obtido` | Real | NOT NULL | Valor efetivamente medido no evento de calibração. |
| `status_resultado` | Texto | CHECK ('APROVADO', 'REPROVADO') | Parecer técnico: aprovado se o valor obtido está dentro da faixa de tolerância. |
| `data_medicao` | Texto/DATETIME | DEFAULT CURRENT_TIMESTAMP | Data e hora do registro da medição no banco. |

---

**Total: 20 campos mapeados nas 3 entidades** (5 em `tecnico`, 5 em
`equipamento`, 10 em `medicao`).
