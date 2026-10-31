<script setup lang="ts">
defineProps<{ quote: string; attribution?: string | null }>()
</script>

<template>
  <figure class="not-prose my-14 border-l-4 border-accent pl-6 sm:pl-8">
    <blockquote class="font-display text-2xl leading-snug font-bold tracking-tight text-balance sm:text-3xl">
      “{{ quote }}”
    </blockquote>
    <figcaption v-if="attribution" class="mt-4 font-mono text-sm text-accent">— {{ attribution }}</figcaption>
  </figure>
</template>
