# 🎯 Discipline Distribution — Cài 1 lần, dùng khắp nơi

Anh có nhiều AI tool/IDE. Discipline "research-first" cần apply NHẤT QUÁN.
Folder này chứa version riêng cho mỗi platform.

## TL;DR — Anh làm gì?

Mở từng platform anh dùng, paste content từ file tương ứng:

| Platform | File | Where to paste |
|---|---|---|
| **Claude Code CLI** (terminal) | `~/.claude/CLAUDE.md` + `~/.claude/skills/*` | ✅ Em đã setup xong |
| **Claude Desktop** (app/web) | `claude-desktop.md` | Settings → Profile → Custom Instructions |
| **Cursor IDE** | `cursor.md` | `.cursorrules` file OR Settings → Rules for AI |
| **Windsurf** | `windsurf-cline-codex.md` | `.windsurfrules` file |
| **Cline** (VSCode ext) | `windsurf-cline-codex.md` | `.clinerules` file |
| **Codex** (OpenAI CLI) | `windsurf-cline-codex.md` | `~/.codex/instructions.md` |
| **Continue** | `windsurf-cline-codex.md` | `~/.continue/config.json` |
| **Trae AI** | `cursor.md` (compact) | Settings → Custom Instructions |

## Master = single source

File `MASTER.md` là source-of-truth. Khi anh muốn update discipline:

1. Edit `MASTER.md`
2. Em re-export ra các file platform khác (Claude Desktop, Cursor, ...)
3. Anh re-paste vào mỗi tool

## Workflow paste (1 lần setup, dùng lâu)

```
1. Mở Claude Desktop → Settings → paste `claude-desktop.md`
2. Cursor → Settings or .cursorrules → paste `cursor.md`
3. Windsurf → .windsurfrules → paste `windsurf-cline-codex.md`
4. (Other tools tương tự)
```

Sau khi paste, **mọi AI tool sẽ behave NHẤT QUÁN**:
- Research existing solutions trước
- Check tool catalog
- Spike test trước commit
- Document decisions
- Trả lời tiếng Việt

## Project-level vs Global

| Layer | Apply scope |
|---|---|
| Global (User Settings / `~/.claude/`) | All projects, mọi session |
| Project (`.cursorrules`, `.windsurfrules` in project root) | Chỉ project đó |

Em recommend: **paste vào Global** cho convenience. Override per-project chỉ khi cần.

## Update routine

Khi em phát hiện tool mới đỉnh (vd: replacement cho MarkItDown):
1. Em update `MASTER.md` knowledge base
2. Em re-export 3 platform files
3. Anh chỉ cần paste lại (5 phút all platforms)

## File tree

```
docs/discipline/
├── README.md                       ← anh đang đọc
├── MASTER.md                       ← single source-of-truth
├── claude-desktop.md               ← Claude Desktop app/web
├── cursor.md                       ← Cursor IDE
└── windsurf-cline-codex.md         ← Windsurf, Cline, Codex, Continue, Trae, etc.
```

## Bonus — Verify discipline works

Test prompt cho mỗi tool sau khi paste:

```
"Anh muốn build hệ thống transcribe audio podcast tiếng Việt sang text."
```

Behaviour đúng:
1. AI start với: "Em research 5 phút trước khi propose plan."
2. Search Whisper, faster-whisper, etc.
3. Score candidates
4. Spike test 1 sample
5. Propose plan với justification
6. Trả lời tiếng Việt

Behaviour sai (cần re-check paste):
- ❌ Jump thẳng vào code
- ❌ Trả lời English
- ❌ Không mention any tool name
- ❌ Generic plan không reference real packages
