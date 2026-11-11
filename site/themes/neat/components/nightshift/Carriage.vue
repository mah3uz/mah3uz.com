<script setup lang="ts">
// The carriage under the paper, from the reference: the platen with its ribbed knobs, the paper bail with two
// rollers and the margin scale (ticks every five columns, numbers every ten, the tab stops in red), and the chrome
// return lever, which swings when the carriage is thrown and can be pulled. NightShift moves all of it with the paper.
import { ref, watch } from 'vue'

const props = defineProps<{ returns: number; columns: number; cell: number; tab: number }>()
const emit = defineEmits<{ return: [] }>()

const lever = ref<HTMLElement | null>(null)
watch(
  () => props.returns,
  () => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
    lever.value?.animate(
      [{ transform: 'rotate(0)' }, { transform: 'rotate(11deg)', offset: 0.3 }, { transform: 'rotate(0)' }],
      {
        duration: 420,
        easing: 'cubic-bezier(.2,1.5,.4,1)',
      },
    )
  },
)
</script>

<template>
  <div class="ns-carriage">
    <div class="ns-bail" aria-hidden="true">
      <span class="ns-roller" style="left: 22%" />
      <span class="ns-roller" style="right: 22%" />
      <span class="ns-scale">
        <template v-for="c in Math.floor(columns / 5) + 1" :key="c">
          <i :style="{ left: `${(c - 1) * 5 * cell}px` }" />
          <b v-if="(c - 1) % 2 === 0" :style="{ left: `${(c - 1) * 5 * cell}px` }">{{ (c - 1) * 5 }}</b>
        </template>
        <u v-for="t in Math.floor((columns - 3) / tab)" :key="`t${t}`" :style="{ left: `${(2 + t * tab) * cell}px` }" />
      </span>
    </div>
    <div class="ns-platen" aria-hidden="true">
      <span class="ns-knob is-left" />
      <span class="ns-knob is-right" />
    </div>
    <span class="ns-lever-mount" aria-hidden="true" />
    <button ref="lever" type="button" class="ns-lever" aria-label="Carriage return lever" @click="emit('return')">
      <svg viewBox="0 0 204 120" aria-hidden="true">
        <path
          d="M198 68 C150 70 118 44 52 34"
          fill="none"
          stroke="var(--ns-chrome-lo)"
          stroke-width="11"
          stroke-linecap="round"
        />
        <path
          d="M198 68 C150 70 118 44 52 34"
          fill="none"
          stroke="var(--ns-chrome-mid)"
          stroke-width="8"
          stroke-linecap="round"
        />
        <path
          d="M196 66 C150 67 118 41 54 31.5"
          fill="none"
          stroke="var(--ns-chrome-hi)"
          stroke-width="2.2"
          stroke-linecap="round"
          opacity=".85"
        />
        <ellipse cx="38" cy="31" rx="30" ry="11.5" transform="rotate(-9 38 31)" fill="var(--ns-chrome-lo)" />
        <ellipse cx="38" cy="30" rx="28" ry="10" transform="rotate(-9 38 30)" fill="var(--ns-chrome-mid)" />
        <ellipse
          cx="34"
          cy="27"
          rx="19"
          ry="4.5"
          transform="rotate(-9 34 27)"
          fill="var(--ns-chrome-hi)"
          opacity=".8"
        />
        <circle cx="197" cy="68" r="8" fill="var(--ns-rubber)" />
        <circle cx="196" cy="67" r="4" fill="var(--ns-chrome-hi)" />
      </svg>
    </button>
  </div>
</template>

<style>
.ns-carriage {
  position: relative;
  z-index: 3;
  margin-top: calc(-2 * var(--ns-line));
}
.ns-bail {
  position: relative;
  width: var(--ns-paper-w);
  height: var(--ns-line);
  margin: 0 auto;
}
.ns-bail::before {
  content: '';
  position: absolute;
  inset: auto -1.9rem 0.3rem;
  height: 13px;
  border-radius: 2px;
  background: linear-gradient(
    180deg,
    var(--ns-chrome-hi) 0,
    var(--ns-chrome-mid) 42%,
    var(--ns-chrome-lo) 58%,
    var(--ns-chrome-hi) 100%
  );
  box-shadow: 0 2px 3px var(--ns-drop);
}
.ns-roller {
  position: absolute;
  bottom: 0.1rem;
  width: 30px;
  height: 20px;
  border-radius: 5px;
  background: linear-gradient(180deg, var(--ns-rubber-hi), var(--ns-rubber) 55%, var(--ns-well));
}
.ns-scale {
  position: absolute;
  left: calc(var(--ns-tractor) + var(--ns-margin));
  right: calc(var(--ns-tractor) + var(--ns-margin));
  bottom: 0.3rem;
  height: 13px;
  background: repeating-linear-gradient(90deg, var(--ns-scale-ink) 0 1px, transparent 1px var(--ns-cell, 9.6px)) 0 0 /
    100% 5px no-repeat;
  --ns-cell: 9.6px;
}
.ns-scale i {
  position: absolute;
  top: 0;
  width: 1px;
  height: 7px;
  background: var(--ns-scale-ink);
}
.ns-scale b {
  position: absolute;
  top: 5.5px;
  translate: -50% 0;
  font:
    700 6.5px/7px var(--font-body),
    sans-serif;
  color: var(--ns-scale-ink);
}
.ns-scale u {
  position: absolute;
  top: -1px;
  width: 3px;
  height: 6px;
  margin-left: -1px;
  border-radius: 0 0 2px 2px;
  background: var(--ns-red);
}
.ns-platen {
  position: relative;
  width: calc(var(--ns-paper-w) + 4rem);
  height: var(--ns-platen);
  margin: 0 auto;
  border-radius: 5px;
  background: linear-gradient(
    180deg,
    var(--ns-well) 0,
    var(--ns-rubber-hi) 20%,
    var(--ns-rubber) 44%,
    var(--ns-well) 72%,
    var(--ns-rubber-lo) 100%
  );
  box-shadow: 0 6px 14px var(--ns-drop);
}
.ns-knob {
  position: absolute;
  top: -25px;
  width: 42px;
  height: calc(var(--ns-platen) + 34px);
  border-radius: 7px;
  background:
    linear-gradient(180deg, var(--ns-sheen), transparent 26%, var(--ns-drop) 100%),
    repeating-linear-gradient(180deg, var(--ns-rubber-hi) 0 2px, var(--ns-well) 2px 4px);
  box-shadow: 0 6px 12px var(--ns-drop);
}
.ns-knob.is-left {
  left: -44px;
}
.ns-knob.is-right {
  right: -44px;
}
.ns-knob::after {
  content: '';
  position: absolute;
  top: calc(50% - 12px);
  height: 24px;
  width: 10px;
  background: linear-gradient(180deg, var(--ns-chrome-hi), var(--ns-chrome-lo) 60%, var(--ns-chrome-mid));
}
.ns-knob.is-left::after {
  right: -8px;
}
.ns-knob.is-right::after {
  left: -8px;
}
/* The lever is mounted on a block at the carriage's left end and pivots there (its pivot is at 197,68 of 204x120). */
.ns-lever-mount {
  position: absolute;
  z-index: 1;
  left: calc(50% - var(--ns-paper-w) / 2 - 2rem + 4px);
  bottom: calc(var(--ns-platen) - 6px);
  width: 30px;
  height: 24px;
  border-radius: 4px 4px 2px 2px;
  background: linear-gradient(180deg, var(--ns-chrome-hi), var(--ns-chrome-mid) 45%, var(--ns-chrome-lo));
  box-shadow:
    0 3px 4px var(--ns-drop),
    inset 0 -3px 0 var(--ns-shade);
}
.ns-lever {
  position: absolute;
  z-index: 2;
  left: calc(50% - var(--ns-paper-w) / 2 - 2rem + 19px - 197px);
  bottom: calc(var(--ns-platen) + 6px - 52px);
  width: 204px;
  height: 120px;
  padding: 0;
  border: 0;
  background: none;
  cursor: pointer;
  transform-origin: 97% 56%;
  transition: rotate 260ms cubic-bezier(0.2, 1.5, 0.4, 1);
  filter: drop-shadow(0 7px 6px var(--ns-drop));
}
.ns-lever svg {
  display: block;
  width: 100%;
  height: 100%;
  overflow: visible;
}
.ns-lever:hover {
  rotate: -3deg;
}
.ns-lever:focus-visible {
  outline: 2px solid var(--ns-focus);
  outline-offset: 2px;
  border-radius: 0.5rem;
}
@media (max-width: 860px) {
  .ns-platen {
    width: calc(var(--ns-paper-w) + 1.4rem);
  }
  .ns-knob {
    top: -0.6rem;
    width: 1.1rem;
    height: 3.2rem;
  }
  .ns-knob.is-left {
    left: -1.05rem;
  }
  .ns-knob.is-right {
    right: -1.05rem;
  }
  .ns-lever,
  .ns-lever-mount,
  .ns-scale {
    display: none;
  }
}
</style>
