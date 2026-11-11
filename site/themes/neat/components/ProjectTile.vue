<script setup lang="ts">
// A project's logo. Products use their own logo, from the asset library; where there isn't one (client work, for now), the
// site's tile stands in: the accent gradient, three corner brackets and the peel, holding the project's monogram.
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
    :class="size"
    class="font-display relative inline-grid shrink-0 place-items-center overflow-hidden rounded-[28%] font-extrabold text-white shadow-lg shadow-black/20"
    :style="{
      background: `linear-gradient(180deg, color-mix(in oklab, ${base} 55%, #62EDD4) 0%, ${base} 55%, color-mix(in oklab, ${base} 70%, #043040) 100%)`,
    }"
    aria-hidden="true"
  >
    <svg class="absolute inset-0 size-full" viewBox="0 0 100 100">
      <path
        d="M18 34V26A8 8 0 0 1 26 18H34M82 34V26A8 8 0 0 0 74 18H66M18 66V74A8 8 0 0 0 26 82H34"
        fill="none"
        stroke="white"
        stroke-opacity="0.75"
        stroke-width="5"
        stroke-linecap="round"
      />
      <path d="M100 62C86 61 73 65 68 70C63 75 60 88 61 100Q78 78 100 62Z" fill="#E9F7F7" />
    </svg>
    <span :class="text" class="relative -translate-x-[6%] -translate-y-[6%] leading-none tracking-tight">{{
      monogram || '•'
    }}</span>
  </span>
</template>
