# Angular Development Guide

**Version**: 1.0
**Last Updated**: {{CURRENT_DATE}}

---

## Component Patterns

```typescript
// user.component.ts
import { Component, Input, Output, EventEmitter, OnInit, OnDestroy } from '@angular/core';
import { Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-user',
  templateUrl: './user.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class UserComponent implements OnInit, OnDestroy {
  @Input() userId!: string;
  @Output() userLoaded = new EventEmitter<User>();

  user$ = this.userService.getUser(this.userId);
  private destroy$ = new Subject<void>();

  constructor(private userService: UserService) {}

  ngOnInit() {
    this.user$
      .pipe(takeUntil(this.destroy$))
      .subscribe(user => this.userLoaded.emit(user));
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
```

---

## Services

```typescript
@Injectable({ providedIn: 'root' })
export class UserService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getUsers(): Observable<User[]> {
    return this.http.get<User[]>(`${this.apiUrl}/users`);
  }

  createUser(user: CreateUserDto): Observable<User> {
    return this.http.post<User>(`${this.apiUrl}/users`, user);
  }
}
```

---

## RxJS Patterns

```typescript
// Good: Proper subscription management
@Component({...})
export class UserListComponent implements OnInit, OnDestroy {
  users$ = this.userService.getUsers().pipe(
    map(users => users.filter(u => u.active)),
    shareReplay(1)
  );

  private destroy$ = new Subject<void>();

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }
}

// In template: Use async pipe
<div *ngFor="let user of users$ | async">{{ user.name }}</div>
```

---

**Last Updated**: {{CURRENT_DATE}}
