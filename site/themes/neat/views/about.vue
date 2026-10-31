<script setup lang="ts">
import { Link } from '@inertiajs/vue3'
import { useGlobals } from '@nibble'
import { computed } from 'vue'
import type { PagesPage, SiteGlobals, ViewProps } from '@site/types'
import BrandMark from '../components/BrandMark.vue'
import ContactForm from '../components/ContactForm.vue'
import Corners from '../components/Corners.vue'
import CoverPhoto from '../components/CoverPhoto.vue'
import PageBody from '../components/PageBody.vue'
import ProjectTile from '../components/ProjectTile.vue'
import StatusPill from '../components/StatusPill.vue'
import { vReveal, vSpotlight, vTilt } from '../lib/motion'
import { socialLinks } from '../lib/links'
import { isClient, onlyProjects, statusLabel, statusOf } from '../lib/projects'

const props = defineProps<ViewProps['about'] & { page: PagesPage }>()
const site = useGlobals<SiteGlobals>('site')

const STARTED = 2009
const years = new Date().getUTCFullYear() - STARTED
const all = computed(() => onlyProjects(props.projects))
const socials = computed(() => socialLinks(site.value?.social_links))
const products = computed(() => all.value.filter((project) => !isClient(project)))
const timeline = computed(() => {
  const groups = new Map<string, typeof all.value>()
  ;[...all.value]
    .sort((a, b) => (b.year ?? '').localeCompare(a.year ?? ''))
    .forEach((project) => groups.set(project.year ?? '—', [...(groups.get(project.year ?? '—') ?? []), project]))
  return [...groups.entries()]
})
</script>

<template>
  <div>
    <section class="grid items-center gap-12 lg:grid-cols-[1.2fr_1fr]">
      <div>
        <p v-if="page.eyebrow" class="neat-eyebrow animate-rise flex items-center gap-3">
          <span class="h-px w-8 bg-accent" aria-hidden="true" />{{ page.eyebrow }}
        </p>
        <h1
          class="animate-rise font-display mt-6 text-5xl font-extrabold tracking-[-0.04em] text-balance [animation-delay:80ms] sm:text-7xl"
        >
          {{ page.title }}
        </h1>
        <p
          v-if="page.intro"
          class="animate-rise mt-7 max-w-[54ch] text-lg leading-8 text-muted [animation-delay:160ms] sm:text-xl sm:leading-9"
        >
          {{ page.intro }}
        </p>
      </div>
      <div class="animate-rise relative mx-auto w-full max-w-sm p-4 [animation-delay:240ms]">
        <Corners size="2rem" />
        <div
          v-tilt="8"
          class="bg-midnight shadow-abyss/40 relative overflow-hidden rounded-[2rem] p-8 text-white shadow-2xl"
        >
          <div class="neat-dots absolute inset-0" aria-hidden="true" />
          <div
            class="animate-drift absolute -top-24 -right-24 size-72 rounded-full bg-[radial-gradient(circle,#21bdb080,transparent_65%)]"
            aria-hidden="true"
          />
          <div class="relative">
            <BrandMark size="size-20" />
            <p class="font-display mt-8 text-3xl font-extrabold tracking-tight">{{ site?.name ?? 'mah3uz' }}</p>
            <p class="text-mist mt-1">Software engineer · since {{ STARTED }}</p>
            <dl class="mt-8 grid grid-cols-3 gap-4 border-t border-white/10 pt-6">
              <div>
                <dt class="text-mist/70 font-mono text-[0.65rem] tracking-wider uppercase">Years</dt>
                <dd class="font-display text-mint mt-1 text-2xl font-extrabold">{{ years }}+</dd>
              </div>
              <div>
                <dt class="text-mist/70 font-mono text-[0.65rem] tracking-wider uppercase">Products</dt>
                <dd class="font-display text-mint mt-1 text-2xl font-extrabold">{{ products.length }}</dd>
              </div>
              <div>
                <dt class="text-mist/70 font-mono text-[0.65rem] tracking-wider uppercase">Shipping</dt>
                <dd class="font-display text-mint mt-1 text-2xl font-extrabold">Still</dd>
              </div>
            </dl>
          </div>
        </div>
      </div>
    </section>

    <div class="mt-24 grid gap-14 lg:grid-cols-[1fr_22rem]">
      <PageBody :content="page.content" :blocks="page.blocks" large />
      <CoverPhoto
        v-if="page.photo"
        v-reveal
        :src="page.photo"
        art="/art/insensical.svg"
        alt="A focused workspace: a laptop and a desk at night"
        :credit="page.photo_credit"
        class="aspect-[4/5] self-start lg:sticky lg:top-28"
      />
    </div>

    <section v-if="page.cards?.length" aria-labelledby="principles" class="mt-28">
      <div v-reveal class="mb-10 max-w-2xl">
        <p class="neat-eyebrow">Principles</p>
        <h2 id="principles" class="font-display mt-3 text-4xl font-extrabold tracking-[-0.03em] sm:text-5xl">
          What {{ years }} years taught me to care about
        </h2>
      </div>
      <ol role="list" class="grid gap-5 sm:grid-cols-2">
        <li
          v-for="(card, index) in page.cards"
          :key="card.id ?? index"
          v-reveal="(index % 2) * 100"
          v-spotlight
          class="neat-card p-7 sm:p-8"
        >
          <span class="font-mono text-sm text-accent">0{{ index + 1 }}</span>
          <h3 class="font-display mt-3 text-2xl font-bold tracking-tight">{{ card.title }}</h3>
          <p class="mt-3 leading-7 text-muted">{{ card.text }}</p>
        </li>
      </ol>
    </section>

    <section v-if="timeline.length" aria-labelledby="timeline" class="mt-28">
      <div v-reveal class="mb-12 max-w-2xl">
        <p class="neat-eyebrow">Recent products</p>
        <h2 id="timeline" class="font-display mt-3 text-4xl font-extrabold tracking-[-0.03em] sm:text-5xl">
          What I’ve been building lately
        </h2>
      </div>
      <ol role="list" class="border-line-strong relative grid gap-12 border-l pl-8 sm:pl-12">
        <li v-for="[year, items] in timeline" :key="year" v-reveal class="relative">
          <span
            class="bg-canvas absolute top-1 -left-[2.55rem] grid size-5 place-items-center rounded-full border-2 border-accent sm:-left-[3.55rem]"
            aria-hidden="true"
            ><span class="size-1.5 rounded-full bg-accent"
          /></span>
          <p class="font-display text-3xl font-extrabold tracking-tight text-accent">{{ year }}</p>
          <ul role="list" class="mt-5 grid gap-3 md:grid-cols-2">
            <li v-for="project in items" :key="project.id">
              <Link
                :href="project.uri ?? '#'"
                class="group neat-card flex items-center gap-4 !rounded-2xl p-4 transition-transform duration-500 hover:-translate-y-0.5"
              >
                <ProjectTile
                  :logo="project.logo"
                  :monogram="project.monogram"
                  :accent="project.accent"
                  size="size-11"
                  text="text-base"
                />
                <span class="min-w-0 flex-1">
                  <span class="font-display block font-bold">{{ project.title }}</span>
                  <span class="block truncate text-sm text-muted">{{ project.tagline }}</span>
                </span>
                <StatusPill :status="statusOf(project)" :label="statusLabel(project)" class="max-sm:hidden" />
              </Link>
            </li>
          </ul>
        </li>
      </ol>
    </section>

    <section id="contact" aria-labelledby="contact-heading" class="mt-28 scroll-mt-28">
      <div class="border-line bg-surface relative overflow-hidden rounded-[2.5rem] border p-6 sm:p-12">
        <Corners inset="1.25rem" />
        <div class="grid gap-12 lg:grid-cols-[1fr_1.4fr]">
          <div v-reveal>
            <p class="neat-eyebrow">Contact</p>
            <h2 id="contact-heading" class="font-display mt-3 text-4xl font-extrabold tracking-[-0.03em] sm:text-5xl">
              Let’s build something
            </h2>
            <p class="mt-5 max-w-[40ch] text-lg leading-8 text-muted">
              Tell me what you’re working on. A product that needs a steady pair of hands, a question about one of my
              tools, or just a hello: it all lands in the same inbox.
            </p>
            <ul v-if="socials.length" role="list" class="mt-8 grid gap-2">
              <li v-for="social in socials" :key="social.url">
                <a :href="social.url" rel="me noopener" target="_blank" class="neat-link font-medium text-accent"
                  >{{ social.label }} ↗</a
                >
              </li>
            </ul>
          </div>
          <div v-reveal="120"><ContactForm :form="contact" /></div>
        </div>
      </div>
    </section>
  </div>
</template>
