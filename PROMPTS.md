# Elephant/Goldfish Maintenance Prompts

Use these prompts to keep your repository in sync with the upstream elephant/goldfish patterns or to propagate changes across different AI adapters.

## For Users: Updating a Target Repo
If you have already bootstrapped a repository and want to pull in the latest logic from the upstream `elephant-goldfish` repo while preserving your local stack configuration (test commands, URLs, etc.), provide this prompt to your AI agent:

```markdown
# Update Elephant/Goldfish Patterns
There is an update available for the elephant/goldfish workflow. Please sync this repository with the upstream templates while preserving my local stack adaptations:

1. **Fetch Upstream:** Go to https://github.com/vshvedov/elephant-goldfish.
2. **Identify Adapter:** Identify which agent I am (Claude Code, Gemini CLI, or Codex) and read the corresponding `BOOTSTRAP.md` in the upstream repo.
3. **Compare & Merge:**
   - Read my local command/skill files (e.g., in `.claude/commands/`, `.gemini/skills/`, or `plugins/`).
   - Identify the stack-specific values I previously filled in (commands for linting, testing, dev URLs, etc.).
   - Fetch the NEW templates from upstream and merge the new logic/steps into my local files.
   - **Constraint:** Do NOT revert my concrete stack commands back to `[BOOTSTRAP]` markers; keep the local implementations.
4. **Update Snippet:** Update the `CLAUDE.md`, `GEMINI.md`, or `AGENTS.md` snippet if the upstream version has improved.
5. **Report:** Summarize what new features or logic steps were added and confirm that local test/lint commands were preserved.
```

---

## For Maintainers: Syncing Adapters
If you have improved a template for one AI (e.g., Claude) and want to propagate that logic to the others (Gemini, Codex) within this repository, use this prompt:

```markdown
# Propagate Pattern Update
I have updated the core elephant/goldfish pattern in one of the adapters. Please propagate these changes across the entire repo:

1. **Analyze:** Look at the recent changes in `claude/commands/`, `gemini/commands/`, or `codex/skills/`.
2. **Propagate:** Apply the same logical updates (e.g., adding a new step, refining the goldfish prompt) to the other adapters.
3. **Adapt Syntax:** Ensure you respect the target platform's specific syntax:
   - **Claude:** Uses `Agent` tool and `.claude/commands/` format.
   - **Gemini:** Uses `invoke_agent` tool and `.gemini/skills/` format.
   - **Codex:** Uses `SKILL.md` format and `$eg-` skill mention syntax.
4. **Update Snippets:** Ensure the `snippet.md` or `gemini-md-snippet.md` files are updated if the command descriptions changed.
5. **Verify:** Confirm all `BOOTSTRAP.md` files still point to the correct updated paths.
```
