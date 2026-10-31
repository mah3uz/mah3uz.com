<script setup lang="ts">
// A page or post's artwork: drawn for the site (see site/art/generate.py), so it always fills its frame.
withDefaults(defineProps<{ src?: string | null; alt?: string; eager?: boolean }>(), {
  src: null,
  alt: '',
  eager: false,
})
</script>

<template>
  <figure v-if="src" class="border-line bg-midnight relative overflow-hidden rounded-[1.75rem] border">
    <img
      :src="src"
      :alt="alt"
      :aria-hidden="alt ? undefined : 'true'"
      :loading="eager ? 'eager' : 'lazy'"
      width="1600"
      height="1000"
      class="size-full object-cover"
    />
    <slot />
  </figure>
</template>
