-- =========================================================
-- Correção: isolar também a tabela `responsavel` por escola.
--
-- Por quê: responsavel NÃO estava na lista original da Etapa 1
-- porque a ideia era isolá-la indiretamente via aluno_responsavel
-- (a ligação N:N com aluno). Só que um responsável pode ser
-- cadastrado ANTES de ser vinculado a qualquer aluno — nesse
-- intervalo ele fica "solto", sem nenhuma escola associada, e
-- GET /responsaveis vazaria registros de todas as escolas juntas.
--
-- Rode isso depois da migracao_multi_escola.sql original.
-- Segue exatamente o mesmo padrão dela (não apaga nada).
-- =========================================================

ALTER TABLE responsavel ADD COLUMN IF NOT EXISTS escola_id BIGINT REFERENCES escola(id);

-- Preenche a partir da escola dos alunos já vinculados a cada responsável
-- (se um responsável tiver vínculo com mais de um aluno, todos devem ser
-- da mesma escola nesse momento da migração, já que só existe 1 escola).
UPDATE responsavel r
SET escola_id = (
    SELECT a.escola_id
    FROM aluno_responsavel ar
    JOIN aluno a ON a.id = ar.aluno_id
    WHERE ar.responsavel_id = r.id
    LIMIT 1
)
WHERE r.escola_id IS NULL;

-- Responsáveis sem nenhum aluno vinculado ainda: caem na escola 1
-- (ajuste o id se a sua escola "atual" não for 1).
UPDATE responsavel SET escola_id = 1 WHERE escola_id IS NULL;

ALTER TABLE responsavel ALTER COLUMN escola_id SET NOT NULL;

CREATE INDEX IF NOT EXISTS idx_responsavel_escola ON responsavel(escola_id);

-- Checagem: deve retornar 0 antes de rodar o ALTER ... SET NOT NULL acima
-- SELECT count(*) FROM responsavel WHERE escola_id IS NULL;
