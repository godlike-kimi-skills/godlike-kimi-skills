#!/usr/bin/env python3
"""
iOS Skill - Test Suite
Comprehensive tests for iOS skill functionality.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from main import (
    IOSSkill, ViewConfig, ViewModelConfig, ModelConfig, ProjectConfig,
    UIFramework
)


class TestViewGeneration(unittest.TestCase):
    """Test view generation functionality."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skill = IOSSkill(output_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_generate_swiftui_view(self):
        """Test SwiftUI view generation."""
        config = ViewConfig(
            name="ProfileView",
            framework=UIFramework.SWIFTUI,
            props=[{"name": "userName", "type": "string", "state": True}]
        )
        
        files = self.skill.generate_view(config)
        
        self.assertIn("ProfileView.swift", files)
        content = files["ProfileView.swift"]
        
        self.assertIn("struct ProfileView: View", content)
        self.assertIn("@State private var userName: String", content)
        self.assertIn("#Preview", content)
    
    def test_generate_uikit_view(self):
        """Test UIKit view controller generation."""
        config = ViewConfig(
            name="ProfileViewController",
            framework=UIFramework.UIKIT,
            props=[{"name": "userId", "type": "string"}]
        )
        
        files = self.skill.generate_view(config)
        content = files["ProfileViewController.swift"]
        
        self.assertIn("class ProfileViewController: UIViewController", content)
        self.assertIn("private let userId: String", content)
        self.assertIn("NSLayoutConstraint.activate", content)
    
    def test_view_with_binding(self):
        """Test view with binding property."""
        config = ViewConfig(
            name="InputField",
            framework=UIFramework.SWIFTUI,
            props=[{"name": "text", "type": "string", "binding": True}]
        )
        
        files = self.skill.generate_view(config)
        content = files["InputField.swift"]
        
        self.assertIn("@Binding var text: String", content)
    
    def test_view_with_viewmodel(self):
        """Test view with view model generation."""
        config = ViewConfig(
            name="SettingsView",
            framework=UIFramework.SWIFTUI,
            include_viewmodel=True
        )
        
        files = self.skill.generate_view(config)
        
        self.assertIn("SettingsView.swift", files)
        self.assertIn("SettingsViewModel.swift", files)
        
        vm_content = files["SettingsViewModel.swift"]
        self.assertIn("@MainActor", vm_content)
        self.assertIn("ObservableObject", vm_content)


class TestViewModelGeneration(unittest.TestCase):
    """Test view model generation functionality."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skill = IOSSkill(output_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_viewmodel_with_combine(self):
        """Test view model with Combine."""
        config = ViewModelConfig(
            name="UserViewModel",
            use_combine=True
        )
        
        content = self.skill._generate_viewmodel(config)
        
        self.assertIn("import Combine", content)
        self.assertIn("cancellables", content)
        self.assertIn("@Published var isLoading", content)
    
    def test_viewmodel_with_dependencies(self):
        """Test view model with dependencies."""
        config = ViewModelConfig(
            name="OrderViewModel",
            dependencies=["order", "payment"]
        )
        
        content = self.skill._generate_viewmodel(config)
        
        self.assertIn("OrderServiceProtocol", content)
        self.assertIn("PaymentServiceProtocol", content)


class TestModelGeneration(unittest.TestCase):
    """Test model generation functionality."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skill = IOSSkill(output_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_generate_codable_model(self):
        """Test Codable model generation."""
        config = ModelConfig(
            name="User",
            properties=[
                {"name": "id", "type": "uuid"},
                {"name": "name", "type": "string"},
                {"name": "age", "type": "int"}
            ],
            codable=True,
            identifiable=True
        )
        
        files = self.skill.generate_model(config)
        content = files["User.swift"]
        
        self.assertIn("struct User: Codable, Identifiable", content)
        self.assertIn("let id: UUID", content)
        self.assertIn("let name: String", content)
        self.assertIn("let age: Int", content)
    
    def test_generate_equatable_model(self):
        """Test Equatable model generation."""
        config = ModelConfig(
            name="Product",
            properties=[{"name": "sku", "type": "string"}],
            equatable=True
        )
        
        files = self.skill.generate_model(config)
        content = files["Product.swift"]
        
        self.assertIn("Equatable", content)
    
    def test_generate_model_with_optionals(self):
        """Test model with optional properties."""
        config = ModelConfig(
            name="Article",
            properties=[
                {"name": "title", "type": "string", "optional": False},
                {"name": "subtitle", "type": "string", "optional": True}
            ]
        )
        
        files = self.skill.generate_model(config)
        content = files["Article.swift"]
        
        self.assertIn("let title: String", content)
        self.assertIn("let subtitle: String?", content)


class TestProjectSetup(unittest.TestCase):
    """Test project setup functionality."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skill = IOSSkill(output_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_setup_swiftui_project(self):
        """Test SwiftUI project setup."""
        config = ProjectConfig(
            name="MyApp",
            bundle_id="com.example.myapp",
            use_swiftui=True
        )
        
        files = self.skill.setup_project(config)
        
        self.assertIn("MyApp/App/MyAppApp.swift", files)
        self.assertNotIn("MyApp/App/AppDelegate.swift", files)
        
        app_content = files["MyApp/App/MyAppApp.swift"]
        self.assertIn("@main", app_content)
        self.assertIn("struct MyAppApp: App", app_content)
    
    def test_setup_uikit_project(self):
        """Test UIKit project setup."""
        config = ProjectConfig(
            name="MyApp",
            bundle_id="com.example.myapp",
            use_swiftui=False
        )
        
        files = self.skill.setup_project(config)
        
        self.assertIn("MyApp/App/AppDelegate.swift", files)
        self.assertIn("MyApp/App/SceneDelegate.swift", files)
    
    def test_project_with_tests(self):
        """Test project with test targets."""
        config = ProjectConfig(
            name="MyApp",
            bundle_id="com.example.myapp",
            include_tests=True
        )
        
        files = self.skill.setup_project(config)
        
        self.assertIn("MyAppTests/MyAppTests.swift", files)
        self.assertIn("MyAppUITests/MyAppUITests.swift", files)
    
    def test_project_structure(self):
        """Test project directory structure."""
        config = ProjectConfig(
            name="MyApp",
            bundle_id="com.example.myapp"
        )
        
        files = self.skill.setup_project(config)
        
        self.assertIn("MyApp/Views/README.md", files)
        self.assertIn("MyApp/ViewModels/README.md", files)
        self.assertIn("MyApp/Models/README.md", files)
        self.assertIn("MyApp/Services/README.md", files)


class TestNetworkGeneration(unittest.TestCase):
    """Test networking layer generation functionality."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skill = IOSSkill(output_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_generate_network_layer(self):
        """Test basic networking layer generation."""
        files = self.skill.generate_networking_layer(
            base_url="https://api.example.com"
        )
        
        self.assertIn("Services/APIServiceProtocol.swift", files)
        self.assertIn("Services/Endpoint.swift", files)
        self.assertIn("Services/APIService.swift", files)
    
    def test_network_with_bearer_auth(self):
        """Test networking layer with bearer auth."""
        files = self.skill.generate_networking_layer(
            base_url="https://api.example.com",
            auth_type="bearer"
        )
        
        api_service = files["Services/APIService.swift"]
        self.assertIn("Authorization", api_service)
        self.assertIn("Bearer", api_service)
    
    def test_endpoint_protocol(self):
        """Test Endpoint protocol generation."""
        files = self.skill.generate_networking_layer(
            base_url="https://api.example.com"
        )
        
        endpoint = files["Services/Endpoint.swift"]
        self.assertIn("protocol Endpoint", endpoint)
        self.assertIn("HTTPMethod", endpoint)
        self.assertIn("https://api.example.com", endpoint)


class TestCoreDataGeneration(unittest.TestCase):
    """Test Core Data generation functionality."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skill = IOSSkill(output_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_generate_coredata_entities(self):
        """Test Core Data entity generation."""
        files = self.skill.generate_coredata_model(
            entities=["User", "Product", "Order"]
        )
        
        self.assertIn("CoreData/PersistenceController.swift", files)
        self.assertIn("CoreData/User+CoreDataClass.swift", files)
        self.assertIn("CoreData/Product+CoreDataClass.swift", files)
        self.assertIn("CoreData/Order+CoreDataClass.swift", files)
    
    def test_coredata_entity_content(self):
        """Test Core Data entity content."""
        files = self.skill.generate_coredata_model(entities=["Customer"])
        
        class_file = files["CoreData/Customer+CoreDataClass.swift"]
        self.assertIn("@objc(Customer)", class_file)
        self.assertIn("class Customer: NSManagedObject", class_file)
        
        properties_file = files["CoreData/Customer+CoreDataProperties.swift"]
        self.assertIn("NSFetchRequest<Customer>", properties_file)


class TestFileOperations(unittest.TestCase):
    """Test file saving operations."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skill = IOSSkill(output_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_save_files(self):
        """Test saving files to disk."""
        files = {
            "Views/HomeView.swift": "struct HomeView: View {}",
            "Models/User.swift": "struct User: Codable {}"
        }
        
        paths = self.skill.save_files(files)
        
        self.assertEqual(len(paths), 2)
        
        for path in paths:
            self.assertTrue(path.exists())
    
    def test_save_with_custom_base_path(self):
        """Test saving files with custom base path."""
        custom_base = Path(self.temp_dir) / "MyProject"
        files = {"Test.swift": "class Test {}"}
        
        paths = self.skill.save_files(files, base_path=custom_base)
        
        self.assertTrue(paths[0].exists())
        self.assertIn("MyProject", str(paths[0]))
    
    def test_nested_directory_creation(self):
        """Test creation of nested directories."""
        files = {"A/B/C/D/File.swift": "class File {}"}
        
        paths = self.skill.save_files(files)
        
        self.assertTrue(paths[0].exists())
        self.assertTrue(paths[0].parent.exists())


class TestSkillInfo(unittest.TestCase):
    """Test skill information methods."""
    
    def setUp(self):
        self.skill = IOSSkill()
    
    def test_get_info(self):
        """Test getting skill information."""
        info = self.skill.get_info()
        
        self.assertEqual(info["name"], "ios-skill")
        self.assertEqual(info["category"], "mobile")
        self.assertIn("features", info)
    
    def test_version(self):
        """Test skill version."""
        self.assertIsNotNone(IOSSkill.VERSION)
        self.assertIsInstance(IOSSkill.VERSION, str)
    
    def test_swift_types(self):
        """Test Swift type mappings."""
        self.assertEqual(self.skill.SWIFT_TYPES["string"], "String")
        self.assertEqual(self.skill.SWIFT_TYPES["int"], "Int")
        self.assertEqual(self.skill.SWIFT_TYPES["bool"], "Bool")
        self.assertEqual(self.skill.SWIFT_TYPES["date"], "Date")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skill = IOSSkill(output_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_empty_props(self):
        """Test view with empty props."""
        config = ViewConfig(
            name="EmptyView",
            framework=UIFramework.SWIFTUI,
            props=[]
        )
        
        files = self.skill.generate_view(config)
        content = files["EmptyView.swift"]
        
        self.assertIn("struct EmptyView: View", content)
    
    def test_multiple_entities(self):
        """Test Core Data with multiple entities."""
        entities = ["Entity" + str(i) for i in range(10)]
        files = self.skill.generate_coredata_model(entities=entities)
        
        for entity in entities:
            self.assertIn(f"CoreData/{entity}+CoreDataClass.swift", files)
    
    def test_special_characters_in_name(self):
        """Test names with special characters handling."""
        config = ViewConfig(
            name="MyViewController",
            framework=UIFramework.UIKIT
        )
        
        files = self.skill.generate_view(config)
        self.assertIn("MyViewController.swift", files)


def run_tests():
    """Run all tests with verbose output."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestViewGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestViewModelGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestModelGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestProjectSetup))
    suite.addTests(loader.loadTestsFromTestCase(TestNetworkGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestCoreDataGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestFileOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestSkillInfo))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
