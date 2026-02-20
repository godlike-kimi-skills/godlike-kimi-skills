# Flutter Skill

A comprehensive skill for Flutter mobile development, providing widget generation, state management setup, theme configuration, and project scaffolding.

## Use When

- Creating new Flutter projects or applications
- Generating custom widgets and reusable components
- Setting up state management (Provider, Riverpod, Bloc, GetX)
- Configuring themes, dark mode, and design systems
- Building responsive layouts for multiple screen sizes
- Setting up navigation (GoRouter, Navigator 2.0)
- Creating platform-specific implementations (iOS/Android)
- Integrating with Firebase and backend services
- Setting up local storage (Hive, SharedPreferences, SQFlite)
- Configuring Flutter for web or desktop

## Out of Scope

- Backend API development (use backend-specific skills)
- Native iOS/Android development without Flutter (use ios-skill/android-skill)
- Complex game development (use Flame or Unity skills)
- Machine learning model training (use ML-specific skills)
- AR/VR development beyond basic Flutter capabilities
- Complex animations requiring custom renderers

## Features

### Widget Generation
- StatelessWidget templates
- StatefulWidget templates
- Custom painter widgets
- Animated widgets
- Sliver widgets for custom scroll effects
- Platform-adaptive widgets

### State Management
- **Provider** - InheritedWidget-based state management
- **Riverpod** - Compile-safe, testable state management
- **Bloc/Cubit** - Business Logic Component pattern
- **GetX** - Lightweight, high-performance state management
- **MobX** - Observable state management with reactions
- **Redux** - Predictable state container

### Navigation
- Navigator 1.0 (imperative)
- Navigator 2.0 (declarative)
- GoRouter - Declarative routing based on Navigator 2.0
- AutoRoute - Code generation for routing
- Deep linking configuration
- Navigation guards and middleware

### Theming & Design
- Material Design 3 (Material You)
- Cupertino (iOS-style) widgets
- Custom theme extensions
- Dark mode support
- Dynamic theming
- Color scheme generation from images

### Architecture Patterns
- Clean Architecture setup
- MVC/MVP/MVVM patterns
- Feature-first folder structure
- Layered architecture
- Repository pattern
- Dependency injection (GetIt, Injectable)

### Local Storage
- SharedPreferences
- Hive (NoSQL, high performance)
- SQFlite (SQLite for Flutter)
- ObjectBox
- Drift (typed SQL)

### Backend Integration
- Firebase setup (Auth, Firestore, Storage, FCM)
- REST API integration (Dio, http)
- GraphQL setup
- WebSocket connections
- Background fetch and processing

### Testing
- Unit testing setup
- Widget testing
- Integration testing
- Golden tests (screenshot testing)
- Mock generation

### Build & Deployment
- Flavor configuration (dev, staging, prod)
- App signing configuration
- CI/CD pipeline templates
- Fastlane setup
- Codemagic configuration

## Installation

```bash
# Clone the skill
cp -r flutter-skill ~/.kimi/skills/

# Install dependencies
cd ~/.kimi/skills/flutter-skill
pip install -r requirements.txt
```

## Usage

### Generate a Widget
```bash
kimi skill flutter-skill generate widget --name="UserCard" --type="stateless" --props="name,email,avatarUrl"
```

### Setup State Management
```bash
kimi skill flutter-skill setup state --provider="riverpod" --features="auth,profile,settings"
```

### Configure Navigation
```bash
kimi skill flutter-skill setup navigation --router="go_router" --routes="/,/profile,/settings"
```

### Setup Theme
```bash
kimi skill flutter-skill setup theme --primary-color="#6200EE" --support-dark-mode
```

### Create Feature Module
```bash
kimi skill flutter-skill generate feature --name="shopping_cart" --include="models,repository,bloc,ui"
```

## API Reference

### Widget Generation
- `generate:widget` - Create Flutter widgets
- `generate:screen` - Generate screen widgets
- `generate:dialog` - Create dialog widgets
- `generate:bottom-sheet` - Generate bottom sheet

### State Management
- `setup:riverpod` - Configure Riverpod
- `setup:bloc` - Setup Bloc pattern
- `setup:provider` - Configure Provider
- `setup:getx` - Setup GetX

### Navigation
- `setup:go_router` - Configure GoRouter
- `setup:auto_route` - Setup AutoRoute
- `generate:guard` - Create navigation guards

### Theming
- `setup:theme` - Initialize theme configuration
- `generate:color_scheme` - Create color scheme
- `setup:adaptive_theme` - Configure adaptive theming

### Features
- `generate:feature` - Create feature module
- `generate:model` - Generate data models
- `generate:repository` - Create repository classes

## Configuration

### skill.json
```json
{
  "name": "flutter-skill",
  "version": "1.0.0",
  "category": "mobile",
  "description": "Flutter mobile development skill",
  "author": "Kimi",
  "dependencies": ["flutter", "dart"]
}
```

## Examples

### Stateless Widget
```dart
import 'package:flutter/material.dart';

class UserCard extends StatelessWidget {
  final String name;
  final String email;
  final String? avatarUrl;

  const UserCard({
    super.key,
    required this.name,
    required this.email,
    this.avatarUrl,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: avatarUrl != null
            ? CircleAvatar(backgroundImage: NetworkImage(avatarUrl!))
            : const CircleAvatar(child: Icon(Icons.person)),
        title: Text(name),
        subtitle: Text(email),
      ),
    );
  }
}
```

### Riverpod State Management
```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Provider
final userProvider = FutureProvider<User>((ref) async {
  final repository = ref.watch(userRepositoryProvider);
  return repository.getCurrentUser();
});

// Consumer Widget
class UserProfile extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final userAsync = ref.watch(userProvider);
    
    return userAsync.when(
      data: (user) => Text(user.name),
      loading: () => CircularProgressIndicator(),
      error: (err, stack) => Text('Error: $err'),
    );
  }
}
```

### GoRouter Configuration
```dart
import 'package:go_router/go_router.dart';

final router = GoRouter(
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => HomeScreen(),
    ),
    GoRoute(
      path: '/profile/:id',
      builder: (context, state) => ProfileScreen(
        id: state.pathParameters['id']!,
      ),
    ),
  ],
);
```

### Custom Theme
```dart
import 'package:flutter/material.dart';

final lightTheme = ThemeData(
  useMaterial3: true,
  colorScheme: ColorScheme.fromSeed(
    seedColor: Colors.deepPurple,
    brightness: Brightness.light,
  ),
  cardTheme: CardTheme(
    elevation: 2,
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(12),
    ),
  ),
);
```

## Testing

Run the test suite:
```bash
python test_skill.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Roadmap

- [ ] Flutter Web support templates
- [ ] Flutter Desktop (Windows, macOS, Linux) templates
- [ ] Internationalization (i18n) setup
- [ ] Accessibility templates
- [ ] Performance optimization guides
- [ ] PlatformView integration templates
- [ ] FFI (Foreign Function Interface) setup
