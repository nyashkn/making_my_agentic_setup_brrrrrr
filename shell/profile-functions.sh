#!/bin/bash
# Claude Code Profile Management Shell Functions

# Capture repo dir at source time (this script lives in <repo>/shell/)
_CLAUDE_SETUP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-${(%):-%x}}")/.." 2>/dev/null && pwd)"

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

# ---------------------------------------------------------------------------
# Identity management (Anthropic OAuth + AWS Bedrock)
# ---------------------------------------------------------------------------

# Load credentials from ~/.claude/configs/credentials.env (user-created, git-ignored)
_cc_load_credentials() {
    local creds="${HOME}/.claude/configs/credentials.env"
    if [[ ! -f "$creds" ]]; then
        echo "⚠  No credentials file found."
        echo "   cp configs/credentials.env.example ~/.claude/configs/credentials.env"
        return 1
    fi
    # shellcheck disable=SC1090
    source "$creds"
}

# Switch to KN identity (Anthropic OAuth)
cc-kn() {
    _cc_load_credentials || return 1
    [[ -z "$CC_KN_OAUTH_TOKEN" ]] && { echo "⚠  CC_KN_OAUTH_TOKEN not set in credentials.env"; return 1; }
    export CLAUDE_CODE_OAUTH_TOKEN="$CC_KN_OAUTH_TOKEN"
    export CLAUDE_CODE_USE_BEDROCK=0
    export CC_IDENTITY="kn"
    export CC_IDENTITY_DISPLAY="${CC_KN_NAME:-KN}"
    echo "✓ Identity: ${CC_IDENTITY_DISPLAY}"
}

# Switch to Naisaie identity (Anthropic OAuth)
cc-naisaie() {
    _cc_load_credentials || return 1
    [[ -z "$CC_NAISAIE_OAUTH_TOKEN" ]] && { echo "⚠  CC_NAISAIE_OAUTH_TOKEN not set in credentials.env"; return 1; }
    export CLAUDE_CODE_OAUTH_TOKEN="$CC_NAISAIE_OAUTH_TOKEN"
    export CLAUDE_CODE_USE_BEDROCK=0
    export CC_IDENTITY="naisaie"
    export CC_IDENTITY_DISPLAY="${CC_NAISAIE_NAME:-Naisaie}"
    echo "✓ Identity: ${CC_IDENTITY_DISPLAY}"
}

# Switch to Kuze identity (AWS Bedrock)
cc-kuze() {
    _cc_load_credentials || return 1
    export AWS_PROFILE="${CC_KUZE_AWS_PROFILE:-default}"
    export AWS_REGION="${CC_KUZE_AWS_REGION:-us-east-1}"
    unset CLAUDE_CODE_OAUTH_TOKEN            # bedrock doesn't use OAuth
    export CLAUDE_CODE_USE_BEDROCK=1
    export CC_IDENTITY="kuze"
    export CC_IDENTITY_DISPLAY="${CC_KUZE_NAME:-Kuze}"
    make -C "$_CLAUDE_SETUP_DIR" switch MODE=bedrock
    echo "✓ Identity: ${CC_IDENTITY_DISPLAY} (Bedrock / ${AWS_REGION})"
}

# Show current profile, identity, and mode
cc-whoami() {
    local profile
    profile=$(claude-profile-current 2>/dev/null || echo "none")

    local identity="${CC_IDENTITY_DISPLAY:-${CC_IDENTITY:-none}}"

    local mode_file="${HOME}/.claude/configs/current_mode"
    local mode
    mode=$( [[ -f "$mode_file" ]] && cat "$mode_file" || echo "unknown" )

    echo "Profile:  ${profile}"
    echo "Identity: ${identity}"
    echo "Mode:     ${mode}"

    if [[ -n "$CLAUDE_CODE_OAUTH_TOKEN" ]]; then
        echo "Token:    ${CLAUDE_CODE_OAUTH_TOKEN:0:20}..."
    elif [[ -n "$AWS_PROFILE" ]]; then
        echo "AWS:      ${AWS_PROFILE} (${AWS_REGION:-unset})"
    else
        echo "Auth:     (not set)"
    fi
}

# Switch Anthropic/Bedrock mode — wraps make switch, profile-aware
cc-mode() {
    if [[ -z "$_CLAUDE_SETUP_DIR" ]]; then
        echo "⚠  Could not detect setup repo dir."
        echo "   Use: make -C <path-to-making_my_agentic_setup_brrrrrr> switch"
        return 1
    fi
    if [[ -n "$1" ]]; then
        make -C "$_CLAUDE_SETUP_DIR" switch MODE="$1"
    else
        make -C "$_CLAUDE_SETUP_DIR" switch
    fi
}

# ---------------------------------------------------------------------------
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
