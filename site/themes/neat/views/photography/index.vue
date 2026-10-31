<script setup lang="ts">
// Photography: the photos are files beside their Markdown (site/content/photography/), published at responsive
// sizes by Nibble, laid out as a masonry wall. Each opens its own page; the profile lives on Unsplash.
import { Link } from '@inertiajs/vue3'
import { RichText } from '@nibble'
import { computed } from 'vue'
import type { PhotographyPhoto, ViewProps } from '@site/types'
import Corners from '../../components/Corners.vue'
import PageHeading from '../../components/PageHeading.vue'
import { vReveal } from '../../lib/motion'

const props = defineProps<ViewProps['photography/index'] & { page: PhotographyPhoto }>()

// The folder's index page is a member of the collection too; the wall wants only the photos under it.
const photos = computed(() => props.photos.filter((photo) => photo.uri?.split('/').length === 3))
const profile = computed(() => props.page.unsplash || 'https://unsplash.com/@mah3uz')
</script>

<template>
  <div>
    <PageHeading :title="page.title" eyebrow="Away from the keyboard" :description="page.description">
      <a
        :href="profile"
        target="_blank"
        rel="me noopener"
        class="neat-button animate-rise mt-8 [animation-delay:240ms]"
      >
        <svg class="size-4" viewBox="0 0 32 32" fill="currentColor" aria-hidden="true">
          <path d="M10 9V0h12v9H10zm12 5h10v18H0V14h10v9h12v-9z" />
        </svg>
        See everything on Unsplash
      </a>
    </PageHeading>

    <div v-if="photos.length" class="columns-1 gap-5 sm:columns-2 lg:columns-3">
      <Link
        v-for="(photo, index) in photos"
        :key="photo.id"
        v-reveal="(index % 3) * 90"
        :href="photo.uri ?? '#'"
        class="group border-line bg-midnight relative mb-5 block break-inside-avoid overflow-hidden rounded-[1.5rem] border"
      >
        <RichText
          :value="photo.body"
          class="[&_img]:w-full [&_img]:transition-transform [&_img]:duration-700 [&_img]:ease-[cubic-bezier(0.16,1,0.3,1)] group-hover:[&_img]:scale-[1.03] [&_p]:m-0"
        />
        <div
          class="absolute inset-x-0 bottom-0 translate-y-2 bg-[linear-gradient(180deg,transparent,rgba(10,26,32,0.9))] p-5 pt-16 text-white opacity-0 transition-all duration-500 group-hover:translate-y-0 group-hover:opacity-100 group-focus-visible:translate-y-0 group-focus-visible:opacity-100"
        >
          <p class="font-display text-lg font-bold">{{ photo.title }}</p>
          <p class="text-mist font-mono text-xs">
            {{ [photo.location, photo.taken].filter(Boolean).join(' · ') }}
          </p>
        </div>
      </Link>
    </div>

    <section
      v-else
      class="border-line bg-midnight relative overflow-hidden rounded-[2.5rem] border p-10 text-center text-white sm:p-16"
    >
      <Corners inset="1.25rem" />
      <div class="neat-dots absolute inset-0" aria-hidden="true" />
      <p class="neat-eyebrow !text-mint relative">On Unsplash</p>
      <p class="font-display relative mx-auto mt-4 max-w-[22ch] text-3xl font-extrabold tracking-tight sm:text-4xl">
        The full collection lives on my Unsplash profile.
      </p>
      <a :href="profile" target="_blank" rel="me noopener" class="neat-button !bg-mint !text-abyss relative mt-8"
        >Open unsplash.com/@mah3uz ↗</a
      >
    </section>
  </div>
</template>
