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

/** v-spotlight lets a .neat-card's glow follow the pointer, updating at most once a frame. */
export const vSpotlight: Directive<HTMLElement> = {
  mounted(el) {
    if (window.matchMedia('(pointer: coarse)').matches) return
    let frame = 0
    let x = 0
    let y = 0
    el.addEventListener('pointermove', (event: PointerEvent) => {
      x = event.clientX
      y = event.clientY
      if (frame) return
      frame = requestAnimationFrame(() => {
        frame = 0
        const box = el.getBoundingClientRect()
        el.style.setProperty('--mx', `${x - box.left}px`)
        el.style.setProperty('--my', `${y - box.top}px`)
      })
    })
  },
}

/**
 * v-tilt leans an element gently toward the pointer. It eases toward the target on every frame rather than starting
 * a CSS transition on every pointer move, which is what makes a tilt judder.
 */
export const vTilt: Directive<HTMLElement, number | undefined> = {
  mounted(el, binding) {
    if (reduced() || window.matchMedia('(pointer: coarse)').matches) return
    const strength = binding.value ?? 6
    const target = { x: 0, y: 0 }
    const current = { x: 0, y: 0 }
    let frame = 0

    function step() {
      current.x += (target.x - current.x) * 0.12
      current.y += (target.y - current.y) * 0.12
      el.style.transform = `perspective(1000px) rotateX(${current.y.toFixed(3)}deg) rotateY(${current.x.toFixed(3)}deg)`
      const settled = Math.abs(target.x - current.x) < 0.01 && Math.abs(target.y - current.y) < 0.01
      frame = settled ? 0 : requestAnimationFrame(step)
    }
    const run = () => (frame ||= requestAnimationFrame(step))

    el.style.willChange = 'transform'
    el.addEventListener('pointermove', (event: PointerEvent) => {
      const box = el.getBoundingClientRect()
      target.x = ((event.clientX - box.left) / box.width - 0.5) * strength
      target.y = -((event.clientY - box.top) / box.height - 0.5) * strength
      run()
    })
    el.addEventListener('pointerleave', () => {
      target.x = 0
      target.y = 0
      run()
    })
  },
}
