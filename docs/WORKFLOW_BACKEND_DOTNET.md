# Backend .NET Workflow - {{PROJECT_NAME}}

**Date**: {{CURRENT_DATE}}
**Status**: ✅ ACTIVE
**Version**: 2.0 - .NET Backend Worktree-Based Workflow

---

## Overview

This guide covers the 13-step worktree-based workflow for **.NET/ASP.NET Core backend development**. This workflow integrates:
- **Worktree isolation** (each feature gets its own worktree, with Docker environment for Docker projects)
- **Architectural planning** (optional for complex features)
- **Automated test writing** (mandatory with xUnit)
- **Quality gates** (tests + code review + integration tests)
- **Merge conflict resolution** (automated before merge)
- **Automatic merge & cleanup** (after all gates pass)

---

## Workflow Architecture

### Core Principle

**Isolated, Test-Driven Quality with Automated Gates**

Every backend feature:
1. Gets its own **isolated worktree** (with Docker environment for Docker projects)
2. Goes through **mandatory quality gates** before being pushed
3. Has **conflicts resolved automatically** before merge
4. Is **merged and cleaned up automatically** after approval

**Quality Gates**:
1. **Unit Test Gate** (Step 5) - All xUnit tests must pass with 80%+ coverage
2. **Code Review Gate** (Step 6) - Code must be approved by backend reviewer
3. **Integration Test Gate** (Step 8) - End-to-end tests must pass
4. **Conflict Resolution Gate** (Step 10) - Merge conflicts must be resolved
5. **Final Integration Gate** (Step 11) - Final tests with base branch merged must pass

---

## Agent System

**Specialized Agents for .NET Backend**:

| Agent | Type | Scope | Role | Model |
|-------|------|-------|------|-------|
| software-architect | Architect | All | Design architecture (optional) | opus |
| **worktree-manager** | **Manager** | **All** | **Create worktrees, merge, cleanup** | sonnet |
| **dotnet-developer** | **Developer** | **Backend** | **Implement .NET/ASP.NET Core features** | sonnet |
| **dotnet-test-specialist** | **Tester** | **Backend** | **Write xUnit tests** | sonnet |
| **backend-code-reviewer** | **Reviewer** | **Backend** | **Review backend code** | sonnet/opus |
| integration-tester | Tester | All | Execute all tests and enforce gates | haiku |
| **docker-debugger** | **Debugger** | **All** | **Diagnose and fix Docker issues** *(Docker projects only)* | sonnet |
| **merge-conflict-resolver** | **Resolver** | **All** | **Detect and resolve merge conflicts** | opus |

---

## 13-Step .NET Backend Workflow

```
Step 0:  [OPTIONAL] software-architect      → Design architecture
Step 1:  worktree-manager                   → Create worktree
Step 1b: [DOCKER/ON-FAILURE] docker-debugger → Debug setup issues
Step 2:  dotnet-developer                   → Implement .NET/ASP.NET Core feature
Step 3:  dotnet-test-specialist             → Write xUnit tests
Step 4:  dotnet-developer                   → Commit code + tests
Step 5:  integration-tester                 → Run xUnit unit tests [GATE]
Step 5b: [DOCKER/ON-FAILURE] docker-debugger → Debug test issues
Step 6:  backend-code-reviewer              → Review code [GATE]
Step 7:  dotnet-developer                   → Fix if needed (loop to 5-6)
Step 8:  integration-tester                 → Run E2E tests [GATE]
Step 8b: [DOCKER/ON-FAILURE] docker-debugger → Debug E2E issues
Step 9:  dotnet-developer                   → Push to feature branch
Step 10: merge-conflict-resolver            → Resolve conflicts [GATE]
Step 11: integration-tester                 → Final integration test [GATE]
Step 11b: [DOCKER/ON-FAILURE] docker-debugger → Debug integration issues
Step 12: worktree-manager                   → Merge to base branch, push
Step 13: worktree-manager                   → Cleanup worktree
Step 13b: [DOCKER/ON-FAILURE] docker-debugger → Force cleanup
```

> `b` steps only activate for Docker projects when container failures occur.

---

## Step-by-Step Guide

### Step 0: Architectural Planning (Optional)

**When to Use**:
- ✅ New API services or major endpoints
- ✅ Database schema changes
- ✅ Complex features with multiple integration points
- ✅ Major refactoring

**When to Skip**:
- ❌ Bug fixes
- ❌ Minor tweaks
- ❌ Simple CRUD operations

**Agent**: software-architect (opus model)

**Output**: Architecture design document with:
- Context and requirements
- Proposed ASP.NET Core architecture
- Database schema (Entity Framework Core models)
- API endpoint design
- Design decisions and trade-offs
- Implementation plan

---

### Step 1: Create Worktree

**Agent**: worktree-manager

**Action**: Create isolated worktree

**Commands**:
```bash
# Agent runs:
bash scripts/worktree_create.sh feature-name "Feature description"
```

**Output**:
- Worktree created at `.worktrees/feature-name`
- Branch created: `feature/feature-name`

> **Note**: The worktree branches from whichever branch is currently checked out. At Step 12, the feature branch will be merged back to that same base branch.

> *(Docker projects only)* Docker containers start with unique ports, providing a completely isolated .NET environment with a separate database (SQL Server/PostgreSQL) per worktree — no shared resources.

**On Failure** (Step 1b) *(Docker projects only)*:
- docker-debugger diagnoses port conflicts, container issues
- Fixes automatically if possible
- Reports if manual intervention needed

---

### Step 2: Implement Feature

**Agent**: dotnet-developer

**Responsibilities**:
- Write clean, maintainable C# code
- Follow .NET coding conventions
- Use nullable reference types
- Write XML documentation comments
- Follow ASP.NET Core patterns (dependency injection, middleware)
- Use Entity Framework Core for database operations
- Handle errors gracefully with exception filters
- Place scripts in `scripts/` folder

**.NET-Specific Patterns**:
```csharp
// ASP.NET Core controller with dependency injection
using Microsoft.AspNetCore.Mvc;
using MyProject.Services;
using MyProject.Models;
using MyProject.DTOs;

namespace MyProject.Controllers;

[ApiController]
[Route("api/[controller]")]
public class UsersController : ControllerBase
{
    private readonly IUserService _userService;
    private readonly ILogger<UsersController> _logger;

    public UsersController(IUserService userService, ILogger<UsersController> logger)
    {
        _userService = userService;
        _logger = logger;
    }

    /// <summary>
    /// Creates a new user.
    /// </summary>
    /// <param name="userDto">User creation data</param>
    /// <returns>Created user data</returns>
    /// <response code="201">User created successfully</response>
    /// <response code="409">User already exists</response>
    [HttpPost]
    [ProducesResponseType(typeof(UserResponseDto), StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status409Conflict)]
    public async Task<ActionResult<UserResponseDto>> CreateUser([FromBody] CreateUserDto userDto)
    {
        try
        {
            var user = await _userService.CreateUserAsync(userDto);
            return CreatedAtAction(nameof(GetUser), new { id = user.Id }, user);
        }
        catch (DuplicateUserException ex)
        {
            _logger.LogWarning(ex, "Attempt to create duplicate user: {Email}", userDto.Email);
            return Conflict(new { message = ex.Message });
        }
    }

    [HttpGet("{id}")]
    public async Task<ActionResult<UserResponseDto>> GetUser(int id)
    {
        var user = await _userService.GetUserByIdAsync(id);
        return user == null ? NotFound() : Ok(user);
    }
}
```

**DO NOT commit yet** - tests need to be written first

---

### Step 3: Write Tests

**Agent**: dotnet-test-specialist

**Responsibilities**:
- Analyze .NET implementation
- Design test scenarios (happy path, errors, edge cases, security)
- Implement xUnit tests with fixtures and Moq
- Target 80%+ coverage
- Document test purpose

**.NET Test Structure** (xUnit with AAA Pattern):
```csharp
using Xunit;
using Moq;
using FluentAssertions;
using MyProject.Controllers;
using MyProject.Services;
using MyProject.DTOs;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;

namespace MyProject.Tests.Controllers;

public class UsersControllerTests
{
    private readonly Mock<IUserService> _mockUserService;
    private readonly Mock<ILogger<UsersController>> _mockLogger;
    private readonly UsersController _controller;

    public UsersControllerTests()
    {
        _mockUserService = new Mock<IUserService>();
        _mockLogger = new Mock<ILogger<UsersController>>();
        _controller = new UsersController(_mockUserService.Object, _mockLogger.Object);
    }

    [Fact]
    public async Task CreateUser_ValidData_ReturnsCreatedResult()
    {
        // Arrange
        var createDto = new CreateUserDto
        {
            Email = "newuser@example.com",
            Username = "newuser",
            Password = "SecurePass123!"
        };

        var expectedUser = new UserResponseDto
        {
            Id = 1,
            Email = createDto.Email,
            Username = createDto.Username
        };

        _mockUserService
            .Setup(s => s.CreateUserAsync(It.IsAny<CreateUserDto>()))
            .ReturnsAsync(expectedUser);

        // Act
        var result = await _controller.CreateUser(createDto);

        // Assert
        var createdResult = result.Result.Should().BeOfType<CreatedAtActionResult>().Subject;
        createdResult.StatusCode.Should().Be(201);
        var returnedUser = createdResult.Value.Should().BeOfType<UserResponseDto>().Subject;
        returnedUser.Email.Should().Be(createDto.Email);
        returnedUser.Username.Should().Be(createDto.Username);
    }

    [Fact]
    public async Task CreateUser_DuplicateEmail_ReturnsConflict()
    {
        // Arrange
        var createDto = new CreateUserDto
        {
            Email = "existing@example.com",
            Username = "newuser",
            Password = "SecurePass123!"
        };

        _mockUserService
            .Setup(s => s.CreateUserAsync(It.IsAny<CreateUserDto>()))
            .ThrowsAsync(new DuplicateUserException("User already exists"));

        // Act
        var result = await _controller.CreateUser(createDto);

        // Assert
        result.Result.Should().BeOfType<ConflictObjectResult>();
    }
}
```

**Test Coverage Requirements**:
- Unit tests: All services and methods
- Controller tests: All endpoints (success + error cases)
- Repository tests: CRUD operations with Entity Framework Core
- Security tests: Authentication, authorization, input validation
- Edge cases: Null inputs, invalid types, boundary conditions

---

### Step 4: Commit Code + Tests

**Agent**: dotnet-developer

**Commands**:
```bash
# With Docker:
docker-compose exec backend dotnet format
docker-compose exec backend dotnet format --verify-no-changes
docker-compose exec backend dotnet build

# Without Docker:
dotnet format
dotnet format --verify-no-changes
dotnet build

# Commit
git add .
git commit -m "feat: add user creation endpoint

- Implement POST /api/users endpoint with ASP.NET Core
- Add CreateUserDto and UserResponseDto data transfer objects
- Add User entity with Entity Framework Core
- Implement UserService with duplicate email check
- Add comprehensive xUnit tests with Moq (unit + integration)
- Test coverage: 85%"
```

**Commit Format**:
```
<type>: <short description>

- Implementation details
- Test coverage: X%
```

**Types**: feat, fix, docs, style, refactor, test, chore

---

### Step 5: Run Unit Tests ⚠️ GATE

**Agent**: integration-tester (haiku model)

**Commands**:
```bash
# With Docker:
docker-compose exec backend dotnet test --collect:"XPlat Code Coverage" --results-directory ./TestResults /p:CollectCoverage=true /p:CoverletOutputFormat=cobertura
docker-compose exec backend reportgenerator -reports:./TestResults/*/coverage.cobertura.xml -targetdir:./TestResults/CoverageReport -reporttypes:Html

# Without Docker:
dotnet test --collect:"XPlat Code Coverage" --results-directory ./TestResults /p:CollectCoverage=true /p:CoverletOutputFormat=cobertura
reportgenerator -reports:./TestResults/*/coverage.cobertura.xml -targetdir:./TestResults/CoverageReport -reporttypes:Html
```

**Pass Criteria**:
- All xUnit tests pass (0 failures, 0 errors)
- Coverage ≥ 80%
- No critical build warnings
- dotnet format passes

**On Fail**:
- Workflow BLOCKED
- Orchestrator invokes dotnet-developer to fix
- Returns to Step 5 after fix

**On Docker Failure** (Step 5b) *(Docker projects only)*:
- docker-debugger diagnoses container issues
- Fixes and retries test execution

---

### Step 6: Code Review ⚠️ GATE

**Agent**: backend-code-reviewer (sonnet, opus for critical)

**Review Criteria**:
- ✅ **Security** (SQL injection, auth bypass, input validation)
- ✅ **Performance** (query optimization, async patterns, N+1 queries)
- ✅ **Best Practices** (.NET conventions, nullable reference types, XML docs)
- ✅ **Architecture** (ASP.NET Core patterns, dependency injection, service layer)
- ✅ **Database** (Entity Framework Core best practices, migrations, constraints)
- ✅ **API Design** (RESTful conventions, status codes, response models)

**.NET-Specific Checks**:
- Nullable reference types enabled and used correctly
- XML documentation on public APIs
- Async/await used correctly (no Task.Wait() or .Result)
- Dependency injection configured properly
- Entity Framework Core DbContext scoped correctly
- Exception handling with proper filters
- No SQL injection vulnerabilities (using parameterized queries)
- IDisposable implemented where needed

**Outcomes**:
- ✅ **APPROVED** - Continue to Step 8
- ❌ **CHANGES REQUESTED** - Go to Step 7

---

### Step 7: Fix Issues

**Agent**: dotnet-developer

**Responsibilities**:
- Address ALL review issues
- Make targeted fixes
- Re-format with dotnet format
- Rebuild to check for warnings
- Commit fixes
- Return to Step 5 (re-test) → Step 6 (re-review)

**Max Cycles**: 3 (if stuck, reassess approach)

---

### Step 8: Run Integration Tests ⚠️ GATE

**Agent**: integration-tester (haiku model)

**Commands**:
```bash
# With Docker:
docker-compose exec backend dotnet test --filter "Category=Integration"
docker-compose exec backend dotnet run --project tests/IntegrationTests

# Check API health:
curl http://localhost:5000/health

# Without Docker:
dotnet test --filter "Category=Integration"
dotnet run --project tests/IntegrationTests

# Check API health:
curl http://localhost:5000/health
```

**Pass Criteria**:
- All E2E tests pass
- API responds correctly to all test scenarios
- Database operations work end-to-end
- No integration failures

**On Fail**:
- Workflow BLOCKED
- dotnet-developer fixes issues
- May loop back to Step 5-6 if code changes needed

**On Docker Failure** (Step 8b) *(Docker projects only)*:
- docker-debugger diagnoses E2E test issues
- Fixes and retries

---

### Step 9: Push Feature Branch

**Agent**: dotnet-developer

**Commands**:
```bash
git push -u origin HEAD
```

**Verification**:
- Branch pushed successfully to remote
- Remote tracking set up
- CI/CD pipeline triggered (if configured)

---

### Step 10: Resolve Merge Conflicts ⚠️ GATE

**Agent**: merge-conflict-resolver (opus model)

**Actions**:
1. Pull latest base branch
2. Merge base branch into feature branch
3. Detect conflicts
4. Resolve automatically (or request manual review for complex cases)
5. Commit resolution
6. Push resolved feature branch to remote

```bash
# Push after conflict resolution:
git push origin HEAD --force-with-lease
```

**.NET-Specific Conflict Types**:
- **Simple**: usings, whitespace, formatting → auto-resolve
- **Models**: Entity Framework models → integrate both, check migrations
- **Controllers**: Different API endpoints → integrate both
- **Logic**: Different implementations of same method → request manual review
- **Project files**: .csproj changes → carefully merge dependencies
- **Complex**: Fundamental conflicts in business logic → request manual review

**Outcomes**:
- ✅ **RESOLVED** - Continue to Step 11
- ⚠️ **MANUAL REVIEW NEEDED** - Workflow PAUSED
- ❌ **FAILED** - Workflow BLOCKED

---

### Step 11: Final Integration Test ⚠️ GATE

**Agent**: integration-tester (haiku model)

**Purpose**: Verify everything works with base branch merged

**Commands**:
```bash
# With Docker:
docker-compose exec backend dotnet test --collect:"XPlat Code Coverage"
docker-compose exec backend dotnet build

# Without Docker:
dotnet test --collect:"XPlat Code Coverage"
dotnet build
```

**Pass Criteria**:
- All tests pass after merge
- No new build warnings
- Solution builds successfully

**On Fail**:
- Workflow BLOCKED
- dotnet-developer fixes merge issues

**On Docker Failure** (Step 11b) *(Docker projects only)*:
- docker-debugger diagnoses issues
- Fixes and retries

---

### Step 12: Merge to Base Branch

**Agent**: worktree-manager

**Actions**:
1. Verify all gates passed
2. Merge feature branch to base branch
3. Push base branch to remote
4. Update worktree registry

**Commands**:
```bash
# Agent runs:
python scripts/worktree_merge.py <worktree-id>
```

**Output**:
- Feature merged to base branch
- Base branch pushed to remote
- Ready for cleanup

---

### Step 13: Cleanup

**Agent**: worktree-manager

**Actions**:
1. Delete worktree
2. Update registry

*(Docker projects only)* Also stops and removes Docker containers, and optionally cleans up images/volumes.

**Commands**:
```bash
# Agent runs:
bash scripts/worktree_cleanup.sh <worktree-id>
```

**On Failure** (Step 13b) *(Docker projects only)*:
- docker-debugger force cleanups stuck resources
- Removes containers, images, volumes
- Ensures clean state

---

## Workflow Variants

### Standard Workflow (11 steps) ⭐ Most Common

**Steps**: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13

**Use For**: Regular .NET backend features, enhancements (80% of work)
**Time**: 25-35 minutes
**Cost**: Medium

### Full Workflow (13 steps)

**Steps**: 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13

**Use For**: New .NET services, architectural changes, database schema changes
**Time**: 35-50 minutes
**Cost**: High

### Hotfix Workflow (9 steps) ⚡

**Steps**: 1 → 2 → 4 → 5 → 6 → 7 → 9 → 10 → 12 → 13

**Use For**: Production bugs, urgent .NET fixes
**Time**: 15-20 minutes
**Cost**: Low
**Note**: Skips test writing (assumes tests exist), skips E2E tests; includes fix loop (Step 7)

### Test-Only Workflow (7 steps)

**Steps**: 1 → 3 → 4 → 5 → 9 → 12 → 13

**Use For**: Adding tests to existing .NET code, improving coverage
**Time**: 15-20 minutes
**Cost**: Low
**Note**: Skips implementation and E2E tests

### Docs-Only Workflow (5 steps)

**Steps**: 1 → 2 → 9 → 12 → 13

**Use For**: Documentation changes only
**Time**: 10-15 minutes
**Cost**: Very Low
**Note**: Skips testing and review; for documentation PRs only

---

## .NET Development Best Practices

### DO

✅ Enable nullable reference types
✅ Write XML documentation for public APIs
✅ Use async/await for I/O operations
✅ Follow dependency injection patterns
✅ Use Entity Framework Core migrations
✅ Implement proper exception handling
✅ Use data transfer objects (DTOs)
✅ Write xUnit tests with Moq for mocking
✅ Use FluentAssertions for readable assertions
✅ Follow .NET naming conventions

### DON'T

❌ Use Task.Wait() or .Result (causes deadlocks)
❌ Ignore compiler warnings
❌ Hardcode connection strings
❌ Skip XML documentation
❌ Use DbContext outside of scoped lifetime
❌ Return entities directly from API (use DTOs)
❌ Commit without running dotnet format
❌ Skip error handling
❌ Use raw SQL without parameterization
❌ Ignore CA (code analysis) warnings

---

## .NET Tools and Commands

### Building and Formatting
```bash
# With Docker:
docker-compose exec backend dotnet build
docker-compose exec backend dotnet format
docker-compose exec backend dotnet format --verify-no-changes
docker-compose exec backend dotnet restore

# Without Docker:
dotnet build
dotnet format
dotnet format --verify-no-changes
dotnet restore
```

### Testing
```bash
# With Docker:
docker-compose exec backend dotnet test
docker-compose exec backend dotnet test --collect:"XPlat Code Coverage"
docker-compose exec backend dotnet test tests/MyProject.Tests
docker-compose exec backend dotnet test --filter "Category=Unit"

# Without Docker:
dotnet test
dotnet test --collect:"XPlat Code Coverage"
dotnet test tests/MyProject.Tests
dotnet test --filter "Category=Unit"
```

### Database Migrations (Entity Framework Core)
```bash
# With Docker:
docker-compose exec backend dotnet ef migrations add AddUserTable
docker-compose exec backend dotnet ef database update
docker-compose exec backend dotnet ef database update PreviousMigration
docker-compose exec backend dotnet ef migrations script

# Without Docker:
dotnet ef migrations add AddUserTable
dotnet ef database update
dotnet ef database update PreviousMigration
dotnet ef migrations script
```

---

## Troubleshooting

### Workflow Stuck

1. **Identify which step failed**
2. **Check agent output** for .NET errors
3. **Fix the issue** manually if needed
4. **Resume workflow** from failed step

### xUnit Tests Failing

1. Review test output for failure details
2. Check mock setups are correct
3. Verify database is in clean state
4. Fix implementation or tests
5. Re-run from Step 5

### Review Rejected Multiple Times

1. Discuss with team if ASP.NET Core approach is correct
2. Consider architectural review
3. May need to restart with different pattern

### Build Errors

1. Verify all packages are restored (`dotnet restore`)
2. Check for missing dependencies
3. With Docker: rebuild the Docker container. Without Docker: rebuild the solution.
4. Check for circular dependencies

---

## Resources

- [.NET Development Guide](../.claude/DOTNET_GUIDE.md) - C# coding standards
- [Testing Guide](TESTING_GUIDE.md) - xUnit practices
- [Docker Guide](../.claude/DOCKER_GUIDE.md) - Docker commands *(Docker projects only)*
- [Architecture](../.claude/ARCHITECTURE.md) - System architecture
- [ASP.NET Core Documentation](https://docs.microsoft.com/aspnet/core) - Official .NET docs
- [xUnit Documentation](https://xunit.net/) - xUnit testing framework

---

**Last Updated**: {{CURRENT_DATE}}
**Status**: Living Document
