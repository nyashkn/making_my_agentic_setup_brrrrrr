# Agents

This directory contains shared Claude Code agents.

## Structure

Each agent should be in its own directory:

```
agents/
├── custom-agent-1/
│   ├── agent.yaml          # Agent definition
│   ├── README.md           # Usage documentation
│   └── examples/           # Example usage (optional)
└── custom-agent-2/
    └── ...
```

## Installing Agents

```bash
# List available agents
task agents:list

# Install an agent to ~/.claude/agents/
task agents:install -- agent-name
```

## Creating Agents

1. Create a new directory in `agents/`
2. Add `agent.yaml` with agent definition
3. Add `README.md` with usage instructions
4. Commit to repo for team sharing
5. Others can install with `task agents:install`

## Agent Definition Example

```yaml
# agents/my-agent/agent.yaml
name: my-agent
description: Brief description
version: 1.0.0
```

See Claude Code documentation for full agent specification.

## Usage

After installation, agents are available in `~/.claude/agents/` and can be invoked in Claude Code sessions.
