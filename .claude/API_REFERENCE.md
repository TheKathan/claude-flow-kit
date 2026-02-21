# API Reference - {{PROJECT_NAME}}

**Base URL**: `{{API_BASE_URL}}`
**Authentication**: Update with your auth method (Bearer token, API key, etc.)

---

## Overview

Document your API endpoints here. Replace this template with your actual API documentation.

---

## Authentication

```http
Authorization: Bearer <token>
```

---

## Endpoints

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

---

## Error Responses

All errors follow a consistent format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description"
  }
}
```

| Status | Meaning |
|--------|---------|
| 400 | Bad Request — invalid input |
| 401 | Unauthorized — missing or invalid auth |
| 403 | Forbidden — insufficient permissions |
| 404 | Not Found |
| 422 | Unprocessable Entity — validation failed |
| 500 | Internal Server Error |

---

*Update this file as you build out your API.*
