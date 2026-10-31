<script setup lang="ts">
// The site's mascot: a cheerful teal keycap with headphones, smiling with the sideways "3" from mah3uz.
// The same drawing lives in site/art/mascot.svg for the favicon and social card.
import { onBeforeUnmount, onMounted, ref, useId, useTemplateRef } from 'vue'

const props = withDefaults(defineProps<{ size?: string; alive?: boolean; label?: string }>(), {
  size: 'size-10',
  alive: false,
  label: '',
})

// Gradient ids must be unique per drawing on the page; useId is stable between server and browser.
const uid = useId()
const id = (name: string) => `${uid}-${name}`
const url = (name: string) => `url(#${id(name)})`

const look = ref({ x: 0, y: 0 })
const root = useTemplateRef<SVGSVGElement>('root')

function follow(event: PointerEvent) {
  const box = root.value?.getBoundingClientRect()
  if (!box) return
  const dx = event.clientX - (box.left + box.width / 2)
  const dy = event.clientY - (box.top + box.height / 2)
  const distance = Math.hypot(dx, dy) || 1
  const reach = Math.min(1, distance / 400)
  look.value = { x: (dx / distance) * 7 * reach, y: (dy / distance) * 6 * reach }
}

onMounted(() => {
  if (!props.alive || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
  window.addEventListener('pointermove', follow, { passive: true })
})
onBeforeUnmount(() => window.removeEventListener('pointermove', follow))
</script>

<template>
  <svg
    ref="root"
    :class="size"
    class="neat-mascot shrink-0"
    viewBox="0 0 512 512"
    :role="label ? 'img' : undefined"
    :aria-label="label || undefined"
    :aria-hidden="label ? undefined : 'true'"
  >
    <defs>
      <linearGradient :id="id('bg')" x1="0" y1="16" x2="0" y2="496" gradientUnits="userSpaceOnUse">
        <stop offset="0" stop-color="#15434E" />
        <stop offset="1" stop-color="#0A1A20" />
      </linearGradient>
      <radialGradient :id="id('glow')" cx="256" cy="270" r="230" gradientUnits="userSpaceOnUse">
        <stop offset="0" stop-color="#21BDB0" stop-opacity="0.5" />
        <stop offset="1" stop-color="#21BDB0" stop-opacity="0" />
      </radialGradient>
      <linearGradient :id="id('skirt')" x1="0" y1="170" x2="0" y2="440" gradientUnits="userSpaceOnUse">
        <stop offset="0" stop-color="#1A9FB3" />
        <stop offset="1" stop-color="#0F5F78" />
      </linearGradient>
      <linearGradient :id="id('top')" x1="0" y1="128" x2="0" y2="372" gradientUnits="userSpaceOnUse">
        <stop offset="0" stop-color="#8AF5E2" />
        <stop offset="0.55" stop-color="#3FD3C2" />
        <stop offset="1" stop-color="#21BDB0" />
      </linearGradient>
      <linearGradient :id="id('dish')" x1="0" y1="140" x2="0" y2="260" gradientUnits="userSpaceOnUse">
        <stop offset="0" stop-color="#FFFFFF" stop-opacity="0.5" />
        <stop offset="1" stop-color="#FFFFFF" stop-opacity="0" />
      </linearGradient>
      <linearGradient :id="id('cup')" x1="0" y1="226" x2="0" y2="330" gradientUnits="userSpaceOnUse">
        <stop offset="0" stop-color="#2A5560" />
        <stop offset="1" stop-color="#0E2B33" />
      </linearGradient>
    </defs>

    <rect x="16" y="16" width="480" height="480" rx="128" :fill="url('bg')" />
    <rect x="16" y="16" width="480" height="480" rx="128" :fill="url('glow')" />
    <path class="mz-spark" d="M92 112l6 14 14 6-14 6-6 14-6-14-14-6 14-6z" fill="#62EDD4" fill-opacity="0.75" />
    <path
      class="mz-spark mz-spark-late"
      d="M424 92l4 10 10 4-10 4-4 10-4-10-10-4 10-4z"
      fill="#A6D3D6"
      fill-opacity="0.65"
    />
    <circle cx="438" cy="170" r="5" fill="#62EDD4" fill-opacity="0.5" />
    <circle cx="74" cy="196" r="4" fill="#A6D3D6" fill-opacity="0.5" />
    <ellipse cx="256" cy="450" rx="140" ry="12" fill="#000" fill-opacity="0.35" />

    <g class="mz-body">
      <path
        d="M150 168H362Q398 168 404 204L420 392Q424 436 380 436H132Q88 436 92 392L108 204Q114 168 150 168Z"
        :fill="url('skirt')"
      />
      <path
        d="M132 436H380Q424 436 420 392L418 372Q410 404 372 404H140Q102 404 94 372L92 392Q88 436 132 436Z"
        fill="#043040"
        fill-opacity="0.3"
      />
      <rect x="132" y="128" width="248" height="248" rx="54" :fill="url('top')" />
      <path d="M186 140H326Q366 140 368 180Q330 160 256 160Q182 160 144 180Q146 140 186 140Z" :fill="url('dish')" />
      <rect
        x="132"
        y="128"
        width="248"
        height="248"
        rx="54"
        fill="none"
        stroke="#E9F7F7"
        stroke-opacity="0.35"
        stroke-width="3"
      />
      <path
        d="M160 202V170L174 188L188 170V202"
        fill="none"
        stroke="#0F5F78"
        stroke-opacity="0.55"
        stroke-width="6"
        stroke-linecap="round"
        stroke-linejoin="round"
      />

      <g class="mz-eyes">
        <ellipse cx="206" cy="262" rx="32" ry="36" fill="#FFFFFF" />
        <ellipse cx="306" cy="262" rx="32" ry="36" fill="#FFFFFF" />
        <g class="mz-pupils" :style="{ transform: `translate(${look.x}px, ${look.y}px)` }">
          <circle cx="210" cy="268" r="21" fill="#043040" />
          <circle cx="310" cy="268" r="21" fill="#043040" />
          <circle cx="201" cy="257" r="8" fill="#FFFFFF" />
          <circle cx="301" cy="257" r="8" fill="#FFFFFF" />
          <circle cx="217" cy="277" r="3.5" fill="#FFFFFF" fill-opacity="0.85" />
          <circle cx="317" cy="277" r="3.5" fill="#FFFFFF" fill-opacity="0.85" />
        </g>
      </g>

      <ellipse cx="166" cy="314" rx="20" ry="12" fill="#FF7D9C" fill-opacity="0.8" />
      <ellipse cx="346" cy="314" rx="20" ry="12" fill="#FF7D9C" fill-opacity="0.8" />
      <path
        d="M232 318Q244 336 256 318Q268 336 280 318"
        fill="none"
        stroke="#043040"
        stroke-width="8"
        stroke-linecap="round"
        stroke-linejoin="round"
      />

      <path d="M116 270C104 54 408 54 396 270" fill="none" stroke="#0E2B33" stroke-width="22" stroke-linecap="round" />
      <path
        d="M124 240C116 80 396 80 388 240"
        fill="none"
        stroke="#62EDD4"
        stroke-opacity="0.85"
        stroke-width="5"
        stroke-linecap="round"
      />
      <rect
        x="94"
        y="226"
        width="50"
        height="96"
        rx="24"
        :fill="url('cup')"
        stroke="#62EDD4"
        stroke-opacity="0.6"
        stroke-width="4"
      />
      <rect class="mz-beat" x="108" y="248" width="10" height="52" rx="5" fill="#62EDD4" fill-opacity="0.85" />
      <rect
        x="368"
        y="226"
        width="50"
        height="96"
        rx="24"
        :fill="url('cup')"
        stroke="#62EDD4"
        stroke-opacity="0.6"
        stroke-width="4"
      />
      <rect class="mz-beat" x="394" y="248" width="10" height="52" rx="5" fill="#62EDD4" fill-opacity="0.85" />
    </g>
  </svg>
</template>

<style>
.neat-mascot .mz-body {
  transform-box: view-box;
  transform-origin: 256px 440px;
  animation: mz-bob 4.5s ease-in-out infinite;
}
.neat-mascot .mz-eyes {
  transform-box: fill-box;
  transform-origin: center;
  animation: mz-blink 5.5s infinite;
}
.neat-mascot .mz-pupils {
  transition: transform 0.25s ease-out;
}
.neat-mascot .mz-spark {
  transform-box: fill-box;
  transform-origin: center;
  animation: mz-twinkle 3s ease-in-out infinite;
}
.neat-mascot .mz-spark-late {
  animation-delay: -1.5s;
}
.neat-mascot .mz-beat {
  animation: mz-beat 1.2s ease-in-out infinite;
}
.neat-mascot:hover .mz-body {
  animation: mz-hop 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes mz-bob {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}
@keyframes mz-blink {
  0%,
  92%,
  100% {
    transform: scaleY(1);
  }
  95% {
    transform: scaleY(0.08);
  }
}
@keyframes mz-twinkle {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.3;
    transform: scale(0.6);
  }
}
@keyframes mz-beat {
  0%,
  100% {
    opacity: 0.85;
  }
  50% {
    opacity: 0.35;
  }
}
@keyframes mz-hop {
  0% {
    transform: translateY(0) scale(1, 1);
  }
  30% {
    transform: translateY(0) scale(1.06, 0.92);
  }
  60% {
    transform: translateY(-22px) scale(0.96, 1.05);
  }
  100% {
    transform: translateY(0) scale(1, 1);
  }
}
@media (prefers-reduced-motion: reduce) {
  .neat-mascot * {
    animation: none !important;
  }
}
</style>
