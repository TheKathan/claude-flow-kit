# Node.js Development Guide

**Version**: 1.0
**Last Updated**: {{CURRENT_DATE}}

---

## Overview

This guide outlines Node.js/TypeScript coding standards and best practices for {{PROJECT_NAME}}.

---

## TypeScript Configuration

### Strict Mode

Always use TypeScript strict mode.

```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "target": "ES2022",
    "module": "commonjs",
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "outDir": "./dist",
    "rootDir": "./src"
  }
}
```

---

## Express Patterns

### Route Handler Structure

```typescript
// Good: Typed route handlers
import { Request, Response, NextFunction } from 'express';
import { CreateUserDto, UserResponseDto } from '../dtos/user.dto';

export class UserController {
  async createUser(
    req: Request<{}, {}, CreateUserDto>,
    res: Response<UserResponseDto>,
    next: NextFunction
  ): Promise<void> {
    try {
      const userData = req.body;
      const user = await this.userService.createUser(userData);
      res.status(201).json(user);
    } catch (error) {
      next(error);
    }
  }
}
```

### Error Handling Middleware

```typescript
// Good: Centralized error handling
export class AppError extends Error {
  constructor(
    public message: string,
    public statusCode: number = 500
  ) {
    super(message);
    this.name = 'AppError';
  }
}

export const errorHandler = (
  err: Error,
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  if (err instanceof AppError) {
    res.status(err.statusCode).json({ error: err.message });
  } else {
    res.status(500).json({ error: 'Internal server error' });
  }
};
```

---

## Async/Await Best Practices

### Always Handle Promises

```typescript
// Good: Proper error handling
async function getUser(id: string): Promise<User> {
  try {
    const user = await userRepository.findById(id);
    if (!user) {
      throw new AppError('User not found', 404);
    }
    return user;
  } catch (error) {
    logger.error('Error fetching user', { id, error });
    throw error;
  }
}

// Bad: Unhandled promise
async function getUser(id: string): Promise<User> {
  return userRepository.findById(id); // What if this rejects?
}
```

---

## Validation with Zod

```typescript
import { z } from 'zod';

export const CreateUserSchema = z.object({
  email: z.string().email(),
  username: z.string().min(3).max(50),
  password: z.string().min(8)
});

export type CreateUserDto = z.infer<typeof CreateUserSchema>;

// In route handler
const userData = CreateUserSchema.parse(req.body);
```

---

## Testing with Jest

```typescript
describe('UserService', () => {
  let userService: UserService;
  let userRepository: jest.Mocked<UserRepository>;

  beforeEach(() => {
    userRepository = {
      create: jest.fn(),
      findByEmail: jest.fn()
    } as any;
    userService = new UserService(userRepository);
  });

  it('should create user successfully', async () => {
    const userData = { email: 'test@example.com', username: 'test' };
    const expectedUser = { id: 1, ...userData };

    userRepository.create.mockResolvedValue(expectedUser);

    const result = await userService.createUser(userData);

    expect(result).toEqual(expectedUser);
    expect(userRepository.create).toHaveBeenCalledWith(userData);
  });
});
```

---

## Environment Configuration

```typescript
// config/env.ts
import { z } from 'zod';

const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']),
  PORT: z.string().transform(Number),
  DATABASE_URL: z.string().url(),
  JWT_SECRET: z.string().min(32)
});

export const env = envSchema.parse(process.env);
```

---

## Security Best Practices

### Input Validation

Always validate and sanitize inputs.

```typescript
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';

// Security middleware
app.use(helmet());
app.use(express.json({ limit: '10mb' }));
app.use(rateLimit({ windowMs: 15 * 60 * 1000, max: 100 }));
```

### SQL Injection Prevention

```typescript
// Good: Parameterized queries
const user = await db.query(
  'SELECT * FROM users WHERE email = $1',
  [email]
);

// Bad: String interpolation
const user = await db.query(
  `SELECT * FROM users WHERE email = '${email}'` // NEVER!
);
```

---

## Resources

- [Node.js Best Practices](https://github.com/goldbergyoni/nodebestpractices)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
- [Express.js Guide](https://expressjs.com/en/guide/routing.html)

---

**Last Updated**: {{CURRENT_DATE}}
