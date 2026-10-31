<script setup lang="ts">
import { Link } from '@inertiajs/vue3'
import { RichText } from '@nibble'
import type { PhotographyPhoto } from '@site/types'

defineProps<{ page: PhotographyPhoto }>()
</script>

<template>
  <article>
    <nav aria-label="Breadcrumb" class="animate-rise text-faint mb-8 font-mono text-xs">
      <Link href="/photography" class="neat-link hover:text-accent">Photography</Link>
      <span class="mx-2" aria-hidden="true">/</span>
      <span aria-current="page" class="text-muted">{{ page.title }}</span>
    </nav>
    <div
      class="animate-rise border-line bg-midnight overflow-hidden rounded-[2rem] border [animation-delay:80ms] [&_img]:mx-auto [&_img]:max-h-[80vh] [&_img]:w-auto [&_p]:m-0"
    >
      <RichText :value="page.body" />
    </div>
    <div class="mt-10 grid gap-8 lg:grid-cols-[1fr_20rem]">
      <header>
        <h1 class="font-display text-4xl font-extrabold tracking-[-0.03em] sm:text-5xl">{{ page.title }}</h1>
        <p v-if="page.description" class="mt-4 max-w-[60ch] text-lg leading-8 text-muted">{{ page.description }}</p>
      </header>
      <dl class="neat-card grid content-start gap-4 p-6">
        <div
          v-for="[label, value] in [
            ['Where', page.location],
            ['When', page.taken],
            ['Camera', page.camera],
          ]"
          :key="label"
        >
          <template v-if="value">
            <dt class="text-faint font-mono text-xs tracking-wider uppercase">{{ label }}</dt>
            <dd class="mt-1 font-medium">{{ value }}</dd>
          </template>
        </div>
        <a
          v-if="page.unsplash"
          :href="page.unsplash"
          target="_blank"
          rel="noopener"
          class="neat-button mt-2 justify-center"
          >View on Unsplash ↗</a
        >
      </dl>
    </div>
  </article>
</template>
