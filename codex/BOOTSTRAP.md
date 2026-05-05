# Codex BOOTSTRAP.md

This file is read by Codex. The user has pointed you at this repo and asked you to set up the elephant/goldfish workflow in their target repo alongside any existing Claude Code setup. Do not remove or rewrite Claude files.

Important: current Codex builds do not support project-defined custom slash commands. Do not install `commands/*.md` and do not promise `/eg-*` or `/elephant-goldfish-codex:eg-*`. Install Codex Skills and tell users to invoke them as `Use $eg-prd ...`, `Use $eg-new-feature ...`, etc.

## How to fetch the rest of this repo's Codex content

There is no local working copy on the target machine — you got here by streaming this file's text through `gh api`. Fetch the remaining Codex files the same way, on demand:

```sh
gh api repos/vshvedov/elephant-goldfish/contents/<PATH> -H 'Accept: application/vnd.github.raw'
```

Files this procedure references later:

- `codex/.codex-plugin/plugin.json`
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
mkdir -p /tmp/elephant-goldfish-codex/codex/.codex-plugin
for s in eg-brainstorm eg-prd eg-fix-bug eg-new-feature eg-precommit-review; do
  mkdir -p "/tmp/elephant-goldfish-codex/codex/skills/${s}/agents"
done

for f in \
  codex/.codex-plugin/plugin.json \
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

## Step 0: Confirm the target and preserve Claude

The user invoked you from a working directory that is the target repo. Confirm the target's absolute path before writing.

This is an additive Codex install. Preserve all existing Claude Code files:

- Do not remove or rewrite `.claude/commands/*`.
- Do not remove or rewrite `CLAUDE.md`.
- It is OK to read `CLAUDE.md` to mirror project conventions into the Codex skills.

If any of these Codex files already exist, ask whether to overwrite, augment, or abort before changing them:

- `plugins/elephant-goldfish-codex/.codex-plugin/plugin.json`
- `plugins/elephant-goldfish-codex/skills/{eg-brainstorm,eg-prd,eg-fix-bug,eg-new-feature,eg-precommit-review}/SKILL.md`
- `plugins/elephant-goldfish-codex/skills/{eg-brainstorm,eg-prd,eg-fix-bug,eg-new-feature,eg-precommit-review}/agents/openai.yaml`
- `.agents/plugins/marketplace.json`
- `AGENTS.md` section `## Working with Codex (elephant/goldfish)`

Also inspect `~/.codex/skills/eg-*`. If any existing non-symlink user skill would be overwritten by the autocomplete symlink step, ask before changing it.

## Step 1: Inspect the stack

Read these files in the target if they exist (parallel reads):

- `AGENTS.md` — Codex conventions, skill policy, repo-local instructions
- `CLAUDE.md` — existing Claude conventions that should be mirrored, not replaced
- `package.json`, `Gemfile`, `pubspec.yaml`, `pyproject.toml`, `requirements.txt`, `setup.py`, `Pipfile`
- `go.mod`, `Cargo.toml`, `composer.json`, `mix.exs`
- `tsconfig.json`, `playwright.config.ts`, `vitest.config.ts`, `jest.config.js`, etc.
- `Rakefile`, `Makefile`, `justfile`, `mise.toml`, `.tool-versions`, `.nvmrc`, `.ruby-version`
- `docker-compose.yml`, `Dockerfile`
- `.github/workflows/*.yml`

Also run `git log --oneline -10` to learn the commit-message convention.

From this, derive a stack profile:

```text
STACK PROFILE
- Language(s) and framework(s):
- Package manager + version manager:
- Linter + how to invoke:
- Type-checker + how to invoke (or "n/a"):
- Unit/integration test runner + how to invoke:
- E2E test runner + how to invoke (or "n/a"):
- Security scanner + how to invoke (or "n/a"):
- Dev server: command + URL:
- Browser validation strategy: Browser Use / in-app browser URL, simulator/device runs, or n/a:
- Code-generation step required before tests + when:
- Existing Claude workflow to preserve:
- Existing Codex workflow, AGENTS.md rules, repo-local plugin setup, or user skill setup:
- Commit message convention from `git log`:
- Multi-tenancy / auth / scoping concerns the reviewer should always check:
- Stack-specific gotchas:
```

Print the stack profile and ask the user to confirm or correct before generating the skills.

## Step 2: Generate the Codex plugin skill files

Use `codex/skills/*/SKILL.md` as the skeletons. Substitute every `[BOOTSTRAP: ...]` marker with concrete values from the stack profile. Copy each matching `agents/openai.yaml` alongside its `SKILL.md`, updating display text only if the target project needs a clearer label.

The generated target layout is:

```text
plugins/elephant-goldfish-codex/
  .codex-plugin/plugin.json
  skills/
    eg-brainstorm/
      SKILL.md
      agents/openai.yaml
    eg-prd/
      SKILL.md
      agents/openai.yaml
    eg-fix-bug/
      SKILL.md
      agents/openai.yaml
    eg-new-feature/
      SKILL.md
      agents/openai.yaml
    eg-precommit-review/
      SKILL.md
      agents/openai.yaml
```

Specifically:

- `[BOOTSTRAP: lint command]` -> actual command, or remove the bullet if none exists.
- `[BOOTSTRAP: typecheck command]` -> actual command, or remove the block if no separate typecheck exists.
- `[BOOTSTRAP: unit test command]`, `[BOOTSTRAP: e2e test command]` -> observed commands.
- `[BOOTSTRAP: dev server URL]` -> e.g. `http://localhost:3000`.
- `[BOOTSTRAP: browser validation block]` -> Browser Use / in-app browser for web, simulator/device for mobile, omitted for backend-only.
- `[BOOTSTRAP: test tier picks]` -> concrete test folder choices in the target.
- `[BOOTSTRAP: stack-specific Hunt for items]` -> append stack-specific reviewer bullets.
- `[BOOTSTRAP: project-specific routing note]` -> reference project-specific `eg-` skills if any.
- `[BOOTSTRAP: commit policy reminder]` -> convention observed in `git log` and repo docs.

Use the Codex tool names in generated skills:

- Fresh goldfish: `spawn_agent` with `fork_context: false` when available.
- Explorer-style lookups: `agent_type: "explorer"` when available; otherwise default agent.
- Implementation workers: `agent_type: "worker"` only for explicitly delegated, disjoint implementation slices.
- Structured user input: `request_user_input` when available; otherwise concise chat questions.
- Browser validation: Browser Use / in-app browser plugin when available; otherwise a project-appropriate browser, simulator, or CLI fallback.

Do not introduce `$ARGUMENTS`; skills do not receive a slash-command argument variable. Use language like "Use the user's text around the `$eg-prd` skill mention as the seed."

## Step 3: Create the repo-local marketplace

Create or update `.agents/plugins/marketplace.json` so Codex can discover the project-local plugin. Preserve any existing entries and append this entry if missing.

Use a marketplace name that is unique to the target repo, because Codex marketplace registrations live in the user's global `~/.codex/config.toml`. Recommended: derive it from the repo basename, lowercased and kebab-cased, with `-local` appended. Examples:

- `/Users/me/code/bifrost` -> `bifrost-local`
- `/Users/me/code/checkout-api` -> `checkout-api-local`

If `.agents/plugins/marketplace.json` already exists, preserve its top-level `"name"` and use that value for later activation steps.

```json
{
  "name": "elephant-goldfish-codex",
  "source": {
    "source": "local",
    "path": "./plugins/elephant-goldfish-codex"
  },
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL"
  },
  "category": "Coding"
}
```

If the marketplace file does not exist, create:

```json
{
  "name": "<repo-slug>-local",
  "interface": {
    "displayName": "<Project Name> Local Plugins"
  },
  "plugins": [
    {
      "name": "elephant-goldfish-codex",
      "source": {
        "source": "local",
        "path": "./plugins/elephant-goldfish-codex"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Coding"
    }
  ]
}
```

## Step 4: Activate the skills in Codex

Creating `.agents/plugins/marketplace.json` is not enough. In current Codex app builds, repo-local plugin skills may not appear in composer autocomplete until they are also visible from the user skill path.

Do not stop after writing the repo files. Complete these activation steps before reporting the install as done.

First, register the target repo as a Codex plugin marketplace. Use the target repo root, not the plugin directory:

```sh
codex plugin marketplace add "$(pwd)"
```

Then verify or add these entries in `~/.codex/config.toml`, preserving all existing marketplaces and plugins:

```toml
[marketplaces.<repo-slug>-local]
source_type = "local"
source = "<absolute path to target repo>"

[plugins."elephant-goldfish-codex@<repo-slug>-local"]
enabled = true
```

Notes:

- `codex plugin marketplace add "$(pwd)"` usually creates or updates the `[marketplaces.<repo-slug>-local]` stanza. If it uses a different marketplace key, use that key in the plugin enable stanza.
- Do not overwrite `~/.codex/config.toml`. Append or update only these two relevant stanzas.
- If another marketplace with the same name already points at a different repo, choose a more specific name, update `.agents/plugins/marketplace.json` to match, then register again.

Then create/update symlinks from the repo-local skills into the user skill path so `$eg-*` autocomplete works in current Codex app builds:

```sh
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
for s in eg-brainstorm eg-prd eg-fix-bug eg-new-feature eg-precommit-review; do
  target="$(pwd)/plugins/elephant-goldfish-codex/skills/${s}"
  link="${CODEX_HOME:-$HOME/.codex}/skills/${s}"
  if [ -L "$link" ]; then
    rm "$link"
  elif [ -e "$link" ]; then
    echo "Refusing to overwrite existing non-symlink user skill: $link" >&2
    exit 1
  fi
  ln -s "$target" "$link"
done
```

If this exits because an existing non-symlink user skill would be overwritten, stop and ask the user whether to preserve, rename, or replace that skill.

Tell the user to start a new Codex session or reload the app after activation. After reload, typing `$eg` should show the skills. They are invoked as prompts, not slash commands:

```text
Use $eg-prd to write a PRD for <idea>
Use $eg-new-feature to build <feature>
Use $eg-fix-bug to fix <bug>
Use $eg-precommit-review to review my pending changes
Use $eg-brainstorm to brainstorm <rough idea>
```

## Step 5: Update AGENTS.md

Read `codex/agents-md-snippet.md`. Tailor the placeholders to match the target's setup and inject the snippet into `AGENTS.md`.

- If `AGENTS.md` exists, inject near the top after the project overview or existing tool workflow section.
- If no `AGENTS.md` exists, ask before creating one. Seed it with a project overview placeholder, the snippet, and a short build/test command stub.
- Do not copy the Claude `CLAUDE.md` section verbatim. Mirror durable project facts only.

## Step 6: Sanity-check the output

For each generated file:

- No `[BOOTSTRAP: ...]` markers remain.
- No `$ARGUMENTS`, `/elephant-goldfish-codex:eg-*`, or unsupported `commands/` references remain in Codex-generated files.
- The plugin manifest JSON parses and contains `"skills": "./skills/"`.
- `.agents/plugins/marketplace.json` parses and preserves existing plugins.
- Each generated skill has a valid `SKILL.md` with `name` and `description` frontmatter.
- Each generated skill has `agents/openai.yaml`.
- `~/.codex/config.toml` has an active `[marketplaces.<repo-slug>-local]` entry pointing at the target repo.
- `~/.codex/config.toml` has `[plugins."elephant-goldfish-codex@<repo-slug>-local"] enabled = true`, using the actual marketplace key if different.
- `${CODEX_HOME:-$HOME/.codex}/skills/eg-*` symlinks point at the target repo's generated skill folders.
- Commands referenced inside the skills actually exist in the target.
- File paths in test-tier picks correspond to real folders where possible.
- The skill prompts still preserve the elephant/goldfish asymmetry: goldfish see only the artifact they need, not the elephant's hidden hypothesis or implementation plan.

## Step 7: Final report

Print to the user:

- Stack profile (confirmed or corrected)
- Codex plugin skill files created
- Marketplace file status
- Codex activation status: marketplace key, plugin enable stanza, user-skill symlinks, and whether a new session/reload is needed
- AGENTS.md change
- Claude files preserved
- Anything you could not infer

Stop short of committing. The user authorizes the commit when ready.

## Re-bootstrapping

When the user says "re-bootstrap Codex" or "update Codex skills from the template repo," diff against the existing Codex plugin skill files before overwriting:

- Preserve project-specific edits.
- Preserve unrelated marketplace entries.
- Preserve unrelated user skills in `${CODEX_HOME:-$HOME/.codex}/skills`.
- Ask before overwriting if a project-specific edit would be lost.
- Do not touch `.claude/commands/*` or `CLAUDE.md` unless the user explicitly asks to update the Claude adapter too.
