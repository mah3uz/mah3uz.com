<script setup lang="ts">
import { Link } from '@inertiajs/vue3'
import { computed } from 'vue'
import { onSite } from '../../lib/links'
import Corners from '../../components/Corners.vue'

const props = defineProps<{
  heading: string
  text?: string | null
  button_label?: string | null
  link?: { type: string; url: string; id?: number; title?: string } | null
}>()

const internal = computed(() => !!props.link && onSite(props.link.url))
</script>

<template>
  <aside class="not-prose bg-midnight relative my-14 overflow-hidden rounded-[2rem] p-8 text-white sm:p-10">
    <Corners inset="1rem" size="1.25rem" />
    <div
      class="absolute -top-20 -right-20 size-64 rounded-full bg-[radial-gradient(circle,#21bdb080,transparent_65%)]"
      aria-hidden="true"
    />
    <h2 class="font-display relative text-3xl font-extrabold tracking-tight">{{ heading }}</h2>
    <p v-if="text" class="text-mist relative mt-3 max-w-[48ch] text-lg leading-8">{{ text }}</p>
    <component
      :is="internal ? Link : 'a'"
      v-if="button_label && link"
      :href="link.url"
      class="bg-mint text-abyss relative mt-6 inline-flex min-h-12 items-center gap-3 rounded-full px-6 py-3 font-semibold"
    >
      {{ button_label }} <span aria-hidden="true">→</span>
    </component>
  </aside>
</template>
