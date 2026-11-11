import type { AssetValue } from '@site/types'

export type Status = 'building' | 'shipped' | 'experiment' | 'archived'

export interface ProjectLike {
  id: number | string
  title: string | null
  uri: string | null
  slug?: string | null
  tagline?: string | null
  description?: string | null
  stage?: { value: string | null; label?: string | null } | null
  category?: { value: string | null; label?: string | null } | null
  client?: string | null
  role?: string | null
  kind?: string | null
  year?: string | null
  monogram?: string | null
  logo?: AssetValue | null
  accent?: string | null
  featured?: boolean | null
  stack?: string[] | null
  cover?: AssetValue | null
  website?: string | null
  repository?: string | null
}

export const STATUS_COPY: Record<Status, { label: string; note: string }> = {
  building: { label: 'Building', note: 'In the workshop right now' },
  shipped: { label: 'Shipped', note: 'Out in the world' },
  experiment: { label: 'Experiment', note: 'Poking at an idea' },
  archived: { label: 'Archived', note: 'Done, kept for reference' },
}

export const statusOf = (project: ProjectLike): Status => (project.stage?.value as Status) ?? 'building'

/** The index page of the folder is a page of the collection too; listings only want the projects under it. */
export const onlyProjects = <T extends ProjectLike>(items: T[]) =>
  items.filter((item) => item.uri?.split('/').length === 3)

export const hostOf = (url: string) => url.replace(/^https?:\/\//, '').replace(/\/$/, '')

export const isClient = (project: ProjectLike) => project.category?.value === 'client'

/** Status words read differently for someone else's product: work is ongoing or delivered, not "building". */
export function statusLabel(project: ProjectLike) {
  const status = statusOf(project)
  if (isClient(project))
    return status === 'building' ? 'Ongoing' : status === 'shipped' ? 'Delivered' : STATUS_COPY[status].label
  return STATUS_COPY[status].label
}
