<script setup lang="ts">
import type { TopicsTopic, ViewProps } from '@site/types'
import PageHeading from '../../components/PageHeading.vue'
import Pager from '../../components/Pager.vue'
import PostCard from '../../components/PostCard.vue'
import { vReveal } from '../../lib/motion'

defineProps<ViewProps['topics/show'] & { page: TopicsTopic }>()
</script>

<template>
  <div>
    <PageHeading :title="page.title" eyebrow="Topic" :description="page.description" />
    <p v-if="!posts.data.length" class="text-lg text-muted">Nothing filed under this topic yet.</p>
    <div class="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
      <div v-for="(post, index) in posts.data" :key="post.id" v-reveal="(index % 3) * 100">
        <PostCard :post="post" />
      </div>
    </div>
    <Pager :meta="posts.meta" />
  </div>
</template>
