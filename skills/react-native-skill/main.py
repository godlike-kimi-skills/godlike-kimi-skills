#!/usr/bin/env python3
"""
React Native Skill - Main Module
Provides comprehensive React Native development capabilities including component generation,
navigation setup, native module integration, and project scaffolding.
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ComponentConfig:
    """Configuration for component generation."""
    name: str
    props: List[str]
    typescript: bool = True
    style_type: str = "StyleSheet"  # StyleSheet, StyledComponents, NativeWind
    with_tests: bool = True
    navigation: Optional[str] = None


@dataclass
class NavigationConfig:
    """Configuration for navigation setup."""
    nav_type: str  # stack, tab, drawer, bottom-tabs
    screens: List[str]
    typescript: bool = True
    auth_flow: bool = False


@dataclass
class NativeModuleConfig:
    """Configuration for native module generation."""
    name: str
    platforms: List[str]  # ios, android
    methods: List[Dict[str, Any]]
    turbo_module: bool = True


class ReactNativeSkill:
    """Main skill class for React Native development."""
    
    VERSION = "1.0.0"
    SUPPORTED_NAV_TYPES = ["stack", "tab", "drawer", "bottom-tabs", "material-top-tabs"]
    STYLE_OPTIONS = ["StyleSheet", "StyledComponents", "NativeWind"]
    
    def __init__(self, output_dir: str = "./generated"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir = Path(__file__).parent / "prompts"
    
    def generate_component(self, config: ComponentConfig) -> Dict[str, str]:
        """
        Generate a React Native component with the specified configuration.
        
        Args:
            config: ComponentConfig object with generation parameters
            
        Returns:
            Dictionary with generated file paths and content
        """
        files = {}
        
        # Main component file
        if config.typescript:
            ext = ".tsx"
            files[f"{config.name}{ext}"] = self._generate_ts_component(config)
            files[f"{config.name}.types.ts"] = self._generate_types_file(config)
        else:
            ext = ".jsx"
            files[f"{config.name}{ext}"] = self._generate_js_component(config)
        
        # Styles file (if separate)
        if config.style_type == "StyleSheet":
            files[f"{config.name}.styles.ts"] = self._generate_styles_file(config)
        
        # Test file
        if config.with_tests:
            files[f"{config.name}.test.tsx"] = self._generate_test_file(config)
        
        # Index export
        files["index.ts"] = f"export {{ {config.name} }} from './{config.name}';\n"
        
        return files
    
    def _generate_ts_component(self, config: ComponentConfig) -> str:
        """Generate TypeScript component code."""
        props_interface = f"{config.name}Props"
        
        # Generate props interface
        props_def = f"interface {props_interface} {{\n"
        for prop in config.props:
            props_def += f"  {prop}: string;\n"
        props_def += "}\n\n"
        
        # Generate style imports
        if config.style_type == "StyledComponents":
            import_style = "import styled from 'styled-components/native';"
            style_usage = self._generate_styled_components(config)
        elif config.style_type == "NativeWind":
            import_style = "import { StyledComponent } from 'nativewind';"
            style_usage = self._generate_nativewind_styles(config)
        else:
            import_style = f"import {{ styles }} from './{config.name}.styles';"
            style_usage = "style={styles.container}"
        
        # Navigation wrapper
        nav_import = ""
        nav_type = ""
        if config.navigation:
            nav_import = f"import {{ useNavigation }} from '@react-navigation/native';\n"
            nav_type = f"import type {{ {config.navigation}NavigationProp }} from '../navigation/types';\n"
        
        component_code = f"""import React from 'react';
import {{ View, Text{', StyleSheet' if config.style_type == 'StyleSheet' else ''} }} from 'react-native';
{import_style}
{nav_import}
{nav_type}
{props_def}
export const {config.name}: React.FC<{props_interface}> = ({{ {', '.join(config.props)} }}) => {{
{'' if not config.navigation else '  const navigation = useNavigation<' + config.navigation + 'NavigationProp>();\\n'}
  return (
    <View {style_usage}>
      <Text>{config.name} Component</Text>
{''.join([f'      <Text>{{{prop}}}</Text>\\n' for prop in config.props])}    </View>
  );
}};
"""
        return component_code
    
    def _generate_js_component(self, config: ComponentConfig) -> str:
        """Generate JavaScript component code."""
        import_style = f"import {{ styles }} from './{config.name}.styles';"
        
        component_code = f"""import React from 'react';
import {{ View, Text }} from 'react-native';
{import_style}

export const {config.name} = ({{ {', '.join(config.props)} }}) => {{
  return (
    <View style={{styles.container}}>
      <Text>{config.name} Component</Text>
{''.join([f'      <Text>{{{prop}}}</Text>\\n' for prop in config.props])}    </View>
  );
}};
"""
        return component_code
    
    def _generate_types_file(self, config: ComponentConfig) -> str:
        """Generate TypeScript types file."""
        return f"""export interface {config.name}Props {{
{chr(10).join([f'  {prop}: string;' for prop in config.props])}
}}
"""
    
    def _generate_styles_file(self, config: ComponentConfig) -> str:
        """Generate StyleSheet file."""
        return f"""import {{ StyleSheet }} from 'react-native';

export const styles = StyleSheet.create({{
  container: {{
    flex: 1,
    padding: 16,
    backgroundColor: '#fff',
  }},
  text: {{
    fontSize: 16,
    color: '#333',
  }},
}});
"""
    
    def _generate_styled_components(self, config: ComponentConfig) -> str:
        """Generate styled components."""
        return """const Container = styled.View`
  flex: 1;
  padding: 16px;
  background-color: #fff;
`;

const Title = styled.Text`
  font-size: 18px;
  font-weight: bold;
`;"""
    
    def _generate_nativewind_styles(self, config: ComponentConfig) -> str:
        """Generate NativeWind class names."""
        return 'className="flex-1 p-4 bg-white"'
    
    def _generate_test_file(self, config: ComponentConfig) -> str:
        """Generate test file."""
        return f"""import React from 'react';
import {{ render }} from '@testing-library/react-native';
import {{ {config.name} }} from './{config.name}';

describe('{config.name}', () => {{
  it('renders correctly', () => {{
    const {{ getByText }} = render(
      <{config.name} {=' '.join([f'{prop}="test_{prop}"' for prop in config.props])} />
    );
    expect(getByText('{config.name} Component')).toBeTruthy();
  }});

{chr(10).join([f'  it("displays {prop} correctly", () => {{\\n    const {{ getByText }} = render(<{config.name} {prop}="test_value" />);\\n    expect(getByText("test_value")).toBeTruthy();\\n  }});' for prop in config.props[:2]])}
}});
"""
    
    def setup_navigation(self, config: NavigationConfig) -> Dict[str, str]:
        """
        Setup React Navigation configuration.
        
        Args:
            config: NavigationConfig object
            
        Returns:
            Dictionary with generated navigation files
        """
        files = {}
        
        # Type definitions
        if config.typescript:
            files["navigation/types.ts"] = self._generate_nav_types(config)
        
        # Main navigator
        files["navigation/AppNavigator.tsx"] = self._generate_navigator(config)
        
        # Navigation service (for navigation outside components)
        files["navigation/NavigationService.ts"] = self._generate_nav_service()
        
        # Auth navigator (if needed)
        if config.auth_flow:
            files["navigation/AuthNavigator.tsx"] = self._generate_auth_navigator(config)
        
        # Screen components
        for screen in config.screens:
            screen_config = ComponentConfig(
                name=screen,
                props=[],
                typescript=config.typescript,
                navigation=config.nav_type.capitalize()
            )
            screen_files = self.generate_component(screen_config)
            for filename, content in screen_files.items():
                files[f"screens/{screen}/{filename}"] = content
        
        return files
    
    def _generate_nav_types(self, config: NavigationConfig) -> str:
        """Generate navigation type definitions."""
        screen_params = "\n".join([f"  {screen}: undefined;" for screen in config.screens])
        
        return f"""import {{ NavigatorScreenParams }} from '@react-navigation/native';

export type RootStackParamList = {{
{screen_params}
}};

export type RootTabParamList = {{
{screen_params}
}};

declare global {{
  namespace ReactNavigation {{
    interface RootParamList extends RootStackParamList {{}}
  }}
}}
"""
    
    def _generate_navigator(self, config: NavigationConfig) -> str:
        """Generate navigator component."""
        nav_imports = {
            "stack": "import { createStackNavigator } from '@react-navigation/stack';",
            "tab": "import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';",
            "drawer": "import { createDrawerNavigator } from '@react-navigation/drawer';",
            "bottom-tabs": "import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';",
        }
        
        nav_creator = {
            "stack": "const Stack = createStackNavigator<RootStackParamList>();",
            "tab": "const Tab = createBottomTabNavigator<RootTabParamList>();",
            "drawer": "const Drawer = createDrawerNavigator<RootStackParamList>();",
            "bottom-tabs": "const Tab = createBottomTabNavigator<RootTabParamList>();",
        }
        
        import_stmt = nav_imports.get(config.nav_type, nav_imports["stack"])
        creator_stmt = nav_creator.get(config.nav_type, nav_creator["stack"])
        
        screen_render = "\n".join([
            f"      <Stack.Screen name=\"{screen}\" component={{{screen}}} />"
            for screen in config.screens
        ])
        
        return f"""import React from 'react';
import {{ NavigationContainer }} from '@react-navigation/native';
{import_stmt}
{chr(10).join([f"import {{ {screen} }} from '../screens/{screen}';" for screen in config.screens])}

{creator_stmt}

export const AppNavigator = () => {{
  return (
    <NavigationContainer>
      <Stack.Navigator>
{screen_render}
      </Stack.Navigator>
    </NavigationContainer>
  );
}};
"""
    
    def _generate_nav_service(self) -> str:
        """Generate navigation service."""
        return """import { NavigationContainerRef } from '@react-navigation/native';
import { RootStackParamList } from './types';

export const navigationRef = React.createRef<NavigationContainerRef<RootStackParamList>>();

export function navigate(name: keyof RootStackParamList, params?: object) {
  navigationRef.current?.navigate(name, params);
}

export function goBack() {
  navigationRef.current?.goBack();
}

export function reset(name: keyof RootStackParamList) {
  navigationRef.current?.reset({
    index: 0,
    routes: [{ name }],
  });
}
"""
    
    def _generate_auth_navigator(self, config: NavigationConfig) -> str:
        """Generate authentication navigator."""
        return """import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import { LoginScreen, RegisterScreen, ForgotPasswordScreen } from '../screens/auth';

const AuthStack = createStackNavigator();

export const AuthNavigator = () => (
  <AuthStack.Navigator screenOptions={{ headerShown: false }}>
    <AuthStack.Screen name="Login" component={LoginScreen} />
    <AuthStack.Screen name="Register" component={RegisterScreen} />
    <AuthStack.Screen name="ForgotPassword" component={ForgotPasswordScreen} />
  </AuthStack.Navigator>
);
"""
    
    def generate_native_module(self, config: NativeModuleConfig) -> Dict[str, str]:
        """
        Generate native module boilerplate for iOS and/or Android.
        
        Args:
            config: NativeModuleConfig object
            
        Returns:
            Dictionary with generated native module files
        """
        files = {}
        
        # TurboModule spec (TypeScript)
        if config.turbo_module:
            files[f"specs/Native{config.name}.ts"] = self._generate_turbo_spec(config)
        
        # iOS implementation
        if "ios" in config.platforms:
            files[f"ios/{config.name}.h"] = self._generate_ios_header(config)
            files[f"ios/{config.name}.mm"] = self._generate_ios_implementation(config)
            files[f"ios/{config.name}Package.swift"] = self._generate_ios_package(config)
        
        # Android implementation
        if "android" in config.platforms:
            files[f"android/{config.name}Module.kt"] = self._generate_android_module(config)
            files[f"android/{config.name}Package.kt"] = self._generate_android_package(config)
        
        # JavaScript/TypeScript wrapper
        files[f"src/Native{config.name}.ts"] = self._generate_js_wrapper(config)
        
        return files
    
    def _generate_turbo_spec(self, config: NativeModuleConfig) -> str:
        """Generate TurboModule specification."""
        methods = "\n".join([
            f"  {method['name']}({', '.join(method.get('params', []))}): Promise<{method.get('return', 'void')}>;"
            for method in config.methods
        ])
        
        return f"""import type {{ TurboModule }} from 'react-native/Libraries/TurboModule/RCTExport';
import {{ TurboModuleRegistry }} from 'react-native';

export interface Spec extends TurboModule {{
{methods}
}}

export default TurboModuleRegistry.get<Spec>('Native{config.name}') as Spec | null;
"""
    
    def _generate_ios_header(self, config: NativeModuleConfig) -> str:
        """Generate iOS header file."""
        return f"""#import <React/RCTBridgeModule.h>
#import <React/RCTEventEmitter.h>

@interface {config.name} : RCTEventEmitter <RCTBridgeModule>
@end
"""
    
    def _generate_ios_implementation(self, config: NativeModuleConfig) -> str:
        """Generate iOS implementation file."""
        methods = "\n".join([
            f"""RCT_EXPORT_METHOD({method['name']}:({method.get('ios_params', 'NSString')} *)param
                  resolver:(RCTPromiseResolveBlock)resolve
                  rejecter:(RCTPromiseRejectBlock)reject)
{{
  // TODO: Implement {method['name']}
  resolve(@{{ @"success": @YES }});
}}"""
            for method in config.methods
        ])
        
        return f"""#import "{config.name}.h"

@implementation {config.name}

RCT_EXPORT_MODULE()

+ (BOOL)requiresMainQueueSetup
{{
  return NO;
}}

{methods}

@end
"""
    
    def _generate_ios_package(self, config: NativeModuleConfig) -> str:
        """Generate iOS package file."""
        return f"""import Foundation

@objc({config.name}Package)
class {config.name}Package: NSObject {{}}
"""
    
    def _generate_android_module(self, config: NativeModuleConfig) -> str:
        """Generate Android Kotlin module."""
        methods = "\n\n".join([
            f"""  @ReactMethod
  fun {method['name']}(param: String, promise: Promise) {{
    // TODO: Implement {method['name']}
    promise.resolve(mapOf("success" to true))
  }}"""
            for method in config.methods
        ])
        
        return f"""package com.yourapp.modules

import com.facebook.react.bridge.*
import com.facebook.react.module.annotations.ReactModule

@ReactModule(name = {config.name}Module.NAME)
class {config.name}Module(reactContext: ReactApplicationContext) : 
  ReactContextBaseJavaModule(reactContext) {{

  companion object {{
    const val NAME = "Native{config.name}"
  }}

  override fun getName(): String = NAME

{methods}
}}
"""
    
    def _generate_android_package(self, config: NativeModuleConfig) -> str:
        """Generate Android package file."""
        return f"""package com.yourapp.modules

import com.facebook.react.ReactPackage
import com.facebook.react.bridge.NativeModule
import com.facebook.react.bridge.ReactApplicationContext
import com.facebook.react.uimanager.ViewManager

class {config.name}Package : ReactPackage {{
  override fun createNativeModules(reactContext: ReactApplicationContext): 
    List<NativeModule> = listOf({config.name}Module(reactContext))

  override fun createViewManagers(reactContext: ReactApplicationContext): 
    List<ViewManager<*, *>> = emptyList()
}}
"""
    
    def _generate_js_wrapper(self, config: NativeModuleConfig) -> str:
        """Generate JavaScript wrapper."""
        methods = "\n".join([
            f"export const {method['name']} = NativeModule.{method['name']};"
            for method in config.methods
        ])
        
        return f"""import {{ NativeModules }} from 'react-native';

const {{ Native{config.name} }} = NativeModules;

export default Native{config.name};

{methods}
"""
    
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
            "name": "react-native-skill",
            "version": self.VERSION,
            "category": "mobile",
            "description": "React Native mobile development skill",
            "features": [
                "Component generation",
                "Navigation setup",
                "Native module generation",
                "Custom hook creation",
                "TypeScript support",
                "Testing templates"
            ]
        }


def main():
    """Main entry point for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='React Native Skill')
    parser.add_argument('--version', action='version', version=f'%(prog)s {ReactNativeSkill.VERSION}')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate component
    gen_comp = subparsers.add_parser('generate:component', help='Generate a component')
    gen_comp.add_argument('--name', required=True, help='Component name')
    gen_comp.add_argument('--props', default='', help='Comma-separated prop names')
    gen_comp.add_argument('--no-ts', action='store_true', help='Generate JavaScript instead of TypeScript')
    gen_comp.add_argument('--style', default='StyleSheet', choices=ReactNativeSkill.STYLE_OPTIONS)
    
    # Setup navigation
    setup_nav = subparsers.add_parser('setup:navigation', help='Setup navigation')
    setup_nav.add_argument('--type', default='stack', choices=ReactNativeSkill.SUPPORTED_NAV_TYPES)
    setup_nav.add_argument('--screens', required=True, help='Comma-separated screen names')
    setup_nav.add_argument('--no-ts', action='store_true', help='Generate JavaScript instead of TypeScript')
    
    # Generate native module
    gen_native = subparsers.add_parser('generate:native-module', help='Generate native module')
    gen_native.add_argument('--name', required=True, help='Module name')
    gen_native.add_argument('--platforms', default='ios,android', help='Comma-separated platforms')
    gen_native.add_argument('--no-turbo', action='store_true', help='Disable TurboModule')
    
    # Info command
    subparsers.add_parser('info', help='Show skill information')
    
    args = parser.parse_args()
    skill = ReactNativeSkill()
    
    if args.command == 'generate:component':
        config = ComponentConfig(
            name=args.name,
            props=args.props.split(',') if args.props else [],
            typescript=not args.no_ts,
            style_type=args.style
        )
        files = skill.generate_component(config)
        paths = skill.save_files(files)
        print(f"Generated {len(paths)} files:")
        for p in paths:
            print(f"  - {p}")
    
    elif args.command == 'setup:navigation':
        config = NavigationConfig(
            nav_type=args.type,
            screens=args.screens.split(','),
            typescript=not args.no_ts
        )
        files = skill.setup_navigation(config)
        paths = skill.save_files(files)
        print(f"Generated {len(paths)} navigation files:")
        for p in paths:
            print(f"  - {p}")
    
    elif args.command == 'generate:native-module':
        config = NativeModuleConfig(
            name=args.name,
            platforms=args.platforms.split(','),
            methods=[{"name": "exampleMethod"}],
            turbo_module=not args.no_turbo
        )
        files = skill.generate_native_module(config)
        paths = skill.save_files(files)
        print(f"Generated {len(paths)} native module files:")
        for p in paths:
            print(f"  - {p}")
    
    elif args.command == 'info':
        info = skill.get_info()
        print(json.dumps(info, indent=2))
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
