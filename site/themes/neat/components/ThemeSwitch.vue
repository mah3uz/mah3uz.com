<script setup lang="ts">
import { onMounted, ref } from 'vue'

const dark = ref(false)

// The shell reads this cookie into <html data-theme>, so the next page arrives in the chosen register.
function remember(theme: string) {
  document.cookie = `nibble_theme=${theme}; path=/; max-age=31536000; samesite=lax`
  document.documentElement.dataset.theme = theme
}

onMounted(() => {
  const theme = document.documentElement.dataset.theme
  dark.value = theme ? theme === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches
})

function apply() {
  dark.value = !dark.value
  remember(dark.value ? 'dark' : 'light')
}

// Where the browser supports view transitions, the new register widens out from the switch in a circle.
function toggle(event: MouseEvent) {
  const doc = document as Document & { startViewTransition?: (callback: () => void) => { ready: Promise<void> } }
  if (!doc.startViewTransition || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return apply()

  const x = event.clientX || window.innerWidth - 40
  const y = event.clientY || 40
  const radius = Math.hypot(Math.max(x, window.innerWidth - x), Math.max(y, window.innerHeight - y))
  doc.startViewTransition(apply).ready.then(() => {
    document.documentElement.animate(
      { clipPath: [`circle(0px at ${x}px ${y}px)`, `circle(${radius}px at ${x}px ${y}px)`] },
      { duration: 650, easing: 'cubic-bezier(0.16, 1, 0.3, 1)', pseudoElement: '::view-transition-new(root)' },
    )
  })
}

defineExpose({ toggle })
</script>

<template>
  <button
    type="button"
    role="switch"
    aria-label="Dark mode"
    :aria-checked="dark"
    :title="dark ? 'Switch to light' : 'Switch to dark'"
    class="text-ink relative grid size-10 place-items-center overflow-hidden rounded-full transition-colors hover:bg-accent/10 hover:text-accent"
    @click="toggle"
  >
    <svg
      class="size-5"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      aria-hidden="true"
    >
      <mask id="neat-moon">
        <rect width="24" height="24" fill="white" />
        <circle
          cx="24"
          cy="10"
          r="6"
          fill="black"
          class="transition-transform duration-500 ease-[cubic-bezier(0.16,1,0.3,1)]"
          :class="dark ? '-translate-x-[7px]' : ''"
        />
      </mask>
      <circle
        cx="12"
        cy="12"
        fill="currentColor"
        stroke="none"
        mask="url(#neat-moon)"
        class="transition-all duration-500"
        :r="dark ? 8 : 5"
      />
      <g class="origin-center transition-all duration-500" :class="dark ? 'scale-50 rotate-45 opacity-0' : ''">
        <path d="M12 1.5v2m0 17v2M4.6 4.6l1.4 1.4m12 12 1.4 1.4M1.5 12h2m17 0h2M4.6 19.4l1.4-1.4m12-12 1.4-1.4" />
      </g>
    </svg>
  </button>
</template>
