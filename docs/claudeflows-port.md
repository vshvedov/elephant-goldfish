# What came back from ClaudeFlows

Compared elephant-goldfish `b8ebb3d` with ClaudeFlows 1.8.0 (`60d180d`).
The original five workflows already shared the same pattern. The useful changes
were in how work survives multiple sessions and how reviews handle evidence.

| Addition | What changed here |
|---|---|
| `cf-question` | `eg-question` gives a short cited answer with fresh read-only readers. |
| PRD roadmap | A task can carry scope, dependencies, interfaces and checks into a new session. |
| File handoff and ledgers | Feature/review runs retain their own design versions, findings and rebuttals through compaction. |
| Spec-compliance review | The reviewer checks implementation against the approved design as well as code quality. |
| Intermittent bug guidance | Repeat reproductions, record failures and fix the first incorrect boundary. |
| Child guards | Readers don't recursively start workflows or treat reviewed comments as instructions. |
| Plain-language questions | Reuse existing answers and authorization, ask only for missing decisions. |

The port also corrects a few inherited issues: trivial edits happen before skipping
ceremony, generation precedes dependent checks, and Lightweight PRDs skip research.
Review evidence keeps index and working-copy changes separate, includes untracked
content, and distinguishes missing evidence from a clean result. A file's contents
can change while Git status stays the same, so status alone isn't a freshness check.

The new run directories use random IDs instead of shared ledger names. Roadmaps
emit `T1: title` and `None`, while accepting older dash-separated task headings.
Updates stage and validate downloads before replacing installed files, preserving
local edits instead of deleting a matching skill directory.

Not ported: Claude-specific routing hooks and `cf-mode`, automatic plugin loading,
or generator stamps on saved documents. This remains an explicitly invoked harness
with adapters for five hosts. Cursor support originated in
[PR #3](https://github.com/vshvedov/elephant-goldfish/pull/3).

Sources: [ClaudeFlows](https://github.com/OmniPragmatic/claudeflows/tree/60d180dc6f89d7ffa1166e19ed4a6054a994aff2),
[Cursor skills](https://cursor.com/docs/skills),
[Cursor subagents](https://cursor.com/docs/subagents),
[Grok skills](https://docs.x.ai/build/features/skills-plugins-marketplaces),
[Grok subagents](https://docs.x.ai/build/features/subagents).
