<script setup lang="ts">
import { Link } from '@inertiajs/vue3'
import { computed } from 'vue'
import type { ProjectsProject, ViewProps } from '@site/types'
import Corners from '../../components/Corners.vue'
import Peel, { peelCut } from '../../components/Peel.vue'
import ProjectTile from '../../components/ProjectTile.vue'
import Prose from '../../components/Prose.vue'
import StatusPill from '../../components/StatusPill.vue'
import { vReveal, vTilt } from '../../lib/motion'
import { hostOf, isClient, onlyProjects, statusLabel, statusOf } from '../../lib/projects'
import ArrowIcon from '../../components/ArrowIcon.vue'

const props = defineProps<ViewProps['projects/show'] & { page: ProjectsProject }>()

const list = computed(() => onlyProjects(props.siblings))
const position = computed(() => list.value.findIndex((project) => project.uri === props.page.uri))
const next = computed(() => list.value[(position.value + 1) % list.value.length])
const previous = computed(() => list.value[(position.value - 1 + list.value.length) % list.value.length])
const facts = computed(() =>
  [
    { label: 'Status', value: null as string | null, status: true },
    { label: 'Client', value: isClient(props.page) ? props.page.client : null },
    { label: 'Role', value: props.page.role },
    { label: 'What', value: props.page.kind },
    { label: 'Year', value: props.page.year },
  ].filter((fact) => fact.status || fact.value),
)
</script>

<template>
  <article>
    <nav aria-label="Breadcrumb" class="animate-rise text-faint mb-8 font-mono text-xs">
      <Link :href="isClient(page) ? '/projects?view=clients' : '/projects'" class="neat-link hover:text-accent">{{
        isClient(page) ? 'Client work' : 'Work'
      }}</Link>
      <span class="mx-2" aria-hidden="true">/</span>
      <span aria-current="page" class="text-muted">{{ page.title }}</span>
    </nav>

    <header class="grid items-end gap-10 lg:grid-cols-[1.3fr_1fr]">
      <div>
        <div class="animate-rise flex items-center gap-5">
          <ProjectTile
            :logo="page.logo?.url"
            :monogram="page.monogram"
            :accent="page.accent"
            size="size-20 sm:size-24"
            text="text-3xl sm:text-4xl"
          />
          <StatusPill :status="statusOf(page)" :label="statusLabel(page)" />
          <span
            v-if="isClient(page)"
            class="bg-mint text-abyss rounded-full px-3 py-1 font-mono text-[0.7rem] tracking-wider uppercase"
            >Client work</span
          >
        </div>
        <h1
          class="animate-rise font-display mt-8 text-6xl font-extrabold tracking-[-0.045em] [animation-delay:80ms] sm:text-8xl"
        >
          {{ page.title }}
        </h1>
        <p
          v-if="page.tagline"
          class="animate-rise mt-6 max-w-[40ch] text-xl leading-9 text-pretty text-muted [animation-delay:160ms] sm:text-2xl sm:leading-10"
        >
          {{ page.tagline }}
        </p>
      </div>
      <div class="animate-rise flex flex-wrap gap-3 [animation-delay:240ms] lg:justify-end">
        <a v-if="page.website" :href="page.website" class="neat-button" rel="noopener" target="_blank"
          >Visit {{ hostOf(page.website) }} <span aria-hidden="true">↗</span></a
        >
        <a v-if="page.repository" :href="page.repository" class="neat-button-ghost" rel="noopener" target="_blank">
          <svg class="size-4" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path
              d="M12 .5a11.5 11.5 0 0 0-3.64 22.41c.58.1.79-.25.79-.56v-2c-3.2.7-3.88-1.37-3.88-1.37-.52-1.33-1.28-1.68-1.28-1.68-1.05-.72.08-.7.08-.7 1.16.08 1.77 1.19 1.77 1.19 1.03 1.77 2.7 1.26 3.36.96.1-.75.4-1.26.73-1.55-2.55-.29-5.24-1.28-5.24-5.69 0-1.26.45-2.29 1.19-3.1-.12-.29-.52-1.46.11-3.05 0 0 .97-.31 3.17 1.18a11 11 0 0 1 5.77 0c2.2-1.49 3.17-1.18 3.17-1.18.63 1.59.23 2.76.11 3.05.74.81 1.19 1.84 1.19 3.1 0 4.42-2.7 5.39-5.26 5.68.41.36.78 1.06.78 2.14v3.17c0 .31.21.67.8.56A11.5 11.5 0 0 0 12 .5Z"
            />
          </svg>
          Source
        </a>
      </div>
    </header>

    <div v-if="page.cover" class="animate-rise relative mt-14 p-3 [animation-delay:300ms] sm:p-5">
      <Corners size="2.25rem" />
      <div v-tilt="3" class="group relative">
        <figure class="neat-peeled relative overflow-hidden rounded-[2rem]" :style="{ '--peel-cut': peelCut(120) }">
          <img
            :src="page.cover.url"
            :alt="`Illustration for ${page.title}`"
            width="1600"
            height="1000"
            loading="eager"
            class="aspect-16/10 w-full object-cover"
          />
        </figure>
        <Peel :size="120" :radius="32" />
      </div>
    </div>

    <div class="mt-16 grid gap-12 lg:grid-cols-[1fr_20rem] lg:gap-16">
      <div class="min-w-0">
        <p
          v-if="page.description"
          v-reveal
          class="font-display mb-10 text-2xl leading-10 font-semibold tracking-tight text-balance"
        >
          {{ page.description }}
        </p>
        <div v-reveal class="prose prose-lg max-w-none">
          <Prose v-if="page.body" :value="page.body" />
        </div>
      </div>

      <aside class="grid content-start gap-5 lg:sticky lg:top-28 lg:self-start" aria-label="Project details">
        <dl v-reveal class="neat-card grid gap-5 p-6">
          <div v-for="fact in facts" :key="fact.label" class="flex items-center justify-between gap-4">
            <dt class="text-faint font-mono text-xs tracking-wider uppercase">{{ fact.label }}</dt>
            <dd class="text-right font-medium">
              <StatusPill v-if="fact.status" :status="statusOf(page)" :label="statusLabel(page)" />
              <template v-else>{{ fact.value }}</template>
            </dd>
          </div>
        </dl>
        <div v-if="page.highlights?.length" v-reveal="80" class="neat-card p-6">
          <p class="neat-eyebrow mb-4">Highlights</p>
          <ul role="list" class="grid gap-3">
            <li v-for="item in page.highlights" :key="item" class="flex gap-3 leading-6">
              <span class="mt-2 size-1.5 shrink-0 rounded-full bg-accent" aria-hidden="true" />{{ item }}
            </li>
          </ul>
        </div>
        <div v-if="page.stack?.length" v-reveal="160" class="neat-card p-6">
          <p class="neat-eyebrow mb-4">Built with</p>
          <ul role="list" class="flex flex-wrap gap-2">
            <li
              v-for="item in page.stack"
              :key="item"
              class="border-line-strong rounded-full border px-3 py-1 font-mono text-xs text-muted"
            >
              {{ item }}
            </li>
          </ul>
        </div>
      </aside>
    </div>

    <nav v-if="list.length > 1" aria-label="More projects" class="mt-24 grid gap-5 sm:grid-cols-2">
      <Link
        v-for="(item, index) in [previous, next]"
        :key="item.id"
        v-reveal="index * 100"
        :href="item.uri ?? '#'"
        class="group neat-card flex items-center gap-5 p-6"
        :class="{ 'sm:flex-row-reverse sm:text-right': index === 1 }"
      >
        <ProjectTile :logo="item.logo?.url" :monogram="item.monogram" :accent="item.accent" size="size-14" text="text-xl" />
        <span class="min-w-0 flex-1">
          <span class="neat-eyebrow flex items-center gap-1.5" :class="{ 'sm:justify-end': index === 1 }"
            ><template v-if="index === 0"><ArrowIcon direction="left" /> Previous</template
            ><template v-else>Next <ArrowIcon /></template
          ></span>
          <span class="font-display mt-1 block text-2xl font-extrabold tracking-tight">{{ item.title }}</span>
          <span class="block truncate text-sm text-muted">{{ item.kind }}</span>
        </span>
      </Link>
    </nav>
  </article>
</template>
