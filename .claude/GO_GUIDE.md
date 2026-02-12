# Go Development Guide

**Version**: 1.0
**Last Updated**: {{CURRENT_DATE}}

---

## Overview

This guide outlines Go coding standards following Effective Go principles for {{PROJECT_NAME}}.

---

## Project Structure

```
cmd/
  api/
    main.go           # Entry point
internal/
  handlers/           # HTTP handlers
  services/           # Business logic
  models/             # Data models
  repository/         # Data access
pkg/                  # Reusable packages
```

---

## Error Handling

### Always Handle Errors

```go
// Good: Explicit error handling
func GetUser(ctx context.Context, id string) (*User, error) {
    user, err := repo.FindByID(ctx, id)
    if err != nil {
        if errors.Is(err, sql.ErrNoRows) {
            return nil, ErrUserNotFound
        }
        return nil, fmt.Errorf("failed to get user: %w", err)
    }
    return user, nil
}

// Bad: Ignored errors
func GetUser(ctx context.Context, id string) *User {
    user, _ := repo.FindByID(ctx, id) // NEVER ignore errors!
    return user
}
```

### Custom Error Types

```go
type ErrNotFound struct {
    Resource string
    ID       string
}

func (e *ErrNotFound) Error() string {
    return fmt.Sprintf("%s with ID %s not found", e.Resource, e.ID)
}

var ErrUserNotFound = &ErrNotFound{Resource: "User"}
```

---

## Interfaces

### Small Interfaces

```go
// Good: Small, focused interfaces
type UserRepository interface {
    Create(ctx context.Context, user *User) error
    FindByID(ctx context.Context, id string) (*User, error)
    Update(ctx context.Context, user *User) error
}

// Composition
type UserService interface {
    UserRepository
    Authenticate(ctx context.Context, email, password string) (*User, error)
}
```

---

## Goroutines and Concurrency

### Context Propagation

```go
// Good: Context for cancellation
func ProcessUsers(ctx context.Context, userIDs []string) error {
    for _, id := range userIDs {
        select {
        case <-ctx.Done():
            return ctx.Err()
        default:
            if err := processUser(ctx, id); err != nil {
                return err
            }
        }
    }
    return nil
}
```

### Avoid Goroutine Leaks

```go
// Good: Wait for goroutines
func FetchData(ctx context.Context) ([]Data, error) {
    var wg sync.WaitGroup
    dataChan := make(chan Data, 10)
    errChan := make(chan error, 1)

    wg.Add(3)
    for i := 0; i < 3; i++ {
        go func(id int) {
            defer wg.Done()
            data, err := fetch(ctx, id)
            if err != nil {
                select {
                case errChan <- err:
                default:
                }
                return
            }
            dataChan <- data
        }(i)
    }

    go func() {
        wg.Wait()
        close(dataChan)
        close(errChan)
    }()

    var results []Data
    for data := range dataChan {
        results = append(results, data)
    }

    if err := <-errChan; err != nil {
        return nil, err
    }
    return results, nil
}
```

---

## HTTP Handlers

```go
// Good: Proper handler structure
func (h *UserHandler) CreateUser(w http.ResponseWriter, r *http.Request) {
    var req CreateUserRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        respondError(w, http.StatusBadRequest, "invalid request body")
        return
    }

    user, err := h.userService.CreateUser(r.Context(), &req)
    if err != nil {
        switch {
        case errors.Is(err, ErrUserExists):
            respondError(w, http.StatusConflict, "user already exists")
        default:
            respondError(w, http.StatusInternalServerError, "failed to create user")
        }
        return
    }

    respondJSON(w, http.StatusCreated, user)
}
```

---

## Testing

### Table-Driven Tests

```go
func TestValidateEmail(t *testing.T) {
    tests := []struct {
        name    string
        email   string
        wantErr bool
    }{
        {"valid email", "test@example.com", false},
        {"missing @", "testexample.com", true},
        {"missing domain", "test@", true},
        {"empty", "", true},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            err := ValidateEmail(tt.email)
            if (err != nil) != tt.wantErr {
                t.Errorf("ValidateEmail() error = %v, wantErr %v", err, tt.wantErr)
            }
        })
    }
}
```

---

## Resources

- [Effective Go](https://golang.org/doc/effective_go)
- [Go Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments)
- [Go Proverbs](https://go-proverbs.github.io/)

---

**Last Updated**: {{CURRENT_DATE}}
