<script setup lang="ts">
// A photo hot-linked from Unsplash, at the size the layout asks for. Until it arrives, its dominant colour and a
// blurred preview decoded from its BlurHash hold its place; the photo fades in over them once it has loaded.
import { computed, onMounted, ref } from 'vue'
import { blurPreview, sized, srcset } from '../lib/unsplash'

const props = withDefaults(
  defineProps<{
    raw?: string | null
    image?: string | null
    width?: number | null
    height?: number | null
    color?: string | null
    blurHash?: string | null
    alt: string
    sizes: string
    base?: number
    eager?: boolean
    imgClass?: string
  }>(),
  { raw: null, image: null, width: null, height: null, color: null, blurHash: null, base: 800, imgClass: '' },
)

const preview = computed(() => blurPreview(props.blurHash, props.width, props.height))

// Server-rendered HTML shows the photo as soon as the browser has it. Only a photo still loading when the page wakes
// up is hidden, so it can fade in rather than paint in strips.
const img = ref<HTMLImageElement>()
const waiting = ref(false)
onMounted(() => {
  if (img.value && !img.value.complete) waiting.value = true
})
</script>

<template>
  <div class="relative isolate overflow-hidden" :style="{ backgroundColor: color ?? 'var(--neat-surface-strong)' }">
    <div
      v-if="preview"
      aria-hidden="true"
      class="absolute inset-0 -z-10 scale-110 bg-cover bg-center blur-xl"
      :style="{ backgroundImage: `url(${preview})` }"
    />
    <img
      ref="img"
      :src="sized(raw ?? image, base)"
      :srcset="srcset(raw)"
      :sizes="sizes"
      :width="width ?? undefined"
      :height="height ?? undefined"
      :alt="alt"
      :loading="eager ? 'eager' : 'lazy'"
      :fetchpriority="eager ? 'high' : undefined"
      decoding="async"
      class="transition-[opacity,transform] duration-700 ease-[cubic-bezier(0.16,1,0.3,1)]"
      :class="[imgClass, { 'opacity-0': waiting }]"
      @load="waiting = false"
      @error="waiting = false"
    />
  </div>
</template>
