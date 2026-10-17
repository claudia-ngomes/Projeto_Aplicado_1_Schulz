-- ==============================================================================
-- UNIDADE CURRICULAR: PROJETO APLICADO I
-- EMPRESA PARCEIRA: SCHULZ S.A.
-- GRUPO: 23
-- ITEM 03: SCRIPT DDL DE CRIAÇÃO DO BANCO DE DADOS RELACIONAL (SQLite)
-- ==============================================================================

-- 1. Ativar obrigatoriedade de Chaves Estrangeiras no SQLite
PRAGMA foreign_keys = ON;

-- 2. TABELA 1: TECNICO (Técnico/Solicitante)
CREATE TABLE IF NOT EXISTS tecnico (
    id_tecnico INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_tecnico TEXT NOT NULL,
    matricula TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL,
    setor TEXT NOT NULL
);

-- 3. TABELA 2: EQUIPAMENTO
CREATE TABLE IF NOT EXISTS equipamento (
    id_equipamento INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_tag TEXT NOT NULL UNIQUE,
    nome_equipamento TEXT NOT NULL,
    fabricante TEXT NOT NULL,
    modelo TEXT NOT NULL
);

-- 4. TABELA 3: MEDICAO (Tabela Transacional com FKs)
CREATE TABLE IF NOT EXISTS medicao (
    id_medicao INTEGER PRIMARY KEY AUTOINCREMENT,
    id_equipamento INTEGER NOT NULL,
    id_tecnico INTEGER NOT NULL,
    parametro_medido TEXT NOT NULL,
    valor_nominal REAL NOT NULL,
    tolerancia_min REAL NOT NULL,
    tolerancia_max REAL NOT NULL,
    valor_obtido REAL NOT NULL,
    status_resultado TEXT NOT NULL CHECK (status_resultado IN ('APROVADO', 'REPROVADO')),
    data_medicao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_equipamento) REFERENCES equipamento (id_equipamento)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (id_tecnico) REFERENCES tecnico (id_tecnico)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- 5. DADOS REAIS (Certificado de Calibração nº 00091/2026, de 26/08/2026)
-- Fonte: Certificado_de_Calibração__Modelo_.pdf e Planilha_do_Software_com_a_Calibração_do_Dispositivo.xlsx
-- Técnico: nome e matrícula conforme aba "Complemento" (B76 e B77).
-- O e-mail não consta nas planilhas da Schulz, por isso fica como "Não informado".
INSERT INTO tecnico (nome_tecnico, matricula, email, setor) VALUES
    ('Jose Alcides Rosa Junior', '16858-0', 'Não informado', 'Metrologia');

-- Equipamento: código/TAG, descritivo, fabricante e modelo conforme aba "Complemento" (B40 a B43)
INSERT INTO equipamento (codigo_tag, nome_equipamento, fabricante, modelo) VALUES
    ('703.1208', 'Dispositivo de controle', 'Não consta', 'Não se aplica');

-- Medições: tabela "4. Resultados (mm)" do certificado.
-- tolerancia_min / tolerancia_max são os desvios permitidos em relação ao valor nominal (colunas Tol. - e Tol. +).
-- status_resultado: APROVADO se valor_obtido ficar entre (nominal + tol_min) e (nominal + tol_max).
INSERT INTO medicao (id_equipamento, id_tecnico, parametro_medido, valor_nominal,
                      tolerancia_min, tolerancia_max, valor_obtido, status_resultado, data_medicao) VALUES
    (1, 1, 'PLANICIDADE_REF',    0.000,  0.000, 0.050,  0.002, 'APROVADO',  '2026-08-26'),
    (1, 1, 'ENTRE CENTROS_REF',  0.000,  0.000, 0.040,  0.027, 'APROVADO',  '2026-08-26'),
    (1, 1, '62P_DIÂMETRO 1',     6.075, -0.010, 0.010,  6.079, 'APROVADO',  '2026-08-26'),
    (1, 1, '62P_POSIÇÃO 1',      0.000,  0.000, 0.100,  0.430, 'REPROVADO', '2026-08-26'),
    (1, 1, '62P_DIÂMETRO 2',     6.075, -0.010, 0.010,  6.078, 'APROVADO',  '2026-08-26'),
    (1, 1, '62P_POSIÇÃO 2',      0.000,  0.000, 0.100,  0.245, 'REPROVADO', '2026-08-26'),
    (1, 1, '13P_DIÂMETRO 1',    16.964, -0.010, 0.010, 16.968, 'APROVADO',  '2026-08-26'),
    (1, 1, '13P_POSIÇÃO 1',      0.000,  0.000, 0.100,  0.959, 'REPROVADO', '2026-08-26'),
    (1, 1, '13P_DIÂMETRO 2',    16.964, -0.010, 0.010, 16.970, 'APROVADO',  '2026-08-26'),
    (1, 1, '13P_POSIÇÃO 2',      0.000,  0.000, 0.100,  0.236, 'REPROVADO', '2026-08-26'),
    (1, 1, '106P_DIÂMETRO 1',    6.345, -0.010, 0.010,  6.346, 'APROVADO',  '2026-08-26'),
    (1, 1, '106P_POSIÇÃO 1',     0.000,  0.000, 0.100,  0.132, 'REPROVADO', '2026-08-26'),
    (1, 1, '106P_DIÂMETRO 2',    6.345, -0.010, 0.010,  6.349, 'APROVADO',  '2026-08-26'),
    (1, 1, '106P_POSIÇÃO 2',     0.000,  0.000, 0.100,  0.868, 'REPROVADO', '2026-08-26');
