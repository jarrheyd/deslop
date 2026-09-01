#!/usr/bin/env python3
"""
Artifact AI-Slop Hook - extends the deslop gate to artifacts that do NOT touch the
local filesystem and so bypass copy_slop_hook.py / design_slop_hook.py.

Targets: Google Docs / Slides / Sheets created through the Drive connector
(mcp__<id>__create_file, which carries the body inline as textContent / base64Content /
html), and the built-in Artifact tool (which publishes from a local file_path).

It reuses the existing copy + design hooks by re-emitting the artifact body as a
synthetic Write payload and piping it through both. If either blocks, this blocks.

Everything BLOCKS (no warn tier). Bypass a session with DISABLE_ANTI_SLOP_HOOK=1.
Exit codes: 0 = allow, 2 = block. Any internal error exits 0 (never break a tool call).
"""

import base64
import json
import os
import subprocess
import sys

HOOK_DIR = os.path.dirname(os.path.abspath(__file__))
COPY = os.path.join(HOOK_DIR, "copy_slop_hook.py")
DESIGN = os.path.join(HOOK_DIR, "design_slop_hook.py")

# Only scan tools that produce a shippable prose/visual artifact from inline content
# or a file. Matched loosely so the connector's per-session UUID does not matter.
def is_artifact_tool(name):
    n = name or ""
    if n == "Artifact":
        return True
    return n.startswith("mcp__") and n.endswith(("__create_file", "__update_file"))


def pick_ext(mime, fallback=".html"):
    m = (mime or "").lower()
    if "html" in m:
        return ".html"
    if "markdown" in m or m.endswith("/md"):
        return ".md"
    if "plain" in m or "text" in m:
        return ".txt"
    return fallback


def extract(tool, ti):
    """Return (text, ext) for the artifact body, or (None, None) to skip."""
    # Built-in Artifact tool: content lives in a local file (already Write-gated,
    # but re-check here so a hand-placed file still gets caught).
    if tool == "Artifact":
        fp = ti.get("file_path")
        if fp and os.path.isfile(fp):
            try:
                with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read(), os.path.splitext(fp)[1].lower() or ".html"
            except OSError:
                return None, None
        return None, None

    # Drive connector create_file / update_file
    mime = ti.get("contentMimeType") or ti.get("mimeType")
    if ti.get("textContent"):
        return ti["textContent"], pick_ext(mime)
    if ti.get("content") and not ti.get("base64Content"):
        # deprecated create_file 'content' is base64; try decode, else treat as text
        raw = ti["content"]
        try:
            dec = base64.b64decode(raw, validate=True).decode("utf-8", "ignore")
            if dec.strip():
                return dec, pick_ext(mime)
        except Exception:
            return raw, pick_ext(mime)
    if ti.get("base64Content"):
        m = (mime or "").lower()
        if not any(k in m for k in ("html", "text", "markdown", "md")):
            return None, None  # binary (image/pdf/font) - nothing to slop-check
        try:
            dec = base64.b64decode(ti["base64Content"]).decode("utf-8", "ignore")
            return dec, pick_ext(mime)
        except Exception:
            return None, None
    if ti.get("html"):
        return ti["html"], ".html"
    return None, None


def run(hook_path, text, ext):
    payload = json.dumps({
        "tool_name": "Write",
        "tool_input": {"file_path": f"artifact{ext}", "content": text},
    })
    try:
        p = subprocess.run(
            ["python3", hook_path],
            input=payload, capture_output=True, text=True, timeout=8,
        )
        return p.returncode, (p.stderr or p.stdout or "").strip()
    except Exception:
        return 0, ""


def main():
    if os.environ.get("DISABLE_ANTI_SLOP_HOOK", "0") == "1":
        sys.exit(0)
    try:
        data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool = data.get("tool_name", "")
    if not is_artifact_tool(tool):
        sys.exit(0)
    ti = data.get("tool_input", {}) or {}

    text, ext = extract(tool, ti)
    if not text or not text.strip():
        sys.exit(0)

    blocks = []
    for hook in (COPY, DESIGN):
        code, msg = run(hook, text, ext)
        if code == 2 and msg:
            blocks.append(msg)

    if blocks:
        sys.stderr.write(
            "Artifact AI-Slop BLOCKED before creating the artifact (deslop gate):\n\n"
            + "\n\n".join(blocks)
            + "\n\nFix the copy/design, then create the doc. Bypass a session with "
              "DISABLE_ANTI_SLOP_HOOK=1.\n"
        )
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
