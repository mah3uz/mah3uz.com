<script setup lang="ts">
// The mechanism under the carriage, from the reference's buildMech: the basket well with its 42 typebars, the
// segment, two ribbon spools feeding the vibrator, the margin bell, louvres, and the type guide at the printing point
// (0, 0). swing() lifts a bar along a curve to the printing point and drops it back; the frame loop runs only while a
// bar is in the air.
import { onBeforeUnmount, ref, watch } from 'vue'
import { BAR_COUNT, barOf } from './keyboard'

const props = defineProps<{ strikes: number; char: string; bells: number; spin: number }>()

const round = (n: number) => Math.round(n * 100) / 100
const E = 0.6
const TOP = 58
const FY = TOP + 7
const RW = 150
const RI = RW * 0.3
const RO = RW - 5
const SR = 40
const SX = RW + 12 + SR
const SY = TOP + 67
const BW = 860
const bwid = RW / 62
const arc = (r: number) => `M${-r} ${FY} A${r} ${round(r * E)} 0 0 0 ${r} ${FY}`

const geo = Array.from({ length: BAR_COUNT }, (_, i) => {
  const a = ((166 - i * (152 / (BAR_COUNT - 1))) * Math.PI) / 180
  const dx = Math.cos(a)
  const dy = Math.sin(a) * E
  return {
    px: round(RI * dx),
    py: round(FY + RI * dy),
    hx: round(RO * dx),
    hy: round(FY + RO * dy),
    sx: round(RO * dx - dx * RW * 0.07),
    sy: round(FY + RO * dy - dy * RW * 0.07),
    tone: i % 3,
  }
})
const spokes = [0, 1, 2].map((i) => {
  const a = i * 2.094 + 0.5
  return { x: round(Math.cos(a) * SR), y: round(Math.sin(a) * SR) }
})

const hidden = ref(new Set<number>())
const pool = ref<SVGGElement[]>([])
const ring = ref<SVGCircleElement | null>(null)
const dome = ref<SVGGElement | null>(null)
const vib = ref<SVGGElement | null>(null)
type Swing = { el: SVGGElement; i: number; t0: number; lx: number | null; ly: number }
const swings: Swing[] = []
let raf = 0
const UP = 62
const HOLD = 12
const DOWN = 105
const still = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches

function tick(now: number) {
  raf = 0
  for (let n = swings.length - 1; n >= 0; n--) {
    const w = swings[n]
    const t = Math.max(0, now - w.t0)
    const G = geo[w.i]
    let p: number
    let rising = false
    if (t < UP) {
      p = Math.pow(t / UP, 2.3)
      rising = true
    } else if (t < UP + HOLD) p = 1
    else if (t < UP + HOLD + DOWN) p = Math.pow(1 - (t - UP - HOLD) / DOWN, 3)
    else {
      w.el.style.display = 'none'
      hidden.value.delete(w.i)
      swings.splice(n, 1)
      continue
    }
    const q = 1 - p
    const cxp = G.px * 0.85
    const cyp = G.py - RW * 0.42
    const x = q * q * G.hx + 2 * q * p * cxp
    const y = q * q * G.hy + 2 * q * p * cyp
    const near = 1 + 0.75 * Math.sin(Math.PI * p)
    const dx = x - G.px
    const dy = y - G.py
    const L = Math.hypot(dx, dy) || 1
    const sl = RW * 0.08 * near
    const [poly, arm, slug] = Array.from(w.el.children) as SVGElement[]
    arm.setAttribute('x1', String(G.px))
    arm.setAttribute('y1', String(G.py))
    arm.setAttribute('x2', String(x))
    arm.setAttribute('y2', String(y))
    arm.setAttribute('stroke-width', String(bwid * 1.25 * near))
    slug.setAttribute('x1', String(x - (dx / L) * sl))
    slug.setAttribute('y1', String(y - (dy / L) * sl))
    slug.setAttribute('x2', String(x))
    slug.setAttribute('y2', String(y))
    slug.setAttribute('stroke-width', String(bwid * 3 * near))
    if (rising && w.lx !== null) {
      poly.setAttribute('points', `${G.px},${G.py} ${w.lx},${w.ly} ${x},${y}`)
      poly.style.display = ''
    } else poly.style.display = 'none'
    w.lx = x
    w.ly = y
  }
  if (swings.length && !document.hidden) raf = requestAnimationFrame(tick)
}

function swing(i: number) {
  if (still()) return
  const el = pool.value.find((candidate) => candidate.style.display === 'none')
  if (!el) return
  el.style.display = ''
  hidden.value.add(i)
  swings.push({ el, i, t0: performance.now(), lx: null, ly: 0 })
  raf ||= requestAnimationFrame(tick)
}

watch(
  () => props.strikes,
  () => {
    if (props.char === ' ') return
    swing(barOf(props.char))
    if (still()) return
    vib.value?.animate(
      [
        { transform: 'translateY(0)' },
        { transform: 'translateY(-16.5px)', offset: 0.38 },
        { transform: 'translateY(-16.5px)', offset: 0.5 },
        { transform: 'translateY(0)' },
      ],
      { duration: 170, easing: 'cubic-bezier(.3,.9,.4,1)' },
    )
  },
)
watch(
  () => props.bells,
  () => {
    if (still()) return
    for (const el of [ring.value, dome.value]) {
      if (!el) continue
      el.classList.remove('go')
      void el.getBoundingClientRect()
      el.classList.add('go')
    }
  },
)

onBeforeUnmount(() => cancelAnimationFrame(raf))
</script>

<template>
  <svg class="ns-mech" :viewBox="`${-BW / 2} -24 ${BW} 200`" aria-hidden="true">
    <defs>
      <radialGradient id="ns-gCh" cx="35%" cy="30%" r="80%">
        <stop offset="0" stop-color="var(--ns-chrome-hi)" />
        <stop offset="0.45" stop-color="var(--ns-chrome-mid)" />
        <stop offset="1" stop-color="var(--ns-chrome-lo)" />
      </radialGradient>
      <linearGradient id="ns-gWl" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="var(--ns-well)" />
        <stop offset="1" stop-color="var(--ns-well-2)" />
      </linearGradient>
    </defs>
    <g v-for="i in 3" :key="`louvre-${i}`" class="ns-louvre">
      <rect :x="BW / 2 - 76" :y="TOP + 14 + (i - 1) * 7" width="46" height="3" rx="1.5" fill="var(--ns-enamel-lo)" />
      <rect :x="BW / 2 - 76" :y="TOP + 17 + (i - 1) * 7" width="46" height="1" fill="var(--ns-sheen)" />
    </g>
    <path :d="`${arc(RW + 9)} Z`" fill="url(#ns-gWl)" stroke="var(--ns-enamel-lo)" stroke-width="2" />
    <path :d="arc(RW + 9)" fill="none" stroke="var(--ns-sheen)" stroke-width="1.2" transform="translate(0,1.6)" />
    <path :d="arc(RO + 1)" fill="none" stroke="var(--ns-rubber)" :stroke-width="RW * 0.06" />
    <g>
      <g v-for="(G, i) in geo" :key="i" :style="{ opacity: hidden.has(i) ? 0 : 1 }">
        <line
          :x1="G.px"
          :y1="G.py"
          :x2="G.hx"
          :y2="G.hy"
          :stroke="['var(--ns-chrome-lo)', 'var(--ns-chrome-hi)', 'var(--ns-chrome-mid)'][G.tone]"
          :stroke-width="bwid"
        />
        <line :x1="G.sx" :y1="G.sy" :x2="G.hx" :y2="G.hy" stroke="var(--ns-chrome-hi)" :stroke-width="bwid * 2.3" />
      </g>
    </g>
    <path :d="arc(RI)" fill="none" stroke="var(--ns-chrome-lo)" :stroke-width="RW * 0.05" />
    <path
      :d="arc(RI)"
      fill="none"
      stroke="var(--ns-well)"
      :stroke-width="RW * 0.05"
      :stroke-dasharray="`1.2 ${round((Math.PI * RI * 0.8) / BAR_COUNT - 1.2)}`"
    />
    <path
      :d="`M${-RI * 0.55} ${FY} A${RI * 0.55} ${round(RI * 0.55 * E)} 0 0 0 ${RI * 0.55} ${FY} Z`"
      fill="var(--ns-chrome-lo)"
      stroke="var(--ns-well)"
    />

    <g v-for="d in [-1, 1]" :key="`ribbon-${d}`">
      <path
        :d="`M${d * (SX - SR * 0.45)} ${SY - SR * 0.8} L${d * 15} 12`"
        stroke="var(--ns-ribbon)"
        stroke-width="3.2"
        fill="none"
      />
      <path
        :d="`M${d * (SX - SR * 0.45)} ${SY - SR * 0.8 + 1.6} L${d * 15} 13.6`"
        stroke="var(--ns-red)"
        stroke-width="1.3"
        fill="none"
      />
    </g>
    <g v-for="d in [-1, 1]" :key="`spool-${d}`" :transform="`translate(${d * SX},${SY})`">
      <circle :r="SR + 2" cy="4" fill="var(--ns-drop)" />
      <circle :r="SR * 0.9" fill="var(--ns-ribbon)" />
      <circle :r="SR * 0.66" fill="none" stroke="var(--ns-red)" :stroke-width="SR * 0.1" opacity="0.9" />
      <g class="ns-spin" :style="{ rotate: `${d < 0 ? spin : spin * 0.8 + 30}deg` }">
        <circle :r="SR" fill="none" stroke="url(#ns-gCh)" :stroke-width="SR * 0.13" />
        <template v-for="(k, j) in spokes" :key="j">
          <path
            :d="`M0 0 L${k.x} ${k.y}`"
            stroke="var(--ns-chrome-mid)"
            :stroke-width="SR * 0.2"
            stroke-linecap="round"
          />
          <path :d="`M0 0 L${k.x} ${k.y}`" stroke="var(--ns-chrome-hi)" :stroke-width="SR * 0.05" opacity="0.7" />
        </template>
        <circle :r="SR * 0.3" fill="url(#ns-gCh)" stroke="var(--ns-chrome-lo)" />
        <path :d="`M${-SR * 0.16} 0H${SR * 0.16}`" stroke="var(--ns-well)" stroke-width="2" />
      </g>
    </g>
    <g :transform="`translate(${-BW / 2 + 40},${TOP + 26})`">
      <circle ref="ring" class="ns-ring" r="10" fill="none" stroke="var(--ns-chrome-hi)" stroke-width="1.5" />
      <g ref="dome" class="ns-dome">
        <circle r="10" fill="url(#ns-gCh)" stroke="var(--ns-chrome-lo)" />
        <circle r="2.8" fill="var(--ns-well)" />
        <circle r="1.6" cx="-0.6" cy="-0.6" fill="var(--ns-chrome-hi)" />
      </g>
    </g>

    <path
      d="M-17 13 L-12 2 L-12 13Z M17 13 L12 2 L12 13Z"
      fill="var(--ns-chrome-hi)"
      stroke="var(--ns-chrome-lo)"
      stroke-width="0.8"
    />
    <path
      class="ns-caret"
      d="M-4.5 8 L0 3.2 L4.5 8"
      fill="none"
      stroke="var(--ns-red)"
      stroke-width="1.8"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    <g ref="vib">
      <g transform="translate(0,17)">
        <path
          d="M-17 7V-9M17 7V-9M-17 7H17"
          fill="none"
          stroke="var(--ns-chrome-lo)"
          stroke-width="3.4"
          stroke-linecap="round"
        />
        <path
          d="M-17 7V-9M17 7V-9M-17 7H17"
          fill="none"
          stroke="var(--ns-chrome-hi)"
          stroke-width="1.8"
          stroke-linecap="round"
        />
        <rect x="-15.5" y="-8" width="31" height="4.2" fill="var(--ns-ribbon)" />
        <rect x="-15.5" y="-3.8" width="31" height="4.2" fill="var(--ns-red)" />
        <rect x="-15.5" y="-8" width="31" height="1" fill="var(--ns-sheen)" />
      </g>
    </g>
    <g v-for="slot in 4" :key="`swing-${slot}`" ref="pool" style="display: none">
      <polygon fill="var(--ns-sheen)" />
      <line stroke="var(--ns-chrome-hi)" stroke-linecap="round" />
      <line stroke="var(--ns-chrome-hi)" />
    </g>
  </svg>
</template>

<style>
.ns-mech {
  position: absolute;
  z-index: 2;
  left: 0;
  top: 0;
  width: 100%;
  overflow: visible;
  translate: 0 -12%;
  pointer-events: none;
}
.ns-spin {
  transform-box: fill-box;
  transform-origin: center;
  transition: rotate 260ms cubic-bezier(0.2, 0.8, 0.3, 1);
}
.ns-caret {
  animation: ns-pulse 1.9s cubic-bezier(0.45, 0, 0.55, 1) infinite;
}
@keyframes ns-pulse {
  0%,
  100% {
    opacity: 0.28;
  }
  50% {
    opacity: 1;
  }
}
.ns-ring {
  opacity: 0;
  transform-box: fill-box;
  transform-origin: center;
}
.ns-ring.go {
  animation: ns-ring 900ms cubic-bezier(0.1, 0.7, 0.2, 1);
}
@keyframes ns-ring {
  0% {
    opacity: 0.9;
    transform: scale(1);
  }
  100% {
    opacity: 0;
    transform: scale(3.4);
  }
}
.ns-dome.go {
  animation: ns-dome 500ms cubic-bezier(0.3, 2.2, 0.4, 1);
}
@keyframes ns-dome {
  0% {
    transform: translate(0, 0);
  }
  20% {
    transform: translate(1.4px, -0.6px);
  }
  45% {
    transform: translate(-1px, 0.4px);
  }
  100% {
    transform: translate(0, 0);
  }
}
@media (prefers-reduced-motion: reduce) {
  .ns-spin {
    transition: none;
  }
  .ns-caret {
    animation: none;
    opacity: 0.85;
  }
}
</style>
