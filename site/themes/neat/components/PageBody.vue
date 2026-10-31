<script setup lang="ts">
import { Blocks } from '@nibble'
import type { RichTextValue, SetBlock } from '@nibble'
import { vReveal } from '../lib/motion'
import Prose from './Prose.vue'

defineProps<{ content?: RichTextValue | null; blocks?: SetBlock[] | null; large?: boolean }>()
</script>

<template>
  <div v-reveal class="prose max-w-[68ch]" :class="{ 'prose-lg': large }">
    <Prose v-if="content" :value="content" />
    <Blocks :blocks="blocks" />
  </div>
</template>
