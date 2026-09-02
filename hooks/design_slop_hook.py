#!/usr/bin/env python3
"""
Design AI-Slop Hook for Claude Code - companion to copy_slop_hook.py.

Scans HTML/CSS/JSX source on Write/Edit for AI-DEFAULT visual design tells and BLOCKS them.
Targets the signatures intentional brand design does NOT use, so on-brand work (cobalt/cyan,
hex borders, a real typeface, a single purposeful gradient) passes, while the AI defaults get
stopped: AI purple, the ChatGPT gradient, gradient text, glassmorphism, left-border accent
cards, the generic rgba(0,0,0,0.1) shadow, ultra-faint card outlines, decorative blur blobs,
Inter-as-default, and overgradient.

Everything here BLOCKS (2026-08-27: no warn tier). Bypass a session with DISABLE_ANTI_SLOP_HOOK=1.

Exit codes: 0 = allow, 2 = block.
"""

import json
import os
import re
import sys

DESIGN_EXTS = {".html", ".htm", ".css", ".scss", ".tsx", ".jsx", ".vue", ".svelte"}

SKIP = [
    "node_modules", "deslop/", "dist/", "build/", ".next/",
    "design-system/references/", "brand-system/references/",
]

def relevant(fp):
    if not fp or any(s in fp for s in SKIP):
        return False
    return os.path.splitext(fp)[1].lower() in DESIGN_EXTS


# (regex, message) - each match is a BLOCK.
TELLS = [
    (r"(?i)#(?:8b5cf6|a855f7|7c3aed|6d28d9|9333ea|7e22ce|c084fc|a78bfa|818cf8|6366f1)\b",
     "AI purple palette (#8b5cf6 / #a855f7 / indigo...) - the default AI accent; choose a color with brand intent"),
    (r"(?i)#(?:667eea|764ba2)\b",
     "the ChatGPT purple-blue gradient (#667eea / #764ba2) - the single most recognizable AI gradient"),
    (r"(?i)(?:-webkit-)?background-clip\s*:\s*text",
     "gradient text (background-clip: text) - a strong AI landing-page tell"),
    (r"(?i)backdrop-filter\s*:\s*blur",
     "glassmorphism (backdrop-filter: blur) - AI-default frosted glass; use a solid surface with intent"),
    (r"(?i)border-left\s*:\s*[3-8]px\s+solid",
     "left-border accent stripe (border-left: 3-8px solid) - the generic 'accent card' move"),
    (r"(?i)box-shadow\s*:[^;{}]*rgba\(\s*0\s*,\s*0\s*,\s*0\s*,\s*0?\.1\d?\s*\)",
     "the generic AI shadow rgba(0,0,0,0.1) - use a real, brand-derived shadow or none"),
    (r"(?i)border\s*:\s*1px\s+solid\s+rgba\([^)]*,\s*0?\.0[0-8]\s*\)",
     "ultra-faint hairline card border (rgba alpha <= .08) - the invisible AI card outline"),
    (r"(?i)filter\s*:\s*blur\(\s*[2-9]\dpx",
     "decorative blur blob (filter: blur >= 20px) - AI background decoration; delete it"),
    (r"(?i)filter\s*:\s*drop-shadow",
     "drop-shadow filter - AI-default depth; use a real, brand-derived shadow or none"),
    (r"(?i)font-family\s*:[^;{}]*\b(?:Inter|Geist|Space\s+Grotesk)\b",
     "Inter / Geist / Space Grotesk - the default AI UI typefaces; choose type with intent"),
    (r"(?i)\blucide(?:-react|-icons?)?\b|data-lucide",
     "Lucide icons - the default AI icon set; pick icons that fit the brand"),
    (r'(?i)class(?:Name)?\s*=\s*["\'][^"\']*\b(?:terminal|code-window|window-dots|traffic-lights?)\b',
     "fake terminal-window mockup - an overused AI landing-page prop"),
    (r"(?is)\bh[1-6]\s*(?:,[^{}]*)?\{[^{}]*border-bottom\s*:",
     "bar line under a heading (h1-h6 with border-bottom) - the AI section-divider rule; let the heading's weight and spacing carry it, no underline bar"),
    (r"(?i)<hr\b(?![^>]*\brole\s*=\s*[\"']?separator)",
     "decorative <hr> rule - AI section-divider furniture; use whitespace and heading hierarchy instead of a bar"),
]


def overgradient(content):
    n = len(re.findall(r"(?i)(?:linear|radial|conic)-gradient\(", content))
    if n >= 4:
        return [f"overgradient ({n} gradients) - gradients used as decoration; a brand uses one with purpose, not four"]
    return []


def extract(tool, ti):
    if tool == "Write":
        return ti.get("content", "")
    if tool == "Edit":
        return ti.get("new_string", "")
    if tool == "MultiEdit":
        return "\n".join(e.get("new_string", "") for e in ti.get("edits", []))
    return ""


def main():
    if os.environ.get("DISABLE_ANTI_SLOP_HOOK", "0") == "1":
        sys.exit(0)
    try:
        data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)
    tool = data.get("tool_name", "")
    ti = data.get("tool_input", {})
    if tool not in ("Write", "Edit", "MultiEdit"):
        sys.exit(0)
    fp = ti.get("file_path", "")
    if not relevant(fp):
        sys.exit(0)
    content = extract(tool, ti)
    if not content:
        sys.exit(0)

    hits = [msg for rx, msg in TELLS if re.search(rx, content)]
    hits += overgradient(content)

    if hits:
        parts = [f"Design AI-Slop BLOCKED - {len(hits)} tell(s) in {os.path.basename(fp)}:\n"]
        for m in hits[:8]:
            parts.append(f"  - {m}")
        if len(hits) > 8:
            parts.append(f"\n  ... and {len(hits) - 8} more.")
        parts.append("\nThese are AI-default visual tells. Design with brand intent. See: ~/.claude/skills/deslop/references/design-slop-patterns.md")
        print("\n".join(parts), file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
