# Claude Code Profile Management

Manage multiple Claude Code configurations with different skills, agents, hooks, and MCP servers.

## Why Profiles?

With profiles, you can:

- **Separate concerns**: Work profile with company skills, personal profile with experimental agents
- **Test safely**: Clone your production profile, test new hooks without breaking existing setup
- **Context switching**: Quick switch between "minimal" and "fully-loaded" configurations
- **Fresh start**: Create clean profiles for specific projects
- **Backup & restore**: Easy snapshots of your configuration

## Architecture

### Profile Structure

```
~/.claude-profiles/
├── default/              # Your main profile (migrated from ~/.claude)
│   ├── skills/           # Installed skills
│   ├── agents/           # Custom agents
│   ├── hooks/            # TypeScript hooks
│   ├── mcp/              # MCP server configurations
│   │   └── servers/
│   ├── settings.json     # Claude Code settings
│   └── configs/          # Mode configs (anthropic.env, etc.)
├── work/                 # Work-specific profile
│   └── ...
├── experimental/         # Testing profile
│   └── ...
├── minimal/              # Lightweight profile
│   └── ...
├── current -> default    # Symlink to active profile
└── backups/              # Profile backups
    ├── default_20260210_143022/
    └── work_20260209_091045/
```

### How `CLAUDE_CONFIG_DIR` Works

Claude Code checks `CLAUDE_CONFIG_DIR` environment variable to find its config:

1. If `CLAUDE_CONFIG_DIR` is set → uses that directory
2. If not set → uses `~/.claude/` (default)

This allows complete isolation between profiles.

## Quick Start

### 1. Migrate Your Current Setup

If you have an existing `~/.claude/` directory (like Continuous Claude v3):

```bash
make profile-migrate
```

This copies your entire `~/.claude/` to `~/.claude-profiles/default/`.

### 2. Add Shell Integration

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
# Claude Code Profile Management
source ~/path/to/making_my_agentic_setup_brrrrrr/shell/profile-functions.sh
```

Reload shell:
```bash
source ~/.zshrc  # or ~/.bashrc
```

### 3. List Profiles

```bash
make profile-list
# or
ccp
```

### 4. Switch Profiles

**Method 1: Using make (permanent)**
```bash
make profile-switch NAME=default
```

**Method 2: Using shell function (current shell only)**
```bash
ccp default        # Quick switch
claude-profile-use default  # Explicit
```

**Method 3: One-off usage**
```bash
CLAUDE_CONFIG_DIR=~/.claude-profiles/work claude
```

## Profile Operations

### Create New Profile

```bash
# Interactive
make profile-create NAME=experimental

# Or directly
python tools/profile.py create experimental
```

Creates:
- Empty profile structure
- Minimal `settings.json`
- Ready for skill/agent installation

### Clone Existing Profile

```bash
# Clone your default setup for testing
make profile-clone SRC=default DEST=testing

# Or
python tools/profile.py clone default testing
```

Perfect for:
- Testing new configurations without risk
- Creating project-specific profiles based on a template
- A/B testing different skill combinations

### Switch Profiles

```bash
# Permanent switch (updates symlink)
make profile-switch NAME=work

# Current shell only
ccp work

# Or set env for single command
CLAUDE_CONFIG_DIR=~/.claude-profiles/work claude
```

### Check Current Profile

```bash
make profile-status
# or
python tools/profile.py status
```

Shows:
- Active profile name
- Location
- CLAUDE_CONFIG_DIR status
- Contents (skills, agents, hooks, MCPs)

### Backup Profile

```bash
make profile-backup NAME=default
# or
python tools/profile.py backup default
```

Creates timestamped backup in `~/.claude-profiles/backups/`.
Keeps last 5 backups per profile.

## Usage Patterns

### Pattern 1: Work vs Personal

```bash
# Create work profile
make profile-create NAME=work

# Install work-specific skills
CLAUDE_CONFIG_DIR=~/.claude-profiles/work make skills-install SKILL=security-audit
CLAUDE_CONFIG_DIR=~/.claude-profiles/work make agents-install AGENT=code-reviewer-buddy

# Switch when starting work
ccp work

# Switch back after hours
ccp default
```

### Pattern 2: Minimal vs Full

```bash
# Create minimal profile (fast startup, basic features)
make profile-create NAME=minimal

# Use minimal for quick tasks
ccp minimal
claude --fast

# Use full profile for complex work
ccp default
```

### Pattern 3: Testing New Configurations

```bash
# Clone your current setup
make profile-clone SRC=default DEST=test-hooks

# Switch to test profile
ccp test-hooks

# Experiment with new hooks
cd ~/.claude-profiles/test-hooks/hooks
# ... add new hooks ...

# Test them
claude

# If broken, just switch back
ccp default
```

### Pattern 4: Project-Specific Profiles

```bash
# Create profile for a specific project
make profile-create NAME=project-alpha

# Install project-specific tools
ccp project-alpha
make skills-install SKILL=kubernetes
make agents-install AGENT=deployment-helper

# Work on project
cd ~/projects/alpha
ccp project-alpha
claude
```

### Pattern 5: Clean Slate for Learning

```bash
# Create minimal profile to learn Claude Code
make profile-create NAME=learning

# Start fresh
ccp learning
claude

# No overwhelming skills/agents, just the basics
```

## Shell Functions Reference

All these functions are available after sourcing `profile-functions.sh`:

### `ccp [profile-name]`
Quick profile switcher.
- Without args: lists profiles
- With profile name: switches to that profile

```bash
ccp              # List profiles
ccp work         # Switch to work profile
```

### `claude-profile-use <name>`
Switch to a profile (sets `CLAUDE_CONFIG_DIR` for current shell).

```bash
claude-profile-use experimental
```

### `claude-profile-list`
List all available profiles with active marker.

```bash
claude-profile-list
```

### `claude-profile-current`
Print name of currently active profile.

```bash
current=$(claude-profile-current)
echo "Using profile: $current"
```

### `claude-profile-autoload`
Auto-loads profile on shell startup. Called automatically when shell starts.

## Environment Variables

### `CLAUDE_CONFIG_DIR`
Points to active profile directory.

```bash
echo $CLAUDE_CONFIG_DIR
# ~/.claude-profiles/default
```

Claude Code uses this to find:
- `settings.json`
- `skills/`
- `agents/`
- `hooks/`
- `mcp/servers/`

### `CLAUDE_PROFILES_DIR`
Base directory for all profiles. Default: `~/.claude-profiles`

```bash
export CLAUDE_PROFILES_DIR=~/Dropbox/claude-profiles  # Cloud sync
```

## Integration with Existing Tools

### cc-switch

[cc-switch](https://github.com/farion1231/cc-switch) is a GUI tool for managing API providers (Anthropic, AWS Bedrock, custom proxies).

**Profiles vs cc-switch:**
- **cc-switch**: Manages API keys, endpoints, model selection
- **Profile system**: Manages skills, agents, hooks, MCPs

**Use together:**
```bash
# Switch API provider with cc-switch GUI
# Switch skill set with profiles

ccp work          # Work skills
# Use cc-switch to select company API proxy

ccp personal      # Personal skills
# Use cc-switch to select personal API key
```

### Continuous Claude v3

If you installed Continuous Claude v3:

```bash
# Migrate it to a profile
make profile-migrate

# This becomes your "default" profile with all hooks
```

Your hooks, skills, and setup are now in `~/.claude-profiles/default/`.

### Mode Switching (Anthropic/Bedrock)

The mode system (from this repo) works **per-profile**:

```bash
# Each profile has its own mode config
ccp work
make switch MODE=bedrock  # Work profile uses Bedrock

ccp personal
make switch MODE=anthropic  # Personal profile uses Anthropic API
```

Configs are stored in:
```
~/.claude-profiles/work/configs/
├── current_mode
├── anthropic.env
└── bedrock.env
```

## Troubleshooting

### Profile not loading

Check if `CLAUDE_CONFIG_DIR` is set:
```bash
echo $CLAUDE_CONFIG_DIR
```

If empty:
```bash
# Reload shell functions
source ~/path/to/shell/profile-functions.sh

# Check again
echo $CLAUDE_CONFIG_DIR
```

### Skills not found

Verify you're in the right profile:
```bash
make profile-status
```

Install skills to active profile:
```bash
make skills-install SKILL=skill-name
```

### Wrong profile active

Switch explicitly:
```bash
ccp <correct-profile-name>
```

### Claude still uses ~/.claude

Set environment before running:
```bash
export CLAUDE_CONFIG_DIR=$(readlink ~/.claude-profiles/current)
claude
```

Or add to shell config for persistence.

### Tab completion not working

**Zsh:**
```bash
# Add to ~/.zshrc
autoload -U compinit && compinit
source ~/path/to/shell/profile-functions.sh
```

**Bash:**
```bash
# Add to ~/.bashrc
source ~/path/to/shell/profile-functions.sh
```

## Advanced Usage

### Cloud Sync Profiles

Sync profiles across machines:

```bash
# Move profiles to cloud folder
mv ~/.claude-profiles ~/Dropbox/claude-profiles

# Update env var
export CLAUDE_PROFILES_DIR=~/Dropbox/claude-profiles

# Add to shell config for persistence
echo 'export CLAUDE_PROFILES_DIR=~/Dropbox/claude-profiles' >> ~/.zshrc
```

On other machines:
```bash
# Set same path
export CLAUDE_PROFILES_DIR=~/Dropbox/claude-profiles
source ~/path/to/shell/profile-functions.sh

# Profiles sync automatically via Dropbox
ccp default
```

### Per-Directory Profile Switching

Use `.envrc` with [direnv](https://direnv.net/):

```bash
# In project directory
cat > .envrc <<EOF
export CLAUDE_CONFIG_DIR=~/.claude-profiles/project-alpha
EOF

# Allow it
direnv allow

# Auto-switches when entering directory
cd ~/projects/alpha  # Loads project-alpha profile
cd ~                 # Back to default profile
```

### Profile Templates

Create template profiles for quick setup:

```bash
# Create template
make profile-create NAME=template-python
ccp template-python
make skills-install SKILL=python-expert
make agents-install AGENT=test-generator

# Clone for new projects
make profile-clone SRC=template-python DEST=project-foo
```

### Scripted Profile Creation

```python
# create_project_profile.py
import sys
import subprocess

project_name = sys.argv[1]
profile_name = f"project-{project_name}"

# Create profile
subprocess.run(["make", "profile-create", f"NAME={profile_name}"])

# Install project-specific tools
subprocess.run(["make", "skills-install", "SKILL=build"],
               env={"CLAUDE_CONFIG_DIR": f"~/.claude-profiles/{profile_name}"})

print(f"Created profile: {profile_name}")
print(f"Switch with: ccp {profile_name}")
```

## Best Practices

1. **Backup before experiments**: `make profile-backup NAME=default`
2. **Clone, don't modify directly**: Clone default → test in clone → merge back
3. **Name profiles clearly**: `work`, `personal`, `experiment-hooks`, not `profile1`
4. **Clean up unused**: Remove test profiles after experiments
5. **Document custom profiles**: Add README.md in profile directory
6. **Use version control**: Track profile configs separately if sharing with team

## FAQ

**Q: Can I share profiles between team members?**
A: Yes, export profile directory and share. Import with `make profile-clone`.

**Q: Does switching profiles require restarting Claude?**
A: Yes, Claude Code reads config on startup. Restart after switching.

**Q: Can I have different API keys per profile?**
A: Yes! Each profile has its own `settings.json` with separate API keys.

**Q: What happens to my original ~/.claude/?**
A: Migration copies it, original stays untouched as backup.

**Q: Can I sync just one profile?**
A: Yes, symlink specific profile to cloud: `ln -s ~/Dropbox/claude-work ~/.claude-profiles/work`

**Q: How do I delete a profile?**
A: `rm -rf ~/.claude-profiles/profile-name` (be careful!)

**Q: Can profiles share skills?**
A: No, each profile is isolated. Use `make profile-clone` to copy configurations.

## Related Tools

- [cc-switch](https://github.com/farion1231/cc-switch): GUI for API provider management
- [Continuous Claude](https://github.com/kontinuity/Continuous-Claude): Hooks, memory, coordination
- This repo: Mode switching, skill/agent/MCP management, profiles

All work together - use what fits your workflow.
