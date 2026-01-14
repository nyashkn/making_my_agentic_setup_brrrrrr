# Extending Guide

How to add skills, agents, commands, and MCP servers to the configuration.

## Adding Skills

### 1. Create Skill Directory

```bash
mkdir -p skills/my-custom-skill
cd skills/my-custom-skill
```

### 2. Create Skill Definition

```yaml
# skills/my-custom-skill/skill.yaml
name: my-custom-skill
description: Does something useful
version: 1.0.0
author: Your Name

# Skill configuration
triggers:
  - pattern: "/my-skill"
    action: execute

# Additional skill settings
```

### 3. Add Documentation

```markdown
# skills/my-custom-skill/README.md

## My Custom Skill

Brief description of what the skill does.

## Usage

/my-skill <args>

## Examples

/my-skill example-arg

## Configuration

Any special configuration needed.
```

### 4. Test Locally

```bash
# Install to your personal setup
task skills:install -- my-custom-skill

# Test in Claude Code
claude
> /my-skill test
```

### 5. Commit to Repository

```bash
git add skills/my-custom-skill
git commit -m "feat: add my-custom-skill"
git push
```

Others can now install with `task skills:install -- my-custom-skill`.

## Adding Agents

### 1. Create Agent Directory

```bash
mkdir -p agents/my-custom-agent
cd agents/my-custom-agent
```

### 2. Create Agent Definition

```yaml
# agents/my-custom-agent/agent.yaml
name: my-custom-agent
description: Handles specific tasks
version: 1.0.0
author: Your Name

# Agent configuration
capabilities:
  - task_planning
  - code_generation

# Additional agent settings
```

### 3. Add Documentation

```markdown
# agents/my-custom-agent/README.md

## My Custom Agent

Brief description of agent capabilities.

## Usage

Invoke with: @my-custom-agent

## Examples

@my-custom-agent help me with X

## Configuration

Any special setup needed.
```

### 4. Test and Commit

```bash
task agents:install -- my-custom-agent
# Test in Claude Code
git add agents/my-custom-agent
git commit -m "feat: add my-custom-agent"
git push
```

## Adding Commands

### 1. Create Command Script

```bash
# commands/my-command.sh
#!/bin/bash
# Usage: my-command.sh <arg1> <arg2>
# Description: Does something useful with arguments

set -e

# Parse arguments
ARG1=$1
ARG2=$2

# Validate
if [[ -z "$ARG1" ]]; then
  echo "Error: Missing ARG1"
  echo "Usage: my-command.sh <arg1> <arg2>"
  exit 1
fi

# Implementation
echo "Processing: $ARG1 and $ARG2"
# ... your logic here
```

### 2. Make Executable

```bash
chmod +x commands/my-command.sh
```

### 3. Test Locally

```bash
./commands/my-command.sh test1 test2
```

### 4. Add Documentation

Add usage examples to `commands/README.md` or in script comments.

### 5. Commit

```bash
git add commands/my-command.sh
git commit -m "feat: add my-command script"
git push
```

Users copy manually to `~/.claude/commands/` or use future `task commands:install`.

## Adding MCP Servers

### 1. Create Server Directory

```bash
mkdir -p mcp/servers/my-mcp-server
cd mcp/servers/my-mcp-server
```

### 2. Implement Server

```python
# mcp/servers/my-mcp-server/server.py
#!/usr/bin/env python3
"""My custom MCP server"""
from mcp.server import Server, Tool
from mcp.types import TextContent

server = Server("my-mcp-server")

@server.tool()
async def my_tool(arg: str) -> list[TextContent]:
    """Tool description"""
    result = f"Processed: {arg}"
    return [TextContent(type="text", text=result)]

if __name__ == "__main__":
    server.run()
```

### 3. Add Dependencies

```txt
# mcp/servers/my-mcp-server/requirements.txt
mcp>=0.1.0
# other dependencies
```

### 4. Add Documentation

```markdown
# mcp/servers/my-mcp-server/README.md

## My MCP Server

Brief description.

## Installation

```bash
task mcp:install -- my-mcp-server
```

## Configuration

Add to Claude Code settings:

```json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "python",
      "args": ["~/.claude/mcp/servers/my-mcp-server/server.py"]
    }
  }
}
```

## Usage

Available tools:
- `my_tool(arg: str)` - Tool description
```

### 5. Update Plugin Config

```toml
# mcp/plugins.toml
[servers.my-mcp-server]
command = "python"
args = ["mcp/servers/my-mcp-server/server.py"]
env = {}  # Environment variables if needed
```

### 6. Test and Commit

```bash
# Test locally
python mcp/servers/my-mcp-server/server.py

# Commit
git add mcp/servers/my-mcp-server mcp/plugins.toml
git commit -m "feat: add my-mcp-server"
git push
```

## Adding Settings Templates

### 1. Create Template

```json
// settings/my-feature.json.tmpl
{
  "feature": {
    "enabled": {{ FEATURE_ENABLED | default(true) }},
    "apiKey": "{{ FEATURE_API_KEY }}",
    "model": "{{ ANTHROPIC_MODEL }}"
  }
}
```

### 2. Add Variable Defaults

Update base configs to include new variables:

```toml
# configs/anthropic.toml
[optional]
feature_enabled = true
feature_api_key = ""  # User overrides in personal.toml
```

### 3. Update Config Loader

If needed, add logic to `tools/config.py` to handle new variables.

### 4. Document

```markdown
# settings/README.md

## My Feature Template

Usage:
- Set `FEATURE_API_KEY` in personal.toml
- Run `task settings:apply`
```

### 5. Commit

```bash
git add settings/my-feature.json.tmpl configs/anthropic.toml
git commit -m "feat: add my-feature settings template"
git push
```

## Modifying Config Templates

### Adding New Variables

1. **Update base template:**
```toml
# configs/anthropic.toml
[models]
new_model = "claude-model-id"
```

2. **Update config loader:**
```python
# tools/config.py - apply_config()
if models.get('new_model'):
    exports.append(f"export NEW_MODEL='{models['new_model']}'")
```

3. **Update CHANGELOG:**
```markdown
## [0.2.0] - 2025-01-XX
### Added
- New `new_model` configuration option
```

4. **Increment VERSION:**
```bash
echo "v0.2.0" > VERSION
```

5. **Commit:**
```bash
git add configs/anthropic.toml tools/config.py CHANGELOG.md VERSION
git commit -m "feat: add new_model configuration"
git push
```

Users will see the update via `task sync` after `git pull`.

## Extending Task Commands

### Add New Task

Edit `Taskfile.yml`:

```yaml
tasks:
  my-task:
    desc: Description of what this does
    deps: [other-task]  # Optional dependencies
    cmds:
      - echo "Doing something"
      - {{.UV}} tools/my-script.py
```

### Add New Python Tool

```python
# tools/my-tool.py
#!/usr/bin/env python3
"""My custom tool"""
from pathlib import Path
from rich.console import Console

console = Console()

CONFIG_DIR = Path.home() / ".claude" / "configs"
REPO_DIR = Path(__file__).parent.parent.resolve()

def main():
    """Main function"""
    console.print("[green]Doing something useful[/green]")

if __name__ == "__main__":
    main()
```

Make it usable from Task:

```yaml
# Taskfile.yml
tasks:
  my-tool:
    desc: Run my custom tool
    cmds:
      - {{.UV}} tools/my-tool.py
```

## Best Practices

1. **Always document**: Every new component needs a README
2. **Version everything**: Use semantic versioning
3. **Test locally first**: Install and test before committing
4. **Update CHANGELOG**: Document all changes
5. **Keep it simple**: Minimal dependencies, clear purpose
6. **Use auto-detection**: Use `{{.ROOT_DIR}}` in Task, `Path(__file__)` in Python
7. **Follow structure**: Match existing patterns
8. **Git commit conventions**: Use `feat:`, `fix:`, `docs:` prefixes

## Git Flow Workflow

### Feature Development

```bash
# Start new feature
git flow feature start my-feature

# Make changes
# ... add skills/agents/commands ...

# Test locally
task skills:install -- my-skill

# Commit
git add .
git commit -m "feat: add my-feature"

# Finish feature (merges to develop)
git flow feature finish my-feature
```

### Release Process

```bash
# Start release
git flow release start v0.2.0

# Update VERSION
echo "v0.2.0" > VERSION

# Update CHANGELOG
nano CHANGELOG.md

# Test everything
task validate

# Finish release (merges to master and develop, creates tag)
git flow release finish v0.2.0
```

## Examples

### Complete Skill Example

```bash
# 1. Create structure
mkdir -p skills/data-analyzer/{examples,tests}

# 2. Skill definition
cat > skills/data-analyzer/skill.yaml <<EOF
name: data-analyzer
description: Analyzes data files and provides insights
version: 1.0.0
author: Your Name
triggers:
  - pattern: "/analyze"
    action: execute
EOF

# 3. Documentation
cat > skills/data-analyzer/README.md <<EOF
## Data Analyzer Skill

Analyzes CSV, JSON, and Excel files.

### Usage
/analyze <file-path>

### Examples
/analyze data/sales.csv
/analyze reports/metrics.json
EOF

# 4. Test locally
task skills:install -- data-analyzer

# 5. Commit
git add skills/data-analyzer
git commit -m "feat: add data-analyzer skill"
git push
```

### Complete MCP Server Example

```bash
# 1. Create structure
mkdir -p mcp/servers/weather-api

# 2. Server implementation
cat > mcp/servers/weather-api/server.py <<EOF
#!/usr/bin/env python3
from mcp.server import Server, Tool

server = Server("weather-api")

@server.tool()
async def get_weather(city: str):
    # Implementation
    return f"Weather for {city}"

if __name__ == "__main__":
    server.run()
EOF

# 3. Dependencies
cat > mcp/servers/weather-api/requirements.txt <<EOF
mcp>=0.1.0
requests>=2.31.0
EOF

# 4. Configuration
cat >> mcp/plugins.toml <<EOF

[servers.weather-api]
command = "python"
args = ["mcp/servers/weather-api/server.py"]
EOF

# 5. Documentation
cat > mcp/servers/weather-api/README.md <<EOF
## Weather API MCP Server

Provides weather information via MCP.
EOF

# 6. Commit
git add mcp/servers/weather-api mcp/plugins.toml
git commit -m "feat: add weather-api MCP server"
git push
```

Last updated: 2025-01-14
