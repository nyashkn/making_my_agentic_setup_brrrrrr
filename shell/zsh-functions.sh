#!/bin/zsh
# Claude Code mode loading

claude-mode-load() {
  local mode_file="$HOME/.claude/configs/current_mode"
  local config_dir="$HOME/.claude/configs"

  if [[ -f "$mode_file" ]]; then
    local mode=$(cat "$mode_file")
    local env_file="$config_dir/${mode}.env"

    if [[ -f "$env_file" ]]; then
      source "$env_file"
    fi
  fi
}

# Load on shell startup
claude-mode-load

# Reload when directory changes (direnv integration)
if command -v direnv &> /dev/null; then
  _claude_mode_direnv_hook() {
    claude-mode-load
  }
  autoload -U add-zsh-hook
  add-zsh-hook precmd _claude_mode_direnv_hook
fi
