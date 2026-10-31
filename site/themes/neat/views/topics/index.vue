<script setup lang="ts">
import { Link } from '@inertiajs/vue3'
import type { ViewProps } from '@site/types'
import PageHeading from '../../components/PageHeading.vue'
import { vReveal, vSpotlight } from '../../lib/motion'

defineProps<ViewProps['topics/index']>()
</script>

<template>
  <div>
    <PageHeading title="Topics" eyebrow="Writing" description="What I write about, grouped by subject." />
    <ul role="list" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <li v-for="(topic, index) in topics" :key="topic.id" v-reveal="(index % 3) * 80">
        <Link v-spotlight :href="topic.uri ?? '#'" class="group neat-card flex h-full flex-col gap-2 p-6">
          <span class="font-mono text-xs text-accent"
            >{{ topic.entries_count }} {{ topic.entries_count === 1 ? 'note' : 'notes' }}</span
          >
          <span class="font-display text-2xl font-extrabold tracking-tight">{{ topic.title }}</span>
          <span v-if="topic.description" class="leading-7 text-muted">{{ topic.description }}</span>
        </Link>
      </li>
    </ul>
  </div>
</template>
