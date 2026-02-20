# Android Skill

A comprehensive skill for Android native development, providing Kotlin/Java code generation, Gradle configuration, AndroidManifest management, and modern Android architecture patterns.

## Use When

- Creating new Android projects from scratch
- Generating Kotlin/Java code for Activities, Fragments, ViewModels
- Setting up Gradle build configuration and dependencies
- Configuring AndroidManifest.xml
- Implementing MVVM or MVI architecture patterns
- Setting up Jetpack Compose UI
- Configuring Room database
- Implementing Retrofit networking
- Setting up Dependency Injection (Hilt/Koin)
- Configuring WorkManager for background tasks
- Implementing notifications
- Setting up Firebase integration
- Creating custom views

## Out of Scope

- Cross-platform development (use react-native-skill or flutter-skill)
- iOS development (use ios-skill)
- Backend API development (use backend-specific skills)
- Game development beyond standard Android SDK (use Unity/Unreal skills)
- Complex AR/VR development (use ARCore specific skills)
- Wear OS/TV specific features

## Features

### Kotlin/Java Code Generation
- Activity and Fragment templates
- ViewModel with LiveData/StateFlow
- Repository pattern
- Data classes (POJOs/Kotlin data classes)
- Custom views
- RecyclerView adapters
- Composable functions (Jetpack Compose)

### Architecture Patterns
- MVVM (Model-View-ViewModel)
- MVI (Model-View-Intent)
- Repository pattern
- Clean Architecture
- Dependency Injection setup

### Gradle Configuration
- Module-level build.gradle
- Project-level build.gradle
- Version catalog (libs.versions.toml)
- Gradle plugin setup
- ProGuard/R8 configuration
- Flavor and build type setup

### AndroidManifest Management
- Permission declarations
- Activity/Service declarations
- Intent filters
- Application configuration
- Meta-data tags

### UI Development
- XML layouts
- Jetpack Compose
- Custom views
- Material Design components
- Navigation component
- ConstraintLayout chains

### Data Persistence
- Room database setup
- DataStore preferences
- SharedPreferences wrapper
- SQLite helpers

### Networking
- Retrofit setup
- OkHttp configuration
- GraphQL integration
- WebSocket clients
- Image loading (Glide/Coil)

### Background Processing
- WorkManager setup
- Foreground services
- Broadcast receivers
- Alarm manager
- Periodic tasks

### System Integration
- Push notifications (FCM)
- Biometric authentication
- Camera integration
- Location services
- Sensors
- Media playback

### Testing
- JUnit tests
- Espresso UI tests
- Mockito/MockK mocking
- Hilt testing

## Installation

```bash
# Clone the skill
cp -r android-skill ~/.kimi/skills/

# Install dependencies
cd ~/.kimi/skills/android-skill
pip install -r requirements.txt
```

## Usage

### Generate Activity
```bash
kimi skill android-skill generate activity --name="MainActivity" --type="compose" --viewmodel
```

### Setup Gradle Configuration
```bash
kimi skill android-skill setup gradle --min-sdk=24 --target-sdk=34 --compose
```

### Configure AndroidManifest
```bash
kimi skill android-skill config manifest --permissions="INTERNET,CAMERA" --activities="MainActivity,SettingsActivity"
```

### Setup Room Database
```bash
kimi skill android-skill setup room --entities="User,Product,Order" --relationships="User.orders"
```

### Setup Networking
```bash
kimi skill android-skill setup retrofit --base-url="https://api.example.com" --auth="bearer"
```

### Setup Dependency Injection
```bash
kimi skill android-skill setup di --framework="hilt" --modules="network,database"
```

## API Reference

### Code Generation
- `generate:activity` - Generate Activity classes
- `generate:fragment` - Generate Fragment classes
- `generate:viewmodel` - Create ViewModels
- `generate:adapter` - Generate RecyclerView adapters
- `generate:model` - Generate data classes

### Configuration
- `setup:gradle` - Configure Gradle build files
- `config:manifest` - Setup AndroidManifest.xml
- `setup:room` - Configure Room database
- `setup:retrofit` - Setup Retrofit networking
- `setup:hilt` - Configure Hilt DI
- `setup:koin` - Configure Koin DI

### UI
- `setup:compose` - Setup Jetpack Compose
- `generate:layout` - Generate XML layouts
- `generate:composable` - Generate Compose functions

### Build
- `config:proguard` - Setup ProGuard rules
- `setup:flavors` - Configure build flavors
- `setup:signing` - Configure signing config

## Configuration

### skill.json
```json
{
  "name": "android-skill",
  "version": "1.0.0",
  "category": "mobile",
  "description": "Android native development skill",
  "author": "Kimi",
  "dependencies": ["android-studio", "gradle", "kotlin"]
}
```

## Examples

### Kotlin Activity with ViewModel
```kotlin
import android.os.Bundle
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {
    
    private val viewModel: MainViewModel by viewModels()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    updateUI(state)
                }
            }
        }
    }
    
    private fun updateUI(state: MainUiState) {
        // Update UI based on state
    }
}
```

### ViewModel with StateFlow
```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class MainUiState(
    val isLoading: Boolean = false,
    val data: List<String> = emptyList(),
    val error: String? = null
)

class MainViewModel(
    private val repository: MainRepository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(MainUiState())
    val uiState: StateFlow<MainUiState> = _uiState.asStateFlow()
    
    fun loadData() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)
            
            try {
                val data = repository.fetchData()
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    data = data
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = e.message
                )
            }
        }
    }
}
```

### Jetpack Compose Screen
```kotlin
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle

@Composable
fun ProfileScreen(
    viewModel: ProfileViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    
    Scaffold(
        topBar = {
            TopAppBar(title = { Text("Profile") })
        }
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            when {
                uiState.isLoading -> CircularProgressIndicator()
                uiState.error != null -> ErrorMessage(uiState.error)
                else -> ProfileContent(uiState.user)
            }
        }
    }
}

@Composable
private fun ProfileContent(user: User?) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            text = user?.name ?: "",
            style = MaterialTheme.typography.headlineMedium
        )
        Text(
            text = user?.email ?: "",
            style = MaterialTheme.typography.bodyLarge
        )
    }
}
```

### Room Database Entity
```kotlin
import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.Date

@Entity(tableName = "users")
data class UserEntity(
    @PrimaryKey val id: String,
    val name: String,
    val email: String,
    val createdAt: Date
)

@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    suspend fun getAll(): List<UserEntity>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(user: UserEntity)
    
    @Delete
    suspend fun delete(user: UserEntity)
}
```

### Retrofit Service
```kotlin
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Body
import retrofit2.http.Path

interface ApiService {
    @GET("users")
    suspend fun getUsers(): List<User>
    
    @GET("users/{id}")
    suspend fun getUser(@Path("id") id: String): User
    
    @POST("users")
    suspend fun createUser(@Body user: User): User
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

- [ ] Kotlin Multiplatform Mobile (KMM) support
- [ ] Jetpack Glance widgets
- [ ] Predictive back gesture
- [ ] Per-app language preferences
- [ ] Downloadable fonts
- [ ] Baseline Profiles
- [ ] Macrobenchmark testing
- [ ] Gradle version catalog templates
