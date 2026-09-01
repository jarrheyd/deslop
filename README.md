# deslop

An AI-slop quality gate. It catches the words, phrases, and visual patterns that read as machine-made, before they ship - whoever or whatever wrote them.

Not a style guide. A bullshit detector.

## Scope: it only subtracts

deslop removes AI tells. That is the whole intent. It does **not** teach voice, tone, or positive style, and it should not - a clean draft with no voice is still lifeless, but that is a separate problem with a separate fix. Bring your own voice or brand model (a style guide, sample writing, a design-methodology skill) and let it add the character; let deslop strip what the model leaves behind. Subtraction here, augmentation there.

## What it does

Two checkers and a skill:

1. **Copy checker** (`hooks/copy_slop_hook.py`) - reads prose and blocks AI copy tells.
2. **Design checker** (`hooks/design_slop_hook.py`) - reads HTML/CSS/JSX and blocks AI-default *visual* tells.
3. **The skill** (`SKILL.md` + `references/` + `agents/`) - invoke it for a full manual review, with the pattern catalogs, a slop-detector agent, and a copy-humanizer agent.

Both checkers are plain Python: they read a file and exit `0` (clean) or `2` (slop found). That makes them usable as an editor hook, a git pre-commit hook, a CI step, or a call from any agent. **Everything blocks** - there is no warn tier. Bypass a run with `DISABLE_ANTI_SLOP_HOOK=1`.

### A sample of what's caught

Copy:

| Tell |
|---|
| Banned phrases (the "fast-paced world" / "not just X, it's Y" / "unlock the power of" family) |
| Vague / landing metaphors ("here's where it lands", "where the magic happens", "moves the needle", "at the end of the day") |
| AI tool-remnant markers (ChatGPT/Gemini citation artifacts left in text) |
| Chatbot outros ("I hope this helps", "feel free to reach out") |
| Significance/legacy puffery ("stands as a testament", "pivotal moment", "cemented its legacy") |
| Vague attributions ("studies show", "experts say", "it is widely known") |
| Sycophantic / manufactured-candor openers ("Great question!", "Honestly,", "Real talk.") |
| Curly quotes, Title Case headings, bold overuse, em dashes |
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

The design checker passes intentional brand work (a single purposeful gradient, hex borders, a real typeface). Non-regexable tells (bento grids, fake testimonials, slide eyebrows and explainer captions) live in `references/` for the review agent. Full catalogs are in `references/`.

## Run it automatically in Claude Code

1. Clone into your skills folder as `deslop` (the name matters - the checkers exempt their own files by that path):
   ```bash
   git clone https://github.com/jarrheyd/deslop.git ~/.claude/skills/deslop
   ```
2. Add both hooks to the `hooks` object in `~/.claude/settings.json`:
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
3. Restart Claude Code. Now every Write/Edit to prose or HTML/CSS is checked automatically.

## Run it anywhere else (pre-commit, CI, Codex, any tool)

The checkers read Claude Code's hook JSON on stdin, so feeding them a file is one line:

```bash
echo '{"tool_name":"Write","tool_input":{"file_path":"draft.md","content":"'"$(cat draft.md)"'"}}' \
  | python3 ~/.claude/skills/deslop/hooks/copy_slop_hook.py   # exit 2 = slop found
```

Wrap that in a git `pre-commit` hook or a CI step to gate any repo, or call it from any agent that can run a shell (Codex, your own scripts). Same logic, no Claude dependency. The skill and catalogs are just Markdown any model can read.

## Designing, not just detecting

deslop *catches* AI design tells. It does not design. To actually build or critique an interface, pair it with a design-methodology skill - [impeccable](https://github.com/jarrheyd) is the companion for that. Reach for impeccable to make the UI good, and let deslop catch the AI defaults that slip back in.

## Customize

Open `SKILL.md` and find **Operator-observed tells** - replace the examples with your own, captured from real draft-vs-final corrections. Add words to `TIER1_WORDS` or phrases to `BANNED_PHRASES` in `hooks/copy_slop_hook.py`, and visual tells to `TELLS` in `hooks/design_slop_hook.py`.

## Structure

```
SKILL.md                      the router, the laws, the Universal Slop Test
hooks/copy_slop_hook.py       copy checker (blocks AI copy tells)
hooks/design_slop_hook.py     design checker (blocks AI visual tells)
references/                   full pattern catalogs (copy, design, image, social, video, website)
agents/                       slop-detector + copy-humanizer sub-agents
```

## License

MIT - see [LICENSE](LICENSE).
