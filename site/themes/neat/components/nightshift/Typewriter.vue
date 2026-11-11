<script setup lang="ts">
// The machine, from the reference's #machine: the mechanism drawn over the deck, the strip with the ribbon switch,
// the name plate, the strike counter and New sheet, and the key bank. It sits at the bottom centre of the desk with
// the carriage and paper rising above it.
import { computed } from 'vue'
import Basket from './Basket.vue'
import Keys from './Keys.vue'

const props = defineProps<{
  pressed: string
  jamming: string
  char: string
  tally: number
  strikes: number
  bells: number
  jams: number
  shift: boolean
  lock: boolean
}>()
const emit = defineEmits<{ key: [key: string]; clear: [] }>()
const red = defineModel<boolean>('red', { required: true })

const digits = computed(() =>
  String(props.tally % 100000)
    .padStart(5, '0')
    .split('')
    .map(Number),
)
</script>

<template>
  <div class="ns-typewriter" :class="{ 'is-jam': jams % 2 === 1 }">
    <section class="ns-mbody" aria-label="The typewriter">
      <Basket :strikes="strikes" :char="char" :bells="bells" :spin="strikes * 5" />
      <div class="ns-deck" />
      <div class="ns-strip">
        <button
          type="button"
          class="ns-rib"
          role="switch"
          :aria-checked="red"
          aria-label="Red ribbon"
          @click="red = !red"
        >
          <span class="ns-rib-txt">Ribbon</span><span class="ns-rib-dot is-k" /><span class="ns-rib-slot"
            ><span class="ns-rib-nub" /></span
          ><span class="ns-rib-dot is-r" />
        </button>
        <div class="ns-plate" aria-hidden="true">mah3uz · tty1</div>
        <div class="ns-count" aria-hidden="true">
          <span>Strikes</span
          ><span class="ns-win"
            ><span v-for="(d, i) in digits" :key="i" class="ns-dg"
              ><span :style="{ transform: `translateY(${-d * 13}px)` }"
                ><i v-for="n in 10" :key="n">{{ n - 1 }}</i></span
              ></span
            ></span
          >
        </div>
        <button type="button" class="ns-newsheet" @click="emit('clear')">
          <svg viewBox="0 0 11 13" aria-hidden="true">
            <path d="M1 .8h6l3 3v8.4H1z" fill="var(--ns-paper)" />
            <path d="M7 .8v3h3" fill="none" stroke="var(--ns-chrome-lo)" stroke-width=".8" />
          </svg>
          New sheet
        </button>
      </div>
      <Keys :pressed="pressed" :jamming="jamming" :shift="shift" :lock="lock" @key="emit('key', $event)" />
    </section>
  </div>
</template>
