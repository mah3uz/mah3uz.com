<script setup lang="ts">
import { Link } from '@inertiajs/vue3'
import { computed } from 'vue'
import type { PagesPage, ViewProps } from '@site/types'
import Corners from '../components/Corners.vue'
import NightShift from '../components/NightShift.vue'
import PostCard from '../components/PostCard.vue'
import ProjectCard from '../components/ProjectCard.vue'
import ProjectTile from '../components/ProjectTile.vue'
import StatusPill from '../components/StatusPill.vue'
import { vReveal, vSpotlight } from '../lib/motion'
import { isClient, onlyProjects, statusLabel, statusOf, STATUS_COPY, type Status } from '../lib/projects'
import ArrowIcon from '../components/ArrowIcon.vue'

const props = defineProps<ViewProps['home'] & { page: PagesPage }>()

const STARTED = 2009
const years = new Date().getUTCFullYear() - STARTED

const everything = computed(() => onlyProjects(props.projects))
const all = computed(() => everything.value.filter((project) => !isClient(project)))
const clients = computed(() => everything.value.filter(isClient))
const featured = computed(() => {
  const picked = all.value.filter((project) => project.featured)
  return (picked.length ? picked : all.value).slice(0, 4)
})
const board = computed(() =>
  (['building', 'shipped', 'experiment'] as Status[])
    .map((status) => ({ status, items: all.value.filter((project) => statusOf(project) === status) }))
    .filter((column) => column.items.length),
)
</script>

<template>
  <div>
    <NightShift :page="page" :projects="projects" :posts="posts" />

    <!-- What I reach for -->
    <section
      aria-labelledby="tools-heading"
      class="border-line flex flex-wrap items-baseline gap-x-16 gap-y-4 border-b py-10 sm:py-12"
    >
      <h2 id="tools-heading" class="neat-eyebrow shrink-0">What I reach for</h2>
      <p
        class="font-display min-w-0 flex-[1_1_40rem] text-xl leading-9 font-semibold tracking-[-0.015em] text-pretty text-muted sm:text-2xl sm:leading-10"
      >
        <span class="text-ink">Rust</span> and <span class="text-ink">Ruby</span> for the code.
        <span class="text-ink">Linux</span>, <span class="text-ink">systemd</span> and
        <span class="text-ink">Kamal</span> to run it. <span class="text-ink">SQLite</span> until something proves it
        needs <span class="text-ink">PostgreSQL</span>. Written in <span class="text-ink">Neovim</span>, on
        <span class="text-ink">Arch</span> and <span class="text-ink">Hyprland</span>.
        <Link href="/uses" class="neat-link font-body ml-2 text-base font-medium whitespace-nowrap text-accent"
          >Everything I use <ArrowIcon
        /></Link>
      </p>
    </section>

    <!-- Selected work -->
    <section v-if="featured.length" aria-labelledby="work-heading" class="pt-24 lg:pt-32">
      <div v-reveal class="mb-10 flex flex-wrap items-end justify-between gap-6">
        <div>
          <p class="neat-eyebrow">Selected work</p>
          <h2 id="work-heading" class="font-display mt-3 text-4xl font-extrabold tracking-[-0.03em] sm:text-5xl">
            Things I’m proud to have built
          </h2>
        </div>
        <Link href="/projects" class="neat-link font-medium text-accent"
          >All {{ all.length }} projects <ArrowIcon
        /></Link>
      </div>
      <div class="grid gap-5 md:grid-cols-2 lg:grid-cols-6">
        <div
          v-for="(project, position) in featured"
          :key="project.id"
          v-reveal="(position % 2) * 120"
          :class="position === 0 || position === 3 ? 'lg:col-span-4' : 'lg:col-span-2'"
        >
          <ProjectCard :project="project" :large="position === 0 || position === 3" :eager="position < 2" />
        </div>
      </div>
    </section>

    <!-- Client work -->
    <section v-if="clients.length" aria-labelledby="clients-heading" class="pt-24 lg:pt-32">
      <div class="grid gap-10 lg:grid-cols-[1fr_1.6fr] lg:gap-16">
        <div v-reveal class="lg:sticky lg:top-32 lg:self-start">
          <p class="neat-eyebrow">Client work</p>
          <h2 id="clients-heading" class="font-display mt-3 text-4xl font-extrabold tracking-[-0.03em] sm:text-5xl">
            Trusted with other people’s products
          </h2>
          <p class="mt-5 text-lg leading-8 text-muted">
            Alongside my own products, I engineer platforms for clients — production systems that real businesses run on
            every day.
          </p>
          <Link href="/projects?view=clients" class="neat-link mt-6 inline-block font-medium text-accent"
            >All client work <ArrowIcon
          /></Link>
        </div>
        <ul role="list" class="grid gap-4">
          <li v-for="(client, position) in clients" :key="client.id" v-reveal="position * 110">
            <Link
              v-spotlight
              :href="client.uri ?? '#'"
              class="group neat-card grid items-center gap-5 p-5 transition-transform duration-500 hover:-translate-y-1 sm:grid-cols-[auto_1fr_auto] sm:p-6"
            >
              <ProjectTile
                :logo="client.logo"
                :monogram="client.monogram"
                :accent="client.accent"
                size="size-16"
                text="text-xl"
              />
              <span class="min-w-0">
                <span class="flex flex-wrap items-center gap-3">
                  <span class="font-display text-2xl font-extrabold tracking-tight">{{ client.title }}</span>
                  <StatusPill :status="statusOf(client)" :label="statusLabel(client)" />
                </span>
                <span class="text-faint mt-1 block font-mono text-xs">{{ client.role }} · {{ client.kind }}</span>
                <span class="mt-3 block leading-7 text-muted">{{ client.tagline }}</span>
              </span>
              <span
                class="border-line-strong hidden size-11 place-items-center rounded-full border text-accent transition-all duration-500 group-hover:rotate-45 group-hover:border-accent sm:grid"
                aria-hidden="true"
                >↗</span
              >
            </Link>
          </li>
        </ul>
      </div>
    </section>

    <!-- The workshop board -->
    <section v-if="board.length" aria-labelledby="board-heading" class="pt-24 lg:pt-32">
      <div v-reveal class="mb-10 max-w-2xl">
        <p class="neat-eyebrow">The workshop</p>
        <h2 id="board-heading" class="font-display mt-3 text-4xl font-extrabold tracking-[-0.03em] sm:text-5xl">
          What’s on the bench
        </h2>
        <p class="mt-4 text-lg leading-8 text-muted">
          Everything I’m working on, out in the open — what’s in progress, what has shipped, and the ideas I’m testing.
        </p>
      </div>
      <div class="grid gap-5 lg:grid-cols-3">
        <div
          v-for="(column, position) in board"
          :key="column.status"
          v-reveal="position * 120"
          v-spotlight
          class="neat-card p-3"
        >
          <div class="flex items-center justify-between px-3 pt-3 pb-4">
            <StatusPill :status="column.status" />
            <span class="text-faint font-mono text-xs">{{ STATUS_COPY[column.status].note }}</span>
          </div>
          <ul role="list" class="grid gap-1">
            <li v-for="project in column.items" :key="project.id">
              <Link
                :href="project.uri ?? '#'"
                class="group/row flex items-center gap-4 rounded-2xl p-3 transition-colors hover:bg-accent/8"
              >
                <ProjectTile
                  :logo="project.logo"
                  :monogram="project.monogram"
                  :accent="project.accent"
                  size="size-11"
                  text="text-base"
                />
                <span class="min-w-0 flex-1">
                  <span class="font-display block font-bold">{{ project.title }}</span>
                  <span class="block truncate text-sm text-muted">{{ project.kind }}</span>
                </span>
                <ArrowIcon
                  class="text-accent opacity-0 transition-all duration-300 group-hover/row:translate-x-1 group-hover/row:opacity-100"
                />
              </Link>
            </li>
          </ul>
        </div>
      </div>
    </section>

    <!-- How I work -->
    <section v-if="page.cards?.length" aria-labelledby="approach-heading" class="pt-24 lg:pt-32">
      <div class="border-line bg-surface relative overflow-hidden rounded-[2.5rem] border p-6 sm:p-12">
        <Corners inset="1.25rem" />
        <div class="neat-dots absolute inset-0 -z-10" aria-hidden="true" />
        <div v-reveal class="mb-10 max-w-2xl">
          <p class="neat-eyebrow">How I work</p>
          <h2 id="approach-heading" class="font-display mt-3 text-4xl font-extrabold tracking-[-0.03em] sm:text-5xl">
            Principles, after {{ years }} years of shipping
          </h2>
        </div>
        <ol role="list" class="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          <li v-for="(card, position) in page.cards" :key="card.id ?? position" v-reveal="position * 90">
            <span class="font-mono text-sm text-accent">0{{ position + 1 }}</span>
            <h3 class="font-display mt-3 text-xl font-bold tracking-tight">{{ card.title }}</h3>
            <p class="mt-2 leading-7 text-muted">{{ card.text }}</p>
          </li>
        </ol>
      </div>
    </section>

    <!-- Writing -->
    <section v-if="posts.length" aria-labelledby="writing-heading" class="pt-24 lg:pt-32">
      <div v-reveal class="mb-10 flex flex-wrap items-end justify-between gap-6">
        <div>
          <p class="neat-eyebrow">Writing</p>
          <h2 id="writing-heading" class="font-display mt-3 text-4xl font-extrabold tracking-[-0.03em] sm:text-5xl">
            Notes from the workshop
          </h2>
        </div>
        <Link href="/blog" class="neat-link font-medium text-accent">Everything I’ve written <ArrowIcon /></Link>
      </div>
      <div class="grid gap-5 md:grid-cols-3">
        <div v-for="(post, position) in posts" :key="post.id" v-reveal="position * 110">
          <PostCard :post="post" />
        </div>
      </div>
    </section>
  </div>
</template>
