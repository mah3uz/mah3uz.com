<script setup lang="ts">
// The home hero's showcase: a deck of featured work that turns over every few seconds. Each card shows the product's
// own banner and logo. The server renders the deck in order, so it is complete before any script runs; turning starts
// once the page is interactive, pauses on hover or focus, and never happens for people who prefer less motion.
import { Link } from '@inertiajs/vue3'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { statusLabel, statusOf, type ProjectLike } from '../lib/projects'
import Corners from './Corners.vue'
import ProjectTile from './ProjectTile.vue'
import StatusPill from './StatusPill.vue'

const props = defineProps<{ projects: (ProjectLike & { banner?: string | null })[]; years: number }>()

const deck = computed(() => props.projects.filter((project) => project.banner).slice(0, 5))
const front = ref(0)
const paused = ref(false)
let timer: ReturnType<typeof setInterval> | undefined

// Where each card sits relative to the front one: 0 is in front, then up and to the right behind it.
const place = (index: number) => (index - front.value + deck.value.length) % deck.value.length

function style(index: number) {
  const depth = place(index)
  const shown = Math.min(depth, 3)
  return {
    transform: `translate3d(${shown * 22}px, ${-shown * 22}px, 0) scale(${1 - shown * 0.05}) rotate(${shown * 2.2}deg)`,
    opacity: depth > 2 ? 0 : 1,
    zIndex: String(deck.value.length - depth),
  }
}

function go(step: number) {
  front.value = (front.value + step + deck.value.length) % deck.value.length
}

onMounted(() => {
  if (deck.value.length < 2 || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
  timer = setInterval(() => !paused.value && go(1), 5200)
})
onBeforeUnmount(() => clearInterval(timer))
</script>

<template>
  <div
    v-if="deck.length"
    class="relative"
    role="region"
    aria-roledescription="carousel"
    aria-label="Featured work"
    @mouseenter="paused = true"
    @mouseleave="paused = false"
    @focusin="paused = true"
    @focusout="paused = false"
  >
    <Corners size="2rem" inset="-0.75rem" />
    <div class="relative h-[25rem] pt-16 pr-16 sm:h-[27rem]">
      <article
        v-for="(project, index) in deck"
        :key="project.id"
        class="border-line bg-surface-strong absolute bottom-0 left-0 flex h-[calc(100%-4rem)] w-[calc(100%-4rem)] origin-bottom-left flex-col overflow-hidden rounded-[1.75rem] border shadow-[0_40px_80px_-40px_rgba(4,48,64,0.55)] transition-[transform,opacity] duration-[1100ms] ease-[cubic-bezier(0.16,1,0.3,1)] will-change-[transform,opacity]"
        :style="style(index)"
        :aria-hidden="place(index) !== 0"
        :inert="place(index) !== 0 || undefined"
        :aria-label="`${index + 1} of ${deck.length}: ${project.title}`"
        role="group"
        aria-roledescription="slide"
      >
        <div
          class="bg-canvas pointer-events-none absolute inset-0 z-10 transition-opacity duration-[1100ms] ease-[cubic-bezier(0.16,1,0.3,1)]"
          :style="{ opacity: Math.min(place(index), 2) * 0.3 }"
          aria-hidden="true"
        />
        <div
          class="relative aspect-[16/5] shrink-0 overflow-hidden bg-[radial-gradient(120%_100%_at_30%_0%,#15434e,#0a1a20)]"
        >
          <img
            :src="project.banner ?? ''"
            :alt="`${project.title} banner`"
            class="relative size-full object-contain"
            :loading="index === 0 ? 'eager' : 'lazy'"
          />
        </div>
        <div class="flex min-h-0 flex-1 flex-col gap-3 p-5 sm:p-6">
          <div class="flex items-center gap-4">
            <ProjectTile
              :logo="project.logo"
              :monogram="project.monogram"
              :accent="project.accent"
              size="size-12"
              text="text-lg"
            />
            <div class="min-w-0 flex-1">
              <h3 class="font-display truncate text-xl font-extrabold tracking-tight sm:text-2xl">
                {{ project.title }}
              </h3>
              <p class="text-faint truncate text-sm">{{ project.kind }}</p>
            </div>
            <StatusPill :status="statusOf(project)" :label="statusLabel(project)" class="max-sm:hidden" />
          </div>
          <p class="line-clamp-2 leading-7 text-muted">{{ project.tagline }}</p>
          <Link
            :href="project.uri ?? '#'"
            class="group/link mt-auto inline-flex w-fit items-center gap-2 text-sm font-semibold text-accent"
          >
            View the case study
            <span class="transition-transform duration-300 group-hover/link:translate-x-1" aria-hidden="true">→</span>
          </Link>
        </div>
      </article>
    </div>

    <div class="mt-6 flex flex-wrap items-center justify-between gap-4 pr-16">
      <p class="flex items-center gap-2 text-sm font-medium">
        <span class="animate-pulse-ring size-2 rounded-full bg-accent" aria-hidden="true" />
        Available for select projects
      </p>
      <div class="flex items-center gap-4">
        <div class="flex gap-1.5">
          <button
            v-for="(project, index) in deck"
            :key="project.id"
            type="button"
            class="h-1.5 rounded-full transition-all duration-500"
            :class="index === front ? 'w-8 bg-accent' : 'bg-line-strong w-3 hover:bg-accent/50'"
            :aria-label="`Show ${project.title}`"
            :aria-current="index === front ? 'true' : undefined"
            @click="front = index"
          />
        </div>
        <div class="flex gap-2">
          <button
            type="button"
            class="border-line-strong grid size-10 place-items-center rounded-full border transition-colors hover:border-accent hover:text-accent"
            aria-label="Previous project"
            @click="go(-1)"
          >
            ←
          </button>
          <button
            type="button"
            class="border-line-strong grid size-10 place-items-center rounded-full border transition-colors hover:border-accent hover:text-accent"
            aria-label="Next project"
            @click="go(1)"
          >
            →
          </button>
        </div>
      </div>
    </div>

    <div
      class="animate-float border-line bg-surface-strong shadow-abyss/10 absolute top-2 -left-3 z-20 hidden rounded-2xl border px-4 py-3 shadow-xl [--tilt:-3deg] sm:block"
    >
      <p class="font-display text-2xl leading-none font-extrabold">{{ years }}+</p>
      <p class="mt-1 text-xs text-muted">years shipping software</p>
    </div>
  </div>
</template>
