#!/usr/bin/env python3
"""
iOS Skill - Main Module
Provides comprehensive iOS development capabilities including Swift code generation,
Xcode project configuration, certificate management, and App Store deployment.
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class UIFramework(Enum):
    """UI framework types."""
    SWIFTUI = "swiftui"
    UIKIT = "uikit"


class ArchitecturePattern(Enum):
    """Architecture patterns."""
    MVVM = "mvvm"
    MVC = "mvc"
    VIPER = "viper"
    CLEAN = "clean"


@dataclass
class ViewConfig:
    """Configuration for view generation."""
    name: str
    framework: UIFramework = UIFramework.SWIFTUI
    props: List[Dict[str, Any]] = field(default_factory=list)
    is_screen: bool = False
    include_preview: bool = True
    include_viewmodel: bool = False


@dataclass
class ViewModelConfig:
    """Configuration for view model generation."""
    name: str
    dependencies: List[str] = field(default_factory=list)
    use_combine: bool = True
    use_async_await: bool = True


@dataclass
class ModelConfig:
    """Configuration for model generation."""
    name: str
    properties: List[Dict[str, Any]] = field(default_factory=list)
    codable: bool = True
    identifiable: bool = True
    equatable: bool = True


@dataclass
class ProjectConfig:
    """Configuration for Xcode project setup."""
    name: str
    bundle_id: str
    organization: str = "com.example"
    deployment_target: str = "16.0"
    swift_version: str = "5.9"
    use_swiftui: bool = True
    include_tests: bool = True
    include_uikit_preview: bool = False


@dataclass
class SigningConfig:
    """Configuration for code signing."""
    team_id: str
    bundle_id: str
    provisioning_profile: Optional[str] = None
    automatic_signing: bool = True
    capabilities: List[str] = field(default_factory=list)


class IOSSkill:
    """Main skill class for iOS development."""
    
    VERSION = "1.0.0"
    
    SWIFT_TYPES = {
        "string": "String",
        "int": "Int",
        "double": "Double",
        "bool": "Bool",
        "date": "Date",
        "data": "Data",
        "uuid": "UUID",
        "url": "URL",
    }
    
    def __init__(self, output_dir: str = "./generated"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_view(self, config: ViewConfig) -> Dict[str, str]:
        """
        Generate a Swift view with the specified configuration.
        
        Args:
            config: ViewConfig object with generation parameters
            
        Returns:
            Dictionary with generated file paths and content
        """
        files = {}
        
        if config.framework == UIFramework.SWIFTUI:
            files[f"{config.name}.swift"] = self._generate_swiftui_view(config)
        else:
            files[f"{config.name}.swift"] = self._generate_uikit_view(config)
        
        if config.include_viewmodel:
            vm_config = ViewModelConfig(name=f"{config.name}Model")
            files[f"{config.name}ViewModel.swift"] = self._generate_viewmodel(vm_config)
        
        return files
    
    def _generate_swiftui_view(self, config: ViewConfig) -> str:
        """Generate SwiftUI view code."""
        # Generate property declarations
        properties = []
        init_params = []
        
        for prop in config.props:
            swift_type = self.SWIFT_TYPES.get(prop.get("type", "string"), "String")
            name = prop.get("name", "")
            optional = prop.get("optional", False)
            state = prop.get("state", False)
            binding = prop.get("binding", False)
            
            if optional:
                swift_type += "?"
            
            if state:
                properties.append(f"    @State private var {name}: {swift_type}")
            elif binding:
                properties.append(f"    @Binding var {name}: {swift_type}")
            else:
                properties.append(f"    let {name}: {swift_type}")
                init_params.append(f"{name}: {swift_type}")
        
        props_str = "\n".join(properties) if properties else ""
        init_str = ", ".join(init_params) if init_params else ""
        
        # Generate preview if enabled
        preview = ""
        if config.include_preview:
            preview = f"""

#Preview {{
    {config.name}({init_str})
}}"""
        
        view_code = f"""import SwiftUI

struct {config.name}: View {{
{props_str}

    var body: some View {{
        VStack {{
            Text("{config.name}")
                .font(.title)
            // TODO: Implement view content
        }}
    }}
}}{preview}
"""
        return view_code
    
    def _generate_uikit_view(self, config: ViewConfig) -> str:
        """Generate UIKit view controller code."""
        properties = []
        
        for prop in config.props:
            swift_type = self.SWIFT_TYPES.get(prop.get("type", "string"), "String")
            name = prop.get("name", "")
            optional = prop.get("optional", False)
            
            if optional:
                swift_type += "?"
            
            properties.append(f"    private let {name}: {swift_type}")
        
        props_str = "\n".join(properties) if properties else ""
        
        view_code = f"""import UIKit

class {config.name}: UIViewController {{
{props_str}

    // MARK: - UI Components
    private let titleLabel: UILabel = {{
        let label = UILabel()
        label.translatesAutoresizingMaskIntoConstraints = false
        label.font = .preferredFont(forTextStyle: .title1)
        label.text = "{config.name}"
        return label
    }}()

    // MARK: - Lifecycle
    override func viewDidLoad() {{
        super.viewDidLoad()
        setupUI()
    }}

    // MARK: - Setup
    private func setupUI() {{
        view.backgroundColor = .systemBackground
        view.addSubview(titleLabel)
        
        NSLayoutConstraint.activate([
            titleLabel.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            titleLabel.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }}
}}
"""
        return view_code
    
    def _generate_viewmodel(self, config: ViewModelConfig) -> str:
        """Generate MVVM view model code."""
        imports = ["import Foundation"]
        if config.use_combine:
            imports.append("import Combine")
        
        imports_str = "\n".join(imports)
        
        published_props = [
            "    @Published var isLoading = false",
            "    @Published var error: Error?"
        ]
        
        combine_declarations = []
        init_deps = []
        
        if config.use_combine:
            combine_declarations.append("    private var cancellables = Set<AnyCancellable>()")
        
        for dep in config.dependencies:
            protocol_name = f"{dep.capitalize()}ServiceProtocol"
            var_name = f"{dep.lower()}Service"
            init_deps.append(f"{var_name}: {protocol_name} = {dep.capitalize()}Service()")
        
        deps_str = "\n    ".join([f"private let {dep}" for dep in init_deps]) if init_deps else ""
        published_str = "\n".join(published_props)
        combine_str = "\n".join(combine_declarations)
        
        viewmodel_code = f"""{imports_str}

@MainActor
class {config.name}: ObservableObject {{
{published_str}
{combine_str}
{deps_str}

    init() {{
        // Initialize with default values or dependency injection
    }}

    // MARK: - Methods
    func load() async {{
        isLoading = true
        defer {{ isLoading = false }}
        
        do {{
            // TODO: Implement loading logic
        }} catch {{
            self.error = error
        }}
    }}
}}
"""
        return viewmodel_code
    
    def generate_model(self, config: ModelConfig) -> Dict[str, str]:
        """
        Generate a Swift model with the specified configuration.
        
        Args:
            config: ModelConfig object
            
        Returns:
            Dictionary with generated model files
        """
        files = {}
        
        # Property declarations
        properties = []
        coding_keys = []
        init_params = []
        init_assignments = []
        
        for prop in config.properties:
            swift_type = self.SWIFT_TYPES.get(prop.get("type", "string"), "String")
            name = prop.get("name", "")
            optional = prop.get("optional", False)
            
            if optional:
                swift_type += "?"
            
            properties.append(f"    let {name}: {swift_type}")
            coding_keys.append(f"        case {name}")
            init_params.append(f"{name}: {swift_type}")
            init_assignments.append(f"        self.{name} = {name}")
        
        props_str = "\n".join(properties)
        coding_str = "\n".join(coding_keys)
        init_params_str = ",\n        ".join(init_params)
        init_assign_str = "\n".join(init_assignments)
        
        # Conformances
        conformances = []
        if config.codable:
            conformances.append("Codable")
        if config.identifiable:
            conformances.append("Identifiable")
        if config.equatable:
            conformances.append("Equatable")
        
        conformance_str = ", ".join(conformances)
        id_property = "    let id: UUID\n" if config.identifiable else ""
        
        model_code = f"""import Foundation

struct {config.name}: {conformance_str} {{
{id_property}{props_str}

    init(
        {init_params_str}
    ) {{
{init_assign_str}
    }}
}}
"""
        
        files[f"{config.name}.swift"] = model_code
        
        return files
    
    def setup_project(self, config: ProjectConfig) -> Dict[str, str]:
        """
        Setup Xcode project structure.
        
        Args:
            config: ProjectConfig object
            
        Returns:
            Dictionary with generated project files
        """
        files = {}
        
        # Main app file
        if config.use_swiftui:
            files[f"{config.name}/App/{config.name}App.swift"] = self._generate_swiftui_app(config)
        else:
            files[f"{config.name}/App/AppDelegate.swift"] = self._generate_uikit_appdelegate(config)
            files[f"{config.name}/App/SceneDelegate.swift"] = self._generate_uikit_scenedelegate(config)
        
        # Project structure
        files[f"{config.name}/Views/README.md"] = "# Views\n\nUI views and components."
        files[f"{config.name}/ViewModels/README.md"] = "# ViewModels\n\nMVVM view models."
        files[f"{config.name}/Models/README.md"] = "# Models\n\nData models."
        files[f"{config.name}/Services/README.md"] = "# Services\n\nBusiness logic services."
        files[f"{config.name}/Utils/README.md"] = "# Utils\n\nUtility classes and extensions."
        files[f"{config.name}/Resources/README.md"] = "# Resources\n\nAssets, colors, fonts."
        
        # Build settings file
        files[f"{config.name}/BuildSettings.xcconfig"] = self._generate_build_config(config)
        
        # Tests
        if config.include_tests:
            files[f"{config.name}Tests/{config.name}Tests.swift"] = self._generate_unit_tests(config)
            files[f"{config.name}UITests/{config.name}UITests.swift"] = self._generate_ui_tests(config)
        
        return files
    
    def _generate_swiftui_app(self, config: ProjectConfig) -> str:
        """Generate SwiftUI app entry point."""
        return f"""import SwiftUI

@main
struct {config.name}App: App {{
    var body: some Scene {{
        WindowGroup {{
            ContentView()
        }}
    }}
}}
"""
    
    def _generate_uikit_appdelegate(self, config: ProjectConfig) -> str:
        """Generate UIKit app delegate."""
        return f"""import UIKit

@main
class AppDelegate: UIResponder, UIApplicationDelegate {{

    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {{
        return true
    }}

    // MARK: UISceneSession Lifecycle
    func application(_ application: UIApplication, configurationForConnecting connectingSceneSession: UISceneSession, options: UIScene.ConnectionOptions) -> UISceneConfiguration {{
        return UISceneConfiguration(name: "Default Configuration", sessionRole: connectingSceneSession.role)
    }}
}}
"""
    
    def _generate_uikit_scenedelegate(self, config: ProjectConfig) -> str:
        """Generate UIKit scene delegate."""
        return f"""import UIKit

class SceneDelegate: UIResponder, UIWindowSceneDelegate {{
    var window: UIWindow?

    func scene(_ scene: UIScene, willConnectTo session: UISceneSession, options connectionOptions: UIScene.ConnectionOptions) {{
        guard let windowScene = (scene as? UIWindowScene) else {{ return }}
        
        window = UIWindow(windowScene: windowScene)
        window?.rootViewController = UINavigationController(rootViewController: ViewController())
        window?.makeKeyAndVisible()
    }}
}}
"""
    
    def _generate_build_config(self, config: ProjectConfig) -> str:
        """Generate build configuration."""
        return f"""// Build Settings
SWIFT_VERSION = {config.swift_version}
IPHONEOS_DEPLOYMENT_TARGET = {config.deployment_target}
TARGETED_DEVICE_FAMILY = 1,2

// Code Signing
CODE_SIGN_STYLE = Automatic
DEVELOPMENT_TEAM = 

// Optimization
SWIFT_OPTIMIZATION_LEVEL = -O
SWIFT_COMPILATION_MODE = wholemodule
"""
    
    def _generate_unit_tests(self, config: ProjectConfig) -> str:
        """Generate unit test template."""
        return f"""import XCTest
@testable import {config.name}

final class {config.name}Tests: XCTestCase {{

    override func setUpWithError() throws {{
        // Put setup code here
    }}

    override func tearDownWithError() throws {{
        // Put teardown code here
    }}

    func testExample() throws {{
        XCTAssertTrue(true)
    }}
}}
"""
    
    def _generate_ui_tests(self, config: ProjectConfig) -> str:
        """Generate UI test template."""
        return f"""import XCTest

final class {config.name}UITests: XCTestCase {{

    override func setUpWithError() throws {{
        continueAfterFailure = false
    }}

    func testExample() throws {{
        let app = XCUIApplication()
        app.launch()
    }}
}}
"""
    
    def generate_networking_layer(self, base_url: str, auth_type: str = "none") -> Dict[str, str]:
        """
        Generate networking layer.
        
        Args:
            base_url: API base URL
            auth_type: Authentication type (none, bearer, apikey)
            
        Returns:
            Dictionary with generated network files
        """
        files = {}
        
        # API Service protocol
        files["Services/APIServiceProtocol.swift"] = """import Foundation

protocol APIServiceProtocol {
    func request<T: Decodable>(_ endpoint: Endpoint) async throws -> T
}

enum APIError: Error {
    case invalidURL
    case invalidResponse
    case decodingError
    case serverError(Int)
}
"""
        
        # Endpoint protocol
        files["Services/Endpoint.swift"] = f"""import Foundation

protocol Endpoint {{
    var baseURL: String {{ get }}
    var path: String {{ get }}
    var method: HTTPMethod {{ get }}
    var headers: [String: String]? {{ get }}
    var body: Data? {{ get }}
}}

extension Endpoint {{
    var baseURL: String {{ "{base_url}" }}
}}

enum HTTPMethod: String {{
    case get = "GET"
    case post = "POST"
    case put = "PUT"
    case patch = "PATCH"
    case delete = "DELETE"
}}
"""
        
        # API Service implementation
        auth_header = ""
        if auth_type == "bearer":
            auth_header = """
        // Add authorization header if needed
        // request.setValue("Bearer \\(token)", forHTTPHeaderField: "Authorization")
"""
        
        files["Services/APIService.swift"] = f"""import Foundation

class APIService: APIServiceProtocol {{
    private let session: URLSession
    private let decoder: JSONDecoder
    
    init(session: URLSession = .shared) {{
        self.session = session
        self.decoder = JSONDecoder()
        self.decoder.keyDecodingStrategy = .convertFromSnakeCase
    }}
    
    func request<T: Decodable>(_ endpoint: Endpoint) async throws -> T {{
        guard let url = URL(string: endpoint.baseURL + endpoint.path) else {{
            throw APIError.invalidURL
        }}
        
        var request = URLRequest(url: url)
        request.httpMethod = endpoint.method.rawValue
        request.httpBody = endpoint.body
        {auth_header}
        
        endpoint.headers?.forEach {{ key, value in
            request.setValue(value, forHTTPHeaderField: key)
        }}
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {{
            throw APIError.invalidResponse
        }}
        
        guard (200...299).contains(httpResponse.statusCode) else {{
            throw APIError.serverError(httpResponse.statusCode)
        }}
        
        do {{
            return try decoder.decode(T.self, from: data)
        }} catch {{
            throw APIError.decodingError
        }}
    }}
}}
"""
        
        return files
    
    def generate_coredata_model(self, entities: List[str]) -> Dict[str, str]:
        """
        Generate Core Data model boilerplate.
        
        Args:
            entities: List of entity names
            
        Returns:
            Dictionary with generated Core Data files
        """
        files = {}
        
        # Persistence controller
        files["CoreData/PersistenceController.swift"] = """import CoreData

struct PersistenceController {
    static let shared = PersistenceController()
    
    let container: NSPersistentContainer
    
    init(inMemory: Bool = false) {
        container = NSPersistentContainer(name: "Model")
        
        if inMemory {
            container.persistentStoreDescriptions.first!.url = URL(fileURLWithPath: "/dev/null")
        }
        
        container.loadPersistentStores { description, error in
            if let error = error {
                fatalError("Error loading Core Data: \\(error)")
            }
        }
        
        container.viewContext.automaticallyMergesChangesFromParent = true
    }
}
"""
        
        # Generate entity files
        for entity in entities:
            entity_lower = entity.lower()
            files[f"CoreData/{entity}+CoreDataClass.swift"] = f"""import Foundation
import CoreData

@objc({entity})
public class {entity}: NSManagedObject {{
}}
"""
            
            files[f"CoreData/{entity}+CoreDataProperties.swift"] = f"""import Foundation
import CoreData

extension {entity} {{
    @nonobjc public class func fetchRequest() -> NSFetchRequest<{entity}> {{
        return NSFetchRequest<{entity}>(entityName: "{entity}")
    }}

    @NSManaged public var id: UUID
    @NSManaged public var createdAt: Date
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
            "name": "ios-skill",
            "version": self.VERSION,
            "category": "mobile",
            "description": "iOS native development skill",
            "features": [
                "SwiftUI/UIKit view generation",
                "MVVM view model generation",
                "Swift model generation",
                "Xcode project setup",
                "Core Data boilerplate",
                "Networking layer setup"
            ]
        }


def main():
    """Main entry point for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='iOS Skill')
    parser.add_argument('--version', action='version', version=f'%(prog)s {IOSSkill.VERSION}')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate view
    gen_view = subparsers.add_parser('generate:view', help='Generate a view')
    gen_view.add_argument('--name', required=True, help='View name')
    gen_view.add_argument('--type', default='swiftui', choices=['swiftui', 'uikit'])
    gen_view.add_argument('--screen', action='store_true', help='Mark as screen')
    
    # Generate model
    gen_model = subparsers.add_parser('generate:model', help='Generate a model')
    gen_model.add_argument('--name', required=True, help='Model name')
    gen_model.add_argument('--no-codable', action='store_true', help='Disable Codable')
    
    # Setup project
    setup_project = subparsers.add_parser('setup:project', help='Setup Xcode project')
    setup_project.add_argument('--name', required=True, help='Project name')
    setup_project.add_argument('--bundle-id', required=True, help='Bundle identifier')
    setup_project.add_argument('--uikit', action='store_true', help='Use UIKit instead of SwiftUI')
    
    # Setup network
    setup_network = subparsers.add_parser('setup:network', help='Setup networking layer')
    setup_network.add_argument('--base-url', required=True, help='API base URL')
    setup_network.add_argument('--auth', default='none', choices=['none', 'bearer', 'apikey'])
    
    # Generate Core Data
    gen_coredata = subparsers.add_parser('generate:coredata', help='Generate Core Data model')
    gen_coredata.add_argument('--entities', required=True, help='Comma-separated entity names')
    
    # Info command
    subparsers.add_parser('info', help='Show skill information')
    
    args = parser.parse_args()
    skill = IOSSkill()
    
    if args.command == 'generate:view':
        config = ViewConfig(
            name=args.name,
            framework=UIFramework(args.type),
            is_screen=args.screen
        )
        files = skill.generate_view(config)
        paths = skill.save_files(files)
        print(f"Generated {len(paths)} view files:")
        for p in paths:
            print(f"  - {p}")
    
    elif args.command == 'generate:model':
        config = ModelConfig(
            name=args.name,
            codable=not args.no_codable
        )
        files = skill.generate_model(config)
        paths = skill.save_files(files)
        print(f"Generated {len(paths)} model files:")
        for p in paths:
            print(f"  - {p}")
    
    elif args.command == 'setup:project':
        config = ProjectConfig(
            name=args.name,
            bundle_id=args.bundle_id,
            use_swiftui=not args.uikit
        )
        files = skill.setup_project(config)
        paths = skill.save_files(files)
        print(f"Generated {len(paths)} project files:")
        for p in paths:
            print(f"  - {p}")
    
    elif args.command == 'setup:network':
        files = skill.generate_networking_layer(args.base_url, args.auth)
        paths = skill.save_files(files)
        print(f"Generated {len(paths)} network files:")
        for p in paths:
            print(f"  - {p}")
    
    elif args.command == 'generate:coredata':
        entities = args.entities.split(',')
        files = skill.generate_coredata_model(entities)
        paths = skill.save_files(files)
        print(f"Generated {len(paths)} Core Data files:")
        for p in paths:
            print(f"  - {p}")
    
    elif args.command == 'info':
        info = skill.get_info()
        print(json.dumps(info, indent=2))
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
