-- =========================================================
-- Sistema de Gestão da Enfermaria Escolar
-- Script de criação do banco de dados (PostgreSQL)
-- Atualizado conforme os models SQLAlchemy reais em backend/app/models
-- =========================================================

CREATE TABLE usuario (
    id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome            VARCHAR(150) NOT NULL,
    login           VARCHAR(100) NOT NULL UNIQUE,
    senha_hash      VARCHAR(255) NOT NULL,
    tipo_acesso     VARCHAR(20) NOT NULL DEFAULT 'ADMIN' CHECK (tipo_acesso IN ('ADMIN', 'ENFERMAGEM', 'PROFESSORA')),
    ativo           BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em       TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_usuario_login ON usuario(login);


CREATE TABLE sala (
    id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome            VARCHAR(100) NOT NULL,
    descricao       VARCHAR(255),
    ativa           BOOLEAN NOT NULL DEFAULT TRUE
);


CREATE TABLE professora (
    id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome            VARCHAR(150) NOT NULL,
    telefone        VARCHAR(20),
    email           VARCHAR(150),
    ativa           BOOLEAN NOT NULL DEFAULT TRUE
);


CREATE TABLE turma (
    id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome            VARCHAR(100) NOT NULL,
    sala_id         BIGINT NOT NULL REFERENCES sala(id),
    turno           VARCHAR(10) NOT NULL CHECK (turno IN ('MANHA', 'TARDE', 'INTEGRAL')),
    ano_letivo      SMALLINT NOT NULL CHECK (ano_letivo >= 2000),
    ativa           BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX idx_turma_sala ON turma(sala_id);

-- Tabela de ligação N:N (uma turma pode ter mais de uma professora)
-- OBS: no código atual essa tabela é criada 2x (app/models/turma.py e
-- app/models/turma_professora.py) com definições quase idênticas — mantenha
-- só uma dessas duas fontes no projeto para evitar conflito de metadata.
CREATE TABLE turma_professora (
    id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    turma_id        BIGINT REFERENCES turma(id) ON DELETE CASCADE,
    professora_id   BIGINT REFERENCES professora(id) ON DELETE CASCADE,
    papel           VARCHAR(20)
);

CREATE INDEX idx_turma_professora_turma ON turma_professora(turma_id);
CREATE INDEX idx_turma_professora_professora ON turma_professora(professora_id);


CREATE TABLE profissional_enfermagem (
    id                   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome                VARCHAR(150) NOT NULL,
    funcao              VARCHAR(20) NOT NULL,
    registro_coren      VARCHAR(30),
    telefone            VARCHAR(20),
    ativa               BOOLEAN NOT NULL DEFAULT TRUE
);


-- ALTERADO: alergias e condições de saúde não são mais tabelas estruturadas
-- (alergia / condicao_saude / aluno_alergia / aluno_condicao foram removidas
-- do código). Agora são campos de texto livre direto em aluno.
CREATE TABLE aluno (
    id                   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome                VARCHAR(150) NOT NULL,
    data_nascimento     DATE NOT NULL,
    foto_url            VARCHAR(255),
    observacoes         TEXT,
    alergias            TEXT,
    condicoes_saude     TEXT,
    ativo               BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em           TIMESTAMP NOT NULL DEFAULT NOW()
);


CREATE TABLE matricula (
    id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    aluno_id        BIGINT NOT NULL REFERENCES aluno(id),
    turma_id        BIGINT NOT NULL REFERENCES turma(id),
    data_inicio     DATE NOT NULL,
    data_fim        DATE
);

CREATE INDEX idx_matricula_aluno ON matricula(aluno_id);
CREATE INDEX idx_matricula_turma ON matricula(turma_id);
-- Mantidas por segurança de integridade (não estão nos models SQLAlchemy,
-- que não declaram __table_args__, mas evitam dados inconsistentes):
CREATE UNIQUE INDEX idx_matricula_unica ON matricula(aluno_id, turma_id, data_inicio);
CREATE UNIQUE INDEX idx_matricula_ativa_unica
    ON matricula(aluno_id)
    WHERE data_fim IS NULL;


CREATE TABLE responsavel (
    id                       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome                    VARCHAR(150) NOT NULL,
    parentesco              VARCHAR(50) NOT NULL,
    telefone_principal      VARCHAR(20) NOT NULL,
    telefone_secundario     VARCHAR(20),
    email                   VARCHAR(150),
    autorizado_buscar       BOOLEAN NOT NULL DEFAULT TRUE
);

-- ALTERADO: agora é chave primária composta (sem coluna id própria),
-- conforme app/models/aluno.py
CREATE TABLE aluno_responsavel (
    aluno_id        BIGINT NOT NULL REFERENCES aluno(id) ON DELETE CASCADE,
    responsavel_id  BIGINT NOT NULL REFERENCES responsavel(id) ON DELETE CASCADE,
    PRIMARY KEY (aluno_id, responsavel_id)
);

CREATE INDEX idx_aluno_responsavel_aluno ON aluno_responsavel(aluno_id);
CREATE INDEX idx_aluno_responsavel_responsavel ON aluno_responsavel(responsavel_id);


CREATE TABLE tipo_ocorrencia (
    id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome    VARCHAR(50) NOT NULL UNIQUE,
    ativo   BOOLEAN NOT NULL DEFAULT TRUE
);


CREATE TABLE ocorrencia (
    id                       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    aluno_id                BIGINT NOT NULL REFERENCES aluno(id),
    data_hora               TIMESTAMP NOT NULL DEFAULT NOW(),
    criado_em               TIMESTAMP NOT NULL DEFAULT NOW(),
    professora_id           BIGINT NOT NULL REFERENCES professora(id),
    profissional_id         BIGINT NOT NULL REFERENCES profissional_enfermagem(id),
    usuario_registrou_id    BIGINT NOT NULL REFERENCES usuario(id),
    tipo_ocorrencia_id      BIGINT NOT NULL REFERENCES tipo_ocorrencia(id),
    descricao               TEXT NOT NULL,
    conduta                 TEXT NOT NULL,
    resultado               VARCHAR(40) NOT NULL CHECK (resultado IN (
                                'RETORNOU_SALA',
                                'PERMANECEU_OBSERVACAO',
                                'RESPONSAVEL_COMUNICADO',
                                'RESPONSAVEL_BUSCOU',
                                'ENCAMINHADO_EXTERNO',
                                'OUTRO'
                             )),
    responsavel_buscou_id   BIGINT REFERENCES responsavel(id),
    observacoes             TEXT,
    modificado_em           TIMESTAMP
);

CREATE INDEX idx_ocorrencia_aluno ON ocorrencia(aluno_id);
CREATE INDEX idx_ocorrencia_data ON ocorrencia(data_hora);
CREATE INDEX idx_ocorrencia_tipo ON ocorrencia(tipo_ocorrencia_id);
CREATE INDEX idx_ocorrencia_profissional ON ocorrencia(profissional_id);


-- Trigger: atualiza modificado_em automaticamente em UPDATE
-- OBS: o SQLAlchemy não gerencia isso sozinho (modificado_em é apenas
-- nullable no model), então o trigger no banco continua sendo a forma
-- mais confiável de manter esse campo correto.
CREATE OR REPLACE FUNCTION atualizar_modificado_em()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modificado_em = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_ocorrencia_modificado
    BEFORE UPDATE ON ocorrencia
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_modificado_em();