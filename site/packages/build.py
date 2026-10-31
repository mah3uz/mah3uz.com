"""Writes site/packages/default — the content this site starts from — as a Nibble content package.

The words live in Markdown files under site/packages/source/: one per page in pages/, one per post in posts/. Each has
YAML frontmatter for its fields; the text after it is the page's `content` (Markdown) or the post's `body` (converted
to the rich-text JSON Nibble stores). Edit those, then:

    python3 site/packages/build.py
    bin/rails nibble:content:validate site/packages/default
    bin/rails nibble:content:import site/packages/default                 # a fresh database
    bin/rails nibble:content:import site/packages/default --mode=update   # replace what's there with this

Once imported, the Control Plane owns the content; this is the seed, and the way to replace everything at once.
Post bodies use a small Markdown subset: ## and ### headings, paragraphs, - and 1. lists, ``` code, > quotes,
**bold**, *italic*, `code` and [links](url).
"""
import re
from pathlib import Path

import yaml

HERE = Path(__file__).parent
ROOT = HERE / 'default'
SOURCE = HERE / 'source'


# --------------------------------------------------------------------------- rich text

def inline(text):
    nodes = []
    pattern = re.compile(r'(\*\*(.+?)\*\*|`(.+?)`|\[(.+?)\]\((.+?)\)|\*(.+?)\*)')
    pos = 0
    for match in pattern.finditer(text):
        if match.start() > pos:
            nodes.append({'type': 'text', 'text': text[pos:match.start()]})
        if match.group(2):
            nodes.append({'type': 'text', 'text': match.group(2), 'marks': [{'type': 'bold'}]})
        elif match.group(3):
            nodes.append({'type': 'text', 'text': match.group(3), 'marks': [{'type': 'code'}]})
        elif match.group(4):
            nodes.append({'type': 'text', 'text': match.group(4),
                          'marks': [{'type': 'link', 'attrs': {'href': match.group(5)}}]})
        elif match.group(6):
            nodes.append({'type': 'text', 'text': match.group(6), 'marks': [{'type': 'italic'}]})
        pos = match.end()
    if pos < len(text):
        nodes.append({'type': 'text', 'text': text[pos:]})
    return nodes


def list_items(block, marker):
    """Split a list block into items, joining wrapped continuation lines onto their item."""
    items = []
    for line in block.split('\n'):
        match = re.match(marker, line)
        if match:
            items.append(line[match.end():])
        elif items:
            items[-1] += ' ' + line.strip()
    return items


def rich(markdown):
    doc = []
    for block in re.split(r'\n\s*\n', markdown.strip()):
        block = block.strip('\n')
        if block.startswith('```'):
            lines = block.split('\n')
            doc.append({'type': 'codeBlock', 'attrs': {'language': lines[0][3:].strip() or None},
                        'content': [{'type': 'text', 'text': '\n'.join(lines[1:-1])}]})
        elif block.startswith('### '):
            doc.append({'type': 'heading', 'attrs': {'level': 3}, 'content': inline(block[4:])})
        elif block.startswith('## '):
            doc.append({'type': 'heading', 'attrs': {'level': 2}, 'content': inline(block[3:])})
        elif block.startswith('> '):
            text = ' '.join(line[2:] for line in block.split('\n'))
            doc.append({'type': 'blockquote', 'content': [{'type': 'paragraph', 'content': inline(text)}]})
        elif block.startswith('- '):
            doc.append({'type': 'bulletList', 'content': [
                {'type': 'listItem', 'content': [{'type': 'paragraph', 'content': inline(item)}]}
                for item in list_items(block, r'- ')
            ]})
        elif re.match(r'\d+\. ', block):
            doc.append({'type': 'orderedList', 'attrs': {'start': 1}, 'content': [
                {'type': 'listItem', 'content': [{'type': 'paragraph', 'content': inline(item)}]}
                for item in list_items(block, r'\d+\. ')
            ]})
        else:
            doc.append({'type': 'paragraph', 'content': inline(' '.join(block.split('\n')))})
    return doc


# --------------------------------------------------------------------------- sources

def read(path):
    """A source file's frontmatter and the text after it."""
    text = path.read_text()
    match = re.match(r'---\n(.*?)\n---\n?(.*)', text, re.S)
    if not match:
        raise SystemExit(f'{path}: needs YAML frontmatter between --- lines')
    return yaml.safe_load(match.group(1)) or {}, match.group(2).strip()


def write(path, data):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=120))


# --------------------------------------------------------------------------- site settings

write('globals/site/en.yml', {
    'name': 'mah3uz',
    'tagline': 'Software engineer and Linux systems administrator since 2009 — building products, and running the '
               'infrastructure they depend on.',
    'social_links': [
        {'label': 'GitHub', 'url': 'https://github.com/mah3uz'},
        {'label': 'Unsplash', 'url': 'https://unsplash.com/@mah3uz'},
        {'label': 'Nibble', 'url': 'https://nibble.ink'},
        {'label': 'Darwan', 'url': 'https://darwan.dev'},
    ],
    'favicon': 'brand/favicon.svg',
})
write('globals/seo/en.yml', {
    'title_template': '{title} · {site_name}',
    'default_description': 'Mahfuz Shaikh (mah3uz): software engineer and Linux systems administrator since 2009, '
                           'building products and running production infrastructure.',
    'organization_name': 'mah3uz',
    'default_share_image': 'brand/social-card.png',
    'organization_logo': 'brand/favicon.svg',
})

# The files themselves sit in assets/brand/ beside this list; the import uploads them once.
write('assets.yml', [
    {'path': 'brand/favicon.svg', 'title': 'mah3uz mark', 'alt': 'The mah3uz mark: a teal tile with a peeled corner'},
    {'path': 'brand/social-card.png', 'title': 'Social card',
     'alt': 'mah3uz — software engineer and Linux systems administrator since 2009.'},
])

write('navigation/main/en.yml', {'tree': [
    {'url': '/projects', 'title': 'Work'},
    {'entry': 'pages/now', 'title': 'Now'},
    {'entry': 'pages/blog', 'title': 'Writing'},
    {'entry': 'pages/uses', 'title': 'Uses'},
    {'url': '/photography', 'title': 'Photography'},
    {'entry': 'pages/about', 'title': 'About'},
]})

# --------------------------------------------------------------------------- topics

TOPICS = {
    'engineering': ('Engineering', 'Architecture, trade-offs and the decisions behind software that lasts.'),
    'operations': ('Operations', 'Running software in production: Linux servers, deployments, backups and reliability.'),
    'security': ('Security', 'Least privilege, safe defaults and honest boundaries, from servers to AI agents.'),
    'rust': ('Rust', 'Building fast, dependable tools, daemons and desktop software in Rust.'),
    'linux': ('Linux', 'The Linux desktop and server, and making both a little better.'),
    'product': ('Product', 'Turning ideas into things people rely on.'),
}
for slug, (title, description) in TOPICS.items():
    write(f'taxonomies/topics/en/{slug}.yml', {'title': title, 'description': description})

# --------------------------------------------------------------------------- pages

PAGE_FIELDS = ['title', 'template', 'eyebrow', 'intro', 'art', 'cards', 'tools', 'milestones', 'seo']
for path in sorted((SOURCE / 'pages').glob('*.md')):
    front, body = read(path)
    page = {key: front[key] for key in PAGE_FIELDS if key in front}
    if body:
        page['content'] = body
    write(f'collections/pages/en/{path.stem}.yml', page)

# --------------------------------------------------------------------------- posts

for path in sorted((SOURCE / 'posts').glob('*.md')):
    front, body = read(path)
    write(f'collections/posts/en/{path.stem}.yml', {
        'title': front['title'],
        'published_at': front['published_at'].strftime('%Y-%m-%dT%H:%M:%SZ')
        if hasattr(front['published_at'], 'strftime') else front['published_at'],
        'topics': [f'topics/{topic}' for topic in front.get('topics', [])],
        'excerpt': front['excerpt'],
        'art': front.get('art'),
        'body': rich(body),
        **({'seo': front['seo']} if 'seo' in front else {}),
    })

print(f'wrote {sum(1 for _ in ROOT.rglob("*.yml"))} files to {ROOT.relative_to(HERE.parent.parent)}')
