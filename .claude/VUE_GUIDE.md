# Vue Development Guide

**Version**: 1.0
**Last Updated**: {{CURRENT_DATE}}

---

## Component Patterns

### Composition API with TypeScript

```vue
<script setup lang="ts">
import { ref, computed } from 'vue';
import type { User } from '@/types';

interface Props {
  userId: string;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  update: [user: User];
  error: [message: string];
}>();

const user = ref<User | null>(null);
const loading = ref(false);

const fullName = computed(() =>
  user.value ? `${user.value.firstName} ${user.value.lastName}` : ''
);

async function fetchUser() {
  loading.value = true;
  try {
    user.value = await getUserById(props.userId);
    emit('update', user.value);
  } catch (error) {
    emit('error', error.message);
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div>
    <p v-if="loading">Loading...</p>
    <p v-else>{{ fullName }}</p>
  </div>
</template>
```

---

## Composables

```typescript
// composables/useUser.ts
import { ref, Ref } from 'vue';
import type { User } from '@/types';

export function useUser(userId: Ref<string>) {
  const user = ref<User | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function fetchUser() {
    loading.value = true;
    error.value = null;
    try {
      user.value = await getUserById(userId.value);
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed';
    } finally {
      loading.value = false;
    }
  }

  watch(userId, fetchUser, { immediate: true });

  return { user, loading, error, refetch: fetchUser };
}
```

---

## Pinia State Management

```typescript
// stores/user.ts
import { defineStore } from 'pinia';

export const useUserStore = defineStore('user', () => {
  const users = ref<User[]>([]);
  const loading = ref(false);

  async function fetchUsers() {
    loading.value = true;
    try {
      users.value = await getUsers();
    } finally {
      loading.value = false;
    }
  }

  return { users, loading, fetchUsers };
});
```

---

**Last Updated**: {{CURRENT_DATE}}
