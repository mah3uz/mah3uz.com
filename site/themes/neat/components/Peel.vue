<script setup lang="ts">
// The banners' peeled corner, for the bottom-right of a card. It lifts further when the card is hovered.
//
// Put it beside the card, not inside it, and give the card `neat-peeled` with `--peel-cut` set by peelCut() below:
// the card's corner is then cut away and the peel draws the corner itself — its back runs under the whole flap and
// rounds off with the card's radius — so nothing of the card shows round the peel's edges as a dark line.
import { computed } from 'vue'

const props = withDefaults(defineProps<{ size?: number; radius?: number }>(), { size: 72, radius: 28 })

// The peel rests at 82% of its size; the back's corner is drawn so that, at rest, it matches the card's.
const REST = 0.82
const r = computed(() => Math.min(90, (props.radius / REST) * (104 / props.size)))
const back = computed(
  () =>
    `M104 0C68.64 -3.12 33.28 6.24 20.8 20.8C6.24 33.28 -3.12 68.64 0 104H${104 - r.value}A${r.value} ${r.value} 0 0 0 104 ${104 - r.value}Z`,
)
</script>

<script lang="ts">
// How far in to cut the card's corner for a peel of this size: well inside the peel's back at rest.
export const peelCut = (size: number) => `${Math.round(size * 0.45)}px`
</script>

<template>
  <svg
    class="pointer-events-none absolute right-0 bottom-0 origin-bottom-right scale-[0.82] overflow-visible transition-transform duration-700 ease-[cubic-bezier(0.16,1,0.3,1)] group-hover:scale-110"
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
    </defs>
    <path :d="back" fill="url(#peel-back)" />
    <path
      d="M104 0C68.64 -3.12 33.28 6.24 20.8 20.8C6.24 33.28 -3.12 68.64 0 104Q45.76 45.76 104 0Z"
      fill="url(#peel-flap)"
    />
  </svg>
</template>
