<script setup lang="ts">
import { Link } from '@inertiajs/vue3'
import type { PhotosPhoto } from '@site/types'
import { compact, referral, sized, srcset } from '../../lib/unsplash'
import { isoDate, useFormatDate } from '../../lib/format'

defineProps<{ page: PhotosPhoto }>()
const formatDate = useFormatDate()
</script>

<template>
  <article>
    <nav aria-label="Breadcrumb" class="animate-rise text-faint mb-8 font-mono text-xs">
      <Link href="/photography" class="neat-link hover:text-accent">Photography</Link>
      <span class="mx-2" aria-hidden="true">/</span>
      <span aria-current="page" class="text-muted">Photo</span>
    </nav>
    <figure
      class="animate-rise border-line overflow-hidden rounded-[2rem] border [animation-delay:80ms]"
      :style="{ backgroundColor: page.color ?? '#0D2A31' }"
    >
      <img
        :src="sized(page.image_raw ?? page.image, 1600)"
        :srcset="srcset(page.image_raw)"
        sizes="(min-width: 72rem) 72rem, 100vw"
        :width="page.width ?? undefined"
        :height="page.height ?? undefined"
        :alt="page.title || page.description || 'A photograph by Mahfuz Shaikh'"
        class="mx-auto max-h-[82vh] w-auto"
      />
    </figure>
    <div class="mt-10 grid gap-8 lg:grid-cols-[1fr_20rem]">
      <header>
        <h1 class="font-display text-3xl font-extrabold tracking-[-0.03em] first-letter:uppercase sm:text-4xl">
          {{ page.title || 'Untitled' }}
        </h1>
        <p v-if="page.description" class="mt-4 max-w-[60ch] text-lg leading-8 text-muted">{{ page.description }}</p>
        <p class="text-faint mt-6 text-sm">
          Photo by
          <a :href="referral('https://unsplash.com/@mah3uz')" class="neat-link text-accent" rel="noopener"
            >Mahfuz Shaikh</a
          >
          on
          <a :href="referral('https://unsplash.com')" class="neat-link text-accent" rel="noopener">Unsplash</a>
        </p>
      </header>
      <dl class="neat-card grid content-start gap-4 p-6">
        <div class="grid grid-cols-3 gap-4 text-center">
          <div
            v-for="[label, value] in [
              ['views', page.views],
              ['downloads', page.downloads],
              ['likes', page.likes],
            ]"
            :key="label as string"
          >
            <dd class="font-display text-2xl font-extrabold">{{ compact(value as number) }}</dd>
            <dt class="text-faint font-mono text-xs">{{ label }}</dt>
          </div>
        </div>
        <div v-if="page.uploaded" class="border-line border-t pt-4">
          <dt class="text-faint font-mono text-xs tracking-wider uppercase">Published</dt>
          <dd class="mt-1 font-medium">
            <time :datetime="isoDate(page.uploaded)">{{
              formatDate(page.uploaded, { month: 'long', year: 'numeric' })
            }}</time>
          </dd>
        </div>
        <a :href="referral(page.page_url)" target="_blank" rel="noopener" class="neat-button mt-2 justify-center"
          >View on Unsplash ↗</a
        >
      </dl>
    </div>
  </article>
</template>
