# iOS Skill

A comprehensive skill for iOS native development, providing Swift code generation, Xcode project configuration, certificate management, and App Store deployment assistance.

## Use When

- Creating new iOS projects from scratch
- Generating Swift code for views, view controllers, and models
- Setting up Xcode project configurations
- Managing code signing and provisioning profiles
- Configuring App Store Connect and distribution
- Implementing SwiftUI or UIKit interfaces
- Setting up Core Data or SwiftData persistence
- Implementing networking with URLSession or Alamofire
- Configuring push notifications (APNs)
- Implementing biometric authentication (Face ID/Touch ID)
- Setting up in-app purchases
- Configuring app extensions (widgets, share extensions, etc.)

## Out of Scope

- Cross-platform development (use react-native-skill or flutter-skill)
- Android development (use android-skill)
- Backend API development (use backend-specific skills)
- Machine learning model training (use Core ML specific tools)
- Game development beyond basic UIKit/SwiftUI (use SpriteKit/SceneKit skills)
- Complex AR/VR development (use ARKit specific skills)
- macOS/tvOS/watchOS specific features

## Features

### Swift Code Generation
- SwiftUI views and components
- UIKit view controllers and cells
- MVVM architecture templates
- Network layer with URLSession
- Core Data models and managers
- SwiftData models
- Swift Concurrency (async/await) patterns
- Combine framework integration

### Xcode Project Setup
- Project structure generation
- Target configuration (iOS, iPadOS)
- Build settings optimization
- Scheme configuration
- Build phases setup
- Run scripts integration
- Swift Package Manager integration
- CocoaPods/Carthage support

### Certificate Management
- Development certificate setup
- Distribution certificate management
- Provisioning profile configuration
- App ID registration
- Device registration
- Push notification certificates

### App Store Deployment
- App Store Connect configuration
- App metadata management
- Screenshot automation
- Build upload automation
- TestFlight management
- Release checklist generation

### UI Frameworks
- SwiftUI components and modifiers
- UIKit storyboard/code generation
- Auto Layout constraints
- Collection view compositional layouts
- Diffable data sources
- Custom view animations

### Data Persistence
- Core Data setup
- SwiftData configuration
- UserDefaults wrapper
- Keychain access
- File manager utilities
- CloudKit integration

### Networking
- URLSession wrappers
- REST API clients
- GraphQL integration
- WebSocket connections
- Background downloads/uploads
- Network monitoring

### System Integration
- Push notifications (APNs)
- Local notifications
- Biometric authentication
- Camera/Photo library access
- Location services
- HealthKit integration
- SiriKit intents
- Shortcuts

### Testing
- XCTest setup
- UI automation tests
- Performance testing
- Snapshot testing
- Mock generation

## Installation

```bash
# Clone the skill
cp -r ios-skill ~/.kimi/skills/

# Install dependencies
cd ~/.kimi/skills/ios-skill
pip install -r requirements.txt
```

## Usage

### Generate SwiftUI View
```bash
kimi skill ios-skill generate view --name="ProfileView" --type="swiftui" --props="user:User"
```

### Setup Xcode Project
```bash
kimi skill ios-skill setup project --name="MyApp" --bundle-id="com.example.myapp" --swiftui
```

### Configure Code Signing
```bash
kimi skill ios-skill config signing --team-id="XXXXX" --bundle-id="com.example.myapp"
```

### Generate Core Data Model
```bash
kimi skill ios-skill generate coredata --entities="User,Product,Order" --relationships="User.orders"
```

### Setup Networking Layer
```bash
kimi skill ios-skill setup network --base-url="https://api.example.com" --auth="bearer"
```

## API Reference

### Code Generation
- `generate:view` - Generate SwiftUI/UIKit views
- `generate:viewmodel` - Create MVVM view models
- `generate:model` - Generate data models
- `generate:service` - Create service classes
- `generate:coredata` - Generate Core Data entities

### Project Setup
- `setup:project` - Initialize Xcode project
- `setup:spm` - Configure Swift Package Manager
- `setup:schemes` - Generate build schemes
- `config:build-settings` - Optimize build settings

### Certificates & Signing
- `config:signing` - Setup code signing
- `config:push` - Configure push notifications
- `generate:provisioning` - Create provisioning profiles

### App Store
- `setup:asc` - Configure App Store Connect
- `generate:metadata` - Create app metadata
- `generate:screenshots` - Screenshot automation

## Configuration

### skill.json
```json
{
  "name": "ios-skill",
  "version": "1.0.0",
  "category": "mobile",
  "description": "iOS native development skill",
  "author": "Kimi",
  "dependencies": ["xcode", "swift"]
}
```

## Examples

### SwiftUI View
```swift
import SwiftUI

struct ProfileView: View {
    @StateObject private var viewModel: ProfileViewModel
    
    var body: some View {
        VStack(spacing: 20) {
            AsyncImage(url: viewModel.avatarURL) { image in
                image.resizable()
            } placeholder: {
                ProgressView()
            }
            .frame(width: 100, height: 100)
            .clipShape(Circle())
            
            Text(viewModel.userName)
                .font(.title)
            
            Text(viewModel.email)
                .font(.subheadline)
                .foregroundColor(.secondary)
        }
        .padding()
    }
}

#Preview {
    ProfileView()
}
```

### MVVM ViewModel
```swift
import Foundation
import Combine

@MainActor
class ProfileViewModel: ObservableObject {
    @Published var user: User?
    @Published var isLoading = false
    @Published var error: Error?
    
    private let userService: UserServiceProtocol
    private var cancellables = Set<AnyCancellable>()
    
    init(userService: UserServiceProtocol = UserService()) {
        self.userService = userService
    }
    
    func loadUser() async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            user = try await userService.fetchCurrentUser()
        } catch {
            self.error = error
        }
    }
}
```

### Core Data Model
```swift
import CoreData

@objc(User)
public class User: NSManagedObject {
    @NSManaged public var id: UUID
    @NSManaged public var name: String
    @NSManaged public var email: String
    @NSManaged public var createdAt: Date
}

extension User {
    @nonobjc public class func fetchRequest() -> NSFetchRequest<User> {
        return NSFetchRequest<User>(entityName: "User")
    }
}
```

### Network Service
```swift
import Foundation

protocol APIServiceProtocol {
    func fetch<T: Decodable>(_ endpoint: Endpoint) async throws -> T
}

class APIService: APIServiceProtocol {
    private let session: URLSession
    private let baseURL: URL
    
    init(baseURL: URL, session: URLSession = .shared) {
        self.baseURL = baseURL
        self.session = session
    }
    
    func fetch<T: Decodable>(_ endpoint: Endpoint) async throws -> T {
        let request = try buildRequest(for: endpoint)
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw APIError.invalidResponse
        }
        
        return try JSONDecoder().decode(T.self, from: data)
    }
}
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

- [ ] Swift 6.0 concurrency updates
- [ ] SwiftData advanced patterns
- [ ] WidgetKit templates
- [ ] App Intents integration
- [ ] TipKit for onboarding
- [ ] StoreKit 2 templates
- [ ] Metal shader integration
- [ ] Xcode Cloud CI/CD templates
