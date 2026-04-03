# Backend Swift Workflow - {{PROJECT_NAME}}

**Date**: {{CURRENT_DATE}}
**Status**: ✅ ACTIVE
**Version**: 1.0 - Swift Backend Worktree-Based Workflow

---

## Overview

This guide covers the 14-step worktree-based workflow for **Swift backend development** using Vapor or Hummingbird. This workflow integrates:
- **Worktree isolation** (each feature gets its own worktree)
- **Architectural planning** (optional for complex features)
- **Automated test writing** (mandatory with XCTest / Swift Testing)
- **Quality gates** (tests + code review + integration tests)
- **Merge conflict resolution** (automated before merge)
- **Automatic merge & cleanup** (after all gates pass)

> **No Docker required**: Swift backend development uses the native Swift toolchain. Docker is optional for deployment parity.

---

## Workflow Architecture

### Core Principle

**Protocol-Driven, Test-First Swift Backend**

Every backend feature:
1. Gets its own **isolated worktree**
2. Goes through **mandatory quality gates** before being pushed
3. Has **conflicts resolved automatically** before merge
4. Is **merged and cleaned up automatically** after approval

**Quality Gates**:
1. **Unit Test Gate** (Step 5) — All Swift tests pass with 80%+ coverage
2. **Code Review Gate** (Step 6) — Code approved by backend reviewer
3. **Integration Test Gate** (Step 8) — End-to-end tests pass
4. **Conflict Resolution Gate** (Step 10) — Merge conflicts resolved
5. **Final Integration Gate** (Step 11) — Final tests with base branch merged

---

## Agent System

**Specialized Agents for Swift Backend**:

| Agent | Type | Role | Model |
|-------|------|------|-------|
| software-architect | Architect | Design architecture (optional) | opus |
| **worktree-manager** | Manager | Create worktrees, merge, cleanup | sonnet |
| **swift-developer** | Developer | Implement Swift backend features | sonnet |
| **swift-test-specialist** | Tester | Write XCTest / Swift Testing tests | sonnet |
| **backend-code-reviewer** | Reviewer | Review backend code | sonnet/opus |
| integration-tester | Tester | Execute tests and enforce gates | haiku |
| **merge-conflict-resolver** | Resolver | Detect and resolve merge conflicts | opus |

---

## 14-Step Swift Backend Workflow

```
Step 0:  [OPTIONAL] software-architect  → Design architecture
Step 1:  worktree-manager               → Create worktree
Step 2:  swift-developer                → Implement Swift feature
Step 3:  swift-test-specialist          → Write XCTest / Swift Testing tests
Step 4:  swift-developer                → Commit code + tests
Step 5:  integration-tester             → Run swift test [GATE]
Step 6:  backend-code-reviewer          → Review code [GATE]
Step 7:  swift-developer                → Fix if needed (loop to 5-6)
Step 8:  integration-tester             → Run integration tests [GATE]
Step 9:  swift-developer                → Push to feature branch
Step 10: merge-conflict-resolver        → Resolve conflicts [GATE]
Step 11: integration-tester             → Final integration test [GATE]
Step 12: worktree-manager               → Merge to {{MAIN_BRANCH}}, push
Step 13: worktree-manager               → Cleanup worktree
Step 14: skill-creator                  → Discover reusable patterns [standard/full only]
```

---

## Step-by-Step Guide

### Step 0: Architectural Planning (Optional)

**When to Use**:
- ✅ New API routes or services
- ✅ Database schema or Fluent model changes
- ✅ Complex features with multiple dependencies
- ✅ Major refactoring

**When to Skip**:
- ❌ Bug fixes
- ❌ Simple CRUD additions
- ❌ Minor endpoint changes

**Agent**: software-architect (opus model)

---

### Step 1: Create Worktree

**Agent**: worktree-manager

```bash
python scripts/worktree_create.py feature-name
```

**Output**:
- Worktree created at `.worktrees/feature-name`
- Branch created: `feature/feature-name`

---

### Step 2: Implement Feature

**Agent**: swift-developer

**Responsibilities**:
- Implement route controllers in `Sources/App/Controllers/`
- Implement business logic in `Sources/App/Services/`
- Define `protocol` before concrete types for testability
- Use `async throws` for all I/O-bound operations
- Conform to `Sendable` for types crossing concurrency boundaries

**Controller Pattern**:
```swift
// Sources/App/Controllers/UserController.swift
struct UserController: RouteCollection {
    let userService: UserServiceProtocol

    func boot(routes: RoutesBuilder) throws {
        let users = routes.grouped("users")
            .grouped(UserAuthMiddleware())
        users.get(":id", use: getUser)
        users.post(use: createUser)
        users.delete(":id", use: deleteUser)
    }

    @Sendable
    func getUser(_ req: Request) async throws -> UserDTO {
        guard let id = req.parameters.get("id", as: UUID.self) else {
            throw AppError.validationFailed(field: "id", reason: "must be a valid UUID")
        }
        return try await userService.find(id: id).toDTO()
    }

    @Sendable
    func createUser(_ req: Request) async throws -> UserDTO {
        try CreateUserDTO.validate(content: req)
        let dto = try req.content.decode(CreateUserDTO.self)
        return try await userService.create(dto).toDTO()
    }

    @Sendable
    func deleteUser(_ req: Request) async throws -> HTTPStatus {
        guard let id = req.parameters.get("id", as: UUID.self) else {
            throw AppError.validationFailed(field: "id", reason: "must be a valid UUID")
        }
        try await userService.delete(id: id)
        return .noContent
    }
}
```

**Service Pattern**:
```swift
// Sources/App/Services/UserService.swift
protocol UserServiceProtocol: Sendable {
    func find(id: UUID) async throws -> User
    func create(_ dto: CreateUserDTO) async throws -> User
    func delete(id: UUID) async throws
}

final class UserService: UserServiceProtocol {
    private let db: Database

    init(db: Database) { self.db = db }

    func find(id: UUID) async throws -> User {
        guard let user = try await User.find(id, on: db) else {
            throw AppError.notFound(resource: "User")
        }
        return user
    }

    func create(_ dto: CreateUserDTO) async throws -> User {
        let user = User(email: dto.email, name: dto.name)
        try await user.save(on: db)
        return user
    }

    func delete(id: UUID) async throws {
        let user = try await find(id: id)
        try await user.delete(on: db)
    }
}
```

---

### Step 3: Write Tests

**Agent**: swift-test-specialist

```swift
// Tests/AppTests/UserControllerTests.swift
import XCTVapor
@testable import App

final class UserControllerTests: XCTestCase {
    var app: Application!

    override func setUp() async throws {
        app = try await Application.make(.testing)
        try await configure(app)
        try await app.autoMigrate()
    }

    override func tearDown() async throws {
        try await app.autoRevert()
        try await app.asyncShutdown()
    }

    func testCreateUser_validPayload_returns201() async throws {
        let payload = CreateUserDTO(email: "test@example.com", name: "Test User")
        try await app.test(.POST, "/users", beforeRequest: { req in
            try req.content.encode(payload)
        }) { res async in
            XCTAssertEqual(res.status, .created)
            let dto = try res.content.decode(UserDTO.self)
            XCTAssertEqual(dto.email, "test@example.com")
        }
    }

    func testGetUser_unknownId_returns404() async throws {
        try await app.test(.GET, "/users/\(UUID())") { res async in
            XCTAssertEqual(res.status, .notFound)
        }
    }

    func testCreateUser_invalidEmail_returns400() async throws {
        let payload = CreateUserDTO(email: "not-an-email", name: "Test")
        try await app.test(.POST, "/users", beforeRequest: { req in
            try req.content.encode(payload)
        }) { res async in
            XCTAssertEqual(res.status, .badRequest)
        }
    }
}
```

---

### Step 4: Commit Code + Tests

**Agent**: swift-developer

```bash
# Format
swift-format format -r -i Sources/ Tests/

# Lint
swiftlint lint

# Build
swift build

# Run tests
swift test --enable-code-coverage

# Commit
git add Sources/ Tests/ Package.swift
git commit -m "feat: add user CRUD endpoints

- Add UserController with GET, POST, DELETE routes
- Add UserService implementing UserServiceProtocol
- Add CreateUserDTO with email + name validation
- Tests: create success/failure, get 404, delete success
- swift-format clean, zero SwiftLint errors"
```

---

### Step 5: Run Unit Tests ⚠️ GATE

**Agent**: integration-tester (haiku model)

```bash
swift test --enable-code-coverage
swiftlint lint --strict
```

**Pass Criteria**:
- All tests pass
- Zero SwiftLint errors
- Coverage ≥ 80% on Controllers and Services

---

### Step 6: Code Review ⚠️ GATE

**Agent**: backend-code-reviewer

**Review Criteria**:
- ✅ **`async throws` on all I/O** — no synchronous blocking calls
- ✅ **Protocol-driven** — controllers depend on service protocols
- ✅ **`Sendable` conformance** — types used across actors are Sendable
- ✅ **No `try?` / `try!`** — errors propagate to Vapor's error middleware
- ✅ **Input validation** — all DTOs have `Validatable` conformance
- ✅ **Proper HTTP status codes** — 201 for create, 204 for delete, etc.

---

### Step 7: Fix Issues

**Agent**: swift-developer

- Address ALL review issues
- Re-run formatting and tests
- Commit fixes
- Return to Step 5 → Step 6

**Max Cycles**: 3

---

### Step 8: Run Integration Tests ⚠️ GATE

**Agent**: integration-tester (haiku model)

```bash
# Full build in release mode
swift build -c release

# Run integration test suite (requires test database)
swift test --enable-code-coverage --filter IntegrationTests
```

**Pass Criteria**:
- Release build succeeds with zero errors
- Integration tests pass

---

### Step 9: Push Feature Branch

**Agent**: swift-developer

```bash
git push -u origin HEAD
```

---

### Step 10: Resolve Merge Conflicts ⚠️ GATE

**Agent**: merge-conflict-resolver (opus model)

**Swift-Specific Conflict Types**:
- **`Package.swift`**: Different dependency or target additions → merge both
- **`configure.swift`**: Different middleware or route registrations → integrate both
- **`routes.swift`**: Different route group additions → integrate both
- **Migration conflicts**: Sequence migrations carefully — request manual review

---

### Step 11: Final Integration Test ⚠️ GATE

**Agent**: integration-tester (haiku model)

```bash
swift test --enable-code-coverage
swift build -c release
```

---

### Step 12: Merge to Base Branch

**Agent**: worktree-manager

```bash
python scripts/worktree_merge.py feature-name
```

---

### Step 13: Cleanup

**Agent**: worktree-manager

```bash
python scripts/worktree_cleanup.py feature-name
```

---

### Step 14: Skill Discovery *(standard and full variants only)*

**Agent**: skill-creator

Review the task and git log. Identify multi-step patterns worth capturing as reusable skills. Apply four gates: non-trivial, generalizable, not already covered, durable. Write or decline.

**Skip if**: variant is `hotfix`, `tests`, or `docs`.

---

## Workflow Variants

### Standard Workflow (13 steps) ⭐ Most Common

**Steps**: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 9 → 10 → 12 → 13

**Use For**: Regular API features (80% of work)
**Time**: 25-35 minutes

### Full Workflow (14 steps)

**Steps**: 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13 → 14

**Use For**: New services, Fluent model changes, middleware additions
**Time**: 35-50 minutes

### Hotfix Workflow (10 steps) ⚡

**Steps**: 1 → 2 → 4 → 5 → 6 → 7 → 9 → 10 → 12 → 13

**Use For**: Production bugs, urgent fixes
**Time**: 15-20 minutes

---

## Swift Backend Best Practices

### DO

✅ Use `async throws` for every function that does I/O
✅ Define `protocol` before `class` — depend on protocols, inject concretes
✅ Validate all DTOs with `Validatable` before processing
✅ Return typed `AbortError` subtypes — never throw raw strings
✅ Conform to `Sendable` for all types used across `async` contexts
✅ Run `swift-format` before every commit

### DON'T

❌ Use `try?` or `try!` in Controllers or Services — propagate errors
❌ Block the event loop with `DispatchQueue.main.sync` or `Thread.sleep`
❌ Store mutable state in `struct` types used across actors
❌ Skip DTO validation — always call `validate(content:)` before decoding
❌ Add routes without corresponding tests

---

## Resources

- [Swift Guide](../.claude/SWIFT_GUIDE.md) — Swift backend coding standards
- [Vapor Documentation](https://docs.vapor.codes/) — Official Vapor docs
- [Swift on Server](https://www.swift.org/documentation/server/) — Swift server ecosystem
- [Swift Concurrency](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/concurrency/)

---

**Last Updated**: {{CURRENT_DATE}}
**Status**: Living Document
