# BOOTSTRAP.md

Compatibility entrypoint for the Claude Code bootstrap.

This repo now keeps agent-specific adapters under `claude/` and `codex/`. Existing install snippets may still fetch this root file, so do not treat it as the full procedure.

Fetch the Claude bootstrap procedure with:

```sh
gh api repos/vshvedov/elephant-goldfish/contents/claude/BOOTSTRAP.md -H 'Accept: application/vnd.github.raw'
```

Then follow that procedure to set up the Claude Code elephant/goldfish workflow.

For Codex, fetch:

```sh
gh api repos/vshvedov/elephant-goldfish/contents/codex/BOOTSTRAP.md -H 'Accept: application/vnd.github.raw'
```
