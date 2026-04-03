# Swift Backend Development Guide

**Version**: 1.0
**Last Updated**: {{CURRENT_DATE}}

---

## Overview

This guide outlines Swift backend coding standards for **{{PROJECT_NAME}}** using Vapor or Hummingbird. Server-side Swift brings Swift's type safety, structured concurrency, and performance to backend development.

---

## Project Structure

```
Sources/
  App/
    Controllers/          # Route handlers
    Models/               # Fluent models / DTOs
    Migrations/           # Database migrations
    Services/             # Business logic
    Middleware/           # Custom middleware
    configure.swift       # App configuration
    routes.swift          # Route registration
Tests/
  AppTests/               # XCTest unit tests
Package.swift             # Swift Package Manager
```

---

## Error Handling

Use `throws` and `do-catch` consistently. Surface meaningful errors to callers.

```swift
// Domain error type conforming to AbortError (Vapor)
enum AppError: AbortError {
    case notFound(resource: String)
    case unauthorized
    case validationFailed(field: String, reason: String)
    case internalError(underlying: Error)

    var status: HTTPResponseStatus {
        switch self {
        case .notFound: return .notFound
        case .unauthorized: return .unauthorized
        case .validationFailed: return .badRequest
        case .internalError: return .internalServerError
        }
    }

    var reason: String {
        switch self {
        case .notFound(let r): return "\(r) not found"
        case .unauthorized: return "Unauthorized"
        case .validationFailed(let f, let r): return "Invalid \(f): \(r)"
        case .internalError: return "Internal server error"
        }
    }
}

// Service with throwing async functions
protocol UserServiceProtocol {
    func find(id: UUID) async throws -> User
    func create(_ dto: CreateUserDTO) async throws -> User
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
}
```

---

## Route Controllers (Vapor)

```swift
struct UserController: RouteCollection {
    let userService: UserServiceProtocol

    func boot(routes: RoutesBuilder) throws {
        let users = routes.grouped("users")
        users.get(":id", use: getUser)
        users.post(use: createUser)
    }

    @Sendable
    func getUser(_ req: Request) async throws -> UserDTO {
        guard let id = req.parameters.get("id", as: UUID.self) else {
            throw AppError.validationFailed(field: "id", reason: "must be a valid UUID")
        }
        let user = try await userService.find(id: id)
        return UserDTO(user)
    }

    @Sendable
    func createUser(_ req: Request) async throws -> UserDTO {
        let dto = try req.content.decode(CreateUserDTO.self)
        try CreateUserDTO.validate(content: req)
        let user = try await userService.create(dto)
        return UserDTO(user)
    }
}
```

---

## Concurrency

Use `async/await` and `Actor` for all async work. Conform to `Sendable` for types crossing actor boundaries.

```swift
// Actor for shared mutable state
actor RateLimiter {
    private var requestCounts: [String: Int] = [:]
    private let limit: Int

    init(limit: Int) { self.limit = limit }

    func check(key: String) throws {
        let count = requestCounts[key, default: 0]
        guard count < limit else {
            throw AppError.unauthorized
        }
        requestCounts[key] = count + 1
    }
}

// Sendable DTO — safe to cross concurrency boundaries
struct CreateUserDTO: Content, Validatable, Sendable {
    let email: String
    let name: String

    static func validations(_ validations: inout Validations) {
        validations.add("email", as: String.self, is: .email)
        validations.add("name", as: String.self, is: !.empty)
    }
}
```

---

## Testing

```swift
import XCTVapor
@testable import App

final class UserControllerTests: XCTestCase {
    var app: Application!

    override func setUp() async throws {
        app = try await Application.make(.testing)
        try await configure(app)
    }

    override func tearDown() async throws {
        try await app.asyncShutdown()
        app = nil
    }

    func testGetUser_existingId_returns200() async throws {
        let user = User(email: "test@example.com", name: "Test")
        try await user.save(on: app.db)

        try await app.test(.GET, "/users/\(user.id!)") { res async in
            XCTAssertEqual(res.status, .ok)
            let dto = try res.content.decode(UserDTO.self)
            XCTAssertEqual(dto.email, "test@example.com")
        }
    }

    func testGetUser_unknownId_returns404() async throws {
        let unknownId = UUID()
        try await app.test(.GET, "/users/\(unknownId)") { res async in
            XCTAssertEqual(res.status, .notFound)
        }
    }
}
```

---

## Code Quality

```bash
# Format
swift-format format -r -i Sources/ Tests/

# Lint
swiftlint lint

# Build
swift build

# Test (with coverage)
swift test --enable-code-coverage

# Check for warnings (treat as errors in CI)
swift build 2>&1 | grep -i warning && exit 1 || exit 0
```

---

## Key Rules

- **`throws` on all fallible functions** — never return `nil` to indicate failure from a service
- **`async throws` for all I/O** — network, database, filesystem calls must be `async throws`
- **`Sendable` on shared types** — any type crossing actor boundaries must conform
- **Protocol-driven services** — depend on protocols for testability
- **No `try!` or `try?` in production** — propagate or handle errors explicitly
- **ALL scripts in `scripts/` folder**, never in `/tmp/`

---

## Resources

- [Vapor Documentation](https://docs.vapor.codes/)
- [Swift on Server](https://www.swift.org/documentation/server/)
- [Swift Concurrency](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/concurrency/)
- [SwiftLint](https://github.com/realm/SwiftLint)

---

**Last Updated**: {{CURRENT_DATE}}
