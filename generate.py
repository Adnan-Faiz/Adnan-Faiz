"""CHROME//DISTRICT - cyberpunk GitHub profile generator.

Edit config.json, then run:  python generate.py
Needs: pip install fonttools pillow
Outputs: README.md, assets/*.svg, preview.html
"""
import base64, io, json, math, os, random, html, re

ROOT = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(ROOT, "config.json"), encoding="utf-8"))
ASSETS = os.path.join(ROOT, "assets")
os.makedirs(ASSETS, exist_ok=True)
random.seed(1077)

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

class Font:
    def __init__(self, path):
        self.f = TTFont(path)
        self.gs = self.f.getGlyphSet()
        self.cmap = self.f.getBestCmap()
        self.upm = self.f["head"].unitsPerEm
        self.hmtx = self.f["hmtx"]

    def width(self, text, size, ls=0):
        s = size / self.upm
        w = sum(self.hmtx[self.cmap.get(ord(c), self.cmap[32])][0] * s + ls for c in text)
        return w - ls if text else 0

    def path(self, text, size, x, y, anchor="start", ls=0):
        s = size / self.upm
        w = self.width(text, size, ls)
        cx = x - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
        d = []
        for c in text:
            g = self.cmap.get(ord(c), self.cmap[32])
            pen = SVGPathPen(self.gs)
            self.gs[g].draw(TransformPen(pen, (s, 0, 0, -s, cx, y)))
            d.append(pen.getCommands())
            cx += self.hmtx[g][0] * s + ls
        return " ".join(d)

    def fit(self, text, size, maxw, ls=0):
        w = self.width(text, size, ls)
        return size if w <= maxw else size * maxw / w

ORB = Font(os.path.join(ROOT, "fonts", "orbitron-latin-900-normal.woff"))
RAJ = Font(os.path.join(ROOT, "fonts", "rajdhani-latin-700-normal.woff"))
MONO = "'Courier New', Consolas, 'Liberation Mono', monospace"
JP = "'Noto Sans JP', 'Hiragino Sans', 'Yu Gothic', 'Meiryo', 'MS Gothic', sans-serif"
MAG, CYA, YEL, RED, GRN, ORG = "#ff003c", "#00f0ff", "#fcee0a", "#ff2a6d", "#39ff14", "#ff8a00"
SKILL_COLORS = [CYA, MAG, YEL, GRN, ORG, "#b388ff"]
esc = lambda s: html.escape(str(s), quote=True)

DEFS = """<filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
<feGaussianBlur stdDeviation="2.5" result="a"/><feGaussianBlur stdDeviation="8" result="b"/>
<feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="a"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2" result="a"/>
<feMerge><feMergeNode in="a"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1.4" fill="#000" opacity=".35"/></pattern>"""

CSS = """
@keyframes flicker{0%,18%,22%,25%,53%,57%,100%{opacity:1}20%,24%,55%{opacity:.2}}
@keyframes blink{50%{opacity:0}}
@keyframes pulse{50%{opacity:.5}}
@keyframes win{0%,100%{opacity:1}50%{opacity:.15}}
@keyframes gm{0%,86%,100%{transform:translate(-4px,0)}88%{transform:translate(-14px,3px)}90%{transform:translate(8px,-2px)}92%{transform:translate(-20px,0)}}
@keyframes gc{0%,86%,100%{transform:translate(4px,0)}88%{transform:translate(16px,-3px)}90%{transform:translate(-9px,2px)}92%{transform:translate(22px,0)}}
@keyframes slice{0%,85%,100%{transform:translateX(0);opacity:0}86%{transform:translateX(-30px);opacity:1}89%{transform:translateX(25px);opacity:1}93%{transform:translateX(-12px);opacity:1}94%{opacity:0}}
@keyframes sweep{from{transform:translateY(-60px)}to{transform:translateY(440px)}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes fill{to{transform:scaleX(1)}}
.flk{animation:flicker 5s infinite}.blk{animation:blink 1s steps(1) infinite}.pls{animation:pulse 2s ease-in-out infinite}
.gm{animation:gm 3s steps(1) infinite}.gc{animation:gc 3s steps(1) infinite}.sl{animation:slice 3s steps(1) infinite}
.sweep{animation:sweep 4s linear infinite}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.bar,.prog{transform:none!important}.in,.rev{opacity:1!important}.hide{opacity:0!important}}
"""

def svg(w, h, body, extra_css="", extra_defs="", label=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{esc(label)}">'
            f"<defs>{DEFS}{extra_defs}</defs><style>{CSS}{extra_css}</style>{body}</svg>")

def chip(x, y, w, h, cut=18):
    return f"M{x+cut},{y} H{x+w} V{y+h-cut} L{x+w-cut},{y+h} H{x} V{y+cut} Z"

def frame(x, y, w, h, c, cut, bg):
    d = chip(x, y, w, h, cut)
    return (f'<path d="{d}" fill="{bg}" stroke="{c}" stroke-width="2" filter="url(#glow)"/><path d="{d}" fill="{bg}"/>'
            f'<path d="{d}" fill="url(#scan)"/><path d="{d}" fill="none" stroke="{c}" stroke-width="2"/>')

def corners(x, y, w, h, c, s=18):
    return (f'<path d="M{x},{y+s} V{y} H{x+s} M{x+w-s},{y} H{x+w} V{y+s} M{x+w},{y+h-s} V{y+h} H{x+w-s} M{x+s},{y+h} H{x} V{y+h-s}" '
            f'fill="none" stroke="{c}" stroke-width="2.5"/>')

def glitch_title(font, text, size, x, y, ls=4, main="#fff6fb"):
    d = font.path(text, size, x, y, "middle", ls)
    return (f'<path d="{d}" fill="{MAG}" class="gm" opacity=".85"/><path d="{d}" fill="{CYA}" class="gc" opacity=".85"/>'
            f'<path d="{d}" fill="{main}" filter="url(#soft)"/>'), d

def skyline(y0, hmin, hmax, fill, windows=False):
    out, x = [], -20
    while x < 1020:
        w, h = random.randint(35, 90), random.randint(hmin, hmax)
        out.append(f'<rect x="{x}" y="{y0-h}" width="{w}" height="{h+80}" fill="{fill}"/>')
        if random.random() < .3:
            out.append(f'<rect x="{x+w//2-1}" y="{y0-h-random.randint(15,40)}" width="2" height="40" fill="{fill}"/>')
        if windows:
            for wy in range(y0 - h + 8, y0 + 60, 11):
                for wx in range(x + 5, x + w - 6, 9):
                    if random.random() < .22:
                        c = random.choice([CYA, YEL, MAG, "#ffb3c6", CYA])
                        a = (f' class="w" style="animation-delay:-{random.uniform(0,6):.1f}s;animation-duration:{random.uniform(2,7):.1f}s"'
                             if random.random() < .25 else "")
                        out.append(f'<rect x="{wx}" y="{wy}" width="4" height="5" fill="{c}" opacity=".85"{a}/>')
        x += w + random.randint(-6, 4)
    return "".join(out)

def rain():
    out = []
    for k in range(-1, 4):
        for _ in range(26):
            x = random.uniform(-100, 1150) - 30 * k
            y = random.uniform(0, 120) + 120 * k - 120
            L = random.uniform(10, 26)
            out.append(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x - L*.25:.0f}" y2="{y + L:.0f}"/>')
    return "".join(out)

# ---------- PHOTO HELPERS ----------
def img_data(p, height):
    if not p:
        return None
    from PIL import Image
    im = Image.open(os.path.join(ROOT, p)).convert("RGBA")
    im = im.resize((round(im.width * height / im.height), height), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, "WEBP", quality=84, method=6)
    return ("data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode(), im.width, im.height)

def hero_photo_svg(hp):
    if not hp:
        return ""
    uri, w, h = hp
    s = CFG.get('hero_photo_height', 460) / h; w, h = w * s, h * s
    x, y = 790 - w / 2, max(380 - h, 14)
    img = f'href="{uri}" x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}"'
    return f"""<g class="holo">
<image {img} filter="url(#rimc)" opacity=".9"/>
<image {img}/>
<image {img} class="pgc" filter="url(#tintc)" style="mix-blend-mode:screen"/>
<image {img} class="pgm" filter="url(#tintm)" style="mix-blend-mode:screen"/>
<g mask="url(#pmask)"><rect x="{x:.0f}" y="0" width="{w:.0f}" height="380" fill="url(#scan)"/>
<rect x="{x:.0f}" y="-20" width="{w:.0f}" height="5" fill="{CYA}" opacity=".55" class="hscan"/></g></g>
<mask id="pmask" style="mask-type:alpha"><image {img}/></mask>"""

PHOTO_DEFS = f"""<filter id="tintc"><feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 .94  0 0 0 0 1  0 0 0 .8 0"/></filter>
<filter id="tintm"><feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 0  0 0 0 0 .24  0 0 0 .8 0"/></filter>
<filter id="rimc" x="-10%" y="-10%" width="120%" height="120%"><feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 0  0 0 0 0 .45  0 0 0 1 0" result="m"/><feGaussianBlur stdDeviation="7"/></filter>"""

# ---------- HERO ----------
def hero():
    W, H = 1000, 380
    hp = img_data(CFG.get("hero_photo"), 400)
    NX = 330 if hp else 470
    size = ORB.fit(CFG["name"], 92, 560 if hp else 700, 4)
    title, tpath = glitch_title(ORB, CFG["name"], size, NX, 200)
    k = CFG.get("katakana", "")
    vsign = "".join(f'<text x="912" y="{110 + i*44}" text-anchor="middle">{esc(ch)}</text>' for i, ch in enumerate(k[:4]))
    sub = CFG["title"]
    subsize = RAJ.fit(sub, 24, 470 if hp else 430, 2)
    subd = RAJ.path(sub, subsize, NX, 254, "middle", 2)
    bar_w = RAJ.width(sub, subsize, 2) + 50
    body = f"""<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="url(#sky)"/><rect width="{W}" height="{H}" fill="url(#haze)"/>
<g opacity=".9">{skyline(300, 120, 230, "#1c0a33")}</g><g>{skyline(330, 60, 170, "#0c0418", True)}</g>
<g opacity=".5"><g class="ring"><circle cx="120" cy="120" r="70" fill="none" stroke="{CYA}" stroke-width="1.5" stroke-dasharray="40 8 4 8"/>
<circle cx="120" cy="120" r="56" fill="none" stroke="{MAG}" stroke-width="1" stroke-dasharray="2 6"/></g></g>
{'' if not k else f'<rect x="886" y="72" width="52" height="{40 + 44*len(k[:4])}" fill="#120010" stroke="{MAG}" stroke-width="2" filter="url(#glow)"/><g font-family="{JP}" font-size="38" font-weight="bold" fill="#ffd1dc" stroke="{MAG}" stroke-width="1" filter="url(#glow)" class="flk">{vsign}</g>'}
<g class="pls"><rect x="{40 if not hp else 40}" y="{228 if not hp else 92}" width="92" height="38" fill="#001418" stroke="{CYA}" stroke-width="2" filter="url(#glow)"/>
<text x="86" y="{257 if not hp else 121}" text-anchor="middle" font-family="{JP}" font-size="26" font-weight="bold" fill="#c8fbff">電脳</text></g>
<rect x="{NX - 30}" y="0" width="60" height="{H}" fill="url(#beam)" class="pls"/>
{hero_photo_svg(hp)}
<g stroke="#9ad7ff" stroke-opacity=".35" stroke-width="1"><g class="rain">{rain()}</g></g>
{title}
<g clip-path="url(#band1)"><path d="{tpath}" fill="{YEL}" class="sl"/></g>
<g clip-path="url(#band2)"><path d="{tpath}" fill="{CYA}" class="sl" style="animation-delay:-.4s"/></g>
<g transform="translate(0 245) skewX(-14) translate(0 -245)"><rect x="{NX - bar_w/2}" y="226" width="{bar_w}" height="38" fill="{YEL}"/>
<rect x="{NX + bar_w/2 + 4}" y="226" width="12" height="38" fill="{YEL}"/><rect x="{NX + bar_w/2 + 20}" y="226" width="6" height="38" fill="{YEL}"/></g>
<path d="{subd}" fill="#0a0a0a"/>
<text x="{NX}" y="296" text-anchor="middle" font-family="{JP}" font-size="15" fill="{CYA}" letter-spacing="6" filter="url(#glow)">ようこそ · WELCOME TO THE GRID</text>
<rect width="{W}" height="{H}" fill="url(#scan)"/><rect class="sweep" width="{W}" height="40" fill="{CYA}" opacity=".06"/>
{corners(14, 14, W-28, H-28, CYA)}
<g font-family="{MONO}" font-weight="bold" font-size="13" filter="url(#glow)">
<text x="34" y="42" fill="{CYA}">SYS://{esc(CFG['username'].upper())}  v4.0.4</text>
<text x="34" y="60" fill="{MAG}">NEURAL LINK ........ [OK]</text>
<text x="966" y="42" text-anchor="end" fill="{RED}" class="blk">&#9679; LIVE</text>
<text x="34" y="78" fill="{YEL}">NET::ONLINE  PING 7ms</text>
<text x="34" y="352" fill="{CYA}" opacity=".85">&gt; jack_in --user {esc(CFG['username'].lower())}<tspan class="blk">_</tspan></text>
<text x="966" y="352" text-anchor="end" fill="{MAG}" opacity=".85">{esc(CFG.get('hud_right','SECTOR 07 // GRID 04'))}</text></g></g>"""
    defs = f"""<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#030008"/><stop offset=".55" stop-color="#1a0030"/><stop offset="1" stop-color="#4a0040"/></linearGradient>
<radialGradient id="haze" cx=".5" cy=".75" r=".6"><stop offset="0" stop-color="{MAG}" stop-opacity=".45"/><stop offset="1" stop-color="{MAG}" stop-opacity="0"/></radialGradient>
<linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{CYA}" stop-opacity="0"/><stop offset=".5" stop-color="{CYA}" stop-opacity=".25"/><stop offset="1" stop-color="{CYA}" stop-opacity="0"/></linearGradient>
<clipPath id="band1"><rect y="{200 - size*.62:.0f}" width="1000" height="16"/></clipPath>
<clipPath id="band2"><rect y="{200 - size*.25:.0f}" width="1000" height="11"/></clipPath>
{PHOTO_DEFS}<clipPath id="frame"><rect width="{W}" height="{H}"/></clipPath>"""
    css = """.w{animation:win 4s steps(1) infinite}
@keyframes holo{0%,93%,100%{opacity:1}94%{opacity:.55}95%{opacity:1}97%{opacity:.7}}.holo{animation:holo 5s steps(1) infinite}
@keyframes pgc{0%,88%,100%{transform:translate(0,0);opacity:0}89%{transform:translate(-10px,0);opacity:.7}91%{transform:translate(7px,-2px);opacity:.7}93%{opacity:0}}
@keyframes pgm{0%,88%,100%{transform:translate(0,0);opacity:0}89%{transform:translate(10px,0);opacity:.7}91%{transform:translate(-6px,2px);opacity:.7}93%{opacity:0}}
.pgc{animation:pgc 3.4s steps(1) infinite}.pgm{animation:pgm 3.4s steps(1) infinite}
@keyframes hscan{from{transform:translateY(0)}to{transform:translateY(380px)}}.hscan{animation:hscan 3s linear infinite}
@keyframes rain{from{transform:translate(0,0)}to{transform:translate(-30px,120px)}}.rain{animation:rain .45s linear infinite}
.ring{transform-origin:120px 120px;animation:spin 14s linear infinite}"""
    return svg(W, H, body, css, defs, f"{CFG['name']} - {CFG['title']}")

# ---------- CYBERWARE ----------
def photo_data():
    p = CFG.get("photo")
    if not p:
        return None
    from PIL import Image
    im = Image.open(os.path.join(ROOT, p)).convert("RGB")
    s = min(im.size)
    im = im.crop(((im.width - s) // 2, (im.height - s) // 2, (im.width + s) // 2, (im.height + s) // 2)).resize((320, 320))
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=82)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

def cyberware():
    W = 1000
    skills = CFG["skills"][:6]
    H = 130 + 34 * len(skills) + 10
    H = max(H, 290)
    cx, cy, r = 120, H / 2 + 6, 82
    hexpts = " ".join(f"{cx + r*math.cos(a*math.pi/3 + math.pi/6):.1f},{cy + r*math.sin(a*math.pi/3 + math.pi/6):.1f}" for a in range(6))
    pd = img_data(CFG.get('photo'), 260)
    if pd:
        pd = pd[0]
        av = (f'<g clip-path="url(#hexclip)"><image href="{pd}" x="{cx-r}" y="{cy-r}" width="{2*r}" height="{2*r}" preserveAspectRatio="xMidYMin slice"/>'
              f'<image href="{pd}" x="{cx-r}" y="{cy-r}" width="{2*r}" height="{2*r}" class="pg1" opacity=".55" preserveAspectRatio="xMidYMin slice" style="mix-blend-mode:screen"/>'
              f'<rect x="{cx-r}" y="{cy-r}" width="{2*r}" height="{2*r}" fill="{MAG}" opacity=".18" style="mix-blend-mode:color"/>'
              f'<rect x="{cx-r}" y="{cy-r}" width="{2*r}" height="{2*r}" fill="url(#scan)"/>'
              f'<rect x="{cx-r}" y="{cy-r}" width="{2*r}" height="6" fill="{CYA}" opacity=".6" class="scanbar"/></g>')
    else:
        av = f'<path d="{ORB.path(CFG["initials"], 56, cx, cy + 20, "middle", 2)}" fill="#fff" filter="url(#glow)" class="flk"/>'
    rows = []
    for i, s in enumerate(skills):
        c = SKILL_COLORS[i % len(SKILL_COLORS)]
        y = 104 + i * 34
        v = max(0, min(100, int(s["level"])))
        segs = "".join(f'<path d="M{440+k*25},{y} l8,-18 h16 l-8,18 z" fill="{c}"/>' for k in range(round(v / 100 * 21)))
        rows.append(f'<text x="250" y="{y-3}" fill="#d9d4ff">{esc(s["name"])}</text>'
                    f'<path d="M436,{y+3} l9,-24 h527 l-9,24 z" fill="none" stroke="{c}" stroke-opacity=".35"/>'
                    f'<g class="bar" style="animation-delay:{.3+i*.2:.1f}s" filter="url(#glow)">{segs}</g>'
                    f'<text x="975" y="{y-3}" text-anchor="end" fill="{c}">{v}%</text>')
    head = RAJ.path("CYBERWARE // INSTALLED", 22, 262, 47, ls=2)
    body = f"""{frame(4, 4, W-8, H-8, CYA, 26, "#07000f")}
<rect x="250" y="24" width="{RAJ.width('CYBERWARE // INSTALLED', 22, 2) + 24:.0f}" height="30" fill="{YEL}"/><path d="{head}" fill="#0a0a0a"/>
<g font-family="{MONO}" font-weight="bold" font-size="15">
<text x="975" y="45" text-anchor="end" fill="{MAG}" class="blk">&#9650; HUMANITY 100%</text>
<polygon points="{hexpts}" fill="#14001f" stroke="{MAG}" stroke-width="2.5" filter="url(#glow)"/>
{av}
<polygon points="{hexpts}" fill="none" stroke="{MAG}" stroke-width="2.5"/>
<g class="ring"><circle cx="{cx}" cy="{cy}" r="{r+16}" fill="none" stroke="{CYA}" stroke-width="1.5" stroke-dasharray="30 10 6 10"/></g>
<text x="{cx}" y="{H-14}" text-anchor="middle" fill="{CYA}" font-size="13" letter-spacing="2">CLASS: {esc(CFG['class'])}</text>
{''.join(rows)}</g>"""
    defs = f'<clipPath id="hexclip"><polygon points="{hexpts}"/></clipPath>'
    css = f""".bar{{transform-box:fill-box;transform-origin:0 50%;transform:scaleX(0);animation:fill 1.3s cubic-bezier(.2,.8,.2,1) forwards}}
.ring{{transform-origin:{cx}px {cy}px;animation:spin 10s linear infinite}}
@keyframes pg{{0%,88%,100%{{transform:translate(0,0);opacity:0}}90%{{transform:translate(-8px,0);opacity:.6}}93%{{transform:translate(6px,2px);opacity:.6}}95%{{opacity:0}}}}
.pg1{{animation:pg 2.6s steps(1) infinite}}
@keyframes sb{{from{{transform:translateY(0)}}to{{transform:translateY({2*r}px)}}}}.scanbar{{animation:sb 2.2s linear infinite}}"""
    return svg(W, H, body, css, defs, "Skills")

# ---------- GIGS ----------
def gigs_header():
    t, _ = glitch_title(ORB, "// GIGS", 42, 500, 58, 6)
    body = f"""<line x1="10" y1="42" x2="990" y2="42" stroke="{MAG}" stroke-opacity=".5" stroke-width="2"/>
<rect x="320" y="8" width="360" height="66" fill="#05010a" rx="4"/>{t}
<text x="990" y="30" text-anchor="end" font-family="{JP}" font-size="14" fill="{MAG}">依頼</text>"""
    return svg(1000, 80, body, label="Projects")

def gig(i, p):
    c = [CYA, MAG, YEL][i % 3]
    W, H = 320, 200
    tsize = RAJ.fit(p["title"], 30, 270, 1)
    desc = p["desc"] if len(p["desc"]) <= 36 else p["desc"][:35] + "…"
    tagd = RAJ.path(p["tag"].upper(), 17, 30, 35, ls=1.5)
    tw = RAJ.width(p["tag"].upper(), 17, 1.5) + 20
    body = f"""<g class="in">{frame(4, 4, W-8, H-8, c, 20, "#08000f")}
<rect x="20" y="16" width="{tw:.0f}" height="26" fill="{c}"/><path d="{tagd}" fill="#0a0a0a"/>
<text x="296" y="34" text-anchor="end" font-family="{MONO}" font-size="12" fill="{c}">#{i+1:02d}</text>
<path d="{RAJ.path(p['title'], tsize, 20, 82, ls=1)}" fill="#fff"/>
<text x="20" y="108" font-family="{MONO}" font-size="13" fill="#b9b3d6">{esc(desc)}</text>
<rect x="20" y="124" width="276" height="50" fill="none" stroke="{c}" stroke-opacity=".5" stroke-dasharray="4 4"/>
<text x="158" y="154" text-anchor="middle" font-family="{MONO}" font-size="13" font-weight="bold" fill="{c}" class="pls">[ {esc(p.get('cta','ACCESS REPO'))} &#9656; ]</text></g>"""
    css = f".in{{opacity:0;animation:boot .5s steps(4) {.2+i*.3:.1f}s forwards}}@keyframes boot{{0%{{opacity:0}}25%{{opacity:1}}50%{{opacity:.2}}100%{{opacity:1}}}}"
    return svg(W, H, body, css, label=p["title"])

# ---------- DATA SHARD ----------
def shard():
    papers = CFG["papers"]
    n = len(papers)
    H = 96 + 44 * n + 16
    rows = []
    for i, pt in enumerate(papers):
        y = 112 + i * 44
        t = f"{pt.get('venue','IEEE')} // {pt['title']}"
        size = RAJ.fit(t, 22, 790, .4)
        d = 1.0 + i * .7
        rows.append(f"""<text x="150" y="{y}" font-size="18" fill="{CYA}" class="hide" style="animation-delay:{d:.1f}s">{' '.join(f'{random.randint(0,255):02X}' for _ in range(6))} ## ## ## ## ##</text>
<path class="rev" style="animation-delay:{d:.1f}s" d="{RAJ.path(t, size, 150, y, ls=.4)}" fill="#fff"/>
<text x="130" y="{y}" text-anchor="end" font-size="14" fill="{YEL}" class="rev" style="animation-delay:{d:.1f}s">{i+1:02d}</text>""")
    total = 1.0 + (n - 1) * .7
    body = f"""{frame(4, 4, 992, H-8, YEL, 22, "#0d0b00")}
<g transform="translate(70,{H/2:.0f})" filter="url(#glow)" class="pls"><polygon points="0,-42 30,0 0,42 -30,0" fill="none" stroke="{YEL}" stroke-width="3"/><polygon points="0,-24 17,0 0,24 -17,0" fill="{YEL}"/></g>
<g font-family="{MONO}" font-weight="bold">
<text x="150" y="44" font-size="17" fill="{YEL}" letter-spacing="3" filter="url(#glow)">DATA SHARDS // DECRYPTING</text>
<rect x="150" y="58" width="440" height="12" fill="none" stroke="{YEL}" stroke-opacity=".6"/>
<rect x="152" y="60" width="436" height="8" fill="{YEL}" class="prog" style="animation-duration:{total:.1f}s"/>
<text x="975" y="44" text-anchor="end" font-size="13" fill="{MAG}" class="rev" style="animation-delay:{total:.1f}s">ACCESS GRANTED</text>
<text x="975" y="70" text-anchor="end" font-size="12" fill="{YEL}" opacity=".8">{esc(CFG.get('shard_stats',''))}</text>
{''.join(rows)}</g>"""
    css = """.prog{transform-box:fill-box;transform-origin:0 50%;transform:scaleX(0);animation:fill 2.2s steps(22) forwards}
.rev{opacity:0;animation:rev .1s forwards}.hide{animation:hide .1s forwards}
@keyframes rev{to{opacity:1}}@keyframes hide{to{opacity:0}}"""
    return svg(1000, H, body, css, label="Publications")

# ---------- FOOTER ----------
def footer():
    t = RAJ.path("CONNECTION TERMINATED // SEE YOU IN THE GRID", 20, 500, 47, "middle", 3)
    body = f"""<rect x="0" y="0" width="1000" height="70" fill="#05010a"/><rect width="1000" height="70" fill="url(#scan)"/>
<rect x="0" y="0" width="1000" height="2" fill="{MAG}" filter="url(#glow)"/><rect x="0" y="68" width="1000" height="2" fill="{CYA}" filter="url(#glow)"/>
<path d="{t}" fill="{MAG}" class="gm" opacity=".7"/><path d="{t}" fill="{CYA}" class="gc" opacity=".7"/><path d="{t}" fill="#fff" class="flk"/>
<text x="30" y="44" font-family="{MONO}" font-size="12" fill="{RED}" class="blk">&#9679;</text>"""
    return svg(1000, 70, body, label="Footer")

files = {"hero.svg": hero(), "cyberware.svg": cyberware(), "gigs.svg": gigs_header(), "shard.svg": shard(), "footer.svg": footer()}
for i, p in enumerate(CFG["projects"][:3]):
    files[f"gig-{i+1}.svg"] = gig(i, p)
for k, v in files.items():
    open(os.path.join(ASSETS, k), "w", encoding="utf-8").write(v)

# ---------- README ----------
L = CFG["links"]
def badge(label, color, logo, url):
    return (f'<a href="{esc(url)}"><img src="https://img.shields.io/badge/{label}-0a0014?style=for-the-badge&logo={logo}&logoColor={color[1:]}&labelColor=0a0014&color=0a0014" alt="{label}"/></a>')
badges = []
if L.get("portfolio"): badges.append(badge("PORTFOLIO", CYA, "vercel", L["portfolio"]))
if L.get("linkedin"): badges.append(badge("LINKEDIN", MAG, "linkedin", L["linkedin"]))
if L.get("ieee"): badges.append(badge("IEEE%20XPLORE", YEL, "ieee", L["ieee"]))
if L.get("email"): badges.append(badge("EMAIL", GRN, "gmail", "mailto:" + L["email"]))
u = CFG["username"]
gig_links = "\n".join(
    (f'  <a href="{esc(p["url"])}"><img src="assets/gig-{i+1}.svg" width="32%" alt="{esc(p["title"])}"/></a>' if p.get("url") else f'  <img src="assets/gig-{i+1}.svg" width="32%" alt="{esc(p["title"])}"/>')
    for i, p in enumerate(CFG["projects"][:3]))
papers_md = "\n".join((f"- <samp>[{i+1:02d}]</samp> [{p['title']}]({p['url']}) · *{p.get('venue','IEEE')}*" if p.get("url") else f"- <samp>[{i+1:02d}]</samp> {p['title']} · *{p.get('venue','IEEE')}*") for i, p in enumerate(CFG["papers"]))
_sl = L.get("ieee") or CFG["papers"][0].get("url")
shard_img = f'<a href="{esc(_sl)}"><img src="assets/shard.svg" width="100%" alt="Publications"/></a>' if _sl else '<img src="assets/shard.svg" width="100%" alt="Publications"/>'
if CFG.get("extra_md"): papers_md += "\n\n" + CFG["extra_md"]
tag = "<br/>\n  ".join(f"<samp>&gt; {esc(t)}</samp>" for t in CFG["tagline"])

readme = f"""<!-- CHROME//DISTRICT · generated by generate.py · edit config.json and re-run -->
<p align="center">
  <img src="assets/hero.svg" width="100%" alt="{esc(CFG['name'])} - {esc(CFG['title'])}"/>
</p>

<p align="center">
  {tag}
</p>

{('<p align="center">' + chr(10) + '  ' + ' '.join(badges) + chr(10) + '</p>' + chr(10)) if badges else ''}
<p align="center">
  <img src="assets/cyberware.svg" width="100%" alt="Skills"/>
</p>

<p align="center">
  <img src="assets/gigs.svg" width="100%" alt="Projects"/>
</p>
<p align="center">
{gig_links}
</p>

<p align="center">
  {shard_img}
</p>

{papers_md}

<p align="center">
  <img src="https://raw.githubusercontent.com/{u}/{u}/output/snake-cyber.svg" width="100%" alt="Contribution snake"/>
</p>

<p align="center">
  <img src="assets/footer.svg" width="100%" alt="See you in the grid"/>
</p>
"""
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(readme)

# ---------- PREVIEW (local only, mimics GitHub dark) ----------
def uri(n): return "data:image/svg+xml;base64," + base64.b64encode(files[n].encode()).decode()
prev = readme.replace(papers_md, re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" style="color:#58a6ff">\1</a>', re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", re.sub(r"\*([^*]+)\*", r"<i>\1</i>", papers_md))).replace("- <samp>", "<br><samp>").replace("\n\n", "<br><br>"))
for n in files:
    prev = prev.replace(f'src="assets/{n}"', f'src="{uri(n)}"')
prev = prev.replace(f'https://raw.githubusercontent.com/{u}/{u}/output/snake-cyber.svg', "data:image/svg+xml;base64," + base64.b64encode(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 120"><rect width="1000" height="120" fill="#0d1117"/><text x="500" y="66" text-anchor="middle" font-family="monospace" font-size="16" fill="#6e7681">[ neon contribution snake appears here after the first GitHub Action run ]</text></svg>'.encode()).decode())
prev = prev.replace("<p align=\"center\">", '<p style="text-align:center;margin:0 0 14px">')
open(os.path.join(ROOT, "preview.html"), "w", encoding="utf-8").write(
    f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>CHROME//DISTRICT preview</title></head>
<body style="margin:0;background:#0d1117;color:#e6edf3;font-family:-apple-system,Segoe UI,sans-serif">
<div style="max-width:880px;margin:0 auto;padding:24px 16px"><div style="font:12px monospace;color:#7d8590;margin-bottom:8px">{u} / README.md</div>
<div style="border:1px solid #30363d;border-radius:8px;padding:24px;line-height:1.6">{prev}</div></div></body></html>""")
print("generated:", ", ".join(sorted(files)), "+ README.md + preview.html")
