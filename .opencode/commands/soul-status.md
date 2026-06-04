---
description: Soul Mode status report (read-only)
---

You are running Soul Mode status check.

Steps:
1) Read `.opencode/soul.md`.
2) Read the last 3 entries from `.opencode/soul/heartbeat.jsonl` (use `tail -3`).
3) Check if scheduler job `soul-heartbeat` exists and its cadence (list_jobs).
4) Output a concise status report:
   - Current focus (from soul.md)
   - Latest heartbeat age
   - Top 2-3 loose ends
   - Next scheduled heartbeat
   - How to steer (use `/steer-soul`)
