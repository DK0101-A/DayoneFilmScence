---
description: Remove Soul Mode (delete job + remove files)
---

Take my soul back.

Do the following in order:
1) Delete the scheduled job named `soul-heartbeat`.
2) Remove these files/directories if they exist:
   - `.opencode/soul.md`
   - `.opencode/soul/`
   - `.opencode/agents/soul.md`
   - `.opencode/commands/soul-heartbeat.md`
   - `.opencode/commands/take-my-soul-back.md`
3) Update `opencode.json*`:
   - Remove `.opencode/soul.md` from `instructions`.
   - If you added `opencode-scheduler` only for Soul Mode, remove it.

When done, say exactly what you deleted/changed.
