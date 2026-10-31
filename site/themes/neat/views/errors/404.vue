<script setup lang="ts">
import { Link } from '@inertiajs/vue3'
import { computed } from 'vue'
import type { ViewProps } from '@site/types'
import Corners from '../../components/Corners.vue'
import ProjectTile from '../../components/ProjectTile.vue'
import { onlyProjects } from '../../lib/projects'

const props = defineProps<ViewProps['errors/404']>()
const suggestions = computed(() => onlyProjects(props.projects).slice(0, 3))
</script>

<template>
  <div class="grid items-center gap-14 py-6 lg:grid-cols-2">
    <div>
      <p class="neat-eyebrow animate-rise">Error 404</p>
      <h1
        class="animate-rise font-display mt-5 text-5xl font-extrabold tracking-[-0.04em] [animation-delay:80ms] sm:text-7xl"
      >
        This page peeled off.
      </h1>
      <p class="animate-rise mt-6 max-w-[44ch] text-lg leading-8 text-muted [animation-delay:160ms]">
        Whatever was here has moved, or never existed. Try the search, press
        <kbd class="border-line rounded border px-1.5 font-mono text-sm">/</kbd> to jump anywhere, or start from one of
        these.
      </p>
      <div class="animate-rise mt-8 flex flex-wrap gap-3 [animation-delay:240ms]">
        <Link href="/" class="neat-button">Back home</Link>
        <Link href="/search" class="neat-button-ghost">Search</Link>
      </div>
      <ul v-if="suggestions.length" role="list" class="animate-rise mt-12 grid gap-2 [animation-delay:320ms]">
        <li v-for="project in suggestions" :key="project.id">
          <Link
            :href="project.uri ?? '#'"
            class="group flex items-center gap-4 rounded-2xl p-2 transition-colors hover:bg-accent/8"
          >
            <ProjectTile
              :logo="project.logo"
              :monogram="project.monogram"
              :accent="project.accent"
              size="size-10"
              text="text-sm"
            />
            <span class="font-display font-bold">{{ project.title }}</span>
            <span class="truncate text-sm text-muted max-sm:hidden">{{ project.tagline }}</span>
          </Link>
        </li>
      </ul>
    </div>
    <div
      class="animate-rise relative mx-auto aspect-square w-full max-w-md p-6 [animation-delay:200ms]"
      aria-hidden="true"
    >
      <Corners size="2.5rem" />
      <div class="bg-midnight relative size-full overflow-hidden rounded-[2.5rem]">
        <div class="neat-dots absolute inset-0" />
        <div class="animate-drift absolute inset-0 bg-[radial-gradient(circle_at_30%_30%,#21bdb066,transparent_60%)]" />
        <p
          class="font-display absolute inset-0 flex items-center justify-center text-[7rem] font-extrabold tracking-tighter text-white sm:text-[9rem]"
        >
          4<span class="neat-gradient-text">0</span>4
        </p>
        <svg class="animate-float absolute right-0 bottom-0 size-[28%] origin-bottom-right" viewBox="0 0 104 104">
          <defs>
            <linearGradient id="nf-flap" x1="93.6" y1="93.6" x2="20.8" y2="20.8" gradientUnits="userSpaceOnUse">
              <stop offset="0" stop-color="#A6D3D6" />
              <stop offset="0.5" stop-color="#E9F7F7" />
              <stop offset="1" stop-color="#FFFFFF" />
            </linearGradient>
          </defs>
          <path d="M104 0Q45.76 45.76 0 104H104Z" fill="#62EDD4" />
          <path
            d="M104 0C68.64 -3.12 33.28 6.24 20.8 20.8C6.24 33.28 -3.12 68.64 0 104Q45.76 45.76 104 0Z"
            fill="url(#nf-flap)"
          />
        </svg>
      </div>
    </div>
  </div>
</template>
