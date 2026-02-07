#!/bin/bash
# Permission dialog script using NotifiCLI
# Shows interactive notification in Notification Center with "Allow" and "Deny" buttons

# Parse hook data from stdin
input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name')

# Simple message - just show tool name as-is
# User has many different MCPs, don't try to parse/format
if [[ "$tool_name" == "Bash" ]]; then
    command=$(echo "$input" | jq -r '.tool_input.command // "unknown"')
    message="Bash: $command"
else
    message="$tool_name"
fi

# Show NotifiCLI notification with action buttons
# notificli blocks until user clicks a button
# Returns button label via stdout: "Allow", "Deny", or "dismissed"
response=$(notificli -persistent \
    -title "Claude Code Permission" \
    -message "$message" \
    -actions "Allow,Deny" \
    -sound Glass)

# Return appropriate exit code to Claude Code
case "$response" in
    "Allow")
        exit 0  # Approve
        ;;
    *)
        exit 2  # Deny (covers "Deny", "dismissed")
        ;;
esac
