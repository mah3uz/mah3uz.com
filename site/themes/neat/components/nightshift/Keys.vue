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

<style>
.ns-keys {
  --k: 2.45rem;
  --g: 0.42rem;
  width: fit-content;
  max-width: 100%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--g);
  padding: calc(var(--k) * 0.34) calc(var(--k) * 0.75) calc(var(--k) * 0.42);
  border-radius: 20px 20px 0 0;
  background: linear-gradient(180deg, var(--ns-well), var(--ns-well-2) 60%, var(--ns-well));
  box-shadow:
    inset 0 7px 14px var(--ns-drop),
    inset 0 0 0 1px var(--ns-shade),
    0 -1px 0 var(--ns-enamel-edge);
  user-select: none;
}
.ns-row {
  position: relative;
  display: flex;
  gap: var(--g);
}
.ns-row.r1 {
  left: calc(var(--k) * -0.4);
}
.ns-row.r2 {
  left: calc(var(--k) * -0.48);
}
.ns-row.r3 {
  left: calc(var(--k) * 0.35);
}
.ns-row.r4 {
  left: calc(var(--k) * 0.27);
}
.ns-row.r5 {
  align-self: stretch;
}
.ns-key {
  position: relative;
  flex: none;
  display: grid;
  place-items: center;
  width: var(--k);
  height: var(--k);
  border: calc(var(--k) * 0.085) solid transparent;
  border-radius: 50%;
  cursor: pointer;
  color: var(--ns-key-ink);
  font:
    700 calc(var(--k) * 0.42) / 1 var(--font-mono),
    monospace;
  background:
    radial-gradient(circle at 50% 120%, var(--ns-key-top-lo), var(--ns-key-top) 55%, var(--ns-key-deep)) padding-box,
    conic-gradient(
        from -50deg,
        var(--ns-chrome-hi),
        var(--ns-chrome-mid) 11%,
        var(--ns-chrome-hi) 24%,
        var(--ns-chrome-lo) 40%,
        var(--ns-chrome-hi) 54%,
        var(--ns-chrome-lo) 69%,
        var(--ns-chrome-hi) 84%,
        var(--ns-chrome-mid) 93%,
        var(--ns-chrome-hi)
      )
      border-box;
  box-shadow:
    0 calc(var(--k) * 0.1) 0 var(--ns-key-skirt),
    0 calc(var(--k) * 0.22) calc(var(--k) * 0.22) var(--ns-drop);
  transition:
    transform 150ms cubic-bezier(0.2, 1.7, 0.4, 1),
    box-shadow 150ms;
}
.ns-key::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
  background:
    radial-gradient(ellipse 58% 40% at 36% 22%, var(--ns-gloss), transparent 70%),
    radial-gradient(ellipse 60% 30% at 60% 96%, var(--ns-sheen), transparent 70%);
}
.ns-key.is-down {
  transform: translateY(calc(var(--k) * 0.1));
  box-shadow:
    0 0 0 var(--ns-key-skirt),
    0 2px 3px var(--ns-drop);
  transition-duration: 30ms;
}
.ns-key.is-jam {
  transform: translateY(calc(var(--k) * 0.045));
  transition-duration: 30ms;
}
.ns-two {
  display: grid;
  gap: calc(var(--k) * 0.02);
  font-size: calc(var(--k) * 0.3);
  line-height: 1;
  text-align: center;
}
.ns-two i {
  font-style: normal;
  opacity: 0.72;
  font-size: 0.82em;
}
.ns-pill {
  width: calc(var(--k) * 1.42);
  border-radius: 999px;
  font:
    700 max(10px, calc(var(--k) * 0.24)) / 1 var(--font-body),
    sans-serif;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.ns-space {
  flex: 1;
  width: auto;
  border-radius: 999px;
}
@media (max-width: 860px) {
  .ns-keys {
    --k: min(2.3rem, calc((100vw - 3rem) / 13.4));
    --g: calc(var(--k) * 0.13);
    padding-inline: calc(var(--k) * 0.45);
  }
  .ns-pill {
    width: calc(var(--k) * 1.55);
    font-size: 9px;
    letter-spacing: 0.04em;
  }
  .ns-pill.is-extra {
    display: none;
  }
}
@media (prefers-reduced-motion: reduce) {
  .ns-key {
    transition-duration: 1ms;
  }
}
</style>
