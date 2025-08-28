# Multi-Agent Collaboration Guide for AI Mini Games

## Overview

This guide explains how to coordinate multiple Claude Code agents working together on the AI Mini Games project. Each agent has specialized roles and follows structured communication protocols.

## Quick Start: Opening Multiple Agents

### Method 1: Using Claude Code CLI
```bash
# Terminal 1 - Main coordination agent
claude-code /Users/by/AIMiniGames

# Terminal 2 - Mobile Frontend Developer  
claude-code /Users/by/AIMiniGames --agent-role mobile-frontend

# Terminal 3 - Backend Expert
claude-code /Users/by/AIMiniGames --agent-role backend-expert

# Terminal 4 - System Architect
claude-code /Users/by/AIMiniGames --agent-role system-architect
```

### Method 2: Using Task Tool with Specialized Agents
From any Claude Code instance, use the Task tool to invoke specialized agents:
```markdown
Use the Task tool with subagent_type:
- "mobile-frontend-developer" - For Flutter UI work
- "python-expert" - For backend API development  
- "system-architect" - For architectural decisions
- "devops-architect" - For infrastructure and deployment
```

## Agent Roles and Responsibilities

### 🎨 Mobile Frontend Developer
**Primary Focus**: Flutter mobile app development
- **Responsibilities**: UI/UX implementation, state management, mobile optimizations
- **Tools**: Flutter, Dart, Riverpod, widget testing
- **Key Files**: `mobile/lib/`, `mobile/pubspec.yaml`

### 🔧 Python Expert (Backend) 
**Primary Focus**: FastAPI backend development
- **Responsibilities**: API endpoints, database models, backend logic
- **Tools**: Python, FastAPI, SQLAlchemy, pytest
- **Key Files**: `app/`, `requirements.txt`, `alembic/`

### 🏗️ System Architect
**Primary Focus**: Overall system design and integration
- **Responsibilities**: Architecture decisions, component integration, performance
- **Tools**: System design, documentation, performance analysis
- **Key Files**: Architecture docs, integration specifications

### 🚀 DevOps Architect
**Primary Focus**: Infrastructure and deployment
- **Responsibilities**: Docker, CI/CD, deployment pipelines, monitoring
- **Tools**: Docker, GitHub Actions, cloud services
- **Key Files**: `Dockerfile`, `.github/`, `docker-compose.yml`

## Communication System

### Status Tracking
All agents coordinate through shared files:
- **Coordination Hub**: `.claude/agents/shared/coordination.json`
- **Status Tracker**: `.claude/agents/shared/status_tracker.py`
- **Protocols**: `.claude/agents/shared/protocols.md`

### Checking Agent Status
```bash
# Check all agent statuses
python .claude/agents/shared/status_tracker.py

# Check specific agent
python .claude/agents/shared/status_tracker.py status mobile_frontend

# Update your status  
python .claude/agents/shared/status_tracker.py update mobile_frontend working "Implementing login UI"
```

## Multi-Agent Workflow Example

### Scenario: Implement User Authentication

#### Step 1: System Architect Plans
```markdown
Architecture Decision: JWT-based authentication with refresh tokens
- FastAPI backend provides /auth endpoints
- Flutter app stores tokens securely  
- Redis for session management
```

#### Step 2: Backend Expert Implements
```markdown
Task: Create authentication endpoints
Deliverables:
- POST /auth/register
- POST /auth/login  
- POST /auth/refresh
- User model and JWT utilities
```

#### Step 3: Handoff to Frontend
```markdown
From: backend_expert
To: mobile_frontend
Task: Implement authentication UI
Context: JWT endpoints ready, see app/features/auth/routes.py
Deliverables: Login screen, registration form, token management
```

#### Step 4: DevOps Sets Up Testing
```markdown
Task: Deploy auth system to staging
Context: Backend and frontend auth ready for integration testing
Deliverables: Staging environment with auth flow working end-to-end
```

## Best Practices for Multi-Agent Work

### 1. Before Starting Work
- Check `coordination.json` for current project status
- Review pending handoffs for your agent role
- Update your status to "working" and add current task
- Look for blockers or decisions that might affect your work

### 2. During Development
- Update progress regularly in coordination.json
- Document architectural decisions as you make them
- Report blockers immediately so other agents can help
- Test integration points with other agents' work

### 3. After Completing Tasks  
- Mark tasks as completed and update status to "available"
- Create handoff entries for work that needs to continue
- Document what you learned and any technical debt
- Test that your changes don't break other agents' work

### 4. Cross-Agent Communication
- Use the handoff templates in `.claude/agents/handoff_templates.md`
- Provide clear context and deliverables  
- Share exact file paths and code locations
- Explain design decisions and constraints

## Common Multi-Agent Scenarios

### Parallel Development
Multiple agents working on independent features:
- Backend: API endpoints
- Frontend: UI screens  
- DevOps: Infrastructure setup
- Architect: Performance monitoring

### Sequential Handoffs
Work that flows between agents:
1. Architect: Design API specification
2. Backend: Implement API endpoints
3. Frontend: Build UI consuming APIs
4. DevOps: Deploy and monitor

### Collaborative Problem Solving
When agents need to solve complex cross-cutting issues:
1. All agents identify the problem scope
2. Architect proposes solution approach
3. Specialists implement in their domains
4. Integration testing by all agents

## Troubleshooting Multi-Agent Issues

### Agent Conflicts
If multiple agents modify the same files:
1. System Architect mediates technical decisions
2. Use git branches for experimental work
3. Communicate changes in coordination.json
4. Review each other's code before merging

### Communication Breakdowns
If handoffs aren't working smoothly:
1. Check coordination.json for status mismatches
2. Use the status tracker to see who's available
3. Be more explicit in handoff descriptions
4. Ask System Architect to clarify requirements

### Integration Problems
When different agents' work doesn't connect properly:
1. Test integration points early and often
2. Share API contracts and data models explicitly  
3. Use the shared coordination system to track dependencies
4. Schedule integration checkpoints between agents

## Getting Started

1. **Open your specialized agent**: Use Claude Code CLI or Task tool
2. **Check project status**: Run `python .claude/agents/shared/status_tracker.py`
3. **Review pending handoffs**: Look for tasks assigned to your role
4. **Update your status**: Mark yourself as working on current task
5. **Start coordinating**: Follow the protocols and communicate progress

The multi-agent system is designed to help you work efficiently while maintaining coordination. Focus on your specialized role while staying connected to the broader project context.