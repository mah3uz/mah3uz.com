<script setup lang="ts">
// A page or post's artwork: drawn for the site (see site/art/generate.py), so it always fills its frame. The art
// carries no corners or peel of its own; they are laid on here, where they can change and animate.
import Corners from './Corners.vue'
import Peel, { peelCut } from './Peel.vue'

withDefaults(defineProps<{ src?: string | null; alt?: string; eager?: boolean }>(), {
  src: null,
  alt: '',
  eager: false,
})

const PEEL = 104
</script>

<template>
  <div v-if="src" class="group relative">
    <figure
      class="neat-peeled relative size-full overflow-hidden rounded-[1.75rem]"
      :style="{ '--peel-cut': peelCut(PEEL) }"
    >
      <img
        :src="src"
        :alt="alt"
        :aria-hidden="alt ? undefined : 'true'"
        :loading="eager ? 'eager' : 'lazy'"
        width="1600"
        height="1000"
        class="size-full object-cover"
      />
      <Corners inset="1.25rem" />
      <slot />
    </figure>
    <Peel :size="PEEL" />
  </div>
</template>
