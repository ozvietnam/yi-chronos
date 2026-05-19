# Cho Windsurf / Cline / Codex / Continue / etc.

## Windsurf

File: `.windsurfrules` at project root (hoặc User Settings → Rules)

```
[Iron Rule: Research First]
Trước mọi task technical >30 phút, BẮT BUỘC search existing open-source solutions.
Lesson 2026-05-12: MarkItDown extract PDF text 22s — user đã waste 4h build OCR pipeline.
PDF có embedded text layer — không check trước. Giả định mặc định: 90% bài toán đã có tool.

Workflow:
1. Start: "Em research 5 phút trước khi propose plan."
2. Search 4/6: GitHub stars>1k+recent, HuggingFace, Awesome lists, pip/npm, papers (arxiv 2024), Reddit/HN
3. Score top 3 (problem-fit 30% / maintenance 20% / popularity 15% / license 10% / integrate 15% / docs 10%)
   → >60 integrate, <40 build from scratch
4. Spike test 1 sample real data — đo speed, quality, errors
5. Document: 3 considered + 1 chosen + 2 reasons + 1-2 rejected + lý do
6. Build wrapper, KHÔNG from-scratch

Verified tools first:
- Document: MarkItDown (Microsoft) ⭐, Docling (IBM), MinerU, Unstructured.io, pdfminer.six, PyMuPDF
- OCR/Vision: Qwen2.5-VL ⭐, olmOCR (Allen AI), Surya, MiniCPM-V, Tesseract
- LLM gateway: OpenRouter (200+ models, free tier) ⭐, LiteLLM, Ollama (local)
- Embedding/RAG: bge-m3 (multi-lingual), nomic-embed-text, Qdrant, LanceDB
- Audio: Whisper, faster-whisper, whisper.cpp
- Web scrape/crawl: Playwright, crawl4ai, Firecrawl
- Data: Polars, DuckDB, Prefect
- Image: Real-ESRGAN
- AI Search APIs: SearXNG (self-hosted, free) ⭐ / Jina Reader (1M tok/mo free) ⭐ / Tavily (1k/mo, RAG) / Exa (semantic, 1k/mo) / Serper (Google, 2.5k/mo) / Perplexity Sonar / Brave Search / DuckDuckGo (no-key)
  Combo: SearXNG+Jina (free) | Exa+Jina (RAG agent) | Brave+Firecrawl (paid prod)

Auto-trigger: khi user nói "xây/build/implement/tạo/develop" hoặc sắp write >50 lines code mới
Red flags: "build 2 tiếng" / "không ai có sẵn" / "skip research" / "wrapper from scratch" / "không ai làm cái này"

Vietnamese reply. Code/log English. No emoji unless user.
```

## Cline (VSCode extension)

File: `.clinerules` at project root.

Same content as Windsurf above.

## Codex (OpenAI CLI)

File: `~/.codex/instructions.md` hoặc `.codex/instructions.md` per project.

Same content. Codex doc: https://github.com/openai/codex

## Continue (VSCode/JetBrains)

File: `~/.continue/config.json` → field `systemMessage` hoặc `.continuerc`.

```json
{
  "systemMessage": "Iron Rule: Research existing open-source solutions FIRST before any technical task >30min. Lesson 2026-05-12: MarkItDown 22s vs 4h OCR pipeline. Auto-trigger on 'build/implement/tạo/develop'. Search GitHub(stars>1k)/HuggingFace/Awesome/pip/arxiv/Reddit. Use AI Search APIs: SearXNG(self-hosted free)⭐ or Jina Reader(r.jina.ai, 1M tok/mo free)⭐ or Tavily/Exa/Serper/Perplexity Sonar. Score candidates >60 integrate, <40 build. Spike test 1 real sample. Document 3 considered + 1 chosen. Tool catalog: MarkItDown⭐/Qwen2.5-VL⭐/OpenRouter⭐/LiteLLM/Ollama/bge-m3/Qdrant/Whisper/faster-whisper/Playwright/crawl4ai/Firecrawl/Polars/DuckDB/Real-ESRGAN/SearXNG/Jina/Tavily/Exa. Combo free: SearXNG+Jina. Combo RAG: Exa+Jina. Vietnamese reply, English code."
}
```

## Trae AI / aider / other tools

Most have "Custom Instructions" or "System Prompt" setting. Paste the Cursor version
(shortest, most general).

## Generic pattern

Bất kỳ AI tool nào có 1 trong các field này:
- "Custom Instructions"
- "System Prompt"
- "User Rules"
- "Rules for AI"
- "AI Instructions"
- `*.rules` file
- `*.config` field

→ Paste compact version.
