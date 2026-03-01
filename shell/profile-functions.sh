#!/bin/bash
# Claude Code Profile Management Shell Functions

# Profile directory
export CLAUDE_PROFILES_DIR="${HOME}/.claude-profiles"

# Get current profile name
claude-profile-current() {
    if [[ -L "${CLAUDE_PROFILES_DIR}/current" ]]; then
        readlink "${CLAUDE_PROFILES_DIR}/current" | xargs basename
    else
        echo "none"
    fi
}

# Switch to a profile (sets CLAUDE_CONFIG_DIR for current shell)
claude-profile-use() {
    local profile_name="$1"

    if [[ -z "$profile_name" ]]; then
        echo "Usage: claude-profile-use <profile-name>"
        echo "Available profiles:"
        claude-profile-list
        return 1
    fi

    local profile_path="${CLAUDE_PROFILES_DIR}/${profile_name}"

    if [[ ! -d "$profile_path" ]]; then
        echo "Profile '${profile_name}' does not exist"
        echo "Available profiles:"
        claude-profile-list
        return 1
    fi

    # Update symlink
    ln -sfT "$profile_path" "${CLAUDE_PROFILES_DIR}/current"

    # Set environment for current shell
    export CLAUDE_CONFIG_DIR="$profile_path"

    echo "✓ Switched to profile: ${profile_name}"
    echo "  CLAUDE_CONFIG_DIR=${CLAUDE_CONFIG_DIR}"
}

# List available profiles
claude-profile-list() {
    if [[ ! -d "$CLAUDE_PROFILES_DIR" ]]; then
        echo "No profiles directory found at $CLAUDE_PROFILES_DIR"
        return 1
    fi

    local current=$(claude-profile-current)

    echo "Available profiles:"
    for profile in "${CLAUDE_PROFILES_DIR}"/*; do
        if [[ -d "$profile" && "$(basename "$profile")" != "backups" ]]; then
            local name=$(basename "$profile")
            if [[ "$name" == "$current" ]]; then
                echo "  * ${name} (active)"
            else
                echo "    ${name}"
            fi
        fi
    done
}

# Quick profile switcher with tab completion
ccp() {
    if [[ -z "$1" ]]; then
        claude-profile-list
    else
        claude-profile-use "$1"
    fi
}

# Auto-load profile on shell startup
claude-profile-autoload() {
    # If CLAUDE_CONFIG_DIR not set, use current profile
    if [[ -z "$CLAUDE_CONFIG_DIR" ]]; then
        local current_link="${CLAUDE_PROFILES_DIR}/current"
        if [[ -L "$current_link" ]]; then
            export CLAUDE_CONFIG_DIR=$(readlink "$current_link")
        fi
    fi
}

# Bash completion for ccp
if [[ -n "$BASH_VERSION" ]]; then
    _ccp_complete() {
        local cur="${COMP_WORDS[COMP_CWORD]}"
        local profiles=$(ls -1 "${CLAUDE_PROFILES_DIR}" 2>/dev/null | grep -v backups)
        COMPREPLY=($(compgen -W "${profiles}" -- ${cur}))
    }
    complete -F _ccp_complete ccp
fi

# Zsh completion for ccp
if [[ -n "$ZSH_VERSION" ]]; then
    _ccp() {
        local -a profiles
        profiles=(${CLAUDE_PROFILES_DIR}/*(/N:t))
        profiles=(${profiles:#backups})
        _describe 'profile' profiles
    }
    # Only set up completion if compdef is available and _comps is initialized
    if (( $+functions[compdef] )) && [[ -n "${_comps}" ]]; then
        compdef _ccp ccp 2>/dev/null || true
    fi
fi

# Auto-load on shell startup
claude-profile-autoload
