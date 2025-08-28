# Multi-Agent Coordination Protocols

## Agent Communication Structure

### 1. Status Updates
Each agent must update their status in `coordination.json` when:
- Starting work on a new task
- Completing a task
- Encountering a blocker
- Going offline/online

### 2. Task Handoff Protocol

**Before Starting Work:**
1. Check `coordination.json` for current project status
2. Review `handoff_log` for recent agent communications
3. Update your `current_status` to "working"
4. Add task to your `current_tasks` array

**During Work:**
1. Document major decisions in `shared_context.decisions_made`
2. Report blockers in `shared_context.blockers`
3. Update task progress regularly

**After Completing Work:**
1. Move completed task to `completed_tasks`
2. Add handoff entry to `handoff_log` if passing work to another agent
3. Update `current_status` to "available"
4. Document any architectural decisions or changes

### 3. Agent-Specific Workflows

#### Mobile Frontend Developer
- **Focus**: Flutter app development, UI/UX, state management
- **Handoff to Backend**: API requirements, data models needed
- **Handoff from Backend**: API endpoints, response formats
- **Tools**: Flutter, Dart, Riverpod, Widget testing

#### Backend Expert
- **Focus**: FastAPI development, database design, API implementation
- **Handoff to Frontend**: API documentation, endpoint specifications
- **Handoff from Frontend**: Data requirements, business logic needs
- **Tools**: Python, FastAPI, SQLAlchemy, pytest

#### System Architect
- **Focus**: Overall system design, integration decisions, performance
- **Handoff to All**: Architecture decisions, integration patterns
- **Handoff from All**: Performance requirements, scalability needs
- **Tools**: System design, documentation, performance analysis

#### DevOps Architect
- **Focus**: Infrastructure, deployment, monitoring, CI/CD
- **Handoff to All**: Deployment procedures, environment setup
- **Handoff from All**: Infrastructure requirements, monitoring needs
- **Tools**: Docker, CI/CD pipelines, monitoring systems

### 4. Communication Templates

#### Task Handoff Template
```json
{
  "timestamp": "2025-01-25T12:00:00Z",
  "from_agent": "backend_expert",
  "to_agent": "mobile_frontend",
  "task": "Implement user authentication",
  "context": "JWT auth endpoints are ready at /auth/login and /auth/register",
  "deliverables": [
    "Login screen with email/password",
    "Registration form",
    "Token storage and management"
  ],
  "dependencies": [],
  "estimated_time": "2-3 hours",
  "notes": "API returns {access_token, refresh_token, user_profile}"
}
```

#### Status Update Template
```json
{
  "agent": "mobile_frontend",
  "status": "working",
  "current_task": "Implementing login screen",
  "progress": "50%",
  "estimated_completion": "2025-01-25T15:00:00Z",
  "blockers": [],
  "notes": "UI design complete, working on form validation"
}
```

### 5. Coordination Rules

1. **One Agent Per Domain**: Only one agent should work on their specific domain at a time
2. **Cross-Domain Consultation**: Always check with other agents for cross-cutting concerns
3. **Documentation First**: Document decisions before implementing
4. **Test Integration**: Each agent should test their integration points
5. **Regular Sync**: Update coordination.json at least every 30 minutes during active work

### 6. Conflict Resolution

If multiple agents need to work on overlapping areas:
1. System Architect has final decision on architecture choices
2. Frontend and Backend agents coordinate directly for API contracts
3. DevOps Architect handles all infrastructure decisions
4. Document conflicts and resolutions in `shared_context.decisions_made`