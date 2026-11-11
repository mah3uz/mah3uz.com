<script setup lang="ts">
// The lamp's rheostat dial, built like a safe dial: a fixed index tab at the top, and under it a dark scale plate,
// a knurled brushed-metal ring and a domed engraved cap that all turn together. 0-10 on the lamp maps to OFF-100 on
// the scale. Drag it round, click to step it on, or use the arrow keys; it snaps to each detent.
import { computed, ref } from 'vue'

const props = withDefaults(defineProps<{ label: string; max?: number }>(), { max: 10 })
const value = defineModel<number>({ required: true })

const STEP = 30
const round = (n: number) => Math.round(n * 100) / 100
const rotation = computed(() => -value.value * STEP)
const ticks = Array.from({ length: 101 }, (_, u) => {
  const a = ((u * 3 - 90) * Math.PI) / 180
  const inner = u % 10 === 0 ? 79 : u % 5 === 0 ? 84 : 87.5
  return {
    x1: round(Math.cos(a) * 93),
    y1: round(Math.sin(a) * 93),
    x2: round(Math.cos(a) * inner),
    y2: round(Math.sin(a) * inner),
    w: u % 10 === 0 ? 1.7 : u % 5 === 0 ? 1.2 : 0.7,
  }
})
const numbers = Array.from({ length: 11 }, (_, i) => ({ text: i === 0 ? 'OFF' : String(i * 10), a: i * STEP }))

const dial = ref<HTMLElement | null>(null)
const turning = ref(false)
let last = 0
let turned = 0
let from = 0
let pressed = false

const set = (next: number) => (value.value = Math.min(props.max, Math.max(0, Math.round(next))))

function angleOf(event: PointerEvent) {
  const box = dial.value!.getBoundingClientRect()
  const x = event.clientX - (box.left + box.width / 2)
  const y = event.clientY - (box.top + box.height / 2)
  return (Math.atan2(x, -y) * 180) / Math.PI
}

function down(event: PointerEvent) {
  pressed = true
  last = angleOf(event)
  turned = 0
  from = value.value
  dial.value?.setPointerCapture(event.pointerId)
}

// The dial turns under the finger: turning it clockwise brings the lower numbers up to the index.
function move(event: PointerEvent) {
  if (!pressed) return
  const angle = angleOf(event)
  let delta = angle - last
  if (delta > 180) delta -= 360
  if (delta < -180) delta += 360
  last = angle
  turned += delta
  if (!turning.value && Math.abs(turned) < 6) return
  turning.value = true
  set(from - turned / STEP)
}

function up() {
  if (pressed && !turning.value) set(value.value >= props.max ? 0 : value.value + 1)
  pressed = false
  turning.value = false
}

function key(event: KeyboardEvent) {
  const steps: Record<string, number> = {
    ArrowRight: value.value + 1,
    ArrowUp: value.value + 1,
    ArrowLeft: value.value - 1,
    ArrowDown: value.value - 1,
    PageUp: value.value + 3,
    PageDown: value.value - 3,
    Home: 0,
    End: props.max,
  }
  if (!(event.key in steps)) return
  event.preventDefault()
  set(steps[event.key])
}
</script>

<template>
  <div class="ns-rheo">
    <span class="ns-rheo-index" aria-hidden="true" />
    <div
      ref="dial"
      class="ns-rheo-dial"
      :class="{ 'is-turning': turning }"
      :style="{ rotate: `${rotation}deg` }"
      role="slider"
      tabindex="0"
      :aria-label="label"
      aria-valuemin="0"
      :aria-valuemax="max"
      :aria-valuenow="value"
      :aria-valuetext="value === 0 ? 'off' : `${value * 10}%`"
      @pointerdown="down"
      @pointermove="move"
      @pointerup="up"
      @pointercancel="up"
      @keydown="key"
    >
      <svg class="ns-rheo-plate" viewBox="-100 -100 200 200" aria-hidden="true">
        <defs>
          <radialGradient id="ns-rheo-plate">
            <stop offset="0.6" stop-color="var(--ns-plate-hi)" />
            <stop offset="1" stop-color="var(--ns-plate-lo)" />
          </radialGradient>
        </defs>
        <circle r="97" fill="url(#ns-rheo-plate)" />
        <line
          v-for="(tick, index) in ticks"
          :key="index"
          :x1="tick.x1"
          :y1="tick.y1"
          :x2="tick.x2"
          :y2="tick.y2"
          :stroke-width="tick.w"
          stroke="var(--ns-dial-ink)"
        />
        <text
          v-for="number in numbers"
          :key="number.text"
          class="ns-rheo-num"
          :transform="`rotate(${number.a}) translate(0 -70)`"
          text-anchor="middle"
          dominant-baseline="central"
        >
          {{ number.text }}
        </text>
      </svg>
      <span class="ns-rheo-knurl" aria-hidden="true" />
      <span class="ns-rheo-cap" aria-hidden="true">
        <svg viewBox="-50 -50 100 100">
          <defs>
            <path id="ns-rheo-arc" d="M0 37 A37 37 0 1 1 0.01 37" />
          </defs>
          <circle r="16" fill="none" stroke="var(--ns-engrave)" stroke-width="0.6" />
          <circle r="28" fill="none" stroke="var(--ns-engrave)" stroke-width="0.6" />
          <path d="M0 -45 L-3.6 -39 L3.6 -39 Z" fill="var(--ns-engrave-deep)" />
          <text class="ns-rheo-engraving">
            <textPath href="#ns-rheo-arc" startOffset="52%">MAH3UZ · LAMP</textPath>
          </text>
        </svg>
      </span>
    </div>
  </div>
</template>

<style>
/* The bezel round the whole dial, with its contact shadow on the box. */
.ns-rheo {
  position: relative;
  width: var(--ns-dial, 8.75rem);
  aspect-ratio: 1;
  padding: 3px;
  border-radius: 50%;
  background: conic-gradient(
    from 30deg,
    var(--ns-chrome-hi),
    var(--ns-chrome-lo) 25%,
    var(--ns-chrome-hi) 50%,
    var(--ns-chrome-mid) 70%,
    var(--ns-chrome-lo) 85%,
    var(--ns-chrome-hi)
  );
  box-shadow:
    0 0.5rem 0.9rem var(--ns-drop),
    0 0.1rem 0.15rem var(--ns-drop);
}
/* The index tab does not turn; the dial turns under it. */
.ns-rheo-index {
  position: absolute;
  z-index: 2;
  left: 50%;
  top: -0.45rem;
  width: 1.15rem;
  height: 0.8rem;
  margin-left: -0.575rem;
  border-radius: 2px 2px 3px 3px;
  background: linear-gradient(180deg, var(--ns-chrome-hi), var(--ns-chrome-mid) 55%, var(--ns-chrome-lo));
  box-shadow: 0 1px 2px var(--ns-drop);
}
.ns-rheo-index::after {
  content: '';
  position: absolute;
  left: 50%;
  top: 0.2rem;
  width: 0.55rem;
  height: 0.55rem;
  margin-left: -0.275rem;
  clip-path: polygon(0 0, 100% 0, 50% 100%);
  background: var(--ns-index);
}
.ns-rheo-dial {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  cursor: grab;
  touch-action: none;
  transition: rotate 0.34s cubic-bezier(0.3, 1.5, 0.45, 1);
}
.ns-rheo-dial.is-turning {
  cursor: grabbing;
  transition-duration: 0.12s;
}
.ns-rheo-dial:focus-visible {
  outline: 2px solid var(--ns-focus);
  outline-offset: 6px;
}
.ns-rheo-plate {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}
.ns-rheo-num {
  font:
    700 13px/1 var(--font-body),
    sans-serif;
  letter-spacing: 0.02em;
  fill: var(--ns-dial-ink);
}
/* The knurled ring: fine ridges over a brushed-metal sweep. */
.ns-rheo-knurl {
  position: absolute;
  inset: 21%;
  border-radius: 50%;
  background:
    repeating-conic-gradient(from 0deg, var(--ns-knurl-hi) 0 1.5deg, var(--ns-knurl-lo) 1.5deg 3deg),
    conic-gradient(
      from 20deg,
      var(--ns-chrome-hi),
      var(--ns-chrome-mid) 20%,
      var(--ns-chrome-lo) 38%,
      var(--ns-chrome-hi) 55%,
      var(--ns-chrome-mid) 75%,
      var(--ns-chrome-lo) 90%,
      var(--ns-chrome-hi)
    );
  box-shadow:
    0 2px 4px var(--ns-drop),
    inset 0 0 0 1px var(--ns-shade);
}
/* The domed cap, lit from the top left, with its engraving. */
.ns-rheo-cap {
  position: absolute;
  inset: 26%;
  border-radius: 50%;
  background:
    radial-gradient(circle at 32% 26%, var(--ns-chrome-hi) 0 6%, transparent 30%),
    conic-gradient(from 200deg, transparent, var(--ns-sheen), transparent 30%, var(--ns-shade) 55%, transparent 80%),
    radial-gradient(circle at 40% 35%, var(--ns-chrome-hi), var(--ns-chrome-mid) 55%, var(--ns-chrome-lo));
  box-shadow:
    inset 0 -2px 4px var(--ns-shade),
    0 0 0 1.5px var(--ns-chrome-lo),
    0 2px 3px var(--ns-drop);
}
.ns-rheo-cap svg {
  display: block;
  width: 100%;
  height: 100%;
}
.ns-rheo-engraving {
  font:
    700 7.5px/1 var(--font-body),
    sans-serif;
  letter-spacing: 0.32em;
  fill: var(--ns-engrave-deep);
}
@media (prefers-reduced-motion: reduce) {
  .ns-rheo-dial {
    transition: none;
  }
}
</style>
