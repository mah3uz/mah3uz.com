<script setup lang="ts">
import { Link } from '@inertiajs/vue3'
import { Pagination, type PaginationMeta } from '@nibble'
import ArrowIcon from './ArrowIcon.vue'

withDefaults(defineProps<{ meta: PaginationMeta; label?: string; previousLabel?: string; nextLabel?: string }>(), {
  label: 'Pages',
  previousLabel: 'Newer',
  nextLabel: 'Older',
})
</script>

<template>
  <Pagination :meta="meta" :label="label">
    <template #default="{ href, current, pages }">
      <div class="mt-16 flex flex-wrap items-center justify-between gap-6">
        <Link v-if="current > 1" :href="href(current - 1)" rel="prev" class="neat-button-ghost"
          ><ArrowIcon direction="left" /> {{ previousLabel }}</Link
        >
        <span v-else />
        <ol class="flex gap-1" role="list">
          <li v-for="number in pages" :key="number">
            <Link
              :href="href(number)"
              class="grid size-10 place-items-center rounded-full font-mono text-sm transition-colors"
              :class="number === current ? 'bg-ink text-canvas' : 'text-muted hover:bg-accent/10'"
              :aria-current="number === current ? 'page' : undefined"
              >{{ number }}</Link
            >
          </li>
        </ol>
        <Link v-if="current < meta.last_page" :href="href(current + 1)" rel="next" class="neat-button-ghost"
          >{{ nextLabel }} <ArrowIcon
        /></Link>
        <span v-else />
      </div>
    </template>
  </Pagination>
</template>
