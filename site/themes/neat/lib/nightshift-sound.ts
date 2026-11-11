// The night-shift typewriter's sounds, ported from the reference: one second of noise played through band filters
// for the mechanism, short tones for the bodies of things, all through a compressor. The context is created on the
// visitor's first gesture in the hero, never before.
const KEY = 'ns-sound'

const A: { on: boolean; ac: AudioContext | null; out: GainNode | null; noise: AudioBuffer | null } = {
  on: true,
  ac: null,
  out: null,
  noise: null,
}
const rnd = (a: number, b: number) => a + Math.random() * (b - a)

export function readSoundPreference() {
  try {
    A.on = localStorage.getItem(KEY) !== '0'
  } catch {
    A.on = true
  }
  return A.on
}

export function setSoundEnabled(on: boolean) {
  A.on = on
  try {
    localStorage.setItem(KEY, on ? '1' : '0')
  } catch {
    // Without storage the choice lasts for this page only.
  }
}

function audioInit() {
  if (A.ac) return
  const Context = window.AudioContext
  if (!Context) return
  const ac = (A.ac = new Context())
  const comp = ac.createDynamicsCompressor()
  comp.threshold.value = -16
  comp.ratio.value = 5
  A.out = ac.createGain()
  A.out.gain.value = 0.85
  A.out.connect(comp)
  comp.connect(ac.destination)
  const b = (A.noise = ac.createBuffer(1, ac.sampleRate, ac.sampleRate))
  const d = b.getChannelData(0)
  for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1
}

/** Creates or resumes the context. Call only from a user gesture. */
export function wake() {
  if (!A.on) return
  audioInit()
  if (A.ac?.state === 'suspended') void A.ac.resume()
}

/** Resumes a context a gesture already started, when the hero is back on screen. */
export function revive() {
  if (A.on && A.ac?.state === 'suspended') void A.ac.resume()
}

export function rest() {
  if (A.ac?.state === 'running') void A.ac.suspend()
}

function burst(t: number, dur: number, freq: number, q: number, gain: number, type: BiquadFilterType = 'bandpass') {
  const ac = A.ac!
  const n = ac.createBufferSource()
  const f = ac.createBiquadFilter()
  const v = ac.createGain()
  n.buffer = A.noise
  f.type = type
  f.frequency.setValueAtTime(freq, t)
  f.Q.value = q
  v.gain.setValueAtTime(gain, t)
  v.gain.exponentialRampToValueAtTime(0.0006, t + dur)
  n.connect(f)
  f.connect(v)
  v.connect(A.out!)
  n.start(t, Math.random() * 0.8, dur + 0.03)
  return f
}

function tone(t: number, dur: number, f0: number, f1: number, gain: number) {
  const ac = A.ac!
  const o = ac.createOscillator()
  const v = ac.createGain()
  o.frequency.setValueAtTime(f0, t)
  if (f1 !== f0) o.frequency.exponentialRampToValueAtTime(f1, t + dur)
  v.gain.setValueAtTime(0.0001, t)
  v.gain.exponentialRampToValueAtTime(gain, t + 0.003)
  v.gain.exponentialRampToValueAtTime(0.0005, t + dur)
  o.connect(v)
  v.connect(A.out!)
  o.start(t)
  o.stop(t + dur + 0.05)
}

const live = () => A.on && !!A.ac && A.ac.state === 'running'

export const S = {
  clack(p: number, vel: number) {
    if (!live()) return
    const t = A.ac!.currentTime + 0.003
    burst(t, 0.034, 1450 * p, 5, 0.95 * vel)
    burst(t, 0.02, 3800 * p, 9, 0.5 * vel)
    burst(t, 0.011, 6500, 1.2, 0.22 * vel, 'highpass')
    tone(t, 0.05, 215, 92, 0.5 * vel)
    burst(t + 0.075, 0.02, 2300, 4, 0.1)
  },
  space() {
    if (!live()) return
    const t = A.ac!.currentTime + 0.003
    burst(t, 0.07, 410, 3, 1)
    tone(t, 0.1, 118, 58, 0.75)
    burst(t, 0.03, 1300, 4, 0.18)
  },
  bell() {
    if (!live()) return
    const t = A.ac!.currentTime + 0.02
    tone(t, 1.7, 2093, 2093, 0.3)
    tone(t, 1.1, 5777, 5777, 0.08)
    tone(t, 0.5, 11300, 11300, 0.025)
    burst(t, 0.012, 5200, 2, 0.2)
  },
  zip(ms: number) {
    if (!live()) return
    const t = A.ac!.currentTime + 0.06
    const d = ms / 1000
    const n = Math.max(3, Math.round(ms / 15))
    for (let i = 0; i < n; i++) burst(t + Math.pow(i / n, 0.82) * d, 0.012, rnd(3000, 3700), 7, 0.2)
    const f = burst(t, d, 800, 2.2, 0.13)
    f.frequency.exponentialRampToValueAtTime(2700, t + d)
    burst(t + d, 0.05, 520, 3, 0.8)
    tone(t + d, 0.09, 150, 66, 0.6)
  },
  feed(n: number) {
    if (!live()) return
    const t = A.ac!.currentTime + 0.003
    for (let i = 0; i < n; i++) burst(t + i * 0.068, 0.014, 2600, 7, 0.3)
  },
  tick() {
    if (!live()) return
    const t = A.ac!.currentTime + 0.003
    burst(t, 0.02, 2000, 6, 0.4)
    tone(t, 0.035, 300, 150, 0.22)
  },
  thud() {
    if (!live()) return
    const t = A.ac!.currentTime + 0.003
    tone(t, 0.22, 96, 44, 0.9)
    burst(t, 0.1, 210, 1.1, 0.85, 'lowpass')
  },
  rip() {
    if (!live()) return
    const t = A.ac!.currentTime + 0.003
    const f = burst(t, 0.46, 1100, 1.4, 0.38)
    f.frequency.exponentialRampToValueAtTime(5400, t + 0.43)
    for (let i = 0; i < 16; i++) burst(t + Math.pow(i / 16, 1.5) * 0.42, 0.01, 3400, 7, 0.2)
    burst(t + 1.25, 0.14, 520, 0.7, 0.22, 'lowpass')
  },
  flip() {
    if (!A.ac) return
    const t = A.ac.currentTime + 0.003
    burst(t, 0.016, 2400, 3, 0.5)
    tone(t, 0.035, 420, 190, 0.3)
  },
  // Additions for this site: the lighter chatter of a reply, the dimmer's detent and the pager's beep.
  chatter(p: number) {
    if (!live()) return
    const t = A.ac!.currentTime + 0.003
    burst(t, 0.018, 2600 * p, 6, 0.32)
    tone(t, 0.03, 240, 120, 0.18)
  },
  detent() {
    if (!live()) return
    const t = A.ac!.currentTime + 0.003
    burst(t, 0.009, 3200, 5, 0.3)
  },
  beep() {
    if (!live()) return
    const t = A.ac!.currentTime + 0.003
    tone(t, 0.07, 3100, 3100, 0.12)
    tone(t + 0.11, 0.07, 3100, 3100, 0.12)
  },
}
