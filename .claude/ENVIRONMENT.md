# Environment Variables - {{PROJECT_NAME}}

**Date**: {{CURRENT_DATE}}

---

## Environment Configuration

This document describes all environment variables used in {{PROJECT_NAME}}.

---

## Required Variables

### Database Configuration

```env
# Database connection URL
DATABASE_URL=postgresql://user:password@host:port/database

# Example for local development
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/{{PROJECT_NAME}}

# Example for Docker
DATABASE_URL=postgresql://postgres:postgres@database:5432/{{PROJECT_NAME}}
```

### Application Configuration

```env
# Secret key for signing tokens/sessions
SECRET_KEY=your-very-secret-key-change-this-in-production

# Application environment (development, staging, production)
ENVIRONMENT=development

# Debug mode (true/false) - MUST be false in production
DEBUG=true

# Application port
PORT=8000
```

### Authentication (if applicable)

```env
# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30

# Session configuration
SESSION_SECRET=your-session-secret
```

---

## Optional Variables

### Caching (Redis)

```env
# Redis connection URL
REDIS_URL=redis://localhost:6379/0

# Redis configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
```

### Email (if applicable)

```env
# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@example.com
```

### External APIs

```env
# [Add your external API credentials]
API_KEY=your-api-key
API_SECRET=your-api-secret
```

### File Storage

```env
# Local file storage
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760  # 10MB in bytes

# AWS S3 (if using cloud storage)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
AWS_BUCKET_NAME=your-bucket-name
```

### Logging

```env
# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Log format (json, text)
LOG_FORMAT=json
```

---

## Environment-Specific Configuration

### Development (.env.development)

```env
# Development settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Local database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/{{PROJECT_NAME}}_dev

# Local Redis
REDIS_URL=redis://localhost:6379/0

# Disable HTTPS locally
FORCE_HTTPS=false
```

### Staging (.env.staging)

```env
# Staging settings
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO

# Staging database
DATABASE_URL=postgresql://user:password@staging-db-host:5432/{{PROJECT_NAME}}_staging

# Staging Redis
REDIS_URL=redis://staging-redis-host:6379/0

# Enable HTTPS
FORCE_HTTPS=true
```

### Production (.env.production)

```env
# Production settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Production database
DATABASE_URL=postgresql://user:password@production-db-host:5432/{{PROJECT_NAME}}

# Production Redis
REDIS_URL=redis://production-redis-host:6379/0

# Security settings
FORCE_HTTPS=true
SECURE_COOKIES=true

# Performance settings
WORKERS=4
THREADS=2
```

---

## Docker Environment Variables

### docker-compose.yml

```yaml
services:
  backend:
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=${DEBUG}
      # Add other variables
    env_file:
      - .env
```

### .env.example

```env
# Copy this to .env and fill in your values

# Database
DATABASE_URL=postgresql://postgres:postgres@database:5432/{{PROJECT_NAME}}

# Application
SECRET_KEY=change-this-in-production
ENVIRONMENT=development
DEBUG=true
PORT=8000

# Redis (optional)
REDIS_URL=redis://cache:6379/0

# [Add other variables with example values]
```

---

## Security Best Practices

### Secrets Management

1. **Never commit secrets to version control**
   ```bash
   # Add .env to .gitignore
   echo ".env" >> .gitignore
   echo ".env.*" >> .gitignore
   echo "!.env.example" >> .gitignore
   ```

2. **Use strong, random secrets**
   ```bash
   # Generate secure random secret
   python -c "import secrets; print(secrets.token_urlsafe(32))"

   # Or using openssl
   openssl rand -base64 32
   ```

3. **Different secrets per environment**
   - Development, staging, and production should use different secrets
   - Never use development secrets in production

4. **Use environment-specific secret management**
   - Local development: `.env` file
   - Production: Use secret management service (AWS Secrets Manager, Azure Key Vault, etc.)

### Environment Variable Validation

Validate required environment variables on startup:

```python
import os

REQUIRED_VARS = [
    "DATABASE_URL",
    "SECRET_KEY",
    "JWT_SECRET_KEY",
]

def validate_environment():
    missing = [var for var in REQUIRED_VARS if not os.getenv(var)]
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

# Call on application startup
validate_environment()
```

---

## Loading Environment Variables

### Python (python-dotenv)

```python
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Access variables
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
```

### Node.js (dotenv)

```javascript
require('dotenv').config();

// Access variables
const DATABASE_URL = process.env.DATABASE_URL;
const SECRET_KEY = process.env.SECRET_KEY;
const DEBUG = process.env.DEBUG === 'true';
```

---

## Troubleshooting

### Variable Not Loading

1. **Check file location**
   - `.env` should be in project root
   - Or specify path: `load_dotenv('.env.development')`

2. **Check file format**
   - No spaces around `=`: `KEY=value` ✅
   - No quotes needed: `KEY=my value` ✅
   - Use quotes for special characters: `KEY="value with spaces"` ✅

3. **Check variable name**
   - Case-sensitive
   - No typos

4. **Check Docker**
   ```bash
   # Verify environment variables in container
   docker-compose exec backend env | grep DATABASE_URL
   ```

### Override Priority

Environment variables are loaded in this order (later overrides earlier):

1. `.env` file
2. `.env.local` file (if exists)
3. Shell environment variables
4. Docker Compose environment section
5. Command-line environment variables

Example:
```bash
# Override DATABASE_URL for one command
DATABASE_URL=postgresql://localhost:5432/test python app.py
```

---

## Resources

- [12-Factor App - Config](https://12factor.net/config)
- [Python dotenv](https://github.com/theskumar/python-dotenv)
- [Node.js dotenv](https://github.com/motdotla/dotenv)

---

**Last Updated**: {{CURRENT_DATE}}
**Status**: Living Document
