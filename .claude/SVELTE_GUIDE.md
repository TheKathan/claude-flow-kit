# Svelte / SvelteKit Development Guide - {{PROJECT_NAME}}

## Core Philosophy

Write **idiomatic Svelte 5** code: use runes, prefer server-side logic in SvelteKit load functions and form actions, and keep components small and composable.

---

## Project Structure

```
src/
├── lib/
│   ├── components/     # Reusable Svelte components
│   ├── stores/         # Svelte stores (cross-component state)
│   ├── utils/          # Pure utility functions
│   └── types.ts        # Shared TypeScript types
├── routes/
│   ├── +layout.svelte  # Root layout
│   ├── +page.svelte    # Home page
│   └── [route]/
│       ├── +page.svelte        # Page component
│       ├── +page.server.ts     # Server load + form actions
│       └── +page.ts            # Universal load (client+server)
└── app.html            # HTML shell
```

---

## Svelte 5 Runes

### State and Derived

```svelte
<script lang="ts">
  let count = $state(0)
  let doubled = $derived(count * 2)
  let label = $derived(count === 1 ? 'item' : 'items')

  $effect(() => {
    document.title = `${count} ${label}`
  })
</script>

<button onclick={() => count++}>
  {count} {label} (doubled: {doubled})
</button>
```

### Props

```svelte
<script lang="ts">
  interface Props {
    title: string
    count?: number
    onSelect?: (id: number) => void
  }

  let { title, count = 0, onSelect }: Props = $props()
</script>
```

### Bindable Props

```svelte
<script lang="ts">
  let { value = $bindable('') }: { value?: string } = $props()
</script>

<input bind:value />
```

---

## SvelteKit Patterns

### Load Functions

```typescript
// +page.server.ts — runs only on server
import type { PageServerLoad } from './$types'
import { error } from '@sveltejs/kit'

export const load: PageServerLoad = async ({ params, locals, fetch }) => {
  const res = await fetch(`/api/products/${params.id}`)
  if (!res.ok) throw error(404, 'Not found')
  return { product: await res.json() }
}
```

### Form Actions

```typescript
// +page.server.ts
import { fail, redirect } from '@sveltejs/kit'
import type { Actions } from './$types'

export const actions: Actions = {
  default: async ({ request, locals }) => {
    const data = await request.formData()
    const name = String(data.get('name') ?? '').trim()
    if (!name) return fail(400, { name, error: 'Name is required' })

    await db.product.create({ data: { name } })
    redirect(303, '/products')
  }
}
```

```svelte
<!-- +page.svelte -->
<script lang="ts">
  import type { ActionData } from './$types'
  let { form }: { form: ActionData } = $props()
</script>

<form method="POST">
  <input name="name" value={form?.name ?? ''} />
  {#if form?.error}<p class="error">{form.error}</p>{/if}
  <button type="submit">Create</button>
</form>
```

### API Routes

```typescript
// src/routes/api/products/+server.ts
import { json } from '@sveltejs/kit'
import type { RequestHandler } from './$types'

export const GET: RequestHandler = async ({ url }) => {
  const page = Number(url.searchParams.get('page') ?? 1)
  const products = await db.product.findMany({ skip: (page - 1) * 20, take: 20 })
  return json(products)
}

export const POST: RequestHandler = async ({ request }) => {
  const body = await request.json()
  const product = await db.product.create({ data: body })
  return json(product, { status: 201 })
}
```

---

## State Management

### Local State (runes)

Use `$state` inside a component for state that doesn't need to be shared.

### Shared State (stores)

```typescript
// src/lib/stores/auth.ts
import { writable, derived } from 'svelte/store'

export const user = writable<User | null>(null)
export const isLoggedIn = derived(user, $user => $user !== null)

export function logout() {
  user.set(null)
}
```

### Context API (component tree scope)

```typescript
// parent component
import { setContext } from 'svelte'
setContext('theme', { primary: '#3b82f6' })

// child component
import { getContext } from 'svelte'
const theme = getContext<Theme>('theme')
```

---

## TypeScript Standards

- Strict mode enabled in `tsconfig.json` — no implicit `any`
- Type all `$props()`, load function returns, and form action data
- Use `$types` imports from SvelteKit for `PageData`, `ActionData`, `LayoutData`
- Prefer `interface` over `type` for object shapes

---

## Testing

```bash
npx vitest run              # Run all tests
npx vitest run --coverage   # With coverage report
npx vitest                  # Watch mode
```

**80%+ coverage required** — see `docs/WORKFLOW_FRONTEND_SVELTE.md`.

---

## DO

- Use Svelte 5 runes (`$state`, `$derived`, `$effect`) for all new components
- Put server-only logic in `+page.server.ts` — never expose secrets in `+page.ts`
- Use form actions over `fetch` for mutations — better progressive enhancement
- Use semantic HTML for accessibility
- Validate all inputs server-side

## DON'T

- Use `{@html}` with user-generated content — XSS risk
- Store auth tokens in `localStorage` — use `httpOnly` cookies
- Put secrets or DB access in `+page.ts` (runs on client too)
- Compute values in templates — use `$derived` instead
- Use the legacy Options API (`export let`, `$:`) in new code

---

**Last Updated**: {{CURRENT_DATE}}
