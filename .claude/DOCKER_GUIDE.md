# Docker Guide - {{PROJECT_NAME}}

**Date**: {{CURRENT_DATE}}

---

## Quick Start

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

---

## Docker Services

### Service Overview

[Update this section with your actual services]

**Example**:

#### 1. database
- Port: `5432`
- Purpose: PostgreSQL database
- Persistent volume: `postgres_data`

#### 2. cache
- Port: `6379`
- Purpose: Redis caching
- Persistent volume: `redis_data`

#### 3. backend
- Port: `8000`
- Purpose: {{BACKEND_FRAMEWORK}} API server
- Hot reload: Enabled

{{#if HAS_FRONTEND}}#### 4. frontend
- Port: `3000`
- Purpose: {{FRONTEND_FRAMEWORK}} web interface
- Hot reload: Enabled
{{/if}}

---

## Container Status Verification

```bash
# Expected output from: docker-compose ps
NAME                        STATUS              PORTS
{{PROJECT_NAME}}-database   Up (healthy)        0.0.0.0:5432->5432/tcp
{{PROJECT_NAME}}-cache      Up                  0.0.0.0:6379->6379/tcp
{{PROJECT_NAME}}-backend    Up                  0.0.0.0:8000->8000/tcp
{{#if HAS_FRONTEND}}{{PROJECT_NAME}}-frontend   Up                  0.0.0.0:3000->3000/tcp{{/if}}
```

---

## Common Commands

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
{{#if HAS_FRONTEND}}docker-compose logs -f frontend{{/if}}

# Last N lines
docker-compose logs --tail=100 backend

# Since timestamp
docker-compose logs --since="2024-01-01" backend
```

### Executing Commands in Containers

```bash
# Open shell
docker-compose exec backend bash

# Run command directly
docker-compose exec backend python manage.py migrate
{{#if HAS_FRONTEND}}docker-compose exec frontend npm run lint{{/if}}

# Run as different user
docker-compose exec -u root backend bash
```

### Managing Services

```bash
# Start specific service
docker-compose up -d backend

# Restart service
docker-compose restart backend

# Stop specific service
docker-compose stop backend

# Rebuild and restart
docker-compose up -d --build backend

# Force recreate containers
docker-compose up -d --force-recreate
```

### Database Operations

```bash
# Connect to database
docker-compose exec database psql -U postgres -d {{PROJECT_NAME}}

# Create database backup
docker-compose exec database pg_dump -U postgres {{PROJECT_NAME}} > backup.sql

# Restore from backup
docker-compose exec -T database psql -U postgres {{PROJECT_NAME}} < backup.sql

# Run migrations
docker-compose exec backend {{MIGRATION_COMMAND}}
```

---

## Development Workflow

### 1. Initial Setup

```bash
# Clone repository
git clone {{REPO_URL}}
cd {{PROJECT_NAME}}

# Copy environment file
cp .env.example .env

# Edit environment variables
# [Edit .env with your editor]

# Start services
docker-compose up -d

# Run migrations (if applicable)
docker-compose exec backend {{MIGRATION_COMMAND}}

# Verify services
curl http://localhost:8000/health
{{#if HAS_FRONTEND}}curl http://localhost:3000{{/if}}
```

### 2. Daily Development

```bash
# Start services
docker-compose up -d

# View logs while developing
docker-compose logs -f backend

# Run tests
docker-compose exec backend {{TEST_COMMAND}}

# Stop services when done
docker-compose down
```

### 3. Code Changes

**Backend code changes**:
- Hot reload is enabled
- Changes reflect automatically
- No container restart needed

{{#if HAS_FRONTEND}}**Frontend code changes**:
- Hot reload is enabled
- Changes reflect automatically
- No container restart needed
{{/if}}

**Configuration changes**:
- Requires container restart
- Run: `docker-compose restart backend`

**Dependency changes**:
- Requires rebuild
- Run: `docker-compose up -d --build backend`

---

## Testing in Docker

### Unit Tests

```bash
# Backend tests
docker-compose exec backend {{TEST_COMMAND}}

# With coverage
docker-compose exec backend {{TEST_COMMAND}} --cov

{{#if HAS_FRONTEND}}# Frontend tests
docker-compose exec frontend npm test

# With coverage
docker-compose exec frontend npm test -- --coverage
{{/if}}
```

### Integration Tests

```bash
# Run integration test scripts
docker-compose exec backend python scripts/test_integration.py

# Run specific test
docker-compose exec backend pytest tests/integration/test_api.py
```

---

## Troubleshooting

### Container Won't Start

**Check logs**:
```bash
docker-compose logs backend
```

**Common issues**:
1. Port already in use
2. Missing environment variables
3. Database connection failed
4. Volume permission issues

### Port Already in Use

```bash
# Find process using port (Linux/Mac)
lsof -i :8000

# Find process using port (Windows)
netstat -ano | findstr :8000

# Kill the process
kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows

# Or use different port in docker-compose.yml
```

### Database Connection Issues

```bash
# Check database container
docker-compose ps database

# Check database logs
docker-compose logs database

# Test connection
docker-compose exec backend psql -h database -U postgres

# Verify environment variables
docker-compose exec backend env | grep DATABASE
```

### Performance Issues

```bash
# Check resource usage
docker stats

# Check disk space
docker system df

# Clean up unused resources
docker system prune -a
```

### Reset Everything

```bash
# Stop and remove all containers
docker-compose down

# Remove volumes (⚠️ deletes all data)
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Start fresh
docker-compose up -d --build
```

---

## Best Practices

### Volume Management

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect {{PROJECT_NAME}}_postgres_data

# Backup volume
docker run --rm -v {{PROJECT_NAME}}_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/data-backup.tar.gz /data

# Restore volume
docker run --rm -v {{PROJECT_NAME}}_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/data-backup.tar.gz -C /
```

### Network Management

```bash
# List networks
docker network ls

# Inspect network
docker network inspect {{PROJECT_NAME}}_default

# Test connectivity between containers
docker-compose exec backend ping database
```

### Image Management

```bash
# List images
docker images

# Remove unused images
docker image prune

# Remove specific image
docker rmi {{PROJECT_NAME}}-backend
```

---

## Docker Compose Configuration

### Environment Variables

Create `.env` file:

```env
# Database
DATABASE_URL=postgresql://postgres:password@database:5432/{{PROJECT_NAME}}

# Redis
REDIS_URL=redis://cache:6379/0

# Application
SECRET_KEY=your-secret-key-here
DEBUG=true

# [Add your environment variables]
```

### Custom Configuration

Edit `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./{{BACKEND_FOLDER}}
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
    volumes:
      - ./{{BACKEND_FOLDER}}:/app
    depends_on:
      - database

  # [Add your services]
```

---

## Production Considerations

### Security

- [ ] Don't expose unnecessary ports
- [ ] Use secrets for sensitive data
- [ ] Run containers as non-root user
- [ ] Keep images updated
- [ ] Scan images for vulnerabilities

### Performance

- [ ] Use multi-stage builds
- [ ] Optimize image size
- [ ] Use specific image tags (not `latest`)
- [ ] Configure resource limits
- [ ] Use production-optimized base images

### Monitoring

```bash
# Resource usage
docker stats

# Container health
docker-compose ps

# Application logs
docker-compose logs -f --tail=100
```

---

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

**Last Updated**: {{CURRENT_DATE}}
**Status**: Living Document
