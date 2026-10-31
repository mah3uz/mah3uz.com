<script setup lang="ts">
import { computed } from 'vue'
import { STATUS_COPY, type Status } from '../lib/projects'

const props = defineProps<{ status: Status; label?: string }>()
const copy = computed(() => STATUS_COPY[props.status] ?? STATUS_COPY.building)
</script>

<template>
  <span
    class="border-line-strong bg-surface inline-flex items-center gap-2 rounded-full border px-3 py-1 font-mono text-[0.7rem] tracking-wider uppercase"
    :title="copy.note"
  >
    <span
      class="size-1.5 rounded-full"
      :class="{
        'animate-pulse-ring bg-accent': status === 'building',
        'bg-teal': status === 'shipped',
        'bg-amber-400': status === 'experiment',
        'bg-faint': status === 'archived',
      }"
    />
    {{ label ?? copy.label }}
  </span>
</template>
