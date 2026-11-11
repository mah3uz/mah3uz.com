<script setup lang="ts">
// What else is on the desk: the on-call pager, a mug going cold, the note card with the hints, and the pile of
// finished sheets, which holds the latest writing. Hovering or focusing a sheet lifts it into the reader; a click
// opens the post.
import { Link } from '@inertiajs/vue3'
import { useSite } from '@nibble'
import { ref } from 'vue'
import { formatDate } from '../../lib/format'
import { S, wake } from '../../lib/nightshift-sound'

type Post = {
  id: number | string
  title: string | null
  uri: string | null
  excerpt?: string | null
  published_at?: string | null
}
const props = defineProps<{ posts: Post[] }>()

const site = useSite()
const acked = ref(false)
const reading = ref<Post | null>(null)
const FAN = [
  [-4.2, -5, 3],
  [2.8, 6, -3],
  [-1.4, -2, -9],
]

function ack() {
  if (acked.value) return
  acked.value = true
  wake()
  S.beep()
}
const day = (value?: string | null) =>
  formatDate(value, { day: '2-digit', month: 'short', year: 'numeric' }, 'en-GB', site.value?.time_zone).toLowerCase()
const sheets = () => [...props.posts].reverse()

// The hit area of each sheet never moves; only the paper inside it lifts. A short delay keeps a pass of the pointer
// from flicking the reader open and shut.
let hover = 0
function enter(post: Post) {
  window.clearTimeout(hover)
  hover = window.setTimeout(() => (reading.value = post), 120)
}
function leave() {
  window.clearTimeout(hover)
  hover = window.setTimeout(() => (reading.value = null), 90)
}
</script>

<template>
  <div class="ns-props">
    <button
      type="button"
      class="ns-prop ns-pager"
      :class="{ 'is-acked': acked }"
      :aria-label="acked ? 'On-call pager, acknowledged' : 'On-call pager: /var at 91% at 03:12. Acknowledge'"
      :aria-pressed="acked"
      @click="ack"
    >
      <span class="ns-pager-top" aria-hidden="true">
        <span>On call</span>
        <span class="ns-pager-led" />
      </span>
      <span class="ns-pager-lcd" aria-hidden="true">
        <template v-if="acked">acked.<br />back to sleep.</template>
        <template v-else>03:12 /var 91%<br />ack?</template>
      </span>
      <span class="ns-pager-keys" aria-hidden="true"><i /><i /></span>
    </button>

    <div class="ns-prop ns-mug" aria-hidden="true">
      <div class="ns-steam">
        <span v-for="wisp in 6" :key="wisp" class="ns-wisp" :style="{ '--ns-wisp': wisp }"><i /></span>
      </div>
      <span class="ns-mug-handle" />
      <span class="ns-mug-cup" />
    </div>

    <aside class="ns-prop ns-card">
      <p>type something.<br />return sends it.<br />try <b>help</b>.</p>
      <p class="ns-card-sm">tab jumps to the stops.<br />the paper keeps everything.<br />hover the pile to read it.</p>
    </aside>

    <nav v-if="posts.length" class="ns-prop ns-pile" aria-label="Finished sheets: my latest writing">
      <Link
        v-for="(post, index) in sheets()"
        :key="post.id"
        :href="post.uri ?? '/blog'"
        class="ns-psheet-hit"
        :class="{ 'is-reading': reading === post }"
        :style="{ '--r': `${FAN[index % 3][0]}deg`, '--ox': `${FAN[index % 3][1]}%`, '--oy': `${FAN[index % 3][2]}%` }"
        @pointerenter="enter(post)"
        @pointerleave="leave"
        @focus="enter(post)"
        @blur="leave"
      >
        <span class="ns-psheet">
          <span class="ns-psheet-date">{{ day(post.published_at) }}</span>
          <span class="ns-psheet-title">{{ post.title }}</span>
        </span>
      </Link>
      <Link href="/blog" class="ns-pile-all">read them all →</Link>
    </nav>

    <div class="ns-reader" :class="{ 'is-on': reading }" aria-hidden="true">
      <template v-if="reading">
        <p class="ns-reader-date">{{ day(reading.published_at) }}</p>
        <p class="ns-reader-title">{{ reading.title }}</p>
        <p v-if="reading.excerpt" class="ns-reader-text">{{ reading.excerpt }}</p>
        <p class="ns-reader-more">click the sheet to read it →</p>
      </template>
    </div>
  </div>
</template>
