# Usage Guide

Daily workflows and common operations.

## Checking Configuration

### View Current Status

```bash
task status
```

Shows:
- Active mode (anthropic/bedrock)
- Bedrock status
- Model IDs
- AWS region/profile (if Bedrock)

### Validate Configuration

```bash
task validate
```

Checks:
- Mode file exists
- Config files exist
- All required settings present

## Mode Switching

### Switch to Anthropic Mode

```bash
task switch -- anthropic
```

Effects:
- Sets `CLAUDE_CODE_USE_BEDROCK=0`
- Loads Anthropic model IDs
- Uses direct Anthropic API
- Requires `ANTHROPIC_API_KEY`

### Switch to Bedrock Mode

```bash
task switch -- bedrock
```

Effects:
- Sets `CLAUDE_CODE_USE_BEDROCK=1`
- Loads Bedrock ARNs
- Uses AWS Bedrock API
- Requires AWS credentials

### Verify Mode Change

```bash
# Check environment variables
echo $CLAUDE_CODE_USE_BEDROCK
echo $ANTHROPIC_MODEL
echo $AWS_REGION
```

## Updating Configuration

### Pull Latest Changes

```bash
task update
```

Workflow:
1. Prompts for confirmation
2. Runs `git pull`
3. Shows config changes via `task sync`
4. Instructions for manual updates

### Compare Templates

```bash
task sync
```

Shows:
- Repository version vs your version
- New variables in templates
- Changed default values
- Relevant changelog entries

### Apply Changes

After reviewing changes:

```bash
# Edit personal config
nano ~/.claude/configs/personal.toml

# Re-apply configuration
task switch -- anthropic  # or bedrock

# Verify changes
task status
```

## Skills Management

### List Available Skills

```bash
task skills:list
```

Shows all skills in repository.

### Install a Skill

```bash
task skills:install -- skill-name
```

Copies from `./skills/skill-name` to `~/.claude/skills/skill-name`.

### Using Installed Skills

Skills in `~/.claude/skills/` are automatically available in Claude Code sessions.

## Agents Management

### List Available Agents

```bash
task agents:list
```

Shows all agents in repository.

### Install an Agent

```bash
task agents:install -- agent-name
```

Copies from `./agents/agent-name` to `~/.claude/agents/agent-name`.

### Using Installed Agents

Agents in `~/.claude/agents/` are automatically available in Claude Code sessions.

## Settings Management

### View Settings Diff

```bash
task settings:diff
```

Compares:
- Template settings
- Current settings
- Shows changes needed

### Apply Settings Template

```bash
task settings:apply
```

Applies template with variable substitution from:
- Environment variables
- Personal config
- Current mode config

## MCP Management

### List MCP Servers

```bash
task mcp:list
```

Shows available MCP server implementations.

### Install MCP Server

```bash
task mcp:install -- server-name
```

Installs MCP server from `./mcp/servers/server-name`.

## Common Workflows

### Daily Development

```bash
# 1. Check current mode
task status

# 2. Switch if needed
task switch -- anthropic

# 3. Start coding
claude "help me with X"
```

### Adding New Content

```bash
# 1. Pull latest
git pull

# 2. Check for new skills/agents
task skills:list
task agents:list

# 3. Install if useful
task skills:install -- new-skill
task agents:install -- new-agent
```

### Updating After Pull

```bash
# 1. Pull changes
git pull

# 2. Check what changed
task sync

# 3. Review changelog
cat CHANGELOG.md

# 4. Update personal config if needed
nano ~/.claude/configs/personal.toml

# 5. Re-apply
task switch -- anthropic
```

### Working on Multiple Machines

**On Dev Laptop:**
```bash
cd ~/Documents/dev_work/personal_productivity/making_my_agentic_setup_brrrrrr
task status
# Uses ~/.claude/configs/personal.toml
```

**On VPS:**
```bash
cd ~/making_my_agentic_setup_brrrrrr
task status
# Uses same ~/.claude/configs/personal.toml
# Different repo location, same personal configs
```

### Troubleshooting

```bash
# Validate configuration
task validate

# Check environment loading
claude-mode-load
env | grep ANTHROPIC
env | grep CLAUDE

# Re-apply mode
task switch -- anthropic

# Check logs
tail -f ~/.claude/logs/*.log  # if logging enabled
```

## Environment Variables

Key variables set by modes:

**Common:**
- `CLAUDE_CODE_USE_BEDROCK` - 0 or 1
- `ANTHROPIC_MODEL` - Primary model ID
- `ANTHROPIC_DEFAULT_HAIKU_MODEL`
- `ANTHROPIC_DEFAULT_SONNET_MODEL`
- `ANTHROPIC_DEFAULT_OPUS_MODEL`
- `CLAUDE_CODE_SUBAGENT_MODEL`

**Bedrock Mode:**
- `AWS_REGION` - AWS region
- `AWS_PROFILE` - AWS profile name

**Optional:**
- `DISABLE_PROMPT_CACHING` - 0 or 1
- `DISABLE_TELEMETRY` - 0 or 1
- `PLAYWRIGHT_HEADLESS` - true or false
- `MAX_THINKING_TOKENS` - Number

## Tips

1. **Always validate after changes**: Run `task validate` after editing configs
2. **Use personal overrides**: Don't modify base templates
3. **Check sync regularly**: Run `task sync` after git pull
4. **Mode switching is instant**: No restart needed
5. **Reload shell after install**: `source ~/.zshrc`

## Advanced Usage

### Custom Mode Override

Temporarily override mode without switching:

```bash
# Use Opus for one command
ANTHROPIC_MODEL="claude-opus-4-5" claude "complex task"

# Use different region
AWS_REGION="eu-west-1" claude "task"
```

### Manual Configuration

```bash
# Edit generated env file directly (not recommended)
nano ~/.claude/configs/anthropic.env

# Better: edit personal.toml and re-apply
nano ~/.claude/configs/personal.toml
task switch -- anthropic
```

### Version Management

```bash
# Check installed version
cat ~/.claude/configs/.version

# Check repository version
cat VERSION

# Force version update
cp VERSION ~/.claude/configs/.version
```

Last updated: 2025-01-14
