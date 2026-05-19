# 🎯 Universal Discipline cho TẤT CẢ Claude variants

Anh chỉ cần edit file NÀY. Mỗi khi đổi rule → em re-export ra các version dưới.

## IRON RULE — Research Existing Solutions FIRST

**Trước mọi task technical > 30 phút work**: search xem ai đã giải quyết chưa. Mặc định
giả định "có người làm rồi". Tránh phát minh lại bánh xe.

### Lesson 2026-05-12 (case study chính)

Anh giao bài toán phục chế 938 trang PDF scan. Em build OCR pipeline 4 tiếng với
qwen-vl + 8 providers parallel. Sau đó test MarkItDown (Microsoft):
- `pip install markitdown` + 22 GIÂY = extract 1.235.950 chars text
- 1300x faster, 99% quality, $0 cost
- PDF có embedded text layer ẩn — em không check trước

→ **Quy tắc: SEARCH TRƯỚC, CODE SAU.**

### Auto-trigger (tự invoke không cần anh nhắc)

Em invoke ngay khi:
- Anh nói "xây / build / implement / tạo / develop / phát triển"
- Vấn đề technical chưa giải quyết trong session
- Em định viết > 50 dòng code mới
- Em định wire 3+ libraries
- Em nghĩ "không ai làm cái này trước" → RED FLAG

### Workflow 4 phase

**Phase 0 — Articulate (1 phút)**
- WHAT: vấn đề kỹ thuật cụ thể
- CONSTRAINTS: lang, scale, cost, offline?
- SUCCESS: tiêu chí "xong"

**Phase 1 — Search 6 sources (5-10 phút). Tối thiểu 4:**
1. GitHub: `search?q=<keyword>&s=stars`. Filter stars > 1k, updated < 1 năm
2. HuggingFace: models + spaces
3. Awesome lists: `awesome <topic> github`
4. Papers + code: `<problem> arxiv 2024`
5. pip / npm registry
6. Reddit (r/MachineLearning) / HN

**AI Search tools cho Phase 1** (dùng thay Google thủ công):
- **SearXNG** (self-hosted, free, no key) — meta-search Google+Bing+DDG ⭐ best for local
- **Jina Reader** `r.jina.ai/<url>` — URL → clean markdown, 1M tokens/month free ⭐
- **Tavily** — purpose-built cho AI agents/RAG, 1k free/month (acquired Nebius 2/2026)
- **Exa** — semantic/neural search, 1k free/month, tốt cho discovery phase
- **Serper** — Google results sạch, 2.5k free/month
- **Perplexity Sonar API** — search + LLM answer + citations, 1 call
- **Brave Search API** — independent index (không phải Google/Bing), metered $5/mo
- **DuckDuckGo** — no API key, free, experimental (prototype only)

**Phase 2 — Evaluate (5 phút)**
Score mỗi candidate:
- Solves actual problem (30%)
- Active maintenance < 90 days (20%)
- Stars/downloads (15%)
- License MIT/Apache OK (10%)
- Easy integrate (15%)
- Docs (10%)

> 60/100 = integrate. < 40 = build from scratch (last resort).

**Phase 3 — Quick spike (5 phút)**
- pip install / clone
- Test với data thật, 1 sample
- Đo speed, quality, errors

**Phase 4 — Document decision (2 phút)**
- 3-5 candidates considered
- 1 chosen + 2 reasons
- 1-2 alternatives + lý do reject

### Red flags (STOP signs)

❌ "Bài này em build trong 2 tiếng" → wrong, search first
❌ "Không ai có sẵn cho project anh" → 90% có
❌ "Anh cần ngay, không research" → urgency = càng phải search nhanh
❌ "Em wrapper từ scratch" → biết wrapper around WHAT?

### Verified Tool Catalog (top picks)

**Document processing**:
- MarkItDown (Microsoft) — multi-format → markdown, ⭐ default
- Docling (IBM) — layout preserved
- MinerU — PDF + figure separation
- Unstructured.io — production
- pdfminer.six, PyMuPDF — low-level

**OCR / Vision**:
- Qwen2.5-VL — vision LLM, Asian langs ⭐
- olmOCR (Allen AI 2024) — academic docs
- Surya — multi-language + layout
- MiniCPM-V — Chinese specialist
- Tesseract — legacy baseline

**LLM gateways**:
- OpenRouter — 200+ models, free tier ⭐
- LiteLLM — proxy + cost tracking
- Ollama — local LLM runtime

**Embedding / RAG**:
- bge-m3 (multi-lingual)
- nomic-embed-text
- Qdrant, LanceDB

**Audio**: Whisper, faster-whisper, whisper.cpp
**Web scrape/crawl**: Playwright, crawl4ai, Firecrawl
**Data**: Polars, DuckDB, Prefect

**AI Search APIs** (cho research workflow + AI agent):
- SearXNG — self-hosted meta-search, free, no key, open-source ⭐ (local Mac OK)
- Jina Reader — `r.jina.ai/<url>` URL→markdown, 1M tokens/month free ⭐
- Tavily — RAG-optimized, structured snippets, 1k free/month (Nebius-owned 2026)
- Exa — neural/semantic search, 1k free/month, tốt cho discovery
- Serper — Google results, 2.5k free/month, $50/50k paid
- Perplexity Sonar API — search+LLM answer+citations in 1 call
- Brave Search API — own index độc lập, metered ~$5/mo
- DuckDuckGo — no key, free, experimental only

Recommended combos:
- 🆓 Local/free: **SearXNG + Jina Reader** (tốt nhất cho project anh, Ollama-friendly)
- 💰 Paid balanced: **Brave Search + Firecrawl** (~$128/month, 10k+10k)
- 🤖 AI agent RAG: **Exa + Jina Reader** (semantic + extraction)

(Full catalog: https://github.com/ozvietnamdesktop/yi/blob/main/docs/discipline/TOOL_CATALOG.md)

## Reminder phrase BẮT BUỘC

Em start mọi technical task với câu này:
> "Em research 5 phút xem có giải pháp sẵn không trước khi propose plan."

## When to build from scratch (sau khi research)

1. Domain quá Vietnamese-specific (vd: Can Chi, Bát Tự)
2. Tight integration với code anh
3. Tools sẵn FAIL spike test (đã thử)
4. Cost tools > cost build (rare)

Nhưng vẫn build TRÊN existing primitives (pdfminer, FastAPI, SQLite) — không reinvent low-level.
