# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A single Claude Code skill, `video-to-roteiro`, that takes a local video file and produces a PT-BR markdown shot list (`roteiro.md`) by uploading the video to the Google Gemini Files API and prompting `gemini-2.5-pro`. Output is plain markdown — there is no JSON schema. The repo is the source of truth; `install.sh` symlinks `skills/video-to-roteiro/` into `~/.claude/skills/` so edits here propagate immediately to the installed skill.

## Common commands

```bash
bash install.sh                                                    # symlink skill to ~/.claude/skills/
export GEMINI_API_KEY="..."                                        # required at runtime
pip install -r skills/video-to-roteiro/requirements.txt            # install google-genai

# Run the script directly (bypass the skill harness):
python skills/video-to-roteiro/scripts/process_video.py <video> [out.md]
```

There is no test suite, linter, or build step. Validate changes by syntax-checking (`python -m py_compile ...`), exercising error paths without an API key, or running end-to-end against a short test clip.

## Architecture

Three pieces, in order of how a user request flows through them:

1. **`skills/video-to-roteiro/SKILL.md`** — the entrypoint Claude Code reads. Frontmatter (`name`, `description`, `allowed-tools`, `argument-hint`) drives skill discovery; the body tells Claude which bash steps to run when invoked. Editing the description changes when the skill auto-triggers from natural language.

2. **`skills/video-to-roteiro/scripts/process_video.py`** — the only real logic. Flow: validate `GEMINI_API_KEY` and file (≤ 2 GB, Files API limit) → `client.files.upload()` → poll `state` until `ACTIVE` (timeout 600 s) → `generate_content(model="gemini-2.5-pro", contents=[uploaded, PROMPT])` → write `response.text` straight to disk → best-effort `files.delete()`. The `PROMPT` constant is the entire spec of the output format and is the file to edit when changing what the markdown looks like.

3. **`install.sh`** — `ln -sfn` from this repo into `~/.claude/skills/video-to-roteiro`. Re-running it is idempotent.

## Conventions specific to this repo

- All user-facing strings (prompt, error messages, README, SKILL.md body) are PT-BR. Keep that consistent when editing.
- Output format changes go in the `PROMPT` constant in `process_video.py`, not in SKILL.md. SKILL.md only orchestrates.
- The default model is `gemini-2.5-pro`, set as the `MODEL` constant. Prefer changing the constant over plumbing a CLI flag unless asked.
- `.gitignore` excludes `*.mp4|mov|mkv|webm|avi`, `roteiro.md`, and `.env` — local test artifacts must never be committed.
- Development branch: `claude/skill-creator-SYMgg`. Push with `git push -u origin claude/skill-creator-SYMgg`.

## External docs worth keeping in mind

- Claude Code skills format: https://code.claude.com/docs/en/skills
- Gemini Files API and video understanding: https://ai.google.dev/gemini-api/docs/video-understanding
