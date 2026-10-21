"""Generate every static SVG used by the profile README, in GitHub dark and light.

    python scripts/build.py

Writes to assets/. Each asset `x.svg` has a light twin `x-light.svg`.
"""

import re
from pathlib import Path

from theme import (LANG, THEMES, draw_line, esc, icon, kt, svg, text_width,
                   window_opacity)

OUT = Path(__file__).resolve().parent.parent / "assets"


def check_keytimes(name, content):
    """Browsers silently drop a SMIL animation whose keyTimes are malformed."""
    for tag in re.findall(r"<animate[^>]*>", content):
        times = re.search(r'keyTimes="([^"]+)"', tag)
        values = re.search(r'values="([^"]+)"', tag)
        if not times:
            continue
        ts = [float(x) for x in times.group(1).split(";")]
        problems = []
        if values and len(values.group(1).split(";")) != len(ts):
            problems.append("values/keyTimes length mismatch")
        if ts[0] != 0 or any(b < a for a, b in zip(ts, ts[1:])):
            problems.append("keyTimes must start at 0 and never decrease")
        if 'calcMode="discrete"' not in tag and ts[-1] != 1:
            problems.append("keyTimes must end at 1")
        if problems:
            raise ValueError(f"{name}: {', '.join(problems)}: {tag[:160]}")


def write(name, theme, content):
    check_keytimes(name, content)
    suffix = "" if theme["name"] == "dark" else "-light"
    (OUT / f"{name}{suffix}.svg").write_text(content, encoding="utf-8")


# --------------------------------------------------------------------------- hero

COMMITS = [
    ("feat: ship REST APIs with FastAPI", "3f9a2c1"),
    ("feat: orchestrate agents with LangGraph", "b71e04d"),
    ("ci: test every push with GitHub Actions", "0c5d9ae"),
    ("build: containerise services with Docker", "e42b8f7"),
    ("fix: make it reliable, then make it fast", "9d13c60"),
]


def typed_commits(t, x, baseline, total, slot):
    """Commit messages that type out, get a SHA and a green check, then roll over."""
    cw, size = 8.4, 14
    out = []
    for i, (msg, sha) in enumerate(COMMITS):
        s = i * slot
        type_start, step = s + 0.25, 0.042
        type_end = type_start + len(msg) * step
        end = s + slot - 0.3
        width = len(msg) * cw
        values, times = ["0", "0"], [0, type_start]
        for k in range(1, len(msg) + 1):
            values.append(f"{k * cw:.1f}")
            times.append(type_start + k * step)
        values.append("0")
        times.append(end + 0.25)
        clip_id = f"type{i}"
        out.append(
            f'<clipPath id="{clip_id}"><rect x="{x}" y="{baseline - 18}" height="26" width="0">'
            f'<animate attributeName="width" values="{";".join(values)}" keyTimes="{kt(times, total)}" '
            f'calcMode="discrete" dur="{total}s" repeatCount="indefinite"/></rect></clipPath>'
        )
        caret_x = ";".join(str(x + float(v) + 1) for v in values)
        out.append(f'<g opacity="0">{window_opacity(s + 0.05, end, total)}')
        out.append(
            f'<g clip-path="url(#{clip_id})"><text x="{x}" y="{baseline}" class="mono" font-size="{size}" '
            f'fill="{t["fg"]}" textLength="{width:.1f}" lengthAdjust="spacing">{esc(msg)}</text></g>'
        )
        out.append(
            f'<rect y="{baseline - 14}" width="2" height="18" fill="{t["accent"]}" x="{x}" opacity="0">'
            f'<animate attributeName="x" values="{caret_x}" keyTimes="{kt(times, total)}" calcMode="discrete" '
            f'dur="{total}s" repeatCount="indefinite"/>'
            f'{window_opacity(type_start - 0.1, type_end + 0.15, total, fade=0.05)}</rect>'
        )
        out.append(
            f'<g opacity="0">{window_opacity(type_end + 0.2, end, total, fade=0.2)}'
            f'<text x="602" y="{baseline}" class="mono" font-size="13" fill="{t["muted"]}">{sha}</text>'
            f'<circle cx="676" cy="{baseline - 5}" r="9" fill="{t["green"]}" fill-opacity=".15"/>'
            f'{icon("check", 668.5, baseline - 12.5, t["green"], size=15, width=2)}'
            f'</g></g>'
        )
    return "\n".join(out)


def git_graph(t, total=12.0):
    """A branch-and-merge history that draws itself along a moving main line."""
    y_main, x0, x1 = 222, 760, 1160
    draw_end, hold_end = 6.4, 10.4

    def t_at(x):
        return 0.15 + (x - x0) / (x1 - x0) * (draw_end - 0.15)

    branches = [
        # name, colour, fork x, merge x, lane y, commit xs
        ("feat/rest-api", t["blue"], 790, 950, 150, [850, 905]),
        ("feat/agents", t["green"], 870, 1080, 296, [925, 985, 1040]),
        ("ci/actions", t["yellow"], 985, 1115, 150, [1045]),
    ]
    parts = [f'<g opacity="1">'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="{kt([0, hold_end, hold_end + .8, total], total)}" '
             f'dur="{total}s" repeatCount="indefinite"/>']

    # main line: a faint track plus the drawn history
    parts.append(f'<path d="M{x0} {y_main}H{x1}" stroke="{t["border"]}" stroke-width="2" stroke-dasharray="2 6"/>')
    parts.append(
        f'<path d="M{x0} {y_main}H{x1}" stroke="{t["accent"]}" stroke-width="3" stroke-linecap="round" '
        f'pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1">'
        f'<animate attributeName="stroke-dashoffset" values="1;1;0;0;1" '
        f'keyTimes="{kt([0, .15, draw_end, hold_end + .8, total], total)}" dur="{total}s" repeatCount="indefinite"/></path>'
    )

    dots, rings, labels = [], [], []
    for name, color, fx, mx, ly, commits in branches:
        up = ly < y_main
        d = (f"M{fx} {y_main}C{fx + 26} {y_main} {fx + 14} {ly} {fx + 40} {ly}"
             f"H{mx - 40}C{mx - 14} {ly} {mx - 26} {y_main} {mx} {y_main}")
        ts, te = t_at(fx), t_at(mx)
        parts.append(
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round" '
            f'pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1">{draw_line(ts, te, total, hold_end + .8)}</path>'
        )
        for cx in commits:
            tc = ts + (cx - fx) / (mx - fx) * (te - ts)
            dots.append((cx, ly, color, tc, False))
        dots.append((mx, y_main, t["accent"], te, True))
        lw = text_width(name, 11, mono=True) + 16
        ly_label = ly - 26 if up else ly + 14
        labels.append(
            f'<g opacity="0">{window_opacity(ts + .3, hold_end, total, fade=.4)}'
            f'<rect x="{fx + 36}" y="{ly_label}" width="{lw:.0f}" height="20" rx="10" fill="{t["canvas"]}" '
            f'stroke="{color}" stroke-opacity=".55"/>'
            f'<text x="{fx + 44}" y="{ly_label + 14}" class="mono" font-size="11" fill="{color}">{name}</text></g>'
        )

    dots.insert(0, (x0 + 10, y_main, t["accent"], .2, False))
    dots.append((1150, y_main, t["accent"], draw_end - .1, True))

    for cx, cy, color, tc, merge in dots:
        r = 7 if merge else 5.5
        parts.append(
            f'<circle cx="{cx}" cy="{cy}" r="0" fill="{color}" stroke="{t["canvas"]}" stroke-width="3">'
            f'<animate attributeName="r" values="0;0;{r + 2.5};{r};{r};0" '
            f'keyTimes="{kt([0, tc, tc + .18, tc + .32, hold_end + .8, total], total)}" dur="{total}s" repeatCount="indefinite"/>'
            f'</circle>'
        )
        if merge:
            rings.append(
                f'<circle cx="{cx}" cy="{cy}" r="7" fill="none" stroke="{t["accent"]}" stroke-width="2" opacity="0">'
                f'<animate attributeName="r" values="7;7;24;24" keyTimes="{kt([0, tc, tc + 1, total], total)}" dur="{total}s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="0;0;.8;0;0" keyTimes="{kt([0, tc - .01, tc + .02, tc + 1, total], total)}" dur="{total}s" repeatCount="indefinite"/>'
                f'</circle>'
            )

    # packets flowing along main once the history exists
    packets = []
    for k in range(3):
        packets.append(
            f'<circle r="3" fill="{t["accent_soft"]}"><animateMotion path="M{x0} {y_main}H{x1}" dur="2.4s" '
            f'begin="{-k * .8:.1f}s" repeatCount="indefinite"/></circle>'
        )
    parts.append(
        f'<g opacity="0">{window_opacity(draw_end, hold_end, total, fade=.4)}{"".join(packets)}</g>'
    )
    parts.extend(rings)
    parts.extend(labels)
    # HEAD pointer
    head = (
        f'<g opacity="0">{window_opacity(draw_end, hold_end, total, fade=.3)}'
        f'<rect x="1078" y="{y_main + 16}" width="98" height="22" rx="11" fill="{t["accent"]}" fill-opacity=".14" '
        f'stroke="{t["accent"]}" stroke-opacity=".6"/>'
        f'<text x="1127" y="{y_main + 31}" text-anchor="middle" class="mono" font-size="11" fill="{t["accent_soft"]}">'
        f'HEAD → main</text></g>'
    )
    return "\n".join(parts) + "\n" + head + "\n</g>"


def hero(t):
    W, H = 1200, 400
    total = 20.0
    slot = total / len(COMMITS)
    body = f"""
<defs>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="12"/></clipPath>
  <radialGradient id="glowA"><stop offset="0" stop-color="{t['accent']}" stop-opacity="{t['glow_op']}"/><stop offset="1" stop-color="{t['accent']}" stop-opacity="0"/></radialGradient>
  <radialGradient id="glowB"><stop offset="0" stop-color="{t['blue']}" stop-opacity="{t['glow_op']}"/><stop offset="1" stop-color="{t['blue']}" stop-opacity="0"/></radialGradient>
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.1" fill="{t['dot']}"/></pattern>
  <radialGradient id="fade" cx=".78" cy=".55" r=".55"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
  <mask id="dotmask"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
  <linearGradient id="shine" x1="0" y1="0" x2="640" y2="0" gradientUnits="userSpaceOnUse" spreadMethod="reflect">
    <stop offset="0" stop-color="{t['fg']}"/>
    <stop offset=".45" stop-color="{t['accent_soft']}"/>
    <stop offset=".75" stop-color="{t['accent']}"/>
    <stop offset="1" stop-color="{t['blue']}"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="0 0;640 0;0 0" dur="10s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="edge" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t['accent']}"/><stop offset="1" stop-color="{t['blue']}"/></linearGradient>
  <linearGradient id="avatar" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t['accent']}"/><stop offset="1" stop-color="{t['blue']}"/></linearGradient>
  {_defs_only(typed_commits(t, 228, 305, total, slot))}
</defs>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="{t['canvas']}"/>
  <ellipse class="blob" cx="1000" cy="40" rx="420" ry="240" fill="url(#glowA)"/>
  <ellipse class="blob b2" cx="180" cy="420" rx="380" ry="200" fill="url(#glowB)"/>
  <rect width="{W}" height="{H}" fill="url(#dots)" mask="url(#dotmask)"/>

  <g class="sans">
    <g class="rise d1">
      <rect x="60" y="52" width="356" height="30" rx="15" fill="{t['subtle']}" stroke="{t['border']}"/>
      <circle cx="80" cy="67" r="4" fill="{t['green']}"/>
      <circle cx="80" cy="67" r="4" fill="none" stroke="{t['green']}"><animate attributeName="r" values="4;10" dur="2s" repeatCount="indefinite"/><animate attributeName="opacity" values=".8;0" dur="2s" repeatCount="indefinite"/></circle>
      <text x="94" y="72" class="mono" font-size="12.5" fill="{t['muted']}">Software Development Intern <tspan fill="{t['accent']}">@ FlyingDuck</tspan></text>
    </g>
    <text class="rise d2" x="56" y="150" font-size="62" font-weight="700" letter-spacing="-1.5" fill="url(#shine)">Boin Prashasthi</text>
    <text class="rise d3" x="60" y="192" font-size="21" font-weight="500" fill="{t['fg']}">Software Engineer <tspan fill="{t['faint']}">·</tspan> Backend &amp; APIs <tspan fill="{t['faint']}">·</tspan> Full-stack <tspan fill="{t['faint']}">·</tspan> Generative AI</text>
    <text class="rise d4" x="60" y="224" font-size="15" fill="{t['muted']}">B.Tech CSE (Cyber Security) · VNR VJIET · Hyderabad, India</text>

    <g class="rise d5">
      <rect x="60" y="270" width="640" height="56" rx="8" fill="{t['subtle']}" stroke="{t['border']}"/>
      <circle cx="88" cy="298" r="13" fill="url(#avatar)"/>
      <text x="88" y="303" text-anchor="middle" font-size="13" font-weight="700" fill="#ffffff">P</text>
      <text x="111" y="304" font-size="14" font-weight="600" fill="{t['fg']}">Prashasthi-18</text>
      __COMMITS__
    </g>
  </g>

  <text x="760" y="96" class="mono rise d3" font-size="12" fill="{t['faint']}">$ git log --graph --all</text>
  <g class="rise d3" fill="none">
  {git_graph(t)}
  </g>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="11.5" fill="none" stroke="{t['border']}"/>
<rect class="run" x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="11.5" fill="none" stroke="url(#edge)" stroke-width="1.5" pathLength="1000"/>
"""
    commit_layers = _commit_layers(t, total, slot)
    body = body.replace("__COMMITS__", commit_layers)
    css = """
    .d1 { animation-delay: .1s; } .d2 { animation-delay: .25s; } .d3 { animation-delay: .4s; } .d4 { animation-delay: .55s; } .d5 { animation-delay: .7s; }
    .blob { transform-box: fill-box; transform-origin: center; animation: drift 18s ease-in-out infinite alternate; }
    .b2 { animation-duration: 24s; animation-delay: -8s; }
    @keyframes drift { 0% { transform: translate(0,0) scale(1); } 50% { transform: translate(-70px,30px) scale(1.12); } 100% { transform: translate(40px,-10px) scale(.94); } }
    .run { stroke-dasharray: 120 880; animation: run 10s linear infinite; }
    @keyframes run { to { stroke-dashoffset: -1000; } }
    """
    return svg(W, H, body,
               "Boin Prashasthi. Software Engineer: Backend and APIs, Full-stack, Generative AI. "
               "Software Development Intern at FlyingDuck. B.Tech CSE (Cyber Security), VNR VJIET, Hyderabad.",
               css)


def _commit_layers(t, total, slot):
    """The visible commit rows; their clip paths live in <defs> via typed_commits."""
    # typed_commits emits clipPaths followed by groups; split so only groups render here.
    raw = typed_commits(t, 228, 305, total, slot)
    return "\n".join(line for line in raw.split("\n") if not line.startswith("<clipPath"))


def _defs_only(raw):
    return "\n".join(line for line in raw.split("\n") if line.startswith("<clipPath"))


# ----------------------------------------------------------------- section header

HEADERS = {
    "about": ("person", "About me", "about.py"),
    "experience": ("briefcase", "Experience & education", "git log --author=prashasthi"),
    "projects": ("code", "Software engineering projects", "pinned"),
    "ai": ("sparkle", "AI & LLM applications", "agents · rag · llmops"),
    "skills": ("stack", "Technical skills", "one request, end to end"),
    "achievements": ("trophy", "Achievements & certifications", "releases"),
    "activity": ("graph", "GitHub activity", "insights"),
    "connect": ("mail", "Let's connect", "open an issue, say hi"),
}


def header(t, key):
    ic, title, hint = HEADERS[key]
    W, H = 1200, 72
    body = f"""
<defs><linearGradient id="hl" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t['accent']}" stop-opacity="0"/><stop offset=".5" stop-color="{t['accent']}"/><stop offset="1" stop-color="{t['blue']}" stop-opacity="0"/></linearGradient></defs>
<g class="sans">
  <g class="rise">
    <rect x="1" y="13" width="40" height="40" rx="9" fill="{t['subtle']}" stroke="{t['border']}"/>
    <rect class="pulse" x="1" y="13" width="40" height="40" rx="9" fill="none" stroke="{t['accent']}"/>
    {icon(ic, 11, 23, t['accent'])}
  </g>
  <text class="rise d1" x="58" y="43" font-size="24" font-weight="600" fill="{t['fg']}">{esc(title)}</text>
  <text class="rise d2 mono" x="{W - 2}" y="41" text-anchor="end" font-size="12.5" fill="{t['faint']}">{esc(hint)}</text>
  <rect x="0" y="66" width="{W}" height="1" fill="{t['border']}"/>
  <rect class="scan" x="-240" y="65.5" width="240" height="2" rx="1" fill="url(#hl)"/>
</g>"""
    css = """
    .d1 { animation-delay: .1s; } .d2 { animation-delay: .2s; }
    .pulse { animation: pulse 4s ease-in-out infinite; }
    @keyframes pulse { 0%, 100% { stroke-opacity: 0; } 50% { stroke-opacity: .9; } }
    .scan { animation: scan 7s cubic-bezier(.5,0,.5,1) infinite; }
    @keyframes scan { 0% { transform: translateX(0); } 70%, 100% { transform: translateX(1440px); } }
    """
    return svg(W, H, body, title, css)


# ------------------------------------------------------------------- about (diff)

def about(t):
    k, s, e, c, v, f, m = (t["s_kw"], t["s_str"], t["s_ent"], t["s_const"], t["s_var"], t["fg"], t["muted"])
    lines = [
        [(k, "class "), (e, "Prashasthi"), (f, "("), (e, "SoftwareEngineer"), (f, "):")],
        [(s, '    """I build backend services, APIs and AI systems that hold up in real use."""')],
        [],
        [(f, "    role      "), (k, "= "), (s, '"Software Development Intern @ FlyingDuck"')],
        [(f, "    education "), (k, "= "), (s, '"B.Tech CSE (Cyber Security), VNR VJIET"'), (f, ", "), (f, "cgpa"), (k, "="), (c, "9.15")],
        [(f, "    location  "), (k, "= "), (s, '"Hyderabad, India"')],
        [(f, "    focus     "), (k, "= "), (f, "["), (s, '"backend"'), (f, ", "), (s, '"rest-apis"'), (f, ", "),
         (s, '"full-stack"'), (f, ", "), (s, '"generative-ai"'), (f, ", "), (s, '"devops"'), (f, "]")],
        [(f, "    shipping  "), (k, "= "), (s, '"a dependency upgrade impact analyzer"')],
        [],
        [(k, "    def "), (e, "build"), (f, "("), (c, "self"), (f, ", "), (v, "idea"), (f, ": "), (c, "str"), (f, ") "),
         (k, "-> "), (e, "Release"), (f, ":")],
        [(k, "        return "), (e, "ship"), (f, "("), (e, "test"), (f, "("), (e, "integrate"), (f, "("),
         (e, "design"), (f, "("), (v, "idea"), (f, "))))")],
    ]
    W = 1200
    head_h, row_h, top_pad = 50, 29, 10
    rows_top = head_h + top_pad
    foot_y = rows_top + len(lines) * row_h + 14
    H = foot_y + 54
    total = 18.0
    cw = 8.4
    merge_t = 0
    rows, clips = [], []
    tcur = 0.8
    for i, toks in enumerate(lines):
        y = rows_top + i * row_h
        text = "".join(x[1] for x in toks)
        dur = max(len(text) * 0.011, 0.12)
        start = tcur
        end_hold = total - 1.0
        clips.append(
            f'<clipPath id="ln{i}"><rect x="96" y="{y}" height="{row_h}" width="0">'
            f'<animate attributeName="width" values="0;0;{len(text) * cw + 12:.0f};{len(text) * cw + 12:.0f};0;0" '
            f'keyTimes="{kt([0, start, start + dur, end_hold, end_hold + .4, total], total)}" dur="{total}s" repeatCount="indefinite"/>'
            f'</rect></clipPath>'
        )
        spans = "".join(f'<tspan fill="{col}">{esc(txt)}</tspan>' for col, txt in toks)
        rows.append(
            f'<g opacity="0">{window_opacity(start, end_hold, total, fade=.15)}'
            f'<rect x="0" y="{y}" width="{W}" height="{row_h}" fill="{t["add_row"]}" fill-opacity="{t["add_row_op"]}"/>'
            f'<rect x="0" y="{y}" width="64" height="{row_h}" fill="{t["add_row"]}" fill-opacity="{t["add_gutter_op"]}"/>'
            f'<text x="48" y="{y + 19}" text-anchor="end" class="mono" font-size="12.5" fill="{t["muted"]}">{i + 1}</text>'
            f'<text x="76" y="{y + 19}" class="mono" font-size="14" fill="{t["green"]}">+</text>'
            f'<g clip-path="url(#ln{i})"><text x="98" y="{y + 19}" class="mono" font-size="14" xml:space="preserve">{spans}</text></g>'
            f'</g>'
        )
        tcur = start + dur + (0.12 if text else 0.05)
    merge_t = tcur + 0.6
    hide = total - 1.0
    n = len(lines)
    body = f"""
<defs>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="10"/></clipPath>
  {''.join(clips)}
</defs>
<g clip-path="url(#card)" class="sans">
  <rect width="{W}" height="{H}" fill="{t['canvas']}"/>
  <rect width="{W}" height="{head_h}" fill="{t['subtle']}"/>
  <rect y="{head_h - 1}" width="{W}" height="1" fill="{t['border']}"/>
  <path d="M20 21l5 5 5-5" fill="none" stroke="{t['muted']}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
  {icon('file', 40, 15, t['muted'])}
  <text x="68" y="30" class="mono" font-size="13.5" fill="{t['fg']}">src/about.py</text>
  <text x="186" y="30" class="mono" font-size="13" fill="{t['green']}">+{n}</text>
  <text x="216" y="30" class="mono" font-size="13" fill="{t['red']}">−0</text>
  {''.join(f'<rect x="{248 + j * 11}" y="20" width="8" height="8" rx="1.5" fill="{t["green"]}"/>' for j in range(5))}

  <g opacity="1">
    <animate attributeName="opacity" values="1;1;0;0;1" keyTimes="{kt([0, merge_t, merge_t + .3, hide + .4, total], total)}" dur="{total}s" repeatCount="indefinite"/>
    <rect x="{W - 112}" y="12" width="96" height="26" rx="13" fill="{t['green_em']}"/>
    {icon('pr', W - 101, 17, '#ffffff', size=16, width=1.6)}
    <text x="{W - 80}" y="30" font-size="13" font-weight="600" fill="#ffffff">Open</text>
  </g>
  <g opacity="0">
    {window_opacity(merge_t, hide + .2, total, fade=.3)}
    <rect x="{W - 124}" y="12" width="108" height="26" rx="13" fill="{t['accent_em']}"/>
    {icon('merge', W - 113, 17, '#ffffff', size=16, width=1.6)}
    <text x="{W - 92}" y="30" font-size="13" font-weight="600" fill="#ffffff">Merged</text>
  </g>

  {''.join(rows)}

  <rect y="{foot_y}" width="{W}" height="1" fill="{t['border']}"/>
  <rect y="{foot_y + 1}" width="{W}" height="{H - foot_y}" fill="{t['subtle']}"/>
  <g opacity="1">
    <animate attributeName="opacity" values="1;1;0;0;1" keyTimes="{kt([0, merge_t, merge_t + .3, hide + .4, total], total)}" dur="{total}s" repeatCount="indefinite"/>
    <circle cx="30" cy="{foot_y + 28}" r="7" fill="none" stroke="{t['yellow']}" stroke-width="2" stroke-dasharray="30 14">
      <animateTransform attributeName="transform" type="rotate" from="0 30 {foot_y + 28}" to="360 30 {foot_y + 28}" dur="1s" repeatCount="indefinite"/>
    </circle>
    <text x="48" y="{foot_y + 33}" font-size="13.5" fill="{t['muted']}">Running checks <tspan class="mono" fill="{t['faint']}">lint · pytest · build</tspan></text>
  </g>
  <g opacity="0">
    {window_opacity(merge_t, hide + .2, total, fade=.3)}
    <circle cx="30" cy="{foot_y + 28}" r="11" fill="{t['accent_em']}"/>
    {icon('merge', 23, foot_y + 21, '#ffffff', size=14, width=1.6)}
    <text x="50" y="{foot_y + 33}" font-size="13.5" fill="{t['fg']}"><tspan font-weight="600">Prashasthi-18</tspan> merged 1 commit into <tspan class="mono" fill="{t['blue']}">main</tspan> <tspan fill="{t['muted']}">· all checks passed</tspan></text>
  </g>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="9.5" fill="none" stroke="{t['border']}"/>
"""
    return svg(W, H, body,
               "about.py: class Prashasthi(SoftwareEngineer). Role: Software Development Intern at FlyingDuck. "
               "Education: B.Tech CSE (Cyber Security), VNR VJIET, CGPA 9.15. Location: Hyderabad, India. "
               "Focus: backend, REST APIs, full-stack, generative AI, DevOps.")


# --------------------------------------------------------------- pipeline (Actions)

JOBS = [
    ("Design", "contracts · data models", "8s"),
    ("Build", "FastAPI · Node.js", "41s"),
    ("Integrate", "APIs · LLMs · Docker", "27s"),
    ("Test", "pytest · Playwright", "36s"),
    ("Ship", "GitHub Actions · CI/CD", "19s"),
]


def pipeline(t):
    W, H = 1200, 232
    total = 16.0
    bw, bh, gap, left = 196, 66, 30, 37
    by = 112
    reset = total - .8
    parts = []
    run_len = 1.7
    done_times = []
    for i, (name, sub, dur) in enumerate(JOBS):
        x = left + i * (bw + gap)
        a = 0.9 + i * 2.1
        b = a + run_len
        done_times.append(b)
        cy = by + 24
        cx = x + 24
        # connector to next job
        if i < len(JOBS) - 1:
            x2 = x + bw + gap
            ym = by + bh / 2
            parts.append(
                f'<path d="M{x + bw} {ym}H{x2}" stroke="{t["border"]}" stroke-width="2"/>'
                f'<path d="M{x + bw} {ym}H{x2}" stroke="{t["green"]}" stroke-width="2" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1">'
                f'{draw_line(b, b + .4, total, reset)}</path>'
                f'<circle cx="{x + bw}" cy="{ym}" r="3.5" fill="{t["canvas"]}" stroke="{t["border"]}" stroke-width="1.5"/>'
                f'<circle cx="{x2}" cy="{ym}" r="3.5" fill="{t["canvas"]}" stroke="{t["border"]}" stroke-width="1.5"/>'
            )
        parts.append(
            f'<rect x="{x}" y="{by}" width="{bw}" height="{bh}" rx="8" fill="{t["canvas"]}" stroke="{t["border"]}"/>'
            # running highlight
            f'<rect x="{x}" y="{by}" width="{bw}" height="{bh}" rx="8" fill="{t["yellow"]}" fill-opacity=".06" stroke="{t["yellow"]}" opacity="0">'
            f'{window_opacity(a, b, total, fade=.2)}</rect>'
            # queued
            f'<circle cx="{cx}" cy="{cy}" r="7" fill="none" stroke="{t["faint"]}" stroke-width="1.6" stroke-dasharray="2.5 2.5">'
            f'<animate attributeName="opacity" values="1;1;0;0;1;1" keyTimes="{kt([0, a, a + .1, reset, reset + .3, total], total)}" dur="{total}s" repeatCount="indefinite"/></circle>'
            # running spinner
            f'<g opacity="0">{window_opacity(a, b, total, fade=.1)}'
            f'<circle cx="{cx}" cy="{cy}" r="7" fill="none" stroke="{t["yellow"]}" stroke-opacity=".3" stroke-width="2"/>'
            f'<circle cx="{cx}" cy="{cy}" r="7" fill="none" stroke="{t["yellow"]}" stroke-width="2" stroke-dasharray="14 30" stroke-linecap="round">'
            f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur=".9s" repeatCount="indefinite"/></circle></g>'
            # success
            f'<g opacity="0">{window_opacity(b, reset, total, fade=.2)}'
            f'<circle cx="{cx}" cy="{cy}" r="9" fill="{t["green_em"]}"/>'
            f'{icon("check", cx - 6.5, cy - 6.5, "#ffffff", size=13, width=2)}'
            f'<text x="{x + bw - 14}" y="{cy + 5}" text-anchor="end" class="mono" font-size="12" fill="{t["muted"]}">{dur}</text></g>'
            f'<text x="{x + 42}" y="{cy + 5}" font-size="14.5" font-weight="600" fill="{t["fg"]}">{name}</text>'
            f'<text x="{x + 42}" y="{cy + 27}" font-size="12" fill="{t["muted"]}">{esc(sub)}</text>'
        )
    finish = done_times[-1] + .3
    body = f"""
<defs>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="10"/></clipPath>
  <pattern id="dots" width="16" height="16" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r="1" fill="{t['dot']}"/></pattern>
</defs>
<g clip-path="url(#card)" class="sans">
  <rect width="{W}" height="{H}" fill="{t['canvas']}"/>
  <rect y="60" width="{W}" height="{H - 60}" fill="url(#dots)" opacity=".7"/>
  <rect width="{W}" height="60" fill="{t['subtle']}"/>
  <rect y="59" width="{W}" height="1" fill="{t['border']}"/>
  <g opacity="1">
    <animate attributeName="opacity" values="1;1;0;0;1;1" keyTimes="{kt([0, finish, finish + .2, reset, reset + .3, total], total)}" dur="{total}s" repeatCount="indefinite"/>
    <circle cx="30" cy="30" r="8" fill="none" stroke="{t['yellow']}" stroke-width="2.2" stroke-dasharray="16 34" stroke-linecap="round">
      <animateTransform attributeName="transform" type="rotate" from="0 30 30" to="360 30 30" dur=".9s" repeatCount="indefinite"/>
    </circle>
    <text x="{W - 20}" y="35" text-anchor="end" font-size="13" fill="{t['yellow']}">In progress</text>
  </g>
  <g opacity="0">
    {window_opacity(finish, reset, total, fade=.2)}
    <circle cx="30" cy="30" r="10" fill="{t['green_em']}"/>
    {icon('check', 23, 23, '#ffffff', size=14, width=2)}
    <text x="{W - 20}" y="35" text-anchor="end" font-size="13" fill="{t['green']}">Success · 2m 11s</text>
  </g>
  <text x="50" y="35" font-size="15" font-weight="600" fill="{t['fg']}">How I build <tspan font-weight="400" fill="{t['muted']}">· build-and-ship.yml · on: push</tspan></text>
  <rect x="{W - 300}" y="19" width="56" height="22" rx="11" fill="{t['blue']}" fill-opacity=".12"/>
  <text x="{W - 272}" y="34" text-anchor="middle" class="mono" font-size="12" fill="{t['blue']}">main</text>
  {''.join(parts)}
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="9.5" fill="none" stroke="{t['border']}"/>
"""
    return svg(W, H, body, "How I build, as a CI workflow: Design, Build, Integrate, Test, Ship.")


# ----------------------------------------------------------------- project cards

PROJECTS = {
    "analyzer": ("Dependency-Upgrade-Analyzer", "Python",
                 "Compares two versions of any PyPI or npm package: merges every release note in between, "
                 "flags breaking changes and known security advisories, and exports one upgrade-impact report.",
                 ["pypi", "npm", "github-api", "security"]),
    "gateway": ("API-Gateway", "Python",
                "API gateway that routes requests between backend services, with API keys, JWT validation, "
                "logging and thread-safe token-bucket and sliding-window rate limiters.",
                ["jwt", "rate-limiting", "microservices"]),
    "voice": ("AI-Voice-Assistant", "Python",
              "Full-stack voice assistant: a FastAPI backend and an interactive speech frontend talking over "
              "REST APIs, containerised with Docker.",
              ["fastapi", "docker", "rest-api"]),
    "req2test": ("Req2Test", "Python",
                 "Turns a user story into reviewed, runnable Playwright tests. FastAPI backend streaming over "
                 "Server-Sent Events, with traceability, validation and exports.",
                 ["fastapi", "sse", "playwright", "crewai"]),
    "pipeline": ("Automated-Code-Testing-Pipeline", "Python",
                 "A pytest suite wired into GitHub Actions: every push installs dependencies and runs the "
                 "tests automatically, so regressions never reach main.",
                 ["pytest", "github-actions", "ci-cd"]),
    "pricepulse": ("Price-Pulse", "JavaScript",
                   "Chrome extension that detects the product on the current page and compares its price "
                   "across Amazon, Flipkart, Croma, Reliance Digital and more.",
                   ["chrome-extension", "service-worker"]),
    "llmops": ("LLMOPS", "Python",
               "Modular platform for AI workflows: prompt management, model evaluation, monitoring and "
               "multi-agent execution, coordinated with LangGraph.",
               ["langgraph", "langchain", "mistral", "fastapi"]),
    "video": ("AI-Video-Assistant-With-RAG", "Python",
              "Turns YouTube transcripts into summaries, action items and decisions, then lets you query the "
              "video through a conversational RAG interface. Live demo available.",
              ["rag", "chromadb", "langchain"]),
    "clearpay": ("ClearPAY", "Python",
                 "Invoice-to-payment AP automation agent: reads invoices, matches purchase orders and recommends "
                 "approve, flag or reject with reasons. The AI never makes the payment decision.",
                 ["flask", "tool-calling", "groq"]),
    "apitest": ("API-Testing-Agent", "TypeScript",
                "Give it an OpenAPI or Postman spec: it generates positive, negative and edge-case tests, runs "
                "them against the real API and explains every failure.",
                ["openapi", "llm-agents", "testing"]),
    "research": ("Multi-Agent-Research-System", "Python",
                 "Search, Reader, Writer and Critic agents research any topic, scrape sources, draft a report "
                 "and review it for quality.",
                 ["multi-agent", "tavily", "langchain"]),
    "guardrails": ("Guardrails-Mini-Project", "Python",
                   "Healthcare assistant with layered guardrails: input validation, PII redaction, human "
                   "approval for bookings and output validation.",
                   ["langgraph", "guardrails", "hitl"]),
}


def wrap(text, size, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if text_width(trial, size) > max_w and cur:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def card(t, key, index):
    name, lang, desc, topics = PROJECTS[key]
    W, H = 600, 176
    lines = wrap(desc, 13.5, W - 48)[:3]
    desc_svg = "".join(
        f'<text x="24" y="{76 + i * 21}" font-size="13.5" fill="{t["muted"]}">{esc(line)}</text>'
        for i, line in enumerate(lines)
    )
    x = 24
    by = H - 30
    foot = [f'<circle cx="{x + 6}" cy="{by}" r="6" fill="{LANG.get(lang, t["faint"])}"/>'
            f'<text x="{x + 18}" y="{by + 4.5}" font-size="12.5" fill="{t["muted"]}">{lang}</text>']
    x += 18 + text_width(lang, 12.5) + 18
    for topic in topics:
        tw = text_width(topic, 11.5) + 20
        if x + tw > W - 20:
            break
        foot.append(
            f'<rect x="{x:.0f}" y="{by - 11}" width="{tw:.0f}" height="22" rx="11" fill="{t["blue"]}" fill-opacity=".1"/>'
            f'<text x="{x + tw / 2:.0f}" y="{by + 4}" text-anchor="middle" font-size="11.5" font-weight="500" fill="{t["blue"]}">{topic}</text>'
        )
        x += tw + 6
    body = f"""
<defs><linearGradient id="edge" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t['accent']}"/><stop offset="1" stop-color="{t['blue']}"/></linearGradient></defs>
<g class="sans rise">
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="8" fill="{t['canvas']}" stroke="{t['border']}"/>
  <rect class="sweep" x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="8" fill="none" stroke="url(#edge)" stroke-width="1.5" pathLength="1000" style="animation-delay:{-index * 1.3:.1f}s"/>
  {icon('repo', 22, 22, t['muted'], size=18)}
  <text x="48" y="37" font-size="16" font-weight="600" fill="{t['blue']}">{esc(name)}</text>
  <rect x="{48 + text_width(name, 16, bold=True) + 10:.0f}" y="23" width="52" height="20" rx="10" fill="none" stroke="{t['border']}"/>
  <text x="{48 + text_width(name, 16, bold=True) + 36:.0f}" y="37" text-anchor="middle" font-size="11.5" font-weight="500" fill="{t['muted']}">Public</text>
  {desc_svg}
  {''.join(foot)}
</g>"""
    css = """
    .sweep { stroke-dasharray: 140 860; stroke-dashoffset: 0; animation: sweep 9s linear infinite; }
    @keyframes sweep { to { stroke-dashoffset: -1000; } }
    """
    return svg(W, H, body, f"{name}: {desc}", css)


# --------------------------------------------------------------- technical skills

LAYERS = [
    ("Languages", ["Python", "Java", "C", "C++", "SQL", "JavaScript"]),
    ("Backend & APIs", ["FastAPI", "Flask", "Node.js", "Express.js", "REST APIs", "JWT · OAuth", "Server-Sent Events"]),
    ("Data", ["PostgreSQL", "SQLite", "ChromaDB", "Pandas", "NumPy", "scikit-learn"]),
    ("AI / LLMs", ["LangChain", "LangGraph", "CrewAI", "RAG", "Multi-agent systems", "Guardrails"]),
    ("Ship & test", ["Docker", "Linux", "Git", "GitHub Actions", "GitLab CI/CD", "pytest", "Playwright"]),
]

# Each trace is one request moving through the layers: (method, route, ms, node per layer).
TRACES = [
    ("POST", "/api/agents/run", 184, ["Python", "FastAPI", "PostgreSQL", "LangGraph", "Docker"]),
    ("GET", "/api/videos/ask", 96, ["Python", "REST APIs", "ChromaDB", "RAG", "GitHub Actions"]),
    ("POST", "/api/invoices/match", 142, ["Python", "Flask", "SQLite", "Guardrails", "pytest"]),
    ("POST", "/api/tests/generate", 231, ["JavaScript", "Node.js", "Pandas", "CrewAI", "Playwright"]),
    ("GET", "/api/upgrades/impact", 77, ["SQL", "JWT · OAuth", "PostgreSQL", "LangChain", "GitLab CI/CD"]),
]


def skills(t):
    W, pad, gap = 1200, 28, 40
    cw = (W - 2 * pad - gap * (len(LAYERS) - 1)) / len(LAYERS)
    top, step, nh = 74, 38, 30
    rows = max(len(items) for _, items in LAYERS)
    bar_y = top + rows * step + 14
    H = bar_y + 58
    slot = 4.0
    total = slot * len(TRACES)

    def node_pos(col, name):
        r = LAYERS[col][1].index(name)
        x = pad + col * (cw + gap)
        return x, top + r * step

    heads, nodes = [], []
    for c, (label, items) in enumerate(LAYERS):
        x = pad + c * (cw + gap)
        heads.append(
            f'<text x="{x:.0f}" y="{top - 22}" class="mono" font-size="11.5" letter-spacing="1" fill="{t["faint"]}">'
            f'<tspan fill="{t["accent"]}">{c + 1:02d}</tspan>  {esc(label.upper())}</text>'
        )
        for r, name in enumerate(items):
            y = top + r * step
            nodes.append(
                f'<rect x="{x:.0f}" y="{y}" width="{cw:.0f}" height="{nh}" rx="6" fill="{t["canvas"]}" stroke="{t["border"]}"/>'
                f'<text x="{x + 14:.0f}" y="{y + 19.5}" font-size="13.5" fill="{t["muted"]}">{esc(name)}</text>'
            )

    routes, lit, bars = [], [], []
    for i, (method, path, ms, hops) in enumerate(TRACES):
        s = i * slot
        draw_s, draw_e, end = s + .2, s + 1.8, s + slot - .35
        pts = [node_pos(c, name) for c, name in enumerate(hops)]
        x0, y0 = pts[0]
        d = f"M{x0 + cw:.0f} {y0 + nh / 2}"
        for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
            ya, yb = ya + nh / 2, yb + nh / 2
            d += f"C{xa + cw + gap / 2:.0f} {ya} {xb - gap / 2:.0f} {yb} {xb:.0f} {yb}H{xb + cw:.0f}"
        routes.append(
            f'<g opacity="0">{window_opacity(draw_s - .05, end, total, fade=.3)}'
            f'<path d="{d}" fill="none" stroke="{t["accent"]}" stroke-width="2" stroke-linecap="round" pathLength="1" '
            f'stroke-dasharray="1 1" stroke-dashoffset="1">{draw_line(draw_s, draw_e, total, total)}</path>'
            f'<g opacity="0">{window_opacity(draw_e, end, total, fade=.2)}'
            + "".join(
                f'<circle r="2.6" fill="{t["accent_soft"]}"><animateMotion path="{d}" dur="1.5s" '
                f'begin="{-k * .5:.1f}s" repeatCount="indefinite"/></circle>' for k in range(3)
            )
            + "</g></g>"
        )
        for c, (x, y) in enumerate(pts):
            tc = draw_s + c * (draw_e - draw_s) / (len(pts) - 1) - .05
            lit.append(
                f'<g opacity="0">{window_opacity(max(tc, .01), end, total, fade=.15)}'
                f'<rect x="{x:.0f}" y="{y}" width="{cw:.0f}" height="{nh}" rx="6" fill="{t["accent"]}" fill-opacity=".1" '
                f'stroke="{t["accent"]}"/>'
                f'<text x="{x + 14:.0f}" y="{y + 19.5}" font-size="13.5" font-weight="600" fill="{t["fg"]}">{esc(hops[c])}</text>'
                f'<circle cx="{x + cw - 14:.0f}" cy="{y + nh / 2}" r="3" fill="{t["accent"]}"/></g>'
            )
        chain = f' <tspan fill="{t["faint"]}">→</tspan> '.join(esc(h) for h in hops)
        bars.append(
            f'<g opacity="0">{window_opacity(draw_s, end, total, fade=.25)}'
            f'<text x="{pad + 16}" y="{bar_y + 27}" class="mono" font-size="12.5" fill="{t["fg"]}">'
            f'<tspan fill="{t["accent"]}" font-weight="600">{method}</tspan> {esc(path)}</text>'
            f'<text x="{pad + 250}" y="{bar_y + 27}" font-size="13" fill="{t["muted"]}">{chain}</text>'
            f'<g opacity="0">{window_opacity(draw_e, end, total, fade=.2)}'
            f'<rect x="{W - pad - 150}" y="{bar_y + 13}" width="64" height="20" rx="10" fill="{t["green"]}" fill-opacity=".14"/>'
            f'<text x="{W - pad - 118}" y="{bar_y + 27}" text-anchor="middle" class="mono" font-size="11.5" fill="{t["green"]}">200 OK</text>'
            f'<text x="{W - pad - 16}" y="{bar_y + 27}" text-anchor="end" class="mono" font-size="12" fill="{t["muted"]}">{ms} ms</text>'
            f'</g></g>'
        )

    body = f"""
<g class="sans">
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="{t['subtle']}" stroke="{t['border']}"/>
  {''.join(heads)}
  {''.join(routes)}
  {''.join(nodes)}
  {''.join(lit)}
  <rect x="{pad}" y="{bar_y}" width="{W - 2 * pad}" height="44" rx="8" fill="{t['canvas']}" stroke="{t['border']}"/>
  {''.join(bars)}
</g>"""
    names = "; ".join(f"{label}: {', '.join(items)}" for label, items in LAYERS)
    return svg(W, H, body, f"Technical skills. {names}")


# ------------------------------------------------------------------- achievements

TILES = [
    ("trophy", "Winner", None, "Room Style CTF", "GDGC cyber security competition"),
    ("code", "25+", "25+", "Hackathons", "software, AI and cybersecurity"),
    ("branch", "7+", "7+", "Capture the Flag", "competitions played"),
    ("sparkle", "9.15", "9.15", "CGPA", "B.Tech CSE (Cyber Security)"),
]


def odometer(value, x, baseline, size, fill, begin):
    """Digits that spin up and settle on the final value."""
    adv = size * 0.62
    out, cx = [], x
    for j, ch in enumerate(value):
        if ch.isdigit():
            d = int(ch)
            seq = list(range(10)) + list(range(d + 1))
            step = size * 1.1
            texts = "".join(
                f'<text x="{cx:.1f}" y="{baseline + k * step:.1f}" font-size="{size}" font-weight="700" fill="{fill}">{n}</text>'
                for k, n in enumerate(seq)
            )
            dy = -(len(seq) - 1) * step
            out.append(
                f'<g><animateTransform attributeName="transform" type="translate" values="0 0;0 {dy:.1f}" '
                f'begin="{begin + j * .12:.2f}s" dur="2.2s" calcMode="spline" keySplines=".15 .7 .2 1" fill="freeze"/>{texts}</g>'
            )
            cx += adv
        else:
            out.append(f'<text x="{cx:.1f}" y="{baseline}" font-size="{size}" font-weight="700" fill="{fill}">{esc(ch)}</text>')
            cx += size * (0.3 if ch == "." else 0.62)
    return "".join(out)


def achievements(t):
    W, H = 1200, 168
    gap = 16
    tw = (W - gap * 3) / 4
    parts, clips = [], []
    for i, (ic, value, odo, label, sub) in enumerate(TILES):
        x = i * (tw + gap)
        size = 40
        base = 92
        clips.append(f'<clipPath id="win{i}"><rect x="{x + 20:.0f}" y="{base - size}" width="{tw - 40:.0f}" height="{size + 10}"/></clipPath>')
        if odo:
            value_svg = f'<g clip-path="url(#win{i})">{odometer(odo, x + 24, base, size, "url(#num)", .3 + i * .25)}</g>'
        else:
            value_svg = f'<text x="{x + 24:.0f}" y="{base}" font-size="{size}" font-weight="700" fill="url(#num)">{value}</text>'
        parts.append(
            f'<g class="rise" style="animation-delay:{i * .12:.2f}s">'
            f'<rect x="{x + .5:.1f}" y=".5" width="{tw - 1:.0f}" height="{H - 1}" rx="10" fill="{t["subtle"]}" stroke="{t["border"]}"/>'
            f'<rect class="sweep" style="animation-delay:{-i * 1.5:.1f}s" x="{x + .5:.1f}" y=".5" width="{tw - 1:.0f}" height="{H - 1}" rx="10" fill="none" stroke="url(#edge)" stroke-width="1.5" pathLength="1000"/>'
            f'<rect x="{x + tw - 52:.0f}" y="18" width="32" height="32" rx="8" fill="{t["accent"]}" fill-opacity=".12"/>'
            f'{icon(ic, x + tw - 45, 25, t["accent"], size=18)}'
            f'{value_svg}'
            f'<text x="{x + 24:.0f}" y="{base + 32}" font-size="15" font-weight="600" fill="{t["fg"]}">{esc(label)}</text>'
            f'<text x="{x + 24:.0f}" y="{base + 53}" font-size="12.5" fill="{t["muted"]}">{esc(sub)}</text></g>'
        )
    body = f"""
<defs>
  <linearGradient id="num" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t['accent_soft']}"/><stop offset="1" stop-color="{t['blue']}"/></linearGradient>
  <linearGradient id="edge" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t['accent']}"/><stop offset="1" stop-color="{t['blue']}"/></linearGradient>
  {''.join(clips)}
</defs>
<g class="sans">{''.join(parts)}</g>"""
    css = """
    .sweep { stroke-dasharray: 110 890; animation: sweep 7s linear infinite; }
    @keyframes sweep { to { stroke-dashoffset: -1000; } }
    """
    return svg(W, H, body, "Winner of the GDGC Room Style CTF; 25+ hackathons; 7+ Capture the Flag competitions; CGPA 9.15.", css)


# ------------------------------------------------------------------------ buttons

BUTTONS = {
    "btn-portfolio": ("globe", "Portfolio", True),
    "btn-linkedin": (None, "LinkedIn", False),
    "btn-email": ("mail", "Email me", False),
}


def button(t, key):
    ic, label, primary = BUTTONS[key]
    W = int(text_width(label, 14, bold=True) + 70)
    H = 44
    fg = "#ffffff" if primary else t["fg"]
    fill = t["accent_em"] if primary else t["subtle"]
    stroke = t["accent_em"] if primary else t["border"]
    if ic:
        glyph = icon(ic, 18, 13, fg, size=18)
    else:
        glyph = (f'<rect x="19" y="13" width="18" height="18" rx="3.5" fill="none" stroke="{fg}" stroke-width="1.6"/>'
                 f'<text x="28" y="27" text-anchor="middle" font-size="11" font-weight="700" fill="{fg}">in</text>')
    body = f"""
<defs>
  <clipPath id="c"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="8"/></clipPath>
  <linearGradient id="sheen" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity="{'.35' if primary else '.10'}"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
</defs>
<g class="sans">
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="8" fill="{fill}" stroke="{stroke}"/>
  <g clip-path="url(#c)"><rect class="sheen" x="-80" y="0" width="60" height="{H}" fill="url(#sheen)" transform="skewX(-20)"/></g>
  {glyph}
  <text x="46" y="27.5" font-size="14" font-weight="600" fill="{fg}">{esc(label)}</text>
</g>"""
    css = f"""
    .sheen {{ animation: sheen 5s ease-in-out infinite; animation-delay: {'0s' if primary else '1.2s'}; }}
    @keyframes sheen {{ 0% {{ transform: skewX(-20deg) translateX(0); }} 40%, 100% {{ transform: skewX(-20deg) translateX({W + 160}px); }} }}
    """
    return svg(W, H, body, label, css)


# ------------------------------------------------------------------------- footer

def footer(t):
    W, H = 1200, 210
    total = 9.0
    y = 160
    cx = W / 2
    left = f"M120 {y - 70}H{cx - 160}C{cx - 80} {y - 70} {cx - 70} {y} {cx} {y}"
    right = f"M{W - 120} {y - 70}H{cx + 160}C{cx + 80} {y - 70} {cx + 70} {y} {cx} {y}"
    m = 2.6
    hold = total - 1
    body = f"""
<defs>
  <linearGradient id="shine" x1="0" y1="0" x2="600" y2="0" gradientUnits="userSpaceOnUse" spreadMethod="reflect">
    <stop offset="0" stop-color="{t['fg']}"/><stop offset=".5" stop-color="{t['accent_soft']}"/><stop offset="1" stop-color="{t['blue']}"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="0 0;600 0;0 0" dur="10s" repeatCount="indefinite"/>
  </linearGradient>
  <radialGradient id="halo"><stop offset="0" stop-color="{t['accent']}" stop-opacity=".5"/><stop offset="1" stop-color="{t['accent']}" stop-opacity="0"/></radialGradient>
</defs>
<g class="sans" fill="none">
  <text x="{cx}" y="44" text-anchor="middle" font-size="30" font-weight="700" letter-spacing="-.5" fill="url(#shine)">Let's build something reliable.</text>
  <text x="{cx}" y="72" text-anchor="middle" class="mono" font-size="13" fill="{t['faint']}">$ git merge --no-ff your-idea</text>

  <path d="M40 {y}H{W - 40}" stroke="{t['border']}" stroke-width="2" stroke-dasharray="2 6"/>
  <path d="{left}" stroke="{t['border']}" stroke-width="2"/>
  <path d="{right}" stroke="{t['border']}" stroke-width="2"/>
  <path d="{left}" stroke="{t['blue']}" stroke-width="2.5" stroke-linecap="round" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1">{draw_line(.3, m, total, hold)}</path>
  <path d="{right}" stroke="{t['green']}" stroke-width="2.5" stroke-linecap="round" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1">{draw_line(.3, m, total, hold)}</path>
  <path d="M{cx} {y}H{W - 40}" stroke="{t['accent']}" stroke-width="3" stroke-linecap="round" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1">{draw_line(m, m + 1.6, total, hold)}</path>
  <path d="M{cx} {y}H40" stroke="{t['accent']}" stroke-width="3" stroke-linecap="round" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1">{draw_line(m, m + 1.6, total, hold)}</path>

  <text x="124" y="{y - 80}" class="mono" font-size="12" fill="{t['blue']}">your-idea</text>
  <text x="{W - 124}" y="{y - 80}" text-anchor="end" class="mono" font-size="12" fill="{t['green']}">prashasthi/code</text>
  <circle cx="120" cy="{y - 70}" r="5" fill="{t['blue']}" stroke="{t['canvas']}" stroke-width="3"/>
  <circle cx="{W - 120}" cy="{y - 70}" r="5" fill="{t['green']}" stroke="{t['canvas']}" stroke-width="3"/>

  <circle cx="{cx}" cy="{y}" r="40" fill="url(#halo)" opacity="0">{window_opacity(m, hold, total, fade=.4)}</circle>
  <circle cx="{cx}" cy="{y}" r="9" stroke="{t['accent']}" stroke-width="2" opacity="0">
    <animate attributeName="r" values="9;9;34;34" keyTimes="{kt([0, m, m + 1.1, total], total)}" dur="{total}s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0;0;.9;0;0" keyTimes="{kt([0, m - .01, m + .02, m + 1.1, total], total)}" dur="{total}s" repeatCount="indefinite"/>
  </circle>
  <circle cx="{cx}" cy="{y}" r="8" fill="{t['accent_em']}" stroke="{t['canvas']}" stroke-width="3"/>
  <g opacity="0">{window_opacity(m + .1, hold, total, fade=.3)}{icon('merge', cx - 6, y - 6, '#ffffff', size=12, width=1.8)}</g>
  <g opacity="0">{window_opacity(m + .5, hold, total, fade=.4)}
    <rect x="{cx - 46}" y="{y + 18}" width="92" height="22" rx="11" fill="{t['accent']}" fill-opacity=".14" stroke="{t['accent']}" stroke-opacity=".55"/>
    <text x="{cx}" y="{y + 33}" text-anchor="middle" class="mono" font-size="11.5" fill="{t['accent_soft']}">merged</text>
  </g>
</g>"""
    return svg(W, H, body, "Let's build something reliable. Your idea, merged with my code.")


# --------------------------------------------------------------------------- main

def main():
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.svg"):
        old.unlink()
    for t in THEMES:
        write("hero", t, hero(t))
        for key in HEADERS:
            write(f"h-{key}", t, header(t, key))
        write("about", t, about(t))
        write("pipeline", t, pipeline(t))
        for i, key in enumerate(PROJECTS):
            write(f"card-{key}", t, card(t, key, i))
        write("skills", t, skills(t))
        write("achievements", t, achievements(t))
        for key in BUTTONS:
            write(key, t, button(t, key))
        write("footer", t, footer(t))
    print(f"wrote {len(list(OUT.glob('*.svg')))} files to {OUT}")


if __name__ == "__main__":
    main()
