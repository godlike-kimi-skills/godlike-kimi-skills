#!/usr/bin/env python3
"""
React Native Skill - Test Suite
Comprehensive tests for React Native skill functionality.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from main import ReactNativeSkill, ComponentConfig, NavigationConfig, NativeModuleConfig


class TestComponentGeneration(unittest.TestCase):
    """Test component generation functionality."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skill = ReactNativeSkill(output_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_generate_ts_component(self):
        """Test TypeScript component generation."""
        config = ComponentConfig(
            name="UserCard",
            props=["name", "email"],
            typescript=True
        )
        
        files = self.skill.generate_component(config)
        
        self.assertIn("UserCard.tsx", files)
        self.assertIn("UserCard.types.ts", files)
        self.assertIn("UserCard.styles.ts", files)
        self.assertIn("UserCard.test.tsx", files)
        
        # Check content
        content = files["UserCard.tsx"]
        self.assertIn("interface UserCardProps", content)
        self.assertIn("name: string;", content)
        self.assertIn("email: string;", content)
        self.assertIn("export const UserCard: React.FC<UserCardProps>", content)
    
    def test_generate_js_component(self):
        """Test JavaScript component generation."""
        config = ComponentConfig(
            name="UserCard",
            props=["name"],
            typescript=False
        )
        
        files = self.skill.generate_component(config)
        
        self.assertIn("UserCard.jsx", files)
        self.assertNotIn("UserCard.types.ts", files)
        
        content = files["UserCard.jsx"]
        self.assertIn("export const UserCard =", content)
    
    def test_component_with_styled_components(self):
        """Test component with styled-components style."""
        config = ComponentConfig(
            name="StyledCard",
            props=["title"],
            style_type="StyledComponents"
        )
        
        files = self.skill.generate_component(config)
        content = files["StyledCard.tsx"]
        
        self.assertIn("import styled from 'styled-components/native'", content)
    
    def test_component_with_nativewind(self):
        """Test component with NativeWind style."""
        config = ComponentConfig(
            name="WindCard",
            props=["title"],
            style_type="NativeWind"
        )
        
        files = self.skill.generate_component(config)
        content = files["WindCard.tsx"]
        
        self.assertIn("nativewind", content.lower())
    
    def test_component_without_tests(self):
        """Test component generation without tests."""
        config = ComponentConfig(
            name="NoTestCard",
            props=[],
            with_tests=False
        )
        
        files = self.skill.generate_component(config)
        
        self.assertNotIn("NoTestCard.test.tsx", files)


class TestNavigationSetup(unittest.TestCase):
    """Test navigation setup functionality."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skill = ReactNativeSkill(output_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_stack_navigator(self):
        """Test stack navigator generation."""
        config = NavigationConfig(
            nav_type="stack",
            screens=["Home", "Profile"],
            typescript=True
        )
        
        files = self.skill.setup_navigation(config)
        
        self.assertIn("navigation/AppNavigator.tsx", files)
        self.assertIn("navigation/types.ts", files)
        
        content = files["navigation/AppNavigator.tsx"]
        self.assertIn("createStackNavigator", content)
        self.assertIn("<Stack.Screen name=\"Home\"", content)
    
    def test_tab_navigator(self):
        """Test tab navigator generation."""
        config = NavigationConfig(
            nav_type="tab",
            screens=["Feed", "Settings"],
            typescript=True
        )
        
        files = self.skill.setup_navigation(config)
        content = files["navigation/AppNavigator.tsx"]
        
        self.assertIn("createBottomTabNavigator", content)
    
    def test_nav_types_generation(self):
        """Test navigation types file generation."""
        config = NavigationConfig(
            nav_type="stack",
            screens=["Home", "Profile", "Settings"],
            typescript=True
        )
        
        files = self.skill.setup_navigation(config)
        content = files["navigation/types.ts"]
        
        self.assertIn("export type RootStackParamList", content)
        self.assertIn("Home: undefined;", content)
        self.assertIn("Profile: undefined;", content)
    
    def test_auth_flow_navigator(self):
        """Test auth flow navigator generation."""
        config = NavigationConfig(
            nav_type="stack",
            screens=["Home"],
            typescript=True,
            auth_flow=True
        )
        
        files = self.skill.setup_navigation(config)
        
        self.assertIn("navigation/AuthNavigator.tsx", files)


class TestNativeModuleGeneration(unittest.TestCase):
    """Test native module generation functionality."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skill = ReactNativeSkill(output_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_ios_native_module(self):
        """Test iOS native module generation."""
        config = NativeModuleConfig(
            name="BluetoothManager",
            platforms=["ios"],
            methods=[{"name": "scan", "return": "void"}],
            turbo_module=True
        )
        
        files = self.skill.generate_native_module(config)
        
        self.assertIn("ios/BluetoothManager.h", files)
        self.assertIn("ios/BluetoothManager.mm", files)
        
        header = files["ios/BluetoothManager.h"]
        self.assertIn("@interface BluetoothManager", header)
        
        impl = files["ios/BluetoothManager.mm"]
        self.assertIn("RCT_EXPORT_METHOD(scan:", impl)
    
    def test_android_native_module(self):
        """Test Android native module generation."""
        config = NativeModuleConfig(
            name="BluetoothManager",
            platforms=["android"],
            methods=[{"name": "scan", "return": "void"}],
            turbo_module=False
        )
        
        files = self.skill.generate_native_module(config)
        
        self.assertIn("android/BluetoothManagerModule.kt", files)
        self.assertIn("android/BluetoothManagerPackage.kt", files)
        
        module = files["android/BluetoothManagerModule.kt"]
        self.assertIn("class BluetoothManagerModule", module)
        self.assertIn("@ReactMethod", module)
    
    def test_both_platforms(self):
        """Test generation for both platforms."""
        config = NativeModuleConfig(
            name="LocationManager",
            platforms=["ios", "android"],
            methods=[{"name": "getCurrentPosition", "return": "object"}],
            turbo_module=True
        )
        
        files = self.skill.generate_native_module(config)
        
        # iOS files
        self.assertIn("ios/LocationManager.h", files)
        self.assertIn("ios/LocationManager.mm", files)
        
        # Android files
        self.assertIn("android/LocationManagerModule.kt", files)
        self.assertIn("android/LocationManagerPackage.kt", files)
        
        # JS wrapper
        self.assertIn("src/NativeLocationManager.ts", files)
    
    def test_turbo_module_spec(self):
        """Test TurboModule spec generation."""
        config = NativeModuleConfig(
            name="SensorModule",
            platforms=["ios"],
            methods=[
                {"name": "start", "params": ["type"], "return": "void"},
                {"name": "stop", "return": "void"}
            ],
            turbo_module=True
        )
        
        files = self.skill.generate_native_module(config)
        
        self.assertIn("specs/NativeSensorModule.ts", files)
        
        spec = files["specs/NativeSensorModule.ts"]
        self.assertIn("interface Spec extends TurboModule", spec)
        self.assertIn("start(type:", spec)
        self.assertIn("stop():", spec)


class TestFileOperations(unittest.TestCase):
    """Test file saving operations."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skill = ReactNativeSkill(output_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_save_files(self):
        """Test saving files to disk."""
        files = {
            "components/Button.tsx": "export const Button = () => {}",
            "components/Input.tsx": "export const Input = () => {}"
        }
        
        paths = self.skill.save_files(files)
        
        self.assertEqual(len(paths), 2)
        
        for path in paths:
            self.assertTrue(path.exists())
            self.assertTrue(path.read_text())
    
    def test_save_with_base_path(self):
        """Test saving files with custom base path."""
        custom_base = Path(self.temp_dir) / "custom"
        files = {"test.txt": "content"}
        
        paths = self.skill.save_files(files, base_path=custom_base)
        
        self.assertTrue(paths[0].exists())
        self.assertIn("custom", str(paths[0]))
    
    def test_nested_directory_creation(self):
        """Test creation of nested directories."""
        files = {"a/b/c/d/file.txt": "content"}
        
        paths = self.skill.save_files(files)
        
        self.assertTrue(paths[0].exists())
        self.assertTrue(paths[0].parent.exists())


class TestSkillInfo(unittest.TestCase):
    """Test skill information methods."""
    
    def setUp(self):
        self.skill = ReactNativeSkill()
    
    def test_get_info(self):
        """Test getting skill information."""
        info = self.skill.get_info()
        
        self.assertEqual(info["name"], "react-native-skill")
        self.assertEqual(info["category"], "mobile")
        self.assertIn("features", info)
        self.assertIsInstance(info["features"], list)
    
    def test_version(self):
        """Test skill version."""
        self.assertIsNotNone(ReactNativeSkill.VERSION)
        self.assertIsInstance(ReactNativeSkill.VERSION, str)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skill = ReactNativeSkill(output_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_empty_props(self):
        """Test component with empty props."""
        config = ComponentConfig(name="EmptyComponent", props=[])
        
        files = self.skill.generate_component(config)
        content = files["EmptyComponent.tsx"]
        
        self.assertIn("interface EmptyComponentProps", content)
    
    def test_special_characters_in_name(self):
        """Test component names with valid characters."""
        config = ComponentConfig(name="UserCard_V2", props=["data"])
        
        files = self.skill.generate_component(config)
        self.assertIn("UserCard_V2.tsx", files)
    
    def test_many_screens(self):
        """Test navigation with many screens."""
        config = NavigationConfig(
            nav_type="stack",
            screens=[f"Screen{i}" for i in range(20)],
            typescript=True
        )
        
        files = self.skill.setup_navigation(config)
        content = files["navigation/types.ts"]
        
        for i in range(20):
            self.assertIn(f"Screen{i}: undefined;", content)


def run_tests():
    """Run all tests with verbose output."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestComponentGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestNavigationSetup))
    suite.addTests(loader.loadTestsFromTestCase(TestNativeModuleGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestFileOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestSkillInfo))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
