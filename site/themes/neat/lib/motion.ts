import type { Directive } from 'vue'

const reduced = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches

let observer: IntersectionObserver | null = null

function watch(el: HTMLElement) {
  observer ??= new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue
        entry.target.classList.add('neat-revealed')
        observer?.unobserve(entry.target)
      }
    },
    { rootMargin: '0px 0px -8% 0px', threshold: 0.08 },
  )
  observer.observe(el)
}

/**
 * v-reveal fades and lifts an element in as it scrolls into view. The value is a delay in milliseconds.
 * Nothing happens on the server or for people who prefer less motion, so the content is always there.
 */
export const vReveal: Directive<HTMLElement, number | undefined> = {
  mounted(el, binding) {
    if (reduced()) return
    if (binding.value) el.style.setProperty('--reveal-delay', `${binding.value}ms`)
    el.classList.add('neat-reveal')
    requestAnimationFrame(() => watch(el))
  },
  unmounted(el) {
    observer?.unobserve(el)
  },
}

/** v-spotlight lets a .neat-card's glow follow the pointer. */
export const vSpotlight: Directive<HTMLElement> = {
  mounted(el) {
    el.addEventListener('pointermove', (event: PointerEvent) => {
      const box = el.getBoundingClientRect()
      el.style.setProperty('--mx', `${event.clientX - box.left}px`)
      el.style.setProperty('--my', `${event.clientY - box.top}px`)
    })
  },
}

/** v-tilt leans an element gently toward the pointer. */
export const vTilt: Directive<HTMLElement, number | undefined> = {
  mounted(el, binding) {
    if (reduced() || window.matchMedia('(pointer: coarse)').matches) return
    const strength = binding.value ?? 6
    el.style.transition = 'transform 0.6s cubic-bezier(0.16, 1, 0.3, 1)'
    el.addEventListener('pointermove', (event: PointerEvent) => {
      const box = el.getBoundingClientRect()
      const x = (event.clientX - box.left) / box.width - 0.5
      const y = (event.clientY - box.top) / box.height - 0.5
      el.style.transform = `perspective(1000px) rotateX(${-y * strength}deg) rotateY(${x * strength}deg)`
    })
    el.addEventListener('pointerleave', () => (el.style.transform = ''))
  },
}
