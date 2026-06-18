# Plan — PHÒNG QUẢN TRỊ Hermes (Admin/Governance Console) cho Founder

> Ngày: 2026-06-18 · Repo: YI-Chronos · Owner-only. Cho dev execute (test-first, nếp P0/H6).
> Mục tiêu: anh (founder) có **một nơi chỉ huy cả hệ Hermes** — xem roster, nói chuyện với
> "chỉ huy", duyệt tri thức mới, giám sát chi phí/paradigm, audit.

## 1. Khái niệm (đã chốt)
- **Roster:** 8 sage độc lập-thuần-khiết + **arbiter** (tổng hợp) + **orchestrator** (điều phối).
- Sage KHÔNG nói với nhau; giao tiếp **qua orchestrator → arbiter**.
- **Chỉ huy = orchestrator (chế độ operator)** — đại diện cả hệ, nói chuyện với founder.
- Mọi cập nhật não-chung qua **`evolve_gate`** (độ tự tin + owner duyệt). Đã có lõi.

## 2. Phạm vi Phòng Quản Trị (owner-only, `require_owner`, audit mọi hành động)

### 2.1 API (TS/FastAPI YI — prefix `/api/admin/hermes/*`, đều `require_owner`)
1. **Roster:** `GET /roster` → danh sách sage (tag, tên, enabled, `knowledge_version`, kích thước SOUL, lượt dùng gần đây, **#cờ paradigm**). `POST /sage/{tag}/toggle` bật/tắt. 
2. **SOUL:** `GET /sage/{tag}/soul` · `PUT /sage/{tag}/soul` (sửa persona — qua `prompt_store.set_prompt`, **ghi audit + version**).
3. **Cổng duyệt (evolve):** `GET /evolve/pending` (hàng đợi đã được em chấm) · `POST /evolve/{id}/review {approve, note}` → wire `evolve_gate.review` (+ bump `knowledge_version` nếu chạm T1).
4. **Giám sát:** `GET /metrics` → `llm_spend.spend_summary` (chi phí/ngày + theo provider) · lượt theo feature (council/quick/deep) · **#vi phạm paradigm** (đếm `user_castings.verdict='paradigm_flag'`) · cache-hit ước lượng · free/paid.
5. **Chỉ huy (commander chat):** `POST /commander/ask {question}` → orchestrator **chế độ operator**: trả lời câu hỏi quản trị bằng **công cụ đọc** (roster/metrics/evolve queue) — CHỈ báo cáo + đề xuất; hành động đụng não-chung trả về *đề xuất + nút xác nhận*, KHÔNG tự thực thi.
6. **Audit:** `GET /audit` → nhật ký (ai, làm gì, khi nào) cho mọi thao tác admin (tái dùng bảng `audit_log`).

### 2.2 UI (Vue `client/webapp` — route `/admin/hermes`, ẩn nếu không phải owner)
- **Panel Roster:** lưới 10 vai + trạng thái + nút bật/tắt + xem/sửa SOUL.
- **Panel Cổng Duyệt:** hàng đợi pending (kind, title, confidence, impact) + nút Duyệt/Bác + note.
- **Panel Giám Sát:** chi phí hôm nay vs ngân sách, lượt theo feature, #cờ paradigm, cache-hit.
- **Khung Chat Chỉ Huy:** ô chat với orchestrator-operator ("hệ thống thế nào?", "có gì chờ duyệt?"). Hành động → hiện thẻ xác nhận trước khi chạy.
- **Audit log:** bảng cuộn.

## 3. Nguyên tắc quản trị (ràng buộc)
- **Owner-only** (`require_owner`) + **audit mọi hành động** (đặc biệt sửa SOUL / duyệt evolve).
- Chỉ huy **đề xuất, không tự phá**: thao tác đụng não-chung (duyệt tri thức, sửa SOUL, bật/tắt sage) cần **owner xác nhận tay**.
- Tách bạch: **Hermes sản phẩm** (end-user) ≠ **Hermes chỉ huy** (quản trị) — khác surface, khác quyền.
- Paradigm: chỉ huy cũng tuân Iron #4/#6/#8 (đọc đồng dạng, không predict) khi báo cáo.
- Privacy: panel KHÔNG hiển thị PII end-user; chỉ số liệu tổng hợp + tri thức chung.

## 4. Tác vụ cho dev (test-first, theo thứ tự)
1. `engine/admin_hermes.py`: tổng hợp roster (đọc `prompt_store` + profiles + metrics) + audit helper. Test dual-driver.
2. API `/api/admin/hermes/*` (require_owner) cho roster / soul / evolve / metrics / audit. Test guest+non-owner → 401/403; owner → 200.
3. Wire `evolve_gate` vào `/evolve/*` (+ bump `knowledge_version` khi approve impact T1). Test.
4. Commander chat `/commander/ask`: orchestrator-operator với **tool đọc** (roster/metrics/evolve) + trả đề-xuất-cần-xác-nhận cho hành động. Test (mock LLM).
5. UI Vue `/admin/hermes` (4 panel + chat) — ẩn non-owner. Build pass.
6. Audit: ghi mọi POST admin vào `audit_log`. Test.

## 5. Acceptance
- Guest/non-owner KHÔNG vào được bất kỳ endpoint admin nào (401/403) — thêm vào test hồi quy privacy.
- Owner thấy roster + metrics + duyệt được 1 đề xuất evolve (→ status approved + audit).
- Chat chỉ huy trả lời "có gì chờ duyệt" bằng số liệu thật; hành động đụng não-chung **chỉ chạy sau xác nhận**.
- Sửa SOUL → ghi audit + (tuỳ) bump version.

## 6. Tham chiếu
- `docs/design/2026-06-17-H6-hermes-multi-user-thiet-ke.md` (roster, arbiter, cổng duyệt).
- `docs/design/2026-06-18-ADR-menh-ly-profile-3-tang.md` (knowledge_version).
- `engine/evolve_gate.py` · `engine/llm_spend.py` · `engine/ai/prompt_store.py` · `api/auth.require_owner`.
