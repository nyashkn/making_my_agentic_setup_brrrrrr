# Skills

This directory contains shared Claude Code skills.

## Structure

Each skill should be in its own directory:

```
skills/
├── custom-skill-1/
│   ├── skill.yaml          # Skill definition
│   ├── README.md           # Usage documentation
│   └── examples/           # Example usage (optional)
└── custom-skill-2/
    └── ...
```

## Installing Skills

```bash
# List available skills
task skills:list

# Install a skill to ~/.claude/skills/
task skills:install -- skill-name
```

## Creating Skills

1. Create a new directory in `skills/`
2. Add `skill.yaml` with skill definition
3. Add `README.md` with usage instructions
4. Commit to repo for team sharing
5. Others can install with `task skills:install`

## Skill Definition Example

```yaml
# skills/my-skill/skill.yaml
name: my-skill
description: Brief description
version: 1.0.0
```

See Claude Code documentation for full skill specification.

## Usage

After installation, skills are available in `~/.claude/skills/` and can be invoked in Claude Code sessions.
