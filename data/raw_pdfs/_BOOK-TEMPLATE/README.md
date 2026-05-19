# Book Template — Bookflow v2.0

**Hướng dẫn**: Copy folder này thành `<author-id>-<work-id>/` khi nạp sách mới.

## Cấu trúc

```
<book-folder>/
├── README.md              ← metadata sách (copy + edit)
├── source.pdf             ← Stage 1: file gốc
├── _TOC.md                ← Stage 2.1: mục lục đã detect
├── _READING-PLAN.md       ← Stage 2.2: priority S/A/B/C-tier
├── _TRANSLATION-PLAN.md   ← Stage 2.3: chunk + budget
├── _LLM-ROUTING.md        ← Stage 3: routing table per content type
├── pages_clean/           ← Stage 4.1: text sạch per page
├── figures_scan/          ← Stage 4.2: ảnh gốc scan
├── figures_restored/      ← Stage 4.3: ảnh phục chế
├── figures_redrawn/       ← Stage 4.4: ảnh vẽ lại
├── figures_manifest.json  ← Stage 4: mapping page → figures
├── pages_vi/              ← Stage 5: bản dịch tiếng Việt (đã QA)
└── journal.md             ← Stage 6 prep: journal thâm nhuần
```

## Workflow checklist

- [ ] Stage 1: Source PDF + metadata + copyright
- [ ] Stage 2.1: Detect TOC (auto + verify)
- [ ] Stage 2.2: Reading plan (S/A/B/C tier per chapter)
- [ ] Stage 2.3: Translation plan (chunks + budget)
- [ ] Stage 3: LLM routing table
- [ ] Stage 4.1: Clean text, STRIP all image refs from LLM cleanup
- [ ] Stage 4.2: Extract page scans
- [ ] Stage 4.3: Enhance fuzzy images
- [ ] Stage 4.4: Redraw if needed
- [ ] Stage 4.M: figures_manifest.json
- [ ] Stage 5: Translate per page + self-review + wiki cross-check
- [ ] Stage 5.QA: human spot-check 5-10%
- [ ] Stage 6: Compose + HTML + PDF + QA
- [ ] Publish to data/published/ + update LEDGER
