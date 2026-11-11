import { beforeAll, describe, expect, it } from 'vitest'
import type { ProjectLike } from './projects'
import { FORTUNES, MANUAL, respond, wrap, type Desk } from './nightshift'

beforeAll(() => {
  process.env.TZ = 'Asia/Dhaka'
})

const project = (slug: string, extra: Partial<ProjectLike> = {}): ProjectLike => ({
  id: slug,
  title: slug.toUpperCase(),
  uri: `/projects/${slug}`,
  tagline: `${slug} tagline`,
  stage: { value: 'shipped' },
  category: { value: 'product' },
  kind: 'cli',
  year: '2026',
  stack: ['Rust'],
  ...extra,
})

const desk = (extra: Partial<Desk> = {}): Desk => ({
  projects: [
    { id: 'idx', title: 'Work', uri: '/projects' },
    project('easyshot', {
      title: 'easyshot',
      tagline: 'screenshots for linux',
      kind: 'desktop app',
      stack: ['Rust', 'Wayland'],
    }),
    project('nibble', {
      stage: { value: 'building' },
      year: '2025',
      kind: 'cms',
      tagline: 'a small cms',
      stack: ['Ruby', 'SQLite'],
    }),
    project('acme', {
      category: { value: 'client' },
      stage: { value: 'building' },
      year: '2024',
      kind: 'website',
      tagline: 'a client site',
      stack: ['Rails'],
    }),
  ],
  latest: { title: 'Post one', uri: '/blog/post-one' },
  cols: 80,
  posts: [
    { title: 'Post one', uri: '/blog/post-one', published_at: '2026-11-11T09:00:00+06:00' },
    { title: 'Post two', uri: '/blog/post-two', published_at: '2026-11-05T09:00:00+06:00' },
    { title: 'Post three', uri: '/blog/post-three', published_at: '2026-10-30T09:00:00+06:00' },
  ],
  history: ['help', 'ls'],
  lamp: 7,
  sound: true,
  theme: 'light',
  now: new Date(2026, 10, 11, 14, 5, 9),
  ...extra,
})

const run = (input: string, extra: Partial<Desk> = {}) => {
  const reply = respond(input, desk(extra))
  return { ...reply, lines: reply.lines.map((line) => line.replace(/ /g, ' ')) }
}

describe('basics', () => {
  it('prints nothing for an empty line, ignores extra spaces and case', () => {
    expect(run('   ').lines).toEqual([])
    expect(run('  PWD  ').lines).toEqual(['/home/mahfuz'])
    expect(run('  Open   NIBBLE ').visit).toBe('/projects/nibble')
  })
  it('wraps to the columns', () => {
    expect(wrap('aaa bbb ccc', 7)).toEqual(['aaa bbb', 'ccc'])
  })
  it('reports unknown commands', () => {
    expect(run('frobnicate now').lines).toEqual(['tty: frobnicate: command not found. try help'])
  })
  it('clear clears', () => {
    expect(run('clear')).toEqual({ lines: [], clear: true })
  })
})

describe('help and man', () => {
  it('groups the commands in three lines', () => {
    expect(run('help').lines).toEqual([
      'site: ls  open  cat  posts  read  grep  which  search  theme  mail',
      'desk: lamp  sound  clear  history  exit',
      'shell: whoami  uptime  date  cal  uname  pwd  echo  top  git log  fortune  man',
    ])
  })
  it('man describes every command it lists in help', () => {
    const listed =
      'ls open cat posts read grep which search theme mail lamp sound clear history exit whoami uptime date cal uname pwd echo top fortune man'
    for (const command of listed.split(' ')) expect(run(`man ${command}`).lines.join(' ')).toContain(MANUAL[command])
    expect(run('man ls').lines[0]).toMatch(/^ls: list my projects/)
  })
  it('man for an unknown command', () => {
    expect(run('man xyzzy').lines).toEqual(['no manual entry for xyzzy'])
    expect(run('man').lines).toEqual(['what manual page do you want?'])
  })
})

describe('whoami, uptime', () => {
  it('whoami', () => {
    expect(run('whoami').lines.join(' ')).toContain('mahfuz shaikh. software engineer and linux systems administrator')
  })
  it('uptime counts years since 2009 and own projects by stage (clients excluded)', () => {
    const projects = [
      project('a'),
      project('b'),
      project('c'),
      project('d', { stage: { value: 'building' } }),
      project('e', { stage: { value: 'experiment' } }),
      project('f', { category: { value: 'client' }, stage: { value: 'building' } }),
    ]
    expect(run('uptime', { projects }).lines).toEqual([
      'up 17 years. on linux since the first computer I used.',
      'load average: 1 building, 3 shipped',
    ])
  })
})

describe('ls', () => {
  it('lists own projects as slugs', () => {
    expect(run('ls').lines).toEqual(['easyshot/  nibble/'])
  })
  it('ls -l pads the stage and shows year, slug and kind', () => {
    expect(run('ls -l').lines).toEqual(['shipped    2026 easyshot/  desktop app', 'building   2025 nibble/  cms'])
  })
  it('ls clients lists client work, in short and long form', () => {
    expect(run('ls clients').lines).toEqual(['acme/'])
    expect(run('ls -l clients').lines).toEqual(['building   2024 acme/  website'])
    expect(run('ls clients', { projects: [] }).lines).toEqual(['ls: no clients'])
  })
  it('ls of something else fails', () => {
    expect(run('ls nowhere').lines).toEqual(["ls: cannot access 'nowhere': no such file or directory"])
  })
})

describe('cat', () => {
  it('prints a project tagline by slug, title or with a trailing slash', () => {
    expect(run('cat nibble').lines).toEqual(['a small cms'])
    expect(run('cat EasyShot/').lines).toEqual(['screenshots for linux'])
    expect(run('cat acme').lines).toEqual(['a client site'])
  })
  it('keeps now and uses', () => {
    expect(run('cat now').lines.join(' ')).toContain('building nibble towards 1.0')
    expect(run('cat uses').lines.join(' ')).toContain('keychron k4')
  })
  it('fails for unknown files and a missing name', () => {
    expect(run('cat ghost').lines).toEqual(['cat: ghost: no such file'])
    expect(run('cat').lines).toEqual(['cat: which file? try ls'])
  })
})

describe('open and cd', () => {
  it('opens a project', () => {
    const reply = run('open easyshot/')
    expect(reply.visit).toBe('/projects/easyshot')
    expect(reply.lines).toEqual(['opening easyshot/ ...'])
  })
  it.each([
    ['work', '/projects'],
    ['blog', '/blog'],
    ['about', '/about'],
    ['now', '/now'],
    ['uses', '/uses'],
    ['photos', '/photography'],
    ['photography', '/photography'],
  ])('opens the %s page', (page, url) => {
    expect(run(`open ${page}`).visit).toBe(url)
    expect(run(`cd ${page}`).visit).toBe(url)
  })
  it('home and ~ scroll to the top without a visit', () => {
    for (const where of ['open home', 'open ~', 'cd home', 'cd']) {
      const reply = run(where)
      expect(reply.action).toEqual({ scroll: 'top' })
      expect(reply.visit).toBeUndefined()
    }
  })
  it('errors', () => {
    expect(run('open ghost').lines).toEqual(['open: ghost: no such project or page. try ls'])
    expect(run('cd ghost').lines).toEqual(['cd: ghost: no such project or page. try ls'])
    expect(run('open').lines).toEqual(['open: which one? try ls'])
  })
})

describe('posts, read, blog, git log', () => {
  it('posts numbers the latest posts with day and month', () => {
    expect(run('posts').lines).toEqual(['1  11 nov  Post one', '2  05 nov  Post two', '3  30 oct  Post three'])
    expect(run('posts', { posts: [] }).lines).toEqual(['no posts yet.'])
  })
  it('read opens the numbered post', () => {
    expect(run('read 2').visit).toBe('/blog/post-two')
    expect(run('read 2').lines).toEqual(['opening: Post two'])
  })
  it('read errors', () => {
    expect(run('read 9').lines).toEqual(['read: no post 9'])
    expect(run('read 0').lines).toEqual(['read: no post 0'])
    expect(run('read x').lines).toEqual(['read: no post x'])
    expect(run('read').lines).toEqual(['read: which one? try posts'])
  })
  it('blog prints the latest and visits /blog', () => {
    expect(run('blog')).toMatchObject({ lines: ['latest: Post one'], visit: '/blog' })
    expect(run('blog', { latest: null }).lines).toEqual(['nothing printed yet.'])
  })
  it('git log prints posts as commits with a stable 7-character hash', () => {
    const lines = run('git log --oneline').lines
    expect(lines).toHaveLength(3)
    expect(lines[0]).toMatch(/^[0-9a-f]{7} 11 nov Post one$/)
    expect(lines[2]).toMatch(/^[0-9a-f]{7} 30 oct Post three$/)
    expect(run('git log').lines).toEqual(lines)
    expect(lines[0].slice(0, 7)).not.toBe(lines[1].slice(0, 7))
  })
  it('git errors', () => {
    expect(run('git push').lines).toEqual(["git: 'push' is not a git command here. try git log"])
    expect(run('git log', { posts: [] }).lines).toEqual(['fatal: your current branch has no commits yet'])
  })
})

describe('grep and which', () => {
  it('grep matches title, tagline, kind and stack of own projects only', () => {
    expect(run('grep screenshots').lines).toEqual(['easyshot/: screenshots for linux'])
    expect(run('grep CMS').lines).toEqual(['nibble/: a small cms'])
    expect(run('grep wayland').lines).toEqual(['easyshot/: screenshots for linux'])
    expect(run('grep tagline').lines).toEqual(['grep: no matches'])
    expect(run('grep client').lines).toEqual(['grep: no matches'])
  })
  it('grep truncates to the columns', () => {
    expect(run('grep screenshots', { cols: 20 }).lines).toEqual(['easyshot/: screensh…'])
  })
  it('grep needs a word', () => {
    expect(run('grep').lines).toEqual(['grep: usage: grep <word>'])
  })
  it('which lists projects whose stack has the tool', () => {
    expect(run('which rust').lines).toEqual(['rust: easyshot'])
    expect(run('which SQL').lines).toEqual(['sql: nibble'])
    expect(run('which cobol').lines).toEqual(['which: no cobol in the stack'])
    expect(run('which').lines).toEqual(['which: which tool?'])
  })
})

describe('search and mail', () => {
  it('search visits the encoded query', () => {
    expect(run('search Rust & more').visit).toBe('/search?q=Rust%20%26%20more')
    expect(run('search').lines).toEqual(['search: for what?'])
  })
  it('mail opens the contact form', () => {
    expect(run('mail')).toMatchObject({ visit: '/about#contact' })
  })
})

describe('theme, lamp, sound', () => {
  it('theme alone shows the current one', () => {
    expect(run('theme').lines).toEqual(['theme: light'])
    expect(run('theme', { theme: 'dark' }).lines).toEqual(['theme: dark'])
  })
  it('theme sets, and toggle prints the opposite', () => {
    expect(run('theme dark')).toMatchObject({ lines: ['theme: dark'], action: { theme: 'dark' } })
    expect(run('theme light')).toMatchObject({ lines: ['theme: light'], action: { theme: 'light' } })
    expect(run('theme toggle')).toMatchObject({ lines: ['theme: dark'], action: { theme: 'toggle' } })
    expect(run('theme toggle', { theme: 'dark' }).lines).toEqual(['theme: light'])
  })
  it('theme rejects other values without an action', () => {
    const reply = run('theme purple')
    expect(reply.lines).toEqual(['theme: purple: expected dark, light or toggle'])
    expect(reply.action).toBeUndefined()
  })
  it('lamp', () => {
    expect(run('lamp').lines).toEqual(['lamp: 7'])
    expect(run('lamp on')).toMatchObject({ lines: ['lamp: 7'], action: { lamp: 7 } })
    expect(run('lamp off')).toMatchObject({ lines: ['lamp: 0'], action: { lamp: 0 } })
    expect(run('lamp 3').action).toEqual({ lamp: 3 })
    expect(run('lamp 10').action).toEqual({ lamp: 10 })
  })
  it('lamp errors', () => {
    for (const bad of ['11', '-1', 'x', '2.5']) {
      const reply = run(`lamp ${bad}`)
      expect(reply.lines).toEqual([`lamp: ${bad}: expected on, off or 0-10`])
      expect(reply.action).toBeUndefined()
    }
  })
  it('sound', () => {
    expect(run('sound').lines).toEqual(['sound: on'])
    expect(run('sound', { sound: false }).lines).toEqual(['sound: off'])
    expect(run('sound off')).toMatchObject({ lines: ['sound: off'], action: { sound: false } })
    expect(run('sound on').action).toEqual({ sound: true })
    expect(run('sound loud').lines).toEqual(['sound: loud: expected on or off'])
  })
})

describe('history, exit', () => {
  it('history numbers the session commands', () => {
    expect(run('history').lines).toEqual(['  1  help', '  2  ls'])
    expect(run('history', { history: [] }).lines).toEqual([])
  })
  it('exit and logout scroll past the hero', () => {
    for (const word of ['exit', 'logout']) {
      expect(run(word)).toMatchObject({
        lines: ['logout. the rest of the site is below.'],
        action: { scroll: 'past' },
      })
    }
  })
})

describe('shell commands', () => {
  it('date uses the date and its own offset', () => {
    expect(run('date').lines).toEqual(['wed 11 nov 2026 14:05:09 +06'])
  })
  it('cal draws the month with today bracketed and every line within the columns', () => {
    const lines = run('cal').lines
    expect(lines[0].trim()).toBe('november 2026')
    expect(lines[1].trim()).toBe('mo tu we th fr sa su')
    expect(lines[2].trim()).toBe('1')
    expect(lines[3].trim()).toBe('2  3  4  5  6  7  8')
    expect(lines.find((line) => line.includes('['))).toContain('[11]')
    expect(lines.filter((line) => line.includes('[')).length).toBe(1)
    expect(lines.find((line) => line.includes('['))).toBe('  9 10[11]12 13 14 15')
    expect(lines.slice(1).every((line) => line.length <= 23)).toBe(true)
    expect(lines.at(-1)).toContain('30')
  })
  it('uname, pwd, hostname', () => {
    expect(run('uname').lines).toEqual(['linux mah3uz 17.0-since-2009 #1 smp typewriter x86_64 gnu/linux'])
    expect(run('uname -a').lines).toEqual(run('uname').lines)
    expect(run('pwd').lines).toEqual(['/home/mahfuz'])
    expect(run('hostname').lines).toEqual(['tty1'])
  })
  it('echo keeps the case and arguments', () => {
    expect(run('ECHO  Hello   World').lines).toEqual(['Hello World'])
    expect(run('echo').lines).toEqual([''])
  })
  it('top lists only building own projects with stable numbers', () => {
    const lines = run('top').lines
    expect(lines[0]).toBe('pid    cpu  command')
    expect(lines).toHaveLength(2)
    expect(lines[1]).toMatch(/^\d{4} {2} {0,2}\d{1,2}\.\d {2}nibble$/)
    expect(run('top').lines).toEqual(lines)
    expect(run('top', { projects: [] }).lines).toEqual(['pid    cpu  command'])
  })
  it('fortune picks a principle from the random source', () => {
    expect(run('fortune', { random: () => 0 }).lines.join(' ')).toBe(FORTUNES[0])
    expect(run('fortune', { random: () => 0.99999 }).lines.join(' ')).toBe(FORTUNES[4])
    expect(FORTUNES).toHaveLength(5)
  })
})

describe('fun', () => {
  it.each([
    ['sudo rm -rf /', 'mahfuz is not in the sudoers file. this incident will be reported.'],
    ['rm file', 'nice try.'],
    ['vim x', 'this is a typewriter. there is only insert mode.'],
    ['vi', 'this is a typewriter. there is only insert mode.'],
    ['nano', 'this is a typewriter. there is only insert mode.'],
    ['emacs', 'this is a typewriter. there is only insert mode.'],
    [':q', "you can't quit a typewriter."],
    [':wq', "you can't quit a typewriter."],
    ['pacman -syu', 'arch, btw. everything is up to date.'],
    ['pacman -s foo', 'arch, btw. everything is up to date.'],
    ['apt install foo', 'arch, btw. everything is up to date.'],
    ['make coffee', 'the mug is already full.'],
    ['make tea', "make: *** no rule to make target 'tea'. stop."],
    ['ping example.com', '64 bytes from example.com: icmp_seq=1 time=0.17 ms'],
    ['ping', 'ping: usage error: destination required'],
  ])('%s', (input, out) => {
    expect(run(input).lines).toEqual([out])
  })
})
