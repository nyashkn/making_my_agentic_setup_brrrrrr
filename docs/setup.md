# Setup Guide

Detailed setup instructions for Claude Code configuration management.

## Prerequisites

### Required

1. **UV** - Fast Python package manager
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Task** - Modern command runner
   ```bash
   # macOS
   brew install go-task

   # Linux
   curl -sL https://taskfile.dev/install.sh | sh
   ```

3. **Python 3.11+** - UV will manage this automatically

4. **Git** - For repository management

### Optional

- **direnv** - For directory-specific environment loading
  ```bash
  brew install direnv  # macOS
  ```

## Installation Steps

### 1. Clone Repository

Clone to any location you prefer:

```bash
# Option 1: Dev workspace
cd ~/Documents/dev_work/personal_productivity
git clone <your-repo> making_my_agentic_setup_brrrrrr

# Option 2: Home directory
cd ~
git clone <your-repo> making_my_agentic_setup_brrrrrr

# Option 3: Custom location
cd /opt
git clone <your-repo> making_my_agentic_setup_brrrrrr
```

### 2. Run Installation

```bash
cd making_my_agentic_setup_brrrrrr
task install
```

This will:
- Create `~/.claude/configs/` directory
- Copy `personal.toml.example` to `~/.claude/configs/personal.toml`
- Prompt for default mode (anthropic/bedrock)
- Add shell integration to `~/.zshrc`
- Save version information

### 3. Configure Personal Settings

Edit your personal configuration:

```bash
nano ~/.claude/configs/personal.toml
```

**For Anthropic Mode:**
```toml
# No additional config needed if using ANTHROPIC_API_KEY env var
# Optional overrides:
[models]
primary = "claude-opus-4-5"  # Use Opus instead of Sonnet

[optional]
disable_telemetry = true
```

**For Bedrock Mode:**
```toml
[aws]
region = "us-west-2"     # Your preferred AWS region
profile = "work"          # Your AWS profile name

[models]
# Override default Bedrock model ARNs if needed
primary = "us.anthropic.claude-opus-4-5-20251101-v1:0"

[optional]
disable_telemetry = true
```

### 4. Set API Credentials

**Anthropic Mode:**
```bash
# Add to ~/.zshrc or ~/.bash_profile
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Bedrock Mode:**
```bash
# Configure AWS credentials
aws configure --profile work
# or use existing AWS credentials in ~/.aws/credentials
```

### 5. Reload Shell

```bash
source ~/.zshrc
```

### 6. Verify Installation

```bash
# Check configuration status
task status

# Should show:
# - Active mode (anthropic or bedrock)
# - Model IDs
# - AWS settings (if Bedrock mode)
```

### 7. Test Claude Code

```bash
claude "Hello, test message"
```

Should respond using the configured mode and model.

## Troubleshooting

### Shell Integration Not Working

```bash
# Manually add to ~/.zshrc if installation missed it
echo 'source ~/making_my_agentic_setup_brrrrrr/shell/zsh-functions.sh' >> ~/.zshrc
source ~/.zshrc
```

### Environment Variables Not Loading

```bash
# Check current mode
cat ~/.claude/configs/current_mode

# Check if env file exists
ls -la ~/.claude/configs/*.env

# Re-apply configuration
task switch -- anthropic  # or bedrock
```

### UV Not Found

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH if needed
export PATH="$HOME/.cargo/bin:$PATH"
```

### Task Not Found

```bash
# macOS
brew install go-task

# Linux - install to /usr/local/bin
sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /usr/local/bin
```

### Permission Errors

```bash
# Make sure config directory is writable
chmod 755 ~/.claude
chmod 755 ~/.claude/configs
```

## Next Steps

1. Read [usage.md](usage.md) for daily workflows
2. Read [extending.md](extending.md) for adding skills/agents
3. Explore available commands with `task --list`

## Uninstallation

```bash
# Remove personal configs
rm -rf ~/.claude/configs

# Remove shell integration from ~/.zshrc
# (manually edit and remove the source line)

# Remove repository
rm -rf ~/making_my_agentic_setup_brrrrrr
```

Last updated: 2025-01-14
