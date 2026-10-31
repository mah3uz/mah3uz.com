<script setup lang="ts">
// A project's small app-icon tile: its accent gradient, the corner brackets and the peel, holding its monogram.
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{ monogram?: string | null; accent?: string | null; size?: string; text?: string }>(),
  { monogram: null, accent: null, size: 'size-12', text: 'text-lg' },
)
const base = computed(() => props.accent || '#21BDB0')
</script>

<template>
  <span
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
      <path d="M100 62C86 61 73 65 68 70C63 75 60 88 61 100H100Z" fill="#043040" fill-opacity="0.35" />
      <path d="M100 62C86 61 73 65 68 70C63 75 60 88 61 100Q78 78 100 62Z" fill="#E9F7F7" />
    </svg>
    <span :class="text" class="relative -translate-x-[6%] -translate-y-[6%] leading-none tracking-tight">{{
      monogram || '•'
    }}</span>
  </span>
</template>
