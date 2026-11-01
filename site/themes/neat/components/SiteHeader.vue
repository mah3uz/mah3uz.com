<script setup lang="ts">
import { Link, usePage } from '@inertiajs/vue3'
import { useGlobals, useNavigation } from '@nibble'
import { computed, onBeforeUnmount, onMounted, ref, useTemplateRef, watch } from 'vue'
import type { SiteGlobals } from '@site/types'
import BrandMark from './BrandMark.vue'
import CommandPalette from './CommandPalette.vue'
import { socialLinks } from '../lib/links'
import MenuLink from './MenuLink.vue'
import ThemeSwitch from './ThemeSwitch.vue'

interface PaletteProject {
  id: number | string
  title: string | null
  uri: string | null
  tagline?: string | null
  monogram?: string | null
  logo?: string | null
  accent?: string | null
}

const props = withDefaults(defineProps<{ projects?: PaletteProject[] }>(), { projects: () => [] })

const site = useGlobals<SiteGlobals>('site')
const menu = useNavigation('main')
const page = usePage()

// The menu comes from the Control Plane; until it is set up, the site still has somewhere to go.
const FALLBACK = [
  { title: 'Work', url: '/projects' },
  { title: 'Now', url: '/now' },
  { title: 'Writing', url: '/blog' },
  { title: 'Uses', url: '/uses' },
  { title: 'About', url: '/about' },
]
const links = computed(() => {
  const items = menu.value?.filter((item) => item.url) ?? []
  return items.length
    ? items.map((item) => ({ title: item.title, url: item.url as string, new_tab: item.new_tab }))
    : FALLBACK.map((item) => ({ ...item, new_tab: false }))
})
const current = (url: string) =>
  page.url === url || (url !== '/' && page.url.startsWith(`${url}/`)) || page.url.startsWith(`${url}?`)

const socials = computed(() => socialLinks(site.value?.social_links))
const scrolled = ref(false)
const menuOpen = ref(false)
const palette = useTemplateRef<InstanceType<typeof CommandPalette>>('palette')
const themeSwitch = useTemplateRef<InstanceType<typeof ThemeSwitch>>('themeSwitch')
const mac = ref(true)

function onScroll() {
  scrolled.value = window.scrollY > 12
}

function toggleTheme() {
  themeSwitch.value?.toggle(new MouseEvent('click'))
}

watch(
  () => page.url,
  () => (menuOpen.value = false),
)

onMounted(() => {
  onScroll()
  mac.value = /Mac|iPhone|iPad/.test(navigator.platform)
  window.addEventListener('scroll', onScroll, { passive: true })
})
onBeforeUnmount(() => window.removeEventListener('scroll', onScroll))
</script>

<template>
  <header class="sticky top-0 z-50 px-5 pt-3 sm:px-8 sm:pt-4" @keydown.escape="menuOpen = false">
    <div
      class="max-w-frame mx-auto flex items-center justify-between gap-4 rounded-full border px-3 py-2 transition-all duration-500 ease-[cubic-bezier(0.16,1,0.3,1)] sm:px-4"
      :class="
        scrolled || menuOpen
          ? 'border-line bg-surface-strong/95 shadow-[0_20px_50px_-30px_rgba(4,48,64,0.5)]'
          : 'border-transparent bg-transparent'
      "
    >
      <Link href="/" class="flex items-center gap-3 rounded-full pr-2" aria-label="Home">
        <BrandMark size="size-9" />
        <span class="font-display text-lg font-extrabold tracking-tight">{{ site?.name ?? 'mah3uz' }}</span>
      </Link>

      <nav aria-label="Main navigation" class="max-lg:hidden">
        <ul class="flex items-center gap-1" role="list">
          <li v-for="link in links" :key="link.url">
            <MenuLink
              :item="{ ...link, current: current(link.url), in_trail: current(link.url) }"
              class="relative block rounded-full px-4 py-2 text-sm font-medium transition-colors hover:text-accent"
              :class="current(link.url) ? 'text-ink bg-accent/12' : 'text-muted'"
            />
          </li>
        </ul>
      </nav>

      <div class="flex items-center gap-1">
        <button
          type="button"
          class="border-line hover:text-ink flex h-10 items-center gap-3 rounded-full border px-3 text-sm text-muted transition-colors hover:border-accent max-sm:w-10 max-sm:justify-center max-sm:px-0"
          aria-label="Open the command palette"
          @click="palette?.show()"
        >
          <svg class="size-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <circle cx="11" cy="11" r="7" />
            <path d="m20 20-3.5-3.5" />
          </svg>
          <span class="max-sm:hidden">Jump to</span>
          <kbd class="border-line rounded-md border px-1.5 font-mono text-[0.65rem] max-sm:hidden">{{
            mac ? '⌘K' : 'Ctrl K'
          }}</kbd>
        </button>
        <ThemeSwitch ref="themeSwitch" />
        <button
          type="button"
          class="grid size-10 place-items-center rounded-full lg:hidden"
          :aria-expanded="menuOpen"
          aria-controls="mobile-navigation"
          aria-label="Menu"
          @click="menuOpen = !menuOpen"
        >
          <span class="relative block h-3 w-5" aria-hidden="true">
            <span
              class="absolute left-0 h-0.5 w-5 rounded bg-current transition-all duration-300"
              :class="menuOpen ? 'top-1.5 rotate-45' : 'top-0'"
            />
            <span
              class="absolute left-0 h-0.5 w-5 rounded bg-current transition-all duration-300"
              :class="menuOpen ? 'top-1.5 -rotate-45' : 'top-3'"
            />
          </span>
        </button>
      </div>
    </div>

    <Transition
      enter-active-class="transition duration-500 ease-[cubic-bezier(0.16,1,0.3,1)]"
      enter-from-class="-translate-y-3 opacity-0"
      leave-active-class="transition duration-200"
      leave-to-class="-translate-y-2 opacity-0"
    >
      <nav
        v-show="menuOpen"
        id="mobile-navigation"
        aria-label="Mobile navigation"
        class="border-line bg-surface-strong max-w-frame mx-auto mt-2 rounded-3xl border p-3 shadow-xl lg:hidden"
      >
        <ul role="list">
          <li v-for="(link, index) in links" :key="link.url">
            <MenuLink
              :item="{ ...link, current: current(link.url), in_trail: current(link.url) }"
              class="font-display flex items-center justify-between rounded-2xl px-4 py-3 text-2xl font-bold"
              :class="current(link.url) ? 'bg-accent/12 text-accent' : ''"
              :style="{ transitionDelay: `${index * 40}ms` }"
            />
          </li>
        </ul>
      </nav>
    </Transition>

    <CommandPalette
      ref="palette"
      :projects="props.projects"
      :links="[{ title: 'Home', url: '/' }, ...links, { title: 'Search', url: '/search' }]"
      :socials="socials"
      @toggle-theme="toggleTheme"
    />
  </header>
</template>
