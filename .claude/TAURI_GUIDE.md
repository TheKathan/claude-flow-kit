# Tauri Development Guide

**Version**: 1.0
**Last Updated**: {{CURRENT_DATE}}

---

## Overview

This guide outlines development standards for **Tauri** desktop applications in {{PROJECT_NAME}}. Tauri apps combine a **Rust backend** (`src-tauri/`) with a **web frontend** (React, Vue, or another framework). Both layers must meet their respective coding standards.

---

## Architecture

```
project/
  src/                    # Frontend source (React/Vue/Angular)
  src-tauri/              # Tauri Rust backend
    src/
      main.rs             # Tauri entry point
      commands/           # Tauri command handlers
        mod.rs
        files.rs
        settings.rs
      state.rs            # Managed application state
      errors.rs           # Error types
    tauri.conf.json        # Tauri configuration
    Cargo.toml            # Rust dependencies
  package.json            # Frontend dependencies + dev scripts
```

---

## Tauri Commands (Rust Backend)

Commands are the IPC bridge between the frontend and Rust backend.

### Command Pattern

```rust
// src-tauri/src/commands/files.rs
use tauri::{command, AppHandle, State};
use crate::{errors::AppError, state::AppState};
use serde::{Deserialize, Serialize};

#[derive(Serialize)]
pub struct FileInfo {
    pub path: String,
    pub size: u64,
    pub modified: u64,
}

#[derive(Deserialize)]
pub struct ReadFileRequest {
    pub path: String,
}

#[command]
pub async fn read_file(
    req: ReadFileRequest,
    state: State<'_, AppState>,
) -> Result<String, AppError> {
    let content = tokio::fs::read_to_string(&req.path)
        .await
        .map_err(|e| AppError::Io(e))?;
    Ok(content)
}

#[command]
pub async fn list_files(
    directory: String,
    state: State<'_, AppState>,
    app: AppHandle,
) -> Result<Vec<FileInfo>, AppError> {
    // Validate path is within allowed directories
    validate_path(&directory, &state.allowed_dirs)?;

    let entries = tokio::fs::read_dir(&directory)
        .await
        .map_err(|e| AppError::Io(e))?;
    // ... collect entries
    todo!()
}
```

### Error Types for Commands

Tauri commands must return `Result<T, E>` where `E` implements `Serialize`.

```rust
// src-tauri/src/errors.rs
use serde::Serialize;

#[derive(Debug, Serialize, thiserror::Error)]
#[serde(tag = "type", content = "message")]
pub enum AppError {
    #[error("IO error: {0}")]
    Io(String),
    #[error("permission denied: {0}")]
    PermissionDenied(String),
    #[error("not found: {0}")]
    NotFound(String),
    #[error("invalid input: {0}")]
    Validation(String),
    #[error("internal error")]
    Internal(String),
}

impl From<std::io::Error> for AppError {
    fn from(e: std::io::Error) -> Self {
        AppError::Io(e.to_string())
    }
}
```

### Register Commands in main.rs

```rust
// src-tauri/src/main.rs
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod commands;
mod errors;
mod state;

use state::AppState;

fn main() {
    tauri::Builder::default()
        .manage(AppState::new())
        .invoke_handler(tauri::generate_handler![
            commands::files::read_file,
            commands::files::list_files,
            commands::settings::get_settings,
            commands::settings::save_settings,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

---

## Managed State

```rust
// src-tauri/src/state.rs
use std::sync::Mutex;
use serde::{Deserialize, Serialize};

#[derive(Debug, Default, Serialize, Deserialize, Clone)]
pub struct Settings {
    pub theme: String,
    pub language: String,
}

pub struct AppState {
    pub settings: Mutex<Settings>,
    pub allowed_dirs: Vec<std::path::PathBuf>,
}

impl AppState {
    pub fn new() -> Self {
        Self {
            settings: Mutex::new(Settings::default()),
            allowed_dirs: vec![],
        }
    }
}
```

---

## Frontend Integration (JavaScript/TypeScript)

Use the official `@tauri-apps/api` package to call commands.

```typescript
// Frontend: calling a Tauri command
import { invoke } from '@tauri-apps/api/tauri';

interface FileInfo {
  path: string;
  size: number;
  modified: number;
}

async function readFile(path: string): Promise<string> {
  return await invoke<string>('read_file', { req: { path } });
}

async function listFiles(directory: string): Promise<FileInfo[]> {
  return await invoke<FileInfo[]>('list_files', { directory });
}

// Error handling on the frontend
try {
  const content = await readFile('/path/to/file');
} catch (error) {
  // error is the serialized AppError from Rust
  console.error('Failed to read file:', error);
}
```

---

## Security

Tauri provides a security model — use it correctly:

1. **Content Security Policy**: Configure in `tauri.conf.json`
2. **Path validation**: Always validate file paths are within allowed directories
3. **Allowlist**: Only expose necessary Tauri APIs
4. **No shell injection**: Use `tauri::api::process::Command` safely

```json
// tauri.conf.json — restrict API surface
{
  "tauri": {
    "allowlist": {
      "all": false,
      "fs": {
        "all": false,
        "readFile": true,
        "writeFile": true,
        "readDir": true,
        "scope": ["$APP/*", "$DOCUMENT/*"]
      },
      "dialog": {
        "open": true,
        "save": true
      }
    },
    "security": {
      "csp": "default-src 'self'; img-src 'self' data: asset: https://asset.localhost"
    }
  }
}
```

---

## Development Commands

```bash
# Start development server (hot reload for frontend + Rust backend)
npm run tauri dev

# Build for production
npm run tauri build

# Build Rust backend only
cargo build --manifest-path src-tauri/Cargo.toml

# Run Rust tests
cargo test --manifest-path src-tauri/Cargo.toml

# Lint Rust backend
cargo clippy --manifest-path src-tauri/Cargo.toml -- -D warnings

# Format Rust backend
cargo fmt --manifest-path src-tauri/Cargo.toml
```

---

## Testing

### Rust Backend Tests

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn validate_path_rejects_traversal() {
        let allowed = vec![std::path::PathBuf::from("/allowed")];
        let result = validate_path("../../etc/passwd", &allowed);
        assert!(result.is_err());
    }
}
```

### Frontend Tests

Use Vitest (or Jest) with `vi.mock('@tauri-apps/api/tauri')` to mock commands in unit tests.

```typescript
import { vi } from 'vitest';

vi.mock('@tauri-apps/api/tauri', () => ({
  invoke: vi.fn(),
}));

import { invoke } from '@tauri-apps/api/tauri';

test('reads file content', async () => {
  vi.mocked(invoke).mockResolvedValue('file content');
  const content = await readFile('/some/file.txt');
  expect(content).toBe('file content');
  expect(invoke).toHaveBeenCalledWith('read_file', { req: { path: '/some/file.txt' } });
});
```

---

## Resources

- [Tauri Documentation](https://tauri.app/v1/guides/) — Official Tauri docs
- [Tauri API Reference](https://tauri.app/v1/api/js/) — JavaScript API
- [Rust Guide](.claude/RUST_GUIDE.md) — Rust coding standards
- [React Guide](.claude/REACT_GUIDE.md) — Frontend standards (if using React)
- [Vue Guide](.claude/VUE_GUIDE.md) — Frontend standards (if using Vue)

---

**Last Updated**: {{CURRENT_DATE}}
