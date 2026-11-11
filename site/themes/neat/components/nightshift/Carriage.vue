<script setup lang="ts">
// The carriage under the paper, from the reference: the platen with its ribbed knobs, the paper bail with two
// rollers and the margin scale (ticks every five columns, numbers every ten, the tab stops in red), and the chrome
// return lever, which swings when the carriage is thrown and can be pulled. NightShift moves all of it with the paper.
import { ref, watch } from 'vue'

const props = defineProps<{ returns: number; columns: number; cell: number; tab: number }>()
const emit = defineEmits<{ return: [] }>()

const lever = ref<HTMLElement | null>(null)
watch(
  () => props.returns,
  () => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
    lever.value?.animate(
      [{ transform: 'rotate(0)' }, { transform: 'rotate(11deg)', offset: 0.3 }, { transform: 'rotate(0)' }],
      {
        duration: 420,
        easing: 'cubic-bezier(.2,1.5,.4,1)',
      },
    )
  },
)
</script>

<template>
  <div class="ns-carriage">
    <div class="ns-bail" aria-hidden="true">
      <span class="ns-roller" style="left: 22%" />
      <span class="ns-roller" style="right: 22%" />
      <span class="ns-scale">
        <template v-for="c in Math.floor(columns / 5) + 1" :key="c">
          <i :style="{ left: `${(c - 1) * 5 * cell}px` }" />
          <b v-if="(c - 1) % 2 === 0" :style="{ left: `${(c - 1) * 5 * cell}px` }">{{ (c - 1) * 5 }}</b>
        </template>
        <u v-for="t in Math.floor((columns - 3) / tab)" :key="`t${t}`" :style="{ left: `${(2 + t * tab) * cell}px` }" />
      </span>
    </div>
    <div class="ns-platen" aria-hidden="true">
      <span class="ns-knob is-left" />
      <span class="ns-knob is-right" />
    </div>
    <span class="ns-lever-mount" aria-hidden="true" />
    <button ref="lever" type="button" class="ns-lever" aria-label="Carriage return lever" @click="emit('return')">
      <svg viewBox="0 0 204 120" aria-hidden="true">
        <path
          d="M198 68 C150 70 118 44 52 34"
          fill="none"
          stroke="var(--ns-chrome-lo)"
          stroke-width="11"
          stroke-linecap="round"
        />
        <path
          d="M198 68 C150 70 118 44 52 34"
          fill="none"
          stroke="var(--ns-chrome-mid)"
          stroke-width="8"
          stroke-linecap="round"
        />
        <path
          d="M196 66 C150 67 118 41 54 31.5"
          fill="none"
          stroke="var(--ns-chrome-hi)"
          stroke-width="2.2"
          stroke-linecap="round"
          opacity=".85"
        />
        <ellipse cx="38" cy="31" rx="30" ry="11.5" transform="rotate(-9 38 31)" fill="var(--ns-chrome-lo)" />
        <ellipse cx="38" cy="30" rx="28" ry="10" transform="rotate(-9 38 30)" fill="var(--ns-chrome-mid)" />
        <ellipse
          cx="34"
          cy="27"
          rx="19"
          ry="4.5"
          transform="rotate(-9 34 27)"
          fill="var(--ns-chrome-hi)"
          opacity=".8"
        />
        <circle cx="197" cy="68" r="8" fill="var(--ns-rubber)" />
        <circle cx="196" cy="67" r="4" fill="var(--ns-chrome-hi)" />
      </svg>
    </button>
  </div>
</template>
