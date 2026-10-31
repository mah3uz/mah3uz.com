<script setup lang="ts">
import { Link } from '@inertiajs/vue3'
import { Image } from '@nibble'
import type { AssetValue } from '@site/types'
import { isoDate, useFormatDate } from '../lib/format'
import { vSpotlight } from '../lib/motion'
import CoverPhoto from './CoverPhoto.vue'

defineProps<{
  post: {
    id: number | string
    title: string | null
    uri: string | null
    excerpt?: string | null
    published_at?: string | null
    photo?: string | null
    photo_credit?: string | null
    art?: string | null
    featured_image?: AssetValue | null
    topics?: { id: number | string; title: string | null }[] | null
  }
}>()

const formatDate = useFormatDate()
</script>

<template>
  <article
    v-spotlight
    class="group neat-card flex h-full flex-col p-2 transition-transform duration-500 ease-[cubic-bezier(0.16,1,0.3,1)] hover:-translate-y-1.5"
  >
    <div class="aspect-16/10 overflow-hidden rounded-[1.4rem]">
      <Image
        v-if="post.featured_image"
        :image="post.featured_image"
        sizes="(min-width: 768px) 24rem, 100vw"
        class="size-full object-cover transition-transform duration-700 ease-[cubic-bezier(0.16,1,0.3,1)] will-change-transform group-hover:scale-105"
      />
      <CoverPhoto
        v-else
        :src="post.photo"
        :art="post.art ?? '/art/nibble.svg'"
        :alt="''"
        class="size-full !rounded-none !border-0 transition-transform duration-700 ease-[cubic-bezier(0.16,1,0.3,1)] will-change-transform group-hover:scale-105"
      />
    </div>
    <div class="flex flex-1 flex-col gap-3 p-5">
      <p class="text-faint flex flex-wrap items-center gap-2 font-mono text-xs">
        <time :datetime="isoDate(post.published_at)">{{ formatDate(post.published_at) }}</time>
        <template v-for="topic in (post.topics ?? []).slice(0, 1)" :key="topic.id">
          <span aria-hidden="true">·</span><span class="text-accent">{{ topic.title }}</span>
        </template>
      </p>
      <h3 class="font-display text-xl font-bold tracking-tight text-balance">
        <Link :href="post.uri ?? '#'" class="after:absolute after:inset-0 focus:outline-none">{{ post.title }}</Link>
      </h3>
      <p v-if="post.excerpt" class="line-clamp-3 leading-7 text-muted">{{ post.excerpt }}</p>
      <p class="mt-auto pt-2 text-sm font-medium text-accent">
        Read <span class="inline-block transition-transform group-hover:translate-x-1" aria-hidden="true">→</span>
      </p>
    </div>
  </article>
</template>
