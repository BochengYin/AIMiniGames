# Claude Code Task Documentation

This directory contains task planning and completion documentation for Claude Code sessions.

## Directory Structure

```
.claude/
├── tasks/           # Individual task documentation
│   ├── TEMPLATE.md  # Template for new tasks
│   └── [task files] # Actual task documentation
└── README.md        # This file
```

## Usage

### Starting a New Task

1. Copy `TEMPLATE.md` to a new file with descriptive name:
   ```bash
   cp .claude/tasks/TEMPLATE.md .claude/tasks/$(date +%Y-%m-%d)_task_name.md
   ```

2. Fill out the planning sections before starting development

3. Use Claude Code's plan mode to review and refine the plan

### During Development

- Update the "Implementation Log" section with progress
- Mark completed steps with ✅
- Note any issues or deviations from the plan

### Task Completion

- Fill out the "Task Completion Summary" section
- Include detailed file changes and reasoning
- Add handover notes for future engineers

## File Naming Convention

Format: `YYYY-MM-DD_descriptive_task_name.md`

Examples:
- `2024-01-15_implement_jwt_authentication.md`
- `2024-01-16_add_game_marketplace_ui.md`
- `2024-01-17_fix_websocket_connection_stability.md`

## Benefits

- **Continuity**: Future Claude Code instances understand previous work
- **Documentation**: Complete record of implementation decisions
- **Handover**: Easy transfer of knowledge to human developers
- **Planning**: Structured approach reduces implementation errors