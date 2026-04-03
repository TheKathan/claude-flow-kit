# SwiftUI Development Guide

**Version**: 1.0
**Last Updated**: {{CURRENT_DATE}}

---

## Overview

This guide outlines development standards for **SwiftUI macOS applications** in {{PROJECT_NAME}}. SwiftUI apps use declarative UI, MVVM architecture, and Swift's structured concurrency model.

---

## Project Structure

```
{{PROJECT_NAME}}/
  Sources/
    {{PROJECT_NAME}}/
      App/
        {{PROJECT_NAME}}App.swift   # App entry point (@main)
      Views/                        # SwiftUI Views (UI only)
        ContentView.swift
        Components/
      ViewModels/                   # @Observable view models
      Models/                       # Data models (structs)
      Services/                     # Business logic, network, persistence
      Repositories/                 # Data access layer
  Tests/
    {{PROJECT_NAME}}Tests/          # XCTest unit tests
    {{PROJECT_NAME}}UITests/        # XCUITest UI tests
  {{PROJECT_NAME}}.xcodeproj
  Package.swift                     # Swift Package Manager (if SPM-only)
```

---

## Architecture: MVVM

Views are dumb — they only render state. Logic lives in ViewModels and Services.

```swift
// Model — plain value type
struct Task: Identifiable, Codable {
    let id: UUID
    var title: String
    var isComplete: Bool
}

// ViewModel — @Observable (Swift 5.9+)
@Observable
final class TaskListViewModel {
    private(set) var tasks: [Task] = []
    private(set) var isLoading = false
    var errorMessage: String?

    private let taskService: TaskServiceProtocol

    init(taskService: TaskServiceProtocol = TaskService()) {
        self.taskService = taskService
    }

    @MainActor
    func loadTasks() async {
        isLoading = true
        defer { isLoading = false }
        do {
            tasks = try await taskService.fetchTasks()
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

// View — reads state, calls ViewModel
struct TaskListView: View {
    @State private var viewModel = TaskListViewModel()

    var body: some View {
        List(viewModel.tasks) { task in
            TaskRow(task: task)
        }
        .overlay {
            if viewModel.isLoading { ProgressView() }
        }
        .task { await viewModel.loadTasks() }
        .alert("Error", isPresented: .constant(viewModel.errorMessage != nil)) {
            Button("OK") { viewModel.errorMessage = nil }
        } message: {
            Text(viewModel.errorMessage ?? "")
        }
    }
}
```

---

## View Composition

Keep Views small and focused. Extract components aggressively.

```swift
// Good: small, single-purpose View
struct TaskRow: View {
    let task: Task

    var body: some View {
        HStack {
            Image(systemName: task.isComplete ? "checkmark.circle.fill" : "circle")
                .foregroundStyle(task.isComplete ? .green : .secondary)
            Text(task.title)
                .strikethrough(task.isComplete)
        }
    }
}

// Bad: monolithic View with business logic
struct TaskListView: View {
    var body: some View {
        List(tasks) { task in
            HStack {
                // 50 lines of inline UI + computed properties + logic...
            }
        }
        .onAppear {
            // network calls directly in the View — NO
        }
    }
}
```

---

## Error Handling

Use `throws` and `Result<T, E>` consistently. Never silence errors with `try?` in business logic.

```swift
// Domain error type
enum TaskError: LocalizedError {
    case notFound(id: UUID)
    case saveFailed(underlying: Error)
    case networkUnavailable

    var errorDescription: String? {
        switch self {
        case .notFound(let id): return "Task \(id) not found"
        case .saveFailed(let err): return "Save failed: \(err.localizedDescription)"
        case .networkUnavailable: return "Network unavailable"
        }
    }
}

// Service using throws
protocol TaskServiceProtocol {
    func fetchTasks() async throws -> [Task]
    func save(_ task: Task) async throws
    func delete(id: UUID) async throws
}

final class TaskService: TaskServiceProtocol {
    func fetchTasks() async throws -> [Task] {
        // Propagate errors with context, never swallow them
        do {
            return try await networkClient.get("/tasks")
        } catch let urlError as URLError {
            throw TaskError.networkUnavailable
        } catch {
            throw TaskError.saveFailed(underlying: error)
        }
    }
}
```

---

## Concurrency

Use `async/await` and `Actor` for all async work. Always update UI on `@MainActor`.

```swift
// Actor for shared mutable state — no data races
actor TaskCache {
    private var cache: [UUID: Task] = [:]

    func task(for id: UUID) -> Task? { cache[id] }

    func store(_ task: Task) { cache[task.id] = task }
}

// @MainActor ensures UI updates happen on the main thread
@MainActor
final class TaskListViewModel {
    // All properties read on main actor — safe for SwiftUI
    private(set) var tasks: [Task] = []

    func loadTasks() async {
        // `await` suspends without blocking the main thread
        let fetched = try? await TaskService().fetchTasks()
        tasks = fetched ?? []
    }
}

// Use Task for fire-and-forget from synchronous contexts
Button("Refresh") {
    Task { await viewModel.loadTasks() }
}
```

---

## Testing

### Unit Tests (XCTest)

```swift
import XCTest
@testable import {{PROJECT_NAME}}

final class TaskListViewModelTests: XCTestCase {
    var sut: TaskListViewModel!
    var mockService: MockTaskService!

    override func setUp() {
        super.setUp()
        mockService = MockTaskService()
        sut = TaskListViewModel(taskService: mockService)
    }

    override func tearDown() {
        sut = nil
        mockService = nil
        super.tearDown()
    }

    func testLoadTasks_success_populatesTasks() async {
        // Arrange
        let expected = [Task(id: UUID(), title: "Buy milk", isComplete: false)]
        mockService.stubbedTasks = expected

        // Act
        await sut.loadTasks()

        // Assert
        XCTAssertEqual(sut.tasks.count, 1)
        XCTAssertEqual(sut.tasks.first?.title, "Buy milk")
        XCTAssertNil(sut.errorMessage)
    }

    func testLoadTasks_failure_setsErrorMessage() async {
        // Arrange
        mockService.shouldFail = true

        // Act
        await sut.loadTasks()

        // Assert
        XCTAssertTrue(sut.tasks.isEmpty)
        XCTAssertNotNil(sut.errorMessage)
    }
}
```

### Swift Testing Framework (`@Test`)

```swift
import Testing
@testable import {{PROJECT_NAME}}

@Suite("TaskListViewModel")
struct TaskListViewModelTests {
    @Test("loads tasks successfully")
    func loadTasks_success() async throws {
        let mockService = MockTaskService()
        mockService.stubbedTasks = [Task(id: UUID(), title: "Test", isComplete: false)]
        let vm = await TaskListViewModel(taskService: mockService)

        await vm.loadTasks()

        #expect(vm.tasks.count == 1)
        #expect(vm.errorMessage == nil)
    }

    @Test("sets error on failure", .tags(.networking))
    func loadTasks_failure() async throws {
        let mockService = MockTaskService(shouldFail: true)
        let vm = await TaskListViewModel(taskService: mockService)

        await vm.loadTasks()

        #expect(vm.tasks.isEmpty)
        #expect(vm.errorMessage != nil)
    }
}
```

---

## Code Quality

```bash
# Format
swift-format format -r -i Sources/

# Lint
swiftlint lint

# Build
xcodebuild -scheme {{PROJECT_NAME}} -configuration Debug build

# Test (with coverage)
xcodebuild -scheme {{PROJECT_NAME}} -enableCodeCoverage YES test

# Or with Swift Package Manager
swift build
swift test --enable-code-coverage
```

---

## Key Rules

- **No logic in Views** — Views bind to `@Observable` ViewModels, nothing more
- **`@MainActor` on ViewModels** — all UI-bound state must be on the main actor
- **Protocol-driven** — depend on protocols, not concrete types (enables testing)
- **Value types for models** — use `struct` for data models, `class` only for reference semantics
- **No `try?` in services** — propagate errors so ViewModels can surface them
- **ALL scripts in `scripts/` folder**, never in `/tmp/`

---

## Resources

- [Swift Documentation](https://www.swift.org/documentation/)
- [SwiftUI Documentation](https://developer.apple.com/documentation/swiftui/)
- [Swift Concurrency](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/concurrency/)
- [Swift Testing](https://developer.apple.com/xcode/swift-testing/)
- [SwiftLint](https://github.com/realm/SwiftLint)

---

**Last Updated**: {{CURRENT_DATE}}
