// The typewriter's mechanism, ported from the reference: every press becomes an action in one queue (input / pump /
// exec), characters strike after the typebar's rise (UP), the carriage steps a column per character, tab jumps to
// the stops, return throws the carriage home with a zip whose length grows with the column, the bell rings eight
// columns before the margin and typing past it jams. Replies print through the same mechanism. Nothing runs idle.
import { computed, nextTick, ref, type Ref } from 'vue'
import { S } from '../../lib/nightshift-sound'
import { ANSWER_BACK, type Reply } from '../../lib/nightshift'

export type Action =
  { t: 'ch'; ch: string } | { t: 'back' } | { t: 'ret' } | { t: 'tab' } | { t: 'new' } | { t: 'hereis' }
export interface Glyph {
  c: string
  d: number
  red?: boolean
  wet?: boolean
  /** False until the typebar has struck: the glyph holds its place in the line but is not inked yet. */
  landed?: boolean
}
export interface Line {
  id: number
  kind: 'cmd' | 'out'
  glyphs: Glyph[]
}
type Where = 'eyebrow' | 'title' | 'intro' | 'log' | null

interface Parts {
  paper: Ref<HTMLElement | null>
  sheet: Ref<HTMLElement | null>
  printed: Ref<HTMLElement | null>
  glyphs: Ref<HTMLElement | null>
  pile: () => HTMLElement | null
  respond: (command: string) => Reply
  visit: (url: string) => void
  announce: (text: string) => void
  red: () => boolean
}

const KEEP = 14
const UP = 62
const TABW = 8
const PREFIX = 2
const REPLY_MS = 19
const rnd = (a: number, b: number) => a + Math.random() * (b - a)
export const reducedMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches
export const labelOf = (char: string) => (char === ' ' ? ' ' : char.toUpperCase())

const quirks: Record<string, { dx: number; dy: number; rot: number; pitch: number }> = {}
/** Each type slug is a little off in its own way, the same way every time: position, tilt and pitch. */
export function quirk(ch: string) {
  let q = quirks[ch]
  if (!q) {
    let h = (ch.charCodeAt(0) * 2654435761) >>> 0
    const f = () => {
      h ^= h << 13
      h >>>= 0
      h ^= h >>> 17
      h ^= h << 5
      h >>>= 0
      return h / 4294967296
    }
    q = quirks[ch] = {
      dx: (f() - 0.5) * 0.8,
      dy: (f() - 0.5) * 1.2,
      rot: (f() - 0.5) * 0.036,
      pitch: 0.82 + f() * 0.42,
    }
    if (ch === 'e') q.dy = -1.05
  }
  return q
}

export function useMachine(parts: Parts) {
  const typed = ref<Glyph[]>([])
  const command = computed(() => typed.value.map((glyph) => glyph.c).join(''))
  const log = ref<Line[]>([])
  const pressed = ref('')
  const jamming = ref('')
  const strikes = ref(0)
  const tally = ref(0)
  const struck = ref('')
  const bells = ref(0)
  const returns = ref(0)
  const jams = ref(0)
  const head = ref(0)
  const travel = ref(80)
  const count = ref(0)
  const busy = ref(false)
  const ready = ref(false)
  const engaged = ref(false)
  const shift = ref(false)
  const lock = ref(false)
  const at = ref<Where>(null)

  const queue: Action[] = []
  let mark: HTMLElement | null = null
  let nextFree = 0
  let timer = 0
  let release = 0
  let lastStrike = 0
  let nextId = 0
  let feeding: Animation | null = null
  let tearing = false
  let alive = true
  let skip = false
  let col = PREFIX

  const wait = (ms: number) => new Promise<void>((done) => window.setTimeout(done, ms))
  const cell = (element: Element) => parseFloat(getComputedStyle(element).fontSize) * 0.6
  const settled = () => (feeding?.playState === 'running' ? feeding.finished.then(() => undefined) : undefined)

  function setMark(element: unknown) {
    if (element) mark = element as HTMLElement
  }

  function columns() {
    const glyphs = parts.glyphs.value
    return glyphs ? Math.floor(parts.printed.value!.clientWidth / cell(glyphs)) : 60
  }

  function follow(ms = 80) {
    const paper = parts.paper.value
    if (!paper) return
    travel.value = ms
    const left = paper.getBoundingClientRect().left
    if (at.value && mark?.isConnected) {
      head.value = mark.getBoundingClientRect().left - left + cell(mark) / 2
      return
    }
    const glyphs = parts.glyphs.value
    if (!glyphs) return
    const step = cell(glyphs)
    head.value = glyphs.getBoundingClientRect().left - left + (col - PREFIX) * step + step / 2
  }

  function press(label: string, ms = 115) {
    pressed.value = label
    window.clearTimeout(release)
    release = window.setTimeout(() => {
      pressed.value = ''
      jamming.value = ''
    }, ms)
  }

  /** The visitor has started using the machine: from now on the carriage carries the paper to the typing point. */
  function engage() {
    if (engaged.value) return
    engaged.value = true
    const length = reducedMotion() ? 0 : 150 + col * 8.5
    S.zip(Math.max(length, 140))
    nextFree = performance.now() + length + 60
    void nextTick(() => follow(length))
  }

  function input(action: Action) {
    queue.push(action)
    pump()
  }

  function pump() {
    if (timer || busy.value || !ready.value) return
    while (queue.length && !busy.value) {
      const now = performance.now()
      if (now < nextFree) {
        timer = window.setTimeout(
          () => {
            timer = 0
            pump()
          },
          nextFree - now + 2,
        )
        return
      }
      exec(queue.shift()!)
    }
  }

  function exec(action: Action) {
    if (action.t === 'ch') doChar(action.ch)
    else if (action.t === 'back') {
      press('BACK')
      if (col > PREFIX) {
        col--
        typed.value.pop()
        S.tick()
        nextFree = performance.now() + 40
        void nextTick(() => follow())
      }
    } else if (action.t === 'ret') doReturn()
    else if (action.t === 'tab') doTab()
    else if (action.t === 'hereis') {
      press('HERE IS', 180)
      void reply([ANSWER_BACK])
    } else void eject()
  }

  function ring() {
    S.bell()
    bells.value++
  }

  function jam(label: string) {
    press(label, 150)
    jamming.value = label
    S.thud()
    jams.value++
  }

  function doChar(raw: string) {
    const ch = shift.value || lock.value ? shifted(raw) : raw
    if (shift.value) shift.value = false
    const label = labelOf(raw)
    const bell = columns() - 8
    if (ch === ' ') {
      if (col >= columns()) return jam(' ')
      press(' ')
      S.space()
      typed.value.push({ c: ' ', d: 1 })
      col++
      if (col === bell) ring()
      void nextTick(() => follow())
      return
    }
    if (col >= columns()) return jam(label)
    press(label)
    const now = performance.now()
    const gap = now - lastStrike
    lastStrike = now
    const density = gap < 55 ? rnd(0.5, 0.62) : gap < 105 ? rnd(0.68, 0.84) : rnd(0.86, 1)
    const instant = reducedMotion()
    typed.value.push({ c: ch, d: 0.55 + density * 0.45, red: parts.red(), wet: !instant, landed: instant })
    const glyph = typed.value[typed.value.length - 1]
    struck.value = ch
    strikes.value++
    const hit = () => {
      glyph.landed = true
      S.clack(quirk(ch).pitch, 0.55 + density * 0.5)
      tally.value++
      void nextTick(() => follow())
    }
    col++
    if (instant) hit()
    else window.setTimeout(hit, UP - 6)
    nextFree = now + UP - 4
    if (col === bell) ring()
  }

  function doTab() {
    press('TAB')
    if (col >= columns()) return jam('TAB')
    const old = col
    col = Math.min(columns(), PREFIX + (Math.floor((col - PREFIX) / TABW) + 1) * TABW)
    for (let index = old; index < col; index++) typed.value.push({ c: ' ', d: 1 })
    const length = 80 + (col - old) * 9
    S.tick()
    const bell = columns() - 8
    if (old < bell && col >= bell) ring()
    nextFree = performance.now() + length + 70
    void nextTick(() => follow(length))
  }

  function doReturn() {
    press('RETURN', 220)
    const length = reducedMotion() ? 140 : 150 + col * 8.5
    returns.value++
    S.zip(length)
    const glyphs = typed.value
    const text = command.value
    typed.value = []
    col = PREFIX
    busy.value = true
    nextFree = performance.now() + length + 100
    void nextTick(() => follow(length))
    window.setTimeout(() => void submit(text, glyphs), length)
  }

  async function addLine(kind: Line['kind'], glyphs: Glyph[] = []) {
    if (log.value.length >= KEEP) {
      log.value.splice(0, log.value.length - KEEP + 1)
      await nextTick()
    }
    log.value.push({ id: nextId++, kind, glyphs })
    return log.value[log.value.length - 1]
  }

  async function submit(text: string, glyphs: Glyph[]) {
    const answer = parts.respond(text)
    if (answer.clear) {
      log.value = []
      return finish()
    }
    await addLine('cmd', [{ c: '$', d: 1 }, { c: ' ', d: 1 }, ...glyphs.map((glyph) => ({ ...glyph, wet: false }))])
    await reply(answer.lines)
    if (answer.visit) {
      const url = answer.visit
      window.setTimeout(() => alive && parts.visit(url), 600)
    }
  }

  async function reply(lines: string[]) {
    busy.value = true
    for (const text of lines) {
      await settled()
      const line = await addLine('out')
      await print(text, (shown) => (line.glyphs = shown), REPLY_MS, 'log', true)
    }
    if (lines.length) parts.announce(lines.join(' '))
    finish()
  }

  function finish() {
    busy.value = false
    void nextTick(() => {
      follow(engaged.value ? 150 + col * 8.5 : 80)
      pump()
    })
  }

  // Prints text a character at a time at the mark, the carriage carrying it. A line never strikes while the paper is
  // still feeding, so it is never printed under the bail.
  async function print(
    text: string,
    show: (glyphs: Glyph[]) => void,
    ms: number | (() => number),
    where: Where,
    machine = false,
  ) {
    at.value = where
    const instant = reducedMotion()
    const glyphs: Glyph[] = []
    for (let index = 0; index < text.length && alive; index++) {
      const char = text[index]
      glyphs.push({ c: char, d: rnd(0.86, 1), wet: !instant && !skip })
      if (skip || instant) continue
      show([...glyphs])
      if (char !== ' ') {
        press(labelOf(char), 70)
        struck.value = char
        strikes.value++
        if (machine) S.chatter(quirk(char).pitch)
        else S.clack(quirk(char).pitch, 0.7)
      }
      await nextTick()
      await settled()
      follow()
      await wait(typeof ms === 'number' ? ms : ms())
    }
    show(glyphs)
    at.value = null
  }

  /** New sheet: the paper is torn off, lifted out and dropped on the pile; a fresh one feeds in. */
  async function eject() {
    const paper = parts.paper.value
    const sheet = parts.sheet.value
    S.rip()
    if (!paper || !sheet || reducedMotion()) {
      log.value = []
      return
    }
    tearing = true
    busy.value = true
    const ghost = sheet.cloneNode(true) as HTMLElement
    ghost.setAttribute('aria-hidden', 'true')
    ghost.inert = true
    ghost.classList.add('ns-ghost')
    paper.appendChild(ghost)
    const from = paper.getBoundingClientRect()
    const to = parts.pile()?.getBoundingClientRect()
    const dx = to ? to.left + to.width / 2 - (from.left + from.width / 2) : 0
    const dy = to ? to.top + to.height / 2 - from.bottom + ghost.offsetHeight / 2 : -from.height
    const fly = ghost.animate(
      [
        { translate: '0 0', scale: '1', rotate: '0deg', opacity: 1 },
        { translate: `0 ${-from.height * 0.55}px`, scale: '0.9', rotate: '0deg', opacity: 1, offset: 0.38 },
        { translate: `${dx * 0.6}px ${dy * 0.4 - 80}px`, scale: '0.5', rotate: '8deg', opacity: 1, offset: 0.7 },
        { translate: `${dx}px ${dy}px`, scale: '0.28', rotate: '3deg', opacity: 0 },
      ],
      { duration: 1050, easing: 'cubic-bezier(.45,0,.4,1)' },
    )
    void fly.finished.then(() => ghost.remove())
    log.value = []
    typed.value = []
    col = PREFIX
    await nextTick()
    await wait(480)
    S.feed(7)
    await sheet.animate([{ translate: '0 70px' }, { translate: '0 0' }], { duration: 430, easing: 'steps(7, end)' })
      .finished
    tearing = false
    finish()
  }

  // The paper feeds up a band at a time: whenever what is printed grows, it starts that much lower and eases up.
  function watchFeed(lineHeight: () => number) {
    let last = 0
    const observer = new ResizeObserver(() => {
      const height = parts.printed.value!.offsetHeight
      const grown = height - last
      const lines = Math.round(grown / lineHeight())
      if (!last) count.value = Math.round(height / lineHeight())
      else if (lines > 0) count.value += lines
      last = height
      if (lines <= 0 || grown === height || tearing) return
      S.feed(lines)
      if (reducedMotion()) return
      feeding = parts.sheet.value!.animate([{ translate: `0 ${grown}px` }, { translate: '0 0' }], {
        duration: 150,
        easing: 'cubic-bezier(.3,1.2,.4,1)',
      })
    })
    observer.observe(parts.printed.value!)
    return () => observer.disconnect()
  }

  function setHistory(text: string) {
    typed.value = [...text].map((c) => ({ c, d: 0.95 }))
    col = PREFIX + text.length
    void nextTick(() => follow())
  }

  function stop() {
    alive = false
    window.clearTimeout(timer)
    window.clearTimeout(release)
  }

  return {
    typed,
    command,
    log,
    pressed,
    jamming,
    strikes,
    tally,
    struck,
    bells,
    returns,
    jams,
    head,
    travel,
    count,
    busy,
    ready,
    engaged,
    shift,
    lock,
    at,
    columns,
    setMark,
    follow,
    engage,
    input,
    pump,
    print,
    watchFeed,
    setHistory,
    stop,
    skipPrinting: () => (skip = true),
    resumePrinting: () => (skip = false),
  }
}

const SHIFTED: Record<string, string> = {
  '1': '!',
  '2': '@',
  '3': '#',
  '4': '$',
  '5': '%',
  '6': '^',
  '7': '&',
  '8': '*',
  '9': '(',
  '0': ')',
  '-': '_',
  ';': ':',
  "'": '"',
  ',': '<',
  '.': '>',
  '/': '?',
}
const shifted = (ch: string) => SHIFTED[ch] ?? ch.toUpperCase()
