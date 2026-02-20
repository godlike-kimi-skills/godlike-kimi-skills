#!/usr/bin/env python3
"""
Flutter Skill - Test Suite
Comprehensive tests for Flutter skill functionality.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from main import (
    FlutterSkill, WidgetConfig, StateConfig, ThemeConfig, FeatureConfig,
    WidgetType, StateProvider
)


class TestWidgetGeneration(unittest.TestCase):
    """Test widget generation functionality."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skill = FlutterSkill(output_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_generate_stateless_widget(self):
        """Test StatelessWidget generation."""
        config = WidgetConfig(
            name="UserCard",
            widget_type=WidgetType.STATELESS,
            props=[{"name": "title", "type": "string", "required": True}]
        )
        
        files = self.skill.generate_widget(config)
        
        self.assertIn("user_card.dart", files)
        content = files["user_card.dart"]
        
        self.assertIn("class UserCard extends StatelessWidget", content)
        self.assertIn("final String title;", content)
        self.assertIn("required this.title", content)
    
    def test_generate_stateful_widget(self):
        """Test StatefulWidget generation."""
        config = WidgetConfig(
            name="CounterButton",
            widget_type=WidgetType.STATEFUL,
            props=[{"name": "initialValue", "type": "int", "required": True}]
        )
        
        files = self.skill.generate_widget(config)
        content = files["user_card.dart"]
        
        self.assertIn("class CounterButton extends StatefulWidget", content)
        self.assertIn("State<CounterButton>", content)
        self.assertIn("initState", content)
        self.assertIn("dispose", content)
    
    def test_generate_consumer_widget(self):
        """Test Riverpod ConsumerWidget generation."""
        config = WidgetConfig(
            name="UserList",
            widget_type=WidgetType.CONSUMER,
            props=[]
        )
        
        files = self.skill.generate_widget(config)
        content = files["user_list.dart"]
        
        self.assertIn("extends ConsumerWidget", content)
        self.assertIn("WidgetRef ref", content)
        self.assertIn("flutter_riverpod", content)
    
    def test_widget_with_tests(self):
        """Test widget generation with tests."""
        config = WidgetConfig(
            name="TestWidget",
            widget_type=WidgetType.STATELESS,
            with_tests=True
        )
        
        files = self.skill.generate_widget(config)
        
        self.assertIn("test_widget.dart", files)
        self.assertIn("test_widget_test.dart", files)
        
        test_content = files["test_widget_test.dart"]
        self.assertIn("flutter_test", test_content)
        self.assertIn("testWidgets", test_content)
    
    def test_widget_without_tests(self):
        """Test widget generation without tests."""
        config = WidgetConfig(
            name="NoTestWidget",
            widget_type=WidgetType.STATELESS,
            with_tests=False
        )
        
        files = self.skill.generate_widget(config)
        
        self.assertIn("no_test_widget.dart", files)
        self.assertNotIn("no_test_widget_test.dart", files)


class TestStateManagement(unittest.TestCase):
    """Test state management setup functionality."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skill = FlutterSkill(output_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_setup_riverpod(self):
        """Test Riverpod setup."""
        config = StateConfig(
            provider=StateProvider.RIVERPOD,
            features=["auth", "profile"],
            include_freezed=True
        )
        
        files = self.skill.setup_state_management(config)
        
        self.assertIn("providers/providers.dart", files)
        self.assertIn("providers/auth/auth_state.dart", files)
        self.assertIn("providers/auth/auth_notifier.dart", files)
        
        providers = files["providers/providers.dart"]
        self.assertIn("flutter_riverpod", providers)
        self.assertIn("authProvider", providers)
    
    def test_setup_bloc(self):
        """Test Bloc setup."""
        config = StateConfig(
            provider=StateProvider.BLOC,
            features=["counter"]
        )
        
        files = self.skill.setup_state_management(config)
        
        self.assertIn("bloc/counter/counter_bloc.dart", files)
        self.assertIn("bloc/counter/counter_event.dart", files)
        self.assertIn("bloc/counter/counter_state.dart", files)
        
        bloc = files["bloc/counter/counter_bloc.dart"]
        self.assertIn("flutter_bloc", bloc)
        self.assertIn("extends Bloc", bloc)
    
    def test_setup_provider(self):
        """Test Provider setup."""
        config = StateConfig(provider=StateProvider.PROVIDER)
        
        files = self.skill.setup_state_management(config)
        
        self.assertIn("providers/app_provider.dart", files)
        
        content = files["providers/app_provider.dart"]
        self.assertIn("extends ChangeNotifier", content)
        self.assertIn("notifyListeners", content)
    
    def test_setup_getx(self):
        """Test GetX setup."""
        config = StateConfig(
            provider=StateProvider.GETX,
            features=["home", "settings"]
        )
        
        files = self.skill.setup_state_management(config)
        
        self.assertIn("controllers/home_controller.dart", files)
        self.assertIn("controllers/settings_controller.dart", files)
        
        controller = files["controllers/home_controller.dart"]
        self.assertIn("extends GetxController", controller)
        self.assertIn("RxBool", controller)


class TestThemeSetup(unittest.TestCase):
    """Test theme configuration functionality."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skill = FlutterSkill(output_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_setup_theme(self):
        """Test theme setup."""
        config = ThemeConfig(
            primary_color="#FF5722",
            secondary_color="#2196F3",
            support_dark_mode=False
        )
        
        files = self.skill.setup_theme(config)
        
        self.assertIn("theme/app_colors.dart", files)
        self.assertIn("theme/app_theme.dart", files)
        
        colors = files["theme/app_colors.dart"]
        self.assertIn("Color(0xFFFF5722)", colors)
        self.assertIn("Color(0xFF2196F3)", colors)
    
    def test_dark_mode_support(self):
        """Test dark mode theme generation."""
        config = ThemeConfig(
            primary_color="#6200EE",
            support_dark_mode=True
        )
        
        files = self.skill.setup_theme(config)
        
        theme = files["theme/app_theme.dart"]
        self.assertIn("darkTheme", theme)
        self.assertIn("Brightness.dark", theme)
    
    def test_material3_support(self):
        """Test Material 3 theme generation."""
        config = ThemeConfig(
            primary_color="#6200EE",
            use_material3=True
        )
        
        files = self.skill.setup_theme(config)
        
        theme = files["theme/app_theme.dart"]
        self.assertIn("useMaterial3: true", theme)


class TestFeatureGeneration(unittest.TestCase):
    """Test feature module generation functionality."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skill = FlutterSkill(output_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_generate_full_feature(self):
        """Test full feature module generation."""
        config = FeatureConfig(
            name="shoppingCart",
            include_model=True,
            include_repository=True,
            include_bloc=True,
            include_ui=True,
            include_tests=True
        )
        
        files = self.skill.generate_feature(config)
        
        self.assertIn("features/shopping_cart/data/models/shopping_cart_model.dart", files)
        self.assertIn("features/shopping_cart/data/repositories/shopping_cart_repository.dart", files)
        self.assertIn("features/shopping_cart/presentation/screens/shopping_cart_screen.dart", files)
        self.assertIn("features/shopping_cart/test/shopping_cart_test.dart", files)
    
    def test_generate_minimal_feature(self):
        """Test minimal feature module generation."""
        config = FeatureConfig(
            name="profile",
            include_model=False,
            include_repository=False,
            include_ui=True,
            include_tests=False
        )
        
        files = self.skill.generate_feature(config)
        
        self.assertNotIn("features/profile/data/models/profile_model.dart", files)
        self.assertNotIn("features/profile/data/repositories/profile_repository.dart", files)
        self.assertIn("features/profile/presentation/screens/profile_screen.dart", files)
    
    def test_feature_model_content(self):
        """Test feature model content."""
        config = FeatureConfig(
            name="Product",
            include_model=True
        )
        
        files = self.skill.generate_feature(config)
        model = files["features/product/data/models/product_model.dart"]
        
        self.assertIn("class ProductModel", model)
        self.assertIn("fromJson", model)
        self.assertIn("toJson", model)
    
    def test_feature_repository_content(self):
        """Test feature repository content."""
        config = FeatureConfig(
            name="Order",
            include_repository=True
        )
        
        files = self.skill.generate_feature(config)
        repo = files["features/order/data/repositories/order_repository.dart"]
        
        self.assertIn("abstract class OrderRepository", repo)
        self.assertIn("class OrderRepositoryImpl", repo)


class TestFileOperations(unittest.TestCase):
    """Test file saving operations."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skill = FlutterSkill(output_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_save_files(self):
        """Test saving files to disk."""
        files = {
            "lib/main.dart": "void main() {}",
            "lib/widgets/button.dart": "class Button {}"
        }
        
        paths = self.skill.save_files(files)
        
        self.assertEqual(len(paths), 2)
        
        for path in paths:
            self.assertTrue(path.exists())
    
    def test_save_with_custom_base_path(self):
        """Test saving files with custom base path."""
        custom_base = Path(self.temp_dir) / "my_project"
        files = {"test.dart": "class Test {}"}
        
        paths = self.skill.save_files(files, base_path=custom_base)
        
        self.assertTrue(paths[0].exists())
        self.assertIn("my_project", str(paths[0]))
    
    def test_nested_directory_creation(self):
        """Test creation of nested directories."""
        files = {"a/b/c/d/file.dart": "class MyClass {}"}
        
        paths = self.skill.save_files(files)
        
        self.assertTrue(paths[0].exists())
        self.assertTrue(paths[0].parent.exists())


class TestSkillInfo(unittest.TestCase):
    """Test skill information methods."""
    
    def setUp(self):
        self.skill = FlutterSkill()
    
    def test_get_info(self):
        """Test getting skill information."""
        info = self.skill.get_info()
        
        self.assertEqual(info["name"], "flutter-skill")
        self.assertEqual(info["category"], "mobile")
        self.assertIn("features", info)
    
    def test_version(self):
        """Test skill version."""
        self.assertIsNotNone(FlutterSkill.VERSION)
        self.assertIsInstance(FlutterSkill.VERSION, str)
    
    def test_dart_types(self):
        """Test Dart type mappings."""
        self.assertEqual(self.skill.DART_TYPES["string"], "String")
        self.assertEqual(self.skill.DART_TYPES["int"], "int")
        self.assertEqual(self.skill.DART_TYPES["bool"], "bool")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skill = FlutterSkill(output_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_empty_props(self):
        """Test widget with empty props."""
        config = WidgetConfig(
            name="EmptyWidget",
            widget_type=WidgetType.STATELESS,
            props=[]
        )
        
        files = self.skill.generate_widget(config)
        content = files["empty_widget.dart"]
        
        self.assertIn("class EmptyWidget extends StatelessWidget", content)
        self.assertIn("super.key", content)
    
    def test_multiple_features(self):
        """Test state management with multiple features."""
        config = StateConfig(
            provider=StateProvider.RIVERPOD,
            features=["auth", "user", "product", "cart", "order"]
        )
        
        files = self.skill.setup_state_management(config)
        
        for feature in config.features:
            self.assertIn(f"providers/{feature}/{feature}_state.dart", files)
            self.assertIn(f"providers/{feature}/{feature}_notifier.dart", files)
    
    def test_nullable_props(self):
        """Test widget with nullable props."""
        config = WidgetConfig(
            name="OptionalCard",
            widget_type=WidgetType.STATELESS,
            props=[{"name": "subtitle", "type": "string", "nullable": True}]
        )
        
        files = self.skill.generate_widget(config)
        content = files["optional_card.dart"]
        
        self.assertIn("final String? subtitle;", content)


def run_tests():
    """Run all tests with verbose output."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestWidgetGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestStateManagement))
    suite.addTests(loader.loadTestsFromTestCase(TestThemeSetup))
    suite.addTests(loader.loadTestsFromTestCase(TestFeatureGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestFileOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestSkillInfo))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
