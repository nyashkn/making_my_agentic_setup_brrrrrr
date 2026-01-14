# Commands

This directory contains custom shell commands for Claude Code.

## Structure

```
commands/
├── custom-command-1.sh
├── custom-command-2.py
└── README.md
```

## Installing Commands

Commands are installed to `~/.claude/commands/` and should be:
- Executable (`chmod +x`)
- Self-contained or documented dependencies
- Include usage comment at top

## Example Command

```bash
#!/bin/bash
# Usage: custom-command-1.sh <arg1> <arg2>
# Description: Does something useful

# Command implementation
echo "Processing $1 and $2"
```

## Creating Commands

1. Create script in `commands/`
2. Add usage documentation in comments
3. Make executable: `chmod +x commands/script.sh`
4. Commit to repo for sharing
5. Others install manually or via future `task commands:install`

## Usage

After copying to `~/.claude/commands/`, commands can be invoked from terminal or Claude Code sessions.
