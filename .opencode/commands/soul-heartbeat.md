---
description: Soul Mode heartbeat (non-interactive check-in)
agent: soul
---

You are running Soul Mode heartbeat.

Constraints:
- Non-interactive: do not ask questions and do not wait for permissions.
- Safe: no destructive actions.

Steps:
1) Read `.opencode/soul.md`.
2) Get workspace path via `pwd`.
3) Try to query OpenCode's sqlite db for recent sessions + open todos for THIS workspace directory.
   - Common db paths: `$XDG_DATA_HOME/opencode/opencode.db`, `$HOME/.local/share/opencode/opencode.db`, `$HOME/Library/Application Support/opencode/opencode.db`, `$HOME/.opencode/opencode.db`.
   - If db lookup fails, continue without it.
   - Prefer these queries (adjust if schema differs):
     - Recent sessions:
       `SELECT id, title, time_updated FROM session WHERE directory = '<pwd>' ORDER BY time_updated DESC LIMIT 8;`
     - Open todos:
       `SELECT s.title AS session_title, t.content, t.status, t.priority, t.time_updated FROM todo t JOIN session s ON s.id = t.session_id WHERE s.directory = '<pwd>' AND t.status != 'completed' ORDER BY t.time_updated DESC LIMIT 20;`
4) Output a concise check-in:
   - 1 sentence summary
   - Loose ends (1-3 bullets)
   - Next action (1 bullet)
   - Curiosity paths (3 bullets: Work / Topics / Improvements)
5) Append ONE JSON line to `.opencode/soul/heartbeat.jsonl` with keys: `ts`, `workspace`, `summary`, `loose_ends`, `next_action`.
6) Append using a heredoc `cat >>` so quoting is safe.
