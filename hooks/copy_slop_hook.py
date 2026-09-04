#!/usr/bin/env python3
"""
Anti AI-Slop Copy Hook for Claude Code

PreToolUse hook that validates prose content for AI writing patterns.
Complements the design-system hook (which catches UI slop in .tsx/.jsx).
This hook focuses on prose in .md, .mdx, .txt, .html, and string-heavy files.

Exit codes:
  0 = allow (no violations or non-prose file)
  2 = block (banned phrase found)
"""

import html
import json
import os
import re
import sys
from datetime import datetime

DEBUG_LOG_FILE = "/tmp/anti-slop-hook-log.txt"


def debug_log(message):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass


# File patterns to check
PROSE_EXTENSIONS = {".md", ".mdx", ".txt", ".html", ".htm"}

# Also check string-heavy source files, but only string literals
SOURCE_EXTENSIONS = {".tsx", ".jsx", ".ts", ".js", ".py"}

SKIP_PATTERNS = [
    "node_modules",
    ".env",
    "CHANGELOG",
    "LICENSE",
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    # Don't check the skill's own reference files
    "deslop/references/",
    "deslop/SKILL.md",
    "deslop/hooks/",
    "deslop/README.md",
    # Don't check design system references
    "design-system/references/",
    "brand-system/references/",
    # Don't check generated files
    ".next/",
    "dist/",
    "build/",
]

# Deployment-specific paths (a personal vault, a ledger dir, generated state) do not belong
# in the shipped list. Set DESLOP_SKIP_PATHS to a comma-separated list to append your own.
_extra_skips = os.environ.get("DESLOP_SKIP_PATHS", "")
if _extra_skips:
    SKIP_PATTERNS.extend(s.strip() for s in _extra_skips.split(",") if s.strip())

# ============================================================
# BANNED PHRASES (blocking — zero tolerance)
# ============================================================

BANNED_PHRASES = [
    # Opening/transition fluff
    (r"(?i)in\s+today'?s\s+fast[- ]paced", "banned phrase: 'in today's fast-paced...' — skip the throat-clearing, start with your point"),
    (r"(?i)in\s+the\s+ever[- ]evolving\s+landscape", "banned phrase: 'in the ever-evolving landscape' — empty opener"),
    (r"(?i)in\s+an?\s+era\s+where", "banned phrase: 'in an era where' — skip the preamble"),
    (r"(?i)without\s+further\s+ado", "banned phrase: 'without further ado' — just say the thing"),

    # The "Not X, but Y" family
    (r"(?i)(?:it'?s|this\s+is)\s+not\s+just\s+\w+[^.]{0,40}\.\s*(?:it'?s|this\s+is)\s+", "banned pattern: 'It's not just X. It's Y.' — the #1 AI tell. Rewrite as a direct statement"),
    (r"(?i)not\s+just\s+about\s+\w+[^—]*\s*—\s*it'?s\s+about", "banned pattern: 'not just about X — it's about Y' — AI reframe structure"),

    # Aspirational fluff
    (r"(?i)unlock\s+the\s+(?:power|potential)\s+of", "banned phrase: 'unlock the power/potential of' — say what it does"),
    (r"(?i)elevate\s+your\s+(?:workflow|experience|game|strategy)", "banned phrase: 'elevate your...' — be specific"),
    (r"(?i)revolutionize\s+the\s+way\s+you", "banned phrase: 'revolutionize the way you' — show, don't tell"),
    (r"(?i)seamlessly\s+integrat", "banned phrase: 'seamlessly integrate' — describe the integration"),
    (r"(?i)harness\s+the\s+power\s+of", "banned phrase: 'harness the power of' — be direct"),
    (r"(?i)take\s+(?:your|it)\s+to\s+the\s+next\s+level", "banned phrase: 'take it to the next level' — what level?"),
    (r"(?i)reimagine\s+what'?s\s+possible", "banned phrase: 'reimagine what's possible' — say what's actually possible"),

    # Redundant verbs (AI padding)
    (r"(?i)\bserves\s+as\b", "banned phrase: 'serves as' — just say 'is'"),

    # Banned words (flagged in live corrections)
    (r"(?i)\bwhack[- ]?a[- ]?mole\b", "banned: 'whack-a-mole' -- plain it out (e.g. 'each fix caused the next problem')"),

    # Sycophantic
    (r"(?i)^great\s+question!", "banned phrase: 'Great question!' — just answer it"),
    (r"(?i)^absolutely!", "banned phrase: 'Absolutely!' — forced enthusiasm"),
    (r"(?i)that'?s\s+a\s+(?:great|fantastic|excellent)\s+(?:point|question|observation)", "banned phrase: sycophantic acknowledgment — answer directly"),

    # Filler closers
    (r"(?i)(?:^|\.\s+)let\s+that\s+sink\s+in\.?$", "banned phrase: 'Let that sink in.' — trust the reader"),
    (r"(?i)(?:^|\.\s+)read\s+that\s+again\.?$", "banned phrase: 'Read that again.' — LinkedIn filler"),

    # Vague attributions (from unslop merge, 2026-08-18) — a claim with no real source is slop
    (r"(?i)\bstudies\s+show\b", "vague attribution: 'studies show' — cite the actual study or drop the claim"),
    (r"(?i)\bresearch(?:ers)?\s+(?:show|shows|suggest|suggests|indicate|indicates|have\s+found)\b", "vague attribution: 'research shows' — name the source or cut it"),
    (r"(?i)\bexperts?\s+(?:say|agree|believe|recommend)\b", "vague attribution: 'experts say' — who, specifically?"),
    (r"(?i)\bit\s+is\s+widely\s+(?:known|believed|accepted|regarded|understood)\b", "vague attribution: 'it is widely known' — by whom? say it plainly or cut"),
    (r"(?i)\b(?:many|most)\s+(?:believe|argue|would\s+agree)\b", "vague attribution: 'many believe' — name who, or state it as your own view"),
    (r"(?i)\bcritics\s+(?:argue|say|claim)\b", "vague attribution: 'critics argue' — which critics?"),

    # AI tool-remnant markers - literal ChatGPT/Gemini leakage, never acceptable (Wikipedia signs-of-AI, 2026-08-27)
    (r":?contentReference\[", "AI tool remnant: 'contentReference[' - ChatGPT artifact, delete it"),
    (r"(?i)\[oaicite:", "AI tool remnant: '[oaicite:' - ChatGPT artifact, delete it"),
    (r"\[cite:\s*\d+\]", "AI tool remnant: '[cite: N]' - Gemini artifact, delete it"),
    (r"(?i)\bturn\d+(?:file|search|news|view|image)\d+", "AI tool remnant: a 'turn0search1'-style token leaked into text, delete it"),

    # Chatbot outros / collaborative communication (Wikipedia signs-of-AI)
    (r"(?i)\bI\s+hope\s+this\s+helps\b", "chatbot outro: 'I hope this helps' - cut it"),
    (r"(?i)\b(?:feel\s+free|don'?t\s+hesitate)\s+to\s+(?:reach\s+out|ask|let\s+me\s+know|contact)", "chatbot outro: 'feel free to reach out' - cut it"),
    (r"(?i)\bif\s+you\s+have\s+any\s+(?:other\s+)?questions", "chatbot outro: 'if you have any questions' - cut it"),

    # Significance/legacy puffery (Wikipedia signs-of-AI: undue emphasis on importance)
    (r"(?i)\bstands?\s+as\s+a\s+testament\s+to\b", "puffery: 'stands as a testament to' - show it, do not proclaim it"),
    (r"(?i)\bmark(?:s|ing|ed)?\s+a\s+pivotal\s+moment\b", "puffery: 'marks a pivotal moment' - overstatement"),
    (r"(?i)\b(?:cement(?:ed|ing|s)?|solidif(?:ied|ying|ies))\s+(?:its|his|her|their)\s+(?:legacy|status|place|role|position)\b", "puffery: 'cemented its legacy/status' - AI significance-inflation"),

    # Vague / landing metaphors (2026-08-27, "here's where it lands" kind of thing)
    (r"(?i)\b(?:here'?s|there'?s|that'?s|this\s+is)\s+where\s+(?:it|that|this|things|we|they|everything|the\s+\w+)\s+(?:lands?|comes?\s+in|shines?|matters?|begins?|happens?|gets\s+\w+)\b",
     "vague landing metaphor: 'here's where it lands / comes in / shines' - say the concrete thing"),
    (r"(?i)\bwhere\s+(?:it|everything|the\s+magic|the\s+rubber)\s+(?:lands?|happens?|meets\s+the\s+road)\b",
     "dead metaphor: 'where it lands / where the magic happens / where the rubber meets the road' - name the actual thing"),
    (r"(?i)\bmoves?\s+the\s+needle\b", "dead metaphor: 'moves the needle' - state the actual effect"),
    (r"(?i)\bthe\s+missing\s+piece\b", "dead metaphor: 'the missing piece' - name what is actually missing"),
    (r"(?i)\bthe\s+right\s+lever\b", "dead metaphor: 'the right lever' - name the actual action"),
    (r"(?i)\bat\s+the\s+end\s+of\s+the\s+day\b", "filler: 'at the end of the day' - cut it, state the point"),
    (r"(?i)\bthe\s+name\s+of\s+the\s+game\b", "cliche: 'the name of the game' - say the actual priority"),
    (r"(?i)\bwhen\s+it\s+comes\s+to\b", "filler opener: 'when it comes to' - start with the point"),
]

# ============================================================
# DENSITY-FLAGGED WORDS (warning — tracked across full content)
# ============================================================

TIER1_WORDS = [
    "delve", "utilize", "spearhead", "bolster", "underscore", "endeavor",
    "foster", "harness", "streamline", "leverage", "pivotal", "multifaceted",
    "holistic", "meticulous", "nuanced", "invaluable", "groundbreaking",
    "tapestry", "synergy", "paradigm", "underpinnings", "linchpin",
    "cornerstone", "catalyst", "nexus", "realm",
]
TIER1_THRESHOLD = 1  # per 500 words

TIER2_WORDS = [
    "transformative", "comprehensive", "crucial", "dynamic", "compelling",
    "innovative", "vibrant", "profound", "ecosystem", "trajectory",
    "furthermore", "moreover", "consequently", "notably", "indeed",
    "additionally", "conversely", "nevertheless",
    # Tech-metaphor nouns. AI reaches for these to sound operator-fluent.
    # Density-flagged rather than banned: "rails" is also a real framework
    # and a playbook is a real document.
    "rails", "rail", "playbook", "flywheel", "moat", "primitives",
]
TIER2_THRESHOLD = 2  # per 500 words

# ============================================================
# STRUCTURAL PATTERNS (warning)
# ============================================================

EM_DASH = "—"
EM_DASH_MAX_PER_300_WORDS = 1

FILLER_TRANSITIONS = [
    r"(?i)^furthermore[,.]",
    r"(?i)^moreover[,.]",
    r"(?i)^it'?s\s+worth\s+noting\s+that",
    r"(?i)^it\s+is\s+important\s+to\s+note\s+that",
    r"(?i)^in\s+conclusion[,.]",
    r"(?i)^(?:and\s+)?that\s+matters\.?$",
    r"(?i)^and\s+honestly\??$",
]

# ============================================================
# BLOCKING: curly quotes, Title Case headings, bold overuse (added 2026-08-18)
# ============================================================

CURLY_QUOTES = {"“", "”", "‘", "’"}  # " " ' '

# Small words that a Title Case heading capitalizes mid-line but sentence case + proper nouns never do.
# A capitalized one of these (not as the first word) is an unambiguous Title-Case tell with ~no false positives.
TITLE_CASE_SMALL = {
    "a", "an", "the", "and", "or", "nor", "but", "of", "to", "in", "on", "at",
    "by", "for", "with", "from", "as", "vs", "via", "into", "onto", "over",
}

# ============================================================
# BLOCKING: explainer furniture in headings (added 2026-09-02)
#
# A title that names the thing, then glosses the ARTIFACT rather than the subject:
# "The system, in two pictures". The gloss describes the format ("in two pictures",
# "at a glance", "explained", "a primer") and carries no information the body does not.
# Deliberately narrow: a plain comma in a heading is legitimate and common (dates,
# "X, or Y?" decision framings), so only the gloss shapes below block.
# ============================================================

# Nouns that describe the ARTIFACT rather than the subject. "in three weeks" is a
# schedule and stays legal; "in three charts" is a format gloss and blocks.
FORMAT_NOUNS = (
    r"pictures?|charts?|graphs?|images?|slides?|numbers?|words?|lines?|minutes?|"
    r"steps?|bullets?|paragraphs?|tables?|screenshots?|diagrams?|acts?|parts?|points?"
)

EXPLAINER_HEADINGS = [
    (r"(?i),\s+in\s+(?:a|an|one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+(?:" + FORMAT_NOUNS + r")\s*$",
     "explainer gloss heading: ', in N <format>' - the title already names the thing; drop the gloss"),
    (r"(?i),?\s+at\s+a\s+glance\s*$",
     "explainer gloss heading: 'at a glance' - drop it; the content is the glance"),
    (r"(?i),\s+explained\s*$",
     "explainer suffix heading: ', explained' - the body is the explanation; drop the label"),
    (r"(?i),\s+a\s+primer\s*$",
     "explainer suffix heading: ', a primer' - drop it and name the subject"),
    (r"(?i)^(?:a\s+)?primer\s+on\s+\S",
     "explainer suffix heading: 'a primer on X' - just name X"),
    (r"(?i)[a-z]\s+101\s*$",
     "explainer suffix heading: 'X 101' - drop the 101; name what it covers"),
    (r"(?i)^what\s+(?:this|that|it)\s+means\s+for\s+you\s*$",
     "explainer heading: 'what this means for you' - say what it means in the body"),
    (r"(?i),\s+and\s+wh(?:y|at)\s+it\s+(?:matters|means)\s*$",
     "why-it-matters tail: ', and why it matters' - if it matters, the body shows it"),
    (r"(?i)^why\s+it\s+matters\s*$",
     "why-it-matters heading: state the stake itself, not that there is one"),
]

# ============================================================
# BLOCKING: density (added 2026-09-02)
#
# Two mechanical forms of overexplaining. RESTATEMENT is the same point twice in a
# row; THROAT-CLEARING is an abstract opener before any substance (dictionary calls
# this "The Warm-Up Problem" - the first 40% of AI content).
# ============================================================

# Tuned against a 648-file corpus. Parallel enumeration (two ticket rows, ToS vs privacy
# policy, "Sprint Planning" vs "Sprint Review") shares scaffolding and topped out at 0.83
# overlap; genuine restatement reuses nearly every word and scores 0.9 to 1.0. Anything
# below 0.9 blocked legitimate parallel lists, so 0.9 is the floor.
#
# Known limit: this catches near-verbatim repeats only. The synonym form ("The system is
# fast." / "It is quick.") scores ~0.2 and is invisible here - that one stays a judgment
# tell for the review gate.
RESTATEMENT_MIN_CONTENT_WORDS = 5   # below this, overlap is noise
RESTATEMENT_OVERLAP = 0.9           # share of the shorter unit's content words

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "than", "that", "this", "these",
    "those", "is", "are", "was", "were", "be", "been", "being", "am", "do", "does", "did",
    "have", "has", "had", "will", "would", "can", "could", "should", "may", "might", "must",
    "of", "to", "in", "on", "at", "by", "for", "with", "from", "as", "into", "onto", "over",
    "under", "about", "after", "before", "between", "through", "during", "without", "within",
    "it", "its", "we", "our", "you", "your", "they", "their", "he", "she", "his", "her",
    "not", "no", "so", "up", "out", "off", "down", "just", "only", "also", "more", "most",
    "which", "what", "when", "where", "who", "whom", "how", "why", "there", "here", "all",
    "any", "each", "both", "some", "such", "one", "two", "very", "much", "many", "still",
}

# WARN: wordy phrases, false ranges, AI disclaimers (from unslop merge, 2026-08-18).
# Warnings, not blocks — these are context-dependent (a real range or a genuine "because" is fine).
WEAK_PHRASES = [
    (r"(?i)\bdue\s+to\s+the\s+fact\s+that\b", "wordy: 'due to the fact that' -> 'because'"),
    (r"(?i)\bin\s+order\s+to\b", "wordy: 'in order to' -> 'to'"),
    (r"(?i)\bat\s+(?:this|that)\s+point\s+in\s+time\b", "wordy: 'at this point in time' -> 'now'"),
    (r"(?i)\ba\s+(?:large|small)\s+number\s+of\b", "wordy: 'a large/small number of' -> 'many'/'few'"),
    (r"(?i)\bin\s+the\s+event\s+that\b", "wordy: 'in the event that' -> 'if'"),
    (r"(?i)\bfor\s+the\s+purpose\s+of\b", "wordy: 'for the purpose of' -> 'to'"),
    (r"(?i)\bhas\s+the\s+ability\s+to\b", "wordy: 'has the ability to' -> 'can'"),
    (r"(?i)\beverything\s+from\s+\w+\s+to\s+\w+", "false range: 'everything from X to Y' -- list the real items or cut"),
    (r"(?i)\bbased\s+on\s+the\s+(?:information|data)\s+(?:provided|available)\b", "AI disclaimer: 'based on the information provided' -- just answer"),
    (r"(?i)\bit\s+appears\s+that\b", "hedge: 'it appears that' -- say what is, or name the uncertainty concretely"),
    # --- unslop merge 2, added 2026-08-27: weak copulas, empty -ing tails, abstract jargon ---
    (r"(?i)\b(?:serves|stands)\s+as\b", "weak copula: 'serves/stands as' -- just say what it is ('is', 'runs', 'handles')"),
    (r"(?i)\bboasts\b", "puffery verb: 'boasts' -- use a plain verb ('has', 'includes')"),
    (r"(?i),\s+(?:highlighting|showcasing|underscoring|emphasizing|reflecting|ensuring|demonstrating)\s+", "empty -ing tail: ', highlighting/ensuring...' -- start a new sentence with the concrete point"),
    (r"(?i)\b(?:substrate|nexus|paradigm|flywheel|north\s+star)\b", "abstract jargon-as-technical -- name the concrete thing instead"),
    # --- Wikipedia signs-of-AI merge, 2026-08-27 ---
    (r"(?i)\bin\s+connection\s+with\b", "vague connection: 'in connection with' -- use a direct preposition (about, for, with)"),
    (r"(?i)\b(?:prioriti|emphasi|favou?r)\w*\s+[\w-]+\s+rather\s+than\s+[\w-]+", "negative parallelism: '...ing X rather than Y' -- state it plainly"),
    (r"[?&]utm_source=", "copied-from-web tell: 'utm_source=' in a URL -- strip campaign tracking params"),
]


def is_prose_file(file_path):
    if not file_path:
        return False
    if any(skip in file_path for skip in SKIP_PATTERNS):
        return False
    ext = os.path.splitext(file_path)[1].lower()
    return ext in PROSE_EXTENSIONS


def is_source_file(file_path):
    if not file_path:
        return False
    if any(skip in file_path for skip in SKIP_PATTERNS):
        return False
    ext = os.path.splitext(file_path)[1].lower()
    return ext in SOURCE_EXTENSIONS


def extract_string_literals(content):
    """Extract string literals from source code for slop checking."""
    strings = []
    # Match quoted strings (both single and double), handling escapes
    for match in re.finditer(r'(?:"([^"\\]*(?:\\.[^"\\]*)*)"|\'([^\'\\]*(?:\\.[^\'\\]*)*)\')', content):
        s = match.group(1) or match.group(2)
        if s and len(s) > 20:  # only check non-trivial strings
            strings.append(s)
    return "\n".join(strings)


def check_banned_phrases(content):
    """Check for zero-tolerance banned phrases. Returns list of (line_num, message)."""
    violations = []
    lines = content.split("\n")

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("<!--"):
            continue

        for pattern, msg in BANNED_PHRASES:
            if re.search(pattern, stripped):
                violations.append((i, f"[BLOCK] {msg}"))
                break  # one violation per line

    return violations


def check_word_density(content):
    """Check for AI-flagged words at excessive density. Returns list of warnings."""
    warnings = []
    words = content.lower().split()
    word_count = len(words)

    if word_count < 50:  # too short to judge density
        return warnings

    blocks_of_500 = max(1, word_count / 500)

    # Tier 1
    for word in TIER1_WORDS:
        count = sum(1 for w in words if w.strip(".,;:!?\"'()") == word)
        if count > TIER1_THRESHOLD * blocks_of_500:
            warnings.append(f"[DENSITY] '{word}' appears {count}x in {word_count} words — strong AI signal (Tier 1)")

    # Tier 2
    for word in TIER2_WORDS:
        count = sum(1 for w in words if w.strip(".,;:!?\"'()") == word)
        if count > TIER2_THRESHOLD * blocks_of_500:
            warnings.append(f"[DENSITY] '{word}' appears {count}x in {word_count} words — moderate AI signal (Tier 2)")

    return warnings


def check_em_dash_density(content):
    """Check for excessive em dash usage."""
    words = content.split()
    word_count = len(words)
    em_dash_count = content.count(EM_DASH)

    if word_count < 50:
        return []

    blocks_of_300 = max(1, word_count / 300)
    if em_dash_count > EM_DASH_MAX_PER_300_WORDS * blocks_of_300:
        return [f"[STRUCTURE] {em_dash_count} em dashes in {word_count} words — max {EM_DASH_MAX_PER_300_WORDS} per 300 words. Use commas or periods instead."]

    return []


def check_filler_transitions(content):
    """Check for AI filler transitions."""
    warnings = []
    lines = content.split("\n")

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        for pattern in FILLER_TRANSITIONS:
            if re.search(pattern, stripped):
                warnings.append((i, f"[FILLER] Line starts with AI filler transition — cut it and start with the point"))
                break

    return warnings


def check_paragraph_uniformity(content):
    """Check if paragraphs are suspiciously uniform in length."""
    # Split into paragraphs (double newline separated)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", content) if p.strip()]
    # Filter to actual prose paragraphs (not headings, lists, code blocks)
    prose_paragraphs = [
        p for p in paragraphs
        if not p.startswith("#")
        and not p.startswith("-")
        and not p.startswith("*")
        and not p.startswith("`")
        and not p.startswith("|")
        and len(p.split()) > 10
    ]

    if len(prose_paragraphs) < 4:  # need enough paragraphs to judge
        return []

    word_counts = [len(p.split()) for p in prose_paragraphs]
    avg = sum(word_counts) / len(word_counts)

    if avg == 0:
        return []

    # Check if all are within 15% of average
    within_range = sum(1 for c in word_counts if abs(c - avg) / avg < 0.15)
    if within_range >= len(word_counts) * 0.8:  # 80%+ paragraphs are uniform
        return [f"[STRUCTURE] {within_range}/{len(word_counts)} paragraphs are within 15% of {int(avg)} words — AI-level uniformity. Vary paragraph length for human rhythm."]

    return []


def check_weak_phrases(content):
    """WARN: wordy phrases, false ranges, AI disclaimers. Returns (line_num, msg)."""
    warnings = []
    for i, line in enumerate(content.split("\n"), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("<!--"):
            continue
        for pattern, msg in WEAK_PHRASES:
            if re.search(pattern, stripped):
                warnings.append((i, f"[WEAK] {msg}"))
                break
    return warnings


def check_curly_quotes(content):
    """BLOCK: smart/curly quotes - use straight ASCII."""
    violations = []
    for i, line in enumerate(content.split("\n"), 1):
        if any(c in line for c in CURLY_QUOTES):
            violations.append((i, "[BLOCK] curly/smart quotes — use straight ASCII quotes (\" and ')"))
    return violations


def check_title_case_headings(content):
    """BLOCK: a markdown heading in Title Case (a small word Capitalized mid-heading)."""
    violations = []
    for i, line in enumerate(content.split("\n"), 1):
        m = re.match(r"^\s*#{1,6}\s+(.+)", line)
        if not m:
            continue
        words = m.group(1).split()
        for w in words[1:]:  # skip the first word (sentence case caps it too)
            core = re.sub(r"[^A-Za-z]", "", w)
            if core.lower() in TITLE_CASE_SMALL and core[:1].isupper():
                violations.append((i, "[BLOCK] Title Case heading — use sentence case (capitalize only the first word + proper nouns)"))
                break
    return violations


def check_bold_overuse(content):
    """BLOCK: bold peppered through a flowing prose paragraph (decoration, not emphasis).
    Skips label-led lines (starting with ** or a list/heading/table marker) — those are legit style."""
    violations = []
    for para in re.split(r"\n\s*\n", content):
        p = para.strip()
        if not p or p.startswith(("#", "-", "*", "|", "`", ">")):
            continue
        bolds = len(re.findall(r"\*\*[^*\n]+\*\*", p))
        sentences = len(re.findall(r"[.!?](?:\s|$)", p))
        if bolds >= 4 and sentences >= 2 and len(p.split()) >= 40:
            violations.append((0, f"[BLOCK] bold overused ({bolds} bold spans in one prose paragraph) — bold is for rare emphasis, not decoration"))
    return violations


def check_bold_lead_paragraph(content):
    """BLOCK: the 'bold title. then body' paragraph tell (2026-08-28).
    A bold fragment used as a sentence-title, period-terminated, then body prose in the
    same paragraph — e.g. '**Evidence boundary.** A format-valid timestamp confirms...'.
    Scoped to a PERIOD-terminated bold lead so it does NOT hit '**Label:** value' lines
    (colon, used in memory files) or ordinary mid-sentence emphasis."""
    violations = []
    patterns = [
        r"\*\*[^*\n]{2,70}\.\*\*\s+[A-Z0-9]",   # **Title.** Body
        r"\*\*[^*\n]{2,70}\*\*\.\s+[A-Z0-9]",   # **Title**. Body
        r"<strong[^>]*>[^<]{2,70}\.</strong>\s+[A-Z0-9]",   # <strong>Title.</strong> Body
        r"<strong[^>]*>[^<]{2,70}</strong>\.\s+[A-Z0-9]",   # <strong>Title</strong>. Body
    ]
    for i, line in enumerate(content.split("\n"), 1):
        for pat in patterns:
            if re.search(pat, line):
                violations.append((i, "[BLOCK] bold-lead paragraph ('**Title.** then body') - an AI tell; drop the bold pseudo-title, just write the sentence"))
                break
    return violations


def check_middot_separator(content):
    """BLOCK: spaced middot separator ' · ' used as connective tissue (2026-08-28).
    An AI tell in copy ('Jan · Jul', 'DBM · Open Gov'). Use a plain word, comma, or line break."""
    violations = []
    for i, line in enumerate(content.split("\n"), 1):
        if re.search(r"\s·\s", line):
            violations.append((i, "[BLOCK] ' · ' middot separator - an AI tell; use a word, comma, or separate line"))
    return violations


def extract_content(tool_name, tool_input):
    if tool_name == "Write":
        return tool_input.get("content", "")
    elif tool_name == "Edit":
        return tool_input.get("new_string", "")
    elif tool_name == "MultiEdit":
        edits = tool_input.get("edits", [])
        return "\n".join(edit.get("new_string", "") for edit in edits)
    return ""


def _heading_texts(content):
    """Yield (line_num, heading_text) for markdown # headings and HTML <h1-h6>."""
    for i, line in enumerate(content.split("\n"), 1):
        m = re.match(r"^\s*#{1,6}\s+(.+?)\s*$", line)
        if m:
            yield i, m.group(1).strip()
            continue
        for hm in re.finditer(r"(?is)<h[1-6][^>]*>(.*?)</h[1-6]>", line):
            text = re.sub(r"(?s)<[^>]+>", "", hm.group(1))
            text = html.unescape(text).strip()
            if text:
                yield i, text


def check_explainer_headings(content):
    """BLOCK: a heading that glosses the artifact instead of naming the subject."""
    violations = []
    for i, text in _heading_texts(content):
        # Strip trailing markdown emphasis/punctuation that would hide an end anchor.
        probe = text.rstrip("*_`#").rstrip()
        for pattern, msg in EXPLAINER_HEADINGS:
            if re.search(pattern, probe):
                violations.append((i, f"[BLOCK] {msg}"))
                break
    return violations


def _content_words(text):
    """Lowercased meaningful tokens: drops stopwords, punctuation, and short words.

    Numbers, dates and identifiers are KEPT and never length-filtered. Parallel rows in
    a log or ledger share their scaffolding and differ only in the values ("Aug 20" vs
    "Aug 22", one ticket key vs another); dropping those values made distinct entries
    look identical and was the main source of false positives.
    """
    tokens = re.findall(r"[A-Za-z][A-Za-z'-]*|\d[\w.:/-]*", text.lower())
    out = set()
    for t in tokens:
        if any(ch.isdigit() for ch in t):
            out.add(t)
        elif len(t) > 3 and t not in STOPWORDS:
            out.add(t)
    return out


# A line carrying this many tags is markup, not prose. Minified HTML puts a whole
# page on one line, and splitting that on sentence punctuation compares fragments of
# markup rather than sentences.
MARKUP_TAG_LIMIT = 3


def _strip_code_and_tables(content):
    """Drop fenced code blocks, markdown table rows, and markup-heavy lines.

    All three repeat by design: a table restates its column shape every row, a code
    block restates its idiom, and a minified HTML line is not prose at all.
    """
    out, in_fence = [], False
    for line in content.split("\n"):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append("")
            continue
        if in_fence or line.lstrip().startswith("|"):
            out.append("")
            continue
        if len(re.findall(r"<[a-zA-Z/!][^>]*>", line)) >= MARKUP_TAG_LIMIT:
            out.append("")
            continue
        out.append(line)
    return "\n".join(out)


def _split_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def check_restatement(content):
    """BLOCK: two adjacent sentences or bullets that make the same point twice.

    Compares content-word sets. Adjacent only - a callback to something said three
    paragraphs up is legitimate; the same point restated immediately is padding.
    """
    violations = []
    cleaned = _strip_code_and_tables(content)
    lines = cleaned.split("\n")

    units = []  # (line_num, text)

    # Adjacent bullets at the same nesting level.
    run = []
    for i, line in enumerate(lines, 1):
        m = re.match(r"^(\s*)(?:[-*+]|\d+[.)])\s+(.+)", line)
        if m:
            indent = len(m.group(1))
            if run and run[-1][0] == indent:
                units.append((run[-1][1], run[-1][2], i, m.group(2)))
            run = [(indent, i, m.group(2))]
        elif line.strip():
            run = []

    for prev_line, prev_text, cur_line, cur_text in units:
        a, b = _content_words(prev_text), _content_words(cur_text)
        if len(a) < RESTATEMENT_MIN_CONTENT_WORDS or len(b) < RESTATEMENT_MIN_CONTENT_WORDS:
            continue
        overlap = len(a & b) / min(len(a), len(b))
        if overlap >= RESTATEMENT_OVERLAP:
            violations.append((cur_line, "[BLOCK] restatement: this bullet repeats the previous one's point - say it once"))

    # Adjacent sentences inside a prose paragraph.
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", cleaned) if p.strip()]
    for para in paragraphs:
        if para.startswith(("#", "-", "*", "`", "|", ">")):
            continue
        sentences = _split_sentences(para)
        for s1, s2 in zip(sentences, sentences[1:]):
            a, b = _content_words(s1), _content_words(s2)
            if len(a) < RESTATEMENT_MIN_CONTENT_WORDS or len(b) < RESTATEMENT_MIN_CONTENT_WORDS:
                continue
            overlap = len(a & b) / min(len(a), len(b))
            if overlap >= RESTATEMENT_OVERLAP:
                line_no = 0
                for i, line in enumerate(content.split("\n"), 1):
                    if s2[:40] in line:
                        line_no = i
                        break
                violations.append((line_no, "[BLOCK] restatement: this sentence repeats the previous one - delete it"))
    return violations


def main():
    if os.environ.get("DISABLE_ANTI_SLOP_HOOK", "0") == "1":
        sys.exit(0)

    try:
        raw_input = sys.stdin.read()
        input_data = json.loads(raw_input)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    if tool_name not in ["Edit", "Write", "MultiEdit"]:
        sys.exit(0)

    file_path = tool_input.get("file_path", "")

    # Determine what to check
    content = extract_content(tool_name, tool_input)
    if not content:
        sys.exit(0)

    # For source files, only check string literals
    if is_source_file(file_path):
        content = extract_string_literals(content)
        if not content:
            sys.exit(0)
    elif not is_prose_file(file_path):
        sys.exit(0)

    # HTML entities hide slop from the character-based checks: &mdash; (and &#8212; / &#x2014;)
    # is an em dash, &middot; a middot, &rsquo; a curly quote. Decode them so encoded slop
    # blocks exactly like a literal character would. (2026-08-28: a deck slipped em dashes as
    # &mdash; past this gate because the scan only saw the literal codepoint.)
    if is_prose_file(file_path) and os.path.splitext(file_path)[1].lower() in {".html", ".htm"}:
        content = html.unescape(content)

    # Run checks
    banned = check_banned_phrases(content)
    curly = check_curly_quotes(content)
    titlecase = check_title_case_headings(content)
    bold = check_bold_overuse(content)
    boldlead = check_bold_lead_paragraph(content)
    middot = check_middot_separator(content)
    explainer = check_explainer_headings(content)
    restate = check_restatement(content)
    # EVERYTHING BLOCKS (2026-08-27: "everything should just block, no need for warn"). The former
    # warn tier (density, em dash, filler transitions, weak copulas / -ing tails / wordy / false ranges) is now
    # blocking. Two deliberate calls: (1) the paragraph-uniformity heuristic is DROPPED, not promoted - blocking
    # a write because "paragraphs are similar length" false-positives on every structured doc. (2) em dashes now
    # block on ANY occurrence (he bans them outright), not just past a density threshold.
    density_blocks = [(0, w) for w in check_word_density(content)]
    filler_blocks = [(w[0], w[1]) if isinstance(w, tuple) else (0, w) for w in check_filler_transitions(content)]
    weak_blocks = check_weak_phrases(content)
    emdash_blocks = []
    if EM_DASH in content:
        emdash_blocks = [(0, f"[BLOCK] em dash present ({content.count(EM_DASH)}x) - banned outright; use a hyphen, comma, or period")]

    all_blocks = (banned + curly + titlecase + bold + boldlead + middot + explainer
                  + restate + weak_blocks + density_blocks + emdash_blocks + filler_blocks)

    if all_blocks:
        parts = [f"AI Slop BLOCKED — {len(all_blocks)} pattern(s) in {os.path.basename(file_path)}:\n"]
        for line_num, msg in all_blocks[:8]:
            parts.append(f"  Line ~{line_num}: {msg}")
        if len(all_blocks) > 8:
            parts.append(f"\n  ... and {len(all_blocks) - 8} more.")
        parts.append("\nRewrite without these AI patterns. See: ~/.claude/skills/deslop/references/copy-slop-dictionary.md")
        debug_log(f"BLOCKED: {file_path} — {len(all_blocks)} patterns")
        print("\n".join(parts), file=sys.stderr)
        sys.exit(2)

    debug_log(f"PASSED: {file_path}")
    sys.exit(0)


if __name__ == "__main__":
    main()
