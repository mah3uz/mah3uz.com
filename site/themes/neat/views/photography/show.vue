<script setup lang="ts">
// One photograph: the image, what it is, how it was taken (camera, exposure, place, tags, from the photo_details
// global the "Photo details from Unsplash" task fills) and how it has done on Unsplash.
import { Link } from '@inertiajs/vue3'
import { useGlobals } from '@nibble'
import { computed } from 'vue'
import type { PhotoDetailsGlobals, PhotosPhoto } from '@site/types'
import Corners from '../../components/Corners.vue'
import UnsplashImage from '../../components/UnsplashImage.vue'
import { vReveal } from '../../lib/motion'
import { compact, detailsFor, exposureSettings, referral } from '../../lib/unsplash'
import { isoDate, useFormatDate } from '../../lib/format'
import ArrowIcon from '../../components/ArrowIcon.vue'

const props = defineProps<{ page: PhotosPhoto }>()
const formatDate = useFormatDate()

const globals = useGlobals<PhotoDetailsGlobals>('photo_details')
const details = computed(() => detailsFor(globals.value.photos, props.page.unsplash_id))
const settings = computed(() => exposureSettings(details.value))
const tags = computed(() =>
  (details.value?.tags ?? '')
    .split(',')
    .map((tag) => tag.trim())
    .filter(Boolean),
)
const map = computed(() => {
  const { latitude, longitude } = details.value ?? {}
  if (!latitude || !longitude) return undefined
  return `https://www.openstreetmap.org/?mlat=${latitude}&mlon=${longitude}#map=11/${latitude}/${longitude}`
})
const hasExif = computed(() => Boolean(details.value?.camera || settings.value.length))

const alt = computed(() => props.page.title || props.page.description || 'A photograph by Mahfuz Shaikh')

// Lucide-style strokes, one per setting.
const icons: Record<string, string> = {
  aperture:
    'M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20Zm2.31 6 5.74 9.94M9.69 8h11.48M7.38 12l5.74-9.94M9.69 16 3.95 6.06M14.31 16H2.83m13.79-4-5.74 9.94',
  exposure: 'M12 5a8 8 0 1 0 0 16 8 8 0 0 0 0-16Zm0 4v4l2.5 2.5M9 2h6',
  focal_length:
    'M3 7V5a2 2 0 0 1 2-2h2m10 0h2a2 2 0 0 1 2 2v2m0 10v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2m9-8a3 3 0 1 0 0 6 3 3 0 0 0 0-6Z',
  iso: 'M6 4h12a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2Zm3 5h6v6H9z',
}
</script>

<template>
  <article>
    <Link href="/photography" class="neat-button-ghost group animate-rise mb-8 gap-2 text-sm">
      <svg
        class="size-4 transition-transform duration-300 group-hover:-translate-x-1"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <path d="M19 12H5m7 7-7-7 7-7" />
      </svg>
      All photographs
    </Link>

    <figure
      class="animate-rise overflow-hidden rounded-[2rem] [animation-delay:80ms]"
      :style="{ backgroundColor: page.color ?? 'var(--neat-surface-strong)' }"
    >
      <UnsplashImage
        :raw="page.image_raw"
        :image="page.image"
        :width="page.width"
        :height="page.height"
        :color="page.color"
        :blur-hash="page.blur_hash"
        :alt="alt"
        :base="1600"
        eager
        sizes="(min-width: 72rem) 72rem, 100vw"
        class="mx-auto w-fit max-w-full"
        img-class="block max-h-[82vh] w-auto max-w-full"
      />
    </figure>

    <div class="mt-10 grid gap-8 lg:grid-cols-[1fr_20rem]">
      <div class="grid content-start gap-10">
        <header>
          <h1 class="font-display text-3xl font-extrabold tracking-[-0.03em] first-letter:uppercase sm:text-4xl">
            {{ page.title || 'Untitled' }}
          </h1>
          <p v-if="page.description" class="mt-4 max-w-[60ch] text-lg leading-8 text-muted">
            {{ page.description }}
          </p>
          <p class="text-faint mt-6 text-sm">
            Photo by
            <a :href="referral('https://unsplash.com/@mah3uz')" class="neat-link text-accent" rel="noopener"
              >Mahfuz Shaikh</a
            >
            on
            <a :href="referral('https://unsplash.com')" class="neat-link text-accent" rel="noopener">Unsplash</a>
          </p>
        </header>

        <!-- How it was taken, read like the display on the back of a camera. -->
        <section
          v-if="hasExif || details?.location || tags.length"
          v-reveal
          aria-labelledby="exif-heading"
          class="neat-card relative p-6 sm:p-8"
        >
          <Corners inset="0.75rem" size="1.25rem" />
          <header v-if="hasExif" class="flex items-center gap-4">
            <span
              class="grid size-12 shrink-0 place-items-center rounded-2xl bg-accent/12 text-accent"
              aria-hidden="true"
            >
              <svg
                class="size-6"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.75"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3Z" />
                <circle cx="12" cy="13" r="3" />
              </svg>
            </span>
            <div class="min-w-0">
              <h2 id="exif-heading" class="text-faint font-mono text-xs tracking-wider uppercase">Shot on</h2>
              <p class="font-display truncate text-xl font-extrabold tracking-tight">
                {{ details?.camera || 'Camera not recorded' }}
              </p>
            </div>
          </header>
          <h2 v-else id="exif-heading" class="sr-only">About this photo</h2>

          <dl v-if="settings.length" class="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
            <div
              v-for="setting in settings"
              :key="setting.key"
              class="border-line bg-canvas/60 grid gap-3 rounded-2xl border p-4"
            >
              <dt class="text-faint flex items-center gap-2 font-mono text-[0.7rem] tracking-wider uppercase">
                <svg
                  class="size-4 text-accent"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.75"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  aria-hidden="true"
                >
                  <path :d="icons[setting.key]" />
                </svg>
                {{ setting.label }}
              </dt>
              <dd class="font-mono text-xl font-semibold tracking-tight tabular-nums">{{ setting.value }}</dd>
            </div>
          </dl>

          <div
            v-if="details?.location || tags.length"
            class="grid gap-4"
            :class="{ 'border-line mt-6 border-t pt-6': hasExif }"
          >
            <p v-if="details?.location" class="flex items-center gap-3">
              <svg
                class="size-5 shrink-0 text-accent"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.75"
                stroke-linecap="round"
                stroke-linejoin="round"
                aria-hidden="true"
              >
                <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z" />
                <circle cx="12" cy="10" r="3" />
              </svg>
              <a v-if="map" :href="map" target="_blank" rel="noopener" class="neat-link font-medium">{{
                details.location
              }}</a>
              <span v-else class="font-medium">{{ details.location }}</span>
            </p>
            <ul v-if="tags.length" role="list" aria-label="Tags" class="flex flex-wrap gap-2">
              <li v-for="tag in tags" :key="tag">
                <a
                  :href="referral(`https://unsplash.com/s/photos/${encodeURIComponent(tag.replace(/\s+/g, '-'))}`)"
                  target="_blank"
                  rel="noopener"
                  class="border-line inline-block rounded-full border px-3 py-1 font-mono text-xs text-muted transition-colors hover:border-accent hover:text-accent"
                  >{{ tag }}</a
                >
              </li>
            </ul>
          </div>
        </section>
      </div>

      <aside class="grid content-start gap-4">
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
        <Link href="/photography" class="neat-button-ghost group justify-center gap-2 text-sm"
          ><ArrowIcon direction="left" class="transition-transform duration-300 group-hover:-translate-x-1" /> Back to
          all photographs</Link
        >
      </aside>
    </div>
  </article>
</template>
