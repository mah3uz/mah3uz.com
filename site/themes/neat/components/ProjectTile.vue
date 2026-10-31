<script setup lang="ts">
// A project's logo. Products use their own logo, from /logos; where there isn't one (client work, for now), a plain
// monogram in the project's accent stands in.
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    logo?: string | null
    monogram?: string | null
    accent?: string | null
    size?: string
    text?: string
  }>(),
  { logo: null, monogram: null, accent: null, size: 'size-12', text: 'text-lg' },
)
const base = computed(() => props.accent || '#21BDB0')
</script>

<template>
  <img
    v-if="logo"
    :src="logo"
    alt=""
    aria-hidden="true"
    :class="size"
    class="shrink-0 object-contain drop-shadow-[0_8px_14px_rgba(4,48,64,0.28)]"
    width="96"
    height="96"
    loading="lazy"
  />
  <span
    v-else
    :class="[size, text]"
    class="font-display relative inline-grid shrink-0 place-items-center rounded-[26%] font-extrabold tracking-tight text-white shadow-lg shadow-black/20"
    :style="{
      background: `linear-gradient(160deg, color-mix(in oklab, ${base} 55%, #62EDD4) 0%, ${base} 55%, color-mix(in oklab, ${base} 70%, #043040) 100%)`,
    }"
    aria-hidden="true"
  >
    <span class="absolute inset-[1px] rounded-[inherit] bg-gradient-to-b from-white/25 to-transparent to-50%" />
    <span class="relative leading-none">{{ monogram || '•' }}</span>
  </span>
</template>
