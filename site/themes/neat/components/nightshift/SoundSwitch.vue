<script setup lang="ts">
// The sound switch: a brushed-metal plate lying on the desk with an engraved title, a recessed slot and a domed knob
// that slides up for ON and down for OFF, and a little lamp that glows while the sound is on. Click it, press Space
// or Enter, or drag the knob.
const on = defineModel<boolean>({ required: true })

let startY = 0
let dragged = false

function down(event: PointerEvent) {
  startY = event.clientY
  dragged = false
}

function up(event: PointerEvent) {
  const dy = event.clientY - startY
  if (Math.abs(dy) < 8) return
  dragged = true
  on.value = dy < 0
}

function click() {
  if (dragged) {
    dragged = false
    return
  }
  on.value = !on.value
}
</script>

<template>
  <button
    type="button"
    class="ns-sound"
    role="switch"
    :aria-checked="on"
    aria-label="Sound"
    @pointerdown="down"
    @pointerup="up"
    @click="click"
  >
    <span class="ns-sound-title" aria-hidden="true">Sound</span>
    <span class="ns-sound-mark is-on" aria-hidden="true">On</span>
    <span class="ns-sound-slot" aria-hidden="true"><span class="ns-sound-knob" /></span>
    <span class="ns-sound-mark is-off" aria-hidden="true">Off</span>
    <span class="ns-sound-lamp" aria-hidden="true" />
  </button>
</template>
