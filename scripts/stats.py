"""Render the GitHub activity card from live GraphQL data.

Runs daily in .github/workflows/snake.yml and publishes to the `output` branch:

    GITHUB_TOKEN=... python scripts/stats.py --user Prashasthi-18 --out dist

`--sample` renders with made-up numbers, for previewing the design offline.
"""

import argparse
import datetime as dt
import json
import os
import random
import urllib.request
from pathlib import Path

from theme import LANG, THEMES, esc, kt, svg

QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""

SKIP_LANGS = {"Jupyter Notebook"}  # notebook JSON dwarfs real source code


def fetch(user, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": user}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if payload.get("errors"):
        raise RuntimeError(payload["errors"])
    u = payload["data"]["user"]
    cc = u["contributionsCollection"]
    days = [d for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    langs, colors = {}, {}
    for repo in u["repositories"]["nodes"]:
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            if name in SKIP_LANGS:
                continue
            langs[name] = langs.get(name, 0) + edge["size"]
            colors[name] = edge["node"]["color"]
    return {
        "total": cc["contributionCalendar"]["totalContributions"],
        "commits": cc["totalCommitContributions"],
        "prs": cc["totalPullRequestContributions"],
        "repos": u["repositories"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in u["repositories"]["nodes"]),
        "days": [(d["date"], d["contributionCount"]) for d in days],
        "langs": langs,
        "colors": colors,
    }


def sample():
    rnd = random.Random(7)
    today = dt.date.today()
    days = []
    for i in range(364, -1, -1):
        d = today - dt.timedelta(days=i)
        busy = 1 if i < 70 else 0.35
        days.append((d.isoformat(), rnd.choice([0, 0, 1, 2, 3, 5, 8]) if rnd.random() < busy else 0))
    return {"total": sum(c for _, c in days), "commits": 412, "prs": 38, "repos": 30, "stars": 4,
            "days": days, "langs": {"Python": 900, "JavaScript": 160, "TypeScript": 90, "HTML": 60, "CSS": 40, "Shell": 8},
            "colors": {}}


def streaks(days):
    counts = [c for _, c in days]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    current, i = 0, len(counts) - 1
    if i >= 0 and counts[i] == 0:  # today may simply not have happened yet
        i -= 1
    while i >= 0 and counts[i]:
        current += 1
        i -= 1
    return current, longest


def odometer(value, x, baseline, size, fill, begin=0.3):
    adv, out, cx = size * 0.6, [], x
    step = size * 1.1
    for j, ch in enumerate(value):
        if ch.isdigit():
            d = int(ch)
            seq = list(range(10)) + list(range(d + 1))
            texts = "".join(f'<text x="{cx:.1f}" y="{baseline + k * step:.1f}" font-size="{size}" font-weight="700" '
                            f'fill="{fill}">{n}</text>' for k, n in enumerate(seq))
            out.append(f'<g><animateTransform attributeName="transform" type="translate" values="0 0;0 {-(len(seq) - 1) * step:.1f}" '
                       f'begin="{begin + j * .1:.2f}s" dur="2.2s" calcMode="spline" keySplines=".15 .7 .2 1" fill="freeze"/>{texts}</g>')
            cx += adv
        else:
            out.append(f'<text x="{cx:.1f}" y="{baseline}" font-size="{size}" font-weight="700" fill="{fill}">{esc(ch)}</text>')
            cx += size * 0.32
    return "".join(out)


def render(t, data):
    W, H = 1200, 344
    current, longest = streaks(data["days"])
    total = f"{data['total']:,}"

    # left: headline number and four small metrics
    metrics = [("Current streak", f"{current} days"), ("Longest streak", f"{longest} days"),
               ("Commits", f"{data['commits']:,}"), ("Public repos", f"{data['repos']:,}")]
    m_svg = []
    for i, (label, value) in enumerate(metrics):
        x = 28 + (i % 2) * 260
        y = 140 + (i // 2) * 44
        m_svg.append(f'<g class="rise" style="animation-delay:{.3 + i * .1:.1f}s">'
                     f'<text x="{x}" y="{y}" font-size="12.5" fill="{t["muted"]}">{label}</text>'
                     f'<text x="{x}" y="{y + 22}" font-size="18" font-weight="600" fill="{t["fg"]}">{value}</text></g>')

    # right: language share
    langs = sorted(data["langs"].items(), key=lambda kv: -kv[1])
    top = langs[:6]
    other = sum(v for _, v in langs[6:])
    whole = sum(v for _, v in langs) or 1
    if other / whole >= 0.005:
        top.append(("Other", other))
    bx, bw, by = 620, 552, 66
    segs, legend, x = [], [], bx
    for i, (name, size) in enumerate(top):
        w = bw * size / whole
        color = LANG.get(name) or data["colors"].get(name) or t["faint"]
        segs.append(f'<rect x="{x:.1f}" y="{by}" width="{max(w - 2, 1):.1f}" height="10" fill="{color}"/>')
        x += w
        lx = bx + (i % 2) * 280
        ly = by + 44 + (i // 2) * 30
        legend.append(f'<g class="rise" style="animation-delay:{.4 + i * .08:.2f}s">'
                      f'<circle cx="{lx + 6}" cy="{ly - 4}" r="5" fill="{color}"/>'
                      f'<text x="{lx + 20}" y="{ly}" font-size="13.5" font-weight="500" fill="{t["fg"]}">{esc(name)}</text>'
                      f'<text x="{lx + 250}" y="{ly}" text-anchor="end" class="mono" font-size="12.5" fill="{t["muted"]}">'
                      f'{100 * size / whole:.1f}%</text></g>')

    # bottom: weekly contributions, drawn as a line
    counts = [c for _, c in data["days"]]
    weeks = [sum(counts[i:i + 7]) for i in range(0, len(counts), 7)]
    peak = max(weeks) or 1
    gx, gw, gy, gh = 28, W - 56, 326, 58
    pts = [(gx + gw * i / max(len(weeks) - 1, 1), gy - gh * w / peak) for i, w in enumerate(weeks)]
    line = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    area = line + f" L{pts[-1][0]:.1f} {gy} L{pts[0][0]:.1f} {gy} Z"
    ex, ey = pts[-1]
    loop = 8.0

    body = f"""
<defs>
  <linearGradient id="num" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t['accent_soft']}"/><stop offset="1" stop-color="{t['blue']}"/></linearGradient>
  <linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t['accent']}" stop-opacity=".35"/><stop offset="1" stop-color="{t['accent']}" stop-opacity="0"/></linearGradient>
  <clipPath id="num-win"><rect x="28" y="60" width="520" height="56"/></clipPath>
  <clipPath id="bar"><rect x="{bx}" y="{by}" height="10" rx="5" width="0"><animate attributeName="width" values="0;{bw}" begin=".4s" dur="1.6s" calcMode="spline" keySplines=".2 .8 .2 1" fill="freeze"/></rect></clipPath>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="10"/></clipPath>
</defs>
<g class="sans" clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="{t['subtle']}"/>
  <text x="28" y="40" font-size="13" font-weight="600" fill="{t['muted']}">Contributions in the last year</text>
  <g clip-path="url(#num-win)">{odometer(total, 28, 104, 44, "url(#num)")}</g>
  {''.join(m_svg)}

  <rect x="590" y="28" width="1" height="180" fill="{t['border']}"/>
  <text x="{bx}" y="40" font-size="13" font-weight="600" fill="{t['muted']}">Most used languages</text>
  <rect x="{bx}" y="{by}" width="{bw}" height="10" rx="5" fill="{t['border_muted']}"/>
  <g clip-path="url(#bar)">{''.join(segs)}</g>
  {''.join(legend)}

  <rect y="224" width="{W}" height="1" fill="{t['border']}"/>
  <text x="28" y="250" font-size="12" fill="{t['faint']}">Weekly contributions · last 52 weeks</text>
  <text x="{W - 28}" y="250" text-anchor="end" class="mono" font-size="11.5" fill="{t['faint']}">updated {dt.date.today().isoformat()}</text>
  <path d="{area}" fill="url(#area)" opacity="0"><animate attributeName="opacity" values="0;0;1;1;0" keyTimes="{kt([0, .8, 2.2, loop - .6, loop], loop)}" dur="{loop}s" repeatCount="indefinite"/></path>
  <path d="{line}" fill="none" stroke="{t['accent']}" stroke-width="2" stroke-linejoin="round" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1">
    <animate attributeName="stroke-dashoffset" values="1;0;0;1" keyTimes="{kt([0, 2.2, loop - .6, loop], loop)}" calcMode="spline" keySplines=".45 0 .25 1;0 0 1 1;0 0 1 1" dur="{loop}s" repeatCount="indefinite"/>
  </path>
  <circle cx="{ex:.1f}" cy="{ey:.1f}" r="4" fill="{t['accent']}" stroke="{t['subtle']}" stroke-width="2"/>
  <circle cx="{ex:.1f}" cy="{ey:.1f}" r="4" fill="none" stroke="{t['accent']}"><animate attributeName="r" values="4;14" dur="2s" repeatCount="indefinite"/><animate attributeName="opacity" values=".9;0" dur="2s" repeatCount="indefinite"/></circle>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="9.5" fill="none" stroke="{t['border']}"/>
"""
    lang_text = ", ".join(f"{n} {100 * s / whole:.0f}%" for n, s in top)
    label = (f"{data['total']} contributions in the last year; current streak {current} days; longest streak "
             f"{longest} days; {data['commits']} commits; {data['repos']} public repos. Languages: {lang_text}.")
    return svg(W, H, body, label)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default=os.environ.get("GITHUB_USER", "Prashasthi-18"))
    ap.add_argument("--out", default="dist")
    ap.add_argument("--sample", action="store_true")
    args = ap.parse_args()
    data = sample() if args.sample else fetch(args.user, os.environ["GITHUB_TOKEN"])
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for t in THEMES:
        suffix = "" if t["name"] == "dark" else "-light"
        (out / f"stats{suffix}.svg").write_text(render(t, data), encoding="utf-8")
    print(f"wrote stats to {out}: {data['total']} contributions, {len(data['langs'])} languages")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Surface the cause as a workflow annotation; the step is allowed to fail.
        print(f"::warning title=Activity card failed::{type(exc).__name__}: {exc}")
        raise
