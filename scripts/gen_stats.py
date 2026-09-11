#!/usr/bin/env python3
"""Render assets/stats.svg from live GitHub data.

Runs locally (uses `gh auth token`) and in Actions (uses $GITHUB_TOKEN).
"""
import datetime as dt
import json
import os
import subprocess
import sys
import urllib.request

LOGIN = os.environ.get("GH_LOGIN", "LazyerIJ")
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "stats.svg")

QUERY = """
query($login:String!){
  user(login:$login){
    followers{totalCount}
    repositories(ownerAffiliations:OWNER, privacy:PUBLIC, first:100, isFork:false){
      totalCount
      nodes{
        stargazerCount
        primaryLanguage{ name color }
      }
    }
    contributionsCollection{
      contributionCalendar{
        totalContributions
        weeks{ firstDay contributionDays{ date contributionCount } }
      }
    }
  }
}
"""

C_PANEL, C_LINE, C_TXT, C_MUT, C_DIM = "#0d1117", "#1c2430", "#c9d4e0", "#7d8a99", "#4d5865"
C_CYAN, C_PURP = "#22d3ee", "#a855f7"
HEAT = ["#161b22", "#0b3f4d", "#11798f", "#19b0cb", "#22d3ee"]
FONT = 'ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace'


def token():
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if t:
        return t
    return subprocess.check_output(["gh", "auth", "token"], text=True).strip()


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": "bearer " + token(), "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if "errors" in body:
        sys.exit("GraphQL error: %s" % body["errors"])
    return body["data"]["user"]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render(u):
    cal = u["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"]
    repos = u["repositories"]
    stars = sum(n["stargazerCount"] for n in repos["nodes"])

    langs = {}
    for n in repos["nodes"]:
        pl = n["primaryLanguage"]
        if not pl:
            continue
        k = (pl["name"], pl["color"] or C_MUT)
        langs[k] = langs.get(k, 0) + 1
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:6]
    total_bytes = sum(v for _, v in top) or 1

    W, H = 1000, 412
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="github stats">' % (W, H, W, H)]
    s.append("<title>github stats</title>")
    s.append('<style>text{font-family:%s;dominant-baseline:middle}</style>' % FONT)
    s.append('<rect width="%d" height="%d" rx="16" fill="%s" stroke="%s"/>' % (W, H, C_PANEL, C_LINE))

    # ── stat tiles with a sweeping progress ring
    tiles = [
        ("contributions", cal["totalContributions"], "last 12 months", C_CYAN),
        ("public repos", repos["totalCount"], "sources only", C_PURP),
        ("stars earned", stars, "across repos", "#f4c430"),
        ("followers", u["followers"]["totalCount"], "on github", "#34d399"),
    ]
    tw, gap = 226, 16
    for i, (label, value, sub, col) in enumerate(tiles):
        x = 24 + i * (tw + gap)
        s.append('<g><animate attributeName="opacity" values="1;0;0;1" keyTimes="0;.004;%.3f;1" dur="%.2fs" fill="freeze"/>'
                 % (0.12 + i * 0.1, 1.0 + i * 0.12))
        s.append('<rect x="%d" y="24" width="%d" height="92" rx="12" fill="#11161f" stroke="%s"/>' % (x, tw, C_LINE))
        r, cx, cy = 26, x + 46, 70
        s.append('<circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" stroke-width="4"/>' % (cx, cy, r, "#1b2330"))
        circ = 2 * 3.14159 * r
        s.append('<circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" stroke-width="4" stroke-linecap="round" '
                 'transform="rotate(-90 %d %d)" stroke-dasharray="%.1f" stroke-dashoffset="%.1f">'
                 '<animate attributeName="stroke-dashoffset" values="%.1f;%.1f;%.1f" keyTimes="0;.004;1" dur="%.2fs" fill="freeze"/></circle>'
                 % (cx, cy, r, col, cx, cy, circ, circ * 0.25, circ * 0.25, circ, circ * 0.25, 1.6 + i * 0.12))
        s.append('<text x="%d" y="%d" text-anchor="middle" fill="%s" font-size="11" font-weight="700">%s</text>'
                 % (cx, cy, col, "%d" % value if value < 1000 else "%.1fk" % (value / 1000.0)))
        s.append('<text x="%d" y="58" fill="%s" font-size="13" font-weight="700">%s</text>' % (x + 84, C_TXT, label))
        s.append('<text x="%d" y="78" fill="%s" font-size="10.5">%s</text>' % (x + 84, C_DIM, sub))
        s.append('</g>')

    # ── language split, bars growing from zero
    s.append('<text x="24" y="146" fill="%s" font-size="11.5" letter-spacing="1.5">LANGUAGE SPLIT</text>' % C_MUT)
    bx, bw = 24, W - 48
    s.append('<rect x="%d" y="160" width="%d" height="14" rx="7" fill="#11161f"/>' % (bx, bw))
    off = 0.0
    for i, ((name, col), size) in enumerate(top):
        frac = size / total_bytes
        w = bw * frac
        s.append('<rect x="%.1f" y="160" height="14" width="%.1f" fill="%s" opacity=".92">'
                 '<animate attributeName="width" values="%.1f;0;%.1f" keyTimes="0;.004;1" dur="%.2fs" '
                 'calcMode="spline" keySplines="0 0 1 1;.2 .8 .2 1" fill="freeze"/></rect>'
                 % (bx + off, w, col, w, w, 1.2 + i * 0.14))
        off += w
    lx = 24
    for i, ((name, col), size) in enumerate(top):
        pct = 100.0 * size / total_bytes
        s.append('<g><animate attributeName="opacity" values="1;0;0;1" keyTimes="0;.004;%.3f;1" dur="%.2fs" fill="freeze"/>'
                 % (0.55, 1.8 + i * 0.1))
        s.append('<circle cx="%d" cy="196" r="4" fill="%s"/>' % (lx + 4, col))
        s.append('<text x="%d" y="196" fill="%s" font-size="11.5">%s</text>' % (lx + 15, C_TXT, esc(name)))
        s.append('<text x="%d" y="196" fill="%s" font-size="11.5">%.1f%%</text>' % (lx + 22 + len(name) * 7.0, C_DIM, pct))
        s.append('</g>')
        lx += 22 + len(name) * 7.0 + len("%.1f%%" % pct) * 7.2 + 24

    # ── contribution heatmap, columns waving in
    cell, pad = 11, 2
    step = cell + pad
    hw = len(weeks) * step - pad
    hx, hy = (W - hw) / 2.0, 258
    s.append('<text x="%.1f" y="228" fill="%s" font-size="11.5" letter-spacing="1.5">CONTRIBUTIONS</text>' % (hx, C_MUT))
    s.append('<text x="%.1f" y="228" text-anchor="end" fill="%s" font-size="11">%d in the last year</text>'
             % (hx + hw, C_DIM, cal["totalContributions"]))

    counts = [d["contributionCount"] for w in weeks for d in w["contributionDays"]]
    peak = max(counts) or 1
    last_month = None
    for wi, wk in enumerate(weeks):
        x = hx + wi * step
        first = dt.date.fromisoformat(wk["firstDay"])
        if first.month != last_month and first.day <= 7:
            s.append('<text x="%.1f" y="%d" fill="%s" font-size="9.5">%s</text>'
                     % (x, hy - 12, C_DIM, first.strftime("%b")))
            last_month = first.month
        s.append('<g><animate attributeName="opacity" values="1;0;0;1" keyTimes="0;.004;%.4f;1" dur="%.2fs" fill="freeze"/>'
                 % (min(0.02 + wi * 0.011, 0.92), 1.2 + wi * 0.03))
        for di, day in enumerate(wk["contributionDays"]):
            n = day["contributionCount"]
            lvl = 0 if n == 0 else min(4, 1 + int(3.0 * n / peak))
            y = hy + di * step
            s.append('<rect x="%.1f" y="%d" width="%d" height="%d" rx="2.5" fill="%s"/>' % (x, y, cell, cell, HEAT[lvl]))
        s.append('</g>')

    hh = 7 * step - pad
    # sweeping scan highlight over the heatmap
    s.append('<defs><linearGradient id="scanx" x1="0" y1="0" x2="1" y2="0">'
             '<stop offset="0" stop-color="%s" stop-opacity="0"/><stop offset=".5" stop-color="%s" stop-opacity=".22"/>'
             '<stop offset="1" stop-color="%s" stop-opacity="0"/></linearGradient></defs>' % (C_CYAN, C_CYAN, C_CYAN))
    s.append('<rect y="%d" width="90" height="%d" fill="url(#scanx)"><animate attributeName="x" values="%.1f;%.1f" dur="5s" begin="3s" repeatCount="indefinite"/></rect>'
             % (hy, hh, hx - 90, hx + hw))

    ly = hy + hh + 26
    s.append('<text x="%.1f" y="%d" text-anchor="end" fill="%s" font-size="10">less</text>' % (hx + hw - 84, ly, C_DIM))
    for i, c in enumerate(HEAT):
        s.append('<rect x="%.1f" y="%d" width="%d" height="%d" rx="2.5" fill="%s"/>' % (hx + hw - 78 + i * step, ly - 5.5, cell, cell, c))
    s.append('<text x="%.1f" y="%d" fill="%s" font-size="10">more</text>' % (hx + hw - 78 + 5 * step + 4, ly, C_DIM))
    s.append('<text x="%.1f" y="%d" fill="%s" font-size="10">generated %s &#183; refreshed daily by github actions</text>'
             % (hx, ly, C_DIM, dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")))
    s.append("</svg>")
    return "\n".join(s)


if __name__ == "__main__":
    svg = render(fetch())
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print("wrote %s (%d bytes)" % (os.path.normpath(OUT), len(svg)))
