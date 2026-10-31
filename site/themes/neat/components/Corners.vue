<script setup lang="ts">
// Three viewfinder corners, as on the banners, drawn in when they mount. The fourth corner belongs to the peel.
withDefaults(defineProps<{ inset?: string; size?: string; four?: boolean }>(), {
  inset: '0',
  size: '1.75rem',
  four: false,
})
</script>

<template>
  <div class="pointer-events-none absolute" :style="{ inset }" aria-hidden="true">
    <span
      v-for="corner in four ? ['tl', 'tr', 'bl', 'br'] : ['tl', 'tr', 'bl']"
      :key="corner"
      class="animate-corner border-bracket absolute"
      :style="{ width: size, height: size, animationDelay: `${['tl', 'tr', 'bl', 'br'].indexOf(corner) * 90 + 150}ms` }"
      :class="{
        'top-0 left-0 rounded-tl-xl border-t-[3px] border-l-[3px]': corner === 'tl',
        'top-0 right-0 rounded-tr-xl border-t-[3px] border-r-[3px]': corner === 'tr',
        'bottom-0 left-0 rounded-bl-xl border-b-[3px] border-l-[3px]': corner === 'bl',
        'right-0 bottom-0 rounded-br-xl border-r-[3px] border-b-[3px]': corner === 'br',
      }"
    />
  </div>
</template>
