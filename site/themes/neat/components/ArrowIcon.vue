<script setup lang="ts">
// An arrow drawn as an icon rather than typed as a character, so it sits on the text's centre line in every font.
// Sized to the text around it; the caller adds any hover movement.
withDefaults(defineProps<{ direction?: 'left' | 'right' }>(), { direction: 'right' })
</script>

<template>
  <svg
    class="inline-block size-[1.1em] shrink-0 align-[-0.2em]"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <path :d="direction === 'left' ? 'M19 12H5m7 7-7-7 7-7' : 'M5 12h14m-7-7 7 7-7 7'" />
  </svg>
</template>
