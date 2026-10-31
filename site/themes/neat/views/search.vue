<script setup lang="ts">
import { Link } from '@inertiajs/vue3'
import { useSite } from '@nibble'
import { computed } from 'vue'
import type { PagesPage, ViewProps } from '@site/types'
import PageHeading from '../components/PageHeading.vue'
import Pager from '../components/Pager.vue'
import { vReveal } from '../lib/motion'

defineProps<ViewProps['search'] & { page: PagesPage }>()

const site = useSite()
const query = computed(() => site.value.params.q ?? '')
const LABELS: Record<string, string> = { posts: 'Writing', projects: 'Project', pages: 'Page' }
</script>

<template>
  <div class="mx-auto max-w-3xl">
    <PageHeading :title="page.title ?? 'Search'" :eyebrow="page.eyebrow ?? 'Find anything'" />
    <form
      action="/search"
      method="get"
      role="search"
      aria-label="Search the site"
      class="animate-rise mb-14 [animation-delay:200ms]"
    >
      <label for="query" class="sr-only">Search the site</label>
      <div
        class="border-line-strong bg-surface flex items-center gap-3 rounded-full border p-2 pl-6 backdrop-blur transition-colors focus-within:border-accent"
      >
        <svg
          class="size-5 shrink-0 text-accent"
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
          id="query"
          type="search"
          name="q"
          maxlength="200"
          :value="query"
          placeholder="Projects, notes, tools…"
          class="placeholder:text-faint min-w-0 flex-1 bg-transparent py-3 text-lg outline-none"
        />
        <button type="submit" class="neat-button !min-h-11">Search</button>
      </div>
    </form>
    <template v-if="query">
      <p v-if="!results.data.length" class="py-8 text-lg text-muted">
        Nothing found for “{{ query }}”. Try another word.
      </p>
      <template v-else>
        <p class="neat-eyebrow mb-6">{{ results.meta.total }} results for “{{ query }}”</p>
        <ol class="grid gap-3" role="list">
          <li v-for="(result, index) in results.data" :key="`${result.type}-${result.id}`" v-reveal="index * 40">
            <Link :href="result.uri ?? '#'" class="group neat-card block p-6">
              <span class="font-mono text-xs text-accent">{{ LABELS[result.collection ?? ''] ?? 'Page' }}</span>
              <span class="font-display mt-1 block text-xl font-bold tracking-tight group-hover:text-accent">{{
                result.title
              }}</span>
              <!-- eslint-disable vue/no-v-html -- snippets are HTML-escaped by the server, with only <mark> added -->
              <span
                v-if="result.search_snippet"
                class="[&_mark]:text-ink mt-2 block leading-7 text-muted [&_mark]:rounded [&_mark]:bg-accent/20 [&_mark]:px-1"
                v-html="result.search_snippet"
              ></span>
              <!-- eslint-enable vue/no-v-html -->
            </Link>
          </li>
        </ol>
        <Pager :meta="results.meta" previous-label="Previous" next-label="More results" />
      </template>
    </template>
    <p v-else class="text-lg text-muted">
      Tip: press <kbd class="border-line rounded border px-1.5 font-mono text-sm">/</kbd> on any page to jump straight
      to a project. Or browse <Link href="/projects" class="text-accent underline underline-offset-4">the work</Link>.
    </p>
  </div>
</template>
