#!/usr/bin/env python3
"""
Android Skill - Main Module
Provides comprehensive Android development capabilities including Kotlin/Java code generation,
Gradle configuration, AndroidManifest management, and modern Android architecture patterns.
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class UIType(Enum):
    """UI implementation types."""
    COMPOSE = "compose"
    XML = "xml"


class ArchitecturePattern(Enum):
    """Architecture patterns."""
    MVVM = "mvvm"
    MVI = "mvi"
    MVP = "mvp"


@dataclass
class ActivityConfig:
    """Configuration for Activity generation."""
    name: str
    ui_type: UIType = UIType.COMPOSE
    package: str = "com.example.app"
    include_viewmodel: bool = True
    hilt_inject: bool = True
    layout_name: Optional[str] = None


@dataclass
class FragmentConfig:
    """Configuration for Fragment generation."""
    name: str
    ui_type: UIType = UIType.COMPOSE
    package: str = "com.example.app"
    include_viewmodel: bool = True


@dataclass
class ViewModelConfig:
    """Configuration for ViewModel generation."""
    name: str
    package: str = "com.example.app"
    use_stateflow: bool = True
    dependencies: List[str] = field(default_factory=list)


@dataclass
class GradleConfig:
    """Configuration for Gradle setup."""
    min_sdk: int = 24
    target_sdk: int = 34
    compile_sdk: int = 34
    kotlin_version: str = "1.9.20"
    compose_version: str = "1.5.10"
    agp_version: str = "8.2.0"
    use_compose: bool = True
    use_hilt: bool = True
    use_room: bool = False
    use_retrofit: bool = False


@dataclass
class ManifestConfig:
    """Configuration for AndroidManifest."""
    package: str = "com.example.app"
    application_name: str = "Application"
    activities: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    services: List[str] = field(default_factory=list)
    receivers: List[str] = field(default_factory=list)


class AndroidSkill:
    """Main skill class for Android development."""
    
    VERSION = "1.0.0"
    
    KOTLIN_TYPES = {
        "string": "String",
        "int": "Int",
        "long": "Long",
        "float": "Float",
        "double": "Double",
        "bool": "Boolean",
        "date": "Date",
        "list": "List",
        "map": "Map",
    }
    
    COMMON_PERMISSIONS = [
        "INTERNET",
        "ACCESS_NETWORK_STATE",
        "CAMERA",
        "READ_EXTERNAL_STORAGE",
        "WRITE_EXTERNAL_STORAGE",
        "ACCESS_FINE_LOCATION",
        "ACCESS_COARSE_LOCATION",
        "READ_CONTACTS",
        "RECORD_AUDIO",
    ]
    
    def __init__(self, output_dir: str = "./generated"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_activity(self, config: ActivityConfig) -> Dict[str, str]:
        """
        Generate an Activity with the specified configuration.
        
        Args:
            config: ActivityConfig object with generation parameters
            
        Returns:
            Dictionary with generated file paths and content
        """
        files = {}
        
        if config.ui_type == UIType.COMPOSE:
            files[f"{config.name}.kt"] = self._generate_compose_activity(config)
        else:
            files[f"{config.name}.kt"] = self._generate_xml_activity(config)
            layout_name = config.layout_name or f"activity_{self._to_snake_case(config.name)}"
            files[f"res/layout/{layout_name}.xml"] = self._generate_activity_layout(config.name)
        
        if config.include_viewmodel:
            vm_config = ViewModelConfig(
                name=f"{config.name}ViewModel",
                package=config.package
            )
            files[f"{config.name}ViewModel.kt"] = self._generate_viewmodel(vm_config)
        
        return files
    
    def _generate_compose_activity(self, config: ActivityConfig) -> str:
        """Generate Jetpack Compose Activity."""
        hilt_import = "import dagger.hilt.android.AndroidEntryPoint" if config.hilt_inject else ""
        hilt_annotation = "@AndroidEntryPoint" if config.hilt_inject else ""
        
        viewmodel_property = ""
        if config.include_viewmodel:
            viewmodel_property = f"""
    private val viewModel: {config.name}ViewModel by viewModels()"""
        
        activity_code = f"""package {config.package}

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import {config.package}.ui.theme.AppTheme
{hilt_import}
{hilt_annotation}
class {config.name} : ComponentActivity() {{{viewmodel_property}

    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        setContent {{
            AppTheme {{
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {{
                    {config.name}Screen()
                }}
            }}
        }}
    }}
}}

@Composable
fun {config.name}Screen() {{
    // TODO: Implement screen content
}}

@Preview(showBackground = true)
@Composable
fun {config.name}ScreenPreview() {{
    AppTheme {{
        {config.name}Screen()
    }}
}}
"""
        return activity_code
    
    def _generate_xml_activity(self, config: ActivityConfig) -> str:
        """Generate traditional XML-based Activity."""
        layout_name = config.layout_name or f"activity_{self._to_snake_case(config.name)}"
        
        viewmodel_property = ""
        viewmodel_init = ""
        if config.include_viewmodel:
            viewmodel_property = f"""
    private val viewModel: {config.name}ViewModel by viewModels()"""
            viewmodel_init = f"""
        viewModel.uiState.observe(this) {{ state ->
            updateUI(state)
        }}"""
        
        activity_code = f"""package {config.package}

import android.os.Bundle
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
{viewmodel_property}

class {config.name} : AppCompatActivity() {{

    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        setContentView(R.layout.{layout_name}){viewmodel_init}
    }}
{'' if not config.include_viewmodel else f'''
    private fun updateUI(state: {config.name}UiState) {{
        // TODO: Update UI based on state
    }}'''}
}}
"""
        return activity_code
    
    def _generate_activity_layout(self, activity_name: str) -> str:
        """Generate XML layout for Activity."""
        return f"""<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout 
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <TextView
        android:id="@+id/titleText"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="{activity_name}"
        android:textSize="24sp"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>
"""
    
    def _generate_viewmodel(self, config: ViewModelConfig) -> str:
        """Generate ViewModel class."""
        state_class = f"""data class {config.name}UiState(
    val isLoading: Boolean = false,
    val error: String? = null
)"""
        
        stateflow_declarations = ""
        stateflow_properties = ""
        
        if config.use_stateflow:
            stateflow_declarations = f"""
    private val _uiState = MutableStateFlow({config.name}UiState())
    val uiState: StateFlow<{config.name}UiState> = _uiState.asStateFlow()"""
            stateflow_properties = stateflow_declarations
        
        dependencies = "\n    ".join([
            f"private val {dep.lower()}Repository: {dep.capitalize()}Repository,"
            for dep in config.dependencies
        ]) if config.dependencies else ""
        
        viewmodel_code = f"""package {config.package}

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

{state_class}

class {config.name}(
{dependencies}
) : ViewModel() {{{stateflow_properties}

    fun load() {{
        viewModelScope.launch {{
            _uiState.value = _uiState.value.copy(isLoading = true)
            
            try {{
                // TODO: Implement loading logic
                _uiState.value = _uiState.value.copy(isLoading = false)
            }} catch (e: Exception) {{
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = e.message
                )
            }}
        }}
    }}
}}
"""
        return viewmodel_code
    
    def generate_fragment(self, config: FragmentConfig) -> Dict[str, str]:
        """
        Generate a Fragment with the specified configuration.
        
        Args:
            config: FragmentConfig object
            
        Returns:
            Dictionary with generated fragment files
        """
        files = {}
        
        if config.ui_type == UIType.COMPOSE:
            files[f"{config.name}.kt"] = self._generate_compose_fragment(config)
        else:
            files[f"{config.name}.kt"] = self._generate_xml_fragment(config)
            layout_name = f"fragment_{self._to_snake_case(config.name)}"
            files[f"res/layout/{layout_name}.xml"] = self._generate_fragment_layout(config.name)
        
        if config.include_viewmodel:
            vm_config = ViewModelConfig(
                name=f"{config.name}ViewModel",
                package=config.package
            )
            files[f"{config.name}ViewModel.kt"] = self._generate_viewmodel(vm_config)
        
        return files
    
    def _generate_compose_fragment(self, config: FragmentConfig) -> str:
        """Generate Jetpack Compose Fragment."""
        return f"""package {config.package}

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.compose.ui.platform.ComposeView
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import {config.package}.ui.theme.AppTheme

class {config.name} : Fragment() {{

    private val viewModel: {config.name}ViewModel by viewModels()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {{
        return ComposeView(requireContext()).apply {{
            setContent {{
                AppTheme {{
                    {config.name}Screen()
                }}
            }}
        }}
    }}
}}
"""
    
    def _generate_xml_fragment(self, config: FragmentConfig) -> str:
        """Generate traditional XML-based Fragment."""
        layout_name = f"fragment_{self._to_snake_case(config.name)}"
        
        return f"""package {config.package}

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels

class {config.name} : Fragment() {{

    private val viewModel: {config.name}ViewModel by viewModels()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {{
        return inflater.inflate(R.layout.{layout_name}, container, false)
    }}

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {{
        super.onViewCreated(view, savedInstanceState)
        // TODO: Setup views
    }}
}}
"""
    
    def _generate_fragment_layout(self, fragment_name: str) -> str:
        """Generate XML layout for Fragment."""
        return f"""<?xml version="1.0" encoding="utf-8"?>
<FrameLayout 
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="center"
        android:text="{fragment_name}"
        android:textSize="20sp" />

</FrameLayout>
"""
    
    def setup_gradle(self, config: GradleConfig) -> Dict[str, str]:
        """
        Setup Gradle configuration files.
        
        Args:
            config: GradleConfig object
            
        Returns:
            Dictionary with generated Gradle files
        """
        files = {}
        
        # Project-level build.gradle
        files["build.gradle.kts"] = self._generate_project_build_gradle(config)
        
        # Module-level build.gradle
        files["app/build.gradle.kts"] = self._generate_module_build_gradle(config)
        
        # Settings.gradle
        files["settings.gradle.kts"] = self._generate_settings_gradle()
        
        # Version catalog
        files["gradle/libs.versions.toml"] = self._generate_version_catalog(config)
        
        # gradle.properties
        files["gradle.properties"] = self._generate_gradle_properties()
        
        return files
    
    def _generate_project_build_gradle(self, config: GradleConfig) -> str:
        """Generate project-level build.gradle."""
        plugins = f"""plugins {{
    id("com.android.application") version "{config.agp_version}" apply false
    id("org.jetbrains.kotlin.android") version "{config.kotlin_version}" apply false
"""
        if config.use_hilt:
            plugins += f"""    id("com.google.dagger.hilt.android") version "2.48" apply false
"""
        plugins += "}"
        
        return f"""// Top-level build file
{plugins}
"""
    
    def _generate_module_build_gradle(self, config: GradleConfig) -> str:
        """Generate module-level build.gradle."""
        plugins = ["androidApplication", "kotlinAndroid"]
        if config.use_hilt:
            plugins.append("kotlinKapt")
            plugins.append("daggerHiltAndroid")
        if config.use_compose:
            plugins.append("kotlinCompose")
        
        plugins_str = "\n    ".join([f'alias(libs.plugins.{p})' for p in plugins])
        
        dependencies = []
        
        # Core
        dependencies.append('implementation(libs.androidx.core.ktx)')
        dependencies.append('implementation(libs.androidx.lifecycle.runtime.ktx)')
        dependencies.append('implementation(libs.androidx.activity.compose)')
        
        if config.use_compose:
            dependencies.append('implementation(platform(libs.androidx.compose.bom))')
            dependencies.append('implementation(libs.androidx.ui)')
            dependencies.append('implementation(libs.androidx.ui.graphics)')
            dependencies.append('implementation(libs.androidx.ui.tooling.preview)')
            dependencies.append('implementation(libs.androidx.material3)')
        
        if config.use_hilt:
            dependencies.append('implementation(libs.hilt.android)')
            dependencies.append('kapt(libs.hilt.compiler)')
        
        if config.use_room:
            dependencies.append('implementation(libs.room.runtime)')
            dependencies.append('implementation(libs.room.ktx)')
            dependencies.append('kapt(libs.room.compiler)')
        
        if config.use_retrofit:
            dependencies.append('implementation(libs.retrofit)')
            dependencies.append('implementation(libs.retrofit.gson)')
            dependencies.append('implementation(libs.okhttp.logging)')
        
        deps_str = "\n    ".join(dependencies)
        
        return f"""plugins {{
    {plugins_str}
}}

android {{
    namespace = "com.example.app"
    compileSdk = {config.compile_sdk}

    defaultConfig {{
        applicationId = "com.example.app"
        minSdk = {config.min_sdk}
        targetSdk = {config.target_sdk}
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }}

    buildTypes {{
        release {{
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }}
    }}

    compileOptions {{
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }}

    kotlinOptions {{
        jvmTarget = "17"
    }}

    buildFeatures {{
        compose = {str(config.use_compose).lower()}
    }}

    composeOptions {{
        kotlinCompilerExtensionVersion = "{config.compose_version}"
    }}

    packaging {{
        resources {{
            excludes += "/META-INF/{{AL2.0,LGPL2.1}}"
        }}
    }}
}}

dependencies {{
    {deps_str}

    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.junit)
    androidTestImplementation(libs.androidx.espresso.core)
}}
"""
    
    def _generate_settings_gradle(self) -> str:
        """Generate settings.gradle."""
        return """pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "MyApplication"
include(":app")
"""
    
    def _generate_version_catalog(self, config: GradleConfig) -> str:
        """Generate version catalog (libs.versions.toml)."""
        return f"""[versions]
agp = "{config.agp_version}"
kotlin = "{config.kotlin_version}"
coreKtx = "1.12.0"
lifecycleRuntimeKtx = "2.6.2"
activityCompose = "1.8.1"
composeBom = "2023.10.01"
junit = "4.13.2"
junitVersion = "1.1.5"
espressoCore = "3.5.1"
"""
    
    def _generate_gradle_properties(self) -> str:
        """Generate gradle.properties."""
        return """# Project-wide Gradle settings.
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
kotlin.code.style=official
android.nonTransitiveRClass=true
"""
    
    def generate_manifest(self, config: ManifestConfig) -> Dict[str, str]:
        """
        Generate AndroidManifest.xml.
        
        Args:
            config: ManifestConfig object
            
        Returns:
            Dictionary with generated manifest
        """
        permissions_xml = "\n    ".join([
            f'<uses-permission android:name="android.permission.{perm}" />'
            for perm in config.permissions
        ])
        
        activities_xml = "\n        ".join([
            f'''<activity
            android:name=".{activity}"
            android:exported="false" />'''
            for activity in config.activities
        ])
        
        manifest = f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    package="{config.package}">

    {permissions_xml}

    <application
        android:name=".{config.application_name}"
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.MyApplication"
        tools:targetApi="31">

        {activities_xml}

    </application>

</manifest>
"""
        
        return {"AndroidManifest.xml": manifest}
    
    def setup_room(self, entities: List[str], package: str = "com.example.app") -> Dict[str, str]:
        """
        Setup Room database configuration.
        
        Args:
            entities: List of entity names
            package: Package name
            
        Returns:
            Dictionary with generated Room files
        """
        files = {}
        
        # Generate entities
        for entity in entities:
            files[f"data/entity/{entity}Entity.kt"] = f"""package {package}.data.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "{entity.lower()}")
data class {entity}Entity(
    @PrimaryKey val id: String,
    val name: String,
    val createdAt: Long = System.currentTimeMillis()
)
"""
            
            # DAO
            files[f"data/dao/{entity}Dao.kt"] = f"""package {package}.data.dao

import androidx.room.*
import {package}.data.entity.{entity}Entity
import kotlinx.coroutines.flow.Flow

@Dao
interface {entity}Dao {{
    @Query("SELECT * FROM {entity.lower()}")
    fun getAll(): Flow<List<{entity}Entity>>

    @Query("SELECT * FROM {entity.lower()} WHERE id = :id")
    suspend fun getById(id: String): {entity}Entity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(entity: {entity}Entity)

    @Delete
    suspend fun delete(entity: {entity}Entity)

    @Query("DELETE FROM {entity.lower()}")
    suspend fun deleteAll()
}}
"""
        
        # Database class
        entities_import = "\n    ".join([
            f"{entity}Entity::class,"
            for entity in entities
        ])
        
        daos = "\n    ".join([
            f"abstract val {entity.lower()}Dao: {entity}Dao"
            for entity in entities
        ])
        
        files["data/database/AppDatabase.kt"] = f"""package {package}.data.database

import androidx.room.Database
import androidx.room.RoomDatabase
import {package}.data.entity.*
import {package}.data.dao.*

@Database(
    entities = [
        {entities_import}
    ],
    version = 1,
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {{
    {daos}
}}
"""
        
        return files
    
    def _to_snake_case(self, name: str) -> str:
        """Convert camelCase to snake_case."""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
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
            "name": "android-skill",
            "version": self.VERSION,
            "category": "mobile",
            "description": "Android native development skill",
            "features": [
                "Activity/Fragment generation",
                "ViewModel generation",
                "Gradle configuration",
                "AndroidManifest generation",
                "Room database setup",
                "Jetpack Compose support"
            ]
        }


def main():
    """Main entry point for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Android Skill')
    parser.add_argument('--version', action='version', version=f'%(prog)s {AndroidSkill.VERSION}')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate activity
    gen_activity = subparsers.add_parser('generate:activity', help='Generate Activity')
    gen_activity.add_argument('--name', required=True, help='Activity name')
    gen_activity.add_argument('--type', default='compose', choices=['compose', 'xml'])
    gen_activity.add_argument('--package', default='com.example.app', help='Package name')
    
    # Setup gradle
    setup_gradle = subparsers.add_parser('setup:gradle', help='Setup Gradle configuration')
    setup_gradle.add_argument('--min-sdk', type=int, default=24)
    setup_gradle.add_argument('--target-sdk', type=int, default=34)
    setup_gradle.add_argument('--no-compose', action='store_true')
    
    # Config manifest
    config_manifest = subparsers.add_parser('config:manifest', help='Configure AndroidManifest')
    config_manifest.add_argument('--package', default='com.example.app')
    config_manifest.add_argument('--permissions', default='', help='Comma-separated permissions')
    config_manifest.add_argument('--activities', default='', help='Comma-separated activities')
    
    # Setup room
    setup_room = subparsers.add_parser('setup:room', help='Setup Room database')
    setup_room.add_argument('--entities', required=True, help='Comma-separated entity names')
    setup_room.add_argument('--package', default='com.example.app')
    
    # Info command
    subparsers.add_parser('info', help='Show skill information')
    
    args = parser.parse_args()
    skill = AndroidSkill()
    
    if args.command == 'generate:activity':
        config = ActivityConfig(
            name=args.name,
            ui_type=UIType(args.type),
            package=args.package
        )
        files = skill.generate_activity(config)
        paths = skill.save_files(files)
        print(f"Generated {len(paths)} activity files:")
        for p in paths:
            print(f"  - {p}")
    
    elif args.command == 'setup:gradle':
        config = GradleConfig(
            min_sdk=args.min_sdk,
            target_sdk=args.target_sdk,
            use_compose=not args.no_compose
        )
        files = skill.setup_gradle(config)
        paths = skill.save_files(files)
        print(f"Generated {len(paths)} Gradle files:")
        for p in paths:
            print(f"  - {p}")
    
    elif args.command == 'config:manifest':
        config = ManifestConfig(
            package=args.package,
            permissions=args.permissions.split(',') if args.permissions else [],
            activities=args.activities.split(',') if args.activities else []
        )
        files = skill.generate_manifest(config)
        paths = skill.save_files(files)
        print(f"Generated {len(paths)} manifest files:")
        for p in paths:
            print(f"  - {p}")
    
    elif args.command == 'setup:room':
        entities = args.entities.split(',')
        files = skill.setup_room(entities, args.package)
        paths = skill.save_files(files)
        print(f"Generated {len(paths)} Room files:")
        for p in paths:
            print(f"  - {p}")
    
    elif args.command == 'info':
        info = skill.get_info()
        print(json.dumps(info, indent=2))
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
