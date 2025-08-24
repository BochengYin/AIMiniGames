# AI Mini Games - Complete Setup Instructions

## Prerequisites Installation

### 1. Flutter Installation
```bash
# macOS (using homebrew)
brew install flutter

# Or download from: https://docs.flutter.dev/get-started/install
# Add to PATH: export PATH="$PATH:`pwd`/flutter/bin"

# Verify installation
flutter doctor
```

### 2. Required Tools
```bash
# Install Android Studio for Android development
# Download from: https://developer.android.com/studio

# Install Xcode for iOS development (macOS only)
# Download from App Store

# Install VS Code with Flutter extension
# Download from: https://code.visualstudio.com/
```

## Project Setup Commands

### 1. Create Flutter Project
```bash
# Run this command in the AIMiniGames directory
flutter create --org com.aimini --project-name ai_mini_games mobile
cd mobile

# Add required dependencies
flutter pub add dio riverpod flutter_riverpod go_router hive flutter_secure_storage firebase_analytics sentry_flutter
flutter pub add --dev build_runner hive_generator json_serializable mockito

# Generate code
flutter packages pub run build_runner build
```

### 2. Backend Setup
```bash
# Already have requirements.txt, just need to install
pip install -r requirements.txt

# Create .env from template
cp .env.example .env
# Edit .env with your settings

# Start services
docker-compose up -d
```

### 3. Development Commands
```bash
# Start Flutter development
cd mobile
flutter run  # iOS simulator
flutter run -d android  # Android emulator

# Start backend
docker-compose up

# Run tests
cd mobile && flutter test
pytest  # Backend tests
```

## Next Steps After Setup
1. Follow the implementation guide for Phase 1 development
2. Set up your IDE with Flutter and Python extensions
3. Configure git hooks and pre-commit
4. Set up Firebase project for analytics and auth