<script setup lang="ts">
import { Link } from '@inertiajs/vue3'
import { Image } from '@nibble'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import type { PostsPost, ViewProps } from '@site/types'
import PostCard from '../../components/PostCard.vue'
import Prose from '../../components/Prose.vue'
import { isoDate, useFormatDate } from '../../lib/format'
import { vReveal } from '../../lib/motion'
import ArrowIcon from '../../components/ArrowIcon.vue'

const props = defineProps<ViewProps['posts/show'] & { page: PostsPost }>()
const formatDate = useFormatDate()

const readingTime = computed(() => {
  const words = (props.page.body ?? '')
    .replace(/<[^>]+>/g, ' ')
    .split(/\s+/)
    .filter(Boolean).length
  return Math.max(1, Math.round(words / 230))
})

// A thin bar along the top that fills as the article is read.
const progress = ref(0)
function measure() {
  const article = document.getElementById('article-body')
  if (!article) return
  const box = article.getBoundingClientRect()
  progress.value = Math.min(1, Math.max(0, -box.top / Math.max(1, box.height - window.innerHeight * 0.6)))
}
onMounted(() => {
  measure()
  window.addEventListener('scroll', measure, { passive: true })
})
onBeforeUnmount(() => window.removeEventListener('scroll', measure))
</script>

<template>
  <article>
    <div
      class="from-mint via-teal to-sea fixed inset-x-0 top-0 z-[55] h-0.5 origin-left bg-gradient-to-r"
      :style="{ transform: `scaleX(${progress})` }"
      aria-hidden="true"
    />
    <header class="mx-auto max-w-4xl text-center">
      <div class="animate-rise flex flex-wrap items-center justify-center gap-2">
        <Link href="/blog" class="neat-eyebrow neat-link group inline-flex items-center gap-1.5"
          ><ArrowIcon
            direction="left"
            class="transition-transform duration-300 group-hover:-translate-x-1"
          />Writing</Link
        >
        <Link
          v-for="topic in page.topics"
          :key="topic.id"
          :href="topic.uri ?? '#'"
          class="rounded-full bg-accent/10 px-3 py-1 font-mono text-xs text-accent"
          >{{ topic.title }}</Link
        >
      </div>
      <h1
        class="animate-rise font-display mt-6 text-4xl font-extrabold tracking-[-0.04em] text-balance [animation-delay:80ms] sm:text-6xl"
      >
        {{ page.title }}
      </h1>
      <p
        v-if="page.excerpt"
        class="animate-rise mx-auto mt-6 max-w-[56ch] text-lg leading-8 text-balance text-muted [animation-delay:160ms] sm:text-xl"
      >
        {{ page.excerpt }}
      </p>
      <p class="animate-rise text-faint mt-6 font-mono text-xs [animation-delay:200ms]">
        <time :datetime="isoDate(page.published_at)">{{
          formatDate(page.published_at, { month: 'long', day: 'numeric', year: 'numeric' })
        }}</time>
        · {{ readingTime }} min read
      </p>
    </header>
    <div class="animate-rise mx-auto mt-12 max-w-5xl [animation-delay:260ms]">
      <Image
        v-if="page.featured_image"
        :image="page.featured_image"
        loading="eager"
        sizes="(min-width: 64rem) 64rem, 100vw"
        class="aspect-[2/1] w-full rounded-[1.75rem] object-cover"
      />
    </div>
    <div id="article-body" class="mx-auto prose prose-lg mt-14 max-w-[68ch]">
      <Prose :value="page.body" />
    </div>
    <section v-if="related.length" aria-labelledby="related-heading" class="mt-28">
      <h2 id="related-heading" v-reveal class="font-display mb-8 text-3xl font-extrabold tracking-tight">
        Keep reading
      </h2>
      <div class="grid gap-5 md:grid-cols-3">
        <div v-for="(post, index) in related" :key="post.id" v-reveal="index * 100"><PostCard :post="post" /></div>
      </div>
    </section>
  </article>
</template>
