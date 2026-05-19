# Session Recap — 2026-05-14

**Phiên dài nhất từ trước đến nay.** Đóng gói lại để chuyển phiên mới gọn gàng.

---

## 1. Những việc đã hoàn thành

### 1.1 Library system (engine/yi_lexicon)
- 46 sách đã đăng ký trong corpus_books (SQLite)
- Tier classification S/A/B/C đã chốt
- Text-layer classifier v5: `restore_method` field (`text_layer | pure_scan | hybrid | unknown`) + `text_layer_chars_per_page`
- LibraryView.vue + BookCard.vue + BookDetail.vue + BookReader.vue (Vue 3)
- LibrarianWizard.vue cho thêm sách mới

### 1.2 Restoration pipeline (engine/yi_lexicon/restoration)
- **MarkItDown backend**: PDF text-layer → markdown nhanh 1300x (lesson 05-12)
- **Qwen2.5-VL via Ollama**: vision OCR cho pure-scan PDF
- **Parallel dispatcher**: 8 workers, fcntl.flock LOCK_EX cho manifest/plan
- **8 providers**: zai, deepseek, anthropic, minimax, gemini, openrouter, ollama, mock
- Routing fix: minimax/openrouter/gemini không còn fall vào auto branch

### 1.3 Sách đã phục dựng (44 MB tổng)
| Sách | Pages | Method | Status |
|---|---|---|---|
| Kinh Dịch Trọn Bộ — Ngô Tất Tố | 938 | text_layer (MarkItDown) | ✅ Complete |
| Mai Hoa Dịch Số — Thiệu Khang Tiết | 672 | pure_scan (qwen-vl + LLM cleanup) | ✅ Complete |
| Học Thuyết Âm Dương Ngũ Hành — Lê Văn Sửu | 5 | text_layer | ✅ Complete |

### 1.4 Discipline system
- Skill `research-existing-solutions` cài ở `~/.claude/skills/`
- Tool catalog auto-grow `~/.claude/skills/tool-catalog.md` (30+ verified tools)
- IRON RULE #1 trong CLAUDE.md (global + project): research 5 phút TRƯỚC khi propose plan
- Multi-platform distribution `docs/discipline/` (claude-desktop, cursor, windsurf-cline-codex)

### 1.5 Wiki design (paradigm-shifted 3 lần)
Design doc `docs/design/wiki-master-apprentice.md` 14 sections, đã chốt:
- **Shift 1**: Author-Worldview-first (không concept-centric)
- **Shift 2**: Procedural grimoire (sách như công cụ hành đạo, không phải tài liệu mô tả)
- **Shift 3**: Master-Apprentice — chọn 1 thầy duy nhất là Thiệu Khang Tiết
- 8 open questions đã có answer của anh
- Schema: Author / Passage / Method / CaseStudy / Prediction / ConceptIndex
- Prediction có `interaction_log` + `tam_note` (anh tự thêm theo insight "động tâm")
- 5-tier lineage hierarchy (Tier 0 Master → Tier 5 modern descendants)

### 1.6 yi_research (GPT Researcher wrapper)
- Package `engine/yi_research/` (agent, CLI, catalog_sync, jobs, _runner)
- ResearchPanel.vue trên UI
- Apache-2.0 (27k★), wired vào 8 providers

### 1.7 Cleanup hôm nay
- `kinh-dich-tron-bo-ngo-tat-to.ocr-attempt/` → moved to `_archive/`
- `kinh-dich-tron-bo-ngo-tat-to.ocr-backup/` → moved to `_archive/`
- 59 old logs archived, kept 25 recent in `_logs/`
- Tổng restored: 44 MB

---

## 2. Lessons học được (đã ghim CLAUDE.md)

| Ngày | Lesson | Hành động |
|---|---|---|
| 05-12 | MarkItDown solve OCR trong 22s vs em build 4h | IRON RULE #1 research-first |
| 05-12 | "đa thư loạn mục" | Reset bulk parallel → sequential by lineage |
| 05-14 | "nấu cháo khái niệm" | Paradigm shift Author-Worldview-First |
| 05-14 | "hành đạo phải chọn sách chọn thầy" | Paradigm shift Master-Apprentice |
| 05-14 | "động tâm" → Prediction cần `tam_note` | Anh trực tiếp sửa schema |

---

## 3. Pending — phiên sau

### 3.1 Anh cần đưa thêm corpus Tổ sư
- `图解梅花易数.pdf` (45 MB, bản TQ Mai Hoa) — đã ở `thư viện sách/thieukhangtiet/`
- Hoàng Cực Kinh Thế 皇極經世 (Thiệu Khang Tiết, sách cốt lõi)
- Quan Vật Nội Ngoại Thiên 觀物內外篇

### 3.2 Em sẽ làm khi có corpus
1. Restore `图解梅花易数.pdf` (pure scan, qwen-vl)
2. Cross-reference VN ↔ TQ version Mai Hoa
3. Build Author/Passage/Method schema từ Mai Hoa trước (sách nhỏ, test pilot)
4. Quét mentions Thiệu Khang Tiết trong toàn corpus 46 sách (scripts/scan_master_mentions.py đã có)

### 3.3 Phase 2 (anh đọc tay)
- Anh đọc Mai Hoa VN, note `interaction_log` + `tam_note` trực tiếp
- Em support tra cứu, không tự ý interpret

### 3.4 Build Wiki proper
- **Sau khi** có full Thiệu corpus + anh đã đọc xong Mai Hoa
- Module mới: `engine/yi_wiki/`

---

## 4. Status các module

| Module | Status |
|---|---|
| `engine/yi_lexicon/` | ✅ Stable |
| `engine/yi_lexicon/restoration/` | ✅ Stable |
| `engine/ai/providers/` | ✅ 8 providers working |
| `engine/yi_research/` | ✅ Wired UI |
| `engine/yi_hermes/` | ✅ Multi-school orchestration |
| `engine/yi_wiki/` | ⏳ Chưa build, chờ corpus |
| `api/main.py` | ✅ Port 8000 |
| `client/webapp/` | ✅ Port 5173 |

---

## 5. File quan trọng cần đọc khi resume

1. `CLAUDE.md` — iron rules
2. `docs/design/wiki-master-apprentice.md` — wiki paradigm
3. `~/.claude/skills/research-existing-solutions.md` — discipline
4. `~/.claude/skills/tool-catalog.md` — verified tools
5. File này — recap state

---

**Đóng gói xong 2026-05-14. Phiên mới em chờ anh đưa sách Tổ sư.**
