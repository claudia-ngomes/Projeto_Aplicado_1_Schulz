# ==============================================================================
# UNIDADE CURRICULAR: PROJETO APLICADO I
# EMPRESA PARCEIRA: SCHULZ S.A.
# GRUPO: 23
# SCRIPT DE GERAÇÃO AUTOMÁTICA DA DOCUMENTAÇÃO EM MARKDOWN (01_estrutura.md)
# ==============================================================================

conteudo_markdown = """# PROJETO APLICADO I - SCHULZ S.A.
## Entrega 02: Modelagem e Estruturação de Banco de Dados Relacional

**Grupo:** 23
**Empresa parceira:** Schulz S.A. — Laboratório de Metrologia

---

### 1. Contexto e Problematização (Transição de Planilhas para BD)

Na Entrega 01, mapeamos o processo real de calibração da Schulz e diagnosticamos,
planilha por planilha, os problemas da gestão atual baseada em arquivos Excel
soltos (`Planilha_do_Software_com_a_Calibração_do_Dispositivo.xlsx`,
`Registro_MMC.xlsx`, `planilha_MMC.xlsm`). Entre as anomalias concretas que
encontramos nos arquivos reais estão:

- **Duplicidade de cadastro:** o mesmo instrumento é descrito em texto livre a
  cada novo arquivo de evento, sem um cadastro único (ex.: código `703.1208`).
- **Inconsistência de identidade:** o mesmo técnico aparece grafado como
  "Jose Alcides Rosa Junior" em uma aba e "José A. Rosa Jr" em outra — sem uma
  chave única de pessoa, duas grafias viram duas "pessoas" diferentes no banco.
- **Mistura de dado bruto e cálculo:** a aba "Certificado" do modelo atual lê
  diretamente de outras abas da mesma planilha, sem separar o dado de origem do
  documento final — qualquer erro de fórmula (como os `#NAME?` encontrados na
  aba "ViK") contamina o certificado emitido.
- **Falta de histórico:** como cada evento vive em um arquivo `.xlsx` isolado,
  não existe uma forma simples de consultar todas as calibrações de um mesmo
  instrumento ao longo do tempo.

A migração para um **Banco de Dados Relacional (SQLite)** resolve esses pontos
ao centralizar os dados, aplicar integridade referencial (chaves primárias e
estrangeiras) e permitir consulta histórica por instrumento, técnico ou
período — sem depender de reabrir arquivos Excel.

---

### 2. Divisão do Banco de Dados em Entidades Principais

Seguindo o modelo conceitual simplificado solicitado nesta entrega, o banco foi
estruturado em 3 entidades principais, mapeadas diretamente a partir dos campos
que já identificamos nas planilhas reais da Schulz:

#### 2.1. Entidade 1: TECNICO (Técnico/Solicitante)

- **Função:** armazena os dados cadastrais de quem executa a calibração —
  hoje repetidos (e grafados de forma inconsistente) a cada arquivo de evento.
- **Atributos previstos:** `id_tecnico` (chave primária), `nome_tecnico`,
  `matricula`, `email`, `setor`.
- **Origem real:** aba "Registro" (campo "Técnico executante") e aba
  "BANCO DE DADOS" (lista de metrologistas por turno).

#### 2.2. Entidade 2: EQUIPAMENTO

- **Função:** registra cada instrumento/dispositivo de controle calibrado
  pela Schulz, hoje descrito em texto livre a cada novo arquivo.
- **Atributos previstos:** `id_equipamento` (chave primária), `codigo_tag`
  (único), `nome_equipamento`, `fabricante`, `modelo`.
- **Origem real:** aba "Registro" (campos "Código do instrumento",
  "Denominação", "Fabricante").

#### 2.3. Entidade 3: MEDICAO (Medição/Calibração)

- **Função:** entidade transacional — uma linha por característica geométrica
  avaliada em um evento de calibração, conectando o técnico ao equipamento.
- **Atributos previstos:** `id_medicao` (chave primária), `id_equipamento`
  (chave estrangeira), `id_tecnico` (chave estrangeira), `parametro_medido`,
  `valor_nominal`, `tolerancia_min`, `tolerancia_max`, `valor_obtido`,
  `status_resultado`, `data_medicao`.
- **Origem real:** tabela de resultados da aba "Registro" (ex.: parâmetros
  "PLANICIDADE_REF", "62P_DIÂMETRO 1", cada um com valor nominal, tolerâncias
  e valor obtido).

---

### 3. Justificativa da Eliminação de Dados Duplicados

Separar o modelo em três entidades relacionadas (em vez de um arquivo por
evento, como é feito hoje) resolve diretamente os problemas mapeados na
Entrega 01:

1. **Cadastro único de técnico e equipamento:** um técnico ou instrumento é
   cadastrado uma única vez e referenciado por chave estrangeira em cada
   medição — evitando o problema real já encontrado de um mesmo profissional
   aparecer grafado de duas formas diferentes em arquivos distintos.
2. **Otimização de armazenamento:** dados que não mudam a cada calibração
   (fabricante, modelo, setor) deixam de ser redigitados em todo novo evento.
3. **Integridade referencial:** com `PRAGMA foreign_keys = ON` e chaves
   estrangeiras em `medicao`, o banco impede o registro de uma medição para um
   equipamento ou técnico que não exista no cadastro — o que hoje não é
   garantido pela planilha.
4. **Histórico consultável:** como todas as medições de um mesmo
   `id_equipamento` ficam na mesma tabela, é possível consultar o histórico
   completo de calibrações de um instrumento com uma única consulta SQL, sem
   precisar abrir arquivo por arquivo.

---

### 4. Próximos Passos (Implementação DDL no SQLite)

A partir dessa estrutura conceitual, a próxima etapa consiste na criação dos
scripts SQL (`CREATE TABLE`) para materializar o banco de dados
`schulz_calibracao.db`, executados via Python (`executar_banco.py`).
"""

nome_arquivo = "01_estrutura.md"
try:
    with open(nome_arquivo, "w", encoding="utf-8") as arquivo:
        arquivo.write(conteudo_markdown)
    print("=" * 60)
    print(f"SUCESSO: O arquivo '{nome_arquivo}' foi gerado com sucesso!")
    print("Abra o VS Code, selecione o arquivo e pressione 'Ctrl + Shift + V'")
    print("para visualizar a documentacao formatada.")
    print("=" * 60)
except Exception as e:
    print(f"ERRO ao gerar o arquivo: {e}")
