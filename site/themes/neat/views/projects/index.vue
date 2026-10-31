<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import type { ProjectsProject, ViewProps } from '@site/types'
import PageHeading from '../../components/PageHeading.vue'
import ProjectCard from '../../components/ProjectCard.vue'
import { isClient, onlyProjects, statusOf, STATUS_COPY, type Status } from '../../lib/projects'
import { vReveal } from '../../lib/motion'

const props = defineProps<ViewProps['projects/index'] & { page: ProjectsProject }>()

const status = ref<Status | 'all'>('all')
const tech = ref<string | null>(null)
const everything = computed(() => onlyProjects(props.projects))
const view = ref<'products' | 'clients'>('products')
const clientCount = computed(() => everything.value.filter(isClient).length)
const all = computed(() => everything.value.filter((project) => isClient(project) === (view.value === 'clients')))

// ?view=clients opens on client work; the choice is kept in the address so it can be shared.
onMounted(() => {
  if (new URLSearchParams(window.location.search).get('view') === 'clients' && clientCount.value) view.value = 'clients'
})
watch(view, (value) => {
  status.value = 'all'
  tech.value = null
  const url = new URL(window.location.href)
  if (value === 'clients') url.searchParams.set('view', 'clients')
  else url.searchParams.delete('view')
  window.history.replaceState(window.history.state, '', url)
})

const statuses = computed(() =>
  (Object.keys(STATUS_COPY) as Status[])
    .map((key) => ({ key, count: all.value.filter((project) => statusOf(project) === key).length }))
    .filter(({ count }) => count),
)
const stack = computed(() => {
  const counts = new Map<string, number>()
  all.value.forEach((project) => project.stack?.forEach((item) => counts.set(item, (counts.get(item) ?? 0) + 1)))
  return [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])).map(([item]) => item)
})
const shown = computed(() =>
  all.value.filter(
    (project) =>
      (status.value === 'all' || statusOf(project) === status.value) &&
      (!tech.value || project.stack?.includes(tech.value)),
  ),
)
</script>

<template>
  <div>
    <PageHeading :title="page.title" :eyebrow="page.tagline ?? 'Work'" :description="page.description" />

    <div
      v-if="clientCount"
      class="animate-rise border-line-strong bg-surface relative mb-8 inline-grid grid-cols-2 rounded-full border p-1 backdrop-blur [animation-delay:200ms]"
      role="tablist"
      aria-label="Kind of work"
    >
      <span
        class="bg-ink absolute inset-y-1 left-1 w-[calc(50%-0.25rem)] rounded-full transition-transform duration-500 ease-[cubic-bezier(0.16,1,0.3,1)]"
        :class="view === 'clients' ? 'translate-x-full' : ''"
        aria-hidden="true"
      />
      <button
        v-for="option in [
          { key: 'products', label: 'My products' },
          { key: 'clients', label: 'Client work' },
        ] as const"
        :key="option.key"
        type="button"
        role="tab"
        :aria-selected="view === option.key"
        class="relative z-10 rounded-full px-5 py-2.5 text-sm font-semibold transition-colors duration-300"
        :class="view === option.key ? 'text-canvas' : 'hover:text-ink text-muted'"
        @click="view = option.key"
      >
        {{ option.label }}
      </button>
    </div>

    <div class="animate-rise mb-10 grid gap-4 [animation-delay:240ms]" role="group" aria-label="Filter projects">
      <div class="flex flex-wrap gap-2">
        <button
          type="button"
          class="rounded-full border px-4 py-2 text-sm font-medium transition-all duration-300"
          :class="
            status === 'all' ? 'border-ink bg-ink text-canvas' : 'border-line-strong text-muted hover:border-accent'
          "
          :aria-pressed="status === 'all'"
          @click="status = 'all'"
        >
          Everything <span class="ml-1 font-mono text-xs opacity-60">{{ all.length }}</span>
        </button>
        <button
          v-for="option in statuses"
          :key="option.key"
          type="button"
          class="rounded-full border px-4 py-2 text-sm font-medium transition-all duration-300"
          :class="
            status === option.key
              ? 'border-ink bg-ink text-canvas'
              : 'border-line-strong text-muted hover:border-accent'
          "
          :aria-pressed="status === option.key"
          @click="status = option.key"
        >
          {{ STATUS_COPY[option.key].label }} <span class="ml-1 font-mono text-xs opacity-60">{{ option.count }}</span>
        </button>
      </div>
      <div class="flex flex-wrap gap-1.5">
        <button
          v-for="item in stack"
          :key="item"
          type="button"
          class="rounded-full px-3 py-1 font-mono text-xs transition-colors"
          :class="tech === item ? 'text-accent-ink bg-accent' : 'bg-accent/8 text-muted hover:bg-accent/15'"
          :aria-pressed="tech === item"
          @click="tech = tech === item ? null : item"
        >
          {{ item }}
        </button>
      </div>
    </div>

    <TransitionGroup
      tag="div"
      class="relative grid gap-5 md:grid-cols-2 lg:grid-cols-3"
      move-class="transition-transform duration-700 ease-[cubic-bezier(0.16,1,0.3,1)]"
      enter-active-class="transition duration-500 ease-[cubic-bezier(0.16,1,0.3,1)]"
      enter-from-class="scale-95 opacity-0"
      leave-active-class="absolute transition duration-300"
      leave-to-class="scale-95 opacity-0"
    >
      <div v-for="(project, position) in shown" :key="project.id" v-reveal="(position % 3) * 100">
        <ProjectCard :project="project" :eager="position < 3" />
      </div>
    </TransitionGroup>
    <p v-if="!shown.length" class="py-16 text-center text-lg text-muted">
      Nothing matches that combination.
      <button type="button" class="text-accent underline" @click="((status = 'all'), (tech = null))">
        Show everything
      </button>
    </p>
  </div>
</template>
