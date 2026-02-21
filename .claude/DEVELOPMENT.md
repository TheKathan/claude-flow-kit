# Development Guide - {{PROJECT_NAME}}

**Date**: {{CURRENT_DATE}}

---

## Development Best Practices

### Before Implementation

1. **Understand Requirements**
   - Read the feature specification
   - Clarify any ambiguities
   - Identify edge cases

2. **Check Existing Code**
   - Search for similar implementations
   - Follow existing patterns
   - Reuse existing utilities

3. **Plan Architecture** (for complex features)
   - Use software-architect agent for complex features
   - Design component boundaries
   - Consider scalability and maintainability

### During Implementation

1. **Follow Code Style**
   - See [Code Style Guidelines](#code-style-guidelines) below
   - Use linters and formatters
   - Write self-documenting code

2. **Security First**
   - Validate all inputs
   - Sanitize user data
   - Prevent SQL injection, XSS, CSRF
   - Use parameterized queries
   - Never trust client input

3. **Error Handling**
   - Handle errors gracefully
   - Provide meaningful error messages
   - Log errors appropriately
   - Don't expose sensitive information in errors

4. **Write Tests as You Go**
   - Write tests immediately after implementation
   - Don't defer testing to later
   - Target 80%+ coverage on critical paths

### After Implementation

1. **Self-Review**
   - Review your own code first
   - Check for security issues
   - Verify error handling
   - Ensure tests pass

2. **Documentation**
   - Add/update docstrings
   - Update README if needed
   - Document any non-obvious behavior
   - Update API documentation

3. **Code Review**
   - Address all review comments
   - Explain your approach if questioned
   - Be open to feedback

---

## Code Style Guidelines

{{#if BACKEND_LANGUAGE includes "C#"}}### C# Code Style

**Standard**: Microsoft C# Coding Conventions

**Key Rules**:
- Use PascalCase for classes, methods, properties
- Use camelCase for parameters, local variables
- Use _camelCase for private fields
- Use IPascalCase for interfaces
- Use 4 spaces for indentation
- Maximum line length: 120 characters
- Always use braces for if/else/for/while (even single line)
- Use var when type is obvious

**Example**:
```csharp
public class UserService : IUserService
{
    private readonly IUserRepository _userRepository;
    private readonly ILogger<UserService> _logger;

    public UserService(
        IUserRepository userRepository,
        ILogger<UserService> logger)
    {
        _userRepository = userRepository;
        _logger = logger;
    }

    public async Task<UserDto> GetUserAsync(int userId)
    {
        if (userId <= 0)
        {
            throw new ArgumentException("User ID must be positive", nameof(userId));
        }

        var user = await _userRepository.GetByIdAsync(userId);

        if (user == null)
        {
            _logger.LogWarning("User not found: {UserId}", userId);
            return null;
        }

        return MapToDto(user);
    }
}
```

**Linting & Formatting**:
```bash
# Format code
dotnet format

# Code analysis
dotnet build /p:EnforceCodeStyleInBuild=true
```
{{/if}}

{{#if BACKEND_LANGUAGE includes "Python"}}### Python Code Style

**Standard**: PEP 8

**Key Rules**:
- Use 4 spaces for indentation (not tabs)
- Maximum line length: 88 characters (Black formatter)
- Use type hints for all function signatures
- Use docstrings for all public functions/classes

**Example**:
```python
from typing import Optional, List

def calculate_total(items: List[dict], tax_rate: float = 0.08) -> float:
    """
    Calculate total price including tax.

    Args:
        items: List of items with 'price' keys
        tax_rate: Tax rate as decimal (default 0.08 = 8%)

    Returns:
        Total price including tax

    Raises:
        ValueError: If items is empty or tax_rate is negative
    """
    if not items:
        raise ValueError("Items list cannot be empty")
    if tax_rate < 0:
        raise ValueError("Tax rate cannot be negative")

    subtotal = sum(item["price"] for item in items)
    return subtotal * (1 + tax_rate)
```

**Linting**:
```bash
# Format code
black {{BACKEND_FOLDER}}/

# Check style
flake8 {{BACKEND_FOLDER}}/

# Type checking
mypy {{BACKEND_FOLDER}}/
```
{{/if}}

{{#if FRONTEND_LANGUAGE includes "TypeScript"}}### TypeScript Code Style

**Standard**: Airbnb TypeScript Style Guide (modified)

**Key Rules**:
- Use 2 spaces for indentation
- Maximum line length: 100 characters
- Always use TypeScript strict mode
- No `any` types (use `unknown` if needed)
- Prefer functional components over class components

**Example**:
```typescript
interface User {
  id: string;
  email: string;
  name: string;
}

interface UserCardProps {
  user: User;
  onClick: (userId: string) => void;
}

export const UserCard: React.FC<UserCardProps> = ({ user, onClick }) => {
  const handleClick = () => {
    onClick(user.id);
  };

  return (
    <div className="user-card" onClick={handleClick}>
      <h3>{user.name}</h3>
      <p>{user.email}</p>
    </div>
  );
};
```

**Linting**:
```bash
# Check style
npm run lint

# Fix auto-fixable issues
npm run lint:fix

# Type checking
npm run type-check
```
{{/if}}

---

## Git Workflow

### Branch Naming

**Format**: `<type>/<description>`

**Types**:
- `feature/` - New features
- `bugfix/` - Bug fixes
- `hotfix/` - Emergency fixes
- `refactor/` - Code refactoring
- `docs/` - Documentation only
- `test/` - Test improvements

**Examples**:
- `feature/user-authentication`
- `bugfix/login-redirect-loop`
- `hotfix/security-patch-auth`

### Commit Messages

**Format**:
```
<type>: <short description>

<detailed description>

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Types**: feat, fix, docs, style, refactor, test, chore

**Examples**:
```
feat: Add user authentication with JWT

- Implement JWT token generation
- Add login and registration endpoints
- Add authentication middleware
- Test coverage: 85%

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

```
fix: Resolve login redirect loop

The login page was redirecting infinitely when user
was already authenticated. Fixed by checking auth
state before redirect.

Fixes #123

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

---

## Testing Guidelines

### Test Coverage Requirements

- **Critical paths**: 100% coverage required
- **Business logic**: 90%+ coverage
- **UI components**: 80%+ coverage
- **Overall target**: 80%+

### Test Structure (AAA Pattern)

```python
# Arrange - Set up test data and preconditions
# Act - Execute the code under test
# Assert - Verify the results

def test_user_registration():
    # Arrange
    user_data = {
        "email": "test@example.com",
        "password": "SecurePass123!"
    }

    # Act
    response = client.post("/api/auth/register", json=user_data)

    # Assert
    assert response.status_code == 201
    assert response.json()["email"] == user_data["email"]
```

### What to Test

**Backend**:
- ✅ Happy path scenarios
- ✅ Error handling (invalid input, missing data)
- ✅ Edge cases (empty lists, null values, boundary conditions)
- ✅ Security (SQL injection, auth bypass)
- ✅ Database operations (create, read, update, delete)
- ✅ API endpoints (request/response format)

{{#if HAS_FRONTEND}}**Frontend**:
- ✅ Component rendering
- ✅ User interactions (clicks, form submissions)
- ✅ Loading and error states
- ✅ Accessibility (ARIA labels, keyboard navigation)
- ✅ Responsive behavior
{{/if}}

---

## Security Best Practices

### Input Validation

- **Always validate** all user inputs
- Use schema validation (Pydantic, Joi, etc.)
- Whitelist allowed values, don't blacklist
- Sanitize HTML content

### Authentication & Authorization

- Use established libraries (don't roll your own crypto)
- Implement rate limiting on auth endpoints
- Use secure password hashing (bcrypt, argon2)
- Implement CSRF protection
- Use HTTPS in production

### Database Security

- **Always use parameterized queries**
- Never concatenate SQL strings with user input
- Implement least-privilege access
- Use database migrations (never manual schema changes)

### Example - SQL Injection Prevention

{{#if BACKEND_LANGUAGE includes "Python"}}❌ **Bad** (Vulnerable to SQL Injection):
```python
query = f"SELECT * FROM users WHERE email = '{email}'"
db.execute(query)
```

✅ **Good** (Safe):
```python
query = "SELECT * FROM users WHERE email = :email"
db.execute(query, {"email": email})
```
{{/if}}

{{#if BACKEND_LANGUAGE includes "C#"}}❌ **Bad** (Vulnerable to SQL Injection):
```csharp
var query = $"SELECT * FROM Users WHERE Email = '{email}'";
var users = await _context.Users.FromSqlRaw(query).ToListAsync();
```

✅ **Good** (Safe - EF Core):
```csharp
// Parameterized LINQ query (recommended)
var user = await _context.Users
    .FirstOrDefaultAsync(u => u.Email == email);

// Parameterized raw SQL
var users = await _context.Users
    .FromSqlRaw("SELECT * FROM Users WHERE Email = {0}", email)
    .ToListAsync();
```
{{/if}}

{{#if BACKEND_LANGUAGE includes "Node"}}❌ **Bad** (Vulnerable to SQL Injection):
```javascript
const query = `SELECT * FROM users WHERE email = '${email}'`;
db.query(query);
```

✅ **Good** (Safe):
```javascript
const query = 'SELECT * FROM users WHERE email = $1';
db.query(query, [email]);
```
{{/if}}

---

## Performance Guidelines

### Backend Performance

1. **Database Optimization**
   - Add indexes on frequently queried columns
   - Use select_related/prefetch_related (ORM)
   - Avoid N+1 queries
   - Use pagination for large result sets

2. **Caching**
   - Cache expensive computations
   - Cache database queries
   - Set appropriate cache TTL
   - Invalidate cache on data changes

3. **Async Operations**
   - Use async/await for I/O operations
   - Don't block the event loop
   - Use background tasks for long operations

{{#if HAS_FRONTEND}}### Frontend Performance

1. **Code Splitting**
   - Lazy load routes
   - Dynamic imports for large components
   - Split vendor bundles

2. **Optimization**
   - Memoize expensive computations (useMemo)
   - Prevent unnecessary re-renders (memo, useCallback)
   - Optimize images (WebP, lazy loading)
   - Use virtual scrolling for long lists

3. **Bundle Size**
   - Monitor bundle size
   - Tree shake unused code
   - Avoid importing entire libraries
{{/if}}

---

## Debugging Tips

{{#if USES_DOCKER}}### Docker Debugging

```bash
# View logs
docker-compose logs -f backend

# Enter container shell
docker-compose exec backend bash

# Check container status
docker-compose ps

# Restart specific service
docker-compose restart backend
```
{{/if}}

### Backend Debugging

- Use debugger breakpoints (pdb, ipdb)
- Add strategic logging
- Check error logs
- Use profiling tools for performance issues

{{#if HAS_FRONTEND}}### Frontend Debugging

- Use React DevTools
- Check browser console
- Use network tab for API issues
- Use Lighthouse for performance audit
{{/if}}

---

## Common Pitfalls

### Backend

- ❌ Not handling errors properly
- ❌ Exposing sensitive data in API responses
- ❌ Not validating user input
- ❌ Using blocking I/O in async code
- ❌ Not using database transactions
- ❌ Hardcoding configuration values

{{#if HAS_FRONTEND}}### Frontend

- ❌ Not handling loading/error states
- ❌ Missing accessibility attributes
- ❌ Not cleaning up useEffect subscriptions
- ❌ Mutating state directly
- ❌ Not handling mobile/responsive design
- ❌ Using `any` type in TypeScript
{{/if}}

---

## Resources

### Documentation
- [Architecture](ARCHITECTURE.md) - System architecture
- [Workflow Guide](../docs/WORKFLOW_GUIDE.md) - Development workflow
- [Testing Guide](../docs/TESTING_GUIDE.md) - Testing standards

### External Resources
{{#if BACKEND_FRAMEWORK includes "FastAPI"}}- [FastAPI Documentation](https://fastapi.tiangolo.com/){{/if}}
{{#if BACKEND_FRAMEWORK includes "ASP.NET"}}- [ASP.NET Core Documentation](https://docs.microsoft.com/en-us/aspnet/core/)
- [Entity Framework Core Documentation](https://docs.microsoft.com/en-us/ef/core/)
- [C# Coding Conventions](https://docs.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions){{/if}}
{{#if BACKEND_FRAMEWORK includes "Express"}}- [Express.js Documentation](https://expressjs.com/){{/if}}
{{#if BACKEND_FRAMEWORK includes "Django"}}- [Django Documentation](https://docs.djangoproject.com/){{/if}}
{{#if FRONTEND_FRAMEWORK includes "Next"}}- [Next.js Documentation](https://nextjs.org/docs){{/if}}
{{#if FRONTEND_FRAMEWORK includes "React"}}- [React Documentation](https://react.dev/){{/if}}
{{#if BACKEND_LANGUAGE includes "Python"}}- [Python PEP 8 Style Guide](https://peps.python.org/pep-0008/){{/if}}
{{#if FRONTEND_LANGUAGE includes "TypeScript"}}- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html){{/if}}

---

**Last Updated**: {{CURRENT_DATE}}
**Status**: Living Document
