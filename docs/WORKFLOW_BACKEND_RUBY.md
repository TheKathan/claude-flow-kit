# Backend Ruby Workflow - {{PROJECT_NAME}}

**Date**: {{CURRENT_DATE}}
**Status**: ✅ ACTIVE
**Version**: 2.0 - Ruby Backend Worktree-Based Workflow

---

## Overview

This guide covers the 13-step worktree-based workflow for **Ruby/Rails backend development**. This workflow integrates:
- **Worktree isolation** (each feature gets its own worktree, with Docker environment for Docker projects)
- **Architectural planning** (optional for complex features)
- **Automated test writing** (mandatory with RSpec)
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
1. **Unit Test Gate** (Step 5) - All RSpec tests must pass with 80%+ coverage
2. **Code Review Gate** (Step 6) - Code must be approved by backend reviewer
3. **Integration Test Gate** (Step 8) - End-to-end tests must pass
4. **Conflict Resolution Gate** (Step 10) - Merge conflicts must be resolved
5. **Final Integration Gate** (Step 11) - Final tests with base branch merged must pass

---

## Agent System

**Specialized Agents for Ruby Backend**:

| Agent | Type | Scope | Role | Model |
|-------|------|-------|------|-------|
| software-architect | Architect | All | Design architecture (optional) | opus |
| **worktree-manager** | **Manager** | **All** | **Create worktrees, merge, cleanup** | sonnet |
| **ruby-developer** | **Developer** | **Backend** | **Implement Ruby/Rails features** | sonnet |
| **ruby-test-specialist** | **Tester** | **Backend** | **Write RSpec tests** | sonnet |
| **backend-code-reviewer** | **Reviewer** | **Backend** | **Review backend code** | sonnet/opus |
| integration-tester | Tester | All | Execute all tests and enforce gates | haiku |
| **docker-debugger** | **Debugger** | **All** | **Diagnose and fix Docker issues** *(Docker projects only)* | sonnet |
| **merge-conflict-resolver** | **Resolver** | **All** | **Detect and resolve merge conflicts** | opus |

---

## 13-Step Ruby Backend Workflow

```
Step 0:  [OPTIONAL] software-architect      → Design architecture
Step 1:  worktree-manager                   → Create worktree
Step 1b: [DOCKER/ON-FAILURE] docker-debugger → Debug setup issues
Step 2:  ruby-developer                     → Implement Ruby/Rails feature
Step 3:  ruby-test-specialist               → Write RSpec tests
Step 4:  ruby-developer                     → Commit code + tests
Step 5:  integration-tester                 → Run RSpec unit tests [GATE]
Step 5b: [DOCKER/ON-FAILURE] docker-debugger → Debug test issues
Step 6:  backend-code-reviewer              → Review code [GATE]
Step 7:  ruby-developer                     → Fix if needed (loop to 5-6)
Step 8:  integration-tester                 → Run E2E tests [GATE]
Step 8b: [DOCKER/ON-FAILURE] docker-debugger → Debug E2E issues
Step 9:  ruby-developer                     → Push to feature branch
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
- Proposed Rails architecture
- Database schema (ActiveRecord models)
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
python scripts/worktree_create.py feature-name
```

**Output**:
- Worktree created at `.worktrees/feature-name`
- Branch created: `feature/feature-name`

> **Note**: The worktree branches from whichever branch is currently checked out. At Step 12, the feature branch will be merged back to that same base branch.

> *(Docker projects only)* The script automatically starts Docker containers with unique ports, providing a completely isolated Ruby environment with a separate database per worktree — no shared resources.

**On Failure** (Step 1b) *(Docker projects only)*:
- docker-debugger diagnoses port conflicts, container issues
- Fixes automatically if possible
- Reports if manual intervention needed

---

### Step 2: Implement Feature

**Agent**: ruby-developer

**Responsibilities**:
- Write clean, idiomatic Ruby code
- Follow RuboCop style guide (zero offenses)
- Add frozen string literal comments to every file
- Write YARD documentation for public methods
- Follow Rails MVC patterns and service objects
- Use ActiveRecord safely (eager loading, strong parameters)
- Handle errors with specific rescue clauses and custom exceptions
- Place scripts in `scripts/` folder

**Ruby-Specific Patterns**:
```ruby
# frozen_string_literal: true

class UsersController < ApplicationController
  before_action :authenticate_user!

  def create
    result = UserCreationService.call(user_params)

    if result.success?
      render json: UserSerializer.new(result.user), status: :created
    else
      render json: { errors: result.errors }, status: :unprocessable_entity
    end
  end

  private

  def user_params
    params.require(:user).permit(:email, :name, :password)
  end
end
```

**DO NOT commit yet** - tests need to be written first

---

### Step 3: Write Tests

**Agent**: ruby-test-specialist

**Responsibilities**:
- Analyze Ruby implementation
- Design test scenarios (happy path, errors, edge cases, security)
- Implement RSpec tests with FactoryBot and shared examples
- Target 80%+ coverage with SimpleCov
- Document test purpose in spec descriptions

**Ruby Test Structure** (RSpec with Four-Phase Pattern):
```ruby
# frozen_string_literal: true

require 'rails_helper'

RSpec.describe UsersController, type: :request do
  describe 'POST /users' do
    context 'with valid parameters' do
      let(:valid_params) do
        { user: { email: 'new@example.com', name: 'New User', password: 'SecurePass123!' } }
      end

      it 'returns 201 Created' do
        post '/users', params: valid_params, as: :json
        expect(response).to have_http_status(:created)
      end

      it 'creates a user record' do
        expect {
          post '/users', params: valid_params, as: :json
        }.to change(User, :count).by(1)
      end

      it 'does not expose the password' do
        post '/users', params: valid_params, as: :json
        expect(JSON.parse(response.body)).not_to have_key('password')
      end
    end

    context 'with a duplicate email' do
      let!(:existing_user) { create(:user, email: 'existing@example.com') }

      it 'returns 422 Unprocessable Entity' do
        post '/users',
             params: { user: { email: 'existing@example.com', name: 'Other' } },
             as: :json
        expect(response).to have_http_status(:unprocessable_entity)
      end
    end
  end
end
```

**Test Coverage Requirements**:
- Model specs: validations, associations, scopes, callbacks
- Request/controller specs: all endpoints (success + error cases)
- Service object specs: business logic paths
- Security specs: authentication, authorization, input validation
- Edge cases: nil inputs, invalid types, boundary conditions

---

### Step 4: Commit Code + Tests

**Agent**: ruby-developer

**Commands**:
```bash
# With Docker:
docker-compose exec app bundle exec rubocop {{BACKEND_FOLDER}}/ --autocorrect
docker-compose exec app bundle exec rubocop {{BACKEND_FOLDER}}/

# Without Docker:
bundle exec rubocop {{BACKEND_FOLDER}}/ --autocorrect
bundle exec rubocop {{BACKEND_FOLDER}}/

# Commit
git add .
git commit -m "feat: add user creation endpoint

- Implement POST /users endpoint with Rails controller
- Add UserCreationService for business logic encapsulation
- Add User model with email uniqueness validation
- Run database migration for users table
- Add comprehensive RSpec request and unit specs
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
docker-compose exec app bundle exec rspec --format progress \
  --require spec_helper

# Without Docker:
bundle exec rspec --format progress
bundle exec rails test  # if using Minitest
```

**Pass Criteria**:
- All RSpec examples pass (0 failures, 0 errors, 0 pending)
- SimpleCov coverage ≥ 80%
- RuboCop reports 0 offenses

**On Fail**:
- Workflow BLOCKED
- Orchestrator invokes ruby-developer to fix
- Returns to Step 5 after fix

**On Docker Failure** (Step 5b) *(Docker projects only)*:
- docker-debugger diagnoses container issues
- Fixes and retries test execution

---

### Step 6: Code Review ⚠️ GATE

**Agent**: backend-code-reviewer (sonnet, opus for critical)

**Review Criteria**:
- ✅ **Security** (SQL injection, strong parameters, mass assignment, input validation)
- ✅ **Performance** (N+1 queries, eager loading, index usage, find_each for batches)
- ✅ **Best Practices** (RuboCop compliance, frozen strings, service objects, SOLID)
- ✅ **Architecture** (Rails MVC conventions, service layer separation, thin controllers)
- ✅ **Database** (ActiveRecord best practices, migrations, constraints, uniqueness)
- ✅ **API Design** (RESTful conventions, status codes, response serialization)

**Ruby-Specific Checks**:
- Frozen string literal on every file
- Strong parameters in all controllers
- No N+1 queries (use includes/eager_load)
- Specific rescue clauses (never bare `rescue`)
- Custom exception classes for domain errors
- No raw SQL without parameterization
- Service objects for complex business logic

**Outcomes**:
- ✅ **APPROVED** - Continue to Step 8
- ❌ **CHANGES REQUESTED** - Go to Step 7

---

### Step 7: Fix Issues

**Agent**: ruby-developer

**Responsibilities**:
- Address ALL review issues
- Make targeted fixes
- Re-run RuboCop with `--autocorrect`
- Commit fixes
- Return to Step 5 (re-test) → Step 6 (re-review)

**Max Cycles**: 3 (if stuck, reassess approach)

---

### Step 8: Run Integration Tests ⚠️ GATE

**Agent**: integration-tester (haiku model)

**Commands**:
```bash
# With Docker:
docker-compose exec app bundle exec rspec spec/requests/ spec/system/ -v
docker-compose exec app bundle exec rails db:migrate RAILS_ENV=test

# Check API health:
curl http://localhost:3000/health

# Without Docker:
bundle exec rspec spec/requests/ spec/system/ -v
bundle exec rails db:migrate RAILS_ENV=test

# Check API health:
curl http://localhost:3000/health
```

**Pass Criteria**:
- All request and system specs pass
- API responds correctly to all test scenarios
- Database operations work end-to-end
- No integration failures

**On Fail**:
- Workflow BLOCKED
- ruby-developer fixes issues
- May loop back to Step 5-6 if code changes needed

**On Docker Failure** (Step 8b) *(Docker projects only)*:
- docker-debugger diagnoses E2E test issues
- Fixes and retries

---

### Step 9: Push Feature Branch

**Agent**: ruby-developer

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

**Ruby-Specific Conflict Types**:
- **Simple**: comments, whitespace, formatting → auto-resolve
- **Models**: ActiveRecord model changes → integrate both, check migrations
- **Routes**: Different route additions → integrate both
- **Logic**: Different implementations of same method → request manual review
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
docker-compose exec app bundle exec rspec --format progress
docker-compose exec app bundle exec rubocop {{BACKEND_FOLDER}}/
docker-compose exec app bundle exec rails db:migrate RAILS_ENV=test

# Without Docker:
bundle exec rspec --format progress
bundle exec rubocop {{BACKEND_FOLDER}}/
bundle exec rails db:migrate RAILS_ENV=test
```

**Pass Criteria**:
- All tests pass after merge
- No new RuboCop offenses
- Database migrations run cleanly

**On Fail**:
- Workflow BLOCKED
- ruby-developer fixes merge issues

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
python scripts/worktree_merge.py feature-name
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
python scripts/worktree_cleanup.py feature-name
```

**On Failure** (Step 13b) *(Docker projects only)*:
- docker-debugger force cleanups stuck resources
- Removes containers, images, volumes
- Ensures clean state

---

## Workflow Variants

### Standard Workflow (11 steps) ⭐ Most Common

**Steps**: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 9 → 10 → 12 → 13

**Use For**: Regular Ruby backend features, enhancements (80% of work)
**Time**: 25-35 minutes
**Cost**: Medium
**Note**: Skips E2E tests (Step 8) and final integration test (Step 11)

### Full Workflow (13 steps)

**Steps**: 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13

**Use For**: New Rails services, architectural changes, database schema changes
**Time**: 35-50 minutes
**Cost**: High

### Hotfix Workflow (10 steps) ⚡

**Steps**: 1 → 2 → 4 → 5 → 6 → 7 → 9 → 10 → 12 → 13

**Use For**: Production bugs, urgent Ruby fixes
**Time**: 15-20 minutes
**Cost**: Low
**Note**: Skips test writing (assumes tests exist), skips E2E tests; includes fix loop (Step 7)

### Test-Only Workflow (7 steps)

**Steps**: 1 → 3 → 4 → 5 → 9 → 12 → 13

**Use For**: Adding tests to existing Ruby code, improving coverage
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

## Ruby Development Best Practices

### DO

✅ Add `# frozen_string_literal: true` to every file
✅ Use strong parameters in all controllers
✅ Write service objects for business logic
✅ Use `includes`/`eager_load` to prevent N+1 queries
✅ Rescue specific exception classes
✅ Use FactoryBot factories in specs (not raw `.create`)
✅ Run RuboCop before committing
✅ Write request specs for all API endpoints
✅ Use database transactions for related operations
✅ Follow Rails naming conventions consistently

### DON'T

❌ Use bare `rescue` without an exception class
❌ Build SQL strings with string interpolation
❌ Skip strong parameters (mass assignment risk)
❌ Put business logic in controllers (keep them thin)
❌ Trigger N+1 queries by omitting eager loading
❌ Commit with RuboCop offenses
❌ Use `User.all` for large datasets (use `find_each`)
❌ Hardcode configuration values
❌ Write specs without FactoryBot factories
❌ Skip error handling

---

## Ruby Tools and Commands

### Formatting and Linting
```bash
# With Docker:
docker-compose exec app bundle exec rubocop {{BACKEND_FOLDER}}/ --autocorrect
docker-compose exec app bundle exec rubocop {{BACKEND_FOLDER}}/

# Without Docker:
bundle exec rubocop {{BACKEND_FOLDER}}/ --autocorrect
bundle exec rubocop {{BACKEND_FOLDER}}/
```

### Testing
```bash
# With Docker:
docker-compose exec app bundle exec rspec -v
docker-compose exec app bundle exec rspec --format documentation
docker-compose exec app bundle exec rspec spec/models/user_spec.rb -v
docker-compose exec app bundle exec rspec -e "creates a user" -v

# Without Docker:
bundle exec rspec -v
bundle exec rspec --format documentation
bundle exec rspec spec/models/user_spec.rb -v
bundle exec rspec -e "creates a user" -v
```

### Database Migrations
```bash
# With Docker:
docker-compose exec app bundle exec rails db:migrate
docker-compose exec app bundle exec rails db:migrate RAILS_ENV=test
docker-compose exec app bundle exec rails db:rollback STEP=1
docker-compose exec app bundle exec rails db:schema:load RAILS_ENV=test

# Without Docker:
bundle exec rails db:migrate
bundle exec rails db:migrate RAILS_ENV=test
bundle exec rails db:rollback STEP=1
bundle exec rails db:schema:load RAILS_ENV=test
```

---

## Troubleshooting

### Workflow Stuck

1. **Identify which step failed**
2. **Check agent output** for Ruby errors
3. **Fix the issue** manually if needed
4. **Resume workflow** from failed step

### RSpec Tests Failing

1. Review RSpec output for failure details
2. Check FactoryBot factories are properly defined
3. Verify database is in clean state (DatabaseCleaner configured)
4. Fix implementation or specs
5. Re-run from Step 5

### Review Rejected Multiple Times

1. Discuss with team if Ruby approach is correct
2. Consider architectural review
3. May need to restart with different Rails pattern

### Bundle Issues

1. Verify dependencies in Gemfile
2. With Docker: rebuild the Docker container. Without Docker: run `bundle install`.
3. Check for gem version conflicts with `bundle update --conservative`

---

## Resources

- [Ruby Development Guide](../.claude/RUBY_GUIDE.md) - Ruby coding standards
- [Testing Guide](TESTING_GUIDE.md) - RSpec practices
- [Docker Guide](../.claude/DOCKER_GUIDE.md) - Docker commands *(Docker projects only)*
- [Architecture](../.claude/ARCHITECTURE.md) - System architecture
- [Rails Guides](https://guides.rubyonrails.org/) - Official Rails documentation
- [RSpec Documentation](https://rspec.info/) - RSpec testing framework

---

**Last Updated**: {{CURRENT_DATE}}
**Status**: Living Document
