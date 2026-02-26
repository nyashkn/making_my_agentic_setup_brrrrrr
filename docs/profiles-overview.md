# Profile System Overview

Visual guide to understanding Claude Code profiles.

## The Problem

You have Continuous Claude v3 installed with hooks, skills, and agents. You want to:

- Test new configurations without breaking your current setup
- Have different tool sets for work vs personal projects
- Create clean environments for specific projects
- Easily switch between configurations

**Old way:** Manually backup/restore `~/.claude/`, risky and tedious.

**New way:** Profile system with instant switching.

## Architecture

### Before Profiles

```
~/.claude/
├── skills/           ← All skills mixed together
├── agents/           ← All agents in one place
├── hooks/            ← Shared hooks
├── mcp/              ← Single MCP config
└── settings.json     ← One settings file
```

**Problem:** Everything in one place, hard to experiment safely.

### After Profiles

```
~/.claude-profiles/
├── default/          ← Your Continuous Claude v3 setup
│   ├── skills/
│   ├── agents/
│   ├── hooks/
│   ├── mcp/
│   └── settings.json
│
├── work/             ← Work-specific tools
│   ├── skills/       (company security scanner, code reviewer)
│   ├── agents/       (compliance checker)
│   └── settings.json (company API key)
│
├── experiment/       ← Safe testing ground
│   ├── skills/       (experimental skills)
│   ├── hooks/        (new hooks being developed)
│   └── settings.json
│
├── minimal/          ← Lightweight for quick tasks
│   └── settings.json (just basics)
│
└── current -> default  ← Symlink to active profile
```

**Solution:** Complete isolation, switch instantly, experiment safely.

## How It Works

### CLAUDE_CONFIG_DIR

Claude Code checks this environment variable:

```bash
# Without CLAUDE_CONFIG_DIR
claude  → uses ~/.claude/

# With CLAUDE_CONFIG_DIR
export CLAUDE_CONFIG_DIR=~/.claude-profiles/work
claude  → uses ~/.claude-profiles/work/
```

### Profile Switching

```
┌─────────────────────────────────────────────────────┐
│  1. You run: ccp work                              │
└─────────────────┬───────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────┐
│  2. Shell function sets:                           │
│     export CLAUDE_CONFIG_DIR=~/.claude-profiles/work│
└─────────────────┬───────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────┐
│  3. You run: claude                                │
└─────────────────┬───────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────┐
│  4. Claude reads from: ~/.claude-profiles/work/     │
│     - work/skills/                                  │
│     - work/agents/                                  │
│     - work/hooks/                                   │
│     - work/settings.json                            │
└─────────────────────────────────────────────────────┘
```

## Workflow Example

### Scenario: Testing New Hooks

**Without profiles:**
```bash
1. cd ~/.claude/hooks
2. cp -r hooks hooks.backup  # Manual backup
3. # Edit hooks...
4. claude  # Test - BREAKS!
5. rm -rf hooks && mv hooks.backup hooks  # Restore manually
6. # 😰 Hope nothing else broke
```

**With profiles:**
```bash
1. make profile-clone SRC=default DEST=test-hooks
2. ccp test-hooks
3. cd ~/.claude-profiles/test-hooks/hooks
4. # Edit hooks...
5. claude  # Test - BREAKS!
6. ccp default  # Instant restore
7. # 😎 Original untouched
```

### Scenario: Work vs Personal

**Morning:**
```bash
ccp work
claude
# Has: security scanner, code reviewer, compliance checker
# Uses: Company API key
```

**Evening:**
```bash
ccp personal
claude
# Has: experimental skills, personal agents
# Uses: Personal API key
```

## Key Features

### 1. Complete Isolation

Each profile is 100% independent:
- Own skills directory
- Own agents
- Own hooks
- Own MCP servers
- Own settings.json (API keys, model config)
- Own mode config (anthropic/bedrock)

### 2. Zero Risk Cloning

```bash
make profile-clone SRC=production DEST=experiment
```

Creates exact copy. Test anything in `experiment`, `production` stays pristine.

### 3. Instant Switching

```bash
ccp work      # Instant
ccp personal  # Instant
ccp test      # Instant
```

No file copying, just environment variable change.

### 4. Backup System

```bash
make profile-backup NAME=important
```

Creates timestamped snapshot:
```
~/.claude-profiles/backups/
└── important_20260210_143022/
    ├── skills/
    ├── agents/
    └── ...
```

Keeps last 5 backups automatically.

## Integration with Existing Tools

### Continuous Claude v3

Your existing setup:
```
~/.claude/
├── hooks/    (from Continuous Claude)
├── skills/   (installed skills)
└── ...
```

After migration:
```
~/.claude-profiles/default/
├── hooks/    (same hooks)
├── skills/   (same skills)
└── ...
```

Nothing changes except location. All functionality preserved.

### cc-switch (API Provider Manager)

cc-switch and profiles solve different problems:

| Tool | Manages | Example |
|------|---------|---------|
| **cc-switch** | API providers, endpoints, keys | Anthropic vs Bedrock vs proxy |
| **Profiles** | Skills, agents, hooks, MCPs | Work vs personal tools |

Use together:
```bash
# Switch API provider (cc-switch GUI)
# Set: Company proxy endpoint

# Switch tool set (profiles)
ccp work

# Result: Company tools + company endpoint
```

### Mode System (This Repo)

Modes (anthropic/bedrock) work **per-profile**:

```
~/.claude-profiles/work/
└── configs/
    ├── current_mode       (bedrock)
    ├── anthropic.env
    └── bedrock.env       ← Active

~/.claude-profiles/personal/
└── configs/
    ├── current_mode       (anthropic)
    ├── anthropic.env     ← Active
    └── bedrock.env
```

Switch both independently:
```bash
ccp work
make switch MODE=bedrock  # Work uses Bedrock

ccp personal
make switch MODE=anthropic  # Personal uses Anthropic
```

## Shell Integration

### What You Get

After adding to `~/.zshrc`:
```bash
source ~/path/to/shell/profile-functions.sh
```

You get these commands:

| Command | What It Does |
|---------|--------------|
| `ccp` | List profiles |
| `ccp <name>` | Switch to profile |
| `claude-profile-list` | Show all profiles with stats |
| `claude-profile-current` | Print active profile name |
| `claude-profile-use <name>` | Explicit switch |

### Tab Completion

Works in both bash and zsh:
```bash
ccp <TAB>
# Shows: default  work  test  experiment
```

### Auto-Load

On shell startup, automatically sets `CLAUDE_CONFIG_DIR` to current profile.

No manual environment variable management needed.

## Common Questions

### Q: Does this replace cc-switch?

**No.** They work together:
- cc-switch: API configuration (keys, endpoints)
- Profiles: Tool configuration (skills, agents, hooks)

### Q: Does this replace mode switching?

**No.** Modes are **per-profile**. Each profile has its own mode setting.

### Q: What about my original ~/.claude/?

**Untouched.** Migration copies, doesn't move. Original stays as backup.

### Q: Can I sync profiles across machines?

**Yes.** Symlink to cloud folder:
```bash
mv ~/.claude-profiles ~/Dropbox/claude-profiles
ln -s ~/Dropbox/claude-profiles ~/.claude-profiles
```

### Q: Can profiles share skills?

**No.** Each profile is isolated. Use `make profile-clone` to copy configurations.

### Q: Performance impact?

**None.** Switching is just an environment variable change, no file operations.

## Summary

### Before

- Single `~/.claude/` directory
- Risky to experiment
- Hard to maintain multiple contexts
- Manual backup/restore

### After

- Multiple isolated profiles
- Safe experimentation (clone & test)
- Easy context switching (`ccp work`)
- Automatic backups

### Migration Path

```bash
# 1. Migrate (copies ~/.claude to profiles)
make profile-migrate

# 2. Add shell integration
echo 'source ~/path/to/shell/profile-functions.sh' >> ~/.zshrc
source ~/.zshrc

# 3. Start using
ccp                          # List
make profile-create NAME=work  # Create
ccp work                     # Switch
```

That's it! Your Continuous Claude v3 setup is now in a profile, ready to clone and experiment with.

## Next Steps

1. Read [Quick Start Guide](profiles-quickstart.md) - 5 minute setup
2. Try creating a test profile and experimenting
3. Set up work vs personal profiles
4. Explore [advanced usage patterns](profiles.md)
