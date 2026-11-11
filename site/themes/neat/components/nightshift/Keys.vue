<script setup lang="ts">
// The key bank, from the reference: round keys in chrome rings, the shifted character above the plain one on the
// non-letter keys, and a row of pills for shift, lock, tab, the space bar, back and return. HERE IS sends the
// machine's answer-back. The bank is hidden from assistive tech; the prompt's input is the accessible way in.
import { ROWS } from './keyboard'

defineProps<{ pressed: string; jamming: string; shift: boolean; lock: boolean }>()
const emit = defineEmits<{ key: [key: string] }>()
const letter = (c: string) => /[a-z]/.test(c)
</script>

<template>
  <div class="ns-keys" aria-hidden="true">
    <div v-for="(row, r) in ROWS" :key="r" class="ns-row" :class="`r${r + 1}`">
      <span
        v-for="key in row"
        :key="key[0]"
        class="ns-key"
        :class="{
          'is-down': pressed === key[0].toUpperCase() || pressed === key[1],
          'is-jam': jamming === key[0].toUpperCase(),
        }"
        @pointerdown.prevent="emit('key', key[0])"
      >
        <template v-if="letter(key[0])">{{ key[1] }}</template>
        <span v-else class="ns-two"
          ><i>{{ key[1] }}</i
          ><span>{{ key[0] }}</span></span
        >
      </span>
    </div>
    <div class="ns-row r5">
      <span class="ns-key ns-pill" :class="{ 'is-down': shift }" @pointerdown.prevent="emit('key', 'shift')"
        >Shift</span
      >
      <span class="ns-key ns-pill is-extra" :class="{ 'is-down': lock }" @pointerdown.prevent="emit('key', 'lock')"
        >Lock</span
      >
      <span class="ns-key ns-pill" :class="{ 'is-down': pressed === 'TAB' }" @pointerdown.prevent="emit('key', 'tab')"
        >Tab</span
      >
      <span
        class="ns-key ns-space"
        :class="{ 'is-down': pressed === ' ', 'is-jam': jamming === ' ' }"
        @pointerdown.prevent="emit('key', ' ')"
      />
      <span class="ns-key ns-pill" :class="{ 'is-down': pressed === 'BACK' }" @pointerdown.prevent="emit('key', 'back')"
        >Back</span
      >
      <span
        class="ns-key ns-pill is-extra"
        :class="{ 'is-down': pressed === 'HERE IS' }"
        @pointerdown.prevent="emit('key', 'hereis')"
        >Here is</span
      >
      <span
        class="ns-key ns-pill"
        :class="{ 'is-down': pressed === 'RETURN' }"
        @pointerdown.prevent="emit('key', 'Enter')"
        >Return</span
      >
    </div>
  </div>
</template>
