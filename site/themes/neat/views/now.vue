<script setup lang="ts">
import { Link } from '@inertiajs/vue3'
import { computed } from 'vue'
import type { PagesPage, ViewProps } from '@site/types'
import PageBody from '../components/PageBody.vue'
import PageHeading from '../components/PageHeading.vue'
import ProjectTile from '../components/ProjectTile.vue'
import { isoDate, useFormatDate } from '../lib/format'
import { vReveal, vSpotlight } from '../lib/motion'
import { onlyProjects, statusOf } from '../lib/projects'

const props = defineProps<ViewProps['now'] & { page: PagesPage }>()
const formatDate = useFormatDate()
const building = computed(() => onlyProjects(props.projects).filter((project) => statusOf(project) === 'building'))
</script>

<template>
  <div>
    <PageHeading :title="page.title" :eyebrow="page.eyebrow" :description="page.intro">
      <p
        class="animate-rise border-line-strong bg-surface mt-8 inline-flex items-center gap-3 rounded-full border px-4 py-2 font-mono text-xs text-muted [animation-delay:240ms]"
      >
        <span class="animate-pulse-ring size-2 rounded-full bg-accent" aria-hidden="true" />
        Updated
        <time :datetime="isoDate(page.updated_at)">{{
          formatDate(page.updated_at, { month: 'long', day: 'numeric', year: 'numeric' })
        }}</time>
      </p>
    </PageHeading>

    <section v-if="building.length" aria-labelledby="on-the-bench" class="mb-20">
      <h2 id="on-the-bench" class="neat-eyebrow mb-5">On the bench</h2>
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Link
          v-for="(project, index) in building"
          :key="project.id"
          v-reveal="index * 80"
          v-spotlight
          :href="project.uri ?? '#'"
          class="group neat-card flex flex-col gap-4 p-6 transition-transform duration-500 hover:-translate-y-1"
        >
          <ProjectTile
            :logo="project.logo"
            :monogram="project.monogram"
            :accent="project.accent"
            size="size-12"
            text="text-lg"
          />
          <span class="font-display text-xl font-extrabold tracking-tight">{{ project.title }}</span>
          <span class="text-sm leading-6 text-muted">{{ project.tagline }}</span>
        </Link>
      </div>
    </section>

    <div class="grid gap-14 lg:grid-cols-[1fr_22rem]">
      <PageBody :content="page.content" :blocks="page.blocks" large />
      <ol v-if="page.cards?.length" role="list" class="grid content-start gap-4">
        <li v-for="(card, index) in page.cards" :key="card.id ?? index" v-reveal="index * 80" class="neat-card p-6">
          <h2 class="font-display text-lg font-bold">{{ card.title }}</h2>
          <p class="mt-2 leading-7 text-muted">{{ card.text }}</p>
        </li>
      </ol>
    </div>
    <p v-reveal class="text-faint mt-16 max-w-[60ch] text-sm leading-6">
      This is a
      <a href="https://nownownow.com/about" class="underline underline-offset-4 hover:text-accent">now page</a>: what
      has my attention at the moment, rather than everything I’ve ever done.
    </p>
  </div>
</template>
