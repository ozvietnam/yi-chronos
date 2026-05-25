# Workspace Dịch sách v2.0 — Design Spec

**Ngày**: 2026-05-22
**Tác giả**: Anh (CEO) + em (Claude)
**Trạng thái**: Approved, ready for implementation plan
**Liên quan**:
- IRON RULE #5 — Bookflow v2.0 (`docs/BOOKFLOW-V2.md`)
- IRON RULE #5 — Paradigm Shift #5 LAYOUT-FIRST OCR (CLAUDE.md)
- Component hiện tại: `client/webapp/src/components/publishing/PublishingWorkspace.vue` (2346 dòng)
- API hiện tại: `/api/yi-publishing/*` (api/main.py:4026+)
- MinerU wrapper hiện tại: `engine/yi_publishing/read_book.py`

---

## 1. Vấn đề

Tab **"📖 Dịch sách"** hiện chỉ là 1 workspace 3-pane editor cho 1 sách tại 1 thời điểm. Chuyển sách = dropdown. Không có:

1. **Library overview** với cover ảnh + metadata + % progress per book
2. **Add book flow** trên UI (hiện phải copy PDF vào `data/raw_pdfs/` bằng tay rồi chạy CLI)
3. **OCR job trigger** trên UI (hiện chạy `engine/yi_publishing/read_book.py` qua terminal)
4. **Job progress monitoring** (không biết MinerU đã chạy được bao nhiêu)

→ Khi anh có > 5 sách trong queue thì workflow này không scale.

---

## 2. Goals & Non-goals

### Goals
- Library Gallery cho phép thấy toàn bộ sách đang dịch trong 1 màn
- Upload PDF + register sách qua UI (không cần SSH/terminal)
- Trigger MinerU OCR job từ UI, theo dõi progress live
- Hiển thị "đang dịch tới đâu" cho từng sách (OCR % + Translation % + stage)
- Giữ nguyên paradigm "layout-first OCR" (MinerU block detection — "bắt khối ảnh")

### Non-goals (phase này)
- Cron scheduler đặt giờ chạy đêm (đợi >5 sách trong queue mới đáng)
- Multi-job OCR parallel (Mac M4 không gánh được — single job at a time)
- AI redraw cover tự động (giữ option, làm sau)
- Advanced search/filter beyond stage filter
- Drag-reorder sách trong gallery
- Webhook/email notification khi job done

---

## 3. Kiến trúc tổng — 2 màn

```
Tab "📖 Dịch sách" (App.vue routing)
│
├─ Nếu selectedBook == null → LibraryView.vue
│   ├─ Header: "📚 Thư viện dịch" + nút "➕ Thêm sách" + filter stage
│   ├─ JobBadge: "🔍 Đang OCR: Tử Vi Q1 (124/346)" (expand → panel jobs)
│   └─ Grid responsive 2/3/4 cột
│       └─ BookCard × N (click → set selectedBook → render Workspace)
│
└─ Nếu selectedBook != null → PublishingWorkspace.vue
    ├─ Header (modified): "← Về thư viện | 📖 {tựa Việt} · trang X/Y | stage badge"
    └─ 3-pane editor giữ nguyên (Editor / Compare / Auto)
```

App.vue thay đổi: tab `publishing` không render trực tiếp Workspace nữa mà render parent component (Library hoặc Workspace tuỳ state).

---

## 4. UI Components mới

### 4.1 LibraryView.vue (~400 dòng)

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ 📚 Thư viện dịch sách                  [➕ Thêm sách]         │
│ Filter: [Tất cả ▼] [⊙ Đang OCR]                              │
│                                                              │
│ 🔍 Đang OCR: Tử Vi Q1 (124/346 trang, còn ~2h)  [Chi tiết]   │
│ ─────────────────────────────────────────────────            │
│                                                              │
│ ┌─Card─┐ ┌─Card─┐ ┌─Card─┐ ┌─Card─┐                          │
│ │      │ │      │ │      │ │      │                          │
│ └──────┘ └──────┘ └──────┘ └──────┘                          │
│ ┌─Card─┐ ┌─Card─┐ ┌─Card─┐ ┌─Card─┐                          │
│ │      │ │      │ │      │ │      │                          │
│ └──────┘ └──────┘ └──────┘ └──────┘                          │
└─────────────────────────────────────────────────────────────┘
```

**State:**
- `books: ref([])` — list từ GET `/api/yi-publishing/books`
- `activeJobs: ref([])` — list từ GET `/api/yi-publishing/jobs?active=true`
- `filterStage: ref("all")` — stage filter
- `showAddModal: ref(false)`
- `showJobsPanel: ref(false)`

**Behaviors:**
- onMount: load books + activeJobs → start polling jobs mỗi 5s (clearInterval khi unmount)
- Click card → `emit('open-book', book.book_id)` → parent set selectedBook
- Filter: client-side filter `books.filter(b => filterStage === 'all' || b.stage === filterStage)`

### 4.2 BookCard.vue (~150 dòng)

**Props:** `book: Object, activeJob: Object | null`

**Layout:**
```
┌─────────────────────────────┐
│ [Cover 240×320 jpg/png]     │   ← img :src="`/api/yi-publishing/books/${id}/cover`"
│ ⠀⠀⠀⠀⠀                      │
├─────────────────────────────┤
│ 紫微斗数全书 · 卷一          │   ← hanzi_title (Trung)
│ Tử Vi Đẩu Số — Quyển 1      │   ← title_vi
│ Trần Đoàn · 35 trang        │   ← author + page_count
│                              │
│ 🏷️ Stage 5: Dịch thuật       │   ← stage_label
│                              │
│ 🔍 OCR     ████████░░  80%   │   ← progress.ocr_pct
│ ✍️ Dịch    ████░░░░░░  42%   │   ← progress.translation_pct
│                              │
│ [📖 Mở để dịch] [⋯]          │
└─────────────────────────────┘
```

**Menu `⋯` items** (dropdown):
- 🖼️ Đổi cover (upload file → PUT cover endpoint)
- 🔍 Đặt scan OCR (open OcrJobModal — pick page range, confirm)
- ✏️ Sửa metadata (open EditMetadataModal)
- 🗑️ Xoá sách (confirm + DELETE endpoint, soft delete)

**Active job state:** Nếu `activeJob != null && activeJob.book_id == book.book_id`, override OCR progress bar bằng job.progress.current/total + spinner icon.

### 4.3 AddBookModal.vue (~250 dòng)

3 bước wizard với indicator 1-2-3 trên top:

**Step 1 — Upload PDF**
- Dropzone (drag + drop hoặc click chọn)
- Validate client-side: file extension `.pdf`, size < 200MB
- Upload bằng FormData → POST `/api/yi-publishing/books/upload` (multipart)
- Backend trả `temp_id` + auto-extract metadata + thumbnail trang 1
- Progress bar khi upload (axios onUploadProgress)

**Step 2 — Metadata**
- Form auto-filled từ PDF metadata (nếu có):
  - `book_id` (slug, auto-suggest từ title, editable)
  - `title_vi` (tựa Việt) *required*
  - `hanzi_title` (tựa gốc Trung/Hán Nôm) optional
  - `author` (tác giả)
  - `year` (năm)
  - `language` (zh / vi / han-nom) *required*
  - `school` (Mai Hoa / Tử Vi / Lục Hào / Other) optional
  - `notes` (free text)
- Preview cover trang 1 ở bên phải

**Step 3 — Confirm**
- Summary + cover lớn + nút "✓ Thêm vào thư viện"
- POST `/api/yi-publishing/books/finalize` với `temp_id` + metadata → tạo entry chính thức
- Backend di chuyển PDF từ temp folder vào `data/raw_pdfs/<book_id>.pdf`, lưu cover, append vào `books.json`
- Modal close, LibraryView refresh

### 4.4 OcrJobModal.vue (~150 dòng)

Mở khi click "🔍 Đặt scan OCR" trong menu BookCard.

**Form:**
- Page range: `start` + `end` (default 1 → total_pages)
- Backend: `pipeline` (auto) / `vlm` (qwen-vl) — default `pipeline`
- Language: `ch` / `en` — default `ch`
- Estimate: "Khoảng (end-start+1) × 1.5 phút = ~Z giờ"
- Nút "🚀 Bắt đầu OCR"

POST `/api/yi-publishing/books/{id}/jobs/ocr` với payload `{start, end, backend, language}` → trả `job_id`. Modal close, JobBadge xuất hiện trên Library header.

### 4.5 JobBadge.vue (~150 dòng)

**Compact mode** (collapsed):
```
🔍 Đang OCR: Tử Vi Q1 (124/346, ~2h)  [Chi tiết ▾]
```

**Expanded panel** (click "Chi tiết"):
```
┌─ Jobs đang chạy (1) ──────────────────┐
│ 🔍 ocr-2026-05-22-abc123              │
│ Sách: Tử Vi Q1                         │
│ ████████████████░░░░  124/346 (36%)   │
│ Bắt đầu: 17:45 · ETA: 19:50           │
│ Stage: layout_detection                │
│ [📋 Log] [✕ Huỷ job]                  │
│                                        │
│ ─── Lịch sử (5 jobs gần nhất) ───      │
│ ✓ ocr-...xyz (Q3) — done, 8m45s       │
│ ✗ ocr-...def (TV-Q2) — failed         │
│ ...                                    │
└────────────────────────────────────────┘
```

Polling: parent (LibraryView) tự poll `/jobs?active=true` mỗi 5s và truyền xuống.

---

## 5. Backend changes

### 5.1 New module: `engine/yi_publishing/books_store.py` (~150 dòng)

Quản lý `data/yi_publishing/books.json` — single source of truth cho danh sách sách + metadata + progress cache.

**Schema (`books.json`):**
```json
{
  "version": 1,
  "books": [
    {
      "book_id": "tu-vi-q1",
      "title_vi": "Tử Vi Đẩu Số — Quyển 1",
      "hanzi_title": "紫微斗数全书·卷一",
      "author": "Trần Đoàn",
      "year": null,
      "language": "zh",
      "school": "tu-vi",
      "notes": "",
      "pdf_path": "data/raw_pdfs/tu-vi-q1.pdf",
      "cover_path": "data/yi_publishing/covers/tu-vi-q1.jpg",
      "cover_custom": false,
      "page_count": 35,
      "stage": 5,
      "stage_label": "Dịch thuật",
      "progress": {
        "ocr_pct": 80,
        "translation_pct": 42,
        "ocr_pages_done": 28,
        "ocr_pages_total": 35,
        "translation_lines_done": 521,
        "translation_lines_total": 1240
      },
      "created_at": "2026-05-19T08:30:00",
      "updated_at": "2026-05-22T17:45:00",
      "deleted": false
    }
  ]
}
```

**API:**
- `load_books() -> list[Book]`
- `get_book(book_id) -> Book | None`
- `add_book(metadata, pdf_path, cover_path) -> Book`
- `update_book(book_id, **fields) -> Book`
- `delete_book(book_id, soft=True)` — set `deleted: true`
- `recompute_progress(book_id)` — đọc MinerU output + translations folder, recompute progress fields

**Concurrency:** dùng `filelock` package (đã có trong requirements) hoặc `fcntl.flock` để atomic write.

### 5.2 New module: `engine/yi_publishing/jobs.py` (~200 dòng)

In-process job queue (single worker, single machine).

**State:** `data/yi_publishing/jobs.json` (persisted), `RUNNING_JOBS: Dict[job_id, threading.Thread]` (in-memory)

**Schema (`jobs.json`):**
```json
{
  "jobs": [
    {
      "job_id": "ocr-2026-05-22-abc123",
      "book_id": "tu-vi-q1",
      "type": "ocr_mineru",
      "status": "running",
      "progress": {
        "current": 124,
        "total": 346,
        "stage": "layout_detection"
      },
      "params": {
        "start_page": 1, "end_page": 346,
        "backend": "pipeline", "language": "ch"
      },
      "started_at": "2026-05-22T17:45:00",
      "ended_at": null,
      "eta_seconds": 8400,
      "error": null,
      "log_tail": ["..."]
    }
  ]
}
```

**API:**
- `submit_ocr_job(book_id, start, end, backend, language) -> job_id` — validate (chỉ 1 OCR job tại 1 lần), tạo entry, spawn `threading.Thread`
- `get_job(job_id) -> Job | None`
- `list_jobs(active=False, book_id=None) -> list[Job]`
- `cancel_job(job_id) -> bool` — set status=`cancelled`, signal thread (cooperative cancel via flag check between MinerU chunks)

**OCR runner pattern** (chunked để có progress):
- Chia page range thành chunks 10 trang
- Mỗi chunk: gọi `step2_ocr(pdf_path, book_id, chunk_start, chunk_end)` từ `read_book.py`
- Sau mỗi chunk: update `progress.current`, persist `jobs.json`, check `should_cancel` flag
- Cuối: gọi `books_store.recompute_progress(book_id)` để cập nhật stage + progress

### 5.3 API endpoints mới (api/main.py, ~400 dòng diff)

**Books CRUD:**

```python
@app.post("/api/yi-publishing/books/upload")
async def upload_book_pdf(file: UploadFile) -> dict:
    """Step 1: lưu PDF tạm vào temp folder, extract trang 1 thumbnail + auto metadata.
    Returns: temp_id, suggested_metadata, cover_temp_url"""

@app.post("/api/yi-publishing/books/finalize")
def finalize_book(req: FinalizeBookRequest) -> dict:
    """Step 3: di chuyển PDF temp → raw_pdfs/, lưu cover → covers/, append vào books.json"""

@app.get("/api/yi-publishing/books")  # MODIFIED
def list_books() -> dict:
    """Enhanced: trả cover_url, metadata đầy đủ, progress, active_job_id từ books.json."""

@app.get("/api/yi-publishing/books/{book_id}/cover")
def get_cover(book_id: str):
    """Serve cover JPG từ data/yi_publishing/covers/{book_id}.jpg"""

@app.put("/api/yi-publishing/books/{book_id}/cover")
async def upload_custom_cover(book_id: str, file: UploadFile) -> dict:
    """Override cover. Validate image type + resize 240×320."""

@app.patch("/api/yi-publishing/books/{book_id}")
def update_book_metadata(book_id: str, req: UpdateBookRequest) -> dict:
    """Update title_vi, author, notes, school, ..."""

@app.delete("/api/yi-publishing/books/{book_id}")
def delete_book(book_id: str) -> dict:
    """Soft delete: set deleted=true trong books.json. PDF không xoá."""
```

**Jobs:**

```python
@app.post("/api/yi-publishing/books/{book_id}/jobs/ocr")
def submit_ocr_job(book_id: str, req: SubmitOcrRequest) -> dict:
    """Trigger MinerU OCR job. Reject nếu đã có job OCR đang chạy."""

@app.get("/api/yi-publishing/jobs")
def list_jobs(active: bool = False, book_id: str | None = None) -> dict:
    """List jobs, filter active/book."""

@app.get("/api/yi-publishing/jobs/{job_id}")
def get_job_status(job_id: str) -> dict:
    """Single job status."""

@app.delete("/api/yi-publishing/jobs/{job_id}")
def cancel_job(job_id: str) -> dict:
    """Set cancel flag, thread checks between chunks."""
```

---

## 6. Data flow examples

### 6.1 Add new book flow

```
[User] drag PDF vào AddBookModal
  ↓
[Frontend] POST /books/upload (multipart)
  ↓
[Backend] save → /tmp/yi-publishing-uploads/{uuid}.pdf
          extract trang 1 → /tmp/.../{uuid}-cover.jpg via pdf2image
          extract metadata (pdfinfo: pages, title?, author?)
          return { temp_id, suggested: {...}, cover_url }
  ↓
[User] edit metadata trong Step 2 form
  ↓
[Frontend] POST /books/finalize { temp_id, metadata }
  ↓
[Backend] validate metadata, slugify book_id
          move /tmp/.../{uuid}.pdf → data/raw_pdfs/{book_id}.pdf
          move /tmp/.../{uuid}-cover.jpg → data/yi_publishing/covers/{book_id}.jpg
          books_store.add_book(...) → append vào books.json
          return book
  ↓
[Frontend] close modal, LibraryView refresh
```

### 6.2 Trigger OCR flow

```
[User] click ⋯ → "Đặt scan OCR" → OcrJobModal
  ↓
[User] chọn page range 1-346, click "Bắt đầu"
  ↓
[Frontend] POST /books/{id}/jobs/ocr { start: 1, end: 346, backend: 'pipeline' }
  ↓
[Backend] jobs.submit_ocr_job(...)
          validate: book exists + PDF exists + no active OCR job
          create entry trong jobs.json status=pending
          spawn threading.Thread → status=running
          return { job_id }
  ↓
[Frontend] close modal, JobBadge appears
  ↓
[Background Thread] chia 346 trang thành 35 chunks × 10 pages
          for chunk in chunks:
            if should_cancel: break
            step2_ocr(pdf, book_id, chunk_start, chunk_end)
            update jobs.json (current += 10)
          books_store.recompute_progress(book_id)
          set status=done
  ↓
[Frontend] polling /jobs?active=true mỗi 5s → progress updates → BookCard re-render
```

### 6.3 Recompute progress flow (after OCR / translation save)

```
books_store.recompute_progress(book_id):
  1. ocr_pages_done = count *_content_list_v2.json entries trong data/yi_publishing_mineru/{book_id}/{auto,ocr}/
  2. ocr_pages_total = book.page_count
  3. ocr_pct = ocr_pages_done / ocr_pages_total * 100
  4. translation_lines_done = sum lines có translation.text_vi trong data/yi_publishing/translations/{book_id}/
  5. translation_lines_total = sum tất cả lines extracted từ MinerU middle.json
  6. translation_pct = lines_done / lines_total * 100
  7. stage = derive_stage(ocr_pct, translation_pct):
       - 0% OCR → stage 1 (uploaded)
       - 0 < OCR < 100 → stage 4 (ocr-in-progress)
       - OCR=100, 0% trans → stage 4 (ocr-done)
       - 0 < trans < 100 → stage 5 (translating)
       - trans=100 → stage 6 (publish-ready)
  8. update books.json
```

---

## 7. Error handling

| Scenario | Handling |
|---|---|
| Upload PDF > 200MB | Backend reject 413, Frontend show "File quá lớn" |
| PDF corrupt / không đọc được | pdf2image throws → return 422 với message |
| `book_id` slug trùng | Reject 409, suggest alternative slug |
| OCR job chạy khi đã có 1 job khác đang chạy | Reject 409 "Đang có job OCR khác đang chạy" |
| MinerU subprocess crash | Capture stderr, set job status=failed, store last 500 chars vào job.error |
| MinerU timeout 30 phút/chunk | Catch TimeoutError, mark chunk failed, continue next chunk hoặc abort tuỳ user config |
| Server restart khi job đang chạy | jobs.json có status=running nhưng không có thread → khi list_jobs, mark zombie jobs là failed với note "Server restarted" |
| Cancel job mid-chunk | Cooperative cancel: chunk hiện tại chạy xong mới dừng (MinerU subprocess không thể kill clean giữa chừng) |
| Cover file mất | Serve placeholder SVG generic |
| books.json corrupt | Backup last good copy, restore + log error |

---

## 8. Testing strategy

### 8.1 Unit tests

**`tests/test_yi_publishing_books_store.py`**
- `test_add_book_persists_to_json`
- `test_get_book_returns_none_for_missing`
- `test_update_book_only_changes_specified_fields`
- `test_delete_book_soft_deletes`
- `test_concurrent_writes_use_lock` (spawn 2 threads writing simultaneously)
- `test_recompute_progress_empty_book` (0% OCR, 0% trans)
- `test_recompute_progress_partial_ocr` (OCR 50%, trans 0%)
- `test_recompute_progress_full_pipeline` (OCR 100%, trans 80%)
- `test_derive_stage_transitions` (test all stage transitions)

**`tests/test_yi_publishing_jobs.py`**
- `test_submit_ocr_job_creates_entry`
- `test_submit_ocr_rejects_when_active_job_exists`
- `test_list_jobs_filters_active`
- `test_cancel_job_sets_flag` (mock thread, verify cancel flag visible)
- `test_zombie_job_detected_on_restart` (write running job to json, no thread, list_jobs marks failed)

**`tests/test_yi_publishing_api.py`**
- `test_upload_book_pdf_returns_temp_id` (use TestClient + small fixture PDF)
- `test_finalize_book_moves_pdf_and_cover`
- `test_finalize_rejects_duplicate_slug`
- `test_get_books_returns_progress_fields`
- `test_get_cover_serves_jpg`
- `test_put_custom_cover_overrides`
- `test_patch_metadata_updates_fields`
- `test_delete_book_soft_deletes`
- `test_submit_ocr_endpoint_creates_job`
- `test_list_jobs_endpoint`

### 8.2 Manual QA

1. Upload PDF nhỏ test (5-10 trang) qua AddBookModal → check books.json + cover xuất hiện
2. Đặt OCR job → wait ~10 phút → check progress live + jobs.json + MinerU output
3. Click vào card → vào Workspace → translate vài dòng → save → quay về Library → check translation_pct tăng
4. Đổi cover bằng upload → verify cover thay đổi
5. Cancel OCR job mid-run → verify status=cancelled
6. Restart API server khi có job running → verify zombie detection

### 8.3 E2E (Playwright optional)

- Full flow: Add book → trigger OCR → wait done → translate 1 line → verify progress

---

## 9. Files affected

### Files mới
| File | Purpose | Est. LOC |
|---|---|---|
| `client/webapp/src/components/publishing/LibraryView.vue` | Gallery + jobs panel | ~400 |
| `client/webapp/src/components/publishing/BookCard.vue` | Single card | ~150 |
| `client/webapp/src/components/publishing/AddBookModal.vue` | 3-step wizard | ~250 |
| `client/webapp/src/components/publishing/OcrJobModal.vue` | OCR config modal | ~150 |
| `client/webapp/src/components/publishing/JobBadge.vue` | Header job badge + panel | ~150 |
| `client/webapp/src/components/publishing/EditMetadataModal.vue` | Edit metadata | ~120 |
| `engine/yi_publishing/books_store.py` | books.json CRUD + lock | ~150 |
| `engine/yi_publishing/jobs.py` | Job queue manager | ~200 |
| `tests/test_yi_publishing_books_store.py` | Unit tests | ~150 |
| `tests/test_yi_publishing_jobs.py` | Unit tests | ~150 |
| `tests/test_yi_publishing_api.py` | API tests | ~250 |

### Files modified
| File | Change |
|---|---|
| `client/webapp/src/components/publishing/PublishingWorkspace.vue` | Header: add back-button, remove book dropdown, show book title + stage badge (~50 dòng diff) |
| `client/webapp/src/App.vue` | Route logic trong tab publishing: render Library vs Workspace tuỳ state (~30 dòng diff) |
| `api/main.py` | Thêm ~10 endpoints mới cho books CRUD + jobs (~400 dòng diff). Modify list_books để return enhanced fields |

### Files KHÔNG đổi (giữ paradigm)
- 3-pane editor (regions/lines/translation) trong PublishingWorkspace.vue
- `/api/yi-publishing/pages/*`, `/regions/*` endpoints
- MinerU pipeline trong `engine/yi_publishing/read_book.py` (chỉ wrap, không sửa)

---

## 10. Dependencies

### Có sẵn (đã cài)
- `pdf2image` — extract trang 1 thumbnail (check requirements.txt)
- `Pillow` — resize cover
- `filelock` hoặc `fcntl` (stdlib) — atomic file lock
- `fastapi.UploadFile` — multipart upload
- `threading.Thread` — single worker queue
- MinerU `.venv-mineru/bin/mineru` — đã cài

### Cần check
- `pdfinfo` (poppler-utils) — extract PDF metadata. Brew install nếu chưa có.

---

## 11. Migration / backfill

Sách hiện đã có trong `data/yi_publishing_mineru/` (q3-first5, q3-pages6-15, tuvidauso-zh) cần migrate vào `books.json`:

**Migration script** (`scripts/migrate_books_to_store.py`):
1. Scan `data/yi_publishing_mineru/*/` để tìm các book_id hiện có
2. Mỗi book_id: tạo entry trong books.json với:
   - `title_vi` = book_id (placeholder, anh sửa sau)
   - `language` = "zh"
   - `pdf_path` = None (chưa có, hoặc tìm trong `data/raw_pdfs/` nếu có)
   - `cover_path` = None → render placeholder
3. recompute_progress cho từng book

Sau khi migrate, anh có thể vào UI sửa metadata + upload cover thật.

---

## 12. Open questions (đã resolve trong session)

| Q | Answer |
|---|---|
| Layout: 2 màn riêng hay sidebar hay drawer? | **2 màn riêng** (Library + Editor) |
| Cover image source? | **Auto trang 1 + cho override upload** |
| OCR scheduling pattern? | **Background queue + live progress** (single worker) |
| Progress metric trong card? | **2 progress bars (OCR + Dịch) + stage badge** |
| MinerU CLI wrapper? | Đã có ở `engine/yi_publishing/read_book.py:step2_ocr()` — em wrap thêm để spawn threading + chunk |
| books.json hay SQLite? | **books.json flat** (đơn giản, <100 sách). Migrate sang SQLite nếu vượt scale |
| Cover serve static hay API? | **API endpoint** — đồng nhất với mọi resource yi-publishing khác, dễ thêm auth/cache headers sau |

---

## 13. Timeline ước tính (cho implementation plan)

| Phase | Estimate | Deliverable |
|---|---|---|
| Backend: books_store + tests | 2-3h | books.json CRUD ổn, tests pass |
| Backend: jobs + tests | 3-4h | Job queue + cancel + zombie detection |
| Backend: API endpoints + tests | 3-4h | Upload, finalize, jobs endpoints |
| Frontend: LibraryView + BookCard | 3-4h | Gallery hiển thị đúng, click vào sách hoạt động |
| Frontend: AddBookModal | 2-3h | 3-step wizard upload + finalize |
| Frontend: OcrJobModal + JobBadge | 2-3h | Trigger OCR + progress live |
| Frontend: Workspace header update | 1h | Back button + title + stage badge |
| Migration script + manual QA | 2-3h | Migrate sách hiện có, QA E2E |
| **Total** | **~20-25h** | Ship trong 2-3 phiên làm việc |

---

## 14. Acceptance criteria

- [ ] Vào tab "📖 Dịch sách" thấy gallery cards thay vì dropdown
- [ ] Mỗi card có cover trang 1 + tựa Việt + tựa Trung + tác giả + page count + stage badge + 2 progress bars
- [ ] Bấm "➕ Thêm sách" mở wizard 3 bước, upload PDF mới → sách xuất hiện trong gallery
- [ ] Bấm menu ⋯ → "Đặt scan OCR" → mở modal config → submit → JobBadge hiện trên header với progress live
- [ ] Progress trong BookCard tăng theo từng chunk OCR
- [ ] Click card → vào Workspace 3-pane (giữ nguyên), header có "← Về thư viện"
- [ ] Bấm "← Về thư viện" quay về Library
- [ ] Dịch xong vài dòng trong Workspace → quay về Library → translation_pct tăng
- [ ] Sách hiện tại (q3-first5, tuvidauso-zh, ...) đã migrate vào books.json và hiển thị trong gallery
- [ ] Tất cả test unit + API pass
- [ ] Manual QA full flow pass

---

**Approval:** Anh đã duyệt design này trong phiên ngày 2026-05-22.
**Next step:** invoke `superpowers:writing-plans` để chốt implementation plan chi tiết (phase-by-phase).
