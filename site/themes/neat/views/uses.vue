<script setup lang="ts">
import type { PagesPage } from '@site/types'
import CoverPhoto from '../components/CoverPhoto.vue'
import PageHeading from '../components/PageHeading.vue'
import Prose from '../components/Prose.vue'
import { vReveal } from '../lib/motion'

defineProps<{ page: PagesPage }>()
</script>

<template>
  <div>
    <PageHeading :title="page.title" :eyebrow="page.eyebrow" :description="page.intro" />
    <CoverPhoto
      v-if="page.photo"
      :src="page.photo"
      art="/art/insensical.svg"
      alt="A desk set up for programming"
      :credit="page.photo_credit"
      eager
      class="animate-rise mb-16 aspect-[21/9] [animation-delay:240ms]"
    />
    <div
      v-reveal
      class="neat-uses [&_h2]:font-display [&_li]:border-line [&_li]:bg-surface [&_li_strong]:font-display [&_li_strong]:text-ink prose prose-lg max-w-none [&_h2]:col-span-full [&_h2]:mt-10 [&_h2]:mb-0 [&_li]:m-0 [&_li]:rounded-2xl [&_li]:border [&_li]:p-5 [&_li]:leading-7 [&_ul]:m-0 [&_ul]:grid [&_ul]:list-none [&_ul]:gap-3 [&_ul]:p-0 sm:[&_ul]:grid-cols-2"
    >
      <Prose v-if="page.content" :value="page.content" />
    </div>
    <div v-if="page.cards?.length" class="mt-16 grid gap-4 sm:grid-cols-3">
      <div v-for="(card, index) in page.cards" :key="card.id ?? index" v-reveal="index * 80" class="neat-card p-6">
        <h2 class="font-display text-lg font-bold">{{ card.title }}</h2>
        <p class="mt-2 leading-7 text-muted">{{ card.text }}</p>
      </div>
    </div>
  </div>
</template>
