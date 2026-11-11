<script setup lang="ts">
// The overhead lamp: a conical metal shade seen from above at about 35 degrees, hanging in over the top-left corner
// on a chrome arm and cropped by the edge of the desk, its mouth turned down toward the typewriter. Everything is one
// static drawing; the rheostat (--ns-lamp on the scene) only fades the light parts: the lit inside of the lip, the
// bulb glare and the bounce on the shell. The pool it throws on the desk lives in the scene's own light layers.
import Dial from './Dial.vue'

const lamp = defineModel<number>({ required: true })
// The shell in its own frame: the crown at the origin, the axis along x, the mouth 260 along it.
const SHELL = 'M0 -26 L260 -150 A70 150 0 0 1 260 150 L0 26 A11 26 0 0 1 0 -26 Z'
</script>

<template>
  <svg class="ns-lampshade" viewBox="0 0 420 340" aria-hidden="true">
    <defs>
      <linearGradient id="ns-shell" gradientUnits="userSpaceOnUse" x1="0" y1="-150" x2="0" y2="150">
        <stop offset="0" stop-color="var(--ns-shell-edge)" />
        <stop offset="0.38" stop-color="var(--ns-shell-band)" />
        <stop offset="0.6" stop-color="var(--ns-shell-mid)" />
        <stop offset="1" stop-color="var(--ns-shell-edge)" />
      </linearGradient>
      <linearGradient id="ns-lip" gradientUnits="userSpaceOnUse" x1="0" y1="-150" x2="0" y2="150">
        <stop offset="0" stop-color="var(--ns-chrome-hi)" />
        <stop offset="0.55" stop-color="var(--ns-chrome-mid)" />
        <stop offset="1" stop-color="var(--ns-chrome-lo)" />
      </linearGradient>
      <linearGradient id="ns-tube" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="var(--ns-chrome-lo)" />
        <stop offset="0.4" stop-color="var(--ns-chrome-hi)" />
        <stop offset="1" stop-color="var(--ns-chrome-lo)" />
      </linearGradient>
      <linearGradient id="ns-inside" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="var(--ns-bulb)" />
        <stop offset="1" stop-color="var(--ns-bulb-2)" />
      </linearGradient>
      <radialGradient id="ns-glare">
        <stop offset="0" stop-color="var(--ns-bulb)" />
        <stop offset="1" stop-color="var(--ns-bulb)" stop-opacity="0" />
      </radialGradient>
      <filter id="ns-soft-3" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3" /></filter>
      <filter id="ns-soft-2" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2" /></filter>
      <filter id="ns-soft-12" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="12" /></filter>
    </defs>
    <g transform="translate(8 26) rotate(28)">
      <!-- its shadow on the desk, thrown away from the pool -->
      <path :d="SHELL" fill="var(--ns-room)" opacity="0.25" filter="url(#ns-soft-12)" transform="translate(-18 -26)" />
      <!-- the arm and the socket at the crown -->
      <path d="M-36 0 L-420 0" stroke="url(#ns-tube)" stroke-width="9" />
      <path d="M-36 -2.5 L-420 -2.5" stroke="var(--ns-chrome-hi)" stroke-width="1" opacity="0.7" />
      <rect x="-28" y="-16" width="30" height="32" rx="3" fill="url(#ns-tube)" />
      <rect
        x="-37"
        y="-11"
        width="9"
        height="22"
        rx="1.5"
        fill="var(--ns-chrome-mid)"
        stroke="var(--ns-chrome-lo)"
        stroke-width="0.8"
      />
      <path d="M-37 -10 H-28" stroke="var(--ns-chrome-hi)" stroke-width="1" />
      <!-- the shell -->
      <path :d="SHELL" fill="url(#ns-shell)" />
      <path
        d="M12 -6 Q140 -26 250 -34"
        fill="none"
        stroke="#ffffff"
        stroke-opacity="0.35"
        stroke-width="5"
        stroke-linecap="round"
        filter="url(#ns-soft-3)"
      />
      <path
        class="ns-lamp-lit"
        d="M143 90 L256 145"
        stroke="var(--ns-bounce)"
        stroke-opacity="0.25"
        stroke-width="3"
        stroke-linecap="round"
        filter="url(#ns-soft-2)"
      />
      <!-- the lit inside of the lip and the bulb's glare -->
      <path
        class="ns-lamp-lit"
        d="M320.6 75 A70 150 0 0 1 260 150 L253 137 A61 137 0 0 0 305.8 68.5 Z"
        fill="url(#ns-inside)"
      />
      <ellipse class="ns-lamp-lit" cx="296" cy="112" rx="16" ry="9" fill="url(#ns-glare)" filter="url(#ns-soft-3)" />
      <!-- the rolled lip -->
      <path
        d="M260 -146 A66 146 0 0 1 260 146"
        fill="none"
        stroke="var(--ns-room)"
        stroke-opacity="0.6"
        stroke-width="1"
      />
      <path d="M260 -150 A70 150 0 0 1 260 150" fill="none" stroke="url(#ns-lip)" stroke-width="2.5" />
    </g>
  </svg>
  <svg class="ns-cord" viewBox="0 0 260 520" aria-hidden="true">
    <g fill="none" stroke-linecap="round">
      <path
        d="M22 -60 C 46 60, 160 110, 128 214 M34 312 C 18 320, 6 342, -20 356"
        stroke="var(--ns-drop)"
        stroke-width="6"
        transform="translate(4 6)"
        opacity="0.5"
      />
      <path
        d="M22 -60 C 46 60, 160 110, 128 214 M34 312 C 18 320, 6 342, -20 356"
        stroke="var(--ns-cord)"
        stroke-width="5"
      />
      <path
        d="M22 -60 C 46 60, 160 110, 128 214 M34 312 C 18 320, 6 342, -20 356"
        stroke="var(--ns-cord-hi)"
        stroke-width="1.4"
        stroke-dasharray="2 3"
      />
    </g>
  </svg>
  <div class="ns-rheostat">
    <span class="ns-rheostat-boss is-top" aria-hidden="true" />
    <span class="ns-rheostat-boss is-left" aria-hidden="true" />
    <Dial v-model="lamp" label="Lamp" />
  </div>
</template>

<style>
.ns-lampshade {
  position: absolute;
  z-index: 6;
  left: 0;
  top: 0;
  width: 420px;
  height: 340px;
  overflow: visible;
  pointer-events: none;
}
.ns-lamp-lit {
  opacity: var(--ns-lamp);
  transition: opacity 0.3s ease;
}
.ns-cord {
  position: absolute;
  z-index: 5;
  left: 0;
  top: var(--ns-header);
  width: 260px;
  height: 520px;
  overflow: visible;
  pointer-events: none;
}
/* The rheostat: a small dark enamel box lying on the desk, the lamp's cord entering at the top and leaving at the
   side, with the dial set into its lid. */
.ns-rheostat {
  --ns-dial: 8.75rem;
  position: absolute;
  z-index: 6;
  left: 40px;
  top: calc(var(--ns-header) + 224px);
  display: grid;
  place-items: center;
  width: 176px;
  height: 176px;
  border-radius: 1.4rem;
  background:
    radial-gradient(ellipse 70% 35% at 35% 0%, var(--ns-sheen), transparent 70%),
    linear-gradient(160deg, var(--ns-bakelite-hi), var(--ns-bakelite) 55%, var(--ns-bakelite-lo));
  box-shadow:
    inset 0 1px 0 var(--ns-enamel-edge),
    inset 0 -8px 14px var(--ns-shade),
    0.5rem 0.9rem 1.4rem var(--ns-drop);
}
.ns-rheostat-boss {
  position: absolute;
  background: linear-gradient(90deg, var(--ns-bakelite-lo), var(--ns-bakelite-hi), var(--ns-bakelite-lo));
  box-shadow: 0 2px 3px var(--ns-drop);
}
.ns-rheostat-boss.is-top {
  left: 50%;
  top: -10px;
  width: 16px;
  height: 14px;
  margin-left: -8px;
  border-radius: 4px 4px 2px 2px;
}
.ns-rheostat-boss.is-left {
  left: -10px;
  top: 50%;
  width: 14px;
  height: 16px;
  margin-top: -8px;
  border-radius: 4px 2px 2px 4px;
  background: linear-gradient(180deg, var(--ns-bakelite-lo), var(--ns-bakelite-hi), var(--ns-bakelite-lo));
}
@media (max-width: 860px) {
  .ns-lampshade,
  .ns-cord,
  .ns-rheostat {
    display: none;
  }
}
</style>
