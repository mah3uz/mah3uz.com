<script setup lang="ts">
defineProps<{ title: string | null; eyebrow?: string | null; description?: string | null }>()
</script>

<template>
  <header class="relative mb-14 max-w-4xl pt-6 lg:mb-20">
    <p v-if="eyebrow" class="neat-eyebrow animate-rise mb-6 flex items-center gap-3">
      <span class="h-px w-8 bg-accent" aria-hidden="true" />{{ eyebrow }}
    </p>
    <h1
      class="animate-rise font-display text-5xl font-extrabold tracking-[-0.035em] text-balance [animation-delay:80ms] sm:text-7xl"
    >
      {{ title }}
    </h1>
    <p
      v-if="description"
      class="animate-rise mt-7 max-w-[56ch] text-lg leading-8 text-pretty text-muted [animation-delay:160ms] sm:text-xl sm:leading-9"
    >
      {{ description }}
    </p>
    <slot />
  </header>
</template>
