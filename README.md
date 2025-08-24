# 🎮 AI Mini Games

An AI-powered platform for creating, sharing, and playing mini-games. Users can describe games in natural language and the AI will generate playable mini-games within minutes.

## 🌟 Features

- **🤖 AI Game Generation**: Describe your game idea and watch AI bring it to life
- **📱 Cross-Platform Mobile App**: Flutter-based app for iOS and Android
- **🎯 Game Marketplace**: Share and discover AI-generated games
- **👥 Multiplayer Gaming**: Play with friends in real-time
- **🏆 Achievement System**: Track progress and compete with others
- **☁️ Cloud Sync**: Your games are saved and synced across devices

## 🏗️ Architecture

### Frontend (Mobile App)
- **Framework**: Flutter 3.16+
- **State Management**: Riverpod
- **Navigation**: GoRouter
- **Local Storage**: Hive + Secure Storage
- **Game Engine**: Flame

### Backend (API)
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy
- **Cache/Queue**: Redis + Celery
- **Authentication**: JWT tokens
- **AI Integration**: OpenAI API + Hugging Face
- **File Storage**: S3-compatible storage

### DevOps
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **Deployment**: AWS ECS / GCP Cloud Run
- **Monitoring**: Sentry + Prometheus

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Flutter 3.16+ (for mobile development)
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/ai-mini-games.git
cd ai-mini-games
```

### 2. Initial Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# At minimum, set OPENAI_API_KEY for AI features

# Run setup (installs dependencies, starts services)
make setup
```

### 3. Start Development Environment
```bash
# Start all backend services
make start

# The API will be available at:
# - Backend API: http://localhost:8000
# - API Documentation: http://localhost:8000/docs
# - Database: localhost:5432
# - Redis: localhost:6379
```

### 4. Start Mobile App
```bash
# Setup Flutter dependencies
make flutter-setup

# Run on iOS simulator
make flutter-run-ios

# Run on Android emulator  
make flutter-run-android

# Or manually:
cd mobile
flutter run
```

## 📖 Documentation

- [Backend Architecture](backend_architecture.md)
- [Implementation Guide](implementation_guide.md) 
- [Project Structure](project_structure.md)
- [Setup Instructions](setup_instructions.md)

## 🛠️ Development Commands

| Command | Description |
|---------|-------------|
| `make help` | Show all available commands |
| `make setup` | Initial project setup |
| `make start` | Start all services |
| `make stop` | Stop all services |
| `make test` | Run all tests |
| `make lint` | Run code linting |
| `make format` | Format all code |
| `make clean` | Clean build artifacts |

### Backend Development
```bash
# Run backend tests
make backend-test

# Access backend container shell
make backend-shell

# Run database migrations
make db-migrate

# Reset database
make db-reset
```

### Mobile Development
```bash
# Run Flutter tests
make flutter-test

# Build for production
make flutter-build-ios
make flutter-build-android
```

## 🧪 Testing

The project includes comprehensive testing:

- **Backend**: pytest with coverage reporting
- **Frontend**: Flutter test framework
- **Integration**: API + mobile app integration tests
- **E2E**: Full user journey testing

```bash
# Run all tests
make test

# Run with coverage
pytest --cov=app --cov-report=html
cd mobile && flutter test --coverage
```

## 📚 API Documentation

Once the backend is running, visit:
- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)

### Key Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/refresh` - Refresh access token

#### Games
- `GET /api/v1/games` - List user's games
- `POST /api/v1/games` - Create new game
- `GET /api/v1/games/{id}` - Get game details
- `PUT /api/v1/games/{id}` - Update game
- `DELETE /api/v1/games/{id}` - Delete game

#### AI Generation
- `POST /api/v1/ai/generate-game` - Generate game from prompt
- `GET /api/v1/ai/generation/{task_id}` - Check generation status

#### Marketplace
- `GET /api/v1/marketplace` - Browse marketplace
- `POST /api/v1/marketplace/{game_id}/purchase` - Purchase game

#### Multiplayer
- `POST /api/v1/multiplayer/sessions` - Create game session
- `POST /api/v1/multiplayer/sessions/{id}/join` - Join session
- `WebSocket /ws/multiplayer/{session_id}` - Real-time gameplay

## 🎯 Game Types Supported

The AI can generate various types of games:

### Puzzle Games
- Block-matching games (Tetris-style)
- Match-3 games (Candy Crush-style)
- Logic puzzles
- Word games

### Action Games  
- Platformers
- Shooters
- Endless runners
- Arcade classics

### Casual Games
- Simple tap games
- Idle games
- Casual puzzles
- Social games

### Strategy Games
- Turn-based strategy
- Real-time strategy
- Board games
- Card games

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Environment
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/aimini_db

# AI Services
OPENAI_API_KEY=sk-your-openai-key
HUGGING_FACE_API_KEY=hf-your-hf-key

# AWS (optional)
USE_S3_STORAGE=false
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
```

### Mobile App Configuration

The Flutter app automatically configures itself based on:
- `--dart-define=API_BASE_URL=http://your-api-url`
- `--dart-define=ENVIRONMENT=production`

## 🚢 Deployment

### Backend Deployment

#### Using Docker
```bash
# Build production image
docker build -t aimini-backend .

# Run with docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

#### Using AWS ECS
See the included Terraform configuration in `infrastructure/`

### Mobile App Deployment

#### iOS App Store
```bash
cd mobile
flutter build ios --release
# Follow iOS deployment guide
```

#### Google Play Store
```bash
cd mobile  
flutter build appbundle --release
# Upload to Google Play Console
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`make test`)
5. Run linting (`make lint`)
6. Commit changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Standards
- Follow PEP 8 for Python code
- Use Flutter/Dart conventions for mobile code
- Write tests for new features
- Update documentation for API changes

## 📊 Project Timeline

This project is designed for **10 hours/week development** over **6 months**:

- **Phase 1 (Weeks 1-4)**: Core architecture and authentication
- **Phase 2 (Weeks 5-8)**: Game management and AI integration  
- **Phase 3 (Weeks 9-12)**: Marketplace and game engine
- **Phase 4 (Weeks 13-16)**: Multiplayer features
- **Phase 5 (Weeks 17-20)**: Polish and testing
- **Phase 6 (Weeks 21-26)**: Deployment and launch

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `docs/` folder
- **Issues**: Open a GitHub issue
- **Questions**: Start a GitHub discussion

## 🙏 Acknowledgments

- OpenAI for AI capabilities
- Flutter team for the amazing framework
- FastAPI for the excellent Python web framework
- The open source community

---

**Built with ❤️ for game creators everywhere**