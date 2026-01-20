# Claude Code Notification System

Comprehensive guide for getting notified when Claude Code tasks complete or require input across multiple terminal instances.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Notification Backends](#notification-backends)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [Advanced Topics](#advanced-topics)

## Overview

The Claude Code notification system solves a critical workflow problem: **how to know when Claude has finished a task when you have multiple terminal windows or Claude instances running**.

### The Problem

Without notifications, you need to:
- Constantly check each terminal window to see if Claude is done
- Remember which window has which task running
- Manually switch between windows and Spaces to check progress

### The Solution

This notification system provides:
- **Desktop notifications** when tasks complete or permission is needed
- **Multi-instance awareness** to identify which window finished (cc-notifier)
- **Click-to-focus** to jump directly to the relevant window (cc-notifier)
- **Remote support** for SSH sessions with push notifications (cc-notifier)
- **Flexible backends** from zero-dependency native solutions to advanced multi-window tracking

## Quick Start

### 1. List Available Backends

```bash
make notifications-list
```

This shows all available notification backends and their capabilities.

### 2. Install a Backend

For quick setup with zero dependencies:

```bash
make notifications-install BACKEND=osascript
```

For advanced multi-instance tracking (recommended for multiple Claude sessions):

```bash
make notifications-install BACKEND=cc-notifier
```

### 3. Enable Notifications

```bash
make notifications-enable BACKEND=osascript
# or
make notifications-enable BACKEND=cc-notifier
```

### 4. Test It

```bash
make notifications-test
```

You should see a notification appear!

## Notification Backends

### Comparison Table

| Backend | Dependencies | Multi-Instance | Click-to-Focus | Remote | Best For |
|---------|--------------|----------------|----------------|--------|----------|
| **osascript** | None (macOS built-in) | ❌ | ❌ | ❌ | Quick setup, single instance |
| **terminal-notifier** | Homebrew | ❌ | ❌ | ❌ | Better branding than osascript |
| **cc-notifier** | Hammerspoon, terminal-notifier | ✅ | ✅ | ✅ | Multiple instances, professional workflow |

### osascript (Native macOS)

**What it is:** Uses macOS AppleScript to send native notifications through the built-in notification system.

**Pros:**
- Zero setup required (built into macOS)
- Works immediately
- Customizable sounds
- No external dependencies

**Cons:**
- Shows Script Editor icon (not Claude branding)
- No window tracking
- Can't differentiate between multiple Claude instances
- No click-to-focus functionality

**When to use:**
- You only run one Claude Code instance at a time
- You want the simplest possible setup
- You don't need advanced features

**Installation:**
```bash
make notifications-install BACKEND=osascript
make notifications-enable BACKEND=osascript
```

### terminal-notifier

**What it is:** Command-line tool for macOS Notification Center with more customization options.

**Pros:**
- Claude Desktop branding (using `-sender` flag)
- More control than osascript
- Can show working directory in subtitle
- Customizable sounds

**Cons:**
- Requires Homebrew installation
- Still no window tracking
- Can't identify which instance finished
- No click-to-restore specific window

**When to use:**
- You want better branding than osascript
- You're okay with installing via Homebrew
- You run 1-2 Claude instances at most

**Installation:**
```bash
brew install terminal-notifier
make notifications-install BACKEND=terminal-notifier
make notifications-enable BACKEND=terminal-notifier
```

### cc-notifier (Advanced) ⭐ RECOMMENDED

**What it is:** Smart notification system with window tracking and multi-instance awareness.

**Pros:**
- ✅ **Window tracking** - knows which specific terminal/IDE has Claude running
- ✅ **Smart notifications** - only notifies when you've switched away from that window
- ✅ **Click-to-focus** - clicking notification jumps to exact window across macOS Spaces
- ✅ **Multi-instance support** - differentiates between multiple Claude sessions
- ✅ **Remote SSH support** - sends push notifications when running over SSH
- ✅ **Mobile workflow** - Pushover integration for notifications on iOS/Android

**Cons:**
- More complex setup (requires Hammerspoon)
- Additional dependencies
- Requires Hammerspoon configuration

**When to use:**
- You run multiple Claude Code instances simultaneously
- You work across multiple terminal windows or Spaces
- You need to know which specific instance finished
- You work remotely over SSH
- You want a professional, production-ready workflow

**Installation:**
```bash
make notifications-install BACKEND=cc-notifier
# Follow the on-screen instructions to:
# 1. Start Hammerspoon
# 2. Grant accessibility permissions
# 3. Configure Pushover (optional, for remote)

make notifications-enable BACKEND=cc-notifier
```

## Installation

### Prerequisites

- macOS (all backends require macOS)
- This repository cloned and installed (`make install`)
- For cc-notifier: Hammerspoon and terminal-notifier

### Step-by-Step Installation

#### Option 1: osascript (Simplest)

```bash
# No dependencies needed!
make notifications-install BACKEND=osascript
make notifications-enable BACKEND=osascript
make notifications-test
```

#### Option 2: terminal-notifier

```bash
# Install terminal-notifier
brew install terminal-notifier

# Install and enable
make notifications-install BACKEND=terminal-notifier
make notifications-enable BACKEND=terminal-notifier
make notifications-test
```

#### Option 3: cc-notifier (Advanced)

```bash
# Run the automated installer
make notifications-install BACKEND=cc-notifier

# This will:
# 1. Install Hammerspoon (via Homebrew)
# 2. Install terminal-notifier (via Homebrew)
# 3. Download and install cc-notifier binary
# 4. Configure Hammerspoon with CCNotifier Spoon
# 5. Create default configuration

# After installation:
# 1. Start Hammerspoon: open -a Hammerspoon
# 2. Grant accessibility permissions:
#    System Settings > Privacy & Security > Accessibility > Enable Hammerspoon

# Enable hooks
make notifications-enable BACKEND=cc-notifier

# Test
make notifications-test BACKEND=cc-notifier
```

### Verifying Installation

Check the status of your notification setup:

```bash
make notifications-status
```

This shows:
- Current mode (anthropic/bedrock)
- Active backend
- Sound configuration
- Enabled hooks

## Configuration

### Sound Customization

Edit your personal config to change notification sounds:

```toml
# ~/.claude/configs/personal.toml

[notifications]
sound = "Submarine"  # Options: Glass, Submarine, Frog, Purr, Ping, Pop, Basso, Blow, Bottle, Hero, Morse, Tink
```

After changing, regenerate your environment:

```bash
make switch MODE=anthropic  # or bedrock
```

### Pushover (Remote Notifications)

For cc-notifier remote SSH support:

1. Sign up for Pushover: https://pushover.net
2. Create an application and get your API token
3. Edit your config:

```toml
# ~/.claude/configs/personal.toml

[notifications]
backend = "cc-notifier"
pushover_api_token = "your_api_token_here"
pushover_user_key = "your_user_key_here"
```

4. Regenerate config:

```bash
make switch MODE=anthropic
```

5. Edit Hammerspoon config:

```lua
-- ~/.hammerspoon/init.lua
hs.loadSpoon("CCNotifier")
hs.settings.set("pushover_api_token", "your_api_token_here")
hs.settings.set("pushover_user_key", "your_user_key_here")
```

### Hooks Configuration

The notification system uses Claude Code hooks to trigger notifications. These are automatically configured when you run `make notifications-enable`, but you can customize them:

```json
// ~/.claude/settings.json
{
  "hooks": {
    "Stop": [/* Triggered when main agent finishes */],
    "SubagentStop": [/* Triggered when subagents complete */],
    "Notification": [/* Triggered for permission prompts, idle alerts */],
    "PermissionRequest": [/* Triggered when permissions are requested */],
    "SessionStart": [/* cc-notifier: captures window ID */],
    "SessionEnd": [/* cc-notifier: cleanup */]
  }
}
```

## Usage

### Basic Workflow

1. Start Claude Code in a terminal:
   ```bash
   claude
   ```

2. Give Claude a task:
   ```
   > Please analyze all TypeScript files and suggest improvements
   ```

3. Switch to another window/Space to work on something else

4. When Claude finishes, you'll get a notification:
   - **osascript/terminal-notifier**: "Task complete"
   - **cc-notifier**: "Task complete" (only if you switched away)

5. Click the notification (cc-notifier only) to jump back to that window

### Multi-Instance Workflow (cc-notifier)

This is where cc-notifier shines:

1. **Terminal 1**: Start Claude Code
   ```bash
   cd ~/project1
   claude
   ```

2. **Terminal 2**: Start another Claude Code session
   ```bash
   cd ~/project2
   claude
   ```

3. **Terminal 1**: Give Claude a long-running task
   ```
   > Refactor the authentication system
   ```

4. Switch to Terminal 2 or another window

5. When Terminal 1's Claude finishes:
   - You get a notification: "Task complete - project1"
   - Click notification → jumps to Terminal 1

6. **Terminal 2**: Give Claude a task
   ```
   > Run the test suite
   ```

7. Switch to Terminal 1

8. When Terminal 2 finishes:
   - You get a notification: "Task complete - project2"
   - Click notification → jumps to Terminal 2

### Permission Prompts

When Claude needs permission (e.g., to run bash commands), you'll get a notification:

```
"Permission needed"
```

Click to jump to that window and approve/deny.

### Testing Notifications

Test that everything works:

```bash
# Test default backend
make notifications-test

# Test specific backend
make notifications-test BACKEND=cc-notifier
```

## Troubleshooting

### Notifications Not Appearing

**Check notification permissions:**

1. System Settings > Notifications
2. Find "Script Editor" (osascript) or "Claude for Desktop" (terminal-notifier)
3. Ensure "Allow Notifications" is enabled

**Check hooks are enabled:**

```bash
make notifications-status
```

Should show enabled hooks: Stop, SubagentStop, Notification, etc.

**Check settings.json:**

```bash
cat ~/.claude/settings.json | grep -A 5 '"hooks"'
```

### cc-notifier Not Working

**Check Hammerspoon is running:**

```bash
ps aux | grep Hammerspoon
```

If not running: `open -a Hammerspoon`

**Check accessibility permissions:**

System Settings > Privacy & Security > Accessibility > Hammerspoon should be enabled

**Check cc-notifier binary:**

```bash
ls -la ~/.cc-notifier/cc-notifier
~/.cc-notifier/cc-notifier --version
```

**Check Hammerspoon logs:**

In Hammerspoon menu bar icon > Console

Look for errors related to CCNotifier

### Click-to-Focus Not Working (cc-notifier)

**Check accessibility permissions:**

Hammerspoon needs accessibility permissions to switch windows.

**Check Hammerspoon configuration:**

```bash
cat ~/.hammerspoon/init.lua
```

Should contain: `hs.loadSpoon("CCNotifier")`

**Reload Hammerspoon:**

Hammerspoon menu > Reload Config

### terminal-notifier Not Found

Install it:

```bash
brew install terminal-notifier
```

Verify:

```bash
which terminal-notifier
terminal-notifier --version
```

## Advanced Topics

### Customizing Notification Messages

Edit the notification scripts to customize messages:

**osascript:**
```bash
vim shell/notifications/osascript-notifier.sh
```

**terminal-notifier:**
```bash
vim shell/notifications/terminal-notifier.sh
```

### Adding Custom Sounds

**macOS system sounds** are in `/System/Library/Sounds/`:

```bash
ls /System/Library/Sounds/
```

Use the filename (without .aiff extension) in your config:

```toml
[notifications]
sound = "Submarine"
```

**Custom sound files:**

For terminal-notifier, you can use custom audio files:

```bash
terminal-notifier -sound ~/custom-sound.aiff
```

### Selective Hook Enabling

If you only want notifications for specific events:

```bash
# Enable manually by editing ~/.claude/settings.json
vim ~/.claude/settings.json
```

Remove hooks you don't want. For example, to only get notifications when tasks complete (not for permissions):

```json
{
  "hooks": {
    "Stop": [/* keep this */],
    "SubagentStop": [/* keep this */],
    // Remove Notification and PermissionRequest hooks
  }
}
```

### Integration with Other Tools

The notification scripts read JSON from stdin, so you can integrate them with other tools:

```bash
# Send custom notification
echo '{"type":"Stop"}' | shell/notifications/osascript-notifier.sh
```

### Remote SSH Setup (cc-notifier)

When working over SSH, cc-notifier can send push notifications to your phone:

1. Install Pushover app on iOS/Android
2. Configure Pushover credentials (see Configuration section)
3. SSH to remote machine
4. Start Claude Code
5. When tasks complete, you get a push notification on your phone
6. Use Blink Shell or similar to jump back to the SSH session

### Disabling Notifications

Temporarily disable all notifications:

```bash
make notifications-disable
```

This removes all notification hooks from settings.json but keeps your backend configuration.

Re-enable later:

```bash
make notifications-enable BACKEND=osascript  # or your preferred backend
```

### Switching Backends

To switch from one backend to another:

```bash
# Disable current backend
make notifications-disable

# Install new backend
make notifications-install BACKEND=cc-notifier

# Enable new backend
make notifications-enable BACKEND=cc-notifier

# Test
make notifications-test
```

## Resources

- [Claude Code Hooks Documentation](https://code.claude.com/docs/en/hooks.md)
- [cc-notifier GitHub](https://github.com/Rendann/cc-notifier)
- [terminal-notifier GitHub](https://github.com/julienXX/terminal-notifier)
- [Hammerspoon](https://www.hammerspoon.org/)
- [Pushover](https://pushover.net)

## Support

If you encounter issues:

1. Check troubleshooting section above
2. Run `make notifications-status` to verify configuration
3. Check hook logs in Claude Code output
4. For cc-notifier issues, check Hammerspoon console
5. Open an issue in this repository with:
   - Output of `make notifications-status`
   - Your backend choice
   - Error messages or unexpected behavior

## License

This notification system is part of the Claude Code configuration management system.
