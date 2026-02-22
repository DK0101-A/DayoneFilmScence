---
description: Interactively steer Soul Mode (update focus/preferences/cadence)
---

You are steering Soul Mode.

Steps:
1) Read current `.opencode/soul.md`.
2) Listen for user guidance on:
   - New/changed goals
   - Updated preferences (tone, format, boundaries)
   - Changed current focus
   - New loose ends to track
   - Desired heartbeat cadence change
3) If user provides explicit values, apply them directly:
   - Update goals, preferences, focus, loose ends in `.opencode/soul.md`
   - If cadence changes, update the `soul-heartbeat` scheduler job
4) Summarize exactly what changed.

Constraints:
- Keep changes small and reversible
- Do not delete existing content without explicit user request
- If no explicit changes provided, ask clarifying questions
