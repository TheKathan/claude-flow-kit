# Python Development Guide

**Version**: 1.0
**Last Updated**: {{CURRENT_DATE}}

---

## Overview

This guide outlines Python coding standards, best practices, and patterns for {{PROJECT_NAME}}. All Python code must follow these guidelines to ensure consistency, maintainability, and quality.

---

## Code Style

### PEP 8 Compliance

All Python code must follow [PEP 8](https://pep8.org/) style guide.

**Enforced by**: black, ruff, flake8

```python
# Good: PEP 8 compliant
def calculate_total_price(items: list[dict], tax_rate: float = 0.08) -> float:
    """Calculate total price including tax."""
    subtotal = sum(item["price"] * item["quantity"] for item in items)
    return subtotal * (1 + tax_rate)

# Bad: Not PEP 8 compliant
def calculateTotalPrice(items,taxRate=0.08):
    subtotal=sum([item['price']*item['quantity'] for item in items])
    return subtotal*(1+taxRate)
```

### Import Order

1. Standard library imports
2. Related third-party imports
3. Local application/library specific imports

**Enforced by**: isort

```python
# Good: Properly ordered imports
import os
import sys
from typing import Optional

from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import User
from app.schemas import UserCreate
```

---

## Type Hints

### Always Use Type Hints

All function signatures must include type hints for parameters and return values.

```python
# Good: Full type hints
def get_user_by_email(email: str, db: AsyncSession) -> Optional[User]:
    """Get user by email address."""
    pass

async def create_user(user_data: UserCreate, db: AsyncSession) -> User:
    """Create a new user."""
    pass

# Bad: No type hints
def get_user_by_email(email, db):
    pass
```

### Complex Types

Use `typing` module for complex types.

```python
from typing import List, Dict, Optional, Union, Tuple, Any
from collections.abc import Sequence

# Good: Clear type definitions
def process_users(
    user_ids: list[int],
    filters: dict[str, Any],
    options: Optional[dict[str, bool]] = None
) -> list[dict[str, Any]]:
    pass
```

---

## Async/Await Patterns

### Use Async for I/O Operations

All I/O operations (database, HTTP, file) should be async.

```python
# Good: Async I/O
async def get_user(user_id: int, db: AsyncSession) -> Optional[User]:
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()

# Bad: Synchronous I/O in async context
async def get_user(user_id: int, db: AsyncSession) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()  # Blocking!
```

### Gather for Parallel Operations

```python
# Good: Parallel async operations
async def get_user_data(user_id: int, db: AsyncSession) -> dict:
    user_task = get_user(user_id, db)
    posts_task = get_user_posts(user_id, db)
    followers_task = get_user_followers(user_id, db)

    user, posts, followers = await asyncio.gather(
        user_task, posts_task, followers_task
    )

    return {"user": user, "posts": posts, "followers": followers}
```

---

## FastAPI Patterns

### Dependency Injection

Use FastAPI's dependency injection system.

```python
# Good: Dependency injection
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

@router.post("/users")
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    pass
```

### Request/Response Models

Always use Pydantic models for request/response validation.

```python
# Good: Pydantic models
from pydantic import BaseModel, EmailStr, constr

class UserCreate(BaseModel):
    email: EmailStr
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=8)

class UserResponse(BaseModel):
    id: int
    email: str
    username: str

    model_config = ConfigDict(from_attributes=True)

@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user_data: UserCreate) -> UserResponse:
    pass
```

### Exception Handling

Use FastAPI HTTPException for API errors.

```python
# Good: Proper exception handling
from fastapi import HTTPException, status

async def get_user(user_id: int, db: AsyncSession) -> User:
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return user
```

---

## SQLAlchemy Patterns

### Async Session Management

Always use async sessions with proper context management.

```python
# Good: Async session with context manager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine("postgresql+asyncpg://...")
async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### Query Patterns

Use select() for queries, avoid legacy query() API.

```python
# Good: Modern SQLAlchemy 2.0 style
from sqlalchemy import select

async def get_users_by_status(status: str, db: AsyncSession) -> list[User]:
    result = await db.execute(
        select(User).where(User.status == status).order_by(User.created_at)
    )
    return list(result.scalars().all())

# Bad: Legacy query API
async def get_users_by_status(status: str, db: AsyncSession) -> list[User]:
    return db.query(User).filter(User.status == status).all()  # Deprecated
```

### Avoid N+1 Queries

Use selectinload() or joinedload() for relationships.

```python
# Good: Eager loading
from sqlalchemy.orm import selectinload

async def get_user_with_posts(user_id: int, db: AsyncSession) -> Optional[User]:
    result = await db.execute(
        select(User)
        .options(selectinload(User.posts))
        .where(User.id == user_id)
    )
    return result.scalar_one_or_none()

# Bad: N+1 query problem
async def get_user_with_posts(user_id: int, db: AsyncSession) -> Optional[User]:
    user = await db.get(User, user_id)
    if user:
        # This triggers N additional queries!
        posts = [post for post in user.posts]
    return user
```

---

## Error Handling

### Explicit Error Handling

Always handle expected errors explicitly.

```python
# Good: Explicit error handling
from sqlalchemy.exc import IntegrityError

async def create_user(user_data: UserCreate, db: AsyncSession) -> User:
    user = User(**user_data.model_dump())
    db.add(user)

    try:
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError as e:
        await db.rollback()
        if "unique constraint" in str(e).lower():
            raise HTTPException(
                status_code=409,
                detail="User with this email already exists"
            )
        raise HTTPException(status_code=500, detail="Database error")
```

### Custom Exceptions

Create custom exceptions for domain-specific errors.

```python
# Good: Custom exceptions
class UserNotFoundError(Exception):
    """Raised when user is not found."""
    pass

class DuplicateUserError(Exception):
    """Raised when attempting to create duplicate user."""
    pass

# In service layer
async def get_user_or_raise(user_id: int, db: AsyncSession) -> User:
    user = await db.get(User, user_id)
    if not user:
        raise UserNotFoundError(f"User {user_id} not found")
    return user

# In API layer
@router.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        user = await get_user_or_raise(user_id, db)
        return UserResponse.model_validate(user)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

---

## Documentation

### Docstrings

Use Google-style docstrings for all public functions, classes, and modules.

```python
def calculate_discount(price: float, discount_percent: float) -> float:
    """Calculate discounted price.

    Args:
        price: Original price of the item
        discount_percent: Discount percentage (0-100)

    Returns:
        Discounted price rounded to 2 decimal places

    Raises:
        ValueError: If discount_percent is not in range 0-100

    Examples:
        >>> calculate_discount(100.0, 20.0)
        80.0
    """
    if not 0 <= discount_percent <= 100:
        raise ValueError("Discount must be between 0 and 100")

    discount = price * (discount_percent / 100)
    return round(price - discount, 2)
```

---

## Testing

### pytest Best Practices

```python
# Good: Clear test structure with AAA pattern
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_user_success(async_client: AsyncClient, db_session):
    """Test successful user creation."""
    # Arrange
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "SecurePass123!"
    }

    # Act
    response = await async_client.post("/api/users", json=user_data)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "password" not in data

@pytest.fixture
async def test_user(db_session):
    """Fixture for creating a test user."""
    user = User(email="test@example.com", username="testuser")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user
```

---

## Security

### Input Validation

Always validate and sanitize inputs.

```python
# Good: Pydantic validation
from pydantic import BaseModel, EmailStr, validator

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v
```

### SQL Injection Prevention

Always use parameterized queries.

```python
# Good: Parameterized query
async def get_user_by_email(email: str, db: AsyncSession) -> Optional[User]:
    result = await db.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()

# Bad: String formatting (SQL injection risk!)
async def get_user_by_email(email: str, db: AsyncSession) -> Optional[User]:
    query = f"SELECT * FROM users WHERE email = '{email}'"  # NEVER DO THIS!
    result = await db.execute(query)
    return result.first()
```

---

## Common Patterns

### Context Managers

Use context managers for resource management.

```python
# Good: Context manager
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_redis_connection():
    redis = await aioredis.create_redis_pool("redis://localhost")
    try:
        yield redis
    finally:
        redis.close()
        await redis.wait_closed()

async with get_redis_connection() as redis:
    await redis.set("key", "value")
```

### Enums for Constants

Use Enums for related constants.

```python
# Good: Enum for constants
from enum import Enum

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"

class User(Base):
    status: Mapped[str] = mapped_column(default=UserStatus.ACTIVE.value)
```

---

## Tools Configuration

### pyproject.toml

```toml
[tool.black]
line-length = 100
target-version = ['py311']

[tool.isort]
profile = "black"
line_length = 100

[tool.ruff]
line-length = 100
select = ["E", "F", "W", "I", "N"]

[tool.mypy]
python_version = "3.11"
strict = true
ignore_missing_imports = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

---

## Resources

- [PEP 8](https://pep8.org/) - Style Guide for Python Code
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [pytest Documentation](https://docs.pytest.org/)

---

**Last Updated**: {{CURRENT_DATE}}
