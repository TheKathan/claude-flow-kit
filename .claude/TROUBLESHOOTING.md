# Troubleshooting Guide - {{PROJECT_NAME}}

**Date**: {{CURRENT_DATE}}

---

## Quick Diagnostics

{{#if USES_DOCKER}}### Docker Services

```bash
# Check all services
docker-compose ps

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart backend

# Full reset
docker-compose down && docker-compose up -d
```
{{/if}}

### Application Health

```bash
# Check backend
curl http://localhost:8000/health

{{#if HAS_FRONTEND}}# Check frontend
curl http://localhost:3000
{{/if}}
```

---

{{#if USES_DOCKER}}## Docker Issues

### Container Won't Start

**Symptoms**: Container exits immediately or won't start

**Check logs**:
```bash
docker-compose logs backend
docker-compose logs --tail=50 backend
```

**Common Causes**:

1. **Port already in use**
   ```bash
   # Find what's using the port (Linux/Mac)
   lsof -i :8000

   # Find what's using the port (Windows)
   netstat -ano | findstr :8000

   # Kill the process
   kill -9 <PID>  # Linux/Mac
   taskkill /PID <PID> /F  # Windows
   ```

2. **Missing environment variables**
   ```bash
   # Check environment variables
   docker-compose exec backend env

   # Verify .env file exists
   cat .env
   ```

3. **Database connection failed**
   ```bash
   # Check database container
   docker-compose ps database

   # Test database connection
   docker-compose exec backend psql $DATABASE_URL
   ```

4. **Volume mount issues**
   ```bash
   # Check volume permissions
   ls -la .

   # Reset volumes
   docker-compose down -v
   docker-compose up -d
   ```

### Container Keeps Restarting

**Check logs** for crash reason:
```bash
docker-compose logs backend --tail=100
```

**Common Causes**:
- Application errors (check stack trace)
- Configuration issues
- Database migrations failed
- Dependency errors

**Solutions**:
```bash
# Enter container to debug
docker-compose exec backend bash

# Check application files
ls -la /app

# Try running manually
{{#if BACKEND_LANGUAGE includes "Python"}}python app/main.py{{/if}}
```

### Slow Performance

**Check resource usage**:
```bash
docker stats
```

**Solutions**:
- Increase Docker memory/CPU limits
- Check for resource-intensive operations
- Optimize database queries
- Check for memory leaks

### Clean Up Docker

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune -a

# Remove unused volumes (⚠️ deletes data)
docker volume prune

# Complete cleanup
docker system prune -a --volumes
```
{{/if}}

---

## Database Issues

### Cannot Connect to Database

**Check connection string**:
```bash
echo $DATABASE_URL
```

**Verify database is running**:
{{#if USES_DOCKER}}```bash
docker-compose ps database
docker-compose logs database
```{{else}}```bash
# Check if database is running
pg_isready -h localhost -p 5432
```{{/if}}

**Test connection**:
```bash
{{#if USES_DOCKER}}docker-compose exec database psql -U postgres -d {{PROJECT_NAME}}{{else}}psql $DATABASE_URL{{/if}}
```

### Migration Errors

**Check migration status**:
```bash
{{#if USES_DOCKER}}docker-compose exec backend {{MIGRATION_STATUS_COMMAND}}{{else}}{{MIGRATION_STATUS_COMMAND}}{{/if}}
```

**Common issues**:

1. **Migration conflicts**
   - Multiple developers created migrations
   - Solution: Merge migrations or recreate

2. **Failed migration**
   ```bash
   # Rollback last migration
   {{MIGRATION_ROLLBACK_COMMAND}}

   # Fix the issue
   # Re-run migration
   {{MIGRATION_COMMAND}}
   ```

3. **Database out of sync**
   ```bash
   # ⚠️ Development only - drops all tables
   {{#if USES_DOCKER}}docker-compose exec backend {{DROP_DB_COMMAND}}
   docker-compose exec backend {{CREATE_DB_COMMAND}}
   docker-compose exec backend {{MIGRATION_COMMAND}}{{else}}{{DROP_DB_COMMAND}}
   {{CREATE_DB_COMMAND}}
   {{MIGRATION_COMMAND}}{{/if}}
   ```

---

## Testing Issues

### Tests Failing

**Run tests with verbose output**:
```bash
{{#if USES_DOCKER}}docker-compose exec backend {{TEST_COMMAND}} -v{{else}}{{TEST_COMMAND}} -v{{/if}}
```

**Common causes**:

1. **Database state issues**
   - Tests not cleaning up
   - Solution: Use transactions in tests or cleanup fixtures

2. **Async issues**
   - Missing await
   - Solution: Check all async functions

3. **Mock not working**
   - Mock not applied correctly
   - Solution: Check mock setup and scope

### Test Coverage Too Low

**Generate detailed coverage report**:
```bash
{{#if USES_DOCKER}}docker-compose exec backend {{TEST_COMMAND}} --cov={{BACKEND_FOLDER}} --cov-report=html{{else}}{{TEST_COMMAND}} --cov={{BACKEND_FOLDER}} --cov-report=html{{/if}}
```

**Identify uncovered code**:
- Open `htmlcov/index.html`
- Focus on critical paths first
- Aim for 80%+ overall

---

{{#if HAS_FRONTEND}}## Frontend Issues

### Build Failures

**Check for errors**:
```bash
{{#if USES_DOCKER}}docker-compose logs frontend{{else}}npm run build{{/if}}
```

**Common causes**:
1. TypeScript errors
2. Missing dependencies
3. Import errors
4. Environment variables missing

**Solutions**:
```bash
# Type check
npm run type-check

# Clean install
rm -rf node_modules package-lock.json
npm install

# Check environment variables
cat .env.local
```

### Hot Reload Not Working

**Restart frontend**:
```bash
{{#if USES_DOCKER}}docker-compose restart frontend{{else}}# Kill the process and restart
npm run dev{{/if}}
```

**Check for**:
- File watcher limits (Linux)
- Volume mounting issues (Docker)
- Browser cache (hard refresh: Ctrl+Shift+R)

### API Calls Failing

**Check CORS configuration**:
```bash
# View network tab in browser DevTools
# Check CORS headers in response
```

**Check API URL**:
```javascript
// Verify API base URL
console.log(process.env.NEXT_PUBLIC_API_URL)
```

**Common causes**:
- Wrong API URL in environment
- CORS not configured on backend
- API endpoint doesn't exist
{{/if}}

---

## Authentication Issues

### Cannot Login

**Check credentials**:
```bash
# Verify user exists in database
{{#if USES_DOCKER}}docker-compose exec backend {{DB_QUERY_COMMAND}}{{else}}{{DB_QUERY_COMMAND}}{{/if}}
```

**Check JWT configuration**:
```bash
# Verify JWT secret is set
echo $JWT_SECRET_KEY
```

**Common causes**:
1. Wrong password
2. JWT secret mismatch
3. Token expired
4. User not activated

### Token Expired Issues

**Check token expiration**:
```bash
# Decode JWT token
# Use jwt.io or jwt-cli
```

**Adjust expiration time** in configuration

---

## Performance Issues

### Slow API Responses

**Enable query logging**:
```bash
# Check which queries are slow
# Enable database query logging
```

**Common causes**:
1. N+1 query problem
2. Missing database indexes
3. Unoptimized queries
4. No caching

**Solutions**:
- Add database indexes
- Use select_related/prefetch_related (ORM)
- Implement caching
- Optimize query logic

### High Memory Usage

**Check memory usage**:
```bash
{{#if USES_DOCKER}}docker stats{{else}}# Check process memory
ps aux | grep {{PROJECT_NAME}}{{/if}}
```

**Common causes**:
- Memory leaks
- Large objects in memory
- Not closing connections
- Too many workers

**Solutions**:
- Profile memory usage
- Fix memory leaks
- Implement pagination
- Adjust worker count

---

## Security Issues

### CORS Errors

**Configure CORS** in backend:
```python
# Example for FastAPI
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### SQL Injection Concerns

**Always use parameterized queries**:
```python
# ✅ Good
query = "SELECT * FROM users WHERE email = :email"
db.execute(query, {"email": email})

# ❌ Bad
query = f"SELECT * FROM users WHERE email = '{email}'"
db.execute(query)
```

---

## Emergency Procedures

### Complete Reset (Development Only)

```bash
{{#if USES_DOCKER}}# Stop everything
docker-compose down -v

# Remove all data
docker volume prune -f

# Rebuild and start
docker-compose up -d --build

# Run migrations
docker-compose exec backend {{MIGRATION_COMMAND}}{{else}}# Drop database
{{DROP_DB_COMMAND}}

# Recreate database
{{CREATE_DB_COMMAND}}

# Run migrations
{{MIGRATION_COMMAND}}

# Reinstall dependencies
{{INSTALL_DEPENDENCIES_COMMAND}}{{/if}}
```

### Rollback Deployment

```bash
# Revert to previous commit
git revert HEAD

# Or reset to specific commit (⚠️ careful)
git reset --hard <commit-hash>

# Redeploy
{{DEPLOY_COMMAND}}
```

---

## Getting Help

### Collect Debug Information

```bash
# System info
{{#if USES_DOCKER}}docker-compose ps
docker-compose logs{{else}}{{SYSTEM_INFO_COMMAND}}{{/if}}

# Application logs
cat logs/application.log

# Recent commits
git log -5 --oneline
```

### Report Issues

Include:
1. Error message (full stack trace)
2. Steps to reproduce
3. Environment (dev/staging/prod)
4. Recent changes
5. Logs

---

## Resources

- [Architecture](ARCHITECTURE.md) - System architecture
- [Development Guide](DEVELOPMENT.md) - Development practices
{{#if USES_DOCKER}}- [Docker Guide](DOCKER_GUIDE.md) - Docker commands{{/if}}
- [Testing Guide](../docs/TESTING_GUIDE.md) - Testing help

---

**Last Updated**: {{CURRENT_DATE}}
**Status**: Living Document
