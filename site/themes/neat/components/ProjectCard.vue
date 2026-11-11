<script setup lang="ts">
import { Link } from '@inertiajs/vue3'
import { computed } from 'vue'
import { isClient, statusLabel, statusOf, type ProjectLike } from '../lib/projects'
import { vSpotlight } from '../lib/motion'
import Peel, { peelCut } from './Peel.vue'
import ProjectTile from './ProjectTile.vue'
import StatusPill from './StatusPill.vue'

const props = withDefaults(defineProps<{ project: ProjectLike; large?: boolean; eager?: boolean }>(), {
  large: false,
  eager: false,
})
const status = computed(() => statusOf(props.project))
</script>

<template>
  <div
    class="group relative h-full transition-transform duration-500 ease-[cubic-bezier(0.16,1,0.3,1)] hover:-translate-y-1.5"
  >
    <article
      v-spotlight
      class="neat-card neat-peeled flex h-full flex-col"
      :style="{ '--peel-cut': peelCut(large ? 92 : 72) }"
    >
      <div v-if="project.cover" class="relative m-2 mb-0 overflow-hidden rounded-[1.4rem]">
        <img
          :src="project.cover.url"
          :alt="`Illustration for ${project.title}`"
          :loading="eager ? 'eager' : 'lazy'"
          width="1600"
          height="1000"
          class="aspect-16/10 w-full object-cover transition-transform duration-700 ease-[cubic-bezier(0.16,1,0.3,1)] will-change-transform group-hover:scale-[1.04]"
        />
        <div class="absolute top-4 left-4 flex gap-2">
          <StatusPill :status="status" :label="statusLabel(project)" />
          <span
            v-if="isClient(project)"
            class="bg-mint text-abyss rounded-full px-3 py-1 font-mono text-[0.7rem] tracking-wider uppercase"
            >Client</span
          >
        </div>
      </div>
      <div class="flex flex-1 flex-col gap-4 p-6 pr-16 sm:p-7 sm:pr-20" :class="{ 'lg:p-9': large }">
        <div class="flex items-center gap-4">
          <ProjectTile
            :logo="project.logo?.url"
            :monogram="project.monogram"
            :accent="project.accent"
            size="size-11"
            text="text-base"
          />
          <div class="min-w-0">
            <h3 class="font-display font-extrabold tracking-tight" :class="large ? 'text-3xl lg:text-4xl' : 'text-2xl'">
              <Link :href="project.uri ?? '#'" class="after:absolute after:inset-0 after:z-10 focus:outline-none">
                {{ project.title }}
              </Link>
            </h3>
            <p class="text-faint font-mono text-xs tracking-wide">
              <template v-if="isClient(project) && project.role">{{ project.role }} · </template>{{ project.kind
              }}<template v-if="project.year"> · {{ project.year }}</template>
            </p>
          </div>
        </div>
        <p class="text-muted" :class="large ? 'text-lg leading-8' : 'leading-7'">
          {{ project.tagline ?? project.description }}
        </p>
        <!-- A small card shares its row with a large one and stretches to its height; the description fills that room. -->
        <p
          v-if="!large && project.tagline && project.description"
          class="line-clamp-6 text-[0.95rem] leading-7 text-muted"
        >
          {{ project.description }}
        </p>
        <ul v-if="project.stack?.length" class="mt-auto flex flex-wrap gap-2 pt-2" role="list" aria-label="Built with">
          <li
            v-for="item in project.stack.slice(0, large ? 6 : 4)"
            :key="item"
            class="border-line rounded-full border px-3 py-1 font-mono text-[0.7rem] text-muted"
          >
            {{ item }}
          </li>
        </ul>
      </div>
      <span
        class="bg-canvas/80 absolute top-6 right-6 z-20 grid size-10 place-items-center rounded-full text-accent opacity-0 transition-all duration-500 group-hover:-translate-y-1 group-hover:opacity-100"
        aria-hidden="true"
      >
        ↗
      </span>
    </article>
    <Peel :size="large ? 92 : 72" />
  </div>
</template>
