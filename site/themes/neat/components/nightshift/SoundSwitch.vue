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

<style>
.ns-sound {
  position: absolute;
  z-index: 6;
  right: 1.75rem;
  top: calc(var(--ns-header) + 1rem);
  width: 4.4rem;
  height: 6.9rem;
  padding: 0;
  border: 0;
  border-radius: 0.6rem;
  cursor: pointer;
  touch-action: none;
  background:
    repeating-linear-gradient(90deg, var(--ns-knurl-hi) 0 1px, transparent 1px 3px),
    linear-gradient(160deg, var(--ns-chrome-hi), var(--ns-chrome-mid) 45%, var(--ns-chrome-lo));
  box-shadow:
    inset 0 0 0 2px var(--ns-chrome-hi),
    inset 0 0 0 3px var(--ns-chrome-lo),
    inset 0 -6px 10px var(--ns-shade),
    0 0.5rem 0.9rem var(--ns-drop),
    0 0.1rem 0.15rem var(--ns-drop);
}
.ns-sound-title,
.ns-sound-mark {
  position: absolute;
  left: 0;
  right: 0;
  text-align: center;
  font-family: var(--font-body), sans-serif;
  font-weight: 800;
  text-transform: uppercase;
  color: var(--ns-engrave-deep);
  text-shadow: 0 1px 0 var(--ns-chrome-hi);
}
.ns-sound-title {
  top: 0.6rem;
  font-size: 9px;
  letter-spacing: 0.3em;
  text-indent: 0.3em;
}
.ns-sound-mark {
  font-size: 7px;
  letter-spacing: 0.16em;
  text-indent: 0.16em;
}
.ns-sound-mark.is-on {
  top: 1.55rem;
}
.ns-sound-mark.is-off {
  bottom: 0.55rem;
}
/* The recessed slot and the domed knob riding in it. */
.ns-sound-slot {
  position: absolute;
  left: 50%;
  top: 2.4rem;
  width: 0.95rem;
  height: 2.9rem;
  margin-left: -0.475rem;
  border-radius: 999px;
  background: linear-gradient(180deg, var(--ns-well), var(--ns-well-2));
  box-shadow:
    inset 0 2px 4px var(--ns-drop),
    0 1px 0 var(--ns-chrome-hi);
}
.ns-sound-knob {
  position: absolute;
  left: 50%;
  top: 0;
  width: 1.55rem;
  height: 1.55rem;
  margin-left: -0.775rem;
  border-radius: 50%;
  translate: 0 1.35rem;
  background: radial-gradient(circle at 36% 30%, var(--ns-chrome-hi), var(--ns-chrome-mid) 45%, var(--ns-chrome-lo));
  box-shadow:
    0 3px 4px var(--ns-drop),
    inset 0 -2px 3px var(--ns-shade);
  transition: translate 0.18s cubic-bezier(0.3, 1.5, 0.45, 1);
}
.ns-sound[aria-checked='true'] .ns-sound-knob {
  translate: 0 0;
}
.ns-sound-lamp {
  position: absolute;
  right: 0.7rem;
  bottom: 0.6rem;
  width: 0.38rem;
  height: 0.38rem;
  border-radius: 50%;
  background: var(--ns-led-off);
  box-shadow: inset 0 1px 1px var(--ns-drop);
  transition:
    background 0.2s ease,
    box-shadow 0.2s ease;
}
.ns-sound[aria-checked='true'] .ns-sound-lamp {
  background: var(--ns-led-on);
  box-shadow: 0 0 6px 1px var(--ns-pointer-glow);
}
.ns-sound:focus-visible {
  outline: 2px solid var(--ns-focus);
  outline-offset: 3px;
}
@media (prefers-reduced-motion: reduce) {
  .ns-sound-knob {
    transition-duration: 1ms;
  }
}
</style>
