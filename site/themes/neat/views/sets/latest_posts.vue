<script setup lang="ts">
import type { ViewProps } from '@site/types'
import PostCard from '../../components/PostCard.vue'

defineProps<{ count?: number | null; heading?: string | null; queries?: ViewProps['sets/latest_posts'] }>()
</script>

<template>
  <section v-if="queries?.posts.length" class="not-prose my-14">
    <h2 v-if="heading" class="font-display mb-6 text-3xl font-extrabold tracking-tight">{{ heading }}</h2>
    <div class="grid gap-5 sm:grid-cols-2">
      <PostCard v-for="post in queries.posts" :key="post.id" :post="post" />
    </div>
  </section>
</template>
