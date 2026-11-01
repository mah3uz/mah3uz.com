<script setup lang="ts">
// Photography: my photographs on Unsplash, imported by the "Photos from Unsplash" scheduled task and hot-linked from
// Unsplash's image CDN as its guidelines ask. Most-viewed first, as a masonry wall.
import { Link } from '@inertiajs/vue3'
import { computed } from 'vue'
import type { ViewProps } from '@site/types'
import Corners from '../../components/Corners.vue'
import PageHeading from '../../components/PageHeading.vue'
import { vReveal } from '../../lib/motion'
import { useGlobals } from '@nibble'
import type { PhotoDetailsGlobals } from '@site/types'
import UnsplashImage from '../../components/UnsplashImage.vue'
import { compact, detailsFor, exposureSettings, PROFILE } from '../../lib/unsplash'

const props = defineProps<ViewProps['photography/index']>()

const details = useGlobals<PhotoDetailsGlobals>('photo_details')
const settings = (id: string | null | undefined) =>
  exposureSettings(detailsFor(details.value.photos, id)).map((setting) => setting.value)

const totals = computed(() => ({
  views: props.photos.reduce((sum, photo) => sum + (photo.views ?? 0), 0),
  downloads: props.photos.reduce((sum, photo) => sum + (photo.downloads ?? 0), 0),
}))
</script>

<template>
  <div>
    <PageHeading
      title="Photography"
      eyebrow="Away from the keyboard"
      description="Photographs I take away from the screen, published on Unsplash and free for anyone to use."
    >
      <div class="animate-rise mt-8 flex flex-wrap items-center gap-x-8 gap-y-4 [animation-delay:240ms]">
        <a :href="PROFILE" target="_blank" rel="me noopener" class="neat-button">
          <svg class="size-4" viewBox="0 0 32 32" fill="currentColor" aria-hidden="true">
            <path d="M10 9V0h12v9H10zm12 5h10v18H0V14h10v9h12v-9z" />
          </svg>
          See everything on Unsplash
        </a>
        <dl v-if="photos.length" class="flex gap-8 font-mono text-sm">
          <div class="flex flex-col-reverse">
            <dt class="text-faint text-xs">views</dt>
            <dd class="font-display text-2xl font-extrabold">{{ compact(totals.views) }}</dd>
          </div>
          <div class="flex flex-col-reverse">
            <dt class="text-faint text-xs">downloads</dt>
            <dd class="font-display text-2xl font-extrabold">{{ compact(totals.downloads) }}</dd>
          </div>
        </dl>
      </div>
    </PageHeading>

    <div v-if="photos.length" class="columns-1 gap-5 sm:columns-2 lg:columns-3">
      <div v-for="(photo, index) in photos" :key="photo.id" v-reveal="(index % 3) * 90" class="mb-5 break-inside-avoid">
        <Link :href="photo.uri ?? '#'" class="group border-line relative block overflow-hidden rounded-[1.5rem] border">
          <UnsplashImage
            :raw="photo.image_raw"
            :image="photo.image"
            :width="photo.width"
            :height="photo.height"
            :color="photo.color"
            :blur-hash="photo.blur_hash"
            :alt="photo.title || photo.description || 'A photograph by Mahfuz Shaikh'"
            sizes="(min-width: 64rem) 22rem, (min-width: 40rem) 50vw, 100vw"
            img-class="h-auto w-full group-hover:scale-[1.03]"
          />
          <div
            class="absolute inset-x-0 bottom-0 translate-y-2 bg-[linear-gradient(180deg,transparent,rgba(10,26,32,0.9))] p-5 pt-16 text-white opacity-0 transition-all duration-500 group-hover:translate-y-0 group-hover:opacity-100 group-focus-visible:translate-y-0 group-focus-visible:opacity-100"
          >
            <p v-if="photo.title" class="font-display line-clamp-2 font-bold first-letter:uppercase">
              {{ photo.title }}
            </p>
            <p class="text-mist mt-1 font-mono text-xs">
              {{ compact(photo.views) }} views · {{ compact(photo.downloads) }} downloads
            </p>
            <p v-if="settings(photo.unsplash_id).length" class="text-mist mt-1 font-mono text-[0.7rem] opacity-80">
              {{ settings(photo.unsplash_id).join(' · ') }}
            </p>
          </div>
        </Link>
      </div>
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
      <a :href="PROFILE" target="_blank" rel="me noopener" class="neat-button !bg-mint !text-abyss relative mt-8"
        >Open unsplash.com/@mah3uz ↗</a
      >
    </section>
  </div>
</template>
