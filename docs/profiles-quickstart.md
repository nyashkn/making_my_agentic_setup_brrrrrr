# Profile System Quick Start

Get up and running with Claude Code profiles in 5 minutes.

## Step 1: Migrate Your Current Setup

```bash
cd ~/path/to/making_my_agentic_setup_brrrrrr
make profile-migrate
```

This creates `~/.claude-profiles/default/` with your current `~/.claude/` contents.

## Step 2: Add Shell Integration

**For Zsh (~/.zshrc):**
```bash
echo 'source ~/Documents/dev_work/personal_productivity/making_my_agentic_setup_brrrrrr/shell/profile-functions.sh' >> ~/.zshrc
source ~/.zshrc
```

**For Bash (~/.bashrc):**
```bash
echo 'source ~/Documents/dev_work/personal_productivity/making_my_agentic_setup_brrrrrr/shell/profile-functions.sh' >> ~/.bashrc
source ~/.bashrc
```

## Step 3: Verify Setup

```bash
# List profiles
ccp

# Should show:
# Available profiles:
#   * default (active)

# Check status
make profile-status
```

You should see:
- Active profile: default
- Location: ~/.claude-profiles/default
- Contents: Your migrated skills, agents, hooks, MCPs

## Step 4: Create a Test Profile

```bash
# Create a clean profile for testing
make profile-create NAME=test

# Or clone your default for safer experiments
make profile-clone SRC=default DEST=experiment
```

## Step 5: Switch Between Profiles

```bash
# Quick switch (current shell only)
ccp test

# Permanent switch
make profile-switch NAME=test

# Check which is active
make profile-status
```

## Step 6: Use Different Profiles

**Start Claude with a specific profile:**

```bash
# Method 1: Switch first
ccp work
claude

# Method 2: One-off
CLAUDE_CONFIG_DIR=~/.claude-profiles/work claude

# Method 3: Per-project (with direnv)
cd ~/projects/my-app
echo 'export CLAUDE_CONFIG_DIR=~/.claude-profiles/work' > .envrc
direnv allow
claude  # Auto-uses work profile
```

## Common Workflows

### Workflow 1: Safe Experimentation

```bash
# Clone current setup
make profile-clone SRC=default DEST=test-new-hooks

# Switch to test profile
ccp test-new-hooks

# Add experimental hooks
cd ~/.claude-profiles/test-new-hooks/hooks
# ... edit hooks ...

# Test
claude

# If broken, switch back
ccp default

# If works, copy hooks to default
cp ~/.claude-profiles/test-new-hooks/hooks/*.ts ~/.claude-profiles/default/hooks/
```

### Workflow 2: Work vs Personal

```bash
# Create work profile
make profile-create NAME=work

# Install work tools
ccp work
make skills-install SKILL=security
make agents-install AGENT=code-reviewer-buddy

# Switch when needed
ccp work      # Start of workday
ccp default   # After hours
```

### Workflow 3: Minimal for Quick Tasks

```bash
# Create lightweight profile
make profile-create NAME=minimal

# Switch to it for fast tasks
ccp minimal
claude --fast
```

## Troubleshooting

### "Profile not found"

```bash
# List available profiles
make profile-list

# Create if needed
make profile-create NAME=<name>
```

### "CLAUDE_CONFIG_DIR not set"

```bash
# Check if shell functions loaded
type ccp

# If not, reload
source ~/.zshrc  # or ~/.bashrc

# Or set manually
export CLAUDE_CONFIG_DIR=~/.claude-profiles/default
```

### "Skills not found after switch"

```bash
# Verify you're in right profile
make profile-status

# Install skills to this profile
make skills-install SKILL=<name>
```

### Changes not taking effect

```bash
# Claude reads config on startup - restart it
# Exit claude and start again

ccp <profile-name>
claude
```

## Next Steps

- Read [full profiles documentation](profiles.md)
- Explore [usage patterns](profiles.md#usage-patterns)
- Set up [cloud sync](profiles.md#cloud-sync-profiles)
- Configure [per-directory switching](profiles.md#per-directory-profile-switching)

## Profile Management Commands

```bash
# List
make profile-list              # or: ccp

# Create
make profile-create NAME=<n>   # or: python tools/profile.py create <n>

# Switch
ccp <name>                     # quick (current shell)
make profile-switch NAME=<n>   # permanent (updates symlink)

# Clone
make profile-clone SRC=<s> DEST=<d>

# Status
make profile-status

# Backup
make profile-backup NAME=<n>
```

## Summary

You now have:

✅ Migrated setup to `~/.claude-profiles/default/`
✅ Shell functions for quick switching (`ccp`)
✅ Ability to create isolated profiles
✅ Safe testing environment (clone profiles)
✅ Per-project profile support (via CLAUDE_CONFIG_DIR)

Your original `~/.claude/` remains untouched as a backup.
