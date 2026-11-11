import { isClient, onlyProjects, statusOf, type ProjectLike } from './projects'

export const STARTED = 2009
export const ANSWER_BACK = 'mah3uz · tty1 · since 2009'

export type Action =
  { theme: 'dark' | 'light' | 'toggle' } | { lamp: number } | { sound: boolean } | { scroll: 'past' | 'top' }

export interface Reply {
  lines: string[]
  clear?: boolean
  visit?: string
  action?: Action
}

export interface DeskPost {
  title: string | null
  uri: string | null
  published_at?: string | null
}

export interface Desk {
  projects: ProjectLike[]
  latest?: { title: string | null; uri: string | null } | null
  cols: number
  posts: DeskPost[]
  history: string[]
  lamp: number
  sound: boolean
  theme: 'dark' | 'light'
  now: Date
  random?: () => number
}

export const FORTUNES = [
  'own the whole path: build like someone who will have to operate it.',
  'fewer moving parts: choose proven, understood technology.',
  'fail safe, not silent: refuse loudly rather than continue wrongly.',
  'ship small, ship often: easy to verify, easy to undo.',
  'backups exist only if restores work.',
]

export const MANUAL: Record<string, string> = {
  help: 'list the commands, grouped.',
  ls: 'list my projects. -l adds stage, year and kind; "ls clients" lists client work.',
  cat: 'print a project\u2019s tagline, or "now" and "uses".',
  open: 'open a project or a page: work blog about now uses photos home.',
  cd: 'alias of open.',
  posts: 'the latest posts, numbered.',
  read: 'open post <n> from the posts list.',
  blog: 'print the latest post and open the blog.',
  git: '"git log" shows the latest posts as commits.',
  grep: 'projects whose title, tagline, kind or stack mentions the word.',
  which: 'projects that use a tool in their stack.',
  search: 'search the whole site.',
  theme: 'dark, light or toggle; alone, shows the current one.',
  mail: 'open the contact form.',
  lamp: 'on, off or 0-10; alone, shows the brightness.',
  sound: 'on or off; alone, shows the setting.',
  clear: 'clear the paper.',
  history: 'the commands typed this session.',
  exit: 'scroll down to the rest of the site.',
  logout: 'alias of exit.',
  whoami: 'who is at the keyboard.',
  uptime: 'how long, and what is building and shipped.',
  date: 'the date and time, in your time zone.',
  cal: 'this month, today marked.',
  uname: 'the system, such as it is.',
  pwd: 'the working directory.',
  hostname: 'the name of this machine.',
  echo: 'print the text as typed.',
  top: 'what is building right now.',
  fortune: 'one of the working principles.',
  man: 'one line on a command.',
  sudo: 'no.',
  rm: 'also no.',
  ping: 'send one packet, receive one lie.',
  pacman: 'arch, btw.',
  apt: 'wrong distro.',
  vim: 'there is only insert mode.',
  make: 'try "make coffee".',
}

const DAYS = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']
const MONTHS = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
const MONTH_NAMES = [
  'january',
  'february',
  'march',
  'april',
  'may',
  'june',
  'july',
  'august',
  'september',
  'october',
  'november',
  'december',
]
const PAGES: Record<string, string> = {
  work: '/projects',
  blog: '/blog',
  about: '/about',
  now: '/now',
  uses: '/uses',
  photos: '/photography',
  photography: '/photography',
}
const NBSP = '\u00a0'
const two = (n: number) => String(n).padStart(2, '0')
const slugOf = (project: ProjectLike) => project.uri?.split('/').filter(Boolean).pop() ?? ''

function hash(text: string) {
  let h = 0x811c9dc5
  for (let i = 0; i < text.length; i++) h = Math.imul(h ^ text.charCodeAt(i), 0x01000193)
  return h >>> 0
}

const dayMonth = (date: Date) => `${two(date.getDate())} ${MONTHS[date.getMonth()]}`

function offsetOf(date: Date) {
  const minutes = -date.getTimezoneOffset()
  const sign = minutes < 0 ? '-' : '+'
  const abs = Math.abs(minutes)
  return `${sign}${two(Math.floor(abs / 60))}${abs % 60 ? two(abs % 60) : ''}`
}

function calendar(now: Date) {
  const first = new Date(now.getFullYear(), now.getMonth(), 1)
  const days = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate()
  const lead = (first.getDay() + 6) % 7
  const cells = [...Array(lead).fill(0), ...Array.from({ length: days }, (_, i) => i + 1)]
  const title = `${MONTH_NAMES[now.getMonth()]} ${now.getFullYear()}`
  const rows = ['mo tu we th fr sa su']
  for (let i = 0; i < cells.length; i += 7) {
    const week = cells.slice(i, i + 7)
    let row = ''
    week.forEach((day, col) => {
      const mark = day === now.getDate()
      const after = col && week[col - 1] === now.getDate()
      row += (mark ? '[' : after ? ']' : col ? ' ' : NBSP) + (day ? String(day).padStart(2, ' ') : '  ')
    })
    if (week.at(-1) === now.getDate()) row += ']'
    rows.push(row.trimEnd())
  }
  return [title.padStart(Math.floor((22 + title.length) / 2), ' '), ...rows].map((line) => line.replace(/ /g, NBSP))
}

export function wrap(text: string, cols: number) {
  const lines: string[] = []
  let line = ''
  for (const [, gap, word] of text.matchAll(/( *)([^ ]+)/g)) {
    if (line && line.length + gap.length + word.length > cols) {
      lines.push(line)
      line = word
    } else line += (line ? gap : '') + word
  }
  return [...lines, line]
}

export function respond(input: string, desk: Desk): Reply {
  const command = input.trim().replace(/\s+/g, ' ')
  const lower = command.toLowerCase()
  const [name = '', ...rest] = lower.split(' ')
  const args = command.split(' ').slice(1)
  const arg = rest.join(' ')
  const everything = onlyProjects(desk.projects)
  const own = everything.filter((project) => !isClient(project))
  const clients = everything.filter(isClient)
  const posts = desk.posts.filter((post) => post.title)
  const say = (...lines: string[]) => ({ lines: lines.flatMap((line) => wrap(line, desk.cols)) })
  const fit = (line: string) => (line.length > desk.cols ? `${line.slice(0, desk.cols - 1)}\u2026` : line)
  const listing = (items: ProjectLike[]) =>
    items.map((project) =>
      `${statusOf(project).padEnd(10, NBSP)} ${project.year ?? '----'} ${slugOf(project)}/  ${project.kind ?? ''}`.trimEnd(),
    )
  const find = (wanted: string) =>
    everything.find((item) => slugOf(item) === wanted || item.title?.toLowerCase() === wanted)
  const dated = (post: DeskPost) => (post.published_at ? dayMonth(new Date(post.published_at)) : '-- ---')

  if (!command) return { lines: [] }
  if (lower === 'clear') return { lines: [], clear: true }
  if (lower === 'help')
    return say(
      'site: ls  open  cat  posts  read  grep  which  search  theme  mail',
      'desk: lamp  sound  clear  history  exit',
      `shell: whoami  uptime  date  cal  uname  pwd  echo  top  git${NBSP}log  fortune  man`,
    )
  if (name === 'man') {
    if (!arg) return say('what manual page do you want?')
    return say(MANUAL[arg] ? `${arg}: ${MANUAL[arg]}` : `no manual entry for ${arg}`)
  }
  if (lower === 'whoami') return say('mahfuz shaikh. software engineer and linux systems administrator, since 2009.')
  if (lower === 'uptime') {
    const count = (stage: string) => own.filter((project) => statusOf(project) === stage).length
    return say(
      `up ${desk.now.getFullYear() - STARTED} years. on linux since the first computer I used.`,
      `load average: ${count('building')} building, ${count('shipped')} shipped`,
    )
  }
  if (name === 'ls') {
    const long = rest.includes('-l')
    const target = rest.find((word) => !word.startsWith('-'))
    if (target === 'clients') {
      if (!clients.length) return say('ls: no clients')
      return {
        lines: (long ? listing(clients) : [clients.map((p) => `${slugOf(p)}/`).join('  ')]).flatMap((l) =>
          wrap(l, desk.cols),
        ),
      }
    }
    if (target) return say(`ls: cannot access '${target}': no such file or directory`)
    return long ? { lines: listing(own).map(fit) } : say(own.map((project) => `${slugOf(project)}/`).join('  '))
  }
  if (name === 'cat') {
    if (!arg) return say('cat: which file? try ls')
    if (arg === 'now')
      return say('building nibble towards 1.0. easyshot 0.1.0 shipped on 11 nov. sysman alerts are next.')
    if (arg === 'uses')
      return say(
        'rust ruby typescript \u00b7 linux systemd kamal \u00b7 sqlite postgres',
        'arch hyprland neovim ghostty \u00b7 a keychron k4',
      )
    const project = find(arg.replace(/\/$/, ''))
    return say(project ? (project.tagline ?? 'no tagline yet.') : `cat: ${arg}: no such file`)
  }
  if (lower === 'blog')
    return { ...say(desk.latest?.title ? `latest: ${desk.latest.title}` : 'nothing printed yet.'), visit: '/blog' }
  if (lower === 'mail') return { ...say('opening the contact form...'), visit: '/about#contact' }
  if (name === 'open' || name === 'cd') {
    const wanted = arg.replace(/\/$/, '')
    if (!wanted) return name === 'cd' ? { ...say('~'), action: { scroll: 'top' } } : say('open: which one? try ls')
    if (wanted === 'home' || wanted === '~') return { ...say('back to the top.'), action: { scroll: 'top' } }
    const project = find(wanted)
    if (project?.uri) return { ...say(`opening ${slugOf(project)}/ ...`), visit: project.uri }
    if (PAGES[wanted]) return { ...say(`opening ${wanted} ...`), visit: PAGES[wanted] }
    return say(`${name}: ${wanted}: no such project or page. try ls`)
  }
  if (name === 'posts') {
    if (!posts.length) return say('no posts yet.')
    return { lines: posts.map((post, i) => fit(`${i + 1}  ${dated(post)}  ${post.title}`)) }
  }
  if (name === 'read') {
    if (!arg) return say('read: which one? try posts')
    const post = /^\d+$/.test(arg) ? posts[Number(arg) - 1] : undefined
    if (!post?.uri) return say(`read: no post ${arg}`)
    return { ...say(`opening: ${post.title}`), visit: post.uri }
  }
  if (name === 'git') {
    if (rest[0] !== 'log') return say(`git: '${rest[0] ?? ''}' is not a git command here. try git log`)
    if (!posts.length) return say('fatal: your current branch has no commits yet')
    return {
      lines: posts.map((post) =>
        fit(
          `${hash(post.uri ?? post.title ?? '')
            .toString(16)
            .padStart(8, '0')
            .slice(0, 7)} ${dated(post)} ${post.title}`,
        ),
      ),
    }
  }
  if (name === 'grep') {
    if (!arg) return say('grep: usage: grep <word>')
    const hits = own.filter((project) =>
      [project.title, project.tagline, project.kind, ...(project.stack ?? [])].some((field) =>
        field?.toLowerCase().includes(arg),
      ),
    )
    if (!hits.length) return say('grep: no matches')
    return { lines: hits.map((project) => fit(`${slugOf(project)}/: ${project.tagline ?? ''}`)) }
  }
  if (name === 'which') {
    if (!arg) return say('which: which tool?')
    const hits = own.filter((project) => project.stack?.some((tool) => tool.toLowerCase().includes(arg)))
    return say(hits.length ? `${arg}: ${hits.map(slugOf).join(' ')}` : `which: no ${arg} in the stack`)
  }
  if (name === 'search') {
    if (!args.length) return say('search: for what?')
    return { ...say(`searching for ${args.join(' ')} ...`), visit: `/search?q=${encodeURIComponent(args.join(' '))}` }
  }
  if (name === 'theme') {
    if (!arg) return say(`theme: ${desk.theme}`)
    if (arg !== 'dark' && arg !== 'light' && arg !== 'toggle')
      return say(`theme: ${arg}: expected dark, light or toggle`)
    const next = arg === 'toggle' ? (desk.theme === 'dark' ? 'light' : 'dark') : arg
    return { ...say(`theme: ${next}`), action: { theme: arg } }
  }
  if (name === 'lamp') {
    if (!arg) return say(`lamp: ${desk.lamp}`)
    const level = arg === 'on' ? 7 : arg === 'off' ? 0 : /^\d+$/.test(arg) ? Number(arg) : -1
    if (level < 0 || level > 10) return say(`lamp: ${arg}: expected on, off or 0-10`)
    return { ...say(`lamp: ${level}`), action: { lamp: level } }
  }
  if (name === 'sound') {
    if (!arg) return say(`sound: ${desk.sound ? 'on' : 'off'}`)
    if (arg !== 'on' && arg !== 'off') return say(`sound: ${arg}: expected on or off`)
    return { ...say(`sound: ${arg}`), action: { sound: arg === 'on' } }
  }
  if (lower === 'history')
    return { lines: desk.history.map((entry, i) => fit(`${String(i + 1).padStart(3, NBSP)}  ${entry}`)) }
  if (name === 'exit' || name === 'logout')
    return { ...say('logout. the rest of the site is below.'), action: { scroll: 'past' } }
  if (lower === 'date') {
    const d = desk.now
    return say(
      `${DAYS[d.getDay()]} ${dayMonth(d)} ${d.getFullYear()} ${two(d.getHours())}:${two(d.getMinutes())}:${two(d.getSeconds())} ${offsetOf(d)}`,
    )
  }
  if (lower === 'cal') return { lines: calendar(desk.now) }
  if (name === 'uname') return say('linux mah3uz 17.0-since-2009 #1 smp typewriter x86_64 gnu/linux')
  if (lower === 'pwd') return say('/home/mahfuz')
  if (lower === 'hostname') return say('tty1')
  if (name === 'echo') return { lines: [args.join(' ')] }
  if (lower === 'top') {
    const rows = own
      .filter((project) => statusOf(project) === 'building')
      .map((project) => {
        const h = hash(slugOf(project))
        return `${String(1000 + (h % 9000)).padEnd(4)}  ${(((h >>> 12) % 1000) / 10).toFixed(1).padStart(4)}  ${slugOf(project)}`
      })
    return {
      lines: [`pid${NBSP}${NBSP}${NBSP}${NBSP}cpu${NBSP}${NBSP}command`, ...rows].map((l) => l.replace(/ /g, NBSP)),
    }
  }
  if (lower === 'fortune') {
    const pick = Math.floor((desk.random ?? Math.random)() * FORTUNES.length)
    return say(FORTUNES[Math.min(pick, FORTUNES.length - 1)])
  }
  if (name === 'sudo') return say('mahfuz is not in the sudoers file. this incident will be reported.')
  if (name === 'rm') return say('nice try.')
  if (['vim', 'vi', 'nano', 'emacs'].includes(name)) return say('this is a typewriter. there is only insert mode.')
  if (name === ':q' || name === ':wq' || name === ':q!') return say("you can't quit a typewriter.")
  if (name === 'pacman' || name === 'apt') return say('arch, btw. everything is up to date.')
  if (name === 'make')
    return say(arg === 'coffee' ? 'the mug is already full.' : `make: *** no rule to make target '${arg}'. stop.`)
  if (name === 'ping')
    return say(
      args[0] ? `64 bytes from ${args[0]}: icmp_seq=1 time=0.17 ms` : 'ping: usage error: destination required',
    )
  return say(`tty: ${name}: command not found. try help`)
}
