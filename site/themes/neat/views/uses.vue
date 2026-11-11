<script setup lang="ts">
// Uses, laid out as a keyboard: a row of keycaps, one per group, that jump to the group; then each group as a card,
// every tool on a keycap of its own. Tools I built are marked. The data is the page's `tools` grid.
import { computed } from 'vue'
import type { PagesPage } from '@site/types'
import ArtBanner from '../components/ArtBanner.vue'
import PageBody from '../components/PageBody.vue'
import PageHeading from '../components/PageHeading.vue'
import { vReveal, vSpotlight } from '../lib/motion'
import { linkTag } from '../lib/links'

const props = defineProps<{ page: PagesPage }>()

const slug = (text: string) =>
  text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '')
const initials = (name: string) => {
  const words = name
    .replace(/[^A-Za-z0-9 ]/g, ' ')
    .split(/\s+/)
    .filter(Boolean)
  return (words.length > 1 ? words[0][0] + words[1][0] : name.slice(0, 2)).replace(/^./, (c) => c.toUpperCase())
}

// Grid rows arrive loosely typed; read each into the shape the page draws.
const tools = computed(() =>
  (props.page.tools ?? []).map((row, index) => ({
    id: String(row.id ?? index),
    group: String(row.group ?? 'Other'),
    name: String(row.name ?? ''),
    note: row.note ? String(row.note) : '',
    url: row.url ? String(row.url) : '',
    mine: Boolean(row.mine),
    key: row.key ? String(row.key) : '',
  })),
)
type Tool = (typeof tools.value)[number]

const groups = computed(() => {
  const map = new Map<string, Tool[]>()
  for (const tool of tools.value) map.set(tool.group, [...(map.get(tool.group) ?? []), tool])
  return [...map.entries()].map(([name, tools]) => ({ name, slug: slug(name), tools }))
})
const mineCount = computed(() => tools.value.filter((tool) => tool.mine).length)
</script>

<template>
  <div>
    <PageHeading :title="page.title" :eyebrow="page.eyebrow" :description="page.intro" />

    <ArtBanner v-if="page.featured_image" :src="page.featured_image.url" eager class="animate-rise mb-14 aspect-[21/8] [animation-delay:200ms]" />

    <!-- The keyboard: one keycap per group. -->
    <nav
      v-if="groups.length"
      aria-label="Tool groups"
      class="animate-rise border-line bg-surface mb-16 rounded-[2rem] border p-4 shadow-[var(--neat-shadow)] [animation-delay:260ms] sm:p-6"
    >
      <div class="text-faint mb-4 flex items-center justify-between gap-4 px-1 font-mono text-xs">
        <span>{{ tools.length }} tools · {{ groups.length }} groups</span>
        <span class="flex items-center gap-2"
          ><span class="size-2 rounded-full bg-accent" aria-hidden="true" />{{ mineCount }} built by me</span
        >
      </div>
      <ul role="list" class="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
        <li v-for="(group, index) in groups" :key="group.slug">
          <a
            :href="`#${group.slug}`"
            class="neat-keycap group flex h-full min-h-24 flex-col justify-between rounded-2xl p-3 sm:min-h-28"
          >
            <span class="text-faint flex items-start justify-between font-mono text-[0.7rem]">
              <span>F{{ index + 1 }}</span>
              <span>{{ group.tools.length }}</span>
            </span>
            <span class="font-display text-lg leading-tight font-extrabold tracking-tight">{{ group.name }}</span>
          </a>
        </li>
      </ul>
    </nav>

    <PageBody v-if="page.content" :content="page.content" class="mb-16" />

    <div class="grid gap-6 lg:grid-cols-2">
      <section
        v-for="(group, index) in groups"
        :id="group.slug"
        :key="group.slug"
        v-reveal="(index % 2) * 100"
        v-spotlight
        :aria-labelledby="`${group.slug}-heading`"
        class="neat-card scroll-mt-28 p-6 sm:p-8"
      >
        <header class="border-line mb-6 flex items-baseline justify-between gap-4 border-b pb-4">
          <h2 :id="`${group.slug}-heading`" class="font-display text-2xl font-extrabold tracking-tight">
            {{ group.name }}
          </h2>
          <span class="text-faint font-mono text-xs">F{{ index + 1 }}</span>
        </header>
        <ul role="list" class="grid gap-5">
          <li v-for="tool in group.tools" :key="tool.id" class="flex gap-4">
            <span
              class="neat-keycap neat-keycap-sm grid size-11 shrink-0 place-items-center rounded-xl font-mono text-sm font-semibold"
              :class="{ 'neat-keycap-mine': tool.mine }"
              aria-hidden="true"
              >{{ tool.key || initials(tool.name) }}</span
            >
            <div class="min-w-0">
              <p class="flex flex-wrap items-center gap-2">
                <component
                  :is="tool.url ? linkTag(tool.url) : 'span'"
                  :href="tool.url || undefined"
                  :target="tool.url && !tool.url.startsWith('/') ? '_blank' : undefined"
                  :rel="tool.url && !tool.url.startsWith('/') ? 'noopener' : undefined"
                  class="font-semibold"
                  :class="{ 'neat-link': tool.url }"
                  >{{ tool.name }}</component
                >
                <span
                  v-if="tool.mine"
                  class="rounded-full bg-accent/12 px-2 py-0.5 font-mono text-[0.65rem] tracking-wider text-accent uppercase"
                  >Built by me</span
                >
              </p>
              <p v-if="tool.note" class="mt-1 leading-7 text-muted">{{ tool.note }}</p>
            </div>
          </li>
        </ul>
      </section>
    </div>
  </div>
</template>
