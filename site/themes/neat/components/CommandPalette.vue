<script setup lang="ts">
import { router } from '@inertiajs/vue3'
import { computed, nextTick, onBeforeUnmount, onMounted, ref, useTemplateRef, watch } from 'vue'
import ProjectTile from './ProjectTile.vue'

interface PaletteProject {
  id: number | string
  title: string | null
  uri: string | null
  tagline?: string | null
  monogram?: string | null
  accent?: string | null
}

interface Item {
  id: string
  group: string
  title: string
  hint?: string
  href?: string
  external?: boolean
  run?: () => void
  project?: PaletteProject
}

const props = defineProps<{
  projects: PaletteProject[]
  links: { title: string; url: string }[]
  socials: { label: string; url: string }[]
}>()
const emit = defineEmits<{ toggleTheme: [] }>()

const open = ref(false)
// The overlay only exists in the browser: server rendering has no <body> to teleport into, and it starts closed.
const ready = ref(false)
const query = ref('')
const active = ref(0)
const input = useTemplateRef<HTMLInputElement>('input')
const list = useTemplateRef<HTMLElement>('list')
let opener: Element | null = null

const items = computed<Item[]>(() => [
  ...props.links.map((link) => ({ id: `go-${link.url}`, group: 'Go to', title: link.title, href: link.url })),
  ...props.projects.map((project) => ({
    id: `project-${project.id}`,
    group: 'Projects',
    title: project.title ?? '',
    hint: project.tagline ?? undefined,
    href: project.uri ?? undefined,
    project,
  })),
  { id: 'theme', group: 'Actions', title: 'Switch light / dark', hint: 'T', run: () => emit('toggleTheme') },
  {
    id: 'copy',
    group: 'Actions',
    title: 'Copy this page’s link',
    run: () => navigator.clipboard?.writeText(window.location.href),
  },
  ...props.socials.map((social) => ({
    id: `social-${social.url}`,
    group: 'Elsewhere',
    title: social.label,
    hint: social.url.replace(/^https?:\/\//, ''),
    href: social.url,
    external: true,
  })),
])

function score(item: Item, q: string) {
  const haystack = `${item.title} ${item.hint ?? ''} ${item.group}`.toLowerCase()
  if (haystack.includes(q)) return haystack.indexOf(q)
  // Letters in order, like a fuzzy finder.
  let position = 0
  for (const char of q) {
    position = haystack.indexOf(char, position)
    if (position === -1) return -1
    position++
  }
  return 100 + position
}

const results = computed(() => {
  const q = query.value.trim().toLowerCase()
  const found = q
    ? items.value
        .map((item) => ({ item, rank: score(item, q) }))
        .filter(({ rank }) => rank >= 0)
        .sort((a, b) => a.rank - b.rank)
        .map(({ item }) => item)
    : items.value
  if (q)
    found.push({
      id: 'search',
      group: 'Search',
      title: `Search the site for “${query.value.trim()}”`,
      href: `/search?q=${encodeURIComponent(query.value.trim())}`,
    })
  return found
})

const grouped = computed(() => {
  const groups = new Map<string, { item: Item; index: number }[]>()
  results.value.forEach((item, index) => groups.set(item.group, [...(groups.get(item.group) ?? []), { item, index }]))
  return [...groups.entries()]
})

watch(query, () => (active.value = 0))
watch(active, async () => {
  await nextTick()
  list.value?.querySelector('[data-active="true"]')?.scrollIntoView({ block: 'nearest' })
})

async function show() {
  opener = document.activeElement
  open.value = true
  query.value = ''
  await nextTick()
  input.value?.focus()
}

function hide() {
  open.value = false
  if (opener instanceof HTMLElement) opener.focus()
}

function choose(item: Item | undefined) {
  if (!item) return
  hide()
  if (item.run) return item.run()
  if (!item.href) return
  if (item.external) window.open(item.href, '_blank', 'noopener')
  else router.visit(item.href)
}

function onKey(event: KeyboardEvent) {
  if (event.key === 'ArrowDown') {
    event.preventDefault()
    active.value = (active.value + 1) % Math.max(results.value.length, 1)
  } else if (event.key === 'ArrowUp') {
    event.preventDefault()
    active.value = (active.value - 1 + results.value.length) % Math.max(results.value.length, 1)
  } else if (event.key === 'Enter') {
    event.preventDefault()
    choose(results.value[active.value])
  } else if (event.key === 'Escape') {
    hide()
  }
}

function typing(target: EventTarget | null) {
  const el = target as HTMLElement | null
  return !!el && (el.isContentEditable || ['INPUT', 'TEXTAREA', 'SELECT'].includes(el.tagName))
}

function global(event: KeyboardEvent) {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
    event.preventDefault()
    if (open.value) hide()
    else show()
    return
  }
  if (open.value || typing(event.target) || event.metaKey || event.ctrlKey || event.altKey) return
  if (event.key === '/') {
    event.preventDefault()
    show()
  } else if (event.key.toLowerCase() === 't') {
    emit('toggleTheme')
  }
}

onMounted(() => {
  ready.value = true
  document.addEventListener('keydown', global)
})
onBeforeUnmount(() => document.removeEventListener('keydown', global))

defineExpose({ show })
</script>

<template>
  <Teleport v-if="ready" to="body">
    <Transition
      enter-active-class="transition duration-300 ease-[cubic-bezier(0.16,1,0.3,1)]"
      enter-from-class="opacity-0"
      leave-active-class="transition duration-200"
      leave-to-class="opacity-0"
    >
      <div v-if="open" class="bg-midnight/50 fixed inset-0 z-[60] backdrop-blur-sm" @click="hide" />
    </Transition>
    <Transition
      enter-active-class="transition duration-500 ease-[cubic-bezier(0.16,1,0.3,1)]"
      enter-from-class="translate-y-4 scale-[0.97] opacity-0"
      leave-active-class="transition duration-200"
      leave-to-class="translate-y-2 opacity-0"
    >
      <div
        v-if="open"
        role="dialog"
        aria-modal="true"
        aria-label="Command palette"
        class="border-line-strong bg-surface-strong text-ink fixed inset-x-4 top-[12vh] z-[61] mx-auto max-w-xl overflow-hidden rounded-3xl border shadow-2xl shadow-black/40"
        @keydown="onKey"
      >
        <div class="border-line flex items-center gap-3 border-b px-5">
          <svg
            class="size-5 text-accent"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            aria-hidden="true"
          >
            <circle cx="11" cy="11" r="7" />
            <path d="m20 20-3.5-3.5" />
          </svg>
          <input
            ref="input"
            v-model="query"
            type="text"
            role="combobox"
            aria-expanded="true"
            aria-controls="palette-list"
            :aria-activedescendant="results[active] ? `palette-${results[active].id}` : undefined"
            placeholder="Jump to a project, a page, or search…"
            class="placeholder:text-faint min-w-0 flex-1 bg-transparent py-5 text-base outline-none"
          />
          <kbd class="border-line text-faint rounded-md border px-2 py-1 font-mono text-[0.65rem]">esc</kbd>
        </div>
        <div id="palette-list" ref="list" role="listbox" class="max-h-[55vh] overflow-y-auto overscroll-contain p-2">
          <div v-for="[group, entries] in grouped" :key="group" role="group" :aria-label="group" class="pb-2">
            <p class="neat-eyebrow px-3 pt-3 pb-2 !text-[0.65rem]">{{ group }}</p>
            <div
              v-for="{ item, index } in entries"
              :id="`palette-${item.id}`"
              :key="item.id"
              role="option"
              :aria-selected="index === active"
              :data-active="index === active"
              class="flex cursor-pointer items-center gap-3 rounded-2xl px-3 py-2.5 transition-colors"
              :class="index === active ? 'text-ink bg-accent/12' : 'text-muted'"
              @mousemove="active = index"
              @click="choose(item)"
            >
              <ProjectTile
                v-if="item.project"
                :monogram="item.project.monogram"
                :accent="item.project.accent"
                size="size-8"
                text="text-xs"
              />
              <span
                v-else
                class="border-line grid size-8 place-items-center rounded-xl border font-mono text-xs text-accent"
                aria-hidden="true"
                >{{
                  item.group === 'Go to' ? '→' : item.group === 'Elsewhere' ? '↗' : item.group === 'Search' ? '⌕' : '⌘'
                }}</span
              >
              <span class="min-w-0 flex-1">
                <span class="text-ink block truncate font-medium">{{ item.title }}</span>
                <span v-if="item.hint" class="text-faint block truncate text-xs">{{ item.hint }}</span>
              </span>
              <span v-if="index === active" class="font-mono text-xs text-accent" aria-hidden="true">↵</span>
            </div>
          </div>
          <p v-if="!results.length" class="px-4 py-8 text-center text-muted">Nothing matches.</p>
        </div>
        <div class="border-line text-faint flex flex-wrap gap-x-5 gap-y-1 border-t px-5 py-3 font-mono text-[0.65rem]">
          <span>↑↓ move</span><span>↵ open</span><span>/ or ⌘K anywhere</span><span>T theme</span>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
