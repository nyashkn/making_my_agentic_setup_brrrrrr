#!/usr/bin/env bash
#==============================================================================
# Claude Code Notification Hook Script
# Simple cross-platform notifications using terminal-notifier (macOS)
#
# Based on: https://github.com/hta218/claude-code-notifier
# Enhanced with sound support and working directory context
#==============================================================================

set -euo pipefail

# Configuration from environment
SOUND="${NOTIFICATION_SOUND:-Glass}"
TITLE="Claude Code"

# Read JSON input from stdin
input=$(cat)

# Extract hook event type
hook_event=$(echo "$input" | grep -o '"type":"[^"]*"' | cut -d'"' -f4)

# Extract working directory for context
working_dir=$(echo "$input" | grep -o '"workingDirectory":"[^"]*"' | cut -d'"' -f4 || echo "")
project_name=$(basename "$working_dir" 2>/dev/null || echo "")

#==============================================================================
# Customize message based on event type
#==============================================================================
case "$hook_event" in
  "SessionStart")
    message="Session started 🚀"
    ;;
  "SessionEnd")
    message="Session completed ✅"
    ;;
  "Stop")
    message="Task complete 🏁"
    ;;
  "SubagentStop")
    message="Agent task complete ✓"
    ;;
  "Notification")
    # Check notification type
    if echo "$input" | grep -q '"notificationType":"permission_prompt"'; then
      message="Permission needed 🔐"
    elif echo "$input" | grep -q '"notificationType":"idle_prompt"'; then
      message="Waiting for input ⏳"
    elif echo "$input" | grep -q '"notificationType":"elicitation_dialog"'; then
      message="Input needed 💬"
    else
      message="Notification from Claude 🔔"
    fi
    ;;
  *)
    message="Claude Code notification"
    ;;
esac

#==============================================================================
# Detect operating system and show notification accordingly
#==============================================================================
case "$(uname -s)" in
  Darwin*)
    # macOS - use terminal-notifier if available, fallback to osascript
    if command -v terminal-notifier >/dev/null 2>&1; then
      # Build notification with optional subtitle
      if [ -n "$project_name" ]; then
        terminal-notifier -title "$TITLE" -subtitle "$project_name" -message "$message" -sound "$SOUND" 2>/dev/null || true
      else
        terminal-notifier -title "$TITLE" -message "$message" -sound "$SOUND" 2>/dev/null || true
      fi
    else
      # Fallback to osascript
      osascript -e "display notification \"$message\" with title \"$TITLE\" sound name \"$SOUND\"" 2>/dev/null || true
    fi
    ;;

  Linux*)
    # Linux - use notify-send
    if command -v notify-send >/dev/null 2>&1; then
      notify-send "$TITLE" "$message" -i dialog-information 2>/dev/null || true
    else
      echo "[$TITLE] $message"
    fi
    ;;

  CYGWIN*|MINGW*|MSYS*)
    # Windows - use PowerShell toast notification
    powershell.exe -Command "
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null;
    [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null;
    \$template = @'
    <toast>
        <visual>
            <binding template=\"ToastGeneric\">
                <text>$TITLE</text>
                <text>$message</text>
            </binding>
        </visual>
    </toast>
'@;
    \$xml = New-Object Windows.Data.Xml.Dom.XmlDocument;
    \$xml.LoadXml(\$template);
    \$toast = [Windows.UI.Notifications.ToastNotification]::new(\$xml);
    [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('Claude Code').Show(\$toast);" 2>/dev/null || true
    ;;

  *)
    # Fallback - just echo to terminal
    echo "[$TITLE] $message"
    ;;
esac

exit 0
