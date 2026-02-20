#!/usr/bin/env python3
"""
Flutter Skill - Main Module
Provides comprehensive Flutter development capabilities including widget generation,
state management setup, theme configuration, and project scaffolding.
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum


class WidgetType(Enum):
    """Flutter widget types."""
    STATELESS = "stateless"
    STATEFUL = "stateful"
    CONSUMER = "consumer"
    HOOK = "hook"


class StateProvider(Enum):
    """State management providers."""
    RIVERPOD = "riverpod"
    BLOC = "bloc"
    PROVIDER = "provider"
    GETX = "getx"
    MOBX = "mobx"
    REDUX = "redux"


class RouterType(Enum):
    """Navigation router types."""
    GO_ROUTER = "go_router"
    AUTO_ROUTE = "auto_route"
    NAVIGATOR_2 = "navigator_2"


@dataclass
class WidgetConfig:
    """Configuration for widget generation."""
    name: str
    widget_type: WidgetType = WidgetType.STATELESS
    props: List[Dict[str, str]] = field(default_factory=list)
    with_animation: bool = False
    with_tests: bool = True
    is_screen: bool = False


@dataclass
class StateConfig:
    """Configuration for state management setup."""
    provider: StateProvider = StateProvider.RIVERPOD
    features: List[str] = field(default_factory=list)
    use_codegen: bool = True
    include_freezed: bool = True


@dataclass
class ThemeConfig:
    """Configuration for theme setup."""
    primary_color: str = "#6200EE"
    secondary_color: str = "#03DAC6"
    support_dark_mode: bool = True
    use_material3: bool = True
    font_family: Optional[str] = None


@dataclass
class FeatureConfig:
    """Configuration for feature module generation."""
    name: str
    include_model: bool = True
    include_repository: bool = True
    include_bloc: bool = False
    include_provider: bool = True
    include_ui: bool = True
    include_tests: bool = True


class FlutterSkill:
    """Main skill class for Flutter development."""
    
    VERSION = "1.0.0"
    
    DART_TYPES = {
        "string": "String",
        "int": "int",
        "double": "double",
        "bool": "bool",
        "list": "List",
        "map": "Map",
        "datetime": "DateTime",
    }
    
    def __init__(self, output_dir: str = "./generated"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_widget(self, config: WidgetConfig) -> Dict[str, str]:
        """
        Generate a Flutter widget with the specified configuration.
        
        Args:
            config: WidgetConfig object with generation parameters
            
        Returns:
            Dictionary with generated file paths and content
        """
        files = {}
        
        # Main widget file
        if config.widget_type == WidgetType.STATELESS:
            files[f"{config.name.snake_case()}.dart"] = self._generate_stateless_widget(config)
        elif config.widget_type == WidgetType.STATEFUL:
            files[f"{config.name.snake_case()}.dart"] = self._generate_stateful_widget(config)
        elif config.widget_type == WidgetType.CONSUMER:
            files[f"{config.name.snake_case()}.dart"] = self._generate_consumer_widget(config)
        
        # Test file
        if config.with_tests:
            files[f"{config.name.snake_case()}_test.dart"] = self._generate_widget_test(config)
        
        return files
    
    def _generate_stateless_widget(self, config: WidgetConfig) -> str:
        """Generate StatelessWidget code."""
        # Build constructor parameters
        params = []
        field_declarations = []
        key_param = "super.key"
        
        for prop in config.props:
            dart_type = self.DART_TYPES.get(prop.get("type", "string"), "String")
            name = prop.get("name", "")
            required = prop.get("required", True)
            nullable = prop.get("nullable", False)
            
            if nullable:
                dart_type = f"{dart_type}?"
            
            field_declarations.append(f"  final {dart_type} {name};")
            
            if required and not nullable:
                params.append(f"required this.{name}")
            else:
                params.append(f"this.{name}")
        
        # Add key to params
        all_params = [key_param] + params
        constructor_params = ",\n    ".join(all_params) if len(all_params) > 1 else ", ".join(all_params)
        
        fields_str = "\n".join(field_declarations) if field_declarations else ""
        
        widget_code = f"""import 'package:flutter/material.dart';

class {config.name} extends StatelessWidget {{
{fields_str}

  const {config.name}({{
    {constructor_params},
  }});

  @override
  Widget build(BuildContext context) {{
    return Container(
      child: Text('{config.name} Widget'),
    );
  }}
}}
"""
        return widget_code
    
    def _generate_stateful_widget(self, config: WidgetConfig) -> str:
        """Generate StatefulWidget code."""
        # Build constructor parameters
        params = []
        field_declarations = []
        
        for prop in config.props:
            dart_type = self.DART_TYPES.get(prop.get("type", "string"), "String")
            name = prop.get("name", "")
            required = prop.get("required", True)
            nullable = prop.get("nullable", False)
            
            if nullable:
                dart_type = f"{dart_type}?"
            
            field_declarations.append(f"  final {dart_type} {name};")
            
            if required and not nullable:
                params.append(f"required this.{name}")
            else:
                params.append(f"this.{name}")
        
        all_params = ["super.key"] + params
        constructor_params = ",\n    ".join(all_params)
        fields_str = "\n".join(field_declarations) if field_declarations else ""
        
        widget_code = f"""import 'package:flutter/material.dart';

class {config.name} extends StatefulWidget {{
{fields_str}

  const {config.name}({{
    {constructor_params},
  }});

  @override
  State<{config.name}> createState() => _{config.name}State();
}}

class _{config.name}State extends State<{config.name}> {{
  @override
  void initState() {{
    super.initState();
    // TODO: Initialize state
  }}

  @override
  void dispose() {{
    // TODO: Clean up resources
    super.dispose();
  }}

  @override
  Widget build(BuildContext context) {{
    return Container(
      child: Text('{config.name} Widget'),
    );
  }}
}}
"""
        return widget_code
    
    def _generate_consumer_widget(self, config: WidgetConfig) -> str:
        """Generate Riverpod ConsumerWidget code."""
        params = ["super.key"]
        
        for prop in config.props:
            params.append(f"this.{prop.get('name', '')}")
        
        constructor_params = ", ".join(params)
        
        widget_code = f"""import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class {config.name} extends ConsumerWidget {{
  const {config.name}({{ {constructor_params} }});

  @override
  Widget build(BuildContext context, WidgetRef ref) {{
    // TODO: Watch providers here
    return Container(
      child: Text('{config.name} Widget'),
    );
  }}
}}
"""
        return widget_code
    
    def _generate_widget_test(self, config: WidgetConfig) -> str:
        """Generate widget test code."""
        snake_name = config.name.snake_case()
        
        test_code = f"""import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:your_app/widgets/{snake_name}.dart';

void main() {{
  group('{config.name} Tests', () {{
    testWidgets('renders correctly', (WidgetTester tester) async {{
      await tester.pumpWidget(
        const MaterialApp(
          home: {config.name}(),
        ),
      );

      expect(find.text('{config.name} Widget'), findsOneWidget);
    }});

    // Add more tests here
  }});
}}
"""
        return test_code
    
    def setup_state_management(self, config: StateConfig) -> Dict[str, str]:
        """
        Setup state management configuration.
        
        Args:
            config: StateConfig object
            
        Returns:
            Dictionary with generated state management files
        """
        files = {}
        
        if config.provider == StateProvider.RIVERPOD:
            files.update(self._setup_riverpod(config))
        elif config.provider == StateProvider.BLOC:
            files.update(self._setup_bloc(config))
        elif config.provider == StateProvider.PROVIDER:
            files.update(self._setup_provider(config))
        elif config.provider == StateProvider.GETX:
            files.update(self._setup_getx(config))
        
        return files
    
    def _setup_riverpod(self, config: StateConfig) -> Dict[str, str]:
        """Setup Riverpod state management."""
        files = {}
        
        # Main providers file
        providers = []
        for feature in config.features:
            provider_name = f"{feature}Provider"
            providers.append(f"""
final {provider_name} = StateNotifierProvider<{feature.capitalize()}Notifier, {feature.capitalize()}State>((ref) {{
  return {feature.capitalize()}Notifier();
}});
""")
        
        files["providers/providers.dart"] = f"""import 'package:flutter_riverpod/flutter_riverpod.dart';

{chr(10).join(providers)}
"""
        
        # Generate state classes and notifiers for each feature
        for feature in config.features:
            feature_cap = feature.capitalize()
            
            # State class
            if config.include_freezed:
                files[f"providers/{feature}/{feature}_state.dart"] = f"""import 'package:freezed_annotation/freezed_annotation.dart';

part '{feature}_state.freezed.dart';

@freezed
class {feature_cap}State with _${feature_cap}State {{
  const factory {feature_cap}State({{
    @Default({feature_cap}Status.initial) {feature_cap}Status status,
    String? error,
    dynamic data,
  }}) = _{feature_cap}State;
}}

enum {feature_cap}Status {{ initial, loading, success, error }}
"""
            else:
                files[f"providers/{feature}/{feature}_state.dart"] = f"""class {feature_cap}State {{
  final {feature_cap}Status status;
  final String? error;
  final dynamic data;

  const {feature_cap}State({{
    this.status = {feature_cap}Status.initial,
    this.error,
    this.data,
  }});

  {feature_cap}State copyWith({{
    {feature_cap}Status? status,
    String? error,
    dynamic data,
  }}) {{
    return {feature_cap}State(
      status: status ?? this.status,
      error: error ?? this.error,
      data: data ?? this.data,
    );
  }}
}}

enum {feature_cap}Status {{ initial, loading, success, error }}
"""
            
            # Notifier class
            files[f"providers/{feature}/{feature}_notifier.dart"] = f"""import 'package:flutter_riverpod/flutter_riverpod.dart';
import '{feature}_state.dart';

class {feature_cap}Notifier extends StateNotifier<{feature_cap}State> {{
  {feature_cap}Notifier() : super(const {feature_cap}State());

  Future<void> load() async {{
    state = state.copyWith(status: {feature_cap}Status.loading);
    
    try {{
      // TODO: Implement data loading
      state = state.copyWith(
        status: {feature_cap}Status.success,
        data: null,
      );
    }} catch (e) {{
      state = state.copyWith(
        status: {feature_cap}Status.error,
        error: e.toString(),
      );
    }}
  }}
}}
"""
        
        return files
    
    def _setup_bloc(self, config: StateConfig) -> Dict[str, str]:
        """Setup Bloc state management."""
        files = {}
        
        for feature in config.features:
            feature_cap = feature.capitalize()
            
            # Events
            files[f"bloc/{feature}/{feature}_event.dart"] = f"""part of '{feature}_bloc.dart';

abstract class {feature_cap}Event {{}}

class {feature_cap}LoadStarted extends {feature_cap}Event {{}}

class {feature_cap}DataLoaded extends {feature_cap}Event {{}}
"""
            
            # States
            files[f"bloc/{feature}/{feature}_state.dart"] = f"""part of '{feature}_bloc.dart';

abstract class {feature_cap}State {{}}

class {feature_cap}Initial extends {feature_cap}State {{}}

class {feature_cap}Loading extends {feature_cap}State {{}}

class {feature_cap}Success extends {feature_cap}State {{}}

class {feature_cap}Error extends {feature_cap}State {{
  final String message;
  {feature_cap}Error(this.message);
}}
"""
            
            # Bloc
            files[f"bloc/{feature}/{feature}_bloc.dart"] = f"""import 'package:flutter_bloc/flutter_bloc.dart';

part '{feature}_event.dart';
part '{feature}_state.dart';

class {feature_cap}Bloc extends Bloc<{feature_cap}Event, {feature_cap}State> {{
  {feature_cap}Bloc() : super({feature_cap}Initial()) {{
    on<{feature_cap}LoadStarted>(_onLoadStarted);
  }}

  Future<void> _onLoadStarted(
    {feature_cap}LoadStarted event,
    Emitter<{feature_cap}State> emit,
  ) async {{
    emit({feature_cap}Loading());
    
    try {{
      // TODO: Implement logic
      emit({feature_cap}Success());
    }} catch (e) {{
      emit({feature_cap}Error(e.toString()));
    }}
  }}
}}
"""
        
        return files
    
    def _setup_provider(self, config: StateConfig) -> Dict[str, str]:
        """Setup Provider state management."""
        files = {}
        
        files["providers/app_provider.dart"] = """import 'package:flutter/material.dart';

class AppProvider extends ChangeNotifier {
  bool _isLoading = false;
  
  bool get isLoading => _isLoading;
  
  void setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }
}
"""
        
        return files
    
    def _setup_getx(self, config: StateConfig) -> Dict[str, str]:
        """Setup GetX state management."""
        files = {}
        
        for feature in config.features:
            feature_cap = feature.capitalize()
            files[f"controllers/{feature}_controller.dart"] = f"""import 'package:get/get.dart';

class {feature_cap}Controller extends GetxController {{
  final RxBool isLoading = false.obs;
  final RxString error = ''.obs;

  @override
  void onInit() {{
    super.onInit();
    // Initialize
  }}

  Future<void> load() async {{
    isLoading.value = true;
    try {{
      // TODO: Implement
    }} catch (e) {{
      error.value = e.toString();
    }} finally {{
      isLoading.value = false;
    }}
  }}
}}
"""
        
        return files
    
    def setup_theme(self, config: ThemeConfig) -> Dict[str, str]:
        """
        Setup theme configuration.
        
        Args:
            config: ThemeConfig object
            
        Returns:
            Dictionary with generated theme files
        """
        files = {}
        
        # Color scheme
        files["theme/app_colors.dart"] = f"""import 'package:flutter/material.dart';

class AppColors {{
  // Primary
  static const Color primary = Color({config.primary_color.replace('#', '0xFF')});
  static const Color secondary = Color({config.secondary_color.replace('#', '0xFF')});
  
  // Semantic
  static const Color success = Color(0xFF4CAF50);
  static const Color warning = Color(0xFFFF9800);
  static const Color error = Color(0xFFF44336);
  static const Color info = Color(0xFF2196F3);
  
  // Neutral
  static const Color background = Color(0xFFFFFFFF);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color onPrimary = Color(0xFFFFFFFF);
  static const Color onSecondary = Color(0xFF000000);
}}
"""
        
        # Light theme
        files["theme/app_theme.dart"] = f"""import 'package:flutter/material.dart';
import 'app_colors.dart';

class AppTheme {{
  static ThemeData get lightTheme {{
    return ThemeData(
      useMaterial3: {str(config.use_material3).lower()},
      colorScheme: ColorScheme.fromSeed(
        seedColor: AppColors.primary,
        brightness: Brightness.light,
      ),
      scaffoldBackgroundColor: AppColors.background,
      {'fontFamily: ' + repr(config.font_family) + ',' if config.font_family else ''}
      appBarTheme: const AppBarTheme(
        centerTitle: true,
        elevation: 0,
      ),
      cardTheme: CardTheme(
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
    );
  }}

  {self._generate_dark_theme(config) if config.support_dark_mode else ''}
}}
"""
        
        return files
    
    def _generate_dark_theme(self, config: ThemeConfig) -> str:
        """Generate dark theme code."""
        return f"""
  static ThemeData get darkTheme {{
    return ThemeData(
      useMaterial3: {str(config.use_material3).lower()},
      colorScheme: ColorScheme.fromSeed(
        seedColor: AppColors.primary,
        brightness: Brightness.dark,
      ),
      scaffoldBackgroundColor: const Color(0xFF121212),
      {'fontFamily: ' + repr(config.font_family) + ',' if config.font_family else ''}
      appBarTheme: const AppBarTheme(
        centerTitle: true,
        elevation: 0,
      ),
    );
  }}
"""
    
    def generate_feature(self, config: FeatureConfig) -> Dict[str, str]:
        """
        Generate a complete feature module.
        
        Args:
            config: FeatureConfig object
            
        Returns:
            Dictionary with generated feature files
        """
        files = {}
        feature_snake = config.name.snake_case()
        feature_cap = config.name.capitalize()
        
        # Data models
        if config.include_model:
            files[f"features/{feature_snake}/data/models/{feature_snake}_model.dart"] = f"""class {feature_cap}Model {{
  final String id;
  final String name;

  {feature_cap}Model({{
    required this.id,
    required this.name,
  }});

  factory {feature_cap}Model.fromJson(Map<String, dynamic> json) {{
    return {feature_cap}Model(
      id: json['id'],
      name: json['name'],
    );
  }}

  Map<String, dynamic> toJson() {{
    return {{
      'id': id,
      'name': name,
    }};
  }}
}}
"""
        
        # Repository
        if config.include_repository:
            files[f"features/{feature_snake}/data/repositories/{feature_snake}_repository.dart"] = f"""import '../models/{feature_snake}_model.dart';

abstract class {feature_cap}Repository {{
  Future<List<{feature_cap}Model>> getAll();
  Future<{feature_cap}Model> getById(String id);
}}

class {feature_cap}RepositoryImpl implements {feature_cap}Repository {{
  @override
  Future<List<{feature_cap}Model>> getAll() async {{
    // TODO: Implement
    return [];
  }}

  @override
  Future<{feature_cap}Model> getById(String id) async {{
    // TODO: Implement
    throw UnimplementedError();
  }}
}}
"""
        
        # UI
        if config.include_ui:
            files[f"features/{feature_snake}/presentation/screens/{feature_snake}_screen.dart"] = f"""import 'package:flutter/material.dart';

class {feature_cap}Screen extends StatelessWidget {{
  const {feature_cap}Screen({{super.key}});

  @override
  Widget build(BuildContext context) {{
    return Scaffold(
      appBar: AppBar(
        title: const Text('{feature_cap}'),
      ),
      body: const Center(
        child: Text('{feature_cap} Screen'),
      ),
    );
  }}
}}
"""
        
        # Tests
        if config.include_tests:
            files[f"features/{feature_snake}/test/{feature_snake}_test.dart"] = f"""import 'package:flutter_test/flutter_test.dart';

void main() {{
  group('{feature_cap} Tests', () {{
    test('initial test', () {{
      expect(true, true);
    }});
  }});
}}
"""
        
        return files
    
    def save_files(self, files: Dict[str, str], base_path: Optional[Path] = None) -> List[Path]:
        """
        Save generated files to disk.
        
        Args:
            files: Dictionary of file paths and content
            base_path: Optional base path for files
            
        Returns:
            List of created file paths
        """
        base = base_path or self.output_dir
        created_files = []
        
        for filepath, content in files.items():
            full_path = base / filepath
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding='utf-8')
            created_files.append(full_path)
        
        return created_files
    
    def get_info(self) -> Dict[str, Any]:
        """Get skill information."""
        return {
            "name": "flutter-skill",
            "version": self.VERSION,
            "category": "mobile",
            "description": "Flutter mobile development skill",
            "features": [
                "Widget generation",
                "State management (Riverpod, Bloc, Provider, GetX)",
                "Theme configuration",
                "Feature module generation",
                "Testing templates"
            ]
        }


# Extension for string conversion
class StringExtension:
    """String extension methods."""
    
    @staticmethod
    def snake_case(value: str) -> str:
        """Convert to snake_case."""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', value)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


# Monkey patch for snake_case
setattr(str, 'snake_case', lambda self: StringExtension.snake_case(self))


def main():
    """Main entry point for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Flutter Skill')
    parser.add_argument('--version', action='version', version=f'%(prog)s {FlutterSkill.VERSION}')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate widget
    gen_widget = subparsers.add_parser('generate:widget', help='Generate a widget')
    gen_widget.add_argument('--name', required=True, help='Widget name')
    gen_widget.add_argument('--type', default='stateless', choices=['stateless', 'stateful', 'consumer'])
    gen_widget.add_argument('--props', default='', help='Comma-separated prop names')
    
    # Setup state management
    setup_state = subparsers.add_parser('setup:state', help='Setup state management')
    setup_state.add_argument('--provider', default='riverpod', choices=['riverpod', 'bloc', 'provider', 'getx'])
    setup_state.add_argument('--features', default='', help='Comma-separated feature names')
    
    # Setup theme
    setup_theme = subparsers.add_parser('setup:theme', help='Setup theme')
    setup_theme.add_argument('--primary-color', default='#6200EE', help='Primary color')
    setup_theme.add_argument('--no-dark-mode', action='store_true', help='Disable dark mode')
    
    # Generate feature
    gen_feature = subparsers.add_parser('generate:feature', help='Generate feature module')
    gen_feature.add_argument('--name', required=True, help='Feature name')
    gen_feature.add_argument('--no-bloc', action='store_true', help='Exclude BLoC')
    gen_feature.add_argument('--no-repository', action='store_true', help='Exclude repository')
    
    # Info command
    subparsers.add_parser('info', help='Show skill information')
    
    args = parser.parse_args()
    skill = FlutterSkill()
    
    if args.command == 'generate:widget':
        props = [{"name": p, "type": "string"} for p in args.props.split(',') if p]
        config = WidgetConfig(
            name=args.name,
            widget_type=WidgetType(args.type),
            props=props
        )
        files = skill.generate_widget(config)
        paths = skill.save_files(files)
        print(f"Generated {len(paths)} files:")
        for p in paths:
            print(f"  - {p}")
    
    elif args.command == 'setup:state':
        config = StateConfig(
            provider=StateProvider(args.provider),
            features=args.features.split(',') if args.features else []
        )
        files = skill.setup_state_management(config)
        paths = skill.save_files(files)
        print(f"Generated {len(paths)} state management files:")
        for p in paths:
            print(f"  - {p}")
    
    elif args.command == 'setup:theme':
        config = ThemeConfig(
            primary_color=args.primary_color,
            support_dark_mode=not args.no_dark_mode
        )
        files = skill.setup_theme(config)
        paths = skill.save_files(files)
        print(f"Generated {len(paths)} theme files:")
        for p in paths:
            print(f"  - {p}")
    
    elif args.command == 'generate:feature':
        config = FeatureConfig(
            name=args.name,
            include_bloc=not args.no_bloc,
            include_repository=not args.no_repository
        )
        files = skill.generate_feature(config)
        paths = skill.save_files(files)
        print(f"Generated {len(paths)} feature files:")
        for p in paths:
            print(f"  - {p}")
    
    elif args.command == 'info':
        info = skill.get_info()
        print(json.dumps(info, indent=2))
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
