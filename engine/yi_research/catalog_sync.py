"""Auto-sync tool mentions từ research report → tool catalog.

Workflow:
1. Parse markdown report → extract candidate tool mentions
2. Diff với existing tool-catalog.md → find tools chưa biết
3. Generate entry skeletons "🆕 to-investigate"
4. Append vào catalog (interactive mode) hoặc dry-run

Tool detection heuristics:
- GitHub URLs: `github.com/<owner>/<repo>` → tool name = repo
- Markdown bold/italic: `**ToolName**`, `*ToolName*` in patterns
- pip/npm references: `pip install <name>`, `npm install <name>`
- Capitalized CamelCase trong context "use X for", "library X"

Em không AI-classify aggressive — chỉ extract candidates, anh manually verify.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse


_CATALOG_PATH = Path.home() / ".claude" / "skills" / "tool-catalog.md"


@dataclass
class ToolMention:
    """1 tool mentioned trong report."""
    name: str                              # 'MarkItDown', 'GPT Researcher', etc.
    canonical: str = ""                    # lowercase, normalized for dedupe
    github_url: str | None = None
    pip_name: str | None = None
    npm_name: str | None = None
    context: str = ""                      # surrounding text snippet
    sources: list[str] = field(default_factory=list)  # where mentioned in report

    def __post_init__(self):
        if not self.canonical:
            self.canonical = self.name.lower().strip()


# ─── Extraction ─────────────────────────────────────────────────────────────


# GitHub URL pattern: github.com/owner/repo
_GITHUB_RE = re.compile(
    r"(?:https?://)?github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)",
    re.IGNORECASE,
)

# pip install pattern
_PIP_RE = re.compile(
    r"pip\s+install\s+(?:-U\s+)?['\"]?([a-zA-Z0-9][a-zA-Z0-9_.\-]+)(?:\[[^\]]*\])?['\"]?",
    re.IGNORECASE,
)

# npm install pattern
_NPM_RE = re.compile(
    r"npm\s+install\s+(?:-g\s+)?([a-zA-Z0-9@][a-zA-Z0-9_/.\-]+)",
    re.IGNORECASE,
)

# Bold tool names in context — em conservative ở đây
_BOLD_TOOL_RE = re.compile(r"\*\*([A-Z][A-Za-z0-9_.\-]{2,30})\*\*")


def extract_tools_from_report(markdown: str) -> list[ToolMention]:
    """Parse markdown research report → list of candidate tool mentions.

    Strategy:
    1. GitHub URLs → repo name = tool name (highest confidence)
    2. pip/npm install commands → package name
    3. Bold names in context → candidates (lower confidence)
    4. Dedupe by canonical name, merge sources
    """
    mentions: dict[str, ToolMention] = {}

    # 1. GitHub URLs
    for m in _GITHUB_RE.finditer(markdown):
        owner, repo = m.group(1), m.group(2)
        repo_clean = repo.rstrip(".").rstrip(",").rstrip(")")
        canonical = repo_clean.lower()
        # Skip common non-tool repos
        if canonical in {"docs", "examples", "tutorial", "blog", "awesome"}:
            continue
        full_url = f"https://github.com/{owner}/{repo_clean}"
        # Use repo name as candidate tool name (capitalize for display)
        display = repo_clean.replace("-", " ").replace("_", " ")
        existing = mentions.get(canonical)
        if existing:
            if full_url not in (existing.sources or []):
                existing.sources.append(full_url)
            if not existing.github_url:
                existing.github_url = full_url
        else:
            mentions[canonical] = ToolMention(
                name=repo_clean, canonical=canonical,
                github_url=full_url, sources=[full_url],
                context=_grab_context(markdown, m.start(), 100),
            )

    # 2. pip install candidates
    for m in _PIP_RE.finditer(markdown):
        pkg = m.group(1).lower()
        if pkg in {"pip", "setuptools", "wheel"}:
            continue
        if pkg in mentions:
            mentions[pkg].pip_name = m.group(1)
        else:
            mentions[pkg] = ToolMention(
                name=m.group(1), canonical=pkg, pip_name=m.group(1),
                context=_grab_context(markdown, m.start(), 80),
            )

    # 3. npm install candidates
    for m in _NPM_RE.finditer(markdown):
        pkg = m.group(1).lower()
        if pkg in mentions:
            mentions[pkg].npm_name = m.group(1)
        else:
            mentions[pkg] = ToolMention(
                name=m.group(1), canonical=pkg, npm_name=m.group(1),
                context=_grab_context(markdown, m.start(), 80),
            )

    return list(mentions.values())


def _grab_context(text: str, idx: int, length: int = 80) -> str:
    """Grab ±length/2 chars around index for context."""
    start = max(0, idx - length // 2)
    end = min(len(text), idx + length // 2)
    return text[start:end].replace("\n", " ").strip()


# ─── Catalog diff ───────────────────────────────────────────────────────────


def load_catalog_tools(catalog_path: Path | None = None) -> set[str]:
    """Read tool-catalog.md → return set of canonical tool names em đã biết."""
    path = catalog_path or _CATALOG_PATH
    if not path.exists():
        return set()
    text = path.read_text(encoding="utf-8")
    # Catalog entries dạng "### ToolName · category"
    entries = re.findall(r"^###\s+([^\n·]+?)(?:\s+·.*)?$", text, re.MULTILINE)
    return {e.strip().lower() for e in entries}


def find_new_tools(
    mentions: list[ToolMention], catalog_path: Path | None = None,
) -> list[ToolMention]:
    """Filter mentions xuống chỉ tools chưa có trong catalog."""
    known = load_catalog_tools(catalog_path)
    new_tools: list[ToolMention] = []
    for m in mentions:
        # Check multiple variants
        canonical_variants = {
            m.canonical,
            m.canonical.replace("-", ""),
            m.canonical.replace("_", ""),
            m.canonical.replace("-", " "),
        }
        if any(v in known for v in canonical_variants):
            continue
        # Skip if name contains in any known name (substring match)
        is_known = False
        for k in known:
            if m.canonical in k or k in m.canonical:
                is_known = True
                break
        if not is_known:
            new_tools.append(m)
    return new_tools


# ─── Entry generation ───────────────────────────────────────────────────────


def format_catalog_entry(tool: ToolMention) -> str:
    """Generate skeleton entry cho catalog (markdown). Em mark 'to-investigate'."""
    lines = [f"### {tool.name} · 🆕 to-investigate"]
    if tool.github_url:
        lines.append(f"- **Repo**: {tool.github_url}")
    if tool.pip_name:
        lines.append(f"- **Install**: `pip install {tool.pip_name}`")
    if tool.npm_name:
        lines.append(f"- **Install**: `npm install {tool.npm_name}`")
    if tool.context:
        lines.append(f"- **What**: {tool.context}")
    lines.append("- **Verified**: chưa — auto-extracted từ research report")
    lines.append("- **Verdict**: pending review")
    return "\n".join(lines)


def propose_additions(new_tools: list[ToolMention]) -> str:
    """Generate markdown block to append vào catalog (review section)."""
    if not new_tools:
        return ""
    import time
    header = f"\n\n<!-- ─── Auto-discovered {time.strftime('%Y-%m-%d %H:%M')} ─── -->\n\n"
    body = "\n\n".join(format_catalog_entry(t) for t in new_tools)
    return header + body + "\n"


def append_to_catalog(
    new_tools: list[ToolMention], catalog_path: Path | None = None,
) -> Path:
    """Append new tools vào catalog under 'Auto-discovered' section."""
    path = catalog_path or _CATALOG_PATH
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Tool Catalog\n\n", encoding="utf-8")
    block = propose_additions(new_tools)
    if block:
        with path.open("a", encoding="utf-8") as f:
            f.write(block)
    return path


# ─── Top-level orchestration ────────────────────────────────────────────────


def sync_from_report(
    report_markdown: str,
    *,
    catalog_path: Path | None = None,
    apply: bool = False,
    verbose: bool = True,
) -> dict:
    """Full workflow: extract → diff → optionally append.

    Args:
        report_markdown: research report text
        catalog_path: defaults to ~/.claude/skills/tool-catalog.md
        apply: if True, append new tools vào catalog. If False, dry-run.
        verbose: print summary

    Returns: {extracted, new, applied, catalog_path}
    """
    extracted = extract_tools_from_report(report_markdown)
    new = find_new_tools(extracted, catalog_path)

    if verbose:
        print(f"🔍 Extracted {len(extracted)} tool mentions")
        print(f"🆕 New tools (not in catalog): {len(new)}")
        for t in new[:10]:
            url = t.github_url or t.pip_name or t.npm_name or "?"
            print(f"   - {t.name:30s} ({url})")

    result = {
        "extracted": [t.name for t in extracted],
        "new": [t.name for t in new],
        "applied": False,
        "catalog_path": str(catalog_path or _CATALOG_PATH),
    }

    if apply and new:
        path = append_to_catalog(new, catalog_path)
        result["applied"] = True
        if verbose:
            print(f"✓ Appended {len(new)} tools to {path}")
            print(f"  Open file để verify + edit 'to-investigate' entries")

    return result
