# React Development Guide

**Version**: 1.0
**Last Updated**: {{CURRENT_DATE}}

---

## Overview

React/Next.js coding standards and best practices for {{PROJECT_NAME}}.

---

## Component Patterns

### Functional Components with TypeScript

```typescript
// Good: Typed functional component
import { FC, ReactNode } from 'react';

interface ButtonProps {
  children: ReactNode;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
  disabled?: boolean;
}

export const Button: FC<ButtonProps> = ({
  children,
  onClick,
  variant = 'primary',
  disabled = false
}) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`btn btn-${variant}`}
    >
      {children}
    </button>
  );
};
```

---

## Hooks Best Practices

### useState and useEffect

```typescript
// Good: Proper hook usage
function UserProfile({ userId }: { userId: string }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchUser() {
      try {
        setLoading(true);
        const data = await getUserById(userId);
        if (!cancelled) {
          setUser(data);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    fetchUser();

    return () => {
      cancelled = true; // Cleanup
    };
  }, [userId]);

  if (loading) return <Spinner />;
  if (error) return <ErrorMessage message={error} />;
  if (!user) return <NotFound />;

  return <div>{user.name}</div>;
}
```

### Custom Hooks

```typescript
// Good: Reusable custom hook
function useUser(userId: string) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchUser() {
      try {
        setLoading(true);
        setError(null);
        const data = await getUserById(userId);
        if (!cancelled) setUser(data);
      } catch (err) {
        if (!cancelled) setError(err as Error);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchUser();
    return () => { cancelled = true; };
  }, [userId]);

  return { user, loading, error };
}

// Usage
function UserProfile({ userId }: { userId: string }) {
  const { user, loading, error } = useUser(userId);
  // ...
}
```

---

## Performance Optimization

### Memoization

```typescript
// Good: Proper memoization
const UserList: FC<{ users: User[] }> = React.memo(({ users }) => {
  return (
    <ul>
      {users.map(user => (
        <UserItem key={user.id} user={user} />
      ))}
    </ul>
  );
});

// useMemo for expensive computations
function DataTable({ data }: { data: Item[] }) {
  const sortedData = useMemo(() => {
    return [...data].sort((a, b) => a.name.localeCompare(b.name));
  }, [data]);

  return <Table data={sortedData} />;
}

// useCallback for stable function references
function UserForm() {
  const [name, setName] = useState('');

  const handleSubmit = useCallback(async (e: FormEvent) => {
    e.preventDefault();
    await saveUser({ name });
  }, [name]);

  return <form onSubmit={handleSubmit}>...</form>;
}
```

---

## Accessibility

### ARIA Attributes

```typescript
// Good: Accessible form
function LoginForm() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');

  return (
    <form aria-label="Login form">
      <label htmlFor="email">Email</label>
      <input
        id="email"
        type="email"
        value={email}
        onChange={e => setEmail(e.target.value)}
        aria-invalid={!!error}
        aria-describedby={error ? 'email-error' : undefined}
      />
      {error && (
        <p id="email-error" role="alert">
          {error}
        </p>
      )}
    </form>
  );
}
```

---

## Testing with React Testing Library

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

describe('UserForm', () => {
  it('should submit form with valid data', async () => {
    const onSubmit = jest.fn();
    const user = userEvent.setup();

    render(<UserForm onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.click(screen.getByRole('button', { name: /submit/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({ email: 'test@example.com' });
    });
  });
});
```

---

## Next.js Patterns

### Server Components

```typescript
// app/users/page.tsx - Server Component
async function UsersPage() {
  const users = await getUsers(); // Direct database/API call

  return (
    <div>
      <h1>Users</h1>
      <UserList users={users} />
    </div>
  );
}

// Client Component when needed
'use client';

export function UserList({ users }: { users: User[] }) {
  const [filter, setFilter] = useState('');

  const filtered = users.filter(u =>
    u.name.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <>
      <input value={filter} onChange={e => setFilter(e.target.value)} />
      {filtered.map(user => <UserCard key={user.id} user={user} />)}
    </>
  );
}
```

---

## Resources

- [React Documentation](https://react.dev/)
- [Next.js Documentation](https://nextjs.org/docs)
- [React Testing Library](https://testing-library.com/react)

---

**Last Updated**: {{CURRENT_DATE}}
