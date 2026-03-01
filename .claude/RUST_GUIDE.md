# Rust Development Guide

**Version**: 1.0
**Last Updated**: {{CURRENT_DATE}}

---

## Overview

This guide outlines Rust coding standards, best practices, and patterns for {{PROJECT_NAME}}. All Rust code must follow these guidelines to ensure correctness, safety, and performance.

---

## Code Style

### Formatting and Linting

All Rust code must be formatted with `rustfmt` and pass `clippy` with zero warnings.

```bash
cargo fmt                          # Format all code
cargo clippy -- -D warnings        # Lint with zero-warning policy
cargo audit                        # Security vulnerability check
```

### Naming Conventions

- **Types, traits, enums**: `CamelCase`
- **Functions, variables, modules**: `snake_case`
- **Constants and statics**: `SCREAMING_SNAKE_CASE`
- **Lifetimes**: Short, lowercase (`'a`, `'db`, `'ctx`)

---

## Project Structure

```
src/
  main.rs               # Entry point
  lib.rs                # Library root (if applicable)
  handlers/             # HTTP route handlers (Axum)
  services/             # Business logic
  models/               # Domain types
  repository/           # Data access layer
  errors.rs             # Centralized error types
  config.rs             # Configuration structs
tests/                  # Integration tests
```

For Tauri apps:
```
src-tauri/
  src/
    main.rs             # Tauri entry point
    commands/           # Tauri command handlers
    state.rs            # Managed app state
    errors.rs           # Error types
```

---

## Error Handling

### Use `thiserror` for Typed Errors

Never use `unwrap()` or `expect()` in production paths.

```rust
use thiserror::Error;
use axum::{http::StatusCode, response::{IntoResponse, Response}, Json};
use serde_json::json;

#[derive(Debug, Error)]
pub enum AppError {
    #[error("resource not found")]
    NotFound,
    #[error("resource already exists")]
    Conflict,
    #[error("validation error: {0}")]
    Validation(String),
    #[error("database error: {0}")]
    Database(#[from] sqlx::Error),
    #[error("internal error")]
    Internal(#[from] anyhow::Error),
}

impl IntoResponse for AppError {
    fn into_response(self) -> Response {
        let (status, message) = match &self {
            AppError::NotFound => (StatusCode::NOT_FOUND, self.to_string()),
            AppError::Conflict => (StatusCode::CONFLICT, self.to_string()),
            AppError::Validation(msg) => (StatusCode::UNPROCESSABLE_ENTITY, msg.clone()),
            AppError::Database(_) | AppError::Internal(_) => {
                (StatusCode::INTERNAL_SERVER_ERROR, "internal server error".to_string())
            }
        };
        (status, Json(json!({"error": message}))).into_response()
    }
}
```

### Error Propagation

```rust
// Good: propagate with ?
pub async fn get_user(id: i64) -> Result<User, AppError> {
    let user = repo.find_by_id(id).await?.ok_or(AppError::NotFound)?;
    Ok(user)
}

// Bad: panic in production code
pub async fn get_user(id: i64) -> User {
    repo.find_by_id(id).await.unwrap().unwrap() // NEVER DO THIS
}
```

---

## Axum Handler Patterns

```rust
use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    response::Json,
};
use serde::{Deserialize, Serialize};

#[derive(Serialize)]
pub struct UserResponse {
    pub id: i64,
    pub email: String,
    pub username: String,
}

#[derive(Deserialize)]
pub struct CreateUserRequest {
    pub email: String,
    pub username: String,
    pub password: String,
}

pub async fn create_user(
    State(state): State<AppState>,
    Json(req): Json<CreateUserRequest>,
) -> Result<(StatusCode, Json<UserResponse>), AppError> {
    let user = state.user_service.create_user(req).await?;
    Ok((StatusCode::CREATED, Json(user)))
}

pub async fn get_user(
    State(state): State<AppState>,
    Path(user_id): Path<i64>,
) -> Result<Json<UserResponse>, AppError> {
    let user = state.user_service.get_user(user_id).await?;
    Ok(Json(user))
}
```

---

## Ownership and Borrowing

```rust
// Good: borrow when you only need to read
fn process(data: &[u8]) -> usize {
    data.len()
}

// Good: take ownership when you need to transform
fn into_uppercase(s: String) -> String {
    s.to_uppercase()
}

// Good: Arc for shared ownership across async tasks
use std::sync::Arc;
let shared = Arc::new(expensive_resource);
let clone = Arc::clone(&shared);
tokio::spawn(async move { use_resource(clone).await });
```

---

## Async with Tokio

```rust
use tokio::time::{timeout, Duration};

// Always await async functions
pub async fn fetch_data(url: &str) -> Result<String, AppError> {
    let response = timeout(
        Duration::from_secs(10),
        reqwest::get(url),
    )
    .await
    .map_err(|_| AppError::Internal(anyhow::anyhow!("request timed out")))?
    .map_err(anyhow::Error::from)?;

    Ok(response.text().await.map_err(anyhow::Error::from)?)
}

// Use spawn_blocking for CPU-intensive work
pub async fn hash_password(password: String) -> Result<String, AppError> {
    tokio::task::spawn_blocking(move || {
        argon2::hash_encoded(password.as_bytes(), &generate_salt(), &Default::default())
            .map_err(|e| AppError::Internal(anyhow::anyhow!(e)))
    })
    .await
    .map_err(anyhow::Error::from)?
}
```

---

## State Management

```rust
#[derive(Clone)]
pub struct AppState {
    pub db: sqlx::PgPool,
    pub user_service: Arc<dyn UserService + Send + Sync>,
    pub config: Arc<Config>,
}

// Pass state via Axum extractor — never global mutable state
pub async fn handler(State(state): State<AppState>) -> Result<Json<Value>, AppError> {
    // use state.db, state.user_service, etc.
    todo!()
}
```

---

## Security

- Validate all inputs with the `validator` crate
- Use parameterized queries via SQLx (never string interpolation in SQL)
- Hash passwords with `argon2` — never store plaintext
- Use `secrecy::Secret<String>` for sensitive values to prevent accidental logging
- Set request timeouts with `tower::timeout::TimeoutLayer`
- Never use `unsafe` unless absolutely necessary and well-documented

```rust
use secrecy::{Secret, ExposeSecret};
use validator::Validate;

#[derive(Deserialize, Validate)]
pub struct CreateUserRequest {
    #[validate(email)]
    pub email: String,
    #[validate(length(min = 8))]
    pub password: Secret<String>,
}

// Access secret value only when needed
let hash = hash_password(req.password.expose_secret().to_string()).await?;
```

---

## Testing

See the [Testing Guide](../docs/TESTING_GUIDE.md) for full details.

```bash
cargo test                         # Run all tests
cargo test -- --nocapture          # Show println! output
cargo tarpaulin --out Html         # Coverage report
cargo llvm-cov --html              # Alternative coverage tool
```

**Minimum coverage**: 80%

---

## Tools Configuration

### `Cargo.toml` Key Dependencies

```toml
[dependencies]
axum = "0.7"
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
sqlx = { version = "0.7", features = ["postgres", "runtime-tokio-native-tls", "macros"] }
thiserror = "1"
anyhow = "1"
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }
validator = { version = "0.18", features = ["derive"] }
secrecy = "0.8"
tower = "0.4"
tower-http = { version = "0.5", features = ["cors", "trace", "timeout"] }

[dev-dependencies]
mockall = "0.12"
wiremock = "0.6"
axum-test = "14"
rstest = "0.19"
fake = "2"
criterion = "0.5"
```

### `rustfmt.toml`

```toml
edition = "2021"
max_width = 100
use_small_heuristics = "Default"
```

---

## Resources

- [The Rust Book](https://doc.rust-lang.org/book/) — Official Rust documentation
- [Rust by Example](https://doc.rust-lang.org/rust-by-example/) — Code examples
- [Axum Documentation](https://docs.rs/axum) — Web framework docs
- [Tokio Tutorial](https://tokio.rs/tokio/tutorial) — Async runtime guide
- [SQLx Documentation](https://docs.rs/sqlx) — Database access
- [Clippy Lints](https://rust-lang.github.io/rust-clippy/) — Lint reference

---

**Last Updated**: {{CURRENT_DATE}}
