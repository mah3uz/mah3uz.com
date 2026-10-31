<script setup lang="ts">
// The banners' peeled corner, for the bottom-right of a card. It lifts further when the card is hovered.
withDefaults(defineProps<{ size?: number }>(), { size: 72 })
</script>

<template>
  <svg
    class="pointer-events-none absolute right-0 bottom-0 origin-bottom-right scale-[0.82] transition-transform duration-700 ease-[cubic-bezier(0.16,1,0.3,1)] group-hover:scale-110"
    :width="size"
    :height="size"
    viewBox="0 0 104 104"
    aria-hidden="true"
  >
    <defs>
      <linearGradient id="peel-back" x1="0" y1="0" x2="0" y2="104" gradientUnits="userSpaceOnUse">
        <stop offset="0" style="stop-color: var(--neat-back-1)" />
        <stop offset="1" style="stop-color: var(--neat-back-2)" />
      </linearGradient>
      <linearGradient id="peel-flap" x1="93.6" y1="93.6" x2="20.8" y2="20.8" gradientUnits="userSpaceOnUse">
        <stop offset="0" stop-color="#A6D3D6" />
        <stop offset="0.5" stop-color="#E9F7F7" />
        <stop offset="1" stop-color="#FFFFFF" />
      </linearGradient>
      <filter id="peel-shadow" x="-40%" y="-40%" width="180%" height="180%">
        <feGaussianBlur stdDeviation="4" />
      </filter>
    </defs>
    <path d="M104 0Q45.76 45.76 0 104H104Z" fill="url(#peel-back)" />
    <path
      d="M104 0C68.64 -3.12 33.28 6.24 20.8 20.8C6.24 33.28 -3.12 68.64 0 104Q45.76 45.76 104 0Z"
      transform="translate(-5 6)"
      fill="#043040"
      fill-opacity="0.3"
      filter="url(#peel-shadow)"
    />
    <path
      d="M104 0C68.64 -3.12 33.28 6.24 20.8 20.8C6.24 33.28 -3.12 68.64 0 104Q45.76 45.76 104 0Z"
      fill="url(#peel-flap)"
    />
  </svg>
</template>
