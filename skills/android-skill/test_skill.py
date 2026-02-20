#!/usr/bin/env python3
"""
Android Skill - Test Suite
Comprehensive tests for Android skill functionality.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from main import (
    AndroidSkill, ActivityConfig, FragmentConfig, ViewModelConfig,
    GradleConfig, ManifestConfig, UIType
)


class TestActivityGeneration(unittest.TestCase):
    """Test Activity generation functionality."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skill = AndroidSkill(output_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_generate_compose_activity(self):
        """Test Jetpack Compose Activity generation."""
        config = ActivityConfig(
            name="MainActivity",
            ui_type=UIType.COMPOSE,
            package="com.example.app",
            include_viewmodel=True
        )
        
        files = self.skill.generate_activity(config)
        
        self.assertIn("MainActivity.kt", files)
        self.assertIn("MainActivityViewModel.kt", files)
        
        activity = files["MainActivity.kt"]
        self.assertIn("class MainActivity : ComponentActivity()", activity)
        self.assertIn("setContent", activity)
        self.assertIn("@AndroidEntryPoint", activity)
    
    def test_generate_xml_activity(self):
        """Test XML-based Activity generation."""
        config = ActivityConfig(
            name="SettingsActivity",
            ui_type=UIType.XML,
            package="com.example.app"
        )
        
        files = self.skill.generate_activity(config)
        
        self.assertIn("SettingsActivity.kt", files)
        self.assertIn("res/layout/activity_settings.xml", files)
        
        activity = files["SettingsActivity.kt"]
        self.assertIn("setContentView(R.layout.activity_settings)", activity)
    
    def test_activity_without_viewmodel(self):
        """Test Activity without ViewModel."""
        config = ActivityConfig(
            name="SimpleActivity",
            ui_type=UIType.COMPOSE,
            include_viewmodel=False
        )
        
        files = self.skill.generate_activity(config)
        
        self.assertIn("SimpleActivity.kt", files)
        self.assertNotIn("SimpleActivityViewModel.kt", files)


class TestFragmentGeneration(unittest.TestCase):
    """Test Fragment generation functionality."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skill = AndroidSkill(output_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_generate_compose_fragment(self):
        """Test Jetpack Compose Fragment generation."""
        config = FragmentConfig(
            name="ProfileFragment",
            ui_type=UIType.COMPOSE,
            package="com.example.app"
        )
        
        files = self.skill.generate_fragment(config)
        
        self.assertIn("ProfileFragment.kt", files)
        
        fragment = files["ProfileFragment.kt"]
        self.assertIn("class ProfileFragment : Fragment()", fragment)
        self.assertIn("ComposeView", fragment)
    
    def test_generate_xml_fragment(self):
        """Test XML-based Fragment generation."""
        config = FragmentConfig(
            name="ListFragment",
            ui_type=UIType.XML
        )
        
        files = self.skill.generate_fragment(config)
        
        self.assertIn("ListFragment.kt", files)
        self.assertIn("res/layout/fragment_list.xml", files)
        
        fragment = files["ListFragment.kt"]
        self.assertIn("inflate(R.layout.fragment_list", fragment)


class TestViewModelGeneration(unittest.TestCase):
    """Test ViewModel generation functionality."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skill = AndroidSkill(output_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_generate_viewmodel_with_stateflow(self):
        """Test ViewModel with StateFlow."""
        config = ViewModelConfig(
            name="HomeViewModel",
            package="com.example.app",
            use_stateflow=True
        )
        
        content = self.skill._generate_viewmodel(config)
        
        self.assertIn("data class HomeViewModelUiState", content)
        self.assertIn("MutableStateFlow", content)
        self.assertIn("StateFlow<HomeViewModelUiState>", content)
        self.assertIn("viewModelScope.launch", content)
    
    def test_viewmodel_with_dependencies(self):
        """Test ViewModel with dependencies."""
        config = ViewModelConfig(
            name="OrderViewModel",
            dependencies=["order", "product"]
        )
        
        content = self.skill._generate_viewmodel(config)
        
        self.assertIn("orderRepository: OrderRepository", content)
        self.assertIn("productRepository: ProductRepository", content)


class TestGradleSetup(unittest.TestCase):
    """Test Gradle configuration functionality."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skill = AndroidSkill(output_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_setup_gradle_with_compose(self):
        """Test Gradle setup with Compose."""
        config = GradleConfig(
            use_compose=True,
            use_hilt=True
        )
        
        files = self.skill.setup_gradle(config)
        
        self.assertIn("build.gradle.kts", files)
        self.assertIn("app/build.gradle.kts", files)
        self.assertIn("settings.gradle.kts", files)
        self.assertIn("gradle/libs.versions.toml", files)
        
        module_gradle = files["app/build.gradle.kts"]
        self.assertIn("compose = true", module_gradle)
        self.assertIn("daggerHiltAndroid", module_gradle)
    
    def test_setup_gradle_without_compose(self):
        """Test Gradle setup without Compose."""
        config = GradleConfig(
            use_compose=False,
            use_hilt=False
        )
        
        files = self.skill.setup_gradle(config)
        module_gradle = files["app/build.gradle.kts"]
        
        self.assertIn("compose = false", module_gradle)
    
    def test_gradle_sdk_versions(self):
        """Test Gradle SDK version configuration."""
        config = GradleConfig(
            min_sdk=26,
            target_sdk=33,
            compile_sdk=33
        )
        
        files = self.skill.setup_gradle(config)
        module_gradle = files["app/build.gradle.kts"]
        
        self.assertIn("minSdk = 26", module_gradle)
        self.assertIn("targetSdk = 33", module_gradle)


class TestManifestGeneration(unittest.TestCase):
    """Test AndroidManifest generation functionality."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skill = AndroidSkill(output_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_generate_manifest(self):
        """Test AndroidManifest generation."""
        config = ManifestConfig(
            package="com.example.myapp",
            application_name="MyApplication",
            activities=["MainActivity", "SettingsActivity"],
            permissions=["INTERNET", "CAMERA"]
        )
        
        files = self.skill.generate_manifest(config)
        
        self.assertIn("AndroidManifest.xml", files)
        
        manifest = files["AndroidManifest.xml"]
        self.assertIn('package="com.example.myapp"', manifest)
        self.assertIn('android:name=".MyApplication"', manifest)
        self.assertIn('<uses-permission android:name="android.permission.INTERNET" />', manifest)
        self.assertIn('<uses-permission android:name="android.permission.CAMERA" />', manifest)
        self.assertIn('android:name=".MainActivity"', manifest)
        self.assertIn('android:name=".SettingsActivity"', manifest)
    
    def test_manifest_without_permissions(self):
        """Test manifest without permissions."""
        config = ManifestConfig(
            package="com.example.app",
            activities=["MainActivity"]
        )
        
        files = self.skill.generate_manifest(config)
        manifest = files["AndroidManifest.xml"]
        
        self.assertIn('package="com.example.app"', manifest)
        self.assertIn('android:name=".MainActivity"', manifest)


class TestRoomSetup(unittest.TestCase):
    """Test Room database setup functionality."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skill = AndroidSkill(output_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_setup_room_entities(self):
        """Test Room entity generation."""
        entities = ["User", "Product", "Order"]
        files = self.skill.setup_room(entities, "com.example.app")
        
        self.assertIn("data/entity/UserEntity.kt", files)
        self.assertIn("data/entity/ProductEntity.kt", files)
        self.assertIn("data/entity/OrderEntity.kt", files)
        
        self.assertIn("data/dao/UserDao.kt", files)
        self.assertIn("data/dao/ProductDao.kt", files)
        self.assertIn("data/dao/OrderDao.kt", files)
        
        self.assertIn("data/database/AppDatabase.kt", files)
    
    def test_room_entity_content(self):
        """Test Room entity content."""
        files = self.skill.setup_room(["User"], "com.example.app")
        
        entity = files["data/entity/UserEntity.kt"]
        self.assertIn("@Entity(tableName = \"user\")", entity)
        self.assertIn("data class UserEntity", entity)
        self.assertIn("@PrimaryKey val id: String", entity)
    
    def test_room_dao_content(self):
        """Test Room DAO content."""
        files = self.skill.setup_room(["User"], "com.example.app")
        
        dao = files["data/dao/UserDao.kt"]
        self.assertIn("@Dao", dao)
        self.assertIn("interface UserDao", dao)
        self.assertIn("@Query(\"SELECT * FROM user\")", dao)
        self.assertIn("Flow<List<UserEntity>>", dao)


class TestFileOperations(unittest.TestCase):
    """Test file saving operations."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skill = AndroidSkill(output_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_save_files(self):
        """Test saving files to disk."""
        files = {
            "MainActivity.kt": "class MainActivity {}",
            "MainViewModel.kt": "class MainViewModel {}"
        }
        
        paths = self.skill.save_files(files)
        
        self.assertEqual(len(paths), 2)
        
        for path in paths:
            self.assertTrue(path.exists())
    
    def test_save_with_custom_base_path(self):
        """Test saving files with custom base path."""
        custom_base = Path(self.temp_dir) / "MyApp"
        files = {"Test.kt": "class Test {}"}
        
        paths = self.skill.save_files(files, base_path=custom_base)
        
        self.assertTrue(paths[0].exists())
        self.assertIn("MyApp", str(paths[0]))
    
    def test_nested_directory_creation(self):
        """Test creation of nested directories."""
        files = {"a/b/c/D/E/File.kt": "class File {}"}
        
        paths = self.skill.save_files(files)
        
        self.assertTrue(paths[0].exists())
        self.assertTrue(paths[0].parent.exists())


class TestSkillInfo(unittest.TestCase):
    """Test skill information methods."""
    
    def setUp(self):
        self.skill = AndroidSkill()
    
    def test_get_info(self):
        """Test getting skill information."""
        info = self.skill.get_info()
        
        self.assertEqual(info["name"], "android-skill")
        self.assertEqual(info["category"], "mobile")
        self.assertIn("features", info)
    
    def test_version(self):
        """Test skill version."""
        self.assertIsNotNone(AndroidSkill.VERSION)
        self.assertIsInstance(AndroidSkill.VERSION, str)
    
    def test_kotlin_types(self):
        """Test Kotlin type mappings."""
        self.assertEqual(self.skill.KOTLIN_TYPES["string"], "String")
        self.assertEqual(self.skill.KOTLIN_TYPES["int"], "Int")
        self.assertEqual(self.skill.KOTLIN_TYPES["bool"], "Boolean")
    
    def test_common_permissions(self):
        """Test common permissions list."""
        self.assertIn("INTERNET", self.skill.COMMON_PERMISSIONS)
        self.assertIn("CAMERA", self.skill.COMMON_PERMISSIONS)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skill = AndroidSkill(output_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_empty_activities(self):
        """Test manifest with empty activities list."""
        config = ManifestConfig(
            package="com.example.app",
            activities=[]
        )
        
        files = self.skill.generate_manifest(config)
        manifest = files["AndroidManifest.xml"]
        
        self.assertIn('package="com.example.app"', manifest)
    
    def test_many_entities(self):
        """Test Room with many entities."""
        entities = [f"Entity{i}" for i in range(20)]
        files = self.skill.setup_room(entities)
        
        for entity in entities:
            self.assertIn(f"data/entity/{entity}Entity.kt", files)
    
    def test_snake_case_conversion(self):
        """Test snake case conversion."""
        self.assertEqual(self.skill._to_snake_case("MainActivity"), "main_activity")
        self.assertEqual(self.skill._to_snake_case("UserProfileFragment"), "user_profile_fragment")
        self.assertEqual(self.skill._to_snake_case("APIKeyManager"), "a_p_i_key_manager")


def run_tests():
    """Run all tests with verbose output."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestActivityGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestFragmentGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestViewModelGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestGradleSetup))
    suite.addTests(loader.loadTestsFromTestCase(TestManifestGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestRoomSetup))
    suite.addTests(loader.loadTestsFromTestCase(TestFileOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestSkillInfo))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
