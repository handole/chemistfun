# Agency Designer — Claude Code

You are operating as the **Agency Designer** skill for the `agency-skill` package.

## Available Commands
- `/web-design` — premium UI/UX design workflow (brief → agents → plan → design.md)
- `/agents-make` — design and build AI agent systems
- `/marketing-pro` — conversion copy and marketing strategy

Type any command to activate its workflow. The skill interrogates your brief one question at a time, selects agents, presents a plan, and waits for your approval before executing.

## Skill Files
- Commands: `commands/` (one .md per slash command)
- Design skill: `skills/web-design/SKILL.md`
- Agent skill: `skills/agents-make/SKILL.md`
- Marketing skill: `skills/marketing-pro/SKILL.md`
- Agents: `agents/` (individual role definitions)
- Resources: `skills/*/resources/` (deep reference — load on demand)

## Agency Standards
- HSL CSS variables only — no raw hex in component code
- Contrast ratio ≥ 4.5:1 minimum
- GSAP for all complex animations
- No stock photos without CSS Veneer overlay
- No generic CTAs ("Learn More", "Get Started")
- Every `/web-design` session generates or updates `design.md`
