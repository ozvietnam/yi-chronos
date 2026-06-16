# Nghiên cứu — Kiến trúc dữ liệu user cho YI: "thấu hiểu user" + nền cho chatbot lá số

> **Ngày:** 2026-06-16 · **Người yêu cầu:** Anh (CEO).
> **Mục tiêu Anh chốt:** (1) YI **chủ động lưu trữ HẾT** data user; (2) **ngày càng hiểu user
> hơn** (tích lũy thông tin theo thời gian); (3) đích đến: **chatbot ngay trong AppChat** để
> user hỏi trực tiếp về lá số của mình.
> **Kỷ luật:** theo Iron Rule #1 (research-existing-solutions) — mọi tầng đều **dùng giải pháp
> sẵn có**, không build from scratch. Nguồn tham chiếu ở §8.

---

## 0. TL;DR (đọc trước)

1. **Chuyển store user từ SQLite (1 file/1 máy) → PostgreSQL + `pgvector`**, đặt **trong VN**.
   Một hệ Postgres lo cả: dữ liệu quan hệ + JSONB linh hoạt + vector search (RAG) + cô lập
   per-user bằng **Row-Level Security (RLS)**. Chưa cần vector DB riêng (pgvector đủ tới 5–10M vector).
2. **Thêm 3 tầng dữ liệu mới**: **event log** (append-only, ghi mọi tương tác) · **unified
   person store** (gộp 2 "sổ" đang lệch) · **memory layer** (mem0/Zep — chưng cất "hiểu biết"
   về user từ hội thoại + hành vi).
3. **Chatbot lá số = RAG**: facts mệnh lý (deterministic từ engine) + memory user + tri thức
   sách (vector) → LLM, **giữ guardrail Iron Rule #6/#8** (đọc đồng dạng, không tiên tri).
4. 🔴 **Ràng buộc pháp lý PDPL 2026 là trục thiết kế, không phải phụ lục**: data localization,
   consent chi tiết, **chuyển dữ liệu xuyên biên giới** (gọi LLM ngoài) cần hồ sơ + giảm thiểu PII,
   thông báo vi phạm 72h, phạt tới 5% doanh thu.

---

## 1. Hiện trạng & điểm đau

| Khía cạnh | Hiện tại | Vấn đề |
|---|---|---|
| Lưu trữ | SQLite file (`data/yi_users/users.sqlite3`, `persons.sqlite3`) trên **1 VPS** | Không replica, không PITR backup, khó scale ghi đồng thời, 1 điểm chết |
| Person store | **2 store lệch**: `user_persons` (sync Firebase) ⟂ `yi_hermes.persons` (Hermes) | Quiz save-result ghi sai sổ (đã ghi nhận); khó hợp nhất "chân dung user" |
| "Hiểu user" | Chỉ có birth + lịch sử cast rời rạc | KHÔNG có event log, KHÔNG memory, không tích lũy hiểu biết |
| Tri thức sách | `wiki.sqlite3` (text) — chưa vector hóa | Chatbot không retrieve được luận cứ kinh điển |
| Bảo mật | Đã từng lộ key (Iron Rule #7); chưa RLS, chưa mã hóa field nhạy cảm | Rủi ro cao với data nhạy cảm (ngày giờ sinh, suy luận tính cách) |
| Pháp lý | Chưa có tầng consent / localization / cross-border | **Vi phạm PDPL 2026** nếu để nguyên |

---

## 2. 🔴 Ràng buộc pháp lý — PDPL Việt Nam 2026 (TRỤC THIẾT KẾ)

**Luật Bảo vệ Dữ liệu Cá nhân (Luật số 91/2025/QH15)** hiệu lực **01/01/2026**, hướng dẫn bởi
**Nghị định 356/2025/NĐ-CP**. Hệ quả trực tiếp cho YI + AppChat:

| Yêu cầu | Nghĩa cho dự án |
|---|---|
| **Data localization** | AppChat là **mạng xã hội/OTT** → thuộc Luật An ninh mạng → dữ liệu user phải **lưu tại VN** + có pháp nhân/đại diện. → **Primary store đặt server VN.** |
| **Consent rõ ràng, chi tiết** (có thể bằng văn bản) | Ngày/giờ sinh + suy luận tính cách/sức khỏe từ lá số → có thể là **dữ liệu nhạy cảm/đời tư** → cần consent riêng, granular, thu hồi được. |
| **Chuyển dữ liệu xuyên biên giới** | Gọi **LLM nước ngoài** (DeepSeek/Anthropic/Gemini) với data user = chuyển dữ liệu ra ngoài VN → cần **hồ sơ đánh giá nộp Bộ Công an** + consent. 🔥 Đây là điểm nóng nhất của chatbot. |
| **Thông báo vi phạm 72h** | Cần quy trình phát hiện + báo cáo sự cố ≤ 72h. |
| **Quyền của chủ thể dữ liệu** | Phải có API **truy cập / sửa / xóa** data user (right to access/erasure). |
| **Chế tài** | Phạt tới **5% doanh thu năm** (vi phạm chuyển dữ liệu) / 10× lợi bất hợp pháp. → bảo mật là bắt buộc. |

**3 quyết sách kiến trúc rút ra:**
- **(a)** Primary user data **trong VN** (managed Postgres in-country hoặc self-host VPS VN).
- **(b)** Khi gọi LLM ngoài: **pseudonymize** (gửi lá số + facts **ẩn danh**, KHÔNG tên/sđt/email/uid thật — LLM không cần biết "ai"); + data minimization; + consent + hồ sơ chuyển dữ liệu. Ưu tiên **model in-country/self-host** (Ollama trên server VN) khi chất lượng đủ.
- **(c)** Tầng **consent + audit** là first-class, không phải gắn thêm sau.

---

## 3. Phân loại data user — "lưu hết" nghĩa là lưu những tầng nào

| Tầng | Tên | Nguồn | Ví dụ | Tính chất |
|---|---|---|---|---|
| **A** | Identity | Firebase/AppChat | uid, phone, email, display_name | Nhạy cảm, ít đổi |
| **B** | Birth facts | User nhập / quiz | ngày-giờ-nơi sinh, độ tin cậy giờ (`exact`/`approx_hour`/`unknown`), âm-dương | **Nhạy cảm** — nguyên liệu mệnh lý |
| **C** | Chart facts (suy ra) | **Engine** (deterministic) | 12 cung + sao + cục (Tử Vi), Tứ Trụ, cách cục, đại vận | Ổn định, **KHÔNG để LLM bịa** |
| **D** | Interaction log | App | đã đọc phần nào, mở chương nào, hỏi gì, gieo quẻ gì, thời lượng | Append-only → hiểu mối quan tâm |
| **E** | Feedback/verdict | User (K5) | độ khớp chân dung (correct/close/wrong/vague) per phần | Vừa validate data sinh, vừa hiệu chỉnh |
| **F** | Self-reported | User khai (chat/quiz) | nghề, hôn nhân, mối bận tâm hiện tại | Làm giàu hồ sơ |
| **G** | "Understanding"/memory | **LLM chưng cất** từ D+E+F + hội thoại | "user quan tâm sự nghiệp", "vừa đổi việc", "thích nói thẳng" | Có thể sai → cần confidence/verdict |

> **Ranh giới sống còn:** tầng **C (mệnh lý)** là *sự thật suy diễn deterministic* — chatbot phải
> lấy từ engine, tuyệt đối không để LLM tự chế sao/cung. Tầng **G (đời sống user)** là *giả định
> mềm* rút từ hội thoại — gắn độ tin, cho user đính chính (đúng tinh thần K4/K5).

---

## 4. Kiến trúc đề xuất (theo tầng)

```
            ┌──────────────────────── AppChat (Flutter, Firebase) ────────────────────────┐
            │  Identity (A)  ·  UI khai vị/chương  ·  Chatbot lá số  ·  Consent UI         │
            └───────────────▲───────────────────────────────────┬─────────────────────────┘
                            │ Cloud Functions (giấu key, X-User-Id, gate)
            ┌───────────────┴───────────────────────────────────▼─────────────────────────┐
            │                         YI-Chronos API (FastAPI, server VN)                  │
            │  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  ┌──────────────────┐  │
            │  │ Engine mệnh │  │ Memory layer │  │  RAG chatbot  │  │ Consent + Audit  │  │
            │  │ lý (C, det.)│  │ (mem0/Zep)   │  │ (retrieve+LLM)│  │ + data-subject   │  │
            │  └──────┬──────┘  └──────┬───────┘  └───────┬───────┘  └────────┬─────────┘  │
            └─────────┼────────────────┼──────────────────┼───────────────────┼────────────┘
                      ▼                ▼                  ▼                   ▼
            ┌─────────────────────────────────────────────────────────────────────────────┐
            │       PostgreSQL (trong VN) + pgvector + Row-Level Security per user_id       │
            │  users · persons(unified) · birth · charts(C, JSONB) · user_events(D log)     │
            │  feedback(E) · self_reported(F) · memory(G + embeddings) · book_corpus(vector)│
            └─────────────────────────────────────────────────────────────────────────────┘
```

### 4.1 Storage core — SQLite → PostgreSQL + pgvector (đặt VN)
- **Một** Postgres lo: quan hệ + **JSONB** (chart facts/insights linh hoạt) + **vector** (pgvector).
- **Tại sao không vector DB riêng** (Pinecone/Qdrant/Weaviate): pgvector + HNSW chạy tốt tới
  **5–10M vector**, <20ms @1M, recall >95% — thừa cho giai đoạn này; giữ embeddings **cạnh row**
  + JOIN được quyền/tenant + 1 hệ → ít moving parts, transaction nhất quán. Khi nào tới hàng tỉ
  vector / multi-region mới tính vector DB chuyên dụng.
- **Cô lập per-user bằng RLS** (Postgres Row-Level Security): policy ràng theo `user_id` ở **tầng
  DB** — kể cả lập trình viên quên filter, data vẫn không rò sang user khác. (Tuyến phòng thủ
  hậu-incident rất đáng giá.)
- **Migration**: `pgloader` (SQLite→Postgres) giữ schema bảng hiện có, thêm bảng/cột mới. `vec2pg`
  nếu sau này gom từ vector DB khác.
- **Hosting** (PDPL): managed Postgres **in-country** (VNG Cloud / Viettel / FPT / Bizfly) hoặc
  self-host trên VPS VN. (Managed → có PITR backup, đỡ vận hành.)

### 4.2 Event log (append-only) — "hiểu user theo thời gian"
- Bảng `user_events(id, user_id, type, payload JSONB, ts)` — append-only.
- Mọi callable hiện có ghi 1 event: đọc khai vị, mở chương, feedback, gieo quẻ, cast, hỏi chatbot.
- Là **nguồn raw** cho: phân tích hành vi + feed memory (G) + audit + data-subject export.

### 4.3 Unified person store — gộp 2 sổ
- Lấy `user_persons` (sync) làm **canonical user-facing**; map sang `yi_hermes.persons` qua
  `external_id` 2 chiều, hoặc hợp nhất 1 bảng `persons` có cột `namespace` (firebase | hermes).
- Khoá xuyên suốt: `firebase_uid ↔ yi user_id ↔ person`. → Hết cảnh "khoá sổ B không mở sổ A".

### 4.4 Memory layer — dùng **mem0** (hoặc Zep), KHÔNG tự build
- Biến event (D) + feedback (E) + self-reported (F) + hội thoại → **"facts" có cấu trúc** về user.
- **mem0**: 3 scope (user / session / agent), **self-editing** (user sửa → update bản ghi cũ,
  không nhân bản) — hợp consumer app. Backend **pgvector** → giữ **in-country**, không lệ thuộc SaaS ngoài.
- **Zep**: chạy **async** (ingest/embed/summarize nền, không làm chậm phản hồi) — chọn nếu cần
  trích fact + tóm tắt hội thoại quy mô lớn.
- ⚠ Memory (G) là **giả định mềm** — luôn kèm confidence + cho user đính chính; KHÔNG trộn với chart facts (C).

### 4.5 Chatbot lá số (RAG) — pipeline
Khi user hỏi *"công danh năm nay của tôi thế nào?"*:
1. **Resolve user** → load **chart facts (C)** + **memory (G)** + **birth (B)** + đại vận năm xem.
2. **Retrieve**:
   - Per-user facts (C+G): **structured**, nhỏ & chính xác → nhét thẳng context (không cần vector).
   - **Tri thức sách** (Tử Vi/Hoàng Cực/…): **vector search (pgvector)** trên `book_corpus` (migrate
     từ `wiki.sqlite3`) → lấy luận cứ kinh điển đúng sao/cung/cách cục.
3. **Compose**: chart facts + đoạn sách retrieve + memory + câu hỏi → LLM.
4. **Guardrail (Iron Rule #6/#8)**: system prompt "đọc đồng dạng · mệnh là động từ · KHÔNG tiên tri".
   Tái dùng đúng tinh thần tầng narrative 3-layer đã có (chatbot = bản hội thoại của khai vị/món chính).
5. **Ghi lại**: Q&A → event log (D) + cập nhật memory (G).
- Tận dụng được toàn bộ engine + narrative hiện có → chatbot KHÔNG phải làm lại luận giải từ đầu.

### 4.6 LLM & chuyển dữ liệu xuyên biên giới (điểm pháp lý nóng)
- **Rủi ro**: gửi data user sang LLM ngoài = cross-border transfer → hồ sơ Bộ Công an + consent.
- **Giảm thiểu**:
  - **Pseudonymize**: chỉ gửi **lá số + facts ẩn danh** (không tên/sđt/email/uid). LLM không cần danh tính.
  - **Data minimization**: chỉ gửi đúng phần liên quan câu hỏi (cung/chủ đề), không gửi cả hồ sơ.
  - **Ưu tiên in-country/self-host**: Ollama trên server VN cho phần nhạy cảm; xác minh **nơi xử lý**
    của MiniMax/provider trước khi tin là "in-country".
  - **Consent rõ ràng** cho "dùng AI + có thể chuyển dữ liệu" + log mỗi lần gọi.

### 4.7 Security & privacy (bắt buộc — hậu incident + PDPL)
- **RLS** per `user_id` ở tầng DB.
- **Mã hóa**: at-rest (disk/TDE) + in-transit (TLS); cân nhắc mã hóa field cực nhạy (birth) ở tầng app.
- **Tách secrets khỏi data** (Iron Rule #7) — DB/keys không bao giờ vào git.
- **Consent store** + **audit log** mỗi lần đọc field nhạy cảm (ai/khi nào/vì sao).
- **Data-subject API**: export + xóa toàn bộ data 1 user (right to access/erasure).
- **Backup**: Postgres **PITR** thay cho copy file SQLite. **Breach plan 72h**.

---

## 5. Lộ trình triển khai (incremental — KHÔNG big-bang)

| Phase | Việc | Đổi behavior? |
|---|---|---|
| **P0 — Nền** | Dựng Postgres in-country + pgvector + RLS. Migrate `users.sqlite3` bằng `pgloader`. Engine/API đọc-ghi Postgres. | Không (chỉ đổi backend) |
| **P1 — Event log + unified person** | Thêm `user_events`; mọi callable ghi event. Gộp 2 person store. | Nhẹ |
| **P2 — Memory layer** | Tích hợp **mem0** (backend pgvector). Distill từ D+E+F. | Thêm |
| **P3 — Vector hóa sách** | Migrate `wiki.sqlite3` → embeddings `book_corpus` (pgvector). | Thêm |
| **P4 — Chatbot** | `POST /api/tu-vi/chat` (RAG, guardrail) → callable prvchat → **UI chat trong AppChat**. | Tính năng mới |
| **P5 — Compliance hardening** | Consent UI + hồ sơ cross-border + data-subject API + breach plan. | Bắt buộc (luật đã hiệu lực) |

> P0–P1 nên làm sớm (nền + localization). P5 không để cuối cùng — **consent + localization phải có
> trước khi chatbot gửi data user sang LLM**.

---

## 6. Stack đề xuất (Iron Rule #1 — dùng sẵn, không tự viết)

| Tầng | Chọn | Thay vì tự build |
|---|---|---|
| DB + vector | **PostgreSQL + pgvector** (managed VN) | viết store/vector riêng |
| Cô lập tenant | **Postgres RLS** | filter `user_id` thủ công khắp code |
| Migration | **pgloader** (SQLite→PG), **vec2pg** | script ad-hoc |
| Memory | **mem0** (pgvector backend) · hoặc **Zep** | tự viết memory/summarizer |
| RAG | engine + narrative **sẵn có** + pgvector retrieve (LlamaIndex/LangChain chỉ khi cần) | framework nặng không cần thiết |
| Backup | Postgres **PITR** (managed) | copy file SQLite |

---

## 7. Quyết định cần Anh chốt (xem câu hỏi kèm)

1. **Hosting Postgres**: managed in-country (VNG/Viettel/FPT/Bizfly) vs self-host VPS VN.
   → *Khuyến nghị: managed in-country* (PDPL + PITR backup + đỡ vận hành).
2. **LLM cho chatbot**: chấp nhận **cross-border** (làm consent + hồ sơ Bộ Công an + pseudonymize)
   hay **ưu tiên self-host in-country** (chậm hơn / chi phí GPU)?
3. **Memory engine**: **mem0** (khuyến nghị, self-host pgvector) vs Zep vs chưa làm vội.
4. **Thứ tự ưu tiên**: làm **nền P0–P1 trước** rồi mới chatbot, hay chạy song song?

---

## 8. Nguồn tham chiếu (đã verify 2026-06)

- AI agent memory frameworks 2026 (mem0, Zep): MachineLearningMastery, Vectorize, Atlan.
- Persistent memory + user profiles cho LLM agent: arXiv 2510.07925.
- PDPL VN — Luật 91/2025/QH15 + Nghị định 356/2025 (hiệu lực 01/01/2026), localization, cross-border,
  consent, breach 72h, phạt theo doanh thu: DFDL, Tilleke & Gibbins, Vietnam-Briefing, KPMG VN, DLA Piper.
- Multi-tenant RAG trên Postgres + RLS + pgvector: Timescale/Tigerdata, Nile, Encore ("you probably
  don't need a vector database").
- pgvector quy mô startup + migration: Supabase (vec2pg), Bytebase, MakerKit.

> _Liên kết đầy đủ kèm trong tin nhắn báo cáo (chat) cùng commit này._
