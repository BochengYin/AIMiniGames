# AI Mini Games - Mobile App Architecture

## Overview
The AI Mini Games mobile app is built with Flutter using a clean architecture pattern with proper separation of concerns. The app uses Riverpod for state management, GoRouter for navigation, and Dio for network requests.

## Project Structure

```
mobile/
├── lib/
│   ├── app/
│   │   └── app.dart                 # Main app widget
│   ├── core/
│   │   ├── auth/                    # Authentication management
│   │   ├── config/                  # App configuration
│   │   ├── network/                 # API client and network utilities
│   │   ├── router/                  # Navigation router
│   │   ├── theme/                   # App theming
│   │   ├── error/                   # Error handling
│   │   └── storage/                 # Local storage
│   ├── features/                    # Feature modules
│   │   ├── auth/                    # Authentication feature
│   │   │   ├── data/               # Repositories
│   │   │   ├── domain/             # Models
│   │   │   └── presentation/       # UI (pages/widgets)
│   │   ├── games/                  # Games feature
│   │   ├── marketplace/            # Marketplace feature
│   │   ├── multiplayer/            # Multiplayer feature
│   │   └── profile/                # User profile feature
│   └── shared/                      # Shared components
│       └── presentation/
│           ├── pages/              # Shared pages
│           └── widgets/            # Reusable widgets
```

## Key Technologies

### State Management - Riverpod
- Provider-based state management
- Compile-safe dependency injection
- Built-in error handling and loading states

### Navigation - GoRouter
- Declarative routing
- Deep linking support
- Guards for authentication

### Network - Dio
- HTTP client with interceptors
- Automatic token refresh
- Request/response logging

### Local Storage
- Hive for structured data
- Flutter Secure Storage for sensitive data
- SharedPreferences for user preferences

### Game Engine - Flame
- 2D game rendering
- Sprite animations
- Physics and collision detection

## Core Features Implemented

### 1. Authentication System
- **Login Page**: Email/password authentication with JWT
- **Register Page**: User registration flow
- **Splash Page**: App initialization and auth check
- **Token Management**: Automatic refresh with secure storage

### 2. Navigation Structure
- **Main Navigation**: Bottom navigation with 4 main sections
- **Nested Routing**: Deep linking support for game details
- **Auth Guards**: Protected routes requiring authentication

### 3. Home & Game Discovery
- **Featured Games**: Carousel of top games
- **Category Filtering**: Browse by game category
- **Game Cards**: Grid display with ratings and play count
- **Search**: Game search functionality (coming soon)

### 4. API Integration
- **Base Client**: Configured Dio instance with interceptors
- **Auth Repository**: Login, register, profile management
- **Games Repository**: CRUD operations for games
- **Error Handling**: Consistent error messages

## Development Guidelines

### Code Organization
1. **Feature-First Structure**: Each feature is self-contained
2. **Clean Architecture**: Separation of data, domain, and presentation
3. **Dependency Injection**: Using Riverpod providers

### Naming Conventions
- **Files**: snake_case (e.g., `game_model.dart`)
- **Classes**: PascalCase (e.g., `GameModel`)
- **Variables**: camelCase (e.g., `gameTitle`)
- **Constants**: SCREAMING_SNAKE_CASE or camelCase for class constants

### State Management Pattern
```dart
// Provider definition
final gamesProvider = FutureProvider<List<GameModel>>((ref) async {
  final repository = ref.watch(gamesRepositoryProvider);
  return repository.getGames();
});

// Using in widget
final gamesAsync = ref.watch(gamesProvider);
gamesAsync.when(
  data: (games) => // Show games
  loading: () => // Show loader
  error: (error, stack) => // Show error
);
```

## API Endpoints

The mobile app connects to the backend API at `http://localhost:8000/api/v1/` (configurable).

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/refresh` - Token refresh
- `GET /users/profile` - Get user profile
- `PUT /users/profile` - Update profile

### Games
- `GET /games` - List games
- `GET /games/{id}` - Get game details
- `POST /games` - Create game
- `PUT /games/{id}` - Update game
- `DELETE /games/{id}` - Delete game
- `POST /games/{id}/rate` - Rate game

### AI Generation
- `POST /ai/generate` - Generate game with AI

## Build & Run

### Requirements
- Flutter SDK >= 3.16.0
- Dart SDK >= 3.9.0
- iOS: Xcode 14+, iOS 12.0+
- Android: Android Studio, minSdkVersion 21

### Running the App
```bash
# Get dependencies
flutter pub get

# Run code generation
flutter pub run build_runner build

# Run on iOS simulator
flutter run -d ios

# Run on Android emulator
flutter run -d android

# Run with specific environment
flutter run --dart-define=API_BASE_URL=https://api.example.com
```

### Building for Production
```bash
# iOS
flutter build ios --release

# Android
flutter build apk --release
flutter build appbundle --release
```

## Testing

### Unit Tests
```bash
flutter test
```

### Integration Tests
```bash
flutter test integration_test
```

## Next Steps

### High Priority
1. Complete registration flow
2. Implement game creation with AI
3. Add game play screen with Flame engine

### Medium Priority
1. User profile management
2. Marketplace browsing
3. Game rating system

### Low Priority
1. Multiplayer lobby
2. Social features
3. Achievements system

## Environment Variables

Configure these in your launch configuration or CI/CD:

```
API_BASE_URL=http://localhost:8000/api/v1
WEBSOCKET_URL=ws://localhost:8000/ws
ENVIRONMENT=development
```

## Security Considerations

1. **Token Storage**: Using Flutter Secure Storage for JWT tokens
2. **API Keys**: Never commit API keys, use environment variables
3. **Certificate Pinning**: Implement for production
4. **Obfuscation**: Enable for release builds

## Performance Optimizations

1. **Image Caching**: Using CachedNetworkImage
2. **Lazy Loading**: Pagination for game lists
3. **State Persistence**: Cache API responses
4. **Code Splitting**: Lazy load features

## Troubleshooting

### Common Issues

1. **Build Runner Issues**
```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

2. **iOS Pod Issues**
```bash
cd ios && pod install --repo-update
```

3. **Android Gradle Issues**
```bash
cd android && ./gradlew clean
```