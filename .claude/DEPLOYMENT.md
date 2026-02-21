# Deployment Guide - {{PROJECT_NAME}}

**Date**: {{CURRENT_DATE}}

---

## Overview

This document describes the deployment process for {{PROJECT_NAME}}.

---

## Environments

| Environment | Branch | URL |
|-------------|--------|-----|
| Development | feature/* | localhost |
| Staging | {{MAIN_BRANCH}} | TBD |
| Production | release/* | TBD |

---

## Prerequisites

- Access to deployment environment
- Required secrets and environment variables configured
- Docker installed (if applicable)

---

## Deployment Steps

### 1. Build

```bash
# Build the application
{{#if USES_DOCKER}}
docker-compose build
{{else}}
# Add build command here
{{/if}}
```

### 2. Run Tests

```bash
# Ensure all tests pass before deploying
# See docs/TESTING_GUIDE.md for test commands
```

### 3. Deploy

```bash
# Add deployment commands here
```

### 4. Verify

```bash
# Verify the deployment is healthy
# Check logs, health endpoints, etc.
```

---

## Environment Variables

See [Environment Variables](ENVIRONMENT.md) for a full list of required configuration.

---

## Rollback

```bash
# Add rollback procedure here
```

---

## Monitoring

- Add monitoring/observability links here
- Log aggregation
- Alerts

---

**Last Updated**: {{CURRENT_DATE}}
