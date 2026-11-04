# Updating an installed harness

Paste this into the agent you use inside your project:

```text
Update my elephant/goldfish workflows from https://github.com/vshvedov/elephant-goldfish.
Read the BOOTSTRAP.md for this agent (claude, codex, gemini, cursor or grok).
Fetch one pinned revision into staging, compare it with my installed skills and
preserve my local commands and custom workflow steps. Show conflicts before
replacing anything. Leave other agents' files alone. Verify all six workflows,
including eg-question, and report what changed. Do not commit.
```

For maintainers: keep the six workflows consistent across adapters while preserving
native dispatch, invocation syntax and install locations. Run the checks described
in [testing](docs/testing.md) before publishing. Bootstrap procedures must fetch
all referenced files and preserve local edits even when a download fails.
