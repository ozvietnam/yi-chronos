-- =====================================================================
-- YI-Chronos — P0 data layer: consolidated Postgres schema + RLS
-- =====================================================================
-- Hợp nhất các file SQLite rời (users/persons/castings/favorites/
-- subscriptions + hermes memory) thành MỘT Postgres, thêm Row-Level
-- Security (RLS) để cô lập tenant ở tầng DB (Iron Rule #7 — chống lộ data).
--
-- Quy ước RLS (2 GUC phiên):
--   app.current_uid  : id user đang thao tác (text; so khớp cả user_id int
--                      lẫn user_id text của bảng memory).
--   app.service_mode : 'on' = bypass RLS cho luồng service-to-service
--                      (Cloud Functions bridge) + admin owner.
-- Mặc định (chưa set GUC) → current_setting(...,true)=NULL → KHÔNG thấy
-- dòng nào (deny-by-default). Phải set GUC mới đọc/ghi được.
--
-- Faithful 1:1 với SQLite hiện tại (epoch BIGINT, JSON→JSONB) để migrate
-- không mất mát + không phải đổi logic app. Partition/shard là bước scale
-- sau (xem master plan §2), KHÔNG làm ở P0-1.
-- =====================================================================

-- ---- helper: điều kiện RLS dùng chung ----
CREATE OR REPLACE FUNCTION app_rls_ok(row_uid text) RETURNS boolean
  LANGUAGE sql STABLE AS $$
  SELECT current_setting('app.service_mode', true) = 'on'
      OR row_uid = current_setting('app.current_uid', true);
$$;

-- =====================================================================
-- 1. users  (nguồn: data/yi_users/users.sqlite3)
-- =====================================================================
CREATE TABLE IF NOT EXISTS users (
    user_id              BIGSERIAL PRIMARY KEY,
    email                TEXT UNIQUE NOT NULL,
    display_name         TEXT NOT NULL,
    password_hash        TEXT NOT NULL,
    password_salt        TEXT NOT NULL,
    role                 TEXT NOT NULL DEFAULT 'user',   -- 'owner' | 'user'
    default_person_id    TEXT,
    created_at           BIGINT NOT NULL,
    last_login_at        BIGINT,
    must_change_password SMALLINT DEFAULT 0,
    is_suspended         SMALLINT DEFAULT 0,
    suspended_at         BIGINT,
    suspend_reason       TEXT,
    firebase_uid         TEXT,
    phone                TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_firebase_uid
    ON users(firebase_uid) WHERE firebase_uid IS NOT NULL;

-- =====================================================================
-- 2. user_persons
-- =====================================================================
CREATE TABLE IF NOT EXISTS user_persons (
    id                   BIGSERIAL PRIMARY KEY,
    user_id              BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    person_key           TEXT NOT NULL,
    name                 TEXT NOT NULL,
    relationship         TEXT,
    gender               TEXT,
    birth_datetime_local TEXT,
    birth_year           INTEGER,
    timezone             TEXT DEFAULT 'Asia/Ho_Chi_Minh',
    birth_place          TEXT,
    notes                TEXT,
    created_at           BIGINT NOT NULL,
    updated_at           BIGINT,
    UNIQUE(user_id, person_key)
);
CREATE INDEX IF NOT EXISTS idx_user_persons_user ON user_persons(user_id);

-- =====================================================================
-- 3. user_castings  (lịch sử cast — H1; có algo_version cho freshness §5bis)
-- =====================================================================
CREATE TABLE IF NOT EXISTS user_castings (
    id                 BIGSERIAL PRIMARY KEY,
    user_id            BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    method             TEXT NOT NULL,
    subject_person_key TEXT,
    question           TEXT,
    input_json         JSONB,
    result_json        JSONB NOT NULL,
    verdict            TEXT,
    tags               TEXT,
    note               TEXT,
    algo_version       TEXT,
    created_at         BIGINT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_user_castings_user    ON user_castings(user_id);
CREATE INDEX IF NOT EXISTS idx_user_castings_method  ON user_castings(user_id, method);
CREATE INDEX IF NOT EXISTS idx_user_castings_created ON user_castings(created_at);

-- =====================================================================
-- 4. user_favorites  (gồm couple_match — gieo duyên)
-- =====================================================================
CREATE TABLE IF NOT EXISTS user_favorites (
    id           BIGSERIAL PRIMARY KEY,
    user_id      BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    kind         TEXT NOT NULL,
    label        TEXT NOT NULL,
    payload_json JSONB NOT NULL,
    created_at   BIGINT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_user_favorites_user ON user_favorites(user_id, kind);

-- =====================================================================
-- 5. user_subscriptions  (gói trả phí — engine/subscriptions.py)
-- =====================================================================
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id             BIGSERIAL PRIMARY KEY,
    user_id        BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    feature_id     TEXT NOT NULL,
    tier           TEXT,
    enabled        SMALLINT DEFAULT 1,
    expires_at     BIGINT,
    remaining_uses INTEGER,
    total_uses     INTEGER DEFAULT 0,
    granted_by     BIGINT,
    granted_at     BIGINT,
    notes          TEXT,
    UNIQUE(user_id, feature_id)
);
CREATE INDEX IF NOT EXISTS idx_user_subs_user ON user_subscriptions(user_id);

-- =====================================================================
-- 6-8. Hermes memory  (nguồn: data/yi_hermes/memory.sqlite3)
--      user_id ở các bảng này là TEXT (firebase uid / chuỗi).
-- =====================================================================
CREATE TABLE IF NOT EXISTS user_facts (
    id                BIGSERIAL PRIMARY KEY,
    user_id           TEXT NOT NULL,
    fact              TEXT NOT NULL,
    category          TEXT,
    confidence        REAL DEFAULT 0.8,
    source_session_id BIGINT,
    notes             TEXT,
    extracted_at      TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_facts_user ON user_facts(user_id);

CREATE TABLE IF NOT EXISTS chat_summaries (
    id              BIGSERIAL PRIMARY KEY,
    user_id         TEXT NOT NULL,
    session_id      BIGINT,
    summary         TEXT NOT NULL,
    key_topics      JSONB,
    chart_data_hash TEXT,
    created_at      TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_summaries_user ON chat_summaries(user_id);
-- FTS tiếng Việt: dùng GIN trên to_tsvector('simple', ...) (thay FTS5 của SQLite)
CREATE INDEX IF NOT EXISTS idx_summaries_fts
    ON chat_summaries USING gin (to_tsvector('simple', coalesce(summary,'')));

CREATE TABLE IF NOT EXISTS glossary_views (
    id        BIGSERIAL PRIMARY KEY,
    user_id   TEXT NOT NULL,
    term_vi   TEXT NOT NULL,
    viewed_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_glossary_user ON glossary_views(user_id);

-- =====================================================================
-- RLS — bật + policy cho mọi bảng theo user
-- =====================================================================
-- Bật + FORCE RLS từng bảng (viết tường minh, KHÔNG dùng DO/format có ký tự
-- đặc biệt — để file chạy được cả qua psql lẫn driver psycopg3).
ALTER TABLE users              ENABLE ROW LEVEL SECURITY;  ALTER TABLE users              FORCE ROW LEVEL SECURITY;
ALTER TABLE user_persons       ENABLE ROW LEVEL SECURITY;  ALTER TABLE user_persons       FORCE ROW LEVEL SECURITY;
ALTER TABLE user_castings      ENABLE ROW LEVEL SECURITY;  ALTER TABLE user_castings      FORCE ROW LEVEL SECURITY;
ALTER TABLE user_favorites     ENABLE ROW LEVEL SECURITY;  ALTER TABLE user_favorites     FORCE ROW LEVEL SECURITY;
ALTER TABLE user_subscriptions ENABLE ROW LEVEL SECURITY;  ALTER TABLE user_subscriptions FORCE ROW LEVEL SECURITY;
ALTER TABLE user_facts         ENABLE ROW LEVEL SECURITY;  ALTER TABLE user_facts         FORCE ROW LEVEL SECURITY;
ALTER TABLE chat_summaries     ENABLE ROW LEVEL SECURITY;  ALTER TABLE chat_summaries     FORCE ROW LEVEL SECURITY;
ALTER TABLE glossary_views     ENABLE ROW LEVEL SECURITY;  ALTER TABLE glossary_views     FORCE ROW LEVEL SECURITY;

-- idempotent: drop trước khi create (cho phép chạy lại schema.sql)
DROP POLICY IF EXISTS p_users      ON users;
DROP POLICY IF EXISTS p_persons    ON user_persons;
DROP POLICY IF EXISTS p_castings   ON user_castings;
DROP POLICY IF EXISTS p_favorites  ON user_favorites;
DROP POLICY IF EXISTS p_subs       ON user_subscriptions;
DROP POLICY IF EXISTS p_facts      ON user_facts;
DROP POLICY IF EXISTS p_summaries  ON chat_summaries;
DROP POLICY IF EXISTS p_glossary   ON glossary_views;

-- users: cột định danh là user_id
CREATE POLICY p_users      ON users             USING (app_rls_ok(user_id::text)) WITH CHECK (app_rls_ok(user_id::text));
CREATE POLICY p_persons    ON user_persons      USING (app_rls_ok(user_id::text)) WITH CHECK (app_rls_ok(user_id::text));
CREATE POLICY p_castings   ON user_castings     USING (app_rls_ok(user_id::text)) WITH CHECK (app_rls_ok(user_id::text));
CREATE POLICY p_favorites  ON user_favorites    USING (app_rls_ok(user_id::text)) WITH CHECK (app_rls_ok(user_id::text));
CREATE POLICY p_subs       ON user_subscriptions USING (app_rls_ok(user_id::text)) WITH CHECK (app_rls_ok(user_id::text));
-- memory: user_id đã là text
CREATE POLICY p_facts      ON user_facts        USING (app_rls_ok(user_id)) WITH CHECK (app_rls_ok(user_id));
CREATE POLICY p_summaries  ON chat_summaries    USING (app_rls_ok(user_id)) WITH CHECK (app_rls_ok(user_id));
CREATE POLICY p_glossary   ON glossary_views    USING (app_rls_ok(user_id)) WITH CHECK (app_rls_ok(user_id));
