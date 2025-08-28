# Agent Handoff Templates

## Common Handoff Scenarios

### 1. Backend → Frontend: API Ready
```
Task: Implement user authentication UI
Context: JWT authentication endpoints are complete at /auth/login, /auth/register, /auth/refresh
Deliverables:
- Login screen with email/password validation
- Registration form with validation
- Token storage and automatic refresh
- Error handling for auth failures
Dependencies: None
Files to modify: mobile/lib/features/auth/
API Documentation: See app/features/auth/routes.py for endpoint specs
```

### 2. Frontend → Backend: API Requirements
```
Task: Create game creation API endpoints
Context: UI mockups complete for game creation flow, need backend support
Deliverables:
- POST /games/create endpoint for new games
- GET /games/{id} endpoint for game details
- POST /games/{id}/play endpoint for game sessions
- Game state persistence in database
Dependencies: Database models for games and sessions
Files to modify: app/features/games/
Data Models: Game, GameSession, UserProgress
```

### 3. System Architect → All: Architecture Decision
```
Task: Implement real-time game state synchronization
Context: Games need real-time updates for multiplayer features
Deliverables:
- WebSocket connection management
- Real-time state broadcasting
- Conflict resolution for simultaneous moves
- Connection recovery mechanisms  
Architecture Decision: Use Socket.IO for real-time communication
Dependencies: Redis for message broadcasting
Technology Stack: FastAPI-SocketIO + Flutter socket_io_client
```

### 4. DevOps → All: Infrastructure Update
```
Task: Deploy staging environment
Context: Code is ready for staging deployment and testing
Deliverables:
- Staging environment at staging.aiminigames.com
- Automated deployment pipeline from main branch
- Environment-specific configuration
- Database migrations and seed data
Infrastructure: 
- Backend: Cloud Run with PostgreSQL Cloud SQL
- Frontend: Firebase Hosting
- Redis: Cloud Memorystore
Monitoring: Logs available in Cloud Console
```

### 5. Frontend → DevOps: Deployment Requirements
```
Task: Set up mobile app distribution
Context: Flutter app is ready for alpha testing distribution
Deliverables:
- Android APK build pipeline
- iOS TestFlight setup
- Automated versioning and signing
- Distribution to test users
Dependencies: Apple Developer and Google Play Console access
Build Requirements: 
- Android: API level 21+
- iOS: iOS 12+
- Flutter 3.16+
```

### 6. Backend → DevOps: Production Setup
```
Task: Configure production database and caching
Context: Application ready for production deployment
Deliverables:
- Production PostgreSQL with backups
- Redis cluster for caching and sessions
- Database connection pooling
- Monitoring and alerting setup
Performance Requirements:
- Handle 1000 concurrent users
- < 200ms API response times
- 99.9% uptime SLA
Security: SSL certificates, firewall rules, secrets management
```

## Handoff Checklist Template

When handing off work, ensure you complete:

### Pre-Handoff
- [ ] Code is tested and working locally
- [ ] Documentation is updated
- [ ] Integration points are clearly defined
- [ ] Dependencies are documented
- [ ] Known issues/limitations are noted

### During Handoff
- [ ] Update coordination.json with handoff details
- [ ] Provide context and background
- [ ] Share relevant code locations
- [ ] Explain design decisions made
- [ ] Set clear expectations and timeline

### Post-Handoff
- [ ] Mark your tasks as completed
- [ ] Update your status to available
- [ ] Be available for questions during transition
- [ ] Review the receiving agent's questions
- [ ] Validate integration when complete

## Emergency Handoff Procedures

### When Agent is Blocked
1. Document the blocker in coordination.json
2. Update status to "blocked" 
3. Create emergency handoff with blocker details
4. Request help from System Architect or other agents
5. Provide all context needed for someone else to continue

### When Agent Goes Offline Unexpectedly  
1. Other agents should check coordination.json for last status
2. System Architect takes over incomplete critical tasks
3. Review handoff_log for any pending work
4. Document decisions made in agent's absence
5. Brief returning agent on changes made

## Communication Best Practices

### Clear Context Setting
- Always explain WHY something needs to be done
- Provide business context, not just technical requirements
- Link to relevant documentation or design decisions
- Mention any user experience considerations

### Technical Handoffs
- Share exact file paths and line numbers
- Explain data structures and API contracts
- Provide test cases or example usage
- Document any performance considerations
- Note security implications

### Cross-Domain Coordination
- Frontend + Backend: API contracts, data models, error handling
- Backend + DevOps: Infrastructure requirements, scaling needs
- Frontend + DevOps: Build requirements, deployment needs
- All + System Architect: Performance, security, scalability decisions