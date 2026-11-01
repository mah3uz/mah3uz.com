// Unsplash asks that its images be hot-linked from images.unsplash.com and resized with URL parameters, and that
// links back to Unsplash carry its referral parameters (https://unsplash.com/documentation).
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
