---
description: Build production-ready agent systems using Anthropic-style agent definitions, tools, skills, MCP, and session planning
---

# /agents-make — Agency Designer Agent Builder

You are activating the **Agency Designer /agents-make** skill. Follow every phase in order.

Read `skills/agents-make/SKILL.md` before executing. Agent tree definitions are in `skills/agents-make/resources/AGENT_TREE.md`.

---

## Core Standard

Do not stop at generic role ideas like "research agent" or "designer agent".

When a user invokes `/agents-make`, produce a definition that matches an Anthropic-grade agent design:

- reusable agent config
- explicit model choice
- system prompt with boundaries
- tool list
- MCP servers if needed
- attached skills if needed
- callable agents if orchestration is needed
- environment assumptions
- session execution plan
- evaluation and failure rules

If the platform is not Anthropic Managed Agents, preserve the same rigor and adapt the syntax to that runtime.

---

## Phase 1 — Brief Interrogation (one question at a time)

Ask only what is missing. Prefer one question at a time.

1. **TASK** — what job should the agent system accomplish?
2. **PLATFORM** — Claude Managed Agents / Claude Code / Copilot / Cursor / Gemini / custom runtime?
3. **SCOPE** — single agent, sequential pipeline, or director tree?
4. **OUTPUT** — what should the final run produce?
5. **TOOLS** — what tools or integrations are required?
6. **ENVIRONMENT** — does it need network access, credentials, files, APIs, or long-running execution?
7. **QUALITY BAR** — what would count as failure even if the task technically completes?

---

## Phase 2 — System Design

Based on the brief, design the system first:

- If single agent: define one reusable agent config with execution boundaries.
- If pipeline: define each agent, its inputs, outputs, and handoff contract.
- If tree: define the director, its callable agents, routing rules, and merge logic.

State the design clearly before the plan.

Always include:

1. Agent names
2. Single responsibility for each
3. Model choice for each
4. Tools for each
5. Skills for each if relevant
6. Callable-agent relationships
7. Final audit path

---

## Phase 3 — Agent Definition Output

Produce a structured definition using this exact order:

1. **Agent Definition**

```json
{
	"name": "...",
	"model": "...",
	"description": "...",
	"system": "...",
	"tools": [],
	"mcp_servers": [],
	"skills": [],
	"callable_agents": [],
	"metadata": {}
}
```

2. **Environment Definition**

- container or runtime assumptions
- network access
- secrets
- filesystems or artifacts

3. **Session Plan**

- initial task payload
- expected event flow
- stop conditions
- completion artifacts

4. **Quality Gates**

- what must be true before the system is considered production-ready

5. **Implementation Plan**

- numbered steps for creating or wiring the system

If the user asks for actual files, API payloads, or runnable config, generate them.

If the user is asking for planning only, stop after the plan.
If the user is asking to build, proceed after presenting the design unless the platform requires confirmation.

---

## Phase 4 — Execute

Execute each step. Reference:
- `skills/agents-make/SKILL.md` — orchestration protocol
- `skills/agents-make/resources/AGENT_TREE.md` — agent role library
- `agents/` — reusable role examples from this package
- `docs/integrations/anthropic/managed_agents_overview.md` — runtime model
- `docs/integrations/anthropic/define_your_agent.md` — agent config shape
- `docs/integrations/anthropic/skills.md` — skill attachment model

During execution:

1. Keep reusable knowledge in skill files, not bloated system prompts.
2. Keep tool access narrow.
3. Separate agent definition from live session behavior.
4. Add callable agents only when delegation is real and useful.
5. Include failure handling, blocked-state behavior, and test criteria.

---

## Sub-commands available under /agents-make

- `/agents-make single` — define one production-ready agent
- `/agents-make pipeline` — define a sequential agent pipeline with handoff contracts
- `/agents-make director` — define a director plus callable sub-agents
- `/agents-make managed` — generate an Anthropic Managed Agents-style spec
- `/agents-make mcp` — define MCP servers and tool boundaries for the agent system
- `/agents-make audit` — review an existing agent system for contract gaps, tool sprawl, and runtime risk
