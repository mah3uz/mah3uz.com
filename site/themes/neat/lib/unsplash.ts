// Unsplash asks that its images be hot-linked from images.unsplash.com and resized with URL parameters, and that
// links back to Unsplash carry its referral parameters (https://unsplash.com/documentation).
import { decode, isBlurhashValid } from 'blurhash'

const REFERRAL = 'utm_source=mah3uz&utm_medium=referral'

export const PROFILE = `https://unsplash.com/@mah3uz?${REFERRAL}`

export function sized(raw: string | null | undefined, width: number) {
  if (!raw) return ''
  const url = new URL(raw)
  url.searchParams.set('w', String(width))
  url.searchParams.set('auto', 'format')
  url.searchParams.set('fit', 'max')
  url.searchParams.set('q', '80')
  return url.toString()
}

export const srcset = (raw: string | null | undefined, widths = [480, 800, 1200, 1600, 2200]) =>
  raw ? widths.map((width) => `${sized(raw, width)} ${width}w`).join(', ') : undefined

export function referral(url: string | null | undefined) {
  if (!url) return PROFILE
  return `${url}${url.includes('?') ? '&' : '?'}${REFERRAL}`
}

export const compact = (value: number | null | undefined) =>
  new Intl.NumberFormat('en', { notation: 'compact', maximumFractionDigits: 1 }).format(value ?? 0)

// A photo's BlurHash, decoded into a tiny bitmap and returned as a data URL. Done in plain code rather than on a
// canvas, so the server renders the same preview the browser would and it is there from the first paint. Eight pixels
// across is all a BlurHash holds; the browser's scaling and a CSS blur smooth it.
export function blurPreview(
  hash: string | null | undefined,
  width?: number | null,
  height?: number | null,
): string | undefined {
  if (!hash || !isBlurhashValid(hash).result) return undefined
  const w = 8
  const h = Math.min(12, Math.max(4, Math.round((w * (height || 1)) / (width || 1))))
  return bitmap(decode(hash, w, h), w, h)
}

// A 24-bit Windows bitmap: the smallest image format every browser reads that needs no compression.
function bitmap(rgba: Uint8ClampedArray, w: number, h: number) {
  const stride = Math.ceil((w * 3) / 4) * 4
  const size = 54 + stride * h
  const bytes = new Uint8Array(size)
  const view = new DataView(bytes.buffer)
  bytes.set([0x42, 0x4d])
  view.setUint32(2, size, true)
  view.setUint32(10, 54, true)
  view.setUint32(14, 40, true)
  view.setInt32(18, w, true)
  view.setInt32(22, h, true)
  view.setUint16(26, 1, true)
  view.setUint16(28, 24, true)
  view.setUint32(34, stride * h, true)
  for (let y = 0; y < h; y++) {
    const row = 54 + (h - 1 - y) * stride
    for (let x = 0; x < w; x++) {
      const from = (y * w + x) * 4
      bytes[row + x * 3] = rgba[from + 2]
      bytes[row + x * 3 + 1] = rgba[from + 1]
      bytes[row + x * 3 + 2] = rgba[from]
    }
  }
  let binary = ''
  for (const byte of bytes) binary += String.fromCharCode(byte)
  return `data:image/bmp;base64,${btoa(binary)}`
}

// Camera settings as a photographer writes them: ƒ/2.8, 1/250 s, 50 mm, ISO 100.
const trim = (value: string) => value.replace(/\.0+$/, '').replace(/(\.\d*?)0+$/, '$1')
export const exposureSettings = (details: PhotoDetails | undefined) =>
  [
    { key: 'aperture', label: 'Aperture', value: details?.aperture ? `ƒ/${trim(details.aperture)}` : '' },
    { key: 'exposure', label: 'Shutter', value: details?.exposure ? `${details.exposure} s` : '' },
    {
      key: 'focal_length',
      label: 'Focal length',
      value: details?.focal_length ? `${trim(details.focal_length)} mm` : '',
    },
    { key: 'iso', label: 'ISO', value: details?.iso ? `ISO ${details.iso}` : '' },
  ].filter((setting) => setting.value)

// One row of the photo_details global, filled by the "Photo details from Unsplash" task.
export interface PhotoDetails {
  unsplash_id: string
  camera?: string | null
  aperture?: string | null
  exposure?: string | null
  focal_length?: string | null
  iso?: string | null
  location?: string | null
  latitude?: string | null
  longitude?: string | null
  tags?: string | null
}

export function detailsFor(rows: unknown, id: string | null | undefined): PhotoDetails | undefined {
  if (!id || !Array.isArray(rows)) return undefined
  return (rows as PhotoDetails[]).find((row) => row?.unsplash_id === id)
}
