// The keyboard layout, from the reference: each key carries its plain and shifted character. Typebars in the basket
// are numbered by where their key sits across the keyboard, so a key's bar swings up from the matching side.
export type KeyDef = [plain: string, shifted: string, wide?: 1]

const L2 = (c: string): KeyDef => [c, c.toUpperCase()]
export const ROWS: KeyDef[][] = [
  [
    ['1', '!'],
    ['2', '@'],
    ['3', '#'],
    ['4', '$'],
    ['5', '%'],
    ['6', '^'],
    ['7', '&'],
    ['8', '*'],
    ['9', '('],
    ['0', ')'],
    ['-', '_', 1],
  ],
  [...'qwertyuiop'].map(L2),
  [...[...'asdfghjkl'].map(L2), [';', ':', 1], ["'", '"']],
  [...[...'zxcvbnm'].map(L2), [',', '<'], ['.', '>'], ['/', '?']],
]

export const BAR_COUNT = 42
const order: { chars: string[]; x: number }[] = []
ROWS.forEach((row, r) =>
  row.forEach((d, j) => order.push({ chars: [d[0], d[1]], x: (j + [0, 0.5, 0.75, 1.25][r]) / 11.5 })),
)
order.sort((a, b) => a.x - b.x)
const bars: Record<string, number> = {}
order.forEach((o, i) => o.chars.forEach((c) => (bars[c] = Math.round((i / (order.length - 1)) * (BAR_COUNT - 1)))))
export const barOf = (ch: string) => bars[ch] ?? bars[ch.toLowerCase()] ?? BAR_COUNT >> 1
