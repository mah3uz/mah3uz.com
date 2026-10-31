<script setup lang="ts">
import type { PagesPage } from '@site/types'
import ArtBanner from '../../components/ArtBanner.vue'
import PageBody from '../../components/PageBody.vue'
import PageHeading from '../../components/PageHeading.vue'
import { vReveal } from '../../lib/motion'

defineProps<{ page: PagesPage }>()
</script>

<template>
  <div>
    <PageHeading :title="page.title" :eyebrow="page.eyebrow" :description="page.intro" />
    <ArtBanner v-if="page.art" :src="page.art" eager class="animate-rise mb-16 aspect-[21/9] [animation-delay:240ms]" />
    <div class="grid gap-14 lg:grid-cols-[1fr_22rem]">
      <PageBody :content="page.content" :blocks="page.blocks" large />
      <ol v-if="page.cards?.length" role="list" class="grid content-start gap-4">
        <li v-for="(card, index) in page.cards" :key="card.id ?? index" v-reveal="index * 80" class="neat-card p-6">
          <h2 class="font-display text-lg font-bold">{{ card.title }}</h2>
          <p class="mt-2 leading-7 text-muted">{{ card.text }}</p>
        </li>
      </ol>
    </div>
  </div>
</template>
