<script setup lang="ts">
// The home hero's reel: two columns of work, each drifting slowly and continuously in opposite directions. It is one
// unbroken CSS animation per column (transform only), so it never ticks or jumps, and it runs on the compositor.
// Hovering or focusing a card pauses the reel; people who prefer less motion get a still, complete grid.
import { Link } from '@inertiajs/vue3'
import { computed } from 'vue'
import { isClient, statusLabel, statusOf, type ProjectLike } from '../lib/projects'
import Corners from './Corners.vue'
import ProjectTile from './ProjectTile.vue'
import StatusPill from './StatusPill.vue'

const props = defineProps<{ projects: ProjectLike[]; years: number }>()

const withArt = computed(() => props.projects.filter((project) => project.cover))
// Deal the projects into two columns, alternately, so each column has a mix.
const columns = computed(() => [
  withArt.value.filter((_, index) => index % 2 === 0),
  withArt.value.filter((_, index) => index % 2 === 1),
])
</script>

<template>
  <div v-if="withArt.length" class="relative">
    <Corners size="2rem" inset="-0.75rem" />
    <div
      class="neat-reel group/reel relative grid h-[30rem] grid-cols-2 gap-4 overflow-hidden rounded-[2rem] sm:h-[36rem]"
      aria-label="Selected work"
      role="region"
    >
      <div
        v-for="(column, columnIndex) in columns"
        :key="columnIndex"
        class="neat-reel-track flex flex-col"
        :class="columnIndex === 1 ? 'neat-reel-reverse -mt-24' : ''"
      >
        <!-- The column is drawn twice so the loop is seamless; the copy is hidden from assistive technology. -->
        <template v-for="copy in 2" :key="copy">
          <Link
            v-for="project in column"
            :key="`${copy}-${project.id}`"
            :href="project.uri ?? '#'"
            :tabindex="copy === 2 ? -1 : undefined"
            :aria-hidden="copy === 2 ? 'true' : undefined"
            class="group/card relative mb-4 block shrink-0 overflow-hidden rounded-[1.4rem] shadow-[0_24px_50px_-28px_rgba(4,48,64,0.6)]"
          >
            <img
              :src="project.cover ?? ''"
              :alt="copy === 1 ? `${project.title}: illustration` : ''"
              width="1600"
              height="1000"
              :loading="copy === 1 ? 'eager' : 'lazy'"
              class="aspect-[4/3] w-full object-cover transition-transform duration-700 ease-[cubic-bezier(0.16,1,0.3,1)] group-hover/card:scale-[1.04]"
            />
            <div
              class="absolute inset-0 bg-[linear-gradient(180deg,transparent_35%,rgba(10,26,32,0.92)_100%)]"
              aria-hidden="true"
            />
            <div class="absolute top-3 left-3">
              <StatusPill
                :status="statusOf(project)"
                :label="statusLabel(project)"
                class="!bg-midnight/70 !text-white"
              />
            </div>
            <div class="absolute inset-x-0 bottom-0 flex items-end gap-3 p-4 text-white">
              <ProjectTile
                :logo="project.logo"
                :monogram="project.monogram"
                :accent="project.accent"
                size="size-10"
                text="text-sm"
              />
              <div class="min-w-0">
                <p class="font-display truncate text-lg leading-tight font-extrabold">{{ project.title }}</p>
                <p class="text-mist truncate text-xs">
                  {{ isClient(project) ? `Client · ${project.kind}` : project.kind }}
                </p>
              </div>
            </div>
          </Link>
        </template>
      </div>
      <!-- soft fades at the top and bottom edges -->
      <div
        class="from-canvas pointer-events-none absolute inset-x-0 top-0 h-20 bg-gradient-to-b to-transparent"
        aria-hidden="true"
      />
      <div
        class="from-canvas pointer-events-none absolute inset-x-0 bottom-0 h-24 bg-gradient-to-t to-transparent"
        aria-hidden="true"
      />
    </div>

    <div class="mt-5 flex flex-wrap items-center justify-between gap-3 text-sm">
      <p class="flex items-center gap-2 font-medium">
        <span class="animate-pulse-ring size-2 rounded-full bg-accent" aria-hidden="true" />
        Available for select projects
      </p>
      <p class="text-faint font-mono text-xs">{{ years }}+ years · {{ withArt.length }} projects</p>
    </div>
  </div>
</template>

<style>
.neat-reel-track {
  animation: neat-reel 60s linear infinite;
  will-change: transform;
}
.neat-reel-reverse {
  animation-direction: reverse;
  animation-duration: 72s;
}
/* Pause while someone is looking at, or tabbing through, the reel. */
.neat-reel:hover .neat-reel-track,
.neat-reel:focus-within .neat-reel-track {
  animation-play-state: paused;
}
@keyframes neat-reel {
  from {
    transform: translate3d(0, 0, 0);
  }
  /* Each column is drawn twice, every card with its space below it, so half the column is exactly one copy and
     moving by it lands on the start. */
  to {
    transform: translate3d(0, -50%, 0);
  }
}
@media (prefers-reduced-motion: reduce) {
  .neat-reel-track {
    animation: none;
  }
}
</style>
