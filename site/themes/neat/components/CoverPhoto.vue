<script setup lang="ts">
// A photograph laid over generated art: if the photo cannot load, the art is still there, so a page is never blank.
import { onMounted, ref, useTemplateRef } from 'vue'

withDefaults(
  defineProps<{ src?: string | null; art?: string | null; alt: string; credit?: string | null; eager?: boolean }>(),
  { src: null, art: null, credit: null, eager: false },
)
const failed = ref(false)
const loaded = ref(false)
const photo = useTemplateRef<HTMLImageElement>('photo')

// The photo may have finished, or failed, before the page became interactive; check once it is.
onMounted(() => {
  const img = photo.value
  if (!img?.complete) return
  if (img.naturalWidth > 0) loaded.value = true
  else failed.value = true
})
</script>

<template>
  <figure class="border-line bg-midnight relative overflow-hidden rounded-[1.75rem] border">
    <img
      v-if="art"
      :src="art"
      alt=""
      aria-hidden="true"
      class="absolute inset-0 size-full object-cover"
      width="1600"
      height="1000"
    />
    <img
      v-if="src && !failed"
      ref="photo"
      :src="src"
      :alt="alt"
      :loading="eager ? 'eager' : 'lazy'"
      referrerpolicy="no-referrer"
      class="relative size-full object-cover transition-opacity duration-1000 ease-out"
      :class="loaded ? 'opacity-100' : 'opacity-0'"
      @load="loaded = true"
      @error="failed = true"
    />
    <div
      class="pointer-events-none absolute inset-0 bg-[linear-gradient(180deg,transparent_55%,#0a1a20cc)]"
      aria-hidden="true"
    />
    <figcaption
      v-if="credit && loaded"
      class="absolute right-4 bottom-3 font-mono text-[0.65rem] tracking-wide text-white/70"
    >
      {{ credit }}
    </figcaption>
    <slot />
  </figure>
</template>
