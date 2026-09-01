# Deslop Skill — Copy Quality Gate

A quality gate that catches AI-generated writing before it ships: the words, phrases, and structures that read as machine-written. Primary use is copy and prose, which is what the auto-hook, the humanizer, and the detector all target. It also keeps slop catalogs for UI, images, social, video, and websites as a secondary checklist, but for interface and visual-design work, reach for the impeccable skill instead.

This is not a style guide. It's a bullshit detector.

## Why This Exists

"Slop" was Merriam-Webster's 2025 Word of the Year. It means AI-generated content that's technically competent but soulless, generic, and statistically average. The root cause: AI outputs converge toward the mean of training data, producing the most probable output every time. A fintech hero section looks identical to a project management tool's. A LinkedIn post reads like every other LinkedIn post. An AI headshot has the same plastic skin as every other AI headshot.

The antidote is not "don't use AI." It's **specificity, intentionality, and human fingerprints.**

## Activation

### 1. PreToolUse Hook (Automatic)

`hooks/copy_slop_hook.py` runs on every Write/Edit to files containing prose: `.md`, `.mdx`, `.txt`, `.tsx`/`.jsx` (string literals), `.html`. It catches:

| Signal | What's Caught | Action |
|--------|--------------|--------|
| Banned words (high density) | "delve," "leverage," "tapestry," "synergy," "holistic" at >1 per 500 words | **Warn** |
| Banned phrases | "In today's fast-paced," "It's not just X, it's Y," "Unlock the power of" | **Block** |
| Em dash abuse | More than 1 em dash per 300 words | **Warn** |
| Sycophantic openers | "Great question!", "Absolutely!", "I love that idea!" | **Block** |
| Hedging soup | "On one hand... on the other hand" in same paragraph | **Warn** |
| Uniform paragraph length | All paragraphs within 15% of same word count | **Warn** |
| Filler transitions | "Furthermore," "Moreover," "It's worth noting that" | **Warn** |
| Rhetorical-question pile-ups | Two or three short questions stacked with no answer ("Top? Bottom? Both?") | **Block** |
| Two-word wisdom closers | "Worth it.", "It tracks.", "Math checks out." as final lines | **Warn** |
| Inline section-headers in prose | "The question:" / "The setup:" / "The result:" used as pseudo-headers | **Warn** |
| Hyphenated-compound titles | "the-position-of-the-rule test", "the-AI-that-can-promote-itself" — over-compounded noun phrases | **Warn** |
| "Not X. Not Y." rhythm | Three-beat negation ladders ("Not 95. Not 98. Fifty for fifty.") | **Warn** |
| Generic abstract metaphors | "wherever it lives", "the right lever", "the missing piece", "moves the needle" | **Warn** |
| Either-or reductive framing | "Either it matches or it doesn't.", "Either X or Y." used to compress a finding | **Warn** |
| Triple-comma cadence | "specific, careful, deliberate" / three adjectives in series with no fourth | **Warn** |
| "Honestly" / "Genuinely" tics | Used as opening words for emphasis | **Block** |
| "Real talk" / "I'll be honest" | Manufactured-candor openers | **Block** |
| "X but make it Y" framing | The TikTok-aphorism pattern | **Block** |
| "Hits different" | The 2022 phrase that's now AI's favorite | **Block** |
| "Operationalize" / "frameworks" / "moats" | Tech-bro abstraction words | **Warn** |
| "It came back null" / "It came back X" | Passive AI-result-rhythm | **Warn** |

Set `DISABLE_ANTI_SLOP_HOOK=1` to bypass.

**Artifact gate (`hooks/artifact_slop_hook.py`, added 2026-08-31).** The two hooks above only see local file writes, so a Google Doc / Slides / Sheet created straight through the Drive connector, or a published Artifact, used to slip past. This hook closes that gap: it fires on `Artifact` and any `mcp__*__create_file` / `mcp__*__update_file`, pulls the body out of `textContent` / `base64Content` / `html` (or the Artifact's `file_path`), and runs it back through the copy and design hooks. Any block there blocks the artifact. Binary uploads (image/pdf/font) and empty/native-shell creates are no-ops. Same `DISABLE_ANTI_SLOP_HOOK=1` bypass. Note: hooks load at session start, so it protects new sessions; mid-session, self-gate by running the checks before create_file.

### 2. Manual Invocation

Use `/deslop` or ask Claude to run a slop check on any content.

### 3. Cross-Skill Integration

The design-system and brand-system skills both reference this skill. Their workflows include an anti-slop check before shipping.

## Jarrhey-observed tells (2026-07, from live draft-vs-sent corrections)

Patterns caught in real usage — his actual sent messages vs AI drafts. These outrank the generic lists when writing AS Jarrhey or FOR his review:

1. **Em dashes: banned outright** in his output, not just "abuse at density." Inline separator is a plain hyphen " - ". (Global rule, all mediums.)
2. **Over-committing language.** AI drafted "locked 300 characters"; he sent "Proposing 300." Drafts must never commit him (or Symph) harder than verified facts: cover what's agreed, ASK the clarifying question ("Are those the 2 sessions you meant?"), never blanket-approve money/scope.
3. **Sectioned essays where numbered questions suffice.** His pushback is 2-3 numbered questions, not 4 headed sections. ALL-CAPS asterisk headers = tell; his real headers are bold sentence-case ("How we'll work"), and only when an email truly needs them.
4. **Compression that drops substance.** Cutting a real point to be short is a loss (the dropped-signatories lesson). Target: his length, the draft's completeness.
5. **Promise-language vs act-language.** AI writes "I'll loop in Flor"; he writes "I have already informed Flor." Act first, then reference the action.
6. **Doom warnings and public assignments in client chat.** Strip alarmism; open questions and offers, not directives naming who must do what in front of the client.
7. **Report verbosity.** Reports to him: fragments over grammar, no preamble, lead with the outcome. Repeating the ask back = slop.
8. **Duplicate artifacts.** Revising by creating a second draft/file and leaving the old one = slop workflow. Revise in place, one clean artifact.
9. **Fake completion language.** "Done/created/sent" without a tool having run. If you didn't see the tool response, it didn't happen.
10. **Bold-lead paragraph (2026-08-28).** A bold fragment used as a pseudo-title, then body prose in the same paragraph -- "**Evidence boundary.** A format-valid timestamp confirms...". Classic AI carousel/marketing tell. Drop the bold pseudo-title; just write the sentence. (Enforced in the hook, period-terminated bold only, so legit `**Label:** value` lines still pass.)
11. **Middot separators (2026-08-28).** " · " used as connective tissue ("Jan · Jul", "DBM · Open Gov"). An AI tell. Use a word, a comma, or a line break. (Enforced in the hook.)
12. **Carousel/slide furniture tells (2026-08-28).** Page-number dots ("1/10", pagination dots), upper-right kicker/eyebrow labels, and per-slide section titles all read as AI-generated deck slop. No page numbers, no eyebrow labels, no "The problem:" pseudo-headers -- let the headline carry the point.
13. **Over-titling / over-repeating (2026-08-28).** Adding a label to a slide that the headline already says, repeating the same footer descriptor on every frame, or restating the credit line twice on one slide. Say it once, in one place.
14. **Bar line under a heading (2026-08-31).** A colored horizontal rule under every section heading -- `h2{border-bottom:2px solid ...}` in CSS, an `<hr>`, or the `---` a heading border becomes when HTML converts to a Google Doc. Reads as AI section-divider furniture. Let the heading weight and the whitespace carry the break, no underline bar. (Enforced in `design_slop_hook.py`: h1-h6 with `border-bottom`, and decorative `<hr>`.)

## Post-implementation review gate (MANDATORY)

After EVERY implementation — a feature, a document, a proposal, a design, copy, a UI — run this skill as a review BEFORE presenting the result:

1. Sweep the deliverable's user-facing surfaces: copy/microcopy, docs, UI choices, generated designs, commit-adjacent prose.
2. Apply the Universal Slop Test + the Jarrhey-observed tells above + the relevant domain reference.
3. High-stakes (client-facing, published, in his voice) → full slop-detector agent pass.
4. Violations get FIXED, then present — never presented with a "note: might be sloppy" caveat.

This gate is part of the global feature-development protocol (`~/.claude/CLAUDE.md`): audit → research → plan → implement → test → fix → **slop review** → done.

## The Three Laws

1. **Specific > Generic.** If you can swap in another brand's name and the content still works, it's slop. Real content names real things — specific tools, specific numbers, specific failures, specific people.

2. **Intentional > Default.** If the answer to "why this?" is "because that's how it's usually done," it's slop. Every choice — word, color, layout, font, composition — must have a reason rooted in the brand or the message.

3. **Human > Polished.** Rough edges, personality quirks, asymmetry, and real references signal authenticity. Flawless, balanced, hedged-on-every-side content signals AI. In 2026, imperfection is premium.

## The Universal Slop Test

Before shipping ANY content — a social post, a landing page, an email, a design, an image prompt — run these five questions:

1. **"Would AI generate this by default?"** If yes, question every element.
2. **"Could this belong to any brand?"** If yes, it's not specific enough.
3. **"Is there a human fingerprint?"** A specific reference only a human would make, an imperfect choice, a voice that comes through.
4. **"Am I decorating or communicating?"** Remove decoration. Keep communication.
5. **"Would someone who knows the brand recognize this without the logo?"** If no, more brand needed.

## The Six Domains of Slop

Each domain has a dedicated reference file with full catalogs of patterns and fixes.

### 1. Copy Slop (`references/copy-slop-dictionary.md`)
The words, phrases, and sentence structures that scream "AI wrote this." Includes the banned word list, banned phrase list, structural tells (uniform paragraphs, em dash abuse, hedging), and era-specific vocabulary shifts.

### 2. Design/UI Slop (`references/design-slop-patterns.md`)
Purple gradients, unchanged component libraries, bento box abuse, default sidebar+topbar layouts, Inter font, uniform border radius, shadow soup, stock illustrations. The visual equivalent of "In today's fast-paced world."

### 3. Image Slop (`references/image-slop-tells.md`)
Plastic skin, too-perfect symmetry, oversaturated HDR, generic compositions, text rendering failures, jewelry merging into skin, uncanny valley expressions. How to spot AI images and how to prompt/edit past the tells.

### 4. Social Media Slop (`references/social-slop-patterns.md`)
LinkedIn broetry, emoji bullet points, "Agree?" closers, manufactured urgency, generic listicles, motivational quotes over AI face images. Platform-specific patterns for LinkedIn, Instagram, X/Twitter, and TikTok.

### 5. Video Slop (`references/video-slop-tells.md`)
Physics violations, object morphing, temporal flickering, hand artifacts, background drift, surface texture crawling. Detection techniques for Sora, Veo, Kling, and other generators.

### 6. Website Slop (`references/website-slop-formula.md`)
The SaaS formula (hero > logos > features > testimonials > pricing > CTA), vague aspirational headlines, gradient blob decorations, glassmorphism without purpose, the AI Purple Problem. Why AI websites convert 91% worse than quality inventory.

## Agents

### Slop Detector (`agents/slop-detector.md`)
Takes any content and audits it against all slop patterns. Returns a slop score, specific violations with references, severity ratings, and suggested fixes.

### Copy Humanizer (`agents/copy-humanizer.md`)
Takes AI-sounding copy and rewrites it: replaces banned words, varies sentence rhythm, adds specificity, removes hedging, applies brand voice from BRAND-SYSTEM.md if available.

## Workflow

### For Any Content Creation

1. **Before writing**: Check if a Brand system and/or Design system exists. These define what the brand sounds and looks like — they're the foundation that prevents slop.
2. **During creation**: The PreToolUse hook catches the most obvious copy tells automatically.
3. **Before shipping**: Run the Universal Slop Test (5 questions above). If any answer is wrong, revise.
4. **For high-stakes content**: Use the slop-detector agent for a full audit.
5. **For copy that feels off**: Use the copy-humanizer agent to rewrite.

### For Reviewing Others' Content

1. Run the slop-detector agent on the content.
2. Share the violation report with specific line references.
3. Focus on critical violations (obvious AI tells) first.
4. Don't over-correct — the goal is human, not anti-AI-for-its-own-sake.

## What Good Looks Like (`references/what-humans-do.md`)

Anti-slop is half of the equation. The other half is knowing what authentic, human-crafted content looks like across all domains. This reference covers the counter-patterns — what to do INSTEAD of the slop defaults.

## Key Rules

### Detection (What to Catch)
1. **Banned vocabulary at density.** One "leverage" is fine. Three per page is a tell. See `references/copy-slop-dictionary.md` for the full list with thresholds.
2. **Banned phrases are absolute.** "In today's fast-paced world," "It's not just X, it's Y," "Unlock the power of" — these are never acceptable. No threshold.
3. **Structural monotony kills.** Uniform paragraph length, identical sentence cadence, symmetric bullet points, consistent-length headings — AI writes at one rhythm. Humans speed up and slow down.
4. **Default choices are suspects.** Purple gradients, Inter font, sidebar+topbar, shadcn defaults, 16px radius on everything — fine IF justified by brand. Slop if chosen by default.
5. **Perfection is a tell.** Too-smooth skin, too-balanced layouts, too-hedged arguments, too-polished prose — the absence of rough edges signals AI.

### Prevention (What to Do)
6. **Specificity is the antidote.** Concrete numbers, real names, actual screenshots, specific failures, named tools. Generic = AI. Specific = human.
7. **Vary the rhythm.** Short sentence. Then a longer one that takes its time getting to the point. Then another short one. AI can't do this naturally.
8. **Earn every element.** Every paragraph, every visual, every section should justify its existence. AI generates volume; humans generate density.
9. **Show receipts.** Real data, real screenshots, real process photos, real stories. AI can generate polish; it can't generate proof.
10. **Embrace useful imperfection.** An asymmetric layout, a surprising word choice, an unexpected color — these signal "a human decided this." Don't sand down every edge.

### Integration (How This Connects)
11. **Brand is the foundation.** Most slop happens because there's no brand system to deviate from. Define the brand first (BRAND-SYSTEM.md), then slop becomes obvious because it doesn't match.
12. **Design system enforces.** Token-only values, component gating, and the "Is It Alive?" test from the design-system skill prevent UI slop at the code level.
13. **This skill audits.** Anti-slop is the quality gate that catches what the other systems miss — especially in copy, images, and content that lives outside the codebase.

## References

| File | Purpose |
|------|---------|
| `references/copy-slop-dictionary.md` | Full catalog of AI copy tells: words, phrases, structures |
| `references/design-slop-patterns.md` | Visual/UI patterns that signal AI generation |
| `references/image-slop-tells.md` | How to detect AI-generated images |
| `references/social-slop-patterns.md` | Platform-specific social media AI patterns |
| `references/video-slop-tells.md` | AI video detection signals |
| `references/website-slop-formula.md` | The generic AI website template and how to break it |
| `references/what-humans-do.md` | Counter-patterns: what authentic content looks like |
| `agents/slop-detector.md` | Content audit agent |
| `agents/copy-humanizer.md` | Copy rewrite agent |
| `hooks/copy_slop_hook.py` | Automatic copy slop detection hook |
