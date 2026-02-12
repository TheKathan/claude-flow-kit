# .NET Development Guide - {{PROJECT_NAME}}

**Date**: {{CURRENT_DATE}}

---

## Quick Start

### Development Environment

```bash
# Check .NET version
dotnet --version

# Restore packages
dotnet restore

# Build solution
dotnet build

# Run application
dotnet run --project {{BACKEND_FOLDER}}/{{PROJECT_NAME}}.csproj

# Run tests
dotnet test

# Watch mode (hot reload)
dotnet watch run --project {{BACKEND_FOLDER}}/{{PROJECT_NAME}}.csproj
```

---

## Project Structure

### ASP.NET Core Web API

```
{{BACKEND_FOLDER}}/
├── Controllers/           # API endpoints
├── Services/             # Business logic
├── Models/               # Domain models
├── Data/                 # Database context and migrations
│   ├── ApplicationDbContext.cs
│   └── Migrations/
├── DTOs/                 # Data transfer objects
├── Middleware/           # Custom middleware
├── Extensions/           # Extension methods
├── Program.cs            # Application entry point
├── appsettings.json      # Configuration
├── appsettings.Development.json
└── {{PROJECT_NAME}}.csproj
```

---

## Code Style Guidelines

### Naming Conventions

**Classes, Methods, Properties**: PascalCase
```csharp
public class UserService
{
    public async Task<User> GetUserAsync(int userId) { }
    public string UserName { get; set; }
}
```

**Parameters, Local Variables**: camelCase
```csharp
public async Task<User> CreateUser(string userName, string email)
{
    var newUser = new User();
    int userId = await SaveUserAsync(newUser);
}
```

**Private Fields**: _camelCase
```csharp
public class UserService
{
    private readonly IUserRepository _userRepository;
    private readonly ILogger<UserService> _logger;
}
```

**Interfaces**: IPascalCase
```csharp
public interface IUserService { }
public interface IUserRepository { }
```

**Constants**: UPPER_CASE or PascalCase
```csharp
public const int MAX_RETRY_COUNT = 3;
public const string DefaultConnectionString = "...";
```

### File Organization

- One class per file
- File name matches class name
- Organize using folders by feature or layer

### Using Directives

- Sort alphabetically
- System namespaces first
- Remove unused usings

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using {{PROJECT_NAME}}.Models;
using {{PROJECT_NAME}}.Services;
```

---

## ASP.NET Core Best Practices

### Dependency Injection

**Register services in Program.cs**:
```csharp
var builder = WebApplication.CreateBuilder(args);

// Add services
builder.Services.AddControllers();
builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection")));

// Register custom services
builder.Services.AddScoped<IUserService, UserService>();
builder.Services.AddScoped<IUserRepository, UserRepository>();

// Add authentication
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options => { /* ... */ });

var app = builder.Build();
```

**Use constructor injection**:
```csharp
public class UserController : ControllerBase
{
    private readonly IUserService _userService;
    private readonly ILogger<UserController> _logger;

    public UserController(
        IUserService userService,
        ILogger<UserController> logger)
    {
        _userService = userService;
        _logger = logger;
    }
}
```

### Controller Design

**Use ApiController attribute**:
```csharp
[ApiController]
[Route("api/[controller]")]
public class UsersController : ControllerBase
{
    [HttpGet]
    public async Task<ActionResult<IEnumerable<UserDto>>> GetUsers()
    {
        var users = await _userService.GetAllUsersAsync();
        return Ok(users);
    }

    [HttpGet("{id}")]
    public async Task<ActionResult<UserDto>> GetUser(int id)
    {
        var user = await _userService.GetUserByIdAsync(id);

        if (user == null)
            return NotFound();

        return Ok(user);
    }

    [HttpPost]
    public async Task<ActionResult<UserDto>> CreateUser(CreateUserDto dto)
    {
        var user = await _userService.CreateUserAsync(dto);
        return CreatedAtAction(nameof(GetUser), new { id = user.Id }, user);
    }

    [HttpPut("{id}")]
    public async Task<IActionResult> UpdateUser(int id, UpdateUserDto dto)
    {
        if (id != dto.Id)
            return BadRequest();

        await _userService.UpdateUserAsync(dto);
        return NoContent();
    }

    [HttpDelete("{id}")]
    public async Task<IActionResult> DeleteUser(int id)
    {
        await _userService.DeleteUserAsync(id);
        return NoContent();
    }
}
```

### DTOs and Validation

**Use Data Annotations**:
```csharp
public class CreateUserDto
{
    [Required]
    [StringLength(100, MinimumLength = 2)]
    public string UserName { get; set; }

    [Required]
    [EmailAddress]
    public string Email { get; set; }

    [Required]
    [StringLength(100, MinimumLength = 8)]
    [RegularExpression(@"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$")]
    public string Password { get; set; }
}
```

**Or use FluentValidation**:
```csharp
public class CreateUserDtoValidator : AbstractValidator<CreateUserDto>
{
    public CreateUserDtoValidator()
    {
        RuleFor(x => x.UserName)
            .NotEmpty()
            .Length(2, 100);

        RuleFor(x => x.Email)
            .NotEmpty()
            .EmailAddress();

        RuleFor(x => x.Password)
            .NotEmpty()
            .MinimumLength(8)
            .Matches(@"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$");
    }
}
```

### Entity Framework Core

**DbContext**:
```csharp
public class ApplicationDbContext : DbContext
{
    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
        : base(options)
    {
    }

    public DbSet<User> Users { get; set; }
    public DbSet<Post> Posts { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Configure entities
        modelBuilder.Entity<User>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Email).IsRequired().HasMaxLength(255);
            entity.HasIndex(e => e.Email).IsUnique();
        });

        modelBuilder.Entity<Post>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.HasOne(p => p.Author)
                .WithMany(u => u.Posts)
                .HasForeignKey(p => p.AuthorId);
        });
    }
}
```

**Repository Pattern**:
```csharp
public interface IUserRepository
{
    Task<User> GetByIdAsync(int id);
    Task<IEnumerable<User>> GetAllAsync();
    Task<User> AddAsync(User user);
    Task UpdateAsync(User user);
    Task DeleteAsync(int id);
}

public class UserRepository : IUserRepository
{
    private readonly ApplicationDbContext _context;

    public UserRepository(ApplicationDbContext context)
    {
        _context = context;
    }

    public async Task<User> GetByIdAsync(int id)
    {
        return await _context.Users
            .Include(u => u.Posts)
            .FirstOrDefaultAsync(u => u.Id == id);
    }

    public async Task<IEnumerable<User>> GetAllAsync()
    {
        return await _context.Users.ToListAsync();
    }

    public async Task<User> AddAsync(User user)
    {
        _context.Users.Add(user);
        await _context.SaveChangesAsync();
        return user;
    }

    public async Task UpdateAsync(User user)
    {
        _context.Users.Update(user);
        await _context.SaveChangesAsync();
    }

    public async Task DeleteAsync(int id)
    {
        var user = await _context.Users.FindAsync(id);
        if (user != null)
        {
            _context.Users.Remove(user);
            await _context.SaveChangesAsync();
        }
    }
}
```

---

## Database Migrations

### Entity Framework Core Migrations

```bash
# Add new migration
dotnet ef migrations add InitialCreate --project {{BACKEND_FOLDER}}

# Update database
dotnet ef database update --project {{BACKEND_FOLDER}}

# Remove last migration (if not applied)
dotnet ef migrations remove --project {{BACKEND_FOLDER}}

# Generate SQL script
dotnet ef migrations script --project {{BACKEND_FOLDER}} --output migration.sql

# Rollback to specific migration
dotnet ef database update PreviousMigration --project {{BACKEND_FOLDER}}
```

### Migration Best Practices

1. **Always review generated migrations**
2. **Test migrations on dev database first**
3. **Backup production database before migration**
4. **Use migration scripts for production**

---

## Testing

### Unit Tests (xUnit)

```csharp
public class UserServiceTests
{
    private readonly Mock<IUserRepository> _mockRepository;
    private readonly Mock<ILogger<UserService>> _mockLogger;
    private readonly UserService _service;

    public UserServiceTests()
    {
        _mockRepository = new Mock<IUserRepository>();
        _mockLogger = new Mock<ILogger<UserService>>();
        _service = new UserService(_mockRepository.Object, _mockLogger.Object);
    }

    [Fact]
    public async Task GetUserByIdAsync_ReturnsUser_WhenUserExists()
    {
        // Arrange
        var userId = 1;
        var expectedUser = new User { Id = userId, UserName = "testuser" };
        _mockRepository.Setup(r => r.GetByIdAsync(userId))
            .ReturnsAsync(expectedUser);

        // Act
        var result = await _service.GetUserByIdAsync(userId);

        // Assert
        Assert.NotNull(result);
        Assert.Equal(expectedUser.Id, result.Id);
        Assert.Equal(expectedUser.UserName, result.UserName);
    }

    [Fact]
    public async Task GetUserByIdAsync_ReturnsNull_WhenUserNotFound()
    {
        // Arrange
        var userId = 999;
        _mockRepository.Setup(r => r.GetByIdAsync(userId))
            .ReturnsAsync((User)null);

        // Act
        var result = await _service.GetUserByIdAsync(userId);

        // Assert
        Assert.Null(result);
    }

    [Theory]
    [InlineData("")]
    [InlineData(null)]
    public async Task CreateUserAsync_ThrowsException_WhenUserNameInvalid(string userName)
    {
        // Arrange
        var dto = new CreateUserDto { UserName = userName };

        // Act & Assert
        await Assert.ThrowsAsync<ArgumentException>(
            () => _service.CreateUserAsync(dto));
    }
}
```

### Integration Tests

```csharp
public class UsersControllerIntegrationTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;
    private readonly HttpClient _client;

    public UsersControllerIntegrationTests(WebApplicationFactory<Program> factory)
    {
        _factory = factory;
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task GetUsers_ReturnsSuccessStatusCode()
    {
        // Act
        var response = await _client.GetAsync("/api/users");

        // Assert
        response.EnsureSuccessStatusCode();
        Assert.Equal("application/json; charset=utf-8",
            response.Content.Headers.ContentType.ToString());
    }

    [Fact]
    public async Task CreateUser_ReturnsCreatedUser()
    {
        // Arrange
        var newUser = new CreateUserDto
        {
            UserName = "testuser",
            Email = "test@example.com",
            Password = "SecurePass123!"
        };

        // Act
        var response = await _client.PostAsJsonAsync("/api/users", newUser);

        // Assert
        response.EnsureSuccessStatusCode();
        Assert.Equal(HttpStatusCode.Created, response.StatusCode);

        var user = await response.Content.ReadFromJsonAsync<UserDto>();
        Assert.Equal(newUser.UserName, user.UserName);
        Assert.Equal(newUser.Email, user.Email);
    }
}
```

---

## Security Best Practices

### Authentication & Authorization

**JWT Configuration**:
```csharp
// Program.cs
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = builder.Configuration["Jwt:Issuer"],
            ValidAudience = builder.Configuration["Jwt:Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(
                Encoding.UTF8.GetBytes(builder.Configuration["Jwt:Key"]))
        };
    });

builder.Services.AddAuthorization(options =>
{
    options.AddPolicy("AdminOnly", policy => policy.RequireRole("Admin"));
    options.AddPolicy("UserOnly", policy => policy.RequireRole("User", "Admin"));
});
```

**Secure Controllers**:
```csharp
[ApiController]
[Route("api/[controller]")]
[Authorize] // Require authentication
public class UsersController : ControllerBase
{
    [HttpGet]
    [AllowAnonymous] // Public endpoint
    public async Task<ActionResult<IEnumerable<UserDto>>> GetUsers() { }

    [HttpPost]
    [Authorize(Roles = "Admin")] // Admin only
    public async Task<ActionResult<UserDto>> CreateUser(CreateUserDto dto) { }

    [HttpDelete("{id}")]
    [Authorize(Policy = "AdminOnly")] // Policy-based
    public async Task<IActionResult> DeleteUser(int id) { }
}
```

### Password Hashing

```csharp
public class PasswordService
{
    public string HashPassword(string password)
    {
        return BCrypt.Net.BCrypt.HashPassword(password);
    }

    public bool VerifyPassword(string password, string hash)
    {
        return BCrypt.Net.BCrypt.Verify(password, hash);
    }
}
```

### SQL Injection Prevention

✅ **Always use parameterized queries** (EF Core does this automatically):
```csharp
// ✅ Safe - parameterized
var user = await _context.Users
    .FirstOrDefaultAsync(u => u.Email == email);

// ✅ Safe - FromSqlRaw with parameters
var users = await _context.Users
    .FromSqlRaw("SELECT * FROM Users WHERE Email = {0}", email)
    .ToListAsync();
```

❌ **Never concatenate SQL strings**:
```csharp
// ❌ Vulnerable to SQL injection
var query = $"SELECT * FROM Users WHERE Email = '{email}'";
var users = await _context.Users.FromSqlRaw(query).ToListAsync();
```

---

## Configuration

### appsettings.json

```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  },
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Database={{PROJECT_NAME}};Username=postgres;Password=postgres"
  },
  "Jwt": {
    "Key": "your-secret-key-min-32-chars",
    "Issuer": "{{PROJECT_NAME}}",
    "Audience": "{{PROJECT_NAME}}-users",
    "ExpirationMinutes": 60
  },
  "AllowedHosts": "*"
}
```

### Environment-Specific Configuration

**appsettings.Development.json**:
```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Debug",
      "Microsoft.AspNetCore": "Information"
    }
  },
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Database={{PROJECT_NAME}}_dev;Username=postgres;Password=postgres"
  }
}
```

### User Secrets (Development)

```bash
# Initialize user secrets
dotnet user-secrets init --project {{BACKEND_FOLDER}}

# Set a secret
dotnet user-secrets set "Jwt:Key" "your-secret-key" --project {{BACKEND_FOLDER}}

# List secrets
dotnet user-secrets list --project {{BACKEND_FOLDER}}
```

---

## Performance Optimization

### Async/Await

✅ **Always use async/await for I/O operations**:
```csharp
public async Task<User> GetUserAsync(int id)
{
    return await _context.Users.FindAsync(id);
}
```

### Query Optimization

```csharp
// ✅ Include related data
var users = await _context.Users
    .Include(u => u.Posts)
    .ToListAsync();

// ✅ Projection (select only needed fields)
var userDtos = await _context.Users
    .Select(u => new UserDto
    {
        Id = u.Id,
        UserName = u.UserName
    })
    .ToListAsync();

// ✅ AsNoTracking for read-only queries
var users = await _context.Users
    .AsNoTracking()
    .ToListAsync();
```

### Caching

```csharp
// In-memory caching
builder.Services.AddMemoryCache();

// Distributed caching (Redis)
builder.Services.AddStackExchangeRedisCache(options =>
{
    options.Configuration = builder.Configuration.GetConnectionString("Redis");
});

// Usage
public class UserService
{
    private readonly IMemoryCache _cache;

    public async Task<User> GetUserAsync(int id)
    {
        var cacheKey = $"user_{id}";

        if (!_cache.TryGetValue(cacheKey, out User user))
        {
            user = await _repository.GetByIdAsync(id);

            var cacheOptions = new MemoryCacheEntryOptions()
                .SetSlidingExpiration(TimeSpan.FromMinutes(5));

            _cache.Set(cacheKey, user, cacheOptions);
        }

        return user;
    }
}
```

---

## Logging

```csharp
public class UserService
{
    private readonly ILogger<UserService> _logger;

    public async Task<User> GetUserAsync(int id)
    {
        _logger.LogInformation("Getting user with ID: {UserId}", id);

        try
        {
            var user = await _repository.GetByIdAsync(id);

            if (user == null)
            {
                _logger.LogWarning("User not found: {UserId}", id);
            }

            return user;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting user: {UserId}", id);
            throw;
        }
    }
}
```

---

## Common Commands

```bash
# Create new project
dotnet new webapi -n {{PROJECT_NAME}}

# Add package
dotnet add package Microsoft.EntityFrameworkCore
dotnet add package Npgsql.EntityFrameworkCore.PostgreSQL

# Restore packages
dotnet restore

# Build
dotnet build

# Run
dotnet run

# Watch mode (hot reload)
dotnet watch run

# Test
dotnet test

# Publish
dotnet publish -c Release -o ./publish

# Clean
dotnet clean
```

---

## Resources

- [ASP.NET Core Documentation](https://docs.microsoft.com/en-us/aspnet/core/)
- [Entity Framework Core](https://docs.microsoft.com/en-us/ef/core/)
- [C# Coding Conventions](https://docs.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions)
- [.NET API Guidelines](https://github.com/microsoft/api-guidelines/blob/vNext/Guidelines.md)

---

**Last Updated**: {{CURRENT_DATE}}
**Status**: Living Document
