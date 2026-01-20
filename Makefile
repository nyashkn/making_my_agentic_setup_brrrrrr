.PHONY: help install status switch validate update sync skills-list skills-install agents-list agents-install settings-apply settings-diff mcp-list mcp-install notifications-list notifications-install notifications-enable notifications-disable notifications-test notifications-status _ensure-deps

CONFIG_DIR := ~/.claude/configs
VENV := .venv
PYTHON := $(VENV)/bin/python3

help:
	@echo "Available commands:"
	@echo "  make install          - First-time setup"
	@echo "  make status           - Show current mode and config"
	@echo "  make switch           - Switch mode interactively"
	@echo "  make switch MODE=<m>  - Switch to specific mode (anthropic/bedrock)"
	@echo "  make validate         - Validate current configuration"
	@echo "  make update           - Pull latest and sync configs"
	@echo "  make sync             - Compare templates with personal config"
	@echo "  make skills-list      - List available skills"
	@echo "  make skills-install SKILL=<name> - Install a skill"
	@echo "  make agents-list      - List available agents"
	@echo "  make agents-install AGENT=<name> - Install an agent"
	@echo "  make settings-apply   - Apply settings template"
	@echo "  make settings-diff    - Show diff between template and current"
	@echo "  make mcp-list         - List available MCP servers"
	@echo "  make mcp-install MCP=<name> - Install MCP server"
	@echo "  make notifications-list - List notification backends"
	@echo "  make notifications-install [BACKEND=<name>] - Install backend (terminal-notifier or cc-notifier)"
	@echo "  make notifications-enable BACKEND=<name> - Enable notification hooks"
	@echo "  make notifications-disable - Disable notification hooks"
	@echo "  make notifications-test [BACKEND=<name>] - Test notification system"
	@echo "  make notifications-status - Show notification status"

_ensure-deps:
	@command -v uv >/dev/null 2>&1 || { echo "UV not installed. Run: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
	@if [ ! -d "$(VENV)" ]; then \
		echo "Creating virtual environment..."; \
		uv venv $(VENV); \
		echo "Installing dependencies..."; \
		uv pip install --python $(PYTHON) tomli tomli-w rich jinja2; \
	fi

install: _ensure-deps
	@mkdir -p $(CONFIG_DIR)
	@$(PYTHON) tools/install.py
	@echo "Edit $(CONFIG_DIR)/personal.toml with your settings"

status: _ensure-deps
	@$(PYTHON) tools/config.py status

switch: _ensure-deps
ifdef MODE
	@$(PYTHON) tools/config.py switch $(MODE)
else
	@$(PYTHON) tools/config.py switch-interactive
endif

validate: _ensure-deps
	@$(PYTHON) tools/validate.py

update:
	@read -p "Pull latest changes? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		git pull && $(MAKE) sync; \
	fi

sync: _ensure-deps
	@$(PYTHON) tools/sync.py

skills-list:
	@ls -1 skills/

skills-install: _ensure-deps
ifndef SKILL
	@echo "Usage: make skills-install SKILL=skill-name"
	@exit 1
endif
	@$(PYTHON) tools/config.py install-skill $(SKILL)

agents-list:
	@ls -1 agents/

agents-install: _ensure-deps
ifndef AGENT
	@echo "Usage: make agents-install AGENT=agent-name"
	@exit 1
endif
	@$(PYTHON) tools/config.py install-agent $(AGENT)

settings-apply: _ensure-deps
	@$(PYTHON) tools/config.py apply-settings

settings-diff: _ensure-deps
	@$(PYTHON) tools/config.py diff-settings

mcp-list:
	@ls -1 mcp/servers/

mcp-install: _ensure-deps
ifndef MCP
	@echo "Usage: make mcp-install MCP=server-name"
	@exit 1
endif
	@$(PYTHON) tools/config.py install-mcp $(MCP)

notifications-list: _ensure-deps
	@$(PYTHON) tools/notifications.py list

notifications-install: _ensure-deps
ifdef BACKEND
	@$(PYTHON) tools/notifications.py install $(BACKEND)
else
	@$(PYTHON) tools/notifications.py install terminal-notifier
endif

notifications-enable: _ensure-deps
ifndef BACKEND
	@echo "Usage: make notifications-enable BACKEND=<terminal-notifier|cc-notifier>"
	@exit 1
endif
	@$(PYTHON) tools/notifications.py enable $(BACKEND)

notifications-disable: _ensure-deps
	@$(PYTHON) tools/notifications.py disable

notifications-test: _ensure-deps
ifdef BACKEND
	@$(PYTHON) tools/notifications.py test $(BACKEND)
else
	@$(PYTHON) tools/notifications.py test
endif

notifications-status: _ensure-deps
	@$(PYTHON) tools/notifications.py status
