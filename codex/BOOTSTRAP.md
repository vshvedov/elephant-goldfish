# Codex BOOTSTRAP.md

This file is read by Codex. The user has pointed you at this repo and asked you to set up the elephant/goldfish workflow for Codex on this machine, alongside any existing Claude Code or Gemini setup.

Important: current Codex builds do not support project-defined custom slash commands. Install Codex Skills directly into the user Codex skills directory and tell users to invoke them as `Use $eg-prd ...`, `Use $eg-new-feature ...`, etc.

## How to fetch this repo's Codex content

There is no local working copy on the target machine — you got here by streaming this file's text through `gh api`. Fetch the remaining Codex files the same way, on demand:

```sh
gh api repos/vshvedov/elephant-goldfish/contents/<PATH> -H 'Accept: application/vnd.github.raw'
```

Files this procedure references later:

- `codex/agents-md-snippet.md`
- `codex/skills/eg-brainstorm/SKILL.md`
- `codex/skills/eg-brainstorm/agents/openai.yaml`
- `codex/skills/eg-prd/SKILL.md`
- `codex/skills/eg-prd/agents/openai.yaml`
- `codex/skills/eg-fix-bug/SKILL.md`
- `codex/skills/eg-fix-bug/agents/openai.yaml`
- `codex/skills/eg-new-feature/SKILL.md`
- `codex/skills/eg-new-feature/agents/openai.yaml`
- `codex/skills/eg-precommit-review/SKILL.md`
- `codex/skills/eg-precommit-review/agents/openai.yaml`

Recommended: fetch them all up front into a tmp dir, then read locally through the rest of the steps:

```sh
for s in eg-brainstorm eg-prd eg-fix-bug eg-new-feature eg-precommit-review; do
  mkdir -p "/tmp/elephant-goldfish-codex/codex/skills/${s}/agents"
done

for f in \
  codex/agents-md-snippet.md \
  codex/skills/eg-brainstorm/SKILL.md \
  codex/skills/eg-brainstorm/agents/openai.yaml \
  codex/skills/eg-prd/SKILL.md \
  codex/skills/eg-prd/agents/openai.yaml \
  codex/skills/eg-fix-bug/SKILL.md \
  codex/skills/eg-fix-bug/agents/openai.yaml \
  codex/skills/eg-new-feature/SKILL.md \
  codex/skills/eg-new-feature/agents/openai.yaml \
  codex/skills/eg-precommit-review/SKILL.md \
  codex/skills/eg-precommit-review/agents/openai.yaml; do
  gh api "repos/vshvedov/elephant-goldfish/contents/${f}" -H 'Accept: application/vnd.github.raw' > "/tmp/elephant-goldfish-codex/${f}"
done
```

After this, every reference to `codex/<path>` below resolves to `/tmp/elephant-goldfish-codex/codex/<path>`.

## Step 0: Confirm the install target

The user invoked you from a project repo, but these Codex skills are shared across projects. Install them directly into the user Codex skills directory:

```sh
${CODEX_HOME:-$HOME/.codex}/skills
```

Do not create project-local `plugins/elephant-goldfish-codex/` folders. Do not create `.agents/plugins/marketplace.json`. Do not create symlinks from a project directory into `~/.codex/skills`.

Preserve all existing project files for other agents:

- Do not remove or rewrite `.claude/commands/*`.
- Do not remove or rewrite `CLAUDE.md`.
- Do not remove or rewrite `.gemini/skills/*`.
- Do not remove or rewrite `GEMINI.md`.

Before installing, inspect `${CODEX_HOME:-$HOME/.codex}/skills/eg-*`:

- If an existing path is a symlink to an older project-local elephant/goldfish install, replace it with a real directory copied from this repo.
- If an existing path is a directory for one of these same elephant/goldfish skills, update it in place after preserving any user-local edits by showing a diff if possible.
- If an existing path is a non-elephant-goldfish user skill, stop and ask whether to skip, rename, or replace it.

## Step 1: Install the shared Codex skills

Copy each fetched skill directory into `${CODEX_HOME:-$HOME/.codex}/skills/` as a real directory, not a symlink:

```sh
skills_root="${CODEX_HOME:-$HOME/.codex}/skills"
mkdir -p "$skills_root"
for s in eg-brainstorm eg-prd eg-fix-bug eg-new-feature eg-precommit-review; do
  src="/tmp/elephant-goldfish-codex/codex/skills/${s}"
  dest="${skills_root}/${s}"

  if [ -L "$dest" ]; then
    rm "$dest"
  elif [ -e "$dest" ] && ! grep -q '^name: "'"${s}"'"$' "$dest/SKILL.md" 2>/dev/null; then
    echo "Refusing to overwrite unrelated user skill: $dest" >&2
    exit 1
  else
    rm -rf "$dest"
  fi

  mkdir -p "$dest"
  cp -R "$src/"* "$dest/"
done
```

If this exits because an unrelated skill would be overwritten, ask the user how to proceed.

Do not substitute project-specific values into the installed `SKILL.md` files. These are shared skills. They intentionally inspect `AGENTS.md`, `CLAUDE.md`, package manifests, and CI files at runtime in whatever project the current Codex session is using.

## Step 2: Optionally update the current project's AGENTS.md

Read `codex/agents-md-snippet.md`. If the current project has an `AGENTS.md`, ask whether to add the snippet near the top after the project overview or existing tool workflow section. If no `AGENTS.md` exists, ask before creating one.

The snippet is documentation only; it is not required for the global skills to work. Do not block the install on `AGENTS.md` changes.

## Step 3: Sanity-check the output

Verify:

- `${CODEX_HOME:-$HOME/.codex}/skills/eg-brainstorm/SKILL.md` exists and is not a symlink.
- `${CODEX_HOME:-$HOME/.codex}/skills/eg-prd/SKILL.md` exists and is not a symlink.
- `${CODEX_HOME:-$HOME/.codex}/skills/eg-fix-bug/SKILL.md` exists and is not a symlink.
- `${CODEX_HOME:-$HOME/.codex}/skills/eg-new-feature/SKILL.md` exists and is not a symlink.
- `${CODEX_HOME:-$HOME/.codex}/skills/eg-precommit-review/SKILL.md` exists and is not a symlink.
- Each skill has `agents/openai.yaml`.
- No `[BOOTSTRAP: ...]` markers remain in the installed Codex skill files.
- No `plugins/elephant-goldfish-codex`, `.agents/plugins/marketplace.json`, or project-local symlink layer was created for Codex.

Tell the user to start a new Codex session or reload the app after installation. After reload, typing `$eg` should show the skills. They are invoked as prompts, not slash commands:

```text
Use $eg-prd to write a PRD for <idea>
Use $eg-new-feature to build <feature>
Use $eg-fix-bug to fix <bug>
Use $eg-precommit-review to review my pending changes
Use $eg-brainstorm to brainstorm <rough idea>
```

## Step 4: Final report

Print to the user:

- Skills installed, with absolute paths under `${CODEX_HOME:-$HOME/.codex}/skills`.
- Whether any old project-local symlinks were replaced.
- Whether `AGENTS.md` was updated or skipped.
- Reminder to reload/start a new Codex session.

Stop short of committing any project changes unless the user explicitly asks.

## Reinstalling or updating

When the user says "reinstall Codex skills" or "update Codex skills from the template repo," repeat this procedure and overwrite only these five elephant/goldfish skill directories in `${CODEX_HOME:-$HOME/.codex}/skills`. Preserve unrelated user skills.
