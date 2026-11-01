<script setup lang="ts">
import { useGlobals } from '@nibble'
import { computed } from 'vue'
import type { PagesPage, SiteGlobals, ViewProps } from '@site/types'
import BrandMark from '../components/BrandMark.vue'
import ContactForm from '../components/ContactForm.vue'
import Corners from '../components/Corners.vue'
import ArtBanner from '../components/ArtBanner.vue'
import PageBody from '../components/PageBody.vue'
import { vReveal, vSpotlight, vTilt } from '../lib/motion'
import { linkTag, socialLinks } from '../lib/links'
import { isClient, onlyProjects } from '../lib/projects'

const props = defineProps<ViewProps['about'] & { page: PagesPage }>()
const site = useGlobals<SiteGlobals>('site')

const STARTED = 2009
const years = new Date().getUTCFullYear() - STARTED
const all = computed(() => onlyProjects(props.projects))
const socials = computed(() => socialLinks(site.value?.social_links))
const products = computed(() => all.value.filter((project) => !isClient(project)))
// Grid rows arrive loosely typed; read each into the shape the timeline draws.
const milestones = computed(() =>
  (props.page.milestones ?? []).map((row, index) => ({
    id: String(row.id ?? index),
    year: String(row.year ?? ''),
    tag: row.tag ? String(row.tag) : '',
    title: String(row.title ?? ''),
    text: String(row.text ?? ''),
    url: row.url ? String(row.url) : '',
    logo: row.logo ? String(row.logo) : '',
  })),
)
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
            <p class="text-mist mt-1">Linux systems &amp; software engineer · since {{ STARTED }}</p>
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
                <dt class="text-mist/70 font-mono text-[0.65rem] tracking-wider uppercase">On Linux</dt>
                <dd class="font-display text-mint mt-1 text-2xl font-extrabold">Always</dd>
              </div>
            </dl>
          </div>
        </div>
      </div>
    </section>

    <div class="mt-24 grid gap-14 lg:grid-cols-[1fr_22rem]">
      <PageBody :content="page.content" :blocks="page.blocks" large />
      <ArtBanner
        v-if="page.art"
        v-reveal
        :src="page.art"
        class="aspect-[4/5] self-start lg:sticky lg:top-28 [&_img]:object-[30%_50%]"
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

    <section v-if="milestones.length" aria-labelledby="timeline" class="mt-28">
      <div v-reveal class="mb-14 max-w-2xl">
        <p class="neat-eyebrow">Timeline</p>
        <h2 id="timeline" class="font-display mt-3 text-4xl font-extrabold tracking-[-0.03em] sm:text-5xl">
          {{ years }} years, one thread
        </h2>
        <p class="mt-4 text-lg leading-8 text-muted">
          The milestones I can point to. Most client work is private, so the public record starts later than the career
          does; where there is something to see, the milestone links to it.
        </p>
      </div>
      <ol role="list" class="neat-timeline relative grid gap-10 lg:gap-6">
        <li
          v-for="(milestone, index) in milestones"
          :key="milestone.id"
          v-reveal="(index % 3) * 60"
          class="neat-milestone relative grid gap-3 pl-12 lg:grid-cols-2 lg:gap-16 lg:pl-0"
          :class="index % 2 ? 'lg:[&>article]:col-start-2' : 'lg:[&>article]:col-start-1 lg:[&>article]:text-right'"
        >
          <span class="neat-timeline-dot" aria-hidden="true" />
          <!-- The card's logo sits on its outer edge: left in the right-hand column, right in the left-hand one. -->
          <article
            class="neat-card flex flex-col items-start gap-4 p-6 sm:flex-row sm:gap-5"
            :class="index % 2 ? '' : 'lg:flex-row-reverse lg:items-start lg:[&_.neat-milestone-meta]:justify-end'"
          >
            <img
              v-if="milestone.logo"
              :src="milestone.logo"
              alt=""
              width="56"
              height="56"
              loading="lazy"
              class="size-12 shrink-0 rounded-[28%] object-contain drop-shadow-[0_8px_14px_rgba(4,48,64,0.22)] sm:size-14"
            />
            <div class="min-w-0 flex-1">
              <p class="neat-milestone-meta flex flex-wrap items-center gap-3">
                <span class="font-display text-2xl font-extrabold tracking-tight text-accent">{{
                  milestone.year
                }}</span>
                <span
                  v-if="milestone.tag"
                  class="border-line-strong rounded-full border px-2.5 py-0.5 font-mono text-[0.65rem] tracking-wider text-muted uppercase"
                  >{{ milestone.tag }}</span
                >
              </p>
              <h3 class="font-display mt-3 text-xl font-bold tracking-tight">
                <component
                  :is="milestone.url ? linkTag(milestone.url) : 'span'"
                  :href="milestone.url || undefined"
                  :target="milestone.url && !milestone.url.startsWith('/') ? '_blank' : undefined"
                  :rel="milestone.url && !milestone.url.startsWith('/') ? 'noopener' : undefined"
                  :class="{ 'neat-link': milestone.url }"
                  >{{ milestone.title }}</component
                >
              </h3>
              <p class="mt-2 leading-7 text-muted">{{ milestone.text }}</p>
            </div>
          </article>
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

<style>
/* The timeline's rail: on the left on small screens, down the middle on large ones. */
.neat-timeline::before {
  content: '';
  position: absolute;
  top: 0.5rem;
  bottom: 0.5rem;
  left: 0.75rem;
  width: 2px;
  border-radius: 2px;
  background: linear-gradient(
    180deg,
    transparent,
    var(--neat-accent) 6%,
    var(--neat-line-strong) 50%,
    var(--neat-accent) 94%,
    transparent
  );
}
.neat-timeline-dot {
  position: absolute;
  top: 1.85rem;
  left: 0.75rem;
  width: 1.1rem;
  height: 1.1rem;
  translate: -50% 0;
  border-radius: 999px;
  background: var(--neat-canvas);
  border: 3px solid var(--neat-accent);
  box-shadow: 0 0 0 6px color-mix(in oklab, var(--neat-accent) 14%, transparent);
}
@media (min-width: 64rem) {
  .neat-timeline::before,
  .neat-timeline-dot {
    left: 50%;
  }
  .neat-timeline::before {
    translate: -50% 0;
  }
}
</style>
