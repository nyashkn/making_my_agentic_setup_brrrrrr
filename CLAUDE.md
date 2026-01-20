# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a portable configuration management system for Claude Code that enables:
- Mode switching between Anthropic API and AWS Bedrock
- Centralized management of skills, agents, commands, and MCP servers
- Personal config overrides using a merge pattern
- Version tracking and update detection

## Build & Development Commands

```bash
# Initial setup (creates venv, installs dependencies, sets up ~/.claude/)
make install

# Check current configuration status
make status

# Validate configuration files
make validate

# Switch between modes
make switch MODE=anthropic  # or MODE=bedrock
make switch                 # interactive mode

# Pull updates and compare with personal config
make update
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

# MCP server management
make mcp-list
make mcp-install MCP=server-name

# Notifications management
make notifications-list                    # List available backends
make notifications-install BACKEND=<name>  # Install a backend
make notifications-enable BACKEND=<name>   # Enable notification hooks
make notifications-disable                 # Disable all notifications
make notifications-test [BACKEND=<name>]   # Send test notification
make notifications-status                  # Show notification status
```

## Architecture

### Configuration System

The configuration system uses a **merge pattern** where:

1. **Base templates** (`configs/anthropic.toml`, `configs/bedrock.toml`) contain default settings
2. **Personal overrides** (`~/.claude/configs/personal.toml`) merge on top of base configs
3. **Mode-specific env files** (`~/.claude/configs/anthropic.env`, `bedrock.env`) are generated from merged config
4. **Shell integration** (`shell/zsh-functions.sh`) auto-loads the active mode's environment

**Key insight**: Users only specify what they want to override in `personal.toml`, avoiding duplication of entire config files.

### Location Philosophy

- **Repository**: Can be cloned anywhere (auto-detected via `Path(__file__).parent.parent` in Python tools)
- **Personal configs**: Always in `~/.claude/` (consistent location across machines)
- **Portability**: Same repo works on dev laptops, VPS, home servers without modification

### Directory Structure

```
making_my_agentic_setup_brrrrrr/
├── configs/           # TOML templates (version controlled)
│   ├── anthropic.toml      # Anthropic API mode defaults
│   ├── bedrock.toml        # AWS Bedrock mode defaults
│   └── personal.toml.example
├── tools/             # Python scripts (all logic here, no bash scripts)
│   ├── config.py      # Mode switching, env generation
│   ├── install.py     # First-time setup
│   ├── sync.py        # Update detection
│   └── validate.py    # Config validation
├── skills/            # Shared skill definitions
├── agents/            # Shared agent definitions
├── commands/          # Custom CLI commands
├── mcp/servers/       # MCP server implementations
├── settings/          # Settings.json templates
└── shell/             # Shell integration scripts

~/.claude/             # Personal installation (never in git)
├── configs/
│   ├── personal.toml         # User overrides
│   ├── current_mode          # Active mode (anthropic|bedrock)
│   ├── anthropic.env         # Generated env vars
│   └── bedrock.env           # Generated env vars
├── skills/            # Installed skills
├── agents/            # Installed agents
└── mcp/servers/       # Installed MCP servers
```

### Python Tools Architecture

All tools follow these patterns:

1. **Auto-detect repo location**: `REPO_DIR = Path(__file__).parent.parent.resolve()`
2. **Use Rich for output**: `from rich.console import Console`
3. **Personal config location**: `CONFIG_DIR = Path.home() / ".claude" / "configs"`
4. **TOML for configs**: Use `tomli` (read) and `tomli_w` (write)

**config.py** is the core tool:
- `load_config(mode)`: Loads base config + personal overrides (deep merge)
- `apply_config(config)`: Generates environment variable exports
- `switch_mode(mode)`: Applies new mode and updates `current_mode` file
- `status()`: Displays current configuration in a Rich table

### Mode System

**Anthropic mode** (`configs/anthropic.toml`):
- `use_bedrock = false`
- Model IDs: `claude-sonnet-4-5`, `claude-opus-4-5`
- No AWS credentials required

**Bedrock mode** (`configs/bedrock.toml`):
- `use_bedrock = true`
- Full ARNs: `us.anthropic.claude-sonnet-4-5-20250929-v1:0`
- Requires AWS region and profile configuration

Generated env vars include:
- `CLAUDE_CODE_USE_BEDROCK`
- `ANTHROPIC_MODEL` (primary model)
- `ANTHROPIC_DEFAULT_HAIKU_MODEL`, `*_SONNET_MODEL`, `*_OPUS_MODEL`
- `CLAUDE_CODE_SUBAGENT_MODEL`
- `AWS_REGION`, `AWS_PROFILE` (bedrock only)
- Optional: `MAX_THINKING_TOKENS`, `DISABLE_PROMPT_CACHING`, `DISABLE_TELEMETRY`, `PLAYWRIGHT_HEADLESS`

## Working with Agents

This repo contains custom agent definitions (`.md` files with YAML frontmatter):

**Existing agents**:
- `code-reviewer-buddy.md`: Reviews code for quality, security, maintainability
- `code-reviewer-buddy-tooled.md`: Enhanced reviewer with Context7 and Tavily search for research
- `smelly-comments.md`: Reviews code comments for quality issues

**Agent frontmatter structure**:
```yaml
---
name: agent-name
description: What the agent does
tools: Read, Grep, Glob, Bash  # Tools it can use
model: sonnet  # or haiku, opus
---
```

**Installing agents**:
```bash
make agents-list               # See available agents
make agents-install AGENT=code-reviewer-buddy-tooled
# Copies from ./agents/code-reviewer-buddy-tooled.md to ~/.claude/agents/
```

## Notification System

Get notified when Claude Code tasks complete or require input across multiple terminal instances.

### Why Notifications?

When running multiple Claude Code instances in different terminals, it's hard to know which one finished or needs input. The notification system solves this by:

- Sending desktop notifications when tasks complete
- Alerting when Claude needs permissions or input
- Supporting multi-instance awareness (cc-notifier)
- Enabling click-to-focus to jump to the relevant window

### Available Backends

| Backend | Dependencies | Multi-Instance | Click-to-Focus | Best For |
|---------|--------------|----------------|----------------|----------|
| **osascript** | None (macOS built-in) | ❌ | ❌ | Quick setup, single instance |
| **terminal-notifier** | Homebrew | ❌ | ❌ | Better branding |
| **cc-notifier** | Hammerspoon, terminal-notifier | ✅ | ✅ | Multiple instances |

### Quick Start

```bash
# List available backends
make notifications-list

# Install osascript (simplest, zero dependencies)
make notifications-install BACKEND=osascript
make notifications-enable BACKEND=osascript

# Or install cc-notifier (advanced, multi-instance aware)
make notifications-install BACKEND=cc-notifier
make notifications-enable BACKEND=cc-notifier

# Test it
make notifications-test
```

### Configuration

Customize notification settings in your personal config:

```toml
# ~/.claude/configs/personal.toml

[notifications]
backend = "osascript"  # or terminal-notifier, cc-notifier
sound = "Glass"        # Glass, Submarine, Frog, Purr, etc.

# Optional: For cc-notifier remote notifications
pushover_api_token = "your_token"
pushover_user_key = "your_key"
```

After editing, regenerate environment:

```bash
make switch MODE=anthropic  # or bedrock
```

### Multi-Instance Workflow (cc-notifier)

cc-notifier tracks which terminal/IDE window has Claude running:

1. **Terminal 1**: Start Claude Code in project A
2. **Terminal 2**: Start Claude Code in project B
3. **Terminal 1**: Give Claude a task, then switch to Terminal 2
4. When Terminal 1 finishes → notification appears
5. Click notification → jumps back to Terminal 1 across Spaces

This solves the problem of multiple Claude instances by identifying which one finished.

### Hooks Enabled

The notification system uses Claude Code hooks:

- **Stop**: When main agent finishes responding
- **SubagentStop**: When subagents complete tasks
- **Notification**: Permission prompts, idle alerts, input dialogs
- **PermissionRequest**: When permission dialogs appear
- **SessionStart/SessionEnd**: Window tracking (cc-notifier only)

### Remote Support (cc-notifier)

When working over SSH, cc-notifier sends push notifications to your phone via Pushover:

1. Configure Pushover credentials in personal.toml
2. SSH to remote machine
3. Start Claude Code
4. Get push notifications on iOS/Android when tasks complete

### Documentation

For comprehensive guide including troubleshooting:

```bash
cat docs/notifications.md
# or view on GitHub
```

## Extending the System

### Adding New Config Variables

1. Add to base template (`configs/anthropic.toml` or `bedrock.toml`)
2. Update `tools/config.py` in `apply_config()` to export the variable
3. Update `CHANGELOG.md` and increment `VERSION` file
4. Commit changes

Users will see updates via `make sync` after `git pull`.

### Adding Skills/Agents

1. Create directory in `skills/` or `agents/`
2. Add definition file (YAML or .md with frontmatter)
3. Add README.md with usage docs
4. Commit to repo
5. Others install with `make skills-install SKILL=name` or `make agents-install AGENT=name`

This copies from repo to `~/.claude/skills/` or `~/.claude/agents/`.

### Adding Python Tools

Create in `tools/`, follow existing patterns:
- Use `REPO_DIR = Path(__file__).parent.parent.resolve()` for repo location
- Use `CONFIG_DIR = Path.home() / ".claude" / "configs"` for personal configs
- Use Rich Console for output
- Add corresponding Makefile target if needed

## Dependencies

- **uv**: Python package manager (install: `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **Python 3.11+**: Required for all tools
- **Make**: Task runner (pre-installed on macOS/Linux)

Python packages (installed via `make install`):
- `tomli`, `tomli-w`: TOML parsing
- `rich`: Terminal formatting
- `jinja2`: Template rendering

## Update Workflow

When pulling updates:

1. `git pull` to get latest changes
2. `make sync` to see version diff, changelog, new variables
3. Review and update `~/.claude/configs/personal.toml` if needed
4. `make switch MODE=<current-mode>` to regenerate env files
5. `make status` to verify

VERSION file tracks semantic versions. CHANGELOG.md documents all changes.
