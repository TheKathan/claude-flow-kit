# Frontend SwiftUI Workflow - {{PROJECT_NAME}}

**Date**: {{CURRENT_DATE}}
**Status**: ✅ ACTIVE
**Version**: 1.0 - SwiftUI Worktree-Based Workflow

---

## Overview

This guide covers the 14-step worktree-based workflow for **SwiftUI macOS application development**. SwiftUI apps use a single language (Swift) for both UI and logic, following MVVM architecture:

- **Views** (`Views/`) — declarative SwiftUI layout, no business logic
- **ViewModels** (`ViewModels/`) — `@Observable` state, async data loading
- **Services** (`Services/`) — business logic, networking, persistence

This workflow integrates:
- **Worktree isolation** (each feature gets its own worktree)
- **Architectural planning** (optional for complex features)
- **Automated test writing** (mandatory, XCTest + Swift Testing)
- **Quality gates** (tests + code review + integration build)
- **Merge conflict resolution** (automated before merge)
- **Automatic merge & cleanup** (after all gates pass)

> **No Docker**: SwiftUI development is macOS-native. Xcode and the Swift toolchain replace containerized environments.

---

## Workflow Architecture

### Core Principle

**MVVM with Protocol-Driven Services**

Every SwiftUI feature:
1. Gets its own **isolated worktree**
2. Implements **Views**, **ViewModels**, and **Services** as needed
3. Goes through **mandatory quality gates**
4. Has **conflicts resolved automatically** before merge
5. Is **merged and cleaned up automatically** after approval

**Quality Gates**:
1. **Unit Test Gate** (Step 5) — Swift tests must pass with ≥80% coverage
2. **Code Review Gate** (Step 6) — SwiftUI + Swift conventions reviewed
3. **Integration Test Gate** (Step 8) — Full Xcode build must succeed
4. **Conflict Resolution Gate** (Step 10) — Merge conflicts resolved
5. **Final Integration Gate** (Step 11) — Final build verified

---

## Agent System

**Specialized Agents for SwiftUI Development**:

| Agent | Scope | Role | Model |
|-------|-------|------|-------|
| software-architect | All | Design architecture (optional) | opus |
| **worktree-manager** | **All** | **Create worktrees, merge, cleanup** | sonnet |
| **swiftui-developer** | **All** | **Implement Views, ViewModels, Services** | sonnet |
| **swiftui-test-specialist** | **Tests** | **Write XCTest / Swift Testing tests** | sonnet |
| **frontend-code-reviewer** | **Review** | **Review SwiftUI conventions and Swift quality** | sonnet/opus |
| integration-tester | All | Execute tests and enforce quality gates | haiku |
| **merge-conflict-resolver** | **All** | **Detect and resolve merge conflicts** | opus |

---

## 14-Step SwiftUI Workflow

```
Step 0:  [OPTIONAL] software-architect   → Design architecture
Step 1:  worktree-manager                → Create worktree
Step 2:  swiftui-developer               → Implement Views + ViewModels + Services
Step 3:  swiftui-test-specialist         → Write XCTest / Swift Testing tests
Step 4:  swiftui-developer               → Commit code + tests
Step 5:  integration-tester              → Run swift test [GATE]
Step 6:  frontend-code-reviewer          → Review SwiftUI code [GATE]
Step 7:  swiftui-developer               → Fix if needed (loop to 5-6)
Step 8:  integration-tester              → Run Xcode build test [GATE]
Step 9:  swiftui-developer               → Push to feature branch
Step 10: merge-conflict-resolver         → Resolve conflicts [GATE]
Step 11: integration-tester              → Final build test [GATE]
Step 12: worktree-manager                → Merge to {{MAIN_BRANCH}}, push
Step 13: worktree-manager                → Cleanup worktree
Step 14: skill-creator                   → Discover reusable patterns [standard/full only]
```

---

## Step-by-Step Guide

### Step 0: Architectural Planning (Optional)

**When to Use**:
- ✅ New major feature with multiple Views + ViewModels
- ✅ Introducing a new Service or data model
- ✅ Changing navigation architecture (NavigationStack, TabView)
- ✅ Adding a new external dependency (Swift Package)

**When to Skip**:
- ❌ Small UI updates or text/styling changes
- ❌ Bug fixes in existing ViewModels
- ❌ Adding a new simple View that reuses existing Services

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

**Agent**: swiftui-developer

**Responsibilities**:
- Implement SwiftUI Views in `Sources/.../Views/`
- Implement `@Observable` ViewModels in `Sources/.../ViewModels/`
- Implement or update Services in `Sources/.../Services/`
- Define protocols before concrete implementations (for testability)
- Use `async/await` for all async operations
- Mark ViewModels and UI-bound state with `@MainActor`

**View Pattern**:
```swift
// Views/TaskListView.swift
struct TaskListView: View {
    @State private var viewModel = TaskListViewModel()

    var body: some View {
        List(viewModel.tasks) { task in
            TaskRow(task: task)
        }
        .navigationTitle("Tasks")
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button("Add") { viewModel.showAddTask = true }
            }
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

**ViewModel Pattern**:
```swift
// ViewModels/TaskListViewModel.swift
@Observable
@MainActor
final class TaskListViewModel {
    private(set) var tasks: [Task] = []
    private(set) var isLoading = false
    var errorMessage: String?
    var showAddTask = false

    private let taskService: TaskServiceProtocol

    init(taskService: TaskServiceProtocol = TaskService()) {
        self.taskService = taskService
    }

    func loadTasks() async {
        isLoading = true
        defer { isLoading = false }
        do {
            tasks = try await taskService.fetchAll()
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
```

---

### Step 3: Write Tests

**Agent**: swiftui-test-specialist

**Test with XCTest**:
```swift
// Tests/AppTests/TaskListViewModelTests.swift
import XCTest
@testable import {{PROJECT_NAME}}

@MainActor
final class TaskListViewModelTests: XCTestCase {
    func testLoadTasks_success_populatesTasks() async {
        let mockService = MockTaskService()
        mockService.stubbedTasks = [Task(id: UUID(), title: "Test", isComplete: false)]
        let vm = TaskListViewModel(taskService: mockService)

        await vm.loadTasks()

        XCTAssertEqual(vm.tasks.count, 1)
        XCTAssertNil(vm.errorMessage)
        XCTAssertFalse(vm.isLoading)
    }

    func testLoadTasks_failure_setsError() async {
        let mockService = MockTaskService(shouldFail: true)
        let vm = TaskListViewModel(taskService: mockService)

        await vm.loadTasks()

        XCTAssertTrue(vm.tasks.isEmpty)
        XCTAssertNotNil(vm.errorMessage)
    }
}
```

**Test with Swift Testing**:
```swift
import Testing
@testable import {{PROJECT_NAME}}

@Suite("TaskListViewModel")
@MainActor
struct TaskListViewModelTests {
    @Test("loads tasks on success")
    func loadTasks_success() async {
        let mock = MockTaskService(stubbedTasks: [Task(id: UUID(), title: "A", isComplete: false)])
        let vm = TaskListViewModel(taskService: mock)
        await vm.loadTasks()
        #expect(vm.tasks.count == 1)
        #expect(vm.errorMessage == nil)
    }
}
```

---

### Step 4: Commit Code + Tests

**Agent**: swiftui-developer

```bash
# Format
swift-format format -r -i Sources/ Tests/

# Lint
swiftlint lint

# Quick sanity build
swift build

# Run tests
swift test

# Commit
git add Sources/ Tests/
git commit -m "feat: add task list with async loading

- Add TaskListView with NavigationStack integration
- Add TaskListViewModel (@Observable, @MainActor)
- Add TaskServiceProtocol + TaskService (URLSession-based)
- Add MockTaskService for unit testing
- Tests: success + failure cases for loadTasks()"
```

---

### Step 5: Run Unit Tests ⚠️ GATE

**Agent**: integration-tester (haiku model)

```bash
# Run tests with coverage
swift test --enable-code-coverage

# Lint check
swiftlint lint --strict
```

**Pass Criteria**:
- All tests pass
- Zero SwiftLint errors (warnings allowed)
- Coverage ≥ 80% on ViewModels and Services

---

### Step 6: Code Review ⚠️ GATE

**Agent**: frontend-code-reviewer

**Review Criteria**:
- ✅ **No logic in Views** — Views only bind to ViewModels
- ✅ **`@MainActor` on ViewModels** — all UI-bound state on main actor
- ✅ **Protocol-driven Services** — concrete types depend on protocols
- ✅ **Error handling** — all errors surfaced to UI, no silenced errors
- ✅ **Concurrency safety** — `Sendable` conformance, no data races
- ✅ **Value types** — models are `struct`, not `class` where appropriate
- ✅ **swift-format compliance** — no formatting drift

---

### Step 7: Fix Issues

**Agent**: swiftui-developer

- Address ALL review issues
- Re-run formatting and tests
- Commit fixes
- Return to Step 5 → Step 6

**Max Cycles**: 3

---

### Step 8: Run Integration Tests ⚠️ GATE

**Agent**: integration-tester (haiku model)

```bash
# Full Xcode build (replace SCHEME with your target scheme)
xcodebuild -scheme {{PROJECT_NAME}} -configuration Debug build | xcpretty

# Or via SPM if Xcode project is not used
swift build -c release
```

**Pass Criteria**:
- Project builds with zero errors
- Zero new warnings introduced

---

### Step 9: Push Feature Branch

**Agent**: swiftui-developer

```bash
git push -u origin HEAD
```

---

### Step 10: Resolve Merge Conflicts ⚠️ GATE

**Agent**: merge-conflict-resolver (opus model)

**SwiftUI-Specific Conflict Types**:
- **`Package.swift`**: Different dependency additions → merge both
- **`routes.swift` / `App.swift`**: Different registrations → integrate both
- **View/ViewModel logic conflicts**: Request manual review

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

**Use For**: Regular UI features (80% of work)
**Time**: 25-35 minutes

### Full Workflow (14 steps)

**Steps**: 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13 → 14

**Use For**: New Services, major ViewModel architecture changes, new Swift Package dependencies
**Time**: 35-50 minutes

### Hotfix Workflow (10 steps) ⚡

**Steps**: 1 → 2 → 4 → 5 → 6 → 7 → 9 → 10 → 12 → 13

**Use For**: Production bugs, urgent fixes
**Time**: 15-20 minutes

---

## SwiftUI Development Best Practices

### DO

✅ Keep Views purely declarative — no async calls, no computed business logic
✅ Mark all ViewModels `@MainActor` to ensure safe UI updates
✅ Define `protocol` before concrete `Service` implementations
✅ Use `struct` for models, `actor` for shared mutable state
✅ Use `swift-format` before every commit — zero formatting drift
✅ Test ViewModels with mock Services — never test Views directly
✅ Use `defer` for cleanup in `async` functions (e.g., `isLoading = false`)

### DON'T

❌ Put `URLSession` calls or business logic directly in Views
❌ Use `try?` or `try!` in Services — propagate errors
❌ Share mutable state across ViewModels without an `actor`
❌ Use `@StateObject` with `ObservableObject` when `@Observable` is available (Swift 5.9+)
❌ Ignore `SwiftLint` warnings — treat `--strict` failures as blocking

---

## Resources

- [SwiftUI Guide](../.claude/SWIFTUI_GUIDE.md) - SwiftUI development standards
- [Apple SwiftUI Documentation](https://developer.apple.com/documentation/swiftui/)
- [Swift Concurrency](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/concurrency/)
- [Swift Testing](https://developer.apple.com/xcode/swift-testing/)
- [SwiftLint](https://github.com/realm/SwiftLint)

---

**Last Updated**: {{CURRENT_DATE}}
**Status**: Living Document
