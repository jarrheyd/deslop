# deslop

A quality gate for [Claude Code](https://docs.claude.com/en/docs/claude-code) that catches AI-generated writing tells in prose **before they ship** - the words, phrases, and structures that read as machine-written.

Not a style guide. A bullshit detector.

## What it does

Two layers:

1. **An automatic `PreToolUse` hook** (`hooks/copy_slop_hook.py`) that runs on every `Write`/`Edit`/`MultiEdit` to prose files (`.md`, `.mdx`, `.txt`, `.html`, and string literals in `.tsx`/`.jsx`/`.ts`/`.js`/`.py`). It **blocks** hard tells and **warns** on softer ones, before the text lands on disk.
3. **A design hook** (`hooks/design_slop_hook.py`) that scans HTML/CSS/JSX on write and blocks AI-default *visual* tells (purple gradients, glassmorphism, left-border accent cards, the generic 0.1 shadow, Lucide, Inter/Geist, drop-shadow, overgradient).
2. **A skill** (`SKILL.md` + `references/` + `agents/`) you can invoke for a full slop review, with a copy dictionary, a slop-detector agent, and a copy-humanizer agent.

### A sample of what's caught

| Catches | Action |
|---|---|
| Banned phrases (the "fast-paced world" / "not just X, it's Y" / "unlock the power of" family) | block |
| AI tool-remnant markers (ChatGPT/Gemini citation artifacts left in text) | block |
| Chatbot outros ("I hope this helps", "feel free to reach out", "any questions") | block |
| Significance/legacy puffery ("stands as a testament", "pivotal moment", "cemented its legacy") | block |
| Vague attributions ("studies show", "experts say", "it is widely known") | block |
| Sycophantic / manufactured-candor openers ("Great question!", "Honestly,", "Real talk.") | block |
| Curly quotes, Title Case headings, bold overused through prose | block |
| AI-vocabulary density ("delve", "leverage", "tapestry", "synergy") | warn |
| Em-dash abuse, uniform paragraph length, hedging soup, filler transitions | warn |
| Weak copulas, empty "-ing" tails, wordy phrases, false ranges | warn |

Full catalogs live in `references/`.

## Install

1. **Clone into your Claude skills folder as `deslop`:**
   ```bash
   git clone https://github.com/jarrheyd/deslop.git ~/.claude/skills/deslop
   ```
   The folder must be named `deslop` - the hook exempts its own files by that path.

2. **Enable the automatic hook** (recommended). Add this to the `hooks` object in `~/.claude/settings.json`:
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
   If your build does not expand `~` in hook commands, use the absolute path (e.g. `python3 /Users/you/.claude/skills/deslop/hooks/copy_slop_hook.py`).

3. **Restart Claude Code** so the hook loads.

The skill works without the hook - invoke it any time. The hook just makes the check automatic.

## Use

- **Automatic:** with the hook on, any Write/Edit to prose gets checked. A block explains the tell and points at the fix; a warn prints but does not stop you.
- **On demand:** ask Claude to run a slop check on a file, or invoke the skill.
- **Bypass** for one session: `DISABLE_ANTI_SLOP_HOOK=1`.

## Customize

Open `SKILL.md` and find **Operator-observed tells**. Replace the examples with your own, captured from real draft-vs-final corrections - those personal tells are the highest-signal patterns you have. Add project words to `TIER1_WORDS` or phrases to `BANNED_PHRASES` in `hooks/copy_slop_hook.py`.

## Structure

```
SKILL.md                     the router, the laws, the Universal Slop Test
hooks/copy_slop_hook.py      the automatic PreToolUse hook (block/warn)
references/                   full pattern catalogs (copy, design, image, social, video, website)
agents/                      slop-detector + copy-humanizer sub-agents
```

## License

MIT - see [LICENSE](LICENSE).
