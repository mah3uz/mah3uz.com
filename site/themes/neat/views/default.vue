<script setup lang="ts">
import type { RichTextValue, SetBlock } from '@nibble'
import PageBody from '../components/PageBody.vue'
import PageHeading from '../components/PageHeading.vue'

defineProps<{
  page: {
    title: string | null
    eyebrow?: string | null
    intro?: string | null
    excerpt?: string | null
    description?: string | null
    content?: RichTextValue | null
    body?: RichTextValue | null
    blocks?: SetBlock[] | null
  }
}>()
</script>

<template>
  <div>
    <PageHeading
      :title="page.title"
      :eyebrow="page.eyebrow"
      :description="page.intro ?? page.excerpt ?? page.description"
    />
    <PageBody :content="page.content ?? page.body" :blocks="page.blocks" />
  </div>
</template>
