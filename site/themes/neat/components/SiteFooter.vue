<script setup lang="ts">
import { Link } from '@inertiajs/vue3'
import { useGlobals, useNavigation } from '@nibble'
import { computed } from 'vue'
import type { SiteGlobals } from '@site/types'
import { socialLinks } from '../lib/links'
import { vReveal } from '../lib/motion'
import BrandMark from './BrandMark.vue'
import Corners from './Corners.vue'
import MenuLink from './MenuLink.vue'
import ArrowIcon from './ArrowIcon.vue'

const site = useGlobals<SiteGlobals>('site')
const footer = useNavigation('footer')

const FALLBACK = [
  { title: 'Work', url: '/projects' },
  { title: 'Now', url: '/now' },
  { title: 'Uses', url: '/uses' },
  { title: 'Writing', url: '/blog' },
  { title: 'About', url: '/about' },
  { title: 'Search', url: '/search' },
]
const links = computed(() => {
  const items = footer.value?.filter((item) => item.url) ?? []
  return items.length ? items.map((item) => ({ title: item.title, url: item.url as string })) : FALLBACK
})
const socials = computed(() => socialLinks(site.value?.social_links))
const year = new Date().getUTCFullYear()
</script>

<template>
  <footer class="relative mt-32 overflow-hidden px-5 pb-10 sm:px-8">
    <div v-reveal class="max-w-frame relative mx-auto">
      <section
        aria-labelledby="footer-cta"
        class="border-line bg-midnight neat-peeled relative overflow-hidden rounded-[2.5rem] border px-6 py-16 text-white [--peel-cut:32px] sm:px-14 sm:py-20 sm:[--peel-cut:36px]"
      >
        <div class="neat-dots absolute inset-0 opacity-60" aria-hidden="true" />
        <div
          class="animate-drift absolute -top-1/2 -left-1/4 size-[48rem] rounded-full bg-[radial-gradient(circle,#21bdb066,transparent_65%)]"
          aria-hidden="true"
        />
        <Corners inset="1.5rem" />
        <div class="relative grid items-end gap-10 pb-6 sm:pb-0 lg:grid-cols-[1.4fr_1fr] lg:pr-16">
          <div>
            <p class="neat-eyebrow !text-mint">Open for the right work</p>
            <h2
              id="footer-cta"
              class="font-display mt-5 text-4xl font-extrabold tracking-tight text-balance sm:text-6xl"
            >
              Have something <span class="neat-gradient-text">worth building</span>? Let’s talk.
            </h2>
            <p class="text-mist mt-6 max-w-[46ch] text-lg leading-8">
              Software built carefully, and the infrastructure to run it — from the first design to production and every
              day after. I’ve been doing both since 2009.
            </p>
          </div>
          <div class="flex flex-wrap gap-3 lg:justify-end">
            <Link
              href="/about#contact"
              class="bg-mint text-abyss inline-flex min-h-12 items-center gap-3 rounded-full px-6 py-3 font-semibold transition-transform duration-500 hover:-translate-y-0.5"
            >
              Start a conversation <ArrowIcon />
            </Link>
            <Link
              href="/projects"
              class="hover:border-mint inline-flex min-h-12 items-center gap-3 rounded-full border border-white/20 px-6 py-3 font-semibold transition-colors"
            >
              See the work
            </Link>
          </div>
        </div>
      </section>
      <svg
        class="pointer-events-none absolute right-0 bottom-0 size-16 overflow-visible sm:size-20"
        viewBox="0 0 104 104"
        aria-hidden="true"
      >
        <defs>
          <linearGradient id="cta-flap" x1="93.6" y1="93.6" x2="20.8" y2="20.8" gradientUnits="userSpaceOnUse">
            <stop offset="0" stop-color="#A6D3D6" />
            <stop offset="0.5" stop-color="#E9F7F7" />
            <stop offset="1" stop-color="#FFFFFF" />
          </linearGradient>
        </defs>
        <path
          d="M104 0C68.64 -3.12 33.28 6.24 20.8 20.8C6.24 33.28 -3.12 68.64 0 104H52A52 52 0 0 0 104 52Z"
          fill="#62EDD4"
        />
        <path
          d="M104 0C68.64 -3.12 33.28 6.24 20.8 20.8C6.24 33.28 -3.12 68.64 0 104Q45.76 45.76 104 0Z"
          fill="url(#cta-flap)"
        />
      </svg>
    </div>

    <div class="max-w-frame mx-auto mt-16 grid gap-10 sm:grid-cols-[1.5fr_1fr_1fr]">
      <div>
        <Link href="/" class="inline-flex items-center gap-3">
          <BrandMark size="size-10" />
          <span class="font-display text-xl font-extrabold tracking-tight">{{ site?.name ?? 'mah3uz' }}</span>
        </Link>
        <p class="mt-4 max-w-[36ch] leading-7 text-muted">
          {{ site?.tagline ?? 'Software engineer and Linux systems administrator since 2009.' }}
        </p>
      </div>
      <nav aria-label="Footer">
        <p class="neat-eyebrow mb-4">Explore</p>
        <ul role="list" class="grid gap-2">
          <li v-for="link in links" :key="link.url">
            <MenuLink
              :item="{ ...link, new_tab: false, current: false, in_trail: false }"
              class="neat-link hover:text-ink text-muted"
            />
          </li>
        </ul>
      </nav>
      <div>
        <p class="neat-eyebrow mb-4">Elsewhere</p>
        <ul role="list" class="grid gap-2">
          <li v-for="social in socials" :key="social.url">
            <a :href="social.url" rel="me noopener" target="_blank" class="neat-link hover:text-ink text-muted"
              >{{ social.label }} <span aria-hidden="true">↗</span></a
            >
          </li>
          <li><a href="/feed-posts.xml" class="neat-link hover:text-ink text-muted">RSS feed</a></li>
        </ul>
      </div>
    </div>

    <div
      class="border-line text-faint max-w-frame mx-auto mt-14 flex flex-wrap items-center justify-between gap-4 border-t pt-6 font-mono text-xs"
    >
      <p>© {{ year }} {{ site?.name ?? 'mah3uz' }} · Built on Nibble, dressed in Neat.</p>
      <p>Press <kbd class="border-line rounded border px-1.5">/</kbd> to jump anywhere</p>
    </div>
  </footer>
</template>
