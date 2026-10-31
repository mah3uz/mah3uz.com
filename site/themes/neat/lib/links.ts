import { Link } from '@inertiajs/vue3'

export const onSite = (url: string) => /^\/(?![/\\])/.test(url)

// Inertia fetches a <Link> with XHR, which the browser blocks for another origin, so off-site addresses need a plain <a>.
export const linkTag = (url: string) => (onSite(url) ? Link : 'a')

/** The site settings' social links, as label and address pairs a template can rely on. */
export const socialLinks = (rows: Record<string, unknown>[] | null | undefined) =>
  (rows ?? [])
    .map((row) => ({ label: String(row.label ?? ''), url: String(row.url ?? '') }))
    .filter((row) => row.label && row.url)
