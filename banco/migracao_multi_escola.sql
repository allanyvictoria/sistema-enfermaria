-- =========================================================
-- Migração: Multi-escola (multi-tenant)
-- Rode isso DEPOIS do estrutura.sql já existente, num banco
-- que já tem dados (não apaga nada).
-- =========================================================

-- 1. Tabela de escolas
CREATE TABLE IF NOT EXISTS escola (
    id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome            VARCHAR(150) NOT NULL,
    ativa           BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em       TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 2. Cria a escola "atual" para migrar os dados existentes.
--    Troque o nome abaixo pelo nome real da escola que já usa o sistema.
INSERT INTO escola (nome) VALUES ('Escola Inicial')
RETURNING id;
-- Anote o id retornado acima (provavelmente 1) — vai ser usado nos
-- UPDATEs abaixo. Se for o primeiro registro da tabela, será 1.

-- 3. Adiciona a coluna escola_id (ainda opcional) nas tabelas que
--    precisam ser isoladas por escola.
ALTER TABLE usuario                 ADD COLUMN IF NOT EXISTS escola_id BIGINT REFERENCES escola(id);
ALTER TABLE sala                    ADD COLUMN IF NOT EXISTS escola_id BIGINT REFERENCES escola(id);
ALTER TABLE professora              ADD COLUMN IF NOT EXISTS escola_id BIGINT REFERENCES escola(id);
ALTER TABLE profissional_enfermagem ADD COLUMN IF NOT EXISTS escola_id BIGINT REFERENCES escola(id);
ALTER TABLE tipo_ocorrencia         ADD COLUMN IF NOT EXISTS escola_id BIGINT REFERENCES escola(id);
ALTER TABLE aluno                   ADD COLUMN IF NOT EXISTS escola_id BIGINT REFERENCES escola(id);

-- 4. Preenche todas as linhas existentes com o id da escola criada
--    no passo 2. Troque o "1" abaixo se o id retornado foi diferente.
UPDATE usuario                 SET escola_id = 1 WHERE escola_id IS NULL;
UPDATE sala                    SET escola_id = 1 WHERE escola_id IS NULL;
UPDATE professora              SET escola_id = 1 WHERE escola_id IS NULL;
UPDATE profissional_enfermagem SET escola_id = 1 WHERE escola_id IS NULL;
UPDATE tipo_ocorrencia         SET escola_id = 1 WHERE escola_id IS NULL;
UPDATE aluno                   SET escola_id = 1 WHERE escola_id IS NULL;

-- 5. Só depois de confirmar que TODAS as linhas têm escola_id
--    preenchido (rode os SELECTs de checagem abaixo antes disso),
--    torna a coluna obrigatória.
ALTER TABLE usuario                 ALTER COLUMN escola_id SET NOT NULL;
ALTER TABLE sala                    ALTER COLUMN escola_id SET NOT NULL;
ALTER TABLE professora              ALTER COLUMN escola_id SET NOT NULL;
ALTER TABLE profissional_enfermagem ALTER COLUMN escola_id SET NOT NULL;
ALTER TABLE tipo_ocorrencia         ALTER COLUMN escola_id SET NOT NULL;
ALTER TABLE aluno                   ALTER COLUMN escola_id SET NOT NULL;

-- 6. Índices (toda consulta filtrada por escola vai usar isso)
CREATE INDEX IF NOT EXISTS idx_usuario_escola ON usuario(escola_id);
CREATE INDEX IF NOT EXISTS idx_sala_escola ON sala(escola_id);
CREATE INDEX IF NOT EXISTS idx_professora_escola ON professora(escola_id);
CREATE INDEX IF NOT EXISTS idx_profissional_escola ON profissional_enfermagem(escola_id);
CREATE INDEX IF NOT EXISTS idx_tipo_ocorrencia_escola ON tipo_ocorrencia(escola_id);
CREATE INDEX IF NOT EXISTS idx_aluno_escola ON aluno(escola_id);

-- 7. Login deixa de ser único globalmente e passa a ser único por
--    escola (duas escolas podem ter cada uma seu "admin").
ALTER TABLE usuario DROP CONSTRAINT IF EXISTS usuario_login_key;
CREATE UNIQUE INDEX IF NOT EXISTS idx_usuario_login_escola ON usuario(login, escola_id);


-- =========================================================
-- Checagens úteis para rodar ANTES do passo 5 (não deixar
-- nenhuma linha sem escola_id):
-- =========================================================
-- SELECT count(*) FROM usuario WHERE escola_id IS NULL;
-- SELECT count(*) FROM sala WHERE escola_id IS NULL;
-- SELECT count(*) FROM professora WHERE escola_id IS NULL;
-- SELECT count(*) FROM profissional_enfermagem WHERE escola_id IS NULL;
-- SELECT count(*) FROM tipo_ocorrencia WHERE escola_id IS NULL;
-- SELECT count(*) FROM aluno WHERE escola_id IS NULL;
-- Todas devem retornar 0 antes de rodar o passo 5.
