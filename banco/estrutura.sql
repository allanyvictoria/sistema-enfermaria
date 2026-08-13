-- Sistema de Gestão da Enfermaria Escolar
-- Script de criação do banco de dados (PostgreSQL)

CREATE TABLE usuario (
    id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome            VARCHAR(150) NOT NULL,
    login           VARCHAR(100) NOT NULL UNIQUE,
    senha_hash      VARCHAR(255) NOT NULL,
    tipo_acesso     VARCHAR(20) NOT NULL CHECK (tipo_acesso IN ('ADMIN', 'ENFERMAGEM', 'PROFESSORA')),
    ativo           BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em       TIMESTAMP NOT NULL DEFAULT NOW()
);


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
    turno           VARCHAR(10) NOT NULL CHECK (turno IN ('MANHA', 'TARDE', 'NOITE', 'INTEGRAL')),
    ano_letivo      SMALLINT NOT NULL CHECK (ano_letivo >= 2000),
    ativa           BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX idx_turma_sala ON turma(sala_id);


-- Tabela de ligação N:N (uma turma pode ter mais de uma professora)
CREATE TABLE turma_professora (
    id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    turma_id        BIGINT NOT NULL REFERENCES turma(id),
    professora_id   BIGINT NOT NULL REFERENCES professora(id),
    papel           VARCHAR(20) CHECK (papel IN ('TITULAR', 'AUXILIAR')),
    UNIQUE (turma_id, professora_id)
);

CREATE INDEX idx_turma_professora_turma ON turma_professora(turma_id);
CREATE INDEX idx_turma_professora_professora ON turma_professora(professora_id);


CREATE TABLE profissional_enfermagem (
    id                   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome                VARCHAR(150) NOT NULL,
    funcao              VARCHAR(20) NOT NULL CHECK (funcao IN ('ENFERMEIRO(A)', 'TECNICO(A)', 'AUXILIAR')),
    registro_coren      VARCHAR(30),
    telefone            VARCHAR(20),
    ativa               BOOLEAN NOT NULL DEFAULT TRUE
);


CREATE TABLE aluno (
    id                   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome                VARCHAR(150) NOT NULL,
    data_nascimento     DATE NOT NULL,
    foto_url            VARCHAR(255),
    observacoes         TEXT,
    ativo               BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em           TIMESTAMP NOT NULL DEFAULT NOW()
);


CREATE TABLE matricula (
    id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    aluno_id        BIGINT NOT NULL REFERENCES aluno(id),
    turma_id        BIGINT NOT NULL REFERENCES turma(id),
    data_inicio     DATE NOT NULL,
    data_fim        DATE,
    UNIQUE (aluno_id, turma_id, data_inicio)
);

CREATE INDEX idx_matricula_aluno ON matricula(aluno_id);
CREATE INDEX idx_matricula_turma ON matricula(turma_id);

-- Garante no máximo uma matrícula "ativa" (data_fim NULL) por aluno
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


-- Tabela de ligação N:N - um responsável pode ter vários alunos, e vice-versa
CREATE TABLE aluno_responsavel (
    id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    aluno_id        BIGINT NOT NULL REFERENCES aluno(id),
    responsavel_id  BIGINT NOT NULL REFERENCES responsavel(id),
    UNIQUE (aluno_id, responsavel_id)
);

CREATE INDEX idx_aluno_responsavel_aluno ON aluno_responsavel(aluno_id);
CREATE INDEX idx_aluno_responsavel_responsavel ON aluno_responsavel(responsavel_id);


CREATE TABLE alergia (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome        VARCHAR(100) NOT NULL UNIQUE,
    categoria   VARCHAR(20) CHECK (categoria IN ('MEDICAMENTO', 'ALIMENTO', 'OUTRO'))
);


CREATE TABLE condicao_saude (
    id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome    VARCHAR(100) NOT NULL UNIQUE
);


CREATE TABLE aluno_alergia (
    id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    aluno_id        BIGINT NOT NULL REFERENCES aluno(id),
    alergia_id      BIGINT NOT NULL REFERENCES alergia(id),
    gravidade       VARCHAR(10) CHECK (gravidade IN ('LEVE', 'MODERADA', 'GRAVE')),
    observacao      VARCHAR(255),
    UNIQUE (aluno_id, alergia_id)
);


CREATE TABLE aluno_condicao (
    id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    aluno_id        BIGINT NOT NULL REFERENCES aluno(id),
    condicao_id     BIGINT NOT NULL REFERENCES condicao_saude(id),
    gravidade       VARCHAR(10) CHECK (gravidade IN ('LEVE', 'MODERADA', 'GRAVE')),
    observacao      VARCHAR(255),
    UNIQUE (aluno_id, condicao_id)
);

CREATE INDEX idx_aluno_alergia_aluno ON aluno_alergia(aluno_id);
CREATE INDEX idx_aluno_condicao_aluno ON aluno_condicao(aluno_id);


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