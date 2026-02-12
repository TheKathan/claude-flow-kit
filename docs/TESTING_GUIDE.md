# Testing Guide - {{PROJECT_NAME}}

**Date**: {{CURRENT_DATE}}

---

## Testing Philosophy

### Core Principles

1. **Tests are documentation** - Tests explain how code should behave
2. **Tests enable refactoring** - Good tests allow confident code changes
3. **Tests catch regressions** - Automated tests prevent bugs from returning
4. **Tests first, not last** - Write tests immediately after implementation

### Coverage Requirements

- **Critical paths**: 100% coverage required
- **Business logic**: 90%+ coverage
- **UI components**: 80%+ coverage
- **Overall target**: 80%+ coverage

---

## Testing Stack

{{#if BACKEND_LANGUAGE includes "C#"}}### Backend Testing (.NET)

**Framework**: xUnit (or NUnit, MSTest)

**Libraries**:
- `xunit` - Test framework
- `xunit.runner.visualstudio` - Test runner
- `Moq` - Mocking framework
- `FluentAssertions` - Assertion library
- `Microsoft.AspNetCore.Mvc.Testing` - Integration testing
- `Bogus` - Test data generation

**Installation**:
```bash
dotnet add package xunit
dotnet add package xunit.runner.visualstudio
dotnet add package Moq
dotnet add package FluentAssertions
dotnet add package Microsoft.AspNetCore.Mvc.Testing
dotnet add package Bogus
```
{{/if}}

{{#if BACKEND_LANGUAGE includes "Python"}}### Backend Testing (Python)

**Framework**: pytest

**Libraries**:
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking utilities
- `httpx` - HTTP client for API testing
- `faker` - Test data generation

**Installation**:
```bash
pip install pytest pytest-asyncio pytest-cov pytest-mock httpx faker
```
{{/if}}

{{#if HAS_FRONTEND && FRONTEND_FRAMEWORK includes "React"}}### Frontend Testing (React)

**Framework**: Jest / Vitest + React Testing Library

**Libraries**:
- `@testing-library/react` - Component testing
- `@testing-library/jest-dom` - Custom matchers
- `@testing-library/user-event` - User interaction simulation
- `jest` or `vitest` - Test runner
- `@testing-library/react-hooks` - Hook testing

**Installation**:
```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event vitest
```
{{/if}}

---

## Test Structure

### AAA Pattern (Arrange-Act-Assert)

All tests should follow this pattern:

```python
def test_user_registration():
    # Arrange - Set up test data and preconditions
    user_data = {
        "email": "test@example.com",
        "password": "SecurePass123!"
    }

    # Act - Execute the code under test
    response = client.post("/api/auth/register", json=user_data)

    # Assert - Verify the results
    assert response.status_code == 201
    assert response.json()["email"] == user_data["email"]
    assert "password" not in response.json()
```

### Test Organization

```
tests/
├── unit/                   # Unit tests (isolated, fast)
│   ├── test_models.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/            # Integration tests (multiple components)
│   ├── test_api.py
│   └── test_database.py
├── e2e/                    # End-to-end tests (full workflow)
│   └── test_user_flow.py
├── fixtures/               # Shared test fixtures
│   └── conftest.py
└── __init__.py
```

---

{{#if BACKEND_LANGUAGE includes "Python"}}## Backend Testing (Python)

### Basic Test Example

```python
import pytest
from app.services.user_service import UserService
from app.models import User

class TestUserService:
    @pytest.fixture
    def user_service(self):
        """Fixture providing a UserService instance."""
        return UserService()

    @pytest.fixture
    def sample_user_data(self):
        """Fixture providing sample user data."""
        return {
            "email": "test@example.com",
            "username": "testuser",
            "password": "SecurePass123!"
        }

    def test_create_user_success(self, user_service, sample_user_data):
        """Test successful user creation."""
        # Arrange
        data = sample_user_data

        # Act
        user = user_service.create_user(data)

        # Assert
        assert user.email == data["email"]
        assert user.username == data["username"]
        assert user.password != data["password"]  # Should be hashed

    def test_create_user_duplicate_email(self, user_service, sample_user_data):
        """Test user creation with duplicate email."""
        # Arrange
        user_service.create_user(sample_user_data)

        # Act & Assert
        with pytest.raises(ValueError, match="Email already exists"):
            user_service.create_user(sample_user_data)
```

### Testing Async Functions

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Test async function."""
    # Arrange
    data = {"key": "value"}

    # Act
    result = await async_function(data)

    # Assert
    assert result["success"] is True
```

### Testing Database Operations

```python
import pytest
from sqlalchemy.orm import Session

@pytest.fixture
def db_session():
    """Create a test database session."""
    # Create test database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    # Create session
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    # Cleanup
    session.close()
    Base.metadata.drop_all(engine)

def test_user_crud(db_session: Session):
    """Test user CRUD operations."""
    # Create
    user = User(email="test@example.com", username="testuser")
    db_session.add(user)
    db_session.commit()

    # Read
    found = db_session.query(User).filter_by(email="test@example.com").first()
    assert found.username == "testuser"

    # Update
    found.username = "newusername"
    db_session.commit()
    assert found.username == "newusername"

    # Delete
    db_session.delete(found)
    db_session.commit()
    assert db_session.query(User).count() == 0
```

### Mocking External Services

```python
import pytest
from unittest.mock import Mock, patch

def test_external_api_call():
    """Test function that calls external API."""
    # Arrange
    mock_response = Mock()
    mock_response.json.return_value = {"data": "mocked"}
    mock_response.status_code = 200

    # Act
    with patch('requests.get', return_value=mock_response):
        result = fetch_data_from_api()

    # Assert
    assert result["data"] == "mocked"
```

### Testing API Endpoints

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_user_endpoint():
    """Test user creation endpoint."""
    user_data = {
        "email": "test@example.com",
        "password": "SecurePass123!"
    }

    response = client.post("/api/users", json=user_data)

    assert response.status_code == 201
    assert response.json()["email"] == user_data["email"]
    assert "password" not in response.json()
```
{{/if}}

{{#if HAS_FRONTEND && FRONTEND_FRAMEWORK includes "React"}}## Frontend Testing (React)

### Component Testing

```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from './Button';

describe('Button', () => {
  describe('Rendering', () => {
    it('should render with text', () => {
      render(<Button>Click me</Button>);
      expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument();
    });

    it('should render with disabled state', () => {
      render(<Button disabled>Click me</Button>);
      expect(screen.getByRole('button')).toBeDisabled();
    });
  });

  describe('User Interactions', () => {
    it('should call onClick when clicked', async () => {
      const user = userEvent.setup();
      const onClick = jest.fn();

      render(<Button onClick={onClick}>Click me</Button>);

      await user.click(screen.getByRole('button'));

      expect(onClick).toHaveBeenCalledTimes(1);
    });

    it('should not call onClick when disabled', async () => {
      const user = userEvent.setup();
      const onClick = jest.fn();

      render(<Button onClick={onClick} disabled>Click me</Button>);

      await user.click(screen.getByRole('button'));

      expect(onClick).not.toHaveBeenCalled();
    });
  });

  describe('Accessibility', () => {
    it('should be keyboard navigable', async () => {
      const user = userEvent.setup();
      const onClick = jest.fn();

      render(<Button onClick={onClick}>Click me</Button>);

      const button = screen.getByRole('button');
      button.focus();

      await user.keyboard('{Enter}');

      expect(onClick).toHaveBeenCalled();
    });
  });
});
```

### Testing Hooks

```typescript
import { renderHook, act } from '@testing-library/react';
import { useCounter } from './useCounter';

describe('useCounter', () => {
  it('should initialize with default value', () => {
    const { result } = renderHook(() => useCounter());
    expect(result.current.count).toBe(0);
  });

  it('should increment count', () => {
    const { result } = renderHook(() => useCounter());

    act(() => {
      result.current.increment();
    });

    expect(result.current.count).toBe(1);
  });

  it('should decrement count', () => {
    const { result } = renderHook(() => useCounter(5));

    act(() => {
      result.current.decrement();
    });

    expect(result.current.count).toBe(4);
  });
});
```

### Testing with Context

```typescript
import { render, screen } from '@testing-library/react';
import { AuthProvider } from './AuthContext';
import { ProtectedComponent } from './ProtectedComponent';

describe('ProtectedComponent', () => {
  it('should render for authenticated user', () => {
    const mockUser = { id: '1', name: 'Test User' };

    render(
      <AuthProvider value={{ user: mockUser, isAuthenticated: true }}>
        <ProtectedComponent />
      </AuthProvider>
    );

    expect(screen.getByText('Welcome, Test User')).toBeInTheDocument();
  });

  it('should redirect for unauthenticated user', () => {
    render(
      <AuthProvider value={{ user: null, isAuthenticated: false }}>
        <ProtectedComponent />
      </AuthProvider>
    );

    expect(screen.getByText('Please log in')).toBeInTheDocument();
  });
});
```

### Mocking API Calls

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { UserList } from './UserList';

const server = setupServer(
  rest.get('/api/users', (req, res, ctx) => {
    return res(
      ctx.json([
        { id: '1', name: 'User 1' },
        { id: '2', name: 'User 2' },
      ])
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('UserList', () => {
  it('should display users after loading', async () => {
    render(<UserList />);

    expect(screen.getByText('Loading...')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('User 1')).toBeInTheDocument();
      expect(screen.getByText('User 2')).toBeInTheDocument();
    });
  });

  it('should display error message on failure', async () => {
    server.use(
      rest.get('/api/users', (req, res, ctx) => {
        return res(ctx.status(500));
      })
    );

    render(<UserList />);

    await waitFor(() => {
      expect(screen.getByText('Error loading users')).toBeInTheDocument();
    });
  });
});
```
{{/if}}

---

## Running Tests

{{#if USES_DOCKER}}### In Docker (Recommended)

```bash
# Backend tests
docker-compose exec backend pytest

# With coverage
docker-compose exec backend pytest --cov=app --cov-report=term-missing

# Specific test file
docker-compose exec backend pytest tests/test_user.py

# Specific test function
docker-compose exec backend pytest tests/test_user.py::test_create_user

{{#if HAS_FRONTEND}}# Frontend tests
docker-compose exec frontend npm test

# With coverage
docker-compose exec frontend npm test -- --coverage

# Watch mode
docker-compose exec frontend npm test -- --watch
{{/if}}
```
{{/if}}

### Locally

```bash
{{#if BACKEND_LANGUAGE includes "Python"}}# Backend tests
pytest

# With coverage
pytest --cov=app --cov-report=html
{{/if}}

{{#if HAS_FRONTEND}}# Frontend tests
npm test

# With coverage
npm test -- --coverage
{{/if}}
```

---

## Coverage Reports

### Viewing Coverage

{{#if BACKEND_LANGUAGE includes "Python"}}**Backend (Python)**:
```bash
# Generate HTML report
pytest --cov=app --cov-report=html

# Open report
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```
{{/if}}

{{#if HAS_FRONTEND}}**Frontend (JavaScript/TypeScript)**:
```bash
# Generate coverage report
npm test -- --coverage

# Open report
open coverage/lcov-report/index.html
```
{{/if}}

### Coverage Thresholds

Configure minimum coverage thresholds:

{{#if BACKEND_LANGUAGE includes "Python"}}**pytest.ini**:
```ini
[tool:pytest]
addopts =
    --cov=app
    --cov-report=term-missing
    --cov-fail-under=80
```
{{/if}}

{{#if HAS_FRONTEND}}**jest.config.js**:
```javascript
module.exports = {
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
```
{{/if}}

---

## Continuous Integration

### CI Pipeline

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      {{#if USES_DOCKER}}- name: Run tests in Docker
        run: |
          docker-compose up -d
          docker-compose exec -T backend pytest --cov=app
          {{#if HAS_FRONTEND}}docker-compose exec -T frontend npm test -- --coverage{{/if}}
      {{else}}- name: Run tests
        run: |
          {{BACKEND_TEST_COMMAND}}
          {{#if HAS_FRONTEND}}{{FRONTEND_TEST_COMMAND}}{{/if}}
      {{/if}}

      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

## Best Practices

### DO

✅ Write tests immediately after implementation
✅ Test edge cases and error conditions
✅ Use descriptive test names
✅ Follow AAA pattern (Arrange-Act-Assert)
✅ Mock external dependencies
✅ Keep tests fast and isolated
✅ Test behavior, not implementation
✅ Aim for 80%+ coverage

### DON'T

❌ Skip testing error cases
❌ Test implementation details
❌ Make tests dependent on each other
❌ Use real external services in tests
❌ Ignore failing tests
❌ Write tests just for coverage
❌ Test third-party library code

---

## Troubleshooting

### Tests Failing Randomly

**Possible causes**:
1. Tests dependent on each other
2. Shared state between tests
3. Timing issues (race conditions)
4. External service dependencies

**Solutions**:
- Ensure test isolation
- Clean up after each test
- Use proper async/await
- Mock external services

### Slow Tests

**Optimization strategies**:
1. Use in-memory databases for testing
2. Mock slow external calls
3. Run tests in parallel
4. Reduce test data size

### Coverage Not Updating

```bash
# Clean coverage data
rm -rf .coverage htmlcov/

# Regenerate coverage
pytest --cov=app --cov-report=html
```

---

**Last Updated**: {{CURRENT_DATE}}
**Status**: Living Document
