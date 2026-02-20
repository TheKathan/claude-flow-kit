# Backend Node.js Workflow - {{PROJECT_NAME}}

**Date**: {{CURRENT_DATE}}
**Status**: ✅ ACTIVE
**Version**: 2.0 - Node.js Backend Worktree-Based Workflow

---

## Overview

This guide covers the 13-step worktree-based workflow for **Node.js/Express backend development**. This workflow integrates:
- **Worktree isolation** (each feature gets its own worktree, with Docker environment for Docker projects)
- **Architectural planning** (optional for complex features)
- **Automated test writing** (mandatory with Jest)
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
1. **Unit Test Gate** (Step 5) - All Jest tests must pass with 80%+ coverage
2. **Code Review Gate** (Step 6) - Code must be approved by backend reviewer
3. **Integration Test Gate** (Step 8) - End-to-end tests must pass
4. **Conflict Resolution Gate** (Step 10) - Merge conflicts must be resolved
5. **Final Integration Gate** (Step 11) - Final tests with base branch merged must pass

---

## Agent System

**Specialized Agents for Node.js Backend**:

| Agent | Type | Scope | Role | Model |
|-------|------|-------|------|-------|
| software-architect | Architect | All | Design architecture (optional) | opus |
| **worktree-manager** | **Manager** | **All** | **Create worktrees, merge, cleanup** | sonnet |
| **nodejs-developer** | **Developer** | **Backend** | **Implement Node.js/Express features** | sonnet |
| **nodejs-test-specialist** | **Tester** | **Backend** | **Write Jest tests** | sonnet |
| **backend-code-reviewer** | **Reviewer** | **Backend** | **Review backend code** | sonnet/opus |
| integration-tester | Tester | All | Execute all tests and enforce gates | haiku |
| **docker-debugger** | **Debugger** | **All** | **Diagnose and fix Docker issues** *(Docker projects only)* | sonnet |
| **merge-conflict-resolver** | **Resolver** | **All** | **Detect and resolve merge conflicts** | opus |

---

## 13-Step Node.js Backend Workflow

```
Step 0:  [OPTIONAL] software-architect      → Design architecture
Step 1:  worktree-manager                   → Create worktree
Step 1b: [DOCKER/ON-FAILURE] docker-debugger → Debug setup issues
Step 2:  nodejs-developer                   → Implement Node.js/Express feature
Step 3:  nodejs-test-specialist             → Write Jest tests
Step 4:  nodejs-developer                   → Commit code + tests
Step 5:  integration-tester                 → Run Jest unit tests [GATE]
Step 5b: [DOCKER/ON-FAILURE] docker-debugger → Debug test issues
Step 6:  backend-code-reviewer              → Review code [GATE]
Step 7:  nodejs-developer                   → Fix if needed (loop to 5-6)
Step 8:  integration-tester                 → Run E2E tests [GATE]
Step 8b: [DOCKER/ON-FAILURE] docker-debugger → Debug E2E issues
Step 9:  nodejs-developer                   → Push to feature branch
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
- Proposed Express/NestJS architecture
- Database schema (Prisma/TypeORM models)
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

> *(Docker projects only)* Docker containers start with unique ports, providing a completely isolated Node.js environment with a separate database per worktree — no shared resources.

**On Failure** (Step 1b) *(Docker projects only)*:
- docker-debugger diagnoses port conflicts, container issues
- Fixes automatically if possible
- Reports if manual intervention needed

---

### Step 2: Implement Feature

**Agent**: nodejs-developer

**Responsibilities**:
- Write clean, maintainable TypeScript/JavaScript code
- Follow Node.js best practices
- Use TypeScript for type safety
- Write JSDoc comments
- Follow Express/NestJS patterns (middleware, controllers, services)
- Use async/await for asynchronous operations
- Handle errors gracefully with error middleware
- Place scripts in `scripts/` folder

**Node.js-Specific Patterns**:
```typescript
// Express controller with service layer
import { Request, Response, NextFunction } from 'express';
import { UserService } from '../services/user.service';
import { CreateUserDto, UserResponseDto } from '../dtos/user.dto';
import { AppError } from '../utils/app-error';

export class UserController {
  private userService: UserService;

  constructor() {
    this.userService = new UserService();
  }

  /**
   * Create a new user
   * @route POST /api/users
   */
  public createUser = async (
    req: Request<{}, {}, CreateUserDto>,
    res: Response<UserResponseDto>,
    next: NextFunction
  ): Promise<void> => {
    try {
      const userData = req.body;
      const user = await this.userService.createUser(userData);

      res.status(201).json({
        id: user.id,
        email: user.email,
        username: user.username,
        createdAt: user.createdAt
      });
    } catch (error) {
      if (error instanceof AppError) {
        next(error);
      } else {
        next(new AppError('Failed to create user', 500));
      }
    }
  };

  /**
   * Get user by ID
   * @route GET /api/users/:id
   */
  public getUser = async (
    req: Request<{ id: string }>,
    res: Response<UserResponseDto>,
    next: NextFunction
  ): Promise<void> => {
    try {
      const userId = parseInt(req.params.id, 10);
      const user = await this.userService.getUserById(userId);

      if (!user) {
        throw new AppError('User not found', 404);
      }

      res.json(user);
    } catch (error) {
      next(error);
    }
  };
}
```

**DO NOT commit yet** - tests need to be written first

---

### Step 3: Write Tests

**Agent**: nodejs-test-specialist

**Responsibilities**:
- Analyze Node.js implementation
- Design test scenarios (happy path, errors, edge cases, security)
- Implement Jest tests with mocks and fixtures
- Target 80%+ coverage
- Document test purpose

**Node.js Test Structure** (Jest with AAA Pattern):
```typescript
import request from 'supertest';
import { app } from '../src/app';
import { UserService } from '../src/services/user.service';

jest.mock('../src/services/user.service');

describe('UserController', () => {
  let userService: jest.Mocked<UserService>;

  beforeEach(() => {
    userService = new UserService() as jest.Mocked<UserService>;
    jest.clearAllMocks();
  });

  describe('POST /api/users', () => {
    it('should create a new user successfully', async () => {
      // Arrange
      const userData = {
        email: 'newuser@example.com',
        username: 'newuser',
        password: 'SecurePass123!'
      };

      const expectedUser = {
        id: 1,
        email: userData.email,
        username: userData.username,
        createdAt: new Date()
      };

      userService.createUser.mockResolvedValue(expectedUser);

      // Act
      const response = await request(app)
        .post('/api/users')
        .send(userData)
        .expect('Content-Type', /json/)
        .expect(201);

      // Assert
      expect(response.body).toMatchObject({
        id: expectedUser.id,
        email: expectedUser.email,
        username: expectedUser.username
      });
      expect(response.body).not.toHaveProperty('password');
      expect(userService.createUser).toHaveBeenCalledWith(userData);
    });

    it('should return 409 when email already exists', async () => {
      const userData = {
        email: 'existing@example.com',
        username: 'newuser',
        password: 'SecurePass123!'
      };

      userService.createUser.mockRejectedValue(
        new AppError('User already exists', 409)
      );

      const response = await request(app)
        .post('/api/users')
        .send(userData)
        .expect(409);

      expect(response.body).toHaveProperty('message', 'User already exists');
    });
  });

  describe('GET /api/users/:id', () => {
    it('should return user when found', async () => {
      const userId = 1;
      const expectedUser = {
        id: userId,
        email: 'user@example.com',
        username: 'testuser',
        createdAt: new Date()
      };

      userService.getUserById.mockResolvedValue(expectedUser);

      const response = await request(app)
        .get(`/api/users/${userId}`)
        .expect(200);

      expect(response.body).toMatchObject(expectedUser);
    });

    it('should return 404 when user not found', async () => {
      userService.getUserById.mockResolvedValue(null);

      await request(app)
        .get('/api/users/999')
        .expect(404);
    });
  });
});
```

**Test Coverage Requirements**:
- Unit tests: All services and utility functions
- API tests: All endpoints (success + error cases)
- Database tests: CRUD operations with Prisma/TypeORM
- Security tests: Authentication, authorization, input validation
- Edge cases: Null inputs, invalid types, boundary conditions

---

### Step 4: Commit Code + Tests

**Agent**: nodejs-developer

**Commands**:
```bash
# With Docker:
docker-compose exec backend npm run format
docker-compose exec backend npm run lint
docker-compose exec backend npm run type-check
docker-compose exec backend npm run build

# Without Docker:
npm run format
npm run lint
npm run type-check
npm run build

# Commit
git add .
git commit -m "feat: add user creation endpoint

- Implement POST /api/users endpoint with Express
- Add CreateUserDto and UserResponseDto interfaces
- Add User model with Prisma
- Implement UserService with duplicate email check
- Add comprehensive Jest tests (unit + integration)
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
docker-compose exec backend npm test -- --coverage --verbose

# Without Docker:
npm test -- --coverage --verbose
```

**Pass Criteria**:
- All Jest tests pass (0 failures, 0 errors)
- Coverage ≥ 80%
- No critical ESLint errors
- TypeScript compilation succeeds

**On Fail**:
- Workflow BLOCKED
- Orchestrator invokes nodejs-developer to fix
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
- ✅ **Best Practices** (TypeScript usage, error handling, async/await)
- ✅ **Architecture** (Express patterns, middleware, service layer)
- ✅ **Database** (Prisma/TypeORM best practices, migrations)
- ✅ **API Design** (RESTful conventions, status codes, response structure)

**Node.js-Specific Checks**:
- TypeScript types on all functions
- Async/await used correctly (no callback hell)
- Error handling with Express error middleware
- Input validation with Joi/Zod/class-validator
- Database connections managed properly (no leaks)
- No SQL injection vulnerabilities
- Promises handled correctly (no unhandled rejections)
- Environment variables used for configuration

**Outcomes**:
- ✅ **APPROVED** - Continue to Step 8
- ❌ **CHANGES REQUESTED** - Go to Step 7

---

### Step 7: Fix Issues

**Agent**: nodejs-developer

**Responsibilities**:
- Address ALL review issues
- Make targeted fixes
- Re-format with Prettier
- Re-lint with ESLint
- Type-check with TypeScript
- Commit fixes
- Return to Step 5 (re-test) → Step 6 (re-review)

**Max Cycles**: 3 (if stuck, reassess approach)

---

### Step 8: Run Integration Tests ⚠️ GATE

**Agent**: integration-tester (haiku model)

**Commands**:
```bash
# With Docker:
docker-compose exec backend npm run test:integration
docker-compose exec backend npm test -- --testPathPattern=integration

# Check API health:
curl http://localhost:3000/health

# Without Docker:
npm run test:integration
npm test -- --testPathPattern=integration

# Check API health:
curl http://localhost:3000/health
```

**Pass Criteria**:
- All E2E tests pass
- API responds correctly to all test scenarios
- Database operations work end-to-end
- No integration failures

**On Fail**:
- Workflow BLOCKED
- nodejs-developer fixes issues
- May loop back to Step 5-6 if code changes needed

**On Docker Failure** (Step 8b) *(Docker projects only)*:
- docker-debugger diagnoses E2E test issues
- Fixes and retries

---

### Step 9: Push Feature Branch

**Agent**: nodejs-developer

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

**Node.js-Specific Conflict Types**:
- **Simple**: imports, whitespace, formatting → auto-resolve
- **Models**: Prisma schema changes → integrate both, regenerate client
- **Routes**: Different API routes → integrate both
- **Logic**: Different implementations of same function → request manual review
- **Package.json**: Dependency conflicts → merge carefully, run npm install
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
docker-compose exec backend npm test -- --coverage
docker-compose exec backend npm run lint
docker-compose exec backend npm run type-check

# Without Docker:
npm test -- --coverage
npm run lint
npm run type-check
```

**Pass Criteria**:
- All tests pass after merge
- No new linting errors
- TypeScript compilation succeeds

**On Fail**:
- Workflow BLOCKED
- nodejs-developer fixes merge issues

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

**Use For**: Regular Node.js backend features, enhancements (80% of work)
**Time**: 25-35 minutes
**Cost**: Medium

### Full Workflow (13 steps)

**Steps**: 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13

**Use For**: New Node.js services, architectural changes, database schema changes
**Time**: 35-50 minutes
**Cost**: High

### Hotfix Workflow (9 steps) ⚡

**Steps**: 1 → 2 → 4 → 5 → 6 → 7 → 9 → 10 → 12 → 13

**Use For**: Production bugs, urgent Node.js fixes
**Time**: 15-20 minutes
**Cost**: Low
**Note**: Skips test writing (assumes tests exist), skips E2E tests; includes fix loop (Step 7)

### Test-Only Workflow (7 steps)

**Steps**: 1 → 3 → 4 → 5 → 9 → 12 → 13

**Use For**: Adding tests to existing Node.js code, improving coverage
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

## Node.js Development Best Practices

### DO

✅ Use TypeScript for type safety
✅ Use async/await for asynchronous operations
✅ Implement proper error handling middleware
✅ Validate input with Joi/Zod/class-validator
✅ Use dependency injection for testability
✅ Write comprehensive Jest tests
✅ Follow Express/NestJS patterns
✅ Use environment variables for configuration
✅ Handle Promise rejections
✅ Use Prettier for code formatting

### DON'T

❌ Use callbacks (callback hell)
❌ Ignore ESLint warnings
❌ Hardcode configuration values
❌ Skip TypeScript types
❌ Leak database connections
❌ Use synchronous operations for I/O
❌ Return inconsistent API responses
❌ Commit without running format/lint
❌ Skip error handling
❌ Ignore unhandled promise rejections

---

## Node.js Tools and Commands

### Building and Linting
```bash
# With Docker:
docker-compose exec backend npm install
docker-compose exec backend npm run build
docker-compose exec backend npm run format
docker-compose exec backend npm run lint
docker-compose exec backend npm run type-check

# Without Docker:
npm install
npm run build
npm run format
npm run lint
npm run type-check
```

### Testing
```bash
# With Docker:
docker-compose exec backend npm test
docker-compose exec backend npm test -- --coverage
docker-compose exec backend npm test -- users.test.ts
docker-compose exec backend npm test -- --watch
docker-compose exec backend npm run test:integration

# Without Docker:
npm test
npm test -- --coverage
npm test -- users.test.ts
npm test -- --watch
npm run test:integration
```

### Database Migrations (Prisma)
```bash
# With Docker:
docker-compose exec backend npx prisma generate
docker-compose exec backend npx prisma migrate dev --name add-user-table
docker-compose exec backend npx prisma migrate deploy
docker-compose exec backend npx prisma migrate reset

# Without Docker:
npx prisma generate
npx prisma migrate dev --name add-user-table
npx prisma migrate deploy
npx prisma migrate reset
```

---

## Troubleshooting

### Workflow Stuck

1. **Identify which step failed**
2. **Check agent output** for Node.js errors
3. **Fix the issue** manually if needed
4. **Resume workflow** from failed step

### Jest Tests Failing

1. Review Jest output for failure details
2. Check mocks are properly configured
3. Verify database is in clean state
4. Fix implementation or tests
5. Re-run from Step 5

### Review Rejected Multiple Times

1. Discuss with team if Express/NestJS approach is correct
2. Consider architectural review
3. May need to restart with different pattern

### Dependency Conflicts

1. Delete node_modules and package-lock.json
2. Run npm install
3. With Docker: rebuild the Docker container. Without Docker: rebuild the project.
4. Check for peer dependency issues

---

## Resources

- [Node.js Development Guide](../.claude/NODEJS_GUIDE.md) - Node.js coding standards
- [Testing Guide](TESTING_GUIDE.md) - Jest practices
- [Docker Guide](../.claude/DOCKER_GUIDE.md) - Docker commands *(Docker projects only)*
- [Architecture](../.claude/ARCHITECTURE.md) - System architecture
- [Express Documentation](https://expressjs.com/) - Official Express docs
- [Jest Documentation](https://jestjs.io/) - Jest testing framework
- [TypeScript Handbook](https://www.typescriptlang.org/docs/) - TypeScript documentation

---

**Last Updated**: {{CURRENT_DATE}}
**Status**: Living Document
