# Worktree Isolation Update Summary

**Date**: 2026-02-08
**Change**: Removed all shared database references, implemented complete worktree isolation

---

## ✅ Changes Made

### 1. **Updated `.agents/config.json` - worktree-manager agent**

**Before** (WRONG):
```
- Shares database (citadel_ai) and Redis with main repo
- Postgres: SHARED (main repo postgres:5432, database: citadel_ai)
- Redis: SHARED (main repo redis:6379)
- IMPORTANT: All worktrees share the same database. Migrations MUST be backward-compatible!
```

**After** (CORRECT):
```
- Each worktree has COMPLETELY ISOLATED Docker containers:
  - Separate database instance with unique port
  - Separate cache instance with unique port
  - Separate backend/frontend containers
  - NO shared resources between worktrees
  - NO impact on main branch Docker containers

Port Allocation: base_port + (worktree_id * 10)
- Backend: 8000, 8010, 8020...
- Frontend: 3000, 3010, 3020...
- Database: 5432, 5442, 5452... (ISOLATED per worktree)
- Cache: 6379, 6389, 6399... (ISOLATED per worktree)
```

**Key Points**:
- ✅ Each worktree runs its own database migrations
- ✅ Database changes are isolated to the worktree
- ✅ After merge, main branch needs to run migrations separately
- ✅ No risk of data conflicts between worktrees
- ✅ Complete cleanup includes database volumes and data

---

### 2. **Updated `CLAUDE.md`**

**Before**:
```
**Worktree Isolation**: Each feature gets its own worktree with isolated Docker
environment (unique ports), while sharing databases with main repo.
```

**After**:
```
**Worktree Isolation**: Each feature gets its own worktree with COMPLETELY ISOLATED
Docker environment including separate database, cache, backend, and frontend containers.
Each worktree uses unique ports and has NO SHARED RESOURCES with main branch or other worktrees.
```

---

### 3. **Updated `docs/WORKFLOW_GUIDE.md`**

**Before**:
```
- Docker containers running with unique ports
- Isolated environment, shared database
```

**After**:
```
- Docker containers running with unique ports (including database and cache)
- Completely isolated environment with separate database per worktree
- No shared resources with main branch
```

---

## 🎯 Complete Isolation Architecture

### Each Worktree Gets:

```
Worktree 1 (.worktrees/feature-1/)
├── Docker Compose Project: project_worktree_1
├── Backend Container (port 8010)
├── Frontend Container (port 3010)
├── Database Container (port 5442) ← ISOLATED
├── Cache Container (port 6389) ← ISOLATED
└── Docker Network: worktree_1_network

Worktree 2 (.worktrees/feature-2/)
├── Docker Compose Project: project_worktree_2
├── Backend Container (port 8020)
├── Frontend Container (port 3020)
├── Database Container (port 5452) ← ISOLATED
├── Cache Container (port 6399) ← ISOLATED
└── Docker Network: worktree_2_network

Main Branch
├── Docker Compose Project: project_main
├── Backend Container (port 8000)
├── Frontend Container (port 3000)
├── Database Container (port 5432) ← ISOLATED
├── Cache Container (port 6379) ← ISOLATED
└── Docker Network: main_network
```

**Key**: NO SHARED RESOURCES - Complete independence!

---

## 🔧 Implementation Requirements

When implementing worktree scripts, ensure:

### worktree_create.sh
```bash
# Must create SEPARATE docker-compose.worktree-{id}.yml
# Must use UNIQUE ports for ALL services including database
# Must use SEPARATE Docker networks
# Must use SEPARATE Docker volumes for database data
```

### worktree_cleanup.sh
```bash
# Must remove database containers
# Must remove database volumes (data cleanup)
# Must remove cache containers and volumes
# Must remove backend/frontend containers
# Must remove Docker images
# Must remove Docker networks
# Must remove worktree directory
```

### Port Allocation Formula
```python
worktree_id = 1, 2, 3, ...
base_ports = {
    "backend": 8000,
    "frontend": 3000,
    "database": 5432,
    "cache": 6379
}

worktree_ports = {
    "backend": base_ports["backend"] + (worktree_id * 10),
    "frontend": base_ports["frontend"] + (worktree_id * 10),
    "database": base_ports["database"] + (worktree_id * 10),
    "cache": base_ports["cache"] + (worktree_id * 10)
}

# Example for worktree_id = 2:
# backend: 8020, frontend: 3020, database: 5452, cache: 6399
```

---

## 📋 Migration Strategy

### In Worktree (During Development)
```bash
# Worktree 1 - isolated database
cd .worktrees/feature-1/
docker-compose -f docker-compose.worktree-1.yml exec backend \
    python manage.py migrate  # OR: dotnet ef database update

# This affects ONLY worktree-1's database
# Main branch database is NOT touched
```

### In Main Branch (After Merge)
```bash
# After merging feature to main, run migrations in main
cd /main/repo/
docker-compose exec backend python manage.py migrate

# This updates main branch's database
# Worktree databases are already cleaned up
```

---

## ✅ Benefits of Complete Isolation

1. **No Database Conflicts**
   - Multiple developers can work on conflicting schema changes
   - Each worktree has independent database state
   - No need for backward-compatible migrations during development

2. **True Testing Isolation**
   - Each worktree's tests use its own database
   - No test data pollution between worktrees
   - No impact on main branch during testing

3. **Independent Development**
   - Breaking changes in worktree don't affect main
   - Can experiment freely with database schema
   - No coordination needed between developers

4. **Clean Separation**
   - Main branch Docker containers untouched by worktrees
   - Easy to identify which resources belong to which worktree
   - Simple cleanup - just remove all containers/volumes

5. **Parallel Development**
   - Multiple features can be developed simultaneously
   - No risk of data race conditions
   - No shared state between features

---

## ⚠️ Important Notes

### Migration Considerations

**During Development** (in worktree):
- Migrations can be breaking/experimental
- No need for backward compatibility
- Can reset database freely for testing

**After Merge** (in main):
- Run migrations in main branch
- Migrations should be production-ready
- Consider migration rollback strategy

### Data Considerations

**Worktree databases are TEMPORARY**:
- Created when worktree is created
- Destroyed when worktree is cleaned up
- Do NOT use for persistent data
- Always seed with test/development data

**Main database is PERSISTENT**:
- Survives across all worktree operations
- Contains actual development/production data
- Requires careful migration management

---

## 🔍 Verification

To verify complete isolation is working:

```bash
# 1. Check running containers
docker ps
# Should show: main containers + worktree-1 containers + worktree-2 containers
# Each with unique ports

# 2. Check Docker networks
docker network ls
# Should show: main_network, worktree_1_network, worktree_2_network

# 3. Check database connections
# Main database
docker exec -it main-database psql -U postgres -c "\l"

# Worktree-1 database
docker exec -it worktree-1-database psql -U postgres -c "\l"

# Should be completely different databases

# 4. Check volumes
docker volume ls
# Should show: main_data, worktree_1_data, worktree_2_data
```

---

## 📚 Updated Documentation

All references to shared databases removed from:
- ✅ `.agents/config.json` (worktree-manager system prompt)
- ✅ `CLAUDE.md` (worktree isolation description)
- ✅ `docs/WORKFLOW_GUIDE.md` (step 1 output description)

All documentation now correctly describes **complete isolation**.

---

## 🎉 Summary

The template now implements **true worktree isolation** where:
- ❌ **No shared databases** between worktrees
- ❌ **No shared cache** between worktrees
- ❌ **No shared Docker resources** at all
- ✅ **Complete independence** for each worktree
- ✅ **Zero impact** on main branch during development
- ✅ **Parallel development** without conflicts

This ensures safe, isolated development environments for all features!

---

**Status**: ✅ Complete
**Template Version**: 1.1.0 (Isolation Update)
**Date**: 2026-02-08
