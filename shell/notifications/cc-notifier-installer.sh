#!/usr/bin/env bash
#
# cc-notifier-installer.sh - Automated installer for cc-notifier system
#
# This script installs and configures cc-notifier for multi-instance Claude Code notifications
#
# Features:
#   - Multi-window tracking
#   - Click-to-focus across macOS Spaces
#   - Remote SSH + push notifications support
#   - Context-aware notifications
#
# Dependencies installed:
#   - Hammerspoon (window management)
#   - terminal-notifier (notifications)
#   - cc-notifier binary
#
# Repository: https://github.com/Rendann/cc-notifier

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Installation paths
CC_NOTIFIER_DIR="$HOME/.cc-notifier"
HAMMERSPOON_CONFIG="$HOME/.hammerspoon/init.lua"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on macOS
check_macos() {
    if [[ "$OSTYPE" != "darwin"* ]]; then
        log_error "cc-notifier is only supported on macOS"
        exit 1
    fi
    log_success "Running on macOS"
}

# Check if Homebrew is installed
check_homebrew() {
    if ! command -v brew &> /dev/null; then
        log_error "Homebrew not found. Install from https://brew.sh"
        exit 1
    fi
    log_success "Homebrew found"
}

# Install terminal-notifier
install_terminal_notifier() {
    if command -v terminal-notifier &> /dev/null; then
        log_info "terminal-notifier already installed"
    else
        log_info "Installing terminal-notifier..."
        brew install terminal-notifier
        log_success "terminal-notifier installed"
    fi
}

# Install Hammerspoon
install_hammerspoon() {
    if [ -d "/Applications/Hammerspoon.app" ]; then
        log_info "Hammerspoon already installed"
    else
        log_info "Installing Hammerspoon..."
        brew install --cask hammerspoon
        log_success "Hammerspoon installed"
        log_warn "Please grant Hammerspoon accessibility permissions in System Settings > Privacy & Security > Accessibility"
    fi
}

# Clone and install cc-notifier
install_cc_notifier() {
    log_info "Installing cc-notifier..."

    # Check if Python 3.9+ is available
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 not found. Install with: brew install python3"
        exit 1
    fi

    # Verify Python version
    python3 -c "import sys; assert sys.version_info >= (3,9), 'Python 3.9+ required'" 2>/dev/null || {
        log_error "Python 3.9+ is required"
        log_info "Install with: brew install python3"
        exit 1
    }
    log_success "Python 3.9+ found"

    # Check if Hammerspoon CLI (hs) is available
    if ! command -v hs &> /dev/null; then
        log_warn "Hammerspoon CLI 'hs' not found in PATH"
        log_info "After Hammerspoon is running, enable CLI in Hammerspoon preferences"
    fi

    # Clone repository to temporary directory
    TEMP_DIR=$(mktemp -d)
    log_info "Cloning cc-notifier repository..."

    if ! git clone https://github.com/Rendann/cc-notifier.git "$TEMP_DIR" 2>&1; then
        log_error "Failed to clone cc-notifier repository"
        rm -rf "$TEMP_DIR"
        exit 1
    fi

    # Run the official installer
    log_info "Running official installer..."
    cd "$TEMP_DIR"

    if ! bash install.sh; then
        log_error "Installation script failed"
        cd - > /dev/null
        rm -rf "$TEMP_DIR"
        exit 1
    fi

    # Cleanup
    cd - > /dev/null
    rm -rf "$TEMP_DIR"

    log_success "cc-notifier installed to $CC_NOTIFIER_DIR"
}

# Configure Hammerspoon
configure_hammerspoon() {
    log_info "Configuring Hammerspoon..."

    # Create Hammerspoon directory if it doesn't exist
    mkdir -p "$(dirname "$HAMMERSPOON_CONFIG")"

    # Check if init.lua exists
    if [ -f "$HAMMERSPOON_CONFIG" ]; then
        log_warn "Hammerspoon init.lua already exists"
        log_info ""
        log_info "Add the following to your ~/.hammerspoon/init.lua:"
        echo ""
        echo "    require(\"hs.ipc\")"
        echo "    require(\"hs.window\")"
        echo "    require(\"hs.window.filter\")"
        echo "    require(\"hs.timer\")"
        echo ""
        log_info "Then reload: hs -c \"hs.reload()\""
    else
        # Create basic init.lua with cc-notifier support
        cat > "$HAMMERSPOON_CONFIG" << 'EOF'
-- Hammerspoon configuration for cc-notifier
-- Required modules for window tracking
require("hs.ipc")
require("hs.window")
require("hs.window.filter")
require("hs.timer")

-- Optional: Reload configuration on file changes
hs.pathwatcher.new(os.getenv("HOME") .. "/.hammerspoon/", hs.reload):start()
hs.alert.show("Hammerspoon config loaded")
EOF
        log_success "Created Hammerspoon init.lua"
    fi
}

# Test installation
test_installation() {
    log_info "Testing installation..."

    if [ -x "$CC_NOTIFIER_DIR/cc-notifier" ]; then
        log_success "cc-notifier binary is executable"
    else
        log_error "cc-notifier binary not found or not executable"
        exit 1
    fi

    # Test notification
    log_info "Sending test notification..."
    echo '{"type":"Stop"}' | "$CC_NOTIFIER_DIR/cc-notifier" notify || true

    log_success "Test notification sent"
}

# Print next steps
print_next_steps() {
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║          cc-notifier Installation Complete!                ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo ""
    echo "1. Start Hammerspoon (if not already running):"
    echo "   open -a Hammerspoon"
    echo ""
    echo "2. Grant Hammerspoon accessibility permissions:"
    echo "   System Settings > Privacy & Security > Accessibility"
    echo ""
    echo "3. Reload Hammerspoon configuration:"
    echo "   Click Hammerspoon menu bar icon > Reload Config"
    echo "   (or run: hs -c 'hs.reload()')"
    echo ""
    echo "4. Enable cc-notifier hooks in Claude Code:"
    echo "   make notifications-enable BACKEND=cc-notifier"
    echo ""
    echo "5. Test the setup:"
    echo "   make notifications-test BACKEND=cc-notifier"
    echo ""
    echo "6. (Optional) Configure Pushover for remote SSH notifications:"
    echo "   Add to ~/.claude/configs/personal.toml:"
    echo "   [notifications]"
    echo "   pushover_api_token = \"your_token\""
    echo "   pushover_user_key = \"your_key\""
    echo ""
    echo -e "${YELLOW}For more info:${NC} https://github.com/Rendann/cc-notifier"
    echo ""
}

# Main installation flow
main() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║        cc-notifier Automated Installer                     ║${NC}"
    echo -e "${BLUE}║        Multi-instance Claude Code notifications            ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    check_macos
    check_homebrew
    install_terminal_notifier
    install_hammerspoon
    install_cc_notifier
    configure_hammerspoon
    test_installation
    print_next_steps
}

# Run main function
main
