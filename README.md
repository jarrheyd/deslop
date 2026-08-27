# deslop

A quality gate for [Claude Code](https://docs.claude.com/en/docs/claude-code) that catches AI tells **before they ship** - the words, phrases, and visual patterns that read as machine-made.

Not a style guide. A bullshit detector.

## Scope: it only subtracts

deslop removes AI tells. That is the whole intent. It does **not** teach voice, tone, or positive style, and it should not - a clean draft with no voice is still lifeless, but that is a separate problem with a separate fix. Bring your own voice or brand model (a style guide, sample writing, a design-methodology skill) and let it add the character; let deslop strip what the model leaves behind. Subtraction here, augmentation there.

## What it does

Three parts:

1. **Copy hook** (`hooks/copy_slop_hook.py`) - a `PreToolUse` hook on every `Write`/`Edit`/`MultiEdit` to prose (`.md`, `.mdx`, `.txt`, `.html`, and string literals in `.tsx`/`.jsx`/`.ts`/`.js`/`.py`). Catches AI copy tells before the text lands on disk.
2. **Design hook** (`hooks/design_slop_hook.py`) - a `PreToolUse` hook on `.html`/`.css`/`.scss`/`.tsx`/`.jsx`/`.vue`/`.svelte`. Catches AI-default *visual* tells in the source.
3. **The skill** (`SKILL.md` + `references/` + `agents/`) - invoke it for a full review, with the pattern catalogs, a slop-detector agent, and a copy-humanizer agent.

**Everything blocks.** There is no warn tier: a tell stops the write and explains itself, so you fix it instead of shipping it. Bypass a session with `DISABLE_ANTI_SLOP_HOOK=1`.

### A sample of what's caught

Copy:

| Tell |
|---|
| Banned phrases (the "fast-paced world" / "not just X, it's Y" / "unlock the power of" family) |
| AI tool-remnant markers (ChatGPT/Gemini citation artifacts left in text) |
| Chatbot outros ("I hope this helps", "feel free to reach out", "any questions") |
| Significance/legacy puffery ("stands as a testament", "pivotal moment", "cemented its legacy") |
| Vague attributions ("studies show", "experts say", "it is widely known") |
| Sycophantic / manufactured-candor openers ("Great question!", "Honestly,", "Real talk.") |
| Curly quotes, Title Case headings, bold overused through prose, em dashes |
| AI-vocabulary density ("delve", "leverage", "tapestry", "synergy") |
| Weak copulas ("serves as"), empty "-ing" tails, wordy phrases, false ranges, eyebrows |

Design:

| Tell |
|---|
| AI purple, the ChatGPT `#667eea`->`#764ba2` gradient, overgradient (4+) |
| Gradient text, glassmorphism (backdrop blur), decorative blur blobs |
| Left-border accent cards, the generic `rgba(0,0,0,0.1)` shadow, drop-shadow, faint hairline borders |
| Lucide icons, Inter / Geist / Space Grotesk as the default typeface |
| Fake terminal-window props |

The design hook is tuned to pass intentional brand work (a single purposeful gradient, hex borders, a real typeface). Non-regexable tells (bento grids, fake testimonials, missing TOS, slide eyebrows and explainer captions) live in `references/design-slop-patterns.md` for the review agent.

Full catalogs live in `references/`.

## Install

1. **Clone into your Claude skills folder as `deslop`:**
   ```bash
   git clone https://github.com/jarrheyd/deslop.git ~/.claude/skills/deslop
   ```
   The folder must be named `deslop` - the hooks exempt their own files by that path.

2. **Enable both hooks.** Add this to the `hooks` object in `~/.claude/settings.json`:
   ```json
   "PreToolUse": [
     {
       "matcher": "Write|Edit|MultiEdit",
       "hooks": [
         { "type": "command", "command": "python3 ~/.claude/skills/deslop/hooks/copy_slop_hook.py", "timeout": 5 },
         { "type": "command", "command": "python3 ~/.claude/skills/deslop/hooks/design_slop_hook.py", "timeout": 5 }
       ]
     }
   ]
   ```
   If your build does not expand `~` in hook commands, use the absolute path.

3. **Restart Claude Code** so the hooks load.

The skill works without the hooks - invoke it any time. The hooks just make the check automatic.

## Use

- **Automatic:** with the hooks on, any Write/Edit to prose or to HTML/CSS gets checked. A block explains the tell and points at the fix.
- **On demand:** ask Claude to run a slop check on a file, or invoke the skill.
- **Bypass** for one session: `DISABLE_ANTI_SLOP_HOOK=1`.

## Designing, not just detecting

deslop *catches* AI design tells. It does not design. For actually building or critiquing an interface (hierarchy, spacing, typography, motion, information architecture), pair it with a design-methodology skill - [impeccable](https://github.com/jarrheyd) is the companion built for that. Rule of thumb: reach for impeccable to make the UI good, and let deslop catch the AI defaults that slip back in.

## Customize

Open `SKILL.md` and find **Operator-observed tells**. Replace the examples with your own, captured from real draft-vs-final corrections - those are the highest-signal patterns you have. Add project words to `TIER1_WORDS` or phrases to `BANNED_PHRASES` in `hooks/copy_slop_hook.py`; add visual tells to `TELLS` in `hooks/design_slop_hook.py`.

## Structure

```
SKILL.md                      the router, the laws, the Universal Slop Test
hooks/copy_slop_hook.py       copy PreToolUse hook (blocks AI copy tells)
hooks/design_slop_hook.py     design PreToolUse hook (blocks AI visual tells)
references/                   full pattern catalogs (copy, design, image, social, video, website)
agents/                       slop-detector + copy-humanizer sub-agents
```

## License

MIT - see [LICENSE](LICENSE).
