<script setup lang="ts">
// A terminal that types its way through the projects, one at a time. The server renders the first one in full, so
// the hero is complete before any script runs; the typing starts once the page is interactive.
import { Link } from '@inertiajs/vue3'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { hostOf, statusOf, STATUS_COPY, type ProjectLike } from '../lib/projects'
import Corners from './Corners.vue'
import ProjectTile from './ProjectTile.vue'

const props = defineProps<{ projects: ProjectLike[] }>()

const scenes = computed(() =>
  props.projects.map((project) => ({
    project,
    command: `open ${project.website ? hostOf(project.website) : project.slug}`,
    status: STATUS_COPY[statusOf(project)].label.toLowerCase(),
  })),
)

const index = ref(0)
const typed = ref<string | null>(null)
const showOutput = ref(true)
const scene = computed(() => scenes.value[index.value])
const shownCommand = computed(() => typed.value ?? scene.value?.command ?? '')

let timer: ReturnType<typeof setTimeout> | undefined
const wait = (ms: number) => new Promise<void>((resolve) => (timer = setTimeout(resolve, ms)))
let alive = true

async function play() {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches || scenes.value.length < 2) return
  await wait(3200)
  while (alive) {
    index.value = (index.value + 1) % scenes.value.length
    showOutput.value = false
    typed.value = ''
    const command = scenes.value[index.value].command
    for (let i = 1; i <= command.length && alive; i++) {
      typed.value = command.slice(0, i)
      await wait(38 + Math.random() * 50)
    }
    await wait(280)
    typed.value = null
    showOutput.value = true
    await wait(3600)
  }
}

onMounted(play)
onBeforeUnmount(() => {
  alive = false
  clearTimeout(timer)
})
</script>

<template>
  <div class="relative p-5 sm:p-7">
    <Corners size="2rem" />
    <div
      class="relative overflow-hidden rounded-[1.6rem] border border-white/10 bg-[#071419]/95 text-[#E9F7F7] shadow-[0_40px_80px_-30px_rgba(4,48,64,0.7)]"
    >
      <div class="flex items-center gap-2 border-b border-white/10 px-5 py-4">
        <span class="bg-mint size-3 rounded-full" />
        <span class="bg-teal size-3 rounded-full" />
        <span class="bg-sea size-3 rounded-full" />
        <span class="text-mist/70 ml-3 font-mono text-xs">~/workshop — zsh</span>
      </div>
      <div class="min-h-[18.5rem] p-5 font-mono text-[0.82rem] leading-7 sm:p-6 sm:text-sm" aria-live="off">
        <p class="text-mist/60">Last login: today, still building since 2009</p>
        <p class="mt-2">
          <span class="text-mint">mah3uz</span><span class="text-mist/60">@</span
          ><span class="text-teal">workshop</span> <span class="text-mist/60"> ~ </span><span class="text-mint">❯</span>
          {{ shownCommand
          }}<span class="animate-blink bg-mint ml-0.5 inline-block h-4 w-2 translate-y-0.5" aria-hidden="true" />
        </p>
        <Transition
          enter-active-class="transition duration-500 ease-[cubic-bezier(0.16,1,0.3,1)]"
          enter-from-class="translate-y-2 opacity-0"
          leave-active-class="transition duration-150"
          leave-to-class="opacity-0"
          mode="out-in"
        >
          <div v-if="scene && showOutput" :key="index" class="mt-4 grid gap-4">
            <div class="flex items-center gap-4">
              <ProjectTile
                :logo="scene.project.logo"
                :monogram="scene.project.monogram"
                :accent="scene.project.accent"
                size="size-14"
                text="text-xl"
              />
              <div class="min-w-0">
                <p class="font-display text-xl font-extrabold tracking-tight text-white">{{ scene.project.title }}</p>
                <p class="text-mist/70 text-xs">{{ scene.project.kind }} · {{ scene.status }}</p>
              </div>
            </div>
            <p class="font-body text-mist text-[0.95rem] leading-7">{{ scene.project.tagline }}</p>
            <p class="text-mist/70 flex flex-wrap gap-x-3 text-xs">
              <span v-for="item in (scene.project.stack ?? []).slice(0, 4)" :key="item"
                ><span class="text-mint">+</span> {{ item }}</span
              >
            </p>
            <Link :href="scene.project.uri ?? '#'" class="text-mint w-fit underline-offset-4 hover:underline"
              >→ read the case study</Link
            >
          </div>
        </Transition>
      </div>
      <div class="flex gap-1.5 border-t border-white/10 px-5 py-3" aria-hidden="true">
        <span
          v-for="(_, dot) in scenes"
          :key="dot"
          class="h-1 rounded-full transition-all duration-500"
          :class="dot === index ? 'bg-mint w-8' : 'w-3 bg-white/15'"
        />
      </div>
    </div>
  </div>
</template>
