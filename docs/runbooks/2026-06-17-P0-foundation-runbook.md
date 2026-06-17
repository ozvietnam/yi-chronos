# Runbook — P0 nền scale (PR1: data layer Postgres + RLS + migration)

> **Đối tượng:** dev local có quyền tạo server/DB + credentials (Claude không có
> quyền hạ tầng thật nên không tự chạy bước provision/cutover).
> **Phạm vi PR1:** tầng dữ liệu (thoát SQLite → Postgres + RLS + migrate). Các phần
> P0 còn lại (PgBouncer prod, replica, Celery workers, ≥3 API, observability, PITR)
> là PR kế tiếp — xem "Lộ trình P0" cuối file.
> **Master plan:** `docs/design/2026-06-17-scale-20M-monetization-masterplan-H5-H8.md`.
> **Issue:** #41.

---

## 0. Đã có sẵn trong PR này (đã test trên Postgres thật)

| File | Vai trò |
|---|---|
| `db/postgres/schema.sql` | 8 bảng hợp nhất + index + **RLS** (idempotent; chạy được cả psql lẫn psycopg) |
| `engine/db.py` | Engine SQLAlchemy dual-driver (Postgres prod / SQLite dev) + `session_scope(uid/service)` set GUC RLS |
| `scripts/migrate_sqlite_to_postgres.py` | Copy SQLite→PG + verify số dòng + sync sequence |
| `infra/docker-compose.p0.yml` | Postgres+pgvector + PgBouncer + Redis cho dev/staging |
| `tests/test_p0_db_foundation.py` | 7 test: RLS cô lập + chặn ghi chéo + deny-by-default + migration |

Kiểm chứng đã chạy: `YI_TEST_PG_DSN=… pytest tests/test_p0_db_foundation.py` → **7 passed**;
không có PG → 3 passed + 4 skipped (an toàn cho CI).

---

## 1. Provision Postgres (prod = self-host VN — PDPL)

Chọn 1: managed Postgres in-VN (Viettel IDC / FPT Cloud / VNG) **hoặc** tự dựng VM VN.
Khởi đầu (≤10k user): 1 instance 4 vCPU / 16GB / SSD là đủ.

```bash
# Tạo DB + role app KHÔNG superuser (RLS chỉ áp lên non-superuser; FORCE RLS áp cả owner).
createdb yi
psql -d yi -c "CREATE ROLE yi_app LOGIN PASSWORD '<secret-mạnh>';"
psql -d yi -c "ALTER DATABASE yi OWNER TO yi_app;"   # yi_app làm chủ → tạo policy được
```

> ⚠️ App PHẢI kết nối bằng **role thường (yi_app), KHÔNG superuser** — superuser bypass RLS.
> Đã bật `FORCE ROW LEVEL SECURITY` nên kể cả owner cũng bị RLS chi phối (đúng ý đồ).

(Local thử nhanh: `docker compose -f infra/docker-compose.p0.yml up -d` → DB qua PgBouncer cổng 6432.)

## 2. Áp schema

```bash
psql "postgresql://yi_app:<secret>@<host>:5432/yi" -v ON_ERROR_STOP=1 -f db/postgres/schema.sql
```
(Idempotent — chạy lại an toàn.)

## 3. Migrate dữ liệu từ SQLite

```bash
export DATABASE_URL="postgresql+psycopg://yi_app:<secret>@<host>:5432/yi"

# 3a. Dry-run: chỉ đọc + đếm, KHÔNG ghi
python scripts/migrate_sqlite_to_postgres.py --dry-run

# 3b. Thật: (schema đã áp ở B2 nên bỏ --apply-schema; --truncate nếu muốn cutover sạch)
python scripts/migrate_sqlite_to_postgres.py --truncate
# → in "VERIFY (source vs postgres)" + "RESULT: ALL OK" (exit 0). Nếu MISMATCH → dừng, điều tra.
```

Nguồn mặc định: `data/yi_users/users.sqlite3` + `data/yi_hermes/memory.sqlite3`
(copy 2 file này lên máy chạy migrate, hoặc chạy ngay trên VPS hiện tại).

## 4. Cutover (chuyển app sang Postgres)

1. Đặt env prod `DATABASE_URL=postgresql+psycopg://yi_app:<secret>@<host>:5432/yi` cho API.
2. **PR kế tiếp** sẽ chuyển từng module (`api/auth.py`, `sync.py`, `subscriptions.py`,
   `yi_hermes/memory.py`) từ `sqlite3.connect(...)` sang `engine.db.session_scope(...)`.
   PR1 này **non-breaking**: chưa đổi code cũ, chỉ thêm tầng mới + migrate sẵn dữ liệu.
3. Sau cutover: bridge (Cloud Functions) gọi qua service-mode; endpoint per-user set `uid`.

## 5. PITR + backup off-site (BẮT BUỘC trước khi nhận traffic thật)

```bash
# WAL archiving + base backup → object storage KHÁC máy/khác vùng (VN).
# pg_dump hằng ngày bổ sung:
pg_dump "postgresql://yi_app:<secret>@<host>:5432/yi" -Fc -f yi_$(date +%F).dump
# → đẩy lên object storage in-VN.
```
**Diễn tập khôi phục** (restore-drill) ít nhất 1 lần: `pg_restore` ra DB tạm + so số dòng.
*Backup chưa test = không có backup.*

## 6. Bẫy đã gặp (đừng lặp lại)

- **Kết nối bằng superuser** → RLS bị bypass, tưởng an toàn mà không. Dùng `yi_app`.
- **`SET LOCAL app.current_uid = :u`** KHÔNG nhận tham số → dùng `set_config('app.current_uid', :u, true)` (đã xử lý trong `engine/db.py`).
- **Ký tự `%` trong schema.sql** (kể cả trong comment / `DO format('%I')`) làm psycopg lỗi placeholder → schema viết tường minh, không `%`.
- **Chèn id tường minh** không advance sequence → migration đã `setval` sau khi copy.

---

## Lộ trình P0 (chuỗi PR)

- **PR1 (file này):** data layer — schema+RLS+engine+migration+test. ✅
- **PR2:** chuyển `api/auth.py` + `sync.py` + `subscriptions.py` + `memory.py` sang `engine.db` (bỏ `sqlite3`), giữ nguyên hành vi (test hồi quy).
- **PR3:** Celery + Redis + Beat (queue `q_deepread`/`q_hermes`/`q_digest`/`q_compat`) — nền cho H5/H7.
- **PR4:** gunicorn đa worker + Nginx LB + ≥3 instance + rolling deploy (sửa `Dockerfile`/`deploy.yml`).
- **PR5:** observability (Prometheus/Grafana/Sentry + bảng `llm_spend`) + rate-limit Redis.
- **PR6:** read replica + PgBouncer prod + partition `user_castings`/`user_events` (khi tới mốc).

Mỗi PR có test + cập nhật runbook. Sharding/Citus: hoãn tới khi đo nghẽn ghi thật.
