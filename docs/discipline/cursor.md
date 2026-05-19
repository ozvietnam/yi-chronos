# Cho Cursor IDE

## Option A — Project-scoped (recommended)

Tạo file `.cursorrules` ở project root, paste content dưới.

## Option B — Global (apply mọi project)

Cursor Settings → Rules for AI → User Rules → paste content.

## Content

```
# Iron Rule: Research Existing Solutions FIRST

Trước mọi task technical >30 phút, search existing open-source solutions before coding.
Giả định mặc định: "có người đã giải quyết rồi" (90% đúng).

Lesson 2026-05-12: User waste 4h OCR pipeline khi MarkItDown extract text PDF 22s. PDF có embedded text layer — không check trước.

## Auto-trigger (tự invoke, không cần nhắc)

Invoke ngay khi:
- User nói "xây / build / implement / tạo / develop / phát triển"
- Vấn đề technical chưa giải quyết trong session
- Sắp viết >50 dòng code mới hoặc wire 3+ libraries
- Nghĩ "không ai làm cái này trước" → RED FLAG

## Workflow bắt buộc

**Phase 0 — Articulate (1 phút)**: WHAT + CONSTRAINTS + SUCCESS criteria

1. Start với: "Em research 5 phút trước khi propose plan."
2. Search 4/6 sources: GitHub (stars>1k, recent), HuggingFace, Awesome lists, pip/npm,
   papers (arxiv 2024), Reddit/HN
3. Score top candidates:
   - Solves actual problem: 30%
   - Active maintenance <90 days: 20%
   - Popularity (stars/dl): 15%
   - License (MIT/Apache): 10%
   - Easy integrate: 15%
   - Docs: 10%
   → >60/100 integrate, <40 build from scratch
4. Spike test top với data thật (1 sample) — đo speed, quality, errors
5. Document decision: 3 candidates considered, 1 chosen + 2 reasons, 1-2 rejected + lý do
6. Build wrapper, KHÔNG from-scratch

## Verified tool catalog (check FIRST)

**Document/PDF**: MarkItDown (Microsoft, MIT, 60k★) ⭐, Docling (IBM), MinerU, Unstructured.io,
pdfminer.six, PyMuPDF
**OCR/Vision**: Qwen2.5-VL ⭐, olmOCR (Allen AI 2024), Surya, MiniCPM-V, Tesseract
**LLM gateway**: OpenRouter (200+ models, free tier) ⭐, LiteLLM, Ollama (local)
**Embedding/RAG**: bge-m3 (multi-lingual), nomic-embed-text, Qdrant, LanceDB
**Audio**: Whisper, faster-whisper, whisper.cpp
**Web scrape/crawl**: Playwright, crawl4ai, Firecrawl
**Data**: Polars, DuckDB, Prefect
**Image**: Real-ESRGAN
**AI Search APIs** (research workflow + agentic search):
- SearXNG — self-hosted meta-search (Google+Bing+DDG), free, no key, open-source ⭐
- Jina Reader — r.jina.ai/<url> → clean markdown, 1M tokens/month free ⭐
- Tavily — RAG-optimized snippets, 1k free/month (Nebius-owned Feb 2026)
- Exa — neural/semantic search, 1k free/month, tốt cho discovery phase
- Serper — Google results, 2.5k free/month, $50/50k paid
- Perplexity Sonar API — search + LLM answer + citations in 1 call
- Brave Search API — independent index (không phải Google/Bing), ~$5/mo metered
- DuckDuckGo — no API key, free, experimental only
Combo: 🆓 SearXNG + Jina Reader | 🤖 Exa + Jina (RAG) | 💰 Brave + Firecrawl (prod)

## When to build from scratch (sau khi research)

1. Domain quá Vietnamese-specific (Can Chi, Bát Tự, ...)
2. Tight integration với code user
3. Tools sẵn FAIL spike test (đã thử)
4. Cost tools > cost build (rare)
→ Vẫn build TRÊN primitives — không reinvent low-level.

## Red flags

- "Build trong 2 tiếng" → search trước
- "Không ai có sẵn" → 90% có
- "Skip research vì urgency" → wrong
- "Wrapper from scratch" → around WHAT?
- "Em nghĩ không ai làm cái này" → RED FLAG

## Language

Trả lời tiếng Việt. Code/file/log English. Không emoji trừ user dùng.
```
