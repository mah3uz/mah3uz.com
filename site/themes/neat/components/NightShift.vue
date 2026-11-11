<script setup lang="ts">
// The home page's hero: a typewriter on a desk under a lamp. The server prints the eyebrow, headline and intro on the
// paper as text; the first home view of a session re-prints them a character at a time. Once the visitor clicks the
// machine or types into the prompt, printable keys go to the paper while the hero is on screen (never with Ctrl,
// Meta or Alt, never while focus is in a field or on a control). Until then the site's own single-key shortcuts work.
import { router } from '@inertiajs/vue3'
import { computed, h, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import type { PagesPage } from '@site/types'
import { respond, type Action as DeskAction } from '../lib/nightshift'
import { readSoundPreference, rest, revive, S, setSoundEnabled, wake } from '../lib/nightshift-sound'
import type { ProjectLike } from '../lib/projects'
import Carriage from './nightshift/Carriage.vue'
import DeskProps from './nightshift/DeskProps.vue'
import Lamp from './nightshift/Lamp.vue'
import SoundSwitch from './nightshift/SoundSwitch.vue'
import Typewriter from './nightshift/Typewriter.vue'
import { quirk, reducedMotion, useMachine, type Action, type Glyph } from './nightshift/useMachine'

type Post = {
  id: number | string
  title: string | null
  uri: string | null
  excerpt?: string | null
  published_at?: string | null
}
const props = defineProps<{ page: PagesPage; projects: ProjectLike[]; posts: Post[] }>()

const eyebrow = props.page.eyebrow ?? ''
const title = props.page.title ?? ''
const intro = props.page.intro ?? ''

// Runs before the paper is painted: on a first visit with motion allowed, the printed text starts hidden so the
// re-print never flashes the finished page first. If the app never mounts, the text comes back after four seconds.
const GATE = `try{if(!sessionStorage.getItem('ns-printed')&&!matchMedia('(prefers-reduced-motion: reduce)').matches&&!matchMedia('(max-width: 767px)').matches){var r=document.documentElement;r.classList.add('ns-reprint');setTimeout(function(){r.classList.remove('ns-reprint')},4000)}}catch(e){}`
const PrintGate = () => h('script', { innerHTML: GATE })

const shownEyebrow = ref(eyebrow)
const shownTitle = ref(title)
const shownIntro = ref(intro)
const printing = ref(false)
const lamp = ref(7)
const sound = ref(true)
const red = ref(false)
const held = ref(false)
const paused = ref(false)
const announcement = ref('')
const columns = ref(65)
const cell = ref(9.6)
const carriageX = ref(0)

const scene = ref<HTMLElement | null>(null)
const paper = ref<HTMLElement | null>(null)
const sheet = ref<HTMLElement | null>(null)
const printed = ref<HTMLElement | null>(null)
const glyphs = ref<HTMLElement | null>(null)
const input = ref<HTMLInputElement | null>(null)

const latest = computed(() => props.posts[0] ?? null)
const history: string[] = []
let recall = 0
let armed = false
let listening = false
// On a phone the hero is a still picture: no typing, no sound, no animation, nothing set up at all.
let still = true
const phone = () => window.matchMedia('(max-width: 767px)').matches
const cleanups: (() => void)[] = []

const machine = useMachine({
  paper,
  sheet,
  printed,
  glyphs,
  pile: () => scene.value?.querySelector<HTMLElement>('.ns-pile') ?? null,
  respond: (command) => {
    if (command.trim()) history.push(command)
    recall = history.length
    const log = printed.value!.querySelector<HTMLElement>('.ns-log')!
    const cols = Math.floor(log.clientWidth / (parseFloat(getComputedStyle(log).fontSize) * 0.6))
    const theme = document.documentElement.dataset.theme
    const reply = respond(command, {
      projects: props.projects,
      latest: latest.value,
      cols,
      posts: props.posts,
      history: [...history],
      lamp: lamp.value,
      sound: sound.value,
      theme: theme
        ? theme === 'dark'
          ? 'dark'
          : 'light'
        : matchMedia('(prefers-color-scheme: dark)').matches
          ? 'dark'
          : 'light',
      now: new Date(),
    })
    if (reply.action) perform(reply.action)
    return reply
  },
  visit: (url) => router.visit(url),
  announce: (text) => (announcement.value = text),
  red: () => red.value,
})
const { typed, command, log, pressed, jamming, strikes, tally, struck, bells, returns, jams, head, travel } = machine
const { busy, ready, engaged, at, setMark } = machine
const lifted = computed(() => machine.shift.value || machine.lock.value || held.value)

// The ink: each glyph lands with its slug's quirks, at the density the stroke gave it, and once in a while a faint
// double impression.
function ink(glyph: Glyph) {
  const q = quirk(glyph.c)
  return {
    opacity: glyph.landed === false ? 0 : glyph.d,
    transform: `translate(${(q.dx * 0.6).toFixed(2)}px, ${(q.dy * 0.6).toFixed(2)}px) rotate(${q.rot.toFixed(3)}rad)`,
  }
}

// The carriage carries the paper so the printing point stays at the machine's centre. Until the visitor uses the
// machine it rests centred, and on a phone the paper always stays put.
watch([head, engaged], ([x]) => {
  const width = paper.value?.clientWidth ?? 0
  carriageX.value = !engaged.value || window.innerWidth <= 860 ? 0 : Math.round(width / 2 - x)
})
const carriageMove = computed(() =>
  travel.value > 80
    ? `translate ${travel.value}ms cubic-bezier(.5,0,.2,1) 60ms, transform 70ms cubic-bezier(.3,.8,.4,1.3)`
    : 'translate 80ms cubic-bezier(.2,.7,.3,1.4), transform 70ms cubic-bezier(.3,.8,.4,1.3)',
)

function measure() {
  if (!glyphs.value || !paper.value) return
  cell.value = parseFloat(getComputedStyle(glyphs.value).fontSize) * 0.6
  columns.value = machine.columns()
}

function wakeUp() {
  if (!still) wake()
}

function take(action: Action) {
  if (still) return
  wake()
  listening = true
  if (printing.value) machine.skipPrinting()
  machine.engage()
  machine.input(action)
}

function takeText(text: string) {
  for (const char of text) if (char >= ' ' && char <= '~') take({ t: 'ch', ch: char })
}

// Keys typed on the page once the visitor has started using the machine, while it is on screen.
const OWN_FOCUS = 'input, textarea, select, button, a[href], summary, [contenteditable], [role=slider], [role=switch]'
function onPageKey(event: KeyboardEvent) {
  if (!armed || !listening || event.defaultPrevented || event.ctrlKey || event.metaKey || event.altKey) return
  if (event.isComposing) return
  const focused = document.activeElement
  if (focused && focused !== document.body && focused.closest(OWN_FOCUS)) return
  const consume = () => {
    event.preventDefault()
    event.stopPropagation()
  }
  if (event.key === 'Shift') held.value = true
  else if (event.key === 'Enter') {
    consume()
    if (!event.repeat) take({ t: 'ret' })
  } else if (event.key === 'Backspace') {
    consume()
    take({ t: 'back' })
  } else if (event.key === 'Tab' && !event.shiftKey) {
    consume()
    if (!event.repeat) take({ t: 'tab' })
  } else if (event.key.length === 1 && event.key >= ' ' && event.key <= '~') {
    consume()
    if (!event.repeat || event.key === ' ') take({ t: 'ch', ch: event.key })
  }
}
function onPageKeyUp(event: KeyboardEvent) {
  if (event.key === 'Shift') held.value = false
}
// A click in the machine starts listening; a click anywhere else outside the hero gives the keys back to the site.
function onPagePointer(event: PointerEvent) {
  const target = event.target as Element | null
  if (target?.closest('.ns-machine, .ns-sound, .ns-rheostat')) listening = true
  else if (!target?.closest('.ns-scene')) listening = false
}

// The prompt's own input: its value always mirrors the machine, so every edit becomes an action instead.
function beforeInput(event: InputEvent) {
  event.preventDefault()
  if (event.inputType.startsWith('insert')) {
    if (event.inputType === 'insertLineBreak' || event.inputType === 'insertParagraph') return take({ t: 'ret' })
    takeText(event.data ?? event.dataTransfer?.getData('text/plain') ?? '')
  } else if (event.inputType.startsWith('delete')) take({ t: 'back' })
}

function inputKey(event: KeyboardEvent) {
  if (event.key === 'Enter') {
    event.preventDefault()
    if (!event.repeat) take({ t: 'ret' })
  } else if (event.key === 'Tab' && !event.shiftKey && typed.value.length) {
    event.preventDefault()
    take({ t: 'tab' })
  } else if ((event.key === 'ArrowUp' || event.key === 'ArrowDown') && history.length && !busy.value) {
    event.preventDefault()
    recall = Math.max(0, Math.min(history.length, recall + (event.key === 'ArrowUp' ? -1 : 1)))
    machine.setHistory(history[recall] ?? '')
  }
}

function tap(key: string) {
  if (still) return
  if (key === 'Enter') return take({ t: 'ret' })
  if (key === 'back' || key === 'tab' || key === 'hereis') return take({ t: key })
  if (key === 'shift' || key === 'lock') {
    wake()
    listening = true
    if (key === 'shift') machine.shift.value = !machine.shift.value
    else machine.lock.value = !machine.lock.value
    return S.tick()
  }
  take({ t: 'ch', ch: key })
}

function focusPaper() {
  if (still) return
  wake()
  listening = true
  if (printing.value) return void machine.skipPrinting()
  if (window.getSelection()?.isCollapsed === false) return
  input.value?.focus({ preventScroll: true })
}

// Same cookie and attribute as the header switch, which watches the attribute and follows.
function perform(action: DeskAction) {
  if ('theme' in action) {
    const now = document.documentElement.dataset.theme
    const dark = now ? now === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches
    const theme = action.theme === 'toggle' ? (dark ? 'light' : 'dark') : action.theme
    document.cookie = `nibble_theme=${theme}; path=/; max-age=31536000; samesite=lax`
    document.documentElement.dataset.theme = theme
  } else if ('lamp' in action) lamp.value = action.lamp
  else if ('sound' in action) setSound(action.sound)
  else if (action.scroll === 'top') scene.value?.scrollIntoView({ behavior: reducedMotion() ? 'auto' : 'smooth' })
  else
    (scene.value?.nextElementSibling ?? scene.value)?.scrollIntoView({
      behavior: reducedMotion() ? 'auto' : 'smooth',
    })
}

function setSound(on: boolean) {
  if (!on) S.flip()
  setSoundEnabled(on)
  sound.value = on
  if (on) {
    wake()
    S.flip()
  }
}

// Each detent of the rheostat clicks; turning it to OFF gives the heavier click of the switch.
watch(lamp, (value) => {
  wakeUp()
  if (value === 0) S.tick()
  else S.detent()
})
watch(red, () => S.tick())

// Typing is armed while at least 40% of the hero is on screen; looping animation and sound rest when it is not.
function watchVisibility() {
  let visible = true
  const update = () => {
    paused.value = !visible || document.hidden
    if (paused.value) rest()
    else revive()
  }
  const observer = new IntersectionObserver(
    ([entry]) => {
      visible = entry.isIntersecting
      armed = entry.intersectionRatio >= 0.4
      update()
    },
    { threshold: [0, 0.4] },
  )
  observer.observe(scene.value!)
  document.addEventListener('visibilitychange', update)
  document.addEventListener('keydown', onPageKey, true)
  document.addEventListener('keyup', onPageKeyUp, true)
  document.addEventListener('pointerdown', onPagePointer, true)
  const resize = () => {
    measure()
    machine.follow()
  }
  window.addEventListener('resize', resize, { passive: true })
  cleanups.push(() => {
    observer.disconnect()
    document.removeEventListener('visibilitychange', update)
    document.removeEventListener('keydown', onPageKey, true)
    document.removeEventListener('keyup', onPageKeyUp, true)
    document.removeEventListener('pointerdown', onPagePointer, true)
    window.removeEventListener('resize', resize)
  })
}

// The desk's grain, as the reference makes it: a tile of soft specks drawn once.
function grain() {
  const canvas = document.createElement('canvas')
  canvas.width = canvas.height = 180
  const context = canvas.getContext('2d')
  if (!context) return
  const image = context.createImageData(180, 180)
  const d = image.data
  for (let i = 0; i < d.length; i += 4) {
    const v = Math.random()
    d[i] = v > 0.5 ? 233 : 4
    d[i + 1] = v > 0.5 ? 247 : 48
    d[i + 2] = v > 0.5 ? 247 : 64
    d[i + 3] = Math.abs(v - 0.5) * 44
  }
  context.putImageData(image, 0, 0)
  scene.value?.style.setProperty('--ns-grain', `url(${canvas.toDataURL()})`)
}

const text = (glyphs: Glyph[]) => glyphs.map((glyph) => glyph.c).join('')
// The reference's typing pace for the headline: uneven, with a breath after punctuation.
const pace = (char: () => string) => () => {
  const c = char()
  let d = 34 + Math.random() * 40
  if (c === ',' || c === '.') d += 120
  return d
}

onMounted(async () => {
  if (phone()) {
    document.documentElement.classList.remove('ns-reprint')
    return
  }
  still = false
  sound.value = readSoundPreference()
  cleanups.push(machine.watchFeed(() => parseFloat(getComputedStyle(input.value!.parentElement!).lineHeight) || 30))
  watchVisibility()
  grain()
  const root = document.documentElement
  const reprint = root.classList.contains('ns-reprint')
  try {
    sessionStorage.setItem('ns-printed', '1')
  } catch {
    // Storage can be blocked; the page just prints again next time.
  }
  if (reprint && !reducedMotion()) {
    printing.value = true
    shownEyebrow.value = ''
    shownTitle.value = ''
    shownIntro.value = ''
    await nextTick()
    root.classList.remove('ns-reprint')
    await new Promise((done) => window.setTimeout(done, 520))
    await machine.print(eyebrow, (g) => (shownEyebrow.value = text(g)), 12, 'eyebrow')
    await machine.print(
      title,
      (g) => (shownTitle.value = text(g)),
      pace(() => shownTitle.value.slice(-1)),
      'title',
    )
    await machine.print(intro, (g) => (shownIntro.value = text(g)), 9, 'intro')
    machine.resumePrinting()
    printing.value = false
  } else root.classList.remove('ns-reprint')
  ready.value = true
  await nextTick()
  measure()
  machine.follow()
  machine.pump()
})

onBeforeUnmount(() => {
  machine.stop()
  cleanups.forEach((cleanup) => cleanup())
})
</script>

<template>
  <section
    ref="scene"
    class="ns-scene"
    :class="{ 'is-paused': paused }"
    :style="{ '--ns-lamp': lamp / 10 }"
    aria-label="The night shift: a typewriter on a desk under a lamp"
    @pointerdown="wakeUp"
  >
    <PrintGate />
    <div class="ns-desk" aria-hidden="true" />
    <div class="ns-daylight" aria-hidden="true" />
    <div class="ns-pool" aria-hidden="true" />
    <div class="ns-room" aria-hidden="true" />

    <div class="ns-stage">
      <DeskProps :posts="posts" />
      <div class="ns-machine">
        <div
          class="ns-run"
          :class="{ 'is-lift': lifted }"
          :style="{ translate: `${carriageX}px 0`, transition: carriageMove }"
        >
          <div ref="paper" class="ns-paper" @click="focusPaper">
            <div ref="sheet" class="ns-sheet">
              <div class="ns-bands" aria-hidden="true" />
              <div class="ns-tractor is-left" aria-hidden="true" />
              <div class="ns-tractor is-right" aria-hidden="true" />
              <div ref="printed" class="ns-printed">
                <div class="ns-perforation" aria-hidden="true" />
                <p v-if="eyebrow" class="ns-eyebrow ns-print">
                  {{ shownEyebrow }}<i v-if="at === 'eyebrow'" :ref="setMark" class="ns-mark" />
                </p>
                <h1 class="ns-headline ns-print">
                  {{ shownTitle }}<i v-if="at === 'title'" :ref="setMark" class="ns-mark" />
                </h1>
                <p v-if="intro" class="ns-intro ns-print">
                  {{ shownIntro }}<i v-if="at === 'intro'" :ref="setMark" class="ns-mark" />
                </p>
                <div class="ns-log">
                  <p v-for="(line, index) in log" :key="line.id" class="ns-line" :class="`is-${line.kind}`">
                    <span
                      v-for="(glyph, place) in line.glyphs"
                      :key="place"
                      class="ns-glyph"
                      :class="{ 'is-red': glyph.red, 'is-wet': glyph.wet && glyph.landed !== false }"
                      :data-c="glyph.c"
                      :style="ink(glyph)"
                      >{{ glyph.c }}</span
                    ><i v-if="at === 'log' && index === log.length - 1" :ref="setMark" class="ns-mark" />
                  </p>
                </div>
                <label class="ns-prompt" :class="{ 'is-waiting': !ready || busy || printing }">
                  <span class="ns-dollar" aria-hidden="true">$</span>
                  <span ref="glyphs" class="ns-glyphs" aria-hidden="true"
                    ><span
                      v-for="(glyph, place) in typed"
                      :key="place"
                      class="ns-glyph"
                      :class="{ 'is-red': glyph.red, 'is-wet': glyph.wet && glyph.landed !== false }"
                      :data-c="glyph.c"
                      :style="ink(glyph)"
                      >{{ glyph.c }}</span
                    ></span
                  >
                  <span class="sr-only">Type a command, then press return. Try help.</span>
                  <input
                    ref="input"
                    :value="command"
                    class="ns-input"
                    type="text"
                    :disabled="!ready"
                    :placeholder="ready && !typed.length ? 'help' : ''"
                    autocomplete="off"
                    autocapitalize="off"
                    spellcheck="false"
                    enterkeyhint="send"
                    @focus="listening = true"
                    @beforeinput="beforeInput"
                    @keydown="inputKey"
                  />
                </label>
              </div>
            </div>
            <div class="ns-paper-light" aria-hidden="true" />
          </div>
          <Carriage :returns="returns" :columns="columns" :cell="cell" :tab="8" @return="take({ t: 'ret' })" />
        </div>
        <Typewriter
          v-model:red="red"
          :pressed="pressed"
          :jamming="jamming"
          :char="struck"
          :tally="tally"
          :strikes="strikes"
          :bells="bells"
          :jams="jams"
          :shift="machine.shift.value"
          :lock="machine.lock.value"
          @key="tap"
          @clear="take({ t: 'new' })"
        />
      </div>
    </div>
    <div class="ns-glow" aria-hidden="true" />
    <div class="ns-dim" aria-hidden="true" />
    <div class="ns-vignette" aria-hidden="true" />
    <div class="ns-vignette-deep" aria-hidden="true" />
    <div class="ns-grain" aria-hidden="true" />
    <Lamp v-model="lamp" />
    <SoundSwitch :model-value="sound" @update:model-value="setSound" />
    <p class="sr-only" aria-live="polite">{{ announcement }}</p>
  </section>
</template>

<style src="./nightshift/tokens.css"></style>
<style src="./nightshift/scene.css"></style>
