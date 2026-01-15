# Making My Agentic Setup Brrrrrr!

Modern, portable configuration management for Claude Code agentic development environment.

## What This Does

- Claude Code mode switching (Anthropic API / AWS Bedrock)
- Portable across dev machines, VPS, home servers
- Skills, agents, commands, and MCP tools management
- Settings.json templates
- Update detection with version tracking
- Personal config overrides (merge pattern)

## Stack

- **Make** - Universal task automation (pre-installed on most systems)
- **UV** - Fast Python package manager
- **TOML** - Structured configs (replaces .env)
- **Python 3.11+** - All logic in Python (no bash scripts)

## Prerequisites

### UV (Required)

UV is the Python package manager.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Verify installation:**
```bash
uv --version
```

**Note:** Make is used for task automation and is pre-installed on macOS and most Linux distributions.

## Quick Start

```bash
# 1. Clone repository (anywhere you want)
git clone <your-repo> ~/making_my_agentic_setup_brrrrrr
cd ~/making_my_agentic_setup_brrrrrr

# 2. Run installation
make install
# Prompts for mode (anthropic/bedrock)
# Creates ~/.claude/configs/personal.toml
# Adds shell integration and claude-switch alias to ~/.zshrc

# 3. Edit personal configs with your credentials
nano ~/.claude/configs/personal.toml

# 4. Reload shell
source ~/.zshrc

# 5. Verify setup
make status
```

## Repository Location Philosophy

**Flexible**: Clone and work from anywhere
- Dev laptop: `~/Documents/dev_work/personal_productivity/making_my_agentic_setup_brrrrrr`
- VPS: `~/making_my_agentic_setup_brrrrrr`
- Home server: `/opt/making_my_agentic_setup_brrrrrr`

**Personal configs**: Always in `~/.claude/` (consistent location)
- `~/.claude/configs/personal.toml` - Your overrides
- `~/.claude/configs/current_mode` - Active mode
- `~/.claude/skills/` - Installed skills
- `~/.claude/agents/` - Installed agents

**How it works**:
- Templates live in repo (version controlled, shareable)
- Personal configs in ~/.claude/ (your secrets, never committed)
- Task auto-detects repo location via `{{.ROOT_DIR}}`
- Python auto-detects via `Path(__file__).parent.parent`

## Key Commands

```bash
# Show available commands
make help

# Check current configuration
make status

# Switch modes (interactive - prompts for confirmation)
make switch

# Switch modes (direct)
make switch MODE=anthropic
make switch MODE=bedrock

# Switch from anywhere (after install)
claude-switch
claude-switch MODE=anthropic
claude-switch MODE=bedrock

# Validate configuration
make validate

# Check for updates
make update

# Compare templates with your config
make sync

# Skills management
make skills-list
make skills-install SKILL=skill-name

# Agents management
make agents-list
make agents-install AGENT=agent-name

# Settings management
make settings-apply
make settings-diff

# MCP management
make mcp-list
make mcp-install MCP=server-name
```

## Configuration

### Personal Overrides

Edit `~/.claude/configs/personal.toml` to override defaults:

```toml
# Only specify what you want to override

[aws]
region = "us-west-2"
profile = "work"

[models]
primary = "claude-opus-4-5"  # Use Opus as default

[optional]
disable_telemetry = true
```

### Modes

**Anthropic Mode** (`configs/anthropic.toml`):
- Direct Anthropic API
- Model IDs: `claude-sonnet-4-5`, `claude-opus-4-5`
- No AWS credentials needed

**Bedrock Mode** (`configs/bedrock.toml`):
- AWS Bedrock API
- Full ARNs: `us.anthropic.claude-sonnet-4-5-20250929-v1:0`
- Requires AWS credentials

## Update Workflow

```bash
# 1. Pull latest changes
git pull

# 2. Check what changed
make sync
# Shows: version diff, changelog, new variables

# 3. Review and update personal config
nano ~/.claude/configs/personal.toml

# 4. Re-apply configuration
make switch MODE=anthropic  # or bedrock
```

## Structure

```
making_my_agentic_setup_brrrrrr/
├── Makefile                  # All commands
├── configs/                  # TOML templates
│   ├── anthropic.toml
│   ├── bedrock.toml
│   └── personal.toml.example
├── tools/                    # Python scripts
│   ├── config.py            # Main config management
│   ├── sync.py              # Update detection
│   ├── install.py           # Installation
│   └── validate.py          # Validation
├── shell/
│   └── zsh-functions.sh     # Auto-load environment
├── skills/                   # Shared skills
├── agents/                   # Shared agents
├── commands/                 # Custom commands
├── mcp/                      # MCP servers
├── settings/                 # Settings templates
└── docs/                     # Documentation
```

## How It Works

1. **Templates in repo**: Base configs, skills, agents (version controlled)
2. **Personal in ~/.claude/**: Your overrides and secrets (git-ignored)
3. **Merge pattern**: Personal overrides merge into base configs
4. **Auto-detection**: Works from any location
5. **Update detection**: VERSION file tracks changes
6. **Shell integration**: Auto-loads correct mode on startup

## Installation Locations

**Repository** (can be anywhere):
```
/Users/njui/Documents/dev_work/personal_productivity/making_my_agentic_setup_brrrrrr
~/making_my_agentic_setup_brrrrrr
/opt/making_my_agentic_setup_brrrrrr
```

**Personal Configs** (always ~/.claude/):
```
~/.claude/configs/personal.toml
~/.claude/configs/current_mode
~/.claude/configs/anthropic.env
~/.claude/configs/bedrock.env
~/.claude/skills/
~/.claude/agents/
```

## Example Workflow

```bash
# On dev laptop - clone wherever
cd ~/Documents/dev_work/personal_productivity
git clone <repo> making_my_agentic_setup_brrrrrr
cd making_my_agentic_setup_brrrrrr

# Install and configure
make install
nano ~/.claude/configs/personal.toml  # Add credentials
make status

# New skill added to repo? Pull and install
git pull
make skills-list  # See new-awesome-skill
make skills-install SKILL=new-awesome-skill
# Copies from ./skills/new-awesome-skill to ~/.claude/skills/new-awesome-skill

# Switch modes anytime
make switch MODE=bedrock
make switch MODE=anthropic

# On VPS - same workflow, different location
cd ~
git clone <repo> making_my_agentic_setup_brrrrrr
make install
# Uses same ~/.claude/configs but different repo location
```

## Benefits

- No bash scripts (all Python)
- Portable (works on dev, VPS, home server)
- Personal overrides (don't duplicate configs)
- Version tracking (know what changed)
- Extensible (easy to add skills/agents/commands)
- Universal (Make + UV + TOML - works everywhere)

## Documentation

- `docs/setup.md` - Detailed setup guide
- `docs/usage.md` - Usage patterns
- `docs/extending.md` - Adding skills/agents/commands
- `CHANGELOG.md` - Version history

## Version

Current: v0.1.0

Last updated: 2025-01-14
