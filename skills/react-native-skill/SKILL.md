# React Native Skill

A comprehensive skill for React Native mobile development, providing code generation, navigation setup, native module integration, and component scaffolding.

## Use When

- Creating new React Native projects or components
- Setting up navigation (React Navigation) for mobile apps
- Generating custom hooks and utility functions
- Configuring native modules and platform-specific code
- Building cross-platform UI components
- Integrating third-party libraries
- Debugging and troubleshooting React Native apps
- Setting up metro configuration and build scripts

## Out of Scope

- Backend API development (use backend-specific skills)
- Pure web frontend development (use React web skills)
- Native iOS/Android development without React Native bridge (use ios-skill/android-skill)
- Game development (use game development skills)
- Desktop application development (use Electron or native desktop skills)
- Complex animations beyond standard React Native capabilities

## Features

### Component Generation
- Functional components with hooks
- Class components (legacy support)
- Higher-Order Components (HOCs)
- Custom hooks for state management
- Reusable UI component library

### Navigation Setup
- Stack Navigator configuration
- Tab Navigator setup
- Drawer Navigator integration
- Nested navigation patterns
- Deep linking configuration
- Navigation type definitions

### Native Module Integration
- Native module boilerplate generation
- iOS native module setup (Objective-C/Swift)
- Android native module setup (Java/Kotlin)
- TurboModules configuration
- JSI (JavaScript Interface) integration
- Native event emitter patterns

### State Management
- Redux Toolkit setup
- Zustand integration
- Context API patterns
- Recoil/Jotai atomic state
- React Query for server state

### Styling & Theming
- StyleSheet generation
- Styled-components setup
- NativeWind (Tailwind) configuration
- Theme provider setup
- Dark mode support
- Responsive design utilities

### Build & Configuration
- Metro configuration
- Environment variable setup
- Fastlane configuration
- CodePush integration
- Hermes engine optimization
- Bundle size optimization

## Installation

```bash
# Clone the skill
cp -r react-native-skill ~/.kimi/skills/

# Install dependencies
cd ~/.kimi/skills/react-native-skill
pip install -r requirements.txt
```

## Usage

### Generate a Component
```bash
kimi skill react-native-skill generate component --name="UserProfile" --props="name,email,avatar"
```

### Setup Navigation
```bash
kimi skill react-native-skill setup navigation --type="stack" --screens="Home,Profile,Settings"
```

### Create Native Module
```bash
kimi skill react-native-skill generate native-module --name="BluetoothManager" --platforms="ios,android"
```

### Generate Custom Hook
```bash
kimi skill react-native-skill generate hook --name="useGeolocation" --dependencies="location-permission"
```

## API Reference

### Component Generation
- `generate:component` - Create React Native components
- `generate:screen` - Generate screen components with navigation
- `generate:hoc` - Create Higher-Order Components

### Navigation
- `setup:navigation` - Initialize React Navigation
- `generate:navigator` - Create navigator components
- `config:deeplinks` - Setup deep linking

### Native Modules
- `generate:native-module` - Create native module boilerplate
- `generate:spec` - Generate TurboModule specs
- `link:dependency` - Link native dependencies

### State & Data
- `setup:redux` - Configure Redux Toolkit
- `setup:react-query` - Setup React Query
- `generate:slice` - Create Redux slices

## Configuration

### skill.json
```json
{
  "name": "react-native-skill",
  "version": "1.0.0",
  "category": "mobile",
  "description": "React Native development skill",
  "author": "Kimi",
  "dependencies": ["node", "react-native-cli"]
}
```

## Examples

### Basic Component
```typescript
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

interface UserCardProps {
  name: string;
  email: string;
}

export const UserCard: React.FC<UserCardProps> = ({ name, email }) => (
  <View style={styles.container}>
    <Text style={styles.name}>{name}</Text>
    <Text style={styles.email}>{email}</Text>
  </View>
);

const styles = StyleSheet.create({
  container: { padding: 16, backgroundColor: '#fff' },
  name: { fontSize: 18, fontWeight: 'bold' },
  email: { fontSize: 14, color: '#666' }
});
```

### Navigation Setup
```typescript
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';

const Stack = createStackNavigator<RootStackParamList>();

export const AppNavigator = () => (
  <NavigationContainer>
    <Stack.Navigator>
      <Stack.Screen name="Home" component={HomeScreen} />
      <Stack.Screen name="Profile" component={ProfileScreen} />
    </Stack.Navigator>
  </NavigationContainer>
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

- [ ] Expo integration support
- [ ] New Architecture (Fabric/TurboModules) templates
- [ ] Performance profiling tools
- [ ] E2E testing templates (Detox/Appium)
- [ ] CI/CD pipeline templates
