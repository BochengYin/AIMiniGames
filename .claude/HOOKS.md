# Claude Code Hooks for AI Mini Games

This directory contains Claude Code hooks to automate development workflows.

## Available Hooks

### 1. Stop Notification Hook
**Trigger:** After `TodoWrite` operations (task updates)
**Purpose:** Play system sound notification when tasks are completed

**Features:**
- Plays macOS system sounds (Glass.aiff for completion)
- Fallback to system beep if sound files unavailable  
- Notifies you when task status changes

### 2. Type Check Hook
**Trigger:** After `Edit|MultiEdit|Write` operations (file changes)
**Purpose:** Catch type errors and linting issues before execution

**Features:**
- **Python files (.py):** Uses `mypy` for type checking and `flake8` for linting
- **Dart files (.dart):** Uses `flutter analyze` or `dart analyze`
- Displays errors similar to VS Code TypeScript linter
- Shows line numbers, error types, and descriptions

## Installation

The hooks are automatically configured via `.claude/settings.json` and will run when:
1. You update task status with TodoWrite → Sound notification plays
2. You edit Python/Dart files → Type checking runs automatically

## Requirements

### For Type Checking:
```bash
# Python type checking
pip install mypy flake8

# Flutter/Dart analysis (already installed with Flutter)
flutter doctor  # Verify Flutter is installed
```

### For Sound Notifications:
- macOS system (uses `afplay` command)
- System audio permissions enabled

## Configuration

### Customize Notification Sounds
Edit `.claude/hooks/stop_notification.py` and modify the `sound_options` list:
```python
sound_options = [
    "/System/Library/Sounds/Glass.aiff",    # Current default
    "/System/Library/Sounds/Hero.aiff",     # Achievement sound
    "/System/Library/Sounds/Purr.aiff",     # Gentle sound  
    # Add your own sound files here
]
```

### Customize Type Checking
Edit `.claude/hooks/type_checker.py` to:
- Add more linters (pylint, black, etc.)
- Change error formatting
- Add support for other file types

## Hook Configuration

The hooks are configured in `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "TodoWrite",
        "hooks": [{"type": "command", "command": "python .claude/hooks/stop_notification.py"}]
      },
      {
        "matcher": "Edit|MultiEdit|Write", 
        "hooks": [{"type": "command", "command": "python .claude/hooks/type_checker.py"}]
      }
    ]
  }
}
```

## Testing Hooks

### Test Stop Notification:
1. Update any task status using TodoWrite
2. Should hear system sound notification

### Test Type Checking:
1. Edit a Python file with type errors (e.g., `x: int = "string"`)
2. Should see linter errors displayed after saving
3. Edit a Dart file with syntax errors
4. Should see Flutter analyze errors

## Troubleshooting

### Sound Not Playing:
- Check macOS audio permissions
- Verify sound files exist in `/System/Library/Sounds/`
- Test manually: `afplay /System/Library/Sounds/Glass.aiff`

### Type Checking Not Working:
- Ensure `mypy` and `flake8` installed: `pip install mypy flake8`
- For Flutter: Ensure `flutter doctor` shows no issues
- Check hook execution: Add `echo "Hook running"` to scripts for debugging

### Hook Not Triggering:
- Verify `.claude/settings.json` exists and is valid JSON
- Check file permissions: `ls -la .claude/hooks/`
- Ensure scripts are executable: `chmod +x .claude/hooks/*.py`

## Example Output

### Type Check Hook Output:
```
🔍 Checking: app/features/auth/routes.py
⚠️  3 linter errors

❌ app/features/auth/routes.py:45:12: error: Incompatible return value type
❌ app/features/auth/routes.py:67:8: error: Argument 1 has incompatible type
⚠️ app/features/auth/routes.py:12:1: W291 trailing whitespace

🔧 2 errors, 1 warnings
```

### Stop Notification Output:
```
📋 Task status updated  
🔔 Task completed! Notification sound played.
```