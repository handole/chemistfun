# Agents

Reusable agent role definitions for the Agency Designer skill.

Each file defines one agent's single responsibility, input/output contract, tools, and rules. These are loaded by the skill during `/web-design`, `/agents-make`, and `/marketing-pro` workflows.

## Included Agents

| Agent | File | Role |
|---|---|---|
| @visual-director | `visual-director.md` | Palette, typography, style selection |
| @motion-engineer | `motion-engineer.md` | GSAP, Framer Motion, scroll behavior |
| @copy-strategist | `copy-strategist.md` | Headlines, CTAs, conversion copy |
| @quality-auditor | `quality-auditor.md` | S-Tier rubric check (0–50 score) |
| @brief-analyst | `brief-analyst.md` | Parses vague briefs into structured specs |

## Using These Agents

The skill activates the right agents automatically based on your brief. You can also reference them directly:

- In Claude Code: the skill loads them via the `agents/` directory
- In Anthropic Managed Agents: use `docs/integrations/anthropic/define_your_agent.md` as the schema reference
- In Cursor / Copilot: the role definitions are loaded via `.cursorrules` and `.github/copilot-instructions.md`

## Adding Custom Agents

Create a new `.md` file in this directory following the same format:

```markdown
---
name: your-agent-name
description: One sentence describing what it does
---

# @your-agent-name

**Single responsibility:** ...
**Input:** ...
**Output:** ...
**Tools:** ...
**Does NOT:** ...
```
