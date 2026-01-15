# Usage Guide

Daily workflows and common operations.

## Checking Configuration

### View Current Status

```bash
make status
```

Shows:
- Active mode (anthropic/bedrock)
- Bedrock status
- Model IDs
- AWS region/profile (if Bedrock)

### Validate Configuration

```bash
make validate
```

Checks:
- Mode file exists
- Config files exist
- All required settings present

## Mode Switching

### Interactive Mode Switching

Run `make switch` without arguments for interactive mode:

```bash
make switch
```

This will:
1. Show your current mode
2. Show the mode you'll switch to
3. Ask for confirmation
4. Switch if you confirm

Example output:
```
Current mode: anthropic
Switch to: bedrock

Switch to bedrock mode? (y/N)
```

### Switch Using Alias (From Anywhere)

After installation, you can use the `claude-switch` alias from any directory:

```bash
# Switch from anywhere (interactive)
cd ~/any/directory
claude-switch

# Or specify mode directly
claude-switch MODE=anthropic
claude-switch MODE=bedrock
```

This is convenient as you don't need to be in the repository directory.

### Switch to Anthropic Mode

```bash
make switch MODE=anthropic
```

Effects:
- Sets `CLAUDE_CODE_USE_BEDROCK=0`
- Loads Anthropic model IDs
- Uses direct Anthropic API
- Requires `ANTHROPIC_API_KEY`

### Switch to Bedrock Mode

```bash
make switch MODE=bedrock
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
make update
```

Workflow:
1. Prompts for confirmation
2. Runs `git pull`
3. Shows config changes via `make sync`
4. Instructions for manual updates

### Compare Templates

```bash
make sync
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
make switch MODE=anthropic  # or bedrock

# Verify changes
make status
```

## Skills Management

### List Available Skills

```bash
make skills-list
```

Shows all skills in repository.

### Install a Skill

```bash
make skills-install SKILL=skill-name
```

Copies from `./skills/skill-name` to `~/.claude/skills/skill-name`.

### Using Installed Skills

Skills in `~/.claude/skills/` are automatically available in Claude Code sessions.

## Agents Management

### List Available Agents

```bash
make agents-list
```

Shows all agents in repository.

### Install an Agent

```bash
make agents-install AGENT=agent-name
```

Copies from `./agents/agent-name` to `~/.claude/agents/agent-name`.

### Using Installed Agents

Agents in `~/.claude/agents/` are automatically available in Claude Code sessions.

## Settings Management

### View Settings Diff

```bash
make settings-diff
```

Compares:
- Template settings
- Current settings
- Shows changes needed

### Apply Settings Template

```bash
make settings-apply
```

Applies template with variable substitution from:
- Environment variables
- Personal config
- Current mode config

## MCP Management

### List MCP Servers

```bash
make mcp-list
```

Shows available MCP server implementations.

### Install MCP Server

```bash
make mcp-install MCP=server-name
```

Installs MCP server from `./mcp/servers/server-name`.

## Common Workflows

### Daily Development

```bash
# 1. Check current mode
make status

# 2. Switch if needed
make switch MODE=anthropic

# 3. Start coding
claude "help me with X"
```

### Adding New Content

```bash
# 1. Pull latest
git pull

# 2. Check for new skills/agents
make skills-list
make agents-list

# 3. Install if useful
make skills-install SKILL=new-skill
make agents-install AGENT=new-agent
```

### Updating After Pull

```bash
# 1. Pull changes
git pull

# 2. Check what changed
make sync

# 3. Review changelog
cat CHANGELOG.md

# 4. Update personal config if needed
nano ~/.claude/configs/personal.toml

# 5. Re-apply
make switch MODE=anthropic
```

### Working on Multiple Machines

**On Dev Laptop:**
```bash
cd ~/Documents/dev_work/personal_productivity/making_my_agentic_setup_brrrrrr
make status
# Uses ~/.claude/configs/personal.toml
```

**On VPS:**
```bash
cd ~/making_my_agentic_setup_brrrrrr
make status
# Uses same ~/.claude/configs/personal.toml
# Different repo location, same personal configs
```

### Troubleshooting

```bash
# Validate configuration
make validate

# Check environment loading
claude-mode-load
env | grep ANTHROPIC
env | grep CLAUDE

# Re-apply mode
make switch MODE=anthropic

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

1. **Always validate after changes**: Run `make validate` after editing configs
2. **Use personal overrides**: Don't modify base templates
3. **Check sync regularly**: Run `make sync` after git pull
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
make switch MODE=anthropic
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
