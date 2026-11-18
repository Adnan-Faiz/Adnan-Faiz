"""CHROME//DISTRICT - cyberpunk GitHub profile generator (v3).

Edit config.json, then run:  python generate.py
Needs: pip install fonttools
Outputs: README.md, assets/*.svg (desktop/mobile x dark/light), preview.html
"""
import base64, json, math, os, random, html

ROOT = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(ROOT, "config.json"), encoding="utf-8"))
ASSETS = os.path.join(ROOT, "assets")
os.makedirs(ASSETS, exist_ok=True)

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

class Font:
    def __init__(self, path):
        self.f = TTFont(path); self.gs = self.f.getGlyphSet(); self.cmap = self.f.getBestCmap()
        self.upm = self.f["head"].unitsPerEm; self.hmtx = self.f["hmtx"]
    def _g(self, c):
        return self.cmap.get(ord(c), self.cmap[32])
    def width(self, text, size, ls=0):
        s = size / self.upm
        return (sum(self.hmtx[self._g(c)][0] * s + ls for c in text) - ls) if text else 0
    def path(self, text, size, x, y, anchor="start", ls=0):
        s = size / self.upm; w = self.width(text, size, ls)
        cx = x - (w / 2 if anchor == "middle" else w if anchor == "end" else 0); d = []
        for c in text:
            g = self._g(c); pen = SVGPathPen(self.gs)
            self.gs[g].draw(TransformPen(pen, (s, 0, 0, -s, cx, y))); d.append(pen.getCommands())
            cx += self.hmtx[g][0] * s + ls
        return " ".join(d)
    def fit(self, text, size, maxw, ls=0):
        w = self.width(text, size, ls)
        return size if w <= maxw else size * maxw / w
    def wrap(self, text, size, maxw, ls=0):
        lines, cur = [], ""
        for word in text.split():
            t = (cur + " " + word).strip()
            if self.width(t, size, ls) <= maxw or not cur:
                cur = t
            else:
                lines.append(cur); cur = word
        if cur: lines.append(cur)
        return lines

ORB = Font(os.path.join(ROOT, "fonts", "orbitron-latin-900-normal.woff"))
RAJ = Font(os.path.join(ROOT, "fonts", "rajdhani-latin-700-normal.woff"))
MONO = "'Courier New', Consolas, 'Liberation Mono', monospace"
JP = "'Noto Sans JP', 'Hiragino Sans', 'Yu Gothic', 'Meiryo', 'MS Gothic', sans-serif"
esc = lambda s: html.escape(str(s), quote=True)

# ---------- THEMES ----------
DARK = dict(light=False, cya="#00f0ff", mag="#ff003c", yel="#fcee0a", grn="#39ff14", org="#ff8a00", pur="#b388ff", gold="#ffb000",
            panel="#07000f", card="#08000f", shard="#0d0b00", head="#05010a", txt="#ffffff", txt2="#d9d4ff", txt3="#b9b3d6",
            on="#0a0a0a", line="#2a1f3d", scan=("#000", .35), glow=(2.5, 8))
LIGHT = dict(light=True, cya="#007f99", mag="#d10038", yel="#9a7b00", grn="#2f7d00", org="#b85400", pur="#6a3fd1", gold="#a86a00",
             panel="#fbfaff", card="#ffffff", shard="#fffdf2", head="#f1edff", txt="#14081f", txt2="#33264d", txt3="#54486b",
             on="#ffffff", line="#d9d2ea", scan=("#3b2a66", .05), glow=(1.2, 3))

def defs(T):
    g1, g2 = T["glow"]; sc, so = T["scan"]
    return f"""<filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
<feGaussianBlur stdDeviation="{g1}" result="a"/><feGaussianBlur stdDeviation="{g2}" result="b"/>
<feMerge><feMergeNode in="b"/>{'' if T['light'] else '<feMergeNode in="b"/>'}<feMergeNode in="a"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2" result="a"/>
<feMerge><feMergeNode in="a"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1.4" fill="{sc}" opacity="{so}"/></pattern>"""

CSS = """
@keyframes flicker{0%,18%,22%,25%,53%,57%,100%{opacity:1}20%,24%,55%{opacity:.2}}
@keyframes blink{50%{opacity:0}}
@keyframes pulse{50%{opacity:.5}}
@keyframes win{0%,100%{opacity:1}50%{opacity:.15}}
@keyframes gm{0%,86%,100%{transform:translate(-4px,0)}88%{transform:translate(-14px,3px)}90%{transform:translate(8px,-2px)}92%{transform:translate(-20px,0)}}
@keyframes gc{0%,86%,100%{transform:translate(4px,0)}88%{transform:translate(16px,-3px)}90%{transform:translate(-9px,2px)}92%{transform:translate(22px,0)}}
@keyframes slice{0%,85%,100%{transform:translateX(0);opacity:0}86%{transform:translateX(-30px);opacity:1}89%{transform:translateX(25px);opacity:1}93%{transform:translateX(-12px);opacity:1}94%{opacity:0}}
@keyframes sweep{from{transform:translateY(-60px)}to{transform:translateY(1400px)}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes fill{to{transform:scaleX(1)}}
@keyframes boot{0%{opacity:0}25%{opacity:1}50%{opacity:.2}100%{opacity:1}}
@keyframes rev{to{opacity:1}}@keyframes hide{to{opacity:0}}
@keyframes stamp{0%{opacity:0;transform:scale(2.2) rotate(-14deg)}60%{opacity:1;transform:scale(.92) rotate(-8deg)}100%{opacity:1;transform:scale(1) rotate(-8deg)}}
.flk{animation:flicker 5s infinite}.blk{animation:blink 1s steps(1) infinite}.pls{animation:pulse 2s ease-in-out infinite}
.gm{animation:gm 3s steps(1) infinite}.gc{animation:gc 3s steps(1) infinite}.sl{animation:slice 3s steps(1) infinite}
.sweep{animation:sweep 5s linear infinite}
.in{opacity:0;animation:boot .5s steps(4) forwards}
.rev{opacity:0;animation:rev .1s forwards}.hide{animation:hide .1s forwards}
.bar{transform-box:fill-box;transform-origin:0 50%;transform:scaleX(0);animation:fill 1.3s cubic-bezier(.2,.8,.2,1) forwards}
.stamp{transform-box:fill-box;transform-origin:50% 50%;opacity:0;animation:stamp .45s cubic-bezier(.2,.8,.2,1) forwards}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.bar{transform:none!important}.in,.rev,.stamp{opacity:1!important}.hide{opacity:0!important}}
"""

def svg(T, w, h, body, css="", extra_defs="", label=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h:.0f}" width="{w}" height="{h:.0f}" role="img" aria-label="{esc(label)}">'
            f"<defs>{defs(T)}{extra_defs}</defs><style>{CSS}{css}</style>{body}</svg>")

def chip(x, y, w, h, cut=18):
    return f"M{x+cut},{y} H{x+w} V{y+h-cut} L{x+w-cut},{y+h} H{x} V{y+cut} Z"

def frame(x, y, w, h, c, cut, bg):
    d = chip(x, y, w, h, cut)
    return (f'<path d="{d}" fill="{bg}" stroke="{c}" stroke-width="2" filter="url(#glow)"/><path d="{d}" fill="{bg}"/>'
            f'<path d="{d}" fill="url(#scan)"/><path d="{d}" fill="none" stroke="{c}" stroke-width="2"/>')

def corners(x, y, w, h, c, s=18):
    return (f'<path d="M{x},{y+s} V{y} H{x+s} M{x+w-s},{y} H{x+w} V{y+s} M{x+w},{y+h-s} V{y+h} H{x+w-s} M{x+s},{y+h} H{x} V{y+h-s}" '
            f'fill="none" stroke="{c}" stroke-width="2.5"/>')

def glitch(T, font, text, size, x, y, ls=4, anchor="middle"):
    d = font.path(text, size, x, y, anchor, ls)
    main = "#fff6fb" if not T["light"] else T["txt"]
    return (f'<path d="{d}" fill="{T["mag"]}" class="gm" opacity=".85"/><path d="{d}" fill="{T["cya"]}" class="gc" opacity=".85"/>'
            f'<path d="{d}" fill="{main}"{"" if T["light"] else " filter=\"url(#soft)\""}/>'), d

def section_header(T, W, text, jp, y=58):
    t, _ = glitch(T, ORB, text, 40 if W >= 1000 else 34, W / 2, y, 6)
    bw = ORB.width(text, 40 if W >= 1000 else 34, 6) + 80
    return (f'<line x1="10" y1="{y-16}" x2="{W-10}" y2="{y-16}" stroke="{T["mag"]}" stroke-opacity=".5" stroke-width="2"/>'
            f'<rect x="{W/2-bw/2:.0f}" y="{y-50}" width="{bw:.0f}" height="66" fill="{T["head"]}" rx="4"/>{t}'
            f'<text x="{W-10}" y="{y-26}" text-anchor="end" font-family="{JP}" font-size="14" fill="{T["mag"]}">{jp}</text>')

# ---------- HERO (always dark: it's a night-city banner) ----------
def skyline(rnd, W, y0, hmin, hmax, fill, T, windows=False):
    out, x = [], -20
    while x < W + 20:
        w, h = rnd.randint(35, 90), rnd.randint(hmin, hmax)
        out.append(f'<rect x="{x}" y="{y0-h}" width="{w}" height="{h+300}" fill="{fill}"/>')
        if rnd.random() < .3:
            out.append(f'<rect x="{x+w//2-1}" y="{y0-h-rnd.randint(15,40)}" width="2" height="40" fill="{fill}"/>')
        if windows:
            for wy in range(y0 - h + 8, y0 + 240, 11):
                for wx in range(x + 5, x + w - 6, 9):
                    if rnd.random() < .22:
                        c = rnd.choice([T["cya"], T["yel"], T["mag"], "#ffb3c6", T["cya"]])
                        a = (f' class="w" style="animation-delay:-{rnd.uniform(0,6):.1f}s;animation-duration:{rnd.uniform(2,7):.1f}s"' if rnd.random() < .25 else "")
                        out.append(f'<rect x="{wx}" y="{wy}" width="4" height="5" fill="{c}" opacity=".85"{a}/>')
        x += w + rnd.randint(-6, 4)
    return "".join(out)

def rain(rnd, W, H):
    out = []
    for k in range(-1, int(H / 120) + 2):
        for _ in range(int(26 * W / 1000)):
            x = rnd.uniform(-100, W + 150) - 30 * k; y = rnd.uniform(0, 120) + 120 * k - 120; L = rnd.uniform(10, 26)
            out.append(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x - L*.25:.0f}" y2="{y + L:.0f}"/>')
    return "".join(out)

def hero(M):
    T = DARK; rnd = random.Random(1077)
    W, H = (600, 600) if M else (1000, 380)
    sky_y1, sky_y2 = (380, 420) if M else (300, 330)
    k = CFG.get("katakana", "")[:4]
    signx = W - 64 if M else 912
    vsign = "".join(f'<text x="{signx}" y="{110 + i*44}" text-anchor="middle">{esc(ch)}</text>' for i, ch in enumerate(k))
    if M:
        l1, l2 = CFG.get("name_lines", CFG["name"].split(" ", 1))
        size = min(ORB.fit(l1, 110, 440, 4), ORB.fit(l2, 110, 440, 4))
        t1, p1 = glitch(T, ORB, l1, size, 270, 250); t2, p2 = glitch(T, ORB, l2, size, 270, 250 + size * 1.05)
        title = t1 + t2; paths = [(p1, 250, size), (p2, 250 + size * 1.05, size)]; NX, by = 270, 250 + size * 1.05 + 46
    else:
        size = ORB.fit(CFG["name"], 92, 700, 4)
        title, p = glitch(T, ORB, CFG["name"], size, 470, 200); paths = [(p, 200, size)]; NX, by = 470, 226
    sub = CFG["title"]; subsize = RAJ.fit(sub, 24, 480 if M else 430, 2)
    subd = RAJ.path(sub, subsize, NX, by + 28, "middle", 2); bw = RAJ.width(sub, subsize, 2) + 46
    bands = "".join(f'<clipPath id="b{i}a"><rect y="{yy - s*.62:.0f}" width="{W}" height="16"/></clipPath><clipPath id="b{i}b"><rect y="{yy - s*.25:.0f}" width="{W}" height="11"/></clipPath>' for i, (_, yy, s) in enumerate(paths))
    slices = "".join(f'<g clip-path="url(#b{i}a)"><path d="{pp}" fill="{T["yel"]}" class="sl"/></g><g clip-path="url(#b{i}b)"><path d="{pp}" fill="{T["cya"]}" class="sl" style="animation-delay:-.4s"/></g>' for i, (pp, _, _) in enumerate(paths))
    welcome_y = by + (70 if M else 76)
    body = f"""<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="url(#sky)"/><rect width="{W}" height="{H}" fill="url(#haze)"/>
<g opacity=".9">{skyline(rnd, W, sky_y1, 120, 230, "#1c0a33", T)}</g><g>{skyline(rnd, W, sky_y2, 60, 170, "#0c0418", T, True)}</g>
<g opacity=".5"><g class="ring"><circle cx="120" cy="120" r="70" fill="none" stroke="{T['cya']}" stroke-width="1.5" stroke-dasharray="40 8 4 8"/>
<circle cx="120" cy="120" r="56" fill="none" stroke="{T['mag']}" stroke-width="1" stroke-dasharray="2 6"/></g></g>
<rect x="{signx-26}" y="72" width="52" height="{40 + 44*len(k)}" fill="#120010" stroke="{T['mag']}" stroke-width="2" filter="url(#glow)"/>
<g font-family="{JP}" font-size="38" font-weight="bold" fill="#ffd1dc" stroke="{T['mag']}" stroke-width="1" filter="url(#glow)" class="flk">{vsign}</g>
<g class="pls"><rect x="40" y="{H-108 if M else 228}" width="92" height="38" fill="#001418" stroke="{T['cya']}" stroke-width="2" filter="url(#glow)"/>
<text x="86" y="{H-79 if M else 257}" text-anchor="middle" font-family="{JP}" font-size="26" font-weight="bold" fill="#c8fbff">電脳</text></g>
<rect x="{NX-30}" y="0" width="60" height="{H}" fill="url(#beam)" class="pls"/>
<g stroke="#9ad7ff" stroke-opacity=".35" stroke-width="1"><g class="rain">{rain(rnd, W, H)}</g></g>
{title}{slices}
<g transform="translate(0 {by+14}) skewX(-14) translate(0 {-(by+14)})"><rect x="{NX - bw/2}" y="{by}" width="{bw}" height="38" fill="{T['yel']}"/>
<rect x="{NX + bw/2 + 4}" y="{by}" width="12" height="38" fill="{T['yel']}"/><rect x="{NX + bw/2 + 20}" y="{by}" width="6" height="38" fill="{T['yel']}"/></g>
<path d="{subd}" fill="#0a0a0a"/>
<text x="{NX}" y="{welcome_y}" text-anchor="middle" font-family="{JP}" font-size="15" fill="{T['cya']}" letter-spacing="{4 if M else 6}" filter="url(#glow)">ようこそ · WELCOME TO THE GRID</text>
<rect width="{W}" height="{H}" fill="url(#scan)"/><rect class="sweep" width="{W}" height="40" fill="{T['cya']}" opacity=".06"/>
{corners(14, 14, W-28, H-28, T['cya'])}
<g font-family="{MONO}" font-weight="bold" font-size="13" filter="url(#glow)">
<text x="34" y="42" fill="{T['cya']}">SYS://{esc(CFG['username'].upper())}  v4.0.4</text>
<text x="34" y="60" fill="{T['mag']}">NEURAL LINK ........ [OK]</text>
<text x="34" y="78" fill="{T['yel']}">NET::ONLINE  PING 7ms</text>
<text x="{W-34}" y="42" text-anchor="end" fill="#ff2a6d" class="blk">&#9679; LIVE</text>
<text x="34" y="{H-28}" fill="{T['cya']}" opacity=".85">&gt; jack_in --user {esc(CFG['username'].lower())}<tspan class="blk">_</tspan></text>
<text x="{W-34}" y="{H-28}" text-anchor="end" fill="{T['mag']}" opacity=".85">{esc(CFG.get('hud_right','SECTOR 07'))}</text></g></g>"""
    d = f"""<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#030008"/><stop offset=".55" stop-color="#1a0030"/><stop offset="1" stop-color="#4a0040"/></linearGradient>
<radialGradient id="haze" cx=".5" cy=".75" r=".6"><stop offset="0" stop-color="{T['mag']}" stop-opacity=".45"/><stop offset="1" stop-color="{T['mag']}" stop-opacity="0"/></radialGradient>
<linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{T['cya']}" stop-opacity="0"/><stop offset=".5" stop-color="{T['cya']}" stop-opacity=".25"/><stop offset="1" stop-color="{T['cya']}" stop-opacity="0"/></linearGradient>
{bands}<clipPath id="frame"><rect width="{W}" height="{H}"/></clipPath>"""
    css = """.w{animation:win 4s steps(1) infinite}
@keyframes rain{from{transform:translate(0,0)}to{transform:translate(-30px,120px)}}.rain{animation:rain .45s linear infinite}
.ring{transform-origin:120px 120px;animation:spin 14s linear infinite}"""
    return svg(T, W, H, body, css, d, f"{CFG['name']} - {CFG['title']}")

# ---------- CYBERWARE (skills) ----------
def cyberware(T, M):
    skills = CFG["skills"][:6]; cols = [T["cya"], T["mag"], T["yel"], T["grn"], T["org"], T["pur"]]
    W = 600 if M else 1000
    if M:
        cx, cy, r = W / 2, 200, 78; top = 350; H = top + 60 * len(skills) + 24
        bx0, bx1, segw = 30, 500, 23
    else:
        H = max(290, 140 + 34 * len(skills)); cx, cy, r = 120, H / 2 + 6, 82; top = 104
        bx0, bx1, segw = 440, 965, 25
    hexpts = " ".join(f"{cx + r*math.cos(a*math.pi/3 + math.pi/6):.1f},{cy + r*math.sin(a*math.pi/3 + math.pi/6):.1f}" for a in range(6))
    rows = []
    nseg = int((bx1 - bx0) / segw)
    for i, s in enumerate(skills):
        c = cols[i % len(cols)]; v = max(0, min(100, int(s["level"])))
        if M:
            ly = top + i * 60; y = ly + 30
            label = f'<text x="{bx0}" y="{ly}" fill="{T["txt2"]}" font-size="17">{esc(s["name"])}</text><text x="{W-30}" y="{ly}" text-anchor="end" fill="{c}" font-size="17">{v}%</text>'
        else:
            y = top + i * 34
            label = f'<text x="250" y="{y-3}" fill="{T["txt2"]}">{esc(s["name"])}</text><text x="975" y="{y-3}" text-anchor="end" fill="{c}">{v}%</text>'
        segs = "".join(f'<path d="M{bx0+k*segw},{y} l8,-18 h{segw-9} l-8,18 z" fill="{c}"/>' for k in range(round(v / 100 * nseg)))
        rows.append(label + f'<path d="M{bx0-4},{y+3} l9,-24 h{bx1-bx0+(segw if M else 7)} l-9,24 z" fill="none" stroke="{c}" stroke-opacity=".35"/>'
                    f'<g class="bar" style="animation-delay:{.3+i*.2:.1f}s" filter="url(#glow)">{segs}</g>')
    head_text = "CYBERWARE // INSTALLED"
    hx, hy = (30, 24) if M else (250, 24)
    head = RAJ.path(head_text, 22, hx + 12, hy + 23, ls=2)
    av = f'<path d="{ORB.path(CFG["initials"], 56, cx, cy + 20, "middle", 2)}" fill="{T["txt"]}" filter="url(#glow)" class="flk"/>'
    body = f"""{frame(4, 4, W-8, H-8, T['cya'], 26, T['panel'])}
<rect x="{hx}" y="{hy}" width="{RAJ.width(head_text, 22, 2) + 24:.0f}" height="30" fill="{T['yel']}"/><path d="{head}" fill="{T['on'] if T['light'] else '#0a0a0a'}"/>
<g font-family="{MONO}" font-weight="bold" font-size="15">
<text x="{W-25}" y="{hy+21 if not M else hy+21}" text-anchor="end" fill="{T['mag']}" class="blk">{'' if M else '&#9650; HUMANITY 100%'}</text>
<polygon points="{hexpts}" fill="{T['head']}" stroke="{T['mag']}" stroke-width="2.5" filter="url(#glow)"/>{av}
<polygon points="{hexpts}" fill="none" stroke="{T['mag']}" stroke-width="2.5"/>
<g class="ring"><circle cx="{cx}" cy="{cy}" r="{r+16}" fill="none" stroke="{T['cya']}" stroke-width="1.5" stroke-dasharray="30 10 6 10"/></g>
<text x="{cx}" y="{cy + r + 46 if M else H-14}" text-anchor="middle" fill="{T['cya']}" font-size="{15 if M else 13}" letter-spacing="2">CLASS: {esc(CFG['class'])}{'  ·  &#9650; HUMANITY 100%' if M else ''}</text>
{''.join(rows)}</g>"""
    css = f".ring{{transform-origin:{cx}px {cy}px;animation:spin 10s linear infinite}}"
    return svg(T, W, H, body, css, label="Skills: " + ", ".join(f"{s['name']} {s['level']}%" for s in skills))

# ---------- GIGS ----------
def gigs(T, M):
    items = CFG["gigs"][:6]; cols = [T["cya"], T["mag"], T["yel"], T["grn"], T["org"], T["pur"]]
    W = 600 if M else 1000
    ncol = 1 if M else 3
    CW, CH, GX, GY, TOP = (560, 178, 0, 18, 100) if M else (310, 190, 25, 22, 96)
    rows = (len(items) + ncol - 1) // ncol
    H = TOP + rows * CH + (rows - 1) * GY + 12
    fs = dict(title=34, desc=17, loot=16, tag=18) if M else dict(title=30, desc=13, loot=13, tag=17)
    cards = []
    for i, p in enumerate(items):
        c = cols[i % len(cols)]
        x = (20 if M else 10) + (i % ncol) * (CW + GX); y = TOP + (i // ncol) * (CH + GY)
        tsize = RAJ.fit(p["title"], fs["title"], CW - 40, 1)
        tag = p["tag"].upper(); tagd = RAJ.path(tag, fs["tag"], x + 30, y + 32, ls=1.5); tw = RAJ.width(tag, fs["tag"], 1.5) + 20
        loot = f"LOOT: {p['loot']}"
        lootsvg = (f'<text x="{x+CW/2:.0f}" y="{y+CH-32}" text-anchor="middle" font-family="{MONO}" font-size="{fs["loot"]}" font-weight="bold" fill="{c}">'
                   f'{esc(loot)}<tspan class="blk">{"_" if p.get("loading") else ""}</tspan></text>')
        if p.get("loading"):
            lootsvg = (f'<rect x="{x+20}" y="{y+CH-62}" width="{CW-40}" height="48" fill="{c}" opacity=".08"/>'
                       f'<rect x="{x+20}" y="{y+CH-62}" width="{CW-40}" height="48" fill="{c}" opacity=".18" class="ld"/>' + lootsvg)
        cards.append(f"""<g class="in" style="animation-delay:{.2 + i*.22:.2f}s">{frame(x, y, CW, CH, c, 20, T['card'])}
<rect x="{x+20}" y="{y+12}" width="{tw:.0f}" height="27" fill="{c}"/><path d="{tagd}" fill="{T['on']}"/>
<text x="{x+CW-16}" y="{y+31}" text-anchor="end" font-family="{MONO}" font-size="{13 if M else 12}" fill="{c}">#{i+1:02d}</text>
<path d="{RAJ.path(p['title'], tsize, x+20, y+(80 if M else 78), ls=1)}" fill="{T['txt']}"/>
<text x="{x+20}" y="{y+(106 if M else 104)}" font-family="{MONO}" font-size="{fs['desc']}" fill="{T['txt3']}">{esc(p['desc'])}</text>
<rect x="{x+20}" y="{y+CH-62}" width="{CW-40}" height="48" fill="none" stroke="{c}" stroke-opacity=".5" stroke-dasharray="4 4"/>
{lootsvg}</g>""")
    body = section_header(T, W, "// GIGS", "依頼") + "".join(cards)
    css = (".ld{transform-box:fill-box;transform-origin:0 50%;animation:ld 2.4s ease-in-out infinite}"
           "@keyframes ld{0%{transform:scaleX(0)}70%{transform:scaleX(1)}100%{transform:scaleX(1);opacity:0}}")
    return svg(T, W, H, body, css, label="Work: " + "; ".join(f"{p['tag']}: {p['title']} ({p['loot']})" for p in items))

# ---------- MISSION LOG ----------
def missions(T, M):
    ms = CFG["missions"]; n = len(ms)
    W = 600 if M else 1000
    if M:
        TOP = 150; STEP = 118; H = TOP + STEP * (n - 1) + 90; lx = 60
        track = f'<line x1="{lx}" y1="{TOP}" x2="{lx}" y2="{TOP + STEP*(n-1)}" stroke="{T["line"]}" stroke-width="4"/>'
        prog = f'<line x1="{lx}" y1="{TOP}" x2="{lx}" y2="{TOP + STEP*(n-2)}" stroke="{T["cya"]}" stroke-width="4" class="trk" filter="url(#glow)"/>'
        dot = f'<circle cx="{lx}" cy="{TOP}" r="5" fill="{T["txt"]}" class="dotv"/>'
    else:
        TOP = 175; x0, x1 = 115, 870; STEP = (x1 - x0) / (n - 1); H = 330
        track = f'<line x1="{x0}" y1="{TOP}" x2="{x1}" y2="{TOP}" stroke="{T["line"]}" stroke-width="4"/>'
        prog = f'<line x1="{x0}" y1="{TOP}" x2="{x0 + STEP*(n-2)}" y2="{TOP}" stroke="{T["cya"]}" stroke-width="4" class="trk" filter="url(#glow)"/>'
        dot = f'<circle cx="{x0}" cy="{TOP}" r="5" fill="{T["txt"]}" class="doth"/>'
    nodes = []
    for i, m in enumerate(ms):
        c = T["mag"] if m.get("next") else (T["yel"] if m.get("current") else T["cya"])
        d = .4 + i * .45
        if M:
            nx, ny = lx, TOP + i * STEP; tx = lx + 44
            rsize = RAJ.fit(m["role"], 26, W - tx - 30, .5)
            txt = (f'<text x="{tx}" y="{ny-26}" font-family="{MONO}" font-size="14" fill="{c}" font-weight="bold">{esc(m["when"])} · {esc(m["lvl"])}</text>'
                   f'<path d="{RAJ.path(m["role"], rsize, tx, ny+6, ls=.5)}" fill="{T["txt"]}"/>'
                   f'<text x="{tx}" y="{ny+32}" font-family="{MONO}" font-size="15" fill="{T["txt3"]}">{esc(m["org"])}</text>')
        else:
            nx, ny = x0 + i * STEP, TOP
            rsize = RAJ.fit(m["role"], 22, STEP - 16, .5)
            txt = (f'<text x="{nx:.0f}" y="{ny-58}" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{c}" font-weight="bold">{esc(m["when"])}</text>'
                   f'<text x="{nx:.0f}" y="{ny-36}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{T["txt3"]}">{esc(m["lvl"])}</text>'
                   f'<path d="{RAJ.path(m["role"], rsize, nx, ny+52, "middle", .5)}" fill="{T["txt"]}"/>'
                   f'<text x="{nx:.0f}" y="{ny+76}" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{T["txt3"]}">{esc(m["org"])}</text>')
        if m.get("next"):
            node = (f'<circle cx="{nx:.0f}" cy="{ny:.0f}" r="16" fill="{T["panel"]}" stroke="{c}" stroke-width="2.5" stroke-dasharray="5 4" class="ring{i}"/>'
                    f'<text x="{nx:.0f}" y="{ny+6:.0f}" text-anchor="middle" font-family="{MONO}" font-size="16" font-weight="bold" fill="{c}" class="blk">?</text>')
        else:
            node = (f'<circle cx="{nx:.0f}" cy="{ny:.0f}" r="15" fill="{T["panel"]}" stroke="{c}" stroke-width="3" filter="url(#glow)"/>'
                    f'<circle cx="{nx:.0f}" cy="{ny:.0f}" r="7" fill="{c}"{" class=\"pls\"" if m.get("current") else ""}/>')
            if m.get("current"):
                node += f'<circle cx="{nx:.0f}" cy="{ny:.0f}" r="24" fill="none" stroke="{c}" stroke-width="1.5" class="ping"/>'
        nodes.append(f'<g class="in" style="animation-delay:{d:.2f}s">{node}{txt}</g>')
    body = f"""{frame(4, 4, W-8, H-8, T['cya'], 26, T['panel'])}
{section_header(T, W, "// MISSION LOG", "経歴", 66)}
{track}{prog}{dot}{''.join(nodes)}"""
    span = (STEP * (n - 2))
    css = (f".trk{{transform-box:fill-box;transform-origin:{'50% 0' if M else '0 50%'};transform:{'scaleY(0)' if M else 'scaleX(0)'};animation:trk 2.2s cubic-bezier(.2,.8,.2,1) .3s forwards}}"
           f"@keyframes trk{{to{{transform:{'scaleY(1)' if M else 'scaleX(1)'}}}}}"
           f".doth{{animation:dh 3.2s linear 2.5s infinite}}@keyframes dh{{from{{transform:translateX(0)}}to{{transform:translateX({span:.0f}px)}}}}"
           f".dotv{{animation:dv 3.2s linear 2.5s infinite}}@keyframes dv{{from{{transform:translateY(0)}}to{{transform:translateY({span:.0f}px)}}}}"
           ".ping{transform-box:fill-box;transform-origin:50% 50%;animation:ping 1.8s ease-out infinite}@keyframes ping{from{transform:scale(.6);opacity:1}to{transform:scale(1.6);opacity:0}}"
           "@media (prefers-reduced-motion:reduce){.trk{transform:none!important}}")
    return svg(T, W, H, body, css, label="Career: " + " → ".join(f"{m['when']} {m['role']} ({m['org']})" for m in ms))

# ---------- DATA SHARD (papers + designs) ----------
def shard(T, M):
    papers = CFG["papers"] + ([CFG["designs"]] if CFG.get("designs") else [])
    W = 600 if M else 1000
    rnd = random.Random(7)
    rows = []; y = 112 if not M else 150
    for i, pt in enumerate(papers):
        t = f"{pt.get('venue','IEEE')} // {pt['title']}"; d = 1.0 + i * .7
        hexg = " ".join(f"{rnd.randint(0,255):02X}" for _ in range(6)) + " ## ## ##"
        if M:
            lines = RAJ.wrap(t, 21, W - 110, .4); y0 = y
            paths = "".join(f'<path d="{RAJ.path(L, 21, 80, y0 + j*27, ls=.4)}" fill="{T["txt"]}"/>' for j, L in enumerate(lines))
            y += 27 * len(lines) + 22
            num_x, hx = 40, 80
        else:
            size = RAJ.fit(t, 22, 790, .4); y0 = y
            paths = f'<path d="{RAJ.path(t, size, 150, y0, ls=.4)}" fill="{T["txt"]}"/>'
            y += 44; num_x, hx = 130, 150
        rows.append(f"""<text x="{hx}" y="{y0}" font-size="18" fill="{T['cya']}" class="hide" style="animation-delay:{d:.1f}s">{hexg}</text>
<g class="rev" style="animation-delay:{d:.1f}s">{paths}</g>
<text x="{num_x}" y="{y0}" text-anchor="{'start' if M else 'end'}" font-size="14" fill="{T['yel']}" class="rev" style="animation-delay:{d:.1f}s">{i+1:02d}</text>""")
    H = y + (0 if M else 4)
    total = 1.0 + (len(papers) - 1) * .7
    if M:
        head = f"""<g transform="translate({W-60},62)" filter="url(#glow)" class="pls"><polygon points="0,-30 22,0 0,30 -22,0" fill="none" stroke="{T['yel']}" stroke-width="3"/><polygon points="0,-17 12,0 0,17 -12,0" fill="{T['yel']}"/></g>
<text x="40" y="50" font-size="19" fill="{T['yel']}" letter-spacing="3" filter="url(#glow)">DATA SHARDS</text>
<rect x="40" y="64" width="380" height="12" fill="none" stroke="{T['yel']}" stroke-opacity=".6"/>
<rect x="42" y="66" width="376" height="8" fill="{T['yel']}" class="prog" style="animation-duration:{total:.1f}s"/>
<text x="40" y="104" font-size="14" fill="{T['mag']}" class="rev" style="animation-delay:{total:.1f}s">ACCESS GRANTED</text>
<text x="{W-40}" y="104" text-anchor="end" font-size="13" fill="{T['yel']}" class="pls">[ TAP TO OPEN IEEE ]</text>"""
    else:
        head = f"""<g transform="translate(70,{H/2:.0f})" filter="url(#glow)" class="pls"><polygon points="0,-42 30,0 0,42 -30,0" fill="none" stroke="{T['yel']}" stroke-width="3"/><polygon points="0,-24 17,0 0,24 -17,0" fill="{T['yel']}"/></g>
<text x="150" y="44" font-size="17" fill="{T['yel']}" letter-spacing="3" filter="url(#glow)">DATA SHARDS // DECRYPTING</text>
<rect x="150" y="58" width="440" height="12" fill="none" stroke="{T['yel']}" stroke-opacity=".6"/>
<rect x="152" y="60" width="436" height="8" fill="{T['yel']}" class="prog" style="animation-duration:{total:.1f}s"/>
<text x="975" y="44" text-anchor="end" font-size="13" fill="{T['mag']}" class="rev" style="animation-delay:{total:.1f}s">ACCESS GRANTED</text>
<text x="975" y="70" text-anchor="end" font-size="12" fill="{T['yel']}" class="pls">{esc(CFG.get('shard_stats',''))}</text>"""
    body = f"""{frame(4, 4, W-8, H-8, T['yel'], 22, T['shard'])}<g font-family="{MONO}" font-weight="bold">{head}{''.join(rows)}</g>"""
    css = ".prog{transform-box:fill-box;transform-origin:0 50%;transform:scaleX(0);animation:fill 2.2s steps(22) forwards}"
    return svg(T, W, H, body, css, label="Publications and designs: " + "; ".join(p["title"] for p in papers))

# ---------- ACHIEVEMENTS ----------
def star(cx, cy, R, r):
    return " ".join(f"{cx + (R if k % 2 == 0 else r)*math.cos(-math.pi/2 + k*math.pi/5):.1f},{cy + (R if k % 2 == 0 else r)*math.sin(-math.pi/2 + k*math.pi/5):.1f}" for k in range(10))

def achievements(T, M):
    items = CFG["achievements"]
    rc = {"LEGENDARY": T["gold"], "EPIC": T["pur"], "RARE": T["cya"], "COMMON": T["grn"]}
    W = 600 if M else 1000; ncol = 2 if M else 3
    CW, CH, GX, GY, TOP = (270, 200, 20, 18, 100) if M else (310, 150, 25, 18, 96)
    rows = (len(items) + ncol - 1) // ncol
    H = TOP + rows * CH + (rows - 1) * GY + 16
    cards = []
    for i, a in enumerate(items):
        c = rc.get(a["rarity"], T["cya"])
        x = 20 + (i % ncol) * (CW + GX) if M else 10 + (i % ncol) * (CW + GX); y = TOP + (i // ncol) * (CH + GY)
        mx, my = x + 44, y + 50
        hexm = " ".join(f"{mx + 26*math.cos(k*math.pi/3 + math.pi/6):.1f},{my + 26*math.sin(k*math.pi/3 + math.pi/6):.1f}" for k in range(6))
        medal = (f'<polygon points="{hexm}" fill="{c}" fill-opacity=".14" stroke="{c}" stroke-width="2.5" filter="url(#glow)"/>'
                 f'<polygon points="{star(mx, my, 13, 5.5)}" fill="{c}"{" class=\"pls\"" if a["rarity"] == "LEGENDARY" else ""}/>')
        d = .3 + i * .18
        if M:
            tl = RAJ.wrap(a["title"], 22, CW - 36, .3)[:2]
            tpaths = "".join(f'<path d="{RAJ.path(L, 22, x+18, y+108 + j*25, ls=.3)}" fill="{T["txt"]}"/>' for j, L in enumerate(tl))
            by = y + 108 + 25 * len(tl) + 2
            meta = (f'<text x="{x+18}" y="{by}" font-family="{MONO}" font-size="13" fill="{T["txt3"]}">{esc(a["by"][:30])}</text>'
                    f'<text x="{x+CW-14}" y="{y+34}" text-anchor="end" font-family="{MONO}" font-size="12" font-weight="bold" fill="{c}">{a["rarity"]}</text>'
                    f'<text x="{x+CW-14}" y="{y+54}" text-anchor="end" font-family="{MONO}" font-size="13" fill="{T["txt3"]}">{esc(a["when"])}</text>')
            stamp_xy = (x + CW - 92, y + CH - 40)
        else:
            tl = RAJ.wrap(a["title"], 21, CW - 104, .3)[:2]
            tpaths = "".join(f'<path d="{RAJ.path(L, 21, x+86, y+46 + j*23, ls=.3)}" fill="{T["txt"]}"/>' for j, L in enumerate(tl))
            meta = (f'<text x="{x+86}" y="{y+46 + 23*len(tl) + 4}" font-family="{MONO}" font-size="12" fill="{T["txt3"]}">{esc(a["by"])}</text>'
                    f'<text x="{x+18}" y="{y+CH-18}" font-family="{MONO}" font-size="11" font-weight="bold" fill="{c}">{a["rarity"]}</text>'
                    f'<text x="{x+CW-16}" y="{y+CH-18}" text-anchor="end" font-family="{MONO}" font-size="12" fill="{T["txt3"]}">{esc(a["when"])}</text>')
            stamp_xy = (x + CW / 2 - 38, y + CH - 36)
        sx, sy = stamp_xy
        stamp = (f'<g class="stamp" style="animation-delay:{d + 1.2:.2f}s"><rect x="{sx}" y="{sy}" width="76" height="22" fill="none" stroke="{c}" stroke-width="2"/>'
                 f'<text x="{sx+38}" y="{sy+16}" text-anchor="middle" font-family="{MONO}" font-size="11" font-weight="bold" fill="{c}">UNLOCKED</text></g>')
        cards.append(f'<g class="in" style="animation-delay:{d:.2f}s">{frame(x, y, CW, CH, c, 16, T["card"])}{medal}{tpaths}{meta}</g>{stamp}')
    body = section_header(T, W, "// TROPHIES", "実績") + "".join(cards)
    return svg(T, W, H, body, label="Achievements: " + "; ".join(f"{a['title']} ({a['by']}, {a['when']})" for a in items))

# ---------- FOOTER ----------
def footer(T, M):
    W = 600 if M else 1000; H = 100 if M else 70
    lines = ["CONNECTION TERMINATED", "SEE YOU IN THE GRID"] if M else ["CONNECTION TERMINATED // SEE YOU IN THE GRID"]
    out = ""
    for j, L in enumerate(lines):
        t = RAJ.path(L, 22 if M else 20, W / 2, (40 + j * 32) if M else 47, "middle", 3)
        out += f'<path d="{t}" fill="{T["mag"]}" class="gm" opacity=".7"/><path d="{t}" fill="{T["cya"]}" class="gc" opacity=".7"/><path d="{t}" fill="{T["txt"]}" class="flk"/>'
    body = f"""<rect width="{W}" height="{H}" fill="{T['head']}"/><rect width="{W}" height="{H}" fill="url(#scan)"/>
<rect width="{W}" height="2" fill="{T['mag']}" filter="url(#glow)"/><rect y="{H-2}" width="{W}" height="2" fill="{T['cya']}" filter="url(#glow)"/>
{out}<text x="24" y="{H/2+5:.0f}" font-family="{MONO}" font-size="12" fill="{T['mag']}" class="blk">&#9679;</text>"""
    return svg(T, W, H, body, label="See you in the grid")

# ---------- BUILD ----------
PANELS = [("cyberware", cyberware), ("gigs", gigs), ("missions", missions), ("shard", shard), ("trophies", achievements), ("footer", footer)]
files = {"hero.svg": hero(False), "hero-m.svg": hero(True)}
for name, fn in PANELS:
    files[f"{name}.svg"] = fn(DARK, False)
    files[f"{name}-light.svg"] = fn(LIGHT, False)
    files[f"{name}-m.svg"] = fn(DARK, True)
    files[f"{name}-m-light.svg"] = fn(LIGHT, True)
for old in os.listdir(ASSETS):
    if old.endswith(".svg") and old not in files and not old.startswith("snake"):
        os.remove(os.path.join(ASSETS, old))
for k, v in files.items():
    open(os.path.join(ASSETS, k), "w", encoding="utf-8").write(v)

MQ = "(max-width: 600px)"
def pic(name, alt, themed=True, href=None):
    src = []
    if themed:
        src.append(f'<source media="{MQ} and (prefers-color-scheme: light)" srcset="assets/{name}-m-light.svg"/>')
    src.append(f'<source media="{MQ}" srcset="assets/{name}-m.svg"/>')
    if themed:
        src.append(f'<source media="(prefers-color-scheme: light)" srcset="assets/{name}-light.svg"/>')
    p = "<picture>\n    " + "\n    ".join(src) + f'\n    <img src="assets/{name}.svg" width="100%" alt="{esc(alt)}"/>\n  </picture>'
    if href:
        p = f'<a href="{esc(href)}">\n  {p}\n  </a>'
    return f'<p align="center">\n  {p}\n</p>\n'

tag = "<br/>\n  ".join(f"<samp>&gt; {esc(t)}</samp>" for t in CFG["tagline"])
readme = (f"<!-- CHROME//DISTRICT · generated by generate.py · edit config.json and re-run -->\n"
          + pic("hero", f"{CFG['name']} - {CFG['title']}", themed=False)
          + f'\n<p align="center">\n  {tag}\n</p>\n\n'
          + pic("cyberware", "Skills") + "\n"
          + pic("gigs", "Work") + "\n"
          + pic("missions", "Mission log: career timeline") + "\n"
          + pic("shard", "Publications and designs (opens IEEE Xplore author profile)", href=CFG.get("ieee_profile")) + "\n"
          + pic("trophies", "Achievements and certifications") + "\n"
          + '<p align="center">\n  <picture>\n    <source media="(prefers-color-scheme: light)" srcset="assets/snake-light.svg"/>\n'
          + '    <img src="assets/snake.svg" width="100%" alt="Contribution snake"/>\n  </picture>\n</p>\n\n'
          + pic("footer", "See you in the grid"))
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(readme)

# ---------- PREVIEW: all four variants side by side ----------
def uri(n):
    p = os.path.join(ASSETS, n)
    data = files.get(n) or (open(p, encoding="utf-8").read() if os.path.exists(p) else
           '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 120"><text x="440" y="66" text-anchor="middle" font-family="monospace" font-size="16" fill="#6e7681">[ snake appears after the first GitHub Action run ]</text></svg>')
    return "data:image/svg+xml;base64," + base64.b64encode(data.encode()).decode()
def column(label, mobile, light, width, bg, fg):
    sfx = ("-m" if mobile else "") + ("-light" if light else "")
    imgs = [f'<img src="{uri("hero" + ("-m" if mobile else "") + ".svg")}" style="width:100%;display:block;margin-bottom:12px">',
            f'<p style="text-align:center;font:{12 if mobile else 14}px/1.7 monospace;color:{fg};margin:0 0 14px">' + "<br>".join("&gt; " + esc(t) for t in CFG["tagline"]) + "</p>"]
    for name, _ in PANELS[:-1]:
        imgs.append(f'<img src="{uri(name + sfx + ".svg")}" style="width:100%;display:block;margin-bottom:14px">')
    imgs.append(f'<img src="{uri("snake" + ("-light" if light else "") + ".svg")}" style="width:100%;display:block;margin-bottom:14px">')
    imgs.append(f'<img src="{uri("footer" + sfx + ".svg")}" style="width:100%;display:block">')
    return (f'<div style="flex:0 0 {width}px"><div style="font:600 13px monospace;color:#8b949e;margin:0 0 8px">{label}</div>'
            f'<div style="background:{bg};border:1px solid #30363d;border-radius:8px;padding:16px">{"".join(imgs)}</div></div>')
open(os.path.join(ROOT, "preview.html"), "w", encoding="utf-8").write(
    '<!DOCTYPE html><html><head><meta charset="utf-8"><title>CHROME//DISTRICT preview</title></head>'
    '<body style="margin:0;background:#010409;padding:24px"><div style="display:flex;gap:24px;align-items:flex-start;overflow-x:auto">'
    + column("DESKTOP · DARK", False, False, 880, "#0d1117", "#c9d1d9")
    + column("DESKTOP · LIGHT", False, True, 880, "#ffffff", "#1f2328")
    + column("PHONE · DARK", True, False, 390, "#0d1117", "#c9d1d9")
    + column("PHONE · LIGHT", True, True, 390, "#ffffff", "#1f2328")
    + "</div></body></html>")
print("generated", len(files), "SVGs + README.md + preview.html")
