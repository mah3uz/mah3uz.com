<script setup lang="ts">
import { Head } from '@inertiajs/vue3'
import { PreviewBar, SeoHead } from '@nibble'
import type { LayoutProps } from '@site/types'
import SiteFooter from '../components/SiteFooter.vue'
import SiteHeader from '../components/SiteHeader.vue'
import { onlyProjects } from '../lib/projects'

const props = defineProps<LayoutProps['default']>()
</script>

<template>
  <div class="neat-backdrop font-body text-ink relative min-h-svh overflow-x-clip antialiased">
    <Head>
      <link head-key="fonts-preconnect" rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
      <link
        head-key="fonts"
        rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&family=Manrope:wght@600;700;800&display=swap"
      />
      <meta head-key="theme-color-light" name="theme-color" content="#F3FCFA" media="(prefers-color-scheme: light)" />
      <meta head-key="theme-color-dark" name="theme-color" content="#0A1A20" media="(prefers-color-scheme: dark)" />
    </Head>
    <SeoHead />
    <PreviewBar />
    <a href="#main" class="bg-ink text-canvas absolute -top-24 left-4 z-[70] rounded-full px-5 py-3 focus:top-4"
      >Skip to content</a
    >
    <SiteHeader :projects="onlyProjects(props.palette ?? [])" />
    <main id="main" tabindex="-1" class="relative isolate mx-auto max-w-6xl px-5 pt-10 outline-none sm:px-8 lg:pt-16">
      <slot />
    </main>
    <SiteFooter />
  </div>
</template>
