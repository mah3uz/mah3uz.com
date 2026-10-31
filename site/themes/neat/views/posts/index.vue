<script setup lang="ts">
import { Link } from '@inertiajs/vue3'
import { computed } from 'vue'
import type { PagesPage, ViewProps } from '@site/types'
import PageHeading from '../../components/PageHeading.vue'
import Pager from '../../components/Pager.vue'
import PostCard from '../../components/PostCard.vue'
import { vReveal } from '../../lib/motion'

const props = defineProps<ViewProps['posts/index'] & { page: PagesPage }>()
const topics = computed(() => props.topics.filter((topic) => (topic.entries_count ?? 0) > 0))
</script>

<template>
  <div>
    <PageHeading :title="page.title" :eyebrow="page.eyebrow ?? 'Writing'" :description="page.intro">
      <div class="animate-rise mt-8 flex flex-wrap items-center gap-2 [animation-delay:240ms]">
        <Link
          v-for="topic in topics"
          :key="topic.id"
          :href="topic.uri ?? '#'"
          class="border-line-strong hover:text-ink rounded-full border px-4 py-1.5 text-sm text-muted transition-colors hover:border-accent"
          >{{ topic.title }} <span class="font-mono text-xs opacity-60">{{ topic.entries_count }}</span></Link
        >
        <a href="/feed-posts.xml" class="rounded-full bg-accent/10 px-4 py-1.5 text-sm text-accent">RSS ↗</a>
      </div>
    </PageHeading>
    <p v-if="!posts.data.length" class="py-10 text-lg text-muted">Nothing published yet — soon.</p>
    <div class="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
      <div v-for="(post, index) in posts.data" :key="post.id" v-reveal="(index % 3) * 100">
        <PostCard :post="post" />
      </div>
    </div>
    <Pager :meta="posts.meta" label="Older and newer writing" />
  </div>
</template>
