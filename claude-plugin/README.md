# elephant-goldfish — Claude Code plugin

Marketplace-distributable build of the elephant-goldfish workflow as a Claude Code **plugin** with five **skills**: `eg-brainstorm`, `eg-prd`, `eg-fix-bug`, `eg-new-feature`, `eg-precommit-review`.

This is a sibling to the [`claude/`](../claude/) adapter, which is the `gh api` install path with install-time stack customization. The plugin format is for users who want a **one-click marketplace install** instead of pasting a bootstrap message.

## Difference from the bootstrap path

The `claude/` adapter customizes templates **at install time**: it detects the user's stack (Rails / Flutter / Vite / etc.) and writes concrete commands (`mise exec ruby@2.7.5 -- bundle exec rails test`, `flutter test`, `npm test && npm run test:e2e`) into the on-disk slash-command files.

The plugin ships **static skills**. Stack detection happens **at invocation time**: the skill reads `package.json` / `Gemfile` / `pubspec.yaml` / `mise.toml` / `.github/workflows/` / `CLAUDE.md` itself and picks the right commands for the repo on each run. Same logic, deferred from install to runtime.

| Aspect | Bootstrap (`claude/`) | Plugin (this directory) |
|---|---|---|
| Install | Paste `gh api` message | `/plugin install elephant-goldfish@claude-plugins-official` |
| Stack customization | Once, at install — files contain concrete commands | Every invocation — skill reads manifests and picks |
| Per-repo concrete trace | Yes (commands hardcoded into files) | No (commands resolved live each time) |
| Marketplace distribution | No | Yes |

Both reach the same workflow. Pick whichever fits your install style.

## Layout

```
claude-plugin/
├── .claude-plugin/
│   └── plugin.json                  # Manifest
├── skills/
│   ├── eg-brainstorm/SKILL.md
│   ├── eg-prd/SKILL.md
│   ├── eg-fix-bug/SKILL.md
│   ├── eg-new-feature/SKILL.md
│   └── eg-precommit-review/SKILL.md
└── README.md                        # This file
```

## Installation (once published)

```
/plugin install elephant-goldfish@claude-plugins-official
```

Skills become available as `/elephant-goldfish:eg-brainstorm`, `/elephant-goldfish:eg-prd`, etc.

## Local testing before publishing

```sh
cd /path/to/your-test-repo
claude --plugin-dir /path/to/elephant-goldfish/claude-plugin
```

Inside the session, try:

```
/elephant-goldfish:eg-precommit-review
```

The skill will detect the test repo's stack from its manifests and run the appropriate lint / test / e2e commands.

## Publishing

Submit at [`platform.claude.com/plugins/submit`](https://platform.claude.com/plugins/submit) with:

- Repository URL: `https://github.com/vshvedov/elephant-goldfish`
- Plugin path within the repo: `claude-plugin/`
- Description and screenshots from the README.

## Pattern reference

The full elephant/goldfish pattern docs (the elephant, the goldfish, the asymmetry, the pipeline diagram) live in the [top-level README](../README.md). The skill bodies in this plugin are the runtime instructions that implement that pattern; the README is the conceptual context.
