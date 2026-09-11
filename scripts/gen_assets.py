#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render the static animated SVGs in assets/ (hero, timeline, stack, divider).

assets/stats.svg is generated separately by gen_stats.py from live GitHub data.
"""
import os, math, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
os.makedirs(OUT, exist_ok=True)

C_BG      = "#0b0f16"
C_PANEL   = "#0d1117"
C_LINE    = "#1c2430"
C_DIM     = "#4d5865"
C_TXT     = "#c9d4e0"
C_MUT     = "#7d8a99"
C_CYAN    = "#22d3ee"
C_BLUE    = "#3b82f6"
C_PURP    = "#a855f7"
C_GREEN   = "#34d399"
C_PINK    = "#f472b6"

FONT = 'ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace'
KFONT = '"Apple SD Gothic Neo","Malgun Gothic","Noto Sans KR",system-ui,sans-serif'

EPS = 0.004  # first keyframe holds the finished state, so a t=0 snapshot renders as done


def reveal(delay, dur=0.7):
    """Staggered fade-in that still reads correctly if a renderer freezes SMIL at t=0."""
    total = delay + dur
    return ('<animate attributeName="opacity" values="1;0;0;1" keyTimes="0;%.4f;%.4f;1" '
            'dur="%.2fs" fill="freeze"/>' % (EPS, max(delay / total, EPS * 2), total))


def rise(delay, dist=12, dur=0.7):
    total = delay + dur
    return ('<animateTransform attributeName="transform" type="translate" values="0,0;0,%d;0,%d;0,0" '
            'keyTimes="0;%.4f;%.4f;1" dur="%.2fs" calcMode="spline" '
            'keySplines="0 0 1 1;0 0 1 1;.2 .8 .2 1" fill="freeze"/>'
            % (dist, dist, EPS, max(delay / total, EPS * 2), total))


BASE_CSS = """
    text{{font-family:{f};dominant-baseline:middle}}
    .k{{font-family:{kf}}}
    @keyframes blink{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}
    @keyframes rise{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:translateY(0)}}}}
    @keyframes fade{{from{{opacity:0}}to{{opacity:1}}}}
    @keyframes breathe{{0%,100%{{opacity:.18}}50%{{opacity:.42}}}}
""".format(f=FONT, kf=KFONT)


def wave(phase, amp, y0, w=1000, n=48, cycles=3.0):
    pts = []
    for i in range(n + 1):
        x = w * i / n
        y = y0 + amp * math.sin(2 * math.pi * (i / n) * cycles + phase)
        pts.append("%.1f,%.1f" % (x, y))
    return "M" + " L".join(pts)


# ─────────────────────────────────────────────────────────── hero
def hero():
    W, H = 1000, 320
    peri = 2 * (W + H)
    s = []
    s.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="lazyer">' % (W, H, W, H))
    s.append('<title>lazyer — always compiling</title>')
    s.append('<defs>')
    s.append('<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
             '<stop offset="0" stop-color="#0e141d"/><stop offset=".55" stop-color="%s"/><stop offset="1" stop-color="#080c12"/></linearGradient>' % C_PANEL)
    s.append('<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">'
             '<stop offset="0" stop-color="%s" stop-opacity="0"/><stop offset=".35" stop-color="%s"/>'
             '<stop offset=".65" stop-color="%s"/><stop offset="1" stop-color="%s" stop-opacity="0"/></linearGradient>' % (C_CYAN, C_CYAN, C_PURP, C_PURP))
    s.append('<linearGradient id="ttl" x1="0" y1="0" x2="1" y2="0">'
             '<stop offset="0" stop-color="#e8f1ff"/><stop offset=".5" stop-color="%s"/><stop offset="1" stop-color="%s">'
             '<animate attributeName="stop-color" values="%s;%s;%s;%s" dur="9s" repeatCount="indefinite"/></stop></linearGradient>'
             % (C_CYAN, C_PURP, C_PURP, C_PINK, C_BLUE, C_PURP))
    s.append('<radialGradient id="glowA"><stop offset="0" stop-color="%s" stop-opacity=".55"/><stop offset="1" stop-color="%s" stop-opacity="0"/></radialGradient>' % (C_BLUE, C_BLUE))
    s.append('<radialGradient id="glowB"><stop offset="0" stop-color="%s" stop-opacity=".5"/><stop offset="1" stop-color="%s" stop-opacity="0"/></radialGradient>' % (C_PURP, C_PURP))
    s.append('<linearGradient id="scan" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#7dd3fc" stop-opacity="0"/><stop offset=".5" stop-color="#7dd3fc" stop-opacity=".30"/>'
             '<stop offset="1" stop-color="#7dd3fc" stop-opacity="0"/></linearGradient>')
    s.append('<clipPath id="panel"><rect x="1" y="1" width="%d" height="%d" rx="18"/></clipPath>' % (W - 2, H - 2))
    s.append('<clipPath id="type1"><rect x="52" y="66" height="30" width="112">'
             '<animate attributeName="width" from="0" to="112" dur="0.7s" begin="0.2s" fill="freeze"/></rect></clipPath>')
    s.append('<clipPath id="type2"><rect x="52" y="176" height="32" width="168">'
             '<animate attributeName="width" from="0" to="168" dur="0.8s" begin="1.8s" fill="freeze"/></rect></clipPath>')
    s.append('<clipPath id="type3"><rect x="52" y="208" height="32" width="530">'
             '<animate attributeName="width" from="0" to="530" dur="1.7s" begin="2.7s" fill="freeze"/></rect></clipPath>')
    s.append('</defs>')

    s.append('<style>%s' % BASE_CSS)
    s.append("""
    .cur{animation:blink 1s steps(1) infinite}
    .cmd{fill:%s;font-size:15px}
    .pr{fill:%s;font-size:15px;font-weight:700}
    .out{fill:%s;font-size:15px}
    .ttl{font-size:66px;font-weight:800;letter-spacing:6px}
    .g1{mix-blend-mode:screen;animation:gl1 5s steps(1) infinite}
    .g2{mix-blend-mode:screen;animation:gl2 5s steps(1) infinite}
    @keyframes gl1{0%%,86%%,100%%{transform:translate(0,0);opacity:0}
      87%%{transform:translate(-4px,2px);opacity:.85}89%%{transform:translate(3px,-2px);opacity:.7}
      91%%{transform:translate(-2px,1px);opacity:.6}93%%{opacity:0}}
    @keyframes gl2{0%%,86%%,100%%{transform:translate(0,0);opacity:0}
      88%%{transform:translate(4px,-2px);opacity:.85}90%%{transform:translate(-3px,2px);opacity:.7}
      92%%{transform:translate(2px,-1px);opacity:.6}94%%{opacity:0}}
    .brk{stroke:%s;stroke-width:2;fill:none}
    """ % (C_TXT, C_CYAN, C_MUT, C_CYAN))
    s.append('</style>')

    s.append('<rect width="%d" height="%d" rx="18" fill="url(#bg)"/>' % (W, H))
    s.append('<g clip-path="url(#panel)">')

    # drifting grid
    s.append('<g opacity=".5"><g stroke="%s" stroke-width="1" opacity=".35">' % C_LINE)
    g = []
    for x in range(0, W + 80, 40):
        g.append('<line x1="%d" y1="0" x2="%d" y2="%d"/>' % (x, x, H))
    for y in range(0, H + 40, 40):
        g.append('<line x1="-40" y1="%d" x2="%d" y2="%d"/>' % (y, W + 40, y))
    s.append("".join(g))
    s.append('<animateTransform attributeName="transform" type="translate" values="0,0;40,40" dur="7s" repeatCount="indefinite"/>')
    s.append('</g></g>')

    # glow blobs
    s.append('<circle cx="180" cy="70" r="220" fill="url(#glowA)" style="animation:breathe 7s ease-in-out infinite"/>')
    s.append('<circle cx="850" cy="270" r="240" fill="url(#glowB)" style="animation:breathe 9s ease-in-out infinite reverse"/>')

    # morphing waveforms
    for i, (amp, y0, op, dur, col) in enumerate([(9, 296, .30, 11, C_CYAN), (13, 302, .18, 15, C_PURP)]):
        d0, d1, d2 = wave(0, amp, y0), wave(2.1, amp, y0), wave(4.2, amp, y0)
        s.append('<path fill="none" stroke="%s" stroke-width="1.5" opacity="%s" d="%s">'
                 '<animate attributeName="d" values="%s;%s;%s;%s" dur="%ss" repeatCount="indefinite"/></path>'
                 % (col, op, d0, d0, d1, d2, d0, dur))

    # right-side orbit rig
    cx, cy = 812, 168
    s.append('<g opacity=".9">')
    for r, dur, rev, dash in [(44, 26, 0, "3 7"), (70, 38, 1, "2 9"), (98, 54, 0, "1 11")]:
        f, t = (0, 360) if not rev else (360, 0)
        s.append('<circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="%s" opacity=".55">'
                 '<animateTransform attributeName="transform" type="rotate" from="%d %d %d" to="%d %d %d" dur="%ss" repeatCount="indefinite"/></circle>'
                 % (cx, cy, r, C_DIM, dash, f, cx, cy, t, cx, cy, dur))
    for r, dur, col, ang in [(44, 9, C_CYAN, 0), (70, 14, C_PURP, 120), (70, 14, C_BLUE, 300), (98, 20, C_GREEN, 60)]:
        s.append('<g><animateTransform attributeName="transform" type="rotate" from="%d %d %d" to="%d %d %d" dur="%ss" repeatCount="indefinite"/>'
                 '<circle cx="%d" cy="%d" r="3.5" fill="%s"><animate attributeName="r" values="3.5;5;3.5" dur="2.4s" repeatCount="indefinite"/></circle></g>'
                 % (ang, cx, cy, ang + 360, cx, cy, dur, cx, cy - r, col))
    s.append('<circle cx="%d" cy="%d" r="7" fill="none" stroke="%s" stroke-width="1.5"><animate attributeName="r" values="7;22;7" dur="3.2s" repeatCount="indefinite"/>'
             '<animate attributeName="opacity" values=".9;0;.9" dur="3.2s" repeatCount="indefinite"/></circle>' % (cx, cy, C_CYAN))
    s.append('<circle cx="%d" cy="%d" r="4.5" fill="%s"/>' % (cx, cy, C_CYAN))
    s.append('</g>')

    # titlebar
    for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        s.append('<circle cx="%d" cy="30" r="5.5" fill="%s"><animate attributeName="opacity" values="1;.45;1" dur="%ss" begin="%ss" repeatCount="indefinite"/></circle>' % (34 + i * 20, c, 3.4, i * 0.4))
    s.append('<text x="500" y="31" text-anchor="middle" fill="%s" font-size="12" letter-spacing="1.5">lazyer@github — ~/introduction</text>' % C_DIM)
    s.append('<line x1="0" y1="54" x2="%d" y2="54" stroke="%s"/>' % (W, C_LINE))

    # line 1
    s.append('<g clip-path="url(#type1)"><text x="52" y="81"><tspan class="pr">&#10095;</tspan><tspan class="cmd" dx="8">whoami</tspan></text></g>')

    # glitch title
    s.append('<g>' + reveal(1.1, 0.8))
    s.append('<text x="52" y="146" class="ttl g1" fill="#ff2d55" opacity="0">LAZYER</text>')
    s.append('<text x="52" y="146" class="ttl g2" fill="#00e5ff" opacity="0">LAZYER</text>')
    s.append('<text x="52" y="146" class="ttl" fill="url(#ttl)">LAZYER</text>')
    s.append('<text x="348" y="152" fill="%s" font-size="13" letter-spacing="2">/ 김인주 · backend &amp; data</text>' % C_DIM)
    s.append('</g>')

    # line 2
    s.append('<g clip-path="url(#type2)"><text x="52" y="192"><tspan class="pr">&#10095;</tspan><tspan class="cmd" dx="8">cat ./purpose</tspan></text></g>')
    # line 3
    s.append('<g clip-path="url(#type3)"><text x="52" y="224" class="out">systems that keep running when nobody is watching.</text></g>')
    s.append('<rect x="582" y="214" width="8" height="17" fill="%s" class="cur">'
             '<animate attributeName="opacity" values="0;0;1" keyTimes="0;.95;1" dur="4.6s" fill="freeze"/></rect>' % C_CYAN)

    # status chips
    chips = [("&#9679; available", C_GREEN), ("seoul, kr", C_MUT), ("always compiling", C_MUT)]
    x = 52
    for i, (label, col) in enumerate(chips):
        w = len(label.replace("&#9679;", "*")) * 7.0 + 26
        s.append('<g>' + reveal(4.5 + i * 0.18))
        s.append('<rect x="%.0f" y="256" width="%.0f" height="26" rx="13" fill="#11161f" stroke="%s"/>' % (x, w, C_LINE))
        s.append('<text x="%.0f" y="270" fill="%s" font-size="11.5" letter-spacing=".5">%s</text>' % (x + 13, col, label))
        s.append('</g>')
        x += w + 10

    # scanline
    s.append('<rect x="0" y="-60" width="%d" height="60" fill="url(#scan)" opacity=".6">'
             '<animate attributeName="y" from="-60" to="%d" dur="5.5s" repeatCount="indefinite"/></rect>' % (W, H))

    s.append('</g>')
    # animated border
    s.append('<rect x="1" y="1" width="%d" height="%d" rx="18" fill="none" stroke="%s" stroke-width="1.5"/>' % (W - 2, H - 2, C_LINE))
    s.append('<rect x="1" y="1" width="%d" height="%d" rx="18" fill="none" stroke="url(#sweep)" stroke-width="2" stroke-linecap="round" stroke-dasharray="360 %d">'
             '<animate attributeName="stroke-dashoffset" from="0" to="-%d" dur="7s" repeatCount="indefinite"/></rect>' % (W - 2, H - 2, peri - 360, peri))
    # corner brackets
    for px, py, sx, sy in [(18, 18, 1, 1), (W - 18, 18, -1, 1), (18, H - 18, 1, -1), (W - 18, H - 18, -1, -1)]:
        s.append('<path class="brk" d="M%d %d l0 %d M%d %d l%d 0">%s</path>' % (px, py, 22 * sy, px, py, 22 * sx, reveal(0.3, 0.6)))
    s.append('</svg>')
    return "\n".join(s)


# ─────────────────────────────────────────────────────── timeline
JOBS = [
    ("2018.08", "솔미테크", "R&amp;D",   ["ECG Peak Detection 알고리즘", "부정맥 분류 모델 · 온보드"], C_DIM),
    ("2020.03", "씨즈데이터", "개발팀",  ["OCR 성능 개선 · 요약엔진", "마이데이터 API · ADMS"],      C_BLUE),
    ("2022.12", "에잇퍼센트", "대외계",  ["신용정보원 전문 집중", "카카오뱅크 연계 시스템"],          C_PURP),
    ("2023.04", "퀀팃", "올리팀",       ["RA ‘올리’ 백엔드 · GraphQL", "K8s · ArgoCD · 관측 운영"],  C_CYAN),
]

def timeline():
    W, H = 1000, 330
    axis_y, x0, x1 = 112, 162, 838
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="career timeline">' % (W, H, W, H)]
    s.append('<title>career timeline</title>')
    s.append('<defs><linearGradient id="ax" gradientUnits="userSpaceOnUse" x1="162" y1="0" x2="838" y2="0">'
             '<stop offset="0" stop-color="%s"/><stop offset=".45" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (C_DIM, C_BLUE, C_CYAN))
    s.append('<radialGradient id="pulse"><stop offset="0" stop-color="%s" stop-opacity=".9"/><stop offset="1" stop-color="%s" stop-opacity="0"/></radialGradient></defs>' % (C_CYAN, C_CYAN))
    s.append('<style>%s' % BASE_CSS)
    s.append("""
    .yr{font-size:12.5px;letter-spacing:1px;fill:%s}
    .co{font-size:16px;font-weight:700}
    .rl{font-size:10.5px;letter-spacing:1px;fill:%s}
    .bu{font-size:11px;fill:%s}
    """ % (C_MUT, C_DIM, C_MUT))
    s.append('</style>')
    s.append('<rect width="%d" height="%d" rx="16" fill="%s" stroke="%s"/>' % (W, H, C_PANEL, C_LINE))

    span = x1 - x0
    n = len(JOBS)
    xs = [x0 + span * i / (n - 1) for i in range(n)]

    # axis draw-in
    s.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="url(#ax)" stroke-width="2.5" stroke-linecap="round" stroke-dasharray="%d" stroke-dashoffset="0">'
             '<animate attributeName="stroke-dashoffset" from="%d" to="0" dur="1.6s" fill="freeze"/></line>' % (x0, axis_y, x1, axis_y, span, span))
    # traveling comet
    s.append('<circle cy="%d" r="4" fill="%s"><animate attributeName="cx" values="%d;%d" dur="4.5s" begin="1.6s" repeatCount="indefinite"/>'
             '<animate attributeName="opacity" values="0;1;1;0" dur="4.5s" begin="1.6s" repeatCount="indefinite"/></circle>' % (axis_y, C_CYAN, x0, x1))

    for i, (yr, co, role, bullets, col) in enumerate(JOBS):
        x = xs[i]
        cur = (i == n - 1)
        d = 1.2 + i * 0.28
        s.append('<g>' + reveal(d, 0.75) + rise(d, 12, 0.75))
        s.append('<text x="%.0f" y="82" text-anchor="middle" class="yr">%s</text>' % (x, yr))
        if cur:
            s.append('<circle cx="%.0f" cy="%d" r="26" fill="url(#pulse)" opacity=".5"><animate attributeName="r" values="14;34;14" dur="3s" repeatCount="indefinite"/>'
                     '<animate attributeName="opacity" values=".55;0;.55" dur="3s" repeatCount="indefinite"/></circle>' % (x, axis_y))
        s.append('<circle cx="%.0f" cy="%d" r="8.5" fill="%s" stroke="%s" stroke-width="2.5"/>' % (x, axis_y, C_PANEL, col))
        s.append('<circle cx="%.0f" cy="%d" r="3.5" fill="%s"/>' % (x, axis_y, col))
        s.append('<line x1="%.0f" y1="%d" x2="%.0f" y2="150" stroke="%s" stroke-dasharray="2 3"/>' % (x, axis_y + 10, x, C_LINE))
        cw = 206.0
        cx = x - cw / 2
        s.append('<rect x="%.0f" y="150" width="%.0f" height="150" rx="12" fill="#11161f" stroke="%s"/>' % (cx, cw, C_LINE))
        s.append('<rect x="%.0f" y="150" width="%.0f" height="3" rx="1.5" fill="%s"/>' % (cx, cw, col))
        s.append('<text x="%.0f" y="180" class="co k" fill="%s">%s</text>' % (cx + 16, C_TXT, co))
        s.append('<text x="%.0f" y="202" class="rl k">%s%s</text>' % (cx + 16, role, " · 재직중" if cur else ""))
        for j, b in enumerate(bullets):
            s.append('<circle cx="%.0f" cy="%d" r="2" fill="%s"/>' % (cx + 19, 232 + j * 26, col))
            s.append('<text x="%.0f" y="%d" class="bu k">%s</text>' % (cx + 28, 232 + j * 26, b))
        s.append('</g>')
    s.append('</svg>')
    return "\n".join(s)


# ────────────────────────────────────────────────────────── stack
RINGS = [
    (152,  74,  30, True,  C_CYAN, ["Python", "Django", "GraphQL"]),
    (252, 118,  44, False, C_PURP, ["PostgreSQL", "Redis", "Celery", "Kafka"]),
    (362, 166,  62, True,  C_BLUE, ["Docker", "Kubernetes", "ArgoCD", "Grafana", "AWS"]),
]


def ellipse_path(cx, cy, rx, ry, clockwise):
    sweep = 1 if clockwise else 0
    return "M%d,%d A%d,%d 0 1,%d %d,%d A%d,%d 0 1,%d %d,%d" % (
        cx, cy - ry, rx, ry, sweep, cx, cy + ry, rx, ry, sweep, cx, cy - ry)


def stack():
    W, H = 1000, 430
    cx, cy = 500, 215
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="tech stack">' % (W, H, W, H)]
    s.append('<title>tech stack</title>')
    s.append('<defs><radialGradient id="core"><stop offset="0" stop-color="%s" stop-opacity=".8"/><stop offset="1" stop-color="%s" stop-opacity="0"/></radialGradient>' % (C_CYAN, C_CYAN))
    s.append('<radialGradient id="vig"><stop offset=".5" stop-color="#0d1117" stop-opacity="0"/><stop offset="1" stop-color="#070a0f" stop-opacity=".9"/></radialGradient></defs>')
    s.append('<style>%s' % BASE_CSS)
    s.append('.lb{font-size:12px;letter-spacing:.4px}')
    s.append('</style>')
    s.append('<rect width="%d" height="%d" rx="16" fill="%s" stroke="%s"/>' % (W, H, C_PANEL, C_LINE))

    dots = []
    for gy in range(26, H - 10, 34):
        for gx in range(26, W - 10, 34):
            dots.append('<circle cx="%d" cy="%d" r="1"/>' % (gx, gy))
    s.append('<g fill="%s" opacity=".35">%s</g>' % (C_LINE, "".join(dots)))
    s.append('<rect width="%d" height="%d" rx="16" fill="url(#vig)"/>' % (W, H))

    # orbit guides with flowing dashes
    for rx, ry, dur, cwise, col, items in RINGS:
        s.append('<ellipse cx="%d" cy="%d" rx="%d" ry="%d" fill="none" stroke="%s" stroke-width="1" stroke-dasharray="3 9" opacity=".8">'
                 '<animate attributeName="stroke-dashoffset" from="0" to="%d" dur="%ss" repeatCount="indefinite"/></ellipse>'
                 % (cx, cy, rx, ry, C_LINE, -96 if cwise else 96, dur / 3.0))

    # core
    s.append('<circle cx="%d" cy="%d" r="54" fill="url(#core)" opacity=".4"><animate attributeName="opacity" values=".22;.55;.22" dur="4s" repeatCount="indefinite"/></circle>' % (cx, cy))
    for i in range(3):
        s.append('<circle cx="%d" cy="%d" r="20" fill="none" stroke="%s" stroke-width="1.5" opacity="0">'
                 '<animate attributeName="r" values="20;64;64" keyTimes="0;.7;1" dur="4s" begin="%ss" repeatCount="indefinite"/>'
                 '<animate attributeName="opacity" values=".8;0;0" keyTimes="0;.7;1" dur="4s" begin="%ss" repeatCount="indefinite"/></circle>' % (cx, cy, C_CYAN, i * 1.33, i * 1.33))
    s.append('<circle cx="%d" cy="%d" r="36" fill="#11161f" stroke="%s" stroke-width="1.5"/>' % (cx, cy, C_CYAN))
    s.append('<text x="%d" y="%d" text-anchor="middle" fill="%s" font-size="15" font-weight="700" letter-spacing="1">core</text>' % (cx, cy - 7, C_TXT))
    s.append('<text x="%d" y="%d" text-anchor="middle" fill="%s" font-size="9.5" letter-spacing="1.4">BACKEND</text>' % (cx, cy + 10, C_DIM))

    delay = 0.9
    for rx, ry, dur, cwise, col, items in RINGS:
        path = ellipse_path(cx, cy, rx, ry, cwise)
        m = len(items)
        for i, name in enumerate(items):
            w = len(name) * 7.4 + 26
            s.append('<g>' + reveal(delay, 0.6))
            s.append('<animateMotion dur="%ss" repeatCount="indefinite" rotate="0" begin="-%.2fs" path="%s"/>' % (dur, dur * i / m, path))
            s.append('<rect x="%.1f" y="-13" width="%.1f" height="26" rx="13" fill="#11161f" stroke="%s" stroke-opacity=".75"/>' % (-w / 2, w, col))
            s.append('<circle cx="%.1f" cy="0" r="3" fill="%s"><animate attributeName="opacity" values="1;.3;1" dur="2.6s" begin="%ss" repeatCount="indefinite"/></circle>' % (-w / 2 + 12, col, i * 0.3))
            s.append('<text x="%.1f" y="1" fill="%s" class="lb">%s</text>' % (-w / 2 + 21, C_TXT, name))
            s.append('</g>')
            delay += 0.1
    s.append('</svg>')
    return "\n".join(s)


# ──────────────────────────────────────────────────────── divider
def divider():
    W, H = 1000, 14
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="">' % (W, H, W, H)]
    s.append('<defs><linearGradient id="d1" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="1000" y2="0">'
             '<stop offset="0" stop-color="%s" stop-opacity="0"/><stop offset=".5" stop-color="%s" stop-opacity=".8"/>'
             '<stop offset="1" stop-color="%s" stop-opacity="0"/></linearGradient>' % (C_DIM, C_DIM, C_DIM))
    s.append('<linearGradient id="d2" x1="0" y1="0" x2="1" y2="0">'
             '<stop offset="0" stop-color="%s" stop-opacity="0"/><stop offset=".5" stop-color="%s"/>'
             '<stop offset="1" stop-color="%s" stop-opacity="0"/></linearGradient></defs>' % (C_CYAN, C_CYAN, C_CYAN))
    s.append('<line x1="0" y1="7" x2="%d" y2="7" stroke="url(#d1)" stroke-width="1"/>' % W)
    s.append('<rect x="-260" y="5.5" width="260" height="3" rx="1.5" fill="url(#d2)">'
             '<animate attributeName="x" from="-260" to="%d" dur="4.5s" repeatCount="indefinite"/></rect>' % W)
    s.append('</svg>')
    return "\n".join(s)


for name, fn in [("hero", hero), ("timeline", timeline), ("stack", stack), ("divider", divider)]:
    p = os.path.join(OUT, name + ".svg")
    open(p, "w", encoding="utf-8").write(fn())
    print("%-14s %6d bytes" % (name + ".svg", os.path.getsize(p)))
