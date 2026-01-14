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

- **Task** - Modern command runner (replaces Make + bash)
- **UV** - Fast Python package manager
- **TOML** - Structured configs (replaces .env)
- **Python 3.11+** - All logic in Python (no bash scripts)

## Prerequisites

Install these first:

```bash
# UV (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Task (command runner)
brew install go-task  # macOS
# or
curl -sL https://taskfile.dev/install.sh | sh  # Linux
```

## Quick Start

```bash
# 1. Clone repository (anywhere you want)
git clone <your-repo> ~/making_my_agentic_setup_brrrrrr
cd ~/making_my_agentic_setup_brrrrrr

# 2. Run installation
task install
# Prompts for mode (anthropic/bedrock)
# Creates ~/.claude/configs/personal.toml
# Adds shell integration to ~/.zshrc

# 3. Edit personal configs with your credentials
nano ~/.claude/configs/personal.toml

# 4. Reload shell
source ~/.zshrc

# 5. Verify setup
task status
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
task --list

# Check current configuration
task status

# Switch modes
task switch -- anthropic
task switch -- bedrock

# Validate configuration
task validate

# Check for updates
task update

# Compare templates with your config
task sync

# Skills management
task skills:list
task skills:install -- skill-name

# Agents management
task agents:list
task agents:install -- agent-name

# Settings management
task settings:apply
task settings:diff

# MCP management
task mcp:list
task mcp:install -- server-name
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
task sync
# Shows: version diff, changelog, new variables

# 3. Review and update personal config
nano ~/.claude/configs/personal.toml

# 4. Re-apply configuration
task switch -- anthropic  # or bedrock
```

## Structure

```
making_my_agentic_setup_brrrrrr/
├── Taskfile.yml              # All commands
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
task install
nano ~/.claude/configs/personal.toml  # Add credentials
task status

# New skill added to repo? Pull and install
git pull
task skills:list  # See new-awesome-skill
task skills:install -- new-awesome-skill
# Copies from ./skills/new-awesome-skill to ~/.claude/skills/new-awesome-skill

# Switch modes anytime
task switch -- bedrock
task switch -- anthropic

# On VPS - same workflow, different location
cd ~
git clone <repo> making_my_agentic_setup_brrrrrr
task install
# Uses same ~/.claude/configs but different repo location
```

## Benefits

- No bash scripts (all Python)
- Portable (works on dev, VPS, home server)
- Personal overrides (don't duplicate configs)
- Version tracking (know what changed)
- Extensible (easy to add skills/agents/commands)
- Modern stack (Task + UV + TOML)

## Documentation

- `docs/setup.md` - Detailed setup guide
- `docs/usage.md` - Usage patterns
- `docs/extending.md` - Adding skills/agents/commands
- `CHANGELOG.md` - Version history

## Version

Current: v0.1.0

Last updated: 2025-01-14
