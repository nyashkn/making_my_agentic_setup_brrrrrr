# Settings

This directory contains settings.json templates for Claude Code.

## Structure

```
settings/
├── global.json.tmpl        # Global settings template
├── project.json.tmpl       # Project-specific template
└── README.md
```

## Using Settings Templates

```bash
# View differences between template and current
task settings:diff

# Apply settings template
task settings:apply
```

## Template Variables

Settings templates use Jinja2 variables for customization:

```json
{
  "apiKey": "{{ AWS_PROFILE }}",
  "model": "{{ ANTHROPIC_MODEL }}"
}
```

Variables are replaced from:
1. Environment variables
2. Personal config (`~/.claude/configs/personal.toml`)
3. Current mode config

## Creating Templates

1. Create `.json.tmpl` file in `settings/`
2. Use `{{ VARIABLE }}` for dynamic values
3. Add documentation in comments (JSON5 style)
4. Commit to repo for sharing

## Settings Location

Claude Code settings are typically in:
- Global: `~/.claude/settings.json`
- Project: `.claude/settings.json`

## Example Template

```json
{
  // Model configuration
  "defaultModel": "{{ ANTHROPIC_MODEL }}",

  // Performance settings
  "disablePromptCaching": {{ DISABLE_PROMPT_CACHING | default(false) }},

  // Optional features
  "disableTelemetry": {{ DISABLE_TELEMETRY | default(false) }}
}
```

## Usage

Settings templates help maintain consistent configuration across:
- Multiple machines
- Team members
- Different projects

Update templates in repo, apply with `task settings:apply`.
