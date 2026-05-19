# Next Session Plan — sau 2026-05-14

**Anh mở phiên mới → em đọc file này đầu tiên.**

---

## 🎯 Mục tiêu phiên mới

Xây **YI-Wiki module** (Master-Apprentice Digital Twin của Thiệu Khang Tiết) — nhưng **CHỜ corpus Tổ sư đầy đủ** trước khi viết code.

---

## ⏸️ Điều kiện đầu phiên (anh kiểm tra)

### Kịch bản A — Anh đã có thêm corpus Tổ sư
Nếu anh đưa được 1 trong 3 cuốn dưới đây:
- `图解梅花易数.pdf` (đã có sẵn, restore trước)
- Hoàng Cực Kinh Thế 皇極經世
- Quan Vật Nội Ngoại Thiên 觀物內外篇

→ Em làm theo Workflow A bên dưới.

### Kịch bản B — Chưa có thêm corpus
→ Em không build Wiki. Em chỉ làm 1 trong các việc support:
- Restore `图解梅花易数.pdf` (đã có file, 45MB, pure scan)
- Quét mentions Thiệu trong 46 sách (`scripts/scan_master_mentions.py`)
- Cross-reference VN Mai Hoa ↔ TQ Mai Hoa khi có TQ
- Đọc Mai Hoa VN cùng anh (Phase 2 — anh đọc tay, em tra cứu)

→ Em **KHÔNG** tự ý build code mới khi chưa có data thật.

---

## 🛠 Workflow A — Khi đủ corpus

### Bước 1: Restore corpus mới
```bash
# 图解梅花易数 (đã có)
.venv/bin/python -m engine.yi_lexicon.restoration \
  --book "图解梅花易数" --provider auto --backend qwen-vl
```

### Bước 2: Build schema cho yi_wiki
```
engine/yi_wiki/
├── __init__.py
├── models.py        # Author, Passage, Method, CaseStudy, Prediction, ConceptIndex
├── store.py         # SQLite tables
├── ingest.py        # Parse restored .md → Passage/Method extraction
├── lineage.py       # 5-tier hierarchy logic
└── api.py           # FastAPI routes
```

**Schema không tự sáng tác — copy nguyên từ `wiki-master-apprentice.md` § 5-8.**

### Bước 3: Pilot với Mai Hoa VN
- Sách nhỏ (672 trang), đã restored
- Extract ~50 Passage đầu tiên thủ công + em assist
- Anh duyệt từng cái — KHÔNG bulk

### Bước 4: Cross-reference VN ↔ TQ
- Sau khi có TQ Mai Hoa
- Anchor: chương/quẻ tên gốc Hán
- Conflict → ghi lại, anh duyệt

### Bước 5: Vue UI MasterView.vue
- Sau khi schema + data ổn định
- KHÔNG build UI trước data

---

## 🚫 Anti-pattern em phải tránh

| Anti-pattern | Lý do |
|---|---|
| Build `engine/yi_wiki/` khi chưa có Hoàng Cực + Quan Vật | Schema sẽ lệch khi data thật vào |
| Auto-extract Passage từ tất cả 46 sách | "Đa thư loạn mục" — anh đã cấm |
| Concept-centric extraction | Vi phạm Paradigm Shift 1 |
| Multi-school equal weight | Vi phạm Paradigm Shift 3 |
| Skip research-existing-solutions skill | Vi phạm IRON RULE #1 |
| Tự ý đọc/interpret Mai Hoa | Phase 2 là anh đọc, em chỉ support |

---

## 📋 Resume checklist (em chạy đầu phiên)

```
[ ] Đọc CLAUDE.md (iron rules)
[ ] Đọc SESSION-RECAP-2026-05-14.md (state)
[ ] Đọc wiki-master-apprentice.md (paradigm)
[ ] Đọc NEXT-SESSION-PLAN.md (file này)
[ ] Hỏi anh: "Anh đã có thêm corpus Tổ sư chưa?"
[ ] Theo kịch bản A hoặc B
[ ] KHÔNG viết code đầu tiên — confirm scope với anh trước
```

---

## 🎓 Một câu nhắc em

> "Hành đạo phải chọn sách chọn thầy."
> Anh đã chọn Thiệu Khang Tiết.
> Em không được dụ dỗ build feature em thấy hay nhưng anh không cần.

---

**Plan đóng gói 2026-05-14. Phiên mới mở file này.**
