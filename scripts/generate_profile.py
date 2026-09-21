#!/usr/bin/env python3
"""
Generates every SVG used by the profile README (assets/*.svg).

* Static art (hero, illustrations, cards, footer) is drawn here in code.
* Live numbers (followers, stars, commits, streak, languages, contribution
  heat-map) are pulled from GitHub each time the script runs.

Run locally:   python scripts/generate_profile.py
Run in CI:     see .github/workflows/update-profile.yml  (daily)
"""
import json
import math
import os
import random
import re
import sys
import urllib.request
from html import escape
from pathlib import Path

USER = os.environ.get("GH_USER", "ShahmeerNaseer")
DISPLAY_NAME = "Shahmeer"
TOKEN = os.environ.get("GITHUB_TOKEN", "")

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
ICONS = json.loads((Path(__file__).parent / "icons.json").read_text())

# ───────────────────────────── content you can edit ─────────────────────────────
ROLE = "Full-Stack Developer"
TAGLINE = "Full-Stack Developer | Creative Problem Solver | Always Learning..."
WORKING_ON = "Hospital Management System"
LEARNING = "React"
INTERESTS = "Interactive web apps & study tools"
FUN_FACT = "Built a game scored entirely with the Web Audio API"
QUOTE = "Building ideas into experiences, one line of code at a time."

PROJECTS = [
    dict(name="Forget \u2192 Remember", desc="Spaced-repetition study app with XP, streaks and SM-2 reviews.",
         tags=["JavaScript", "Firebase", "Firestore"], url=f"https://github.com/{USER}/Forget-N-Remember"),
    dict(name="The Hollow Quill", desc="Branching narrative game with a live-synthesized soundtrack.",
         tags=["JavaScript", "GSAP", "Web Audio"], url=f"https://github.com/{USER}?tab=repositories"),
    dict(name="Hospital Management System", desc="Role-based hospital app with four dashboards + Supabase sync.",
         tags=["React", "Vite", "Supabase"], url=f"https://github.com/{USER}/HospitalManagementSystem"),
    dict(name="SocialSphere", desc="Social media MVP: auth, live feed and image uploads.",
         tags=["HTML/CSS/JS", "Firebase", "Storage"], url=f"https://github.com/{USER}?tab=repositories"),
]

# Replace the placeholder handles below with your real links.
SOCIALS = [
    ("linkedin", "LinkedIn", "https://www.linkedin.com/in/YOUR_LINKEDIN"),
    ("x", "X", "https://x.com/YOUR_X"),
    ("instagram", "Instagram", "https://instagram.com/YOUR_INSTAGRAM"),
    ("tiktok", "TikTok", "https://www.tiktok.com/@YOUR_TIKTOK"),
    ("youtube", "YouTube", "https://youtube.com/@YOUR_YOUTUBE"),
    ("gmail", "Email", "mailto:YOUR_EMAIL"),
]

# ───────────────────────────── styling constants ─────────────────────────────
W = 1024
BG = "#06051b"
SANS = "'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif"
MONO = "'Fira Code','Cascadia Code',Consolas,'Courier New',monospace"
SCRIPT = "'Brush Script MT','Segoe Script','Snell Roundhand','Apple Chancery','Comic Sans MS',cursive"

ICON_COLOR = {  # brightened brand colours so they read on the dark background
    "next": "#ffffff", "express": "#e5e7eb", "github": "#ffffff", "python": "#4f9fe0",
    "ts": "#3b8de6", "css": "#2d8fe0", "mysql": "#5ba4d0", "bootstrap": "#9a6be0",
    "vscode": "#2fa3f2", "node": "#68b358", "php": "#8e93d0",
}


# ───────────────────────────── small helpers ─────────────────────────────
def esc(s):
    return escape(str(s), quote=True)


def txt(x, y, s, size=14, fill="#d1d5db", weight=400, anchor="start", family=SANS, extra="", fit=None):
    """Text element. `fit` (px) pins the rendered width so it never overflows on other fonts."""
    tl = f' textLength="{fit}" lengthAdjust="spacingAndGlyphs"' if fit else ""
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}"{tl} {extra}>{esc(s)}</text>')


def est(s, size, ratio=0.5):
    return round(len(s) * size * ratio)


def icon(key, x, y, size, fill=None):
    i = ICONS[key]
    color = fill or ICON_COLOR.get(key) or "#" + i["hex"]
    return f'<path transform="translate({x:.2f} {y:.2f}) scale({size / 24:.4f})" d="{i["path"]}" fill="{color}"/>'


def svg_doc(w, h, body, bg=True, extra_defs=""):
    bgrect = f'<rect width="{w}" height="{h}" fill="{BG}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img">{DEFS}{extra_defs}{bgrect}{body}</svg>\n')


DEFS = f"""<defs>
<linearGradient id="gTitle" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#22e4ff"/><stop offset=".5" stop-color="#8f7bff"/><stop offset="1" stop-color="#f43fe0"/></linearGradient>
<linearGradient id="gBorder" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7c3aed"/><stop offset=".55" stop-color="#5b3fd0"/><stop offset="1" stop-color="#c026d3"/></linearGradient>
<linearGradient id="gCyan" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#22d3ee"/><stop offset="1" stop-color="#6366f1"/></linearGradient>
<linearGradient id="gPinkBorder" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#e879f9"/><stop offset="1" stop-color="#7c3aed"/></linearGradient>
<linearGradient id="gCyanBorder" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#22d3ee"/><stop offset="1" stop-color="#6d5ff5"/></linearGradient>
<linearGradient id="gPill" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#22d3ee"/><stop offset=".5" stop-color="#8b5cf6"/><stop offset="1" stop-color="#22d3ee"/></linearGradient>
<linearGradient id="gLineR" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#a855f7"/><stop offset="1" stop-color="#a855f7" stop-opacity="0"/></linearGradient>
<linearGradient id="gLineL" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#a855f7" stop-opacity="0"/><stop offset="1" stop-color="#a855f7"/></linearGradient>
<linearGradient id="gFlame" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#f43f5e"/><stop offset=".55" stop-color="#fb7185"/><stop offset="1" stop-color="#fdba74"/></linearGradient>
<linearGradient id="gSky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#050419"/><stop offset=".38" stop-color="#1a0e4c"/><stop offset=".68" stop-color="#5a2088"/><stop offset="1" stop-color="#c24aa6"/></linearGradient>
<linearGradient id="gMount1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6244d6"/><stop offset="1" stop-color="#2a1a78"/></linearGradient>
<linearGradient id="gMount2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3b2896"/><stop offset="1" stop-color="#180f48"/></linearGradient>
<linearGradient id="gFade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="{BG}"/></linearGradient>
<linearGradient id="gSwoosh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#22e4ff" stop-opacity="0"/><stop offset=".3" stop-color="#22e4ff"/><stop offset=".75" stop-color="#c04cff"/><stop offset="1" stop-color="#f43fe0" stop-opacity="0"/></linearGradient>
<linearGradient id="gRoom" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1a1045"/><stop offset=".6" stop-color="#2d1570"/><stop offset="1" stop-color="#4a1a8a"/></linearGradient>
<linearGradient id="gCity" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3b1f8f"/><stop offset=".7" stop-color="#8a3fc4"/><stop offset="1" stop-color="#f06ec0"/></linearGradient>
<linearGradient id="gHill1" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#3b1d9a"/><stop offset=".5" stop-color="#8b2fd0"/><stop offset="1" stop-color="#d63fc4"/></linearGradient>
<linearGradient id="gHill2" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#241068"/><stop offset=".6" stop-color="#5a24b0"/><stop offset="1" stop-color="#7c3aed"/></linearGradient>
<linearGradient id="gThanks" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#f0abfc"/><stop offset=".5" stop-color="#e879f9"/><stop offset="1" stop-color="#a78bfa"/></linearGradient>
<linearGradient id="gMeteor" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7dd3fc" stop-opacity="0"/><stop offset="1" stop-color="#e0f2fe"/></linearGradient>
<radialGradient id="rSun" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffb3e6"/><stop offset=".55" stop-color="#ff6ec7"/><stop offset="1" stop-color="#c026d3"/></radialGradient>
<radialGradient id="rGlow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ff6ec7" stop-opacity=".55"/><stop offset="1" stop-color="#ff6ec7" stop-opacity="0"/></radialGradient>
<radialGradient id="rGlowC" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#22d3ee" stop-opacity=".35"/><stop offset="1" stop-color="#22d3ee" stop-opacity="0"/></radialGradient>
<radialGradient id="rVisor" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#7c6cff"/><stop offset="1" stop-color="#1b1050"/></radialGradient>
<filter id="glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="glowS" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="1.8" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="blur10"><feGaussianBlur stdDeviation="10"/></filter>
<filter id="blur4"><feGaussianBlur stdDeviation="4"/></filter>
</defs>"""


# ───────────────────────────── data collection ─────────────────────────────
def http(url, api=False):
    headers = {"User-Agent": "profile-readme-generator"}
    if api:
        headers["Accept"] = "application/vnd.github+json"
        if TOKEN:
            headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def try_json(url):
    try:
        return json.loads(http(url, api=True))
    except Exception as e:  # rate limits, network, etc.
        print(f"  ! {url.split('?')[0]} -> {e}", file=sys.stderr)
        return None


def collect():
    d = dict(followers=0, repos=0, stars=0, commits=0, prs=0, issues=0, langs={}, days=[], year_total=0)

    # --- profile counters (HTML, no rate limit) ---
    try:
        h = http(f"https://github.com/{USER}")
        m = re.search(r'tab=followers"[^>]*>.*?text-bold color-fg-default">\s*([\d.,]+k?)\s*<', h, re.S)
        if m:
            v = m.group(1).replace(",", "")
            d["followers"] = int(float(v[:-1]) * 1000) if v.endswith("k") else int(float(v))
        m = re.search(r'tab=repositories"[^>]*>.*?Counter">\s*([\d,]+)', h, re.S)
        if m:
            d["repos"] = int(m.group(1).replace(",", ""))
    except Exception as e:
        print("  ! profile scrape failed:", e, file=sys.stderr)

    # --- REST API (rich data; needs a token in CI, may be rate limited locally) ---
    got_api = False
    user = try_json(f"https://api.github.com/users/{USER}")
    if user and "followers" in user:
        d["followers"], d["repos"] = user["followers"], user["public_repos"]
        repos = try_json(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner") or []
        if isinstance(repos, list) and repos:
            got_api = True
            d["stars"] = sum(r.get("stargazers_count", 0) for r in repos)
            for r in repos:
                if r.get("fork"):
                    continue
                lg = try_json(f"https://api.github.com/repos/{USER}/{r['name']}/languages") or {}
                for k, v in lg.items():
                    d["langs"][k] = d["langs"].get(k, 0) + v
        c = try_json(f"https://api.github.com/search/commits?q=author:{USER}&per_page=1")
        p = try_json(f"https://api.github.com/search/issues?q=author:{USER}+type:pr&per_page=1")
        i = try_json(f"https://api.github.com/search/issues?q=author:{USER}+type:issue&per_page=1")
        d["commits"] = (c or {}).get("total_count", 0)
        d["prs"] = (p or {}).get("total_count", 0)
        d["issues"] = (i or {}).get("total_count", 0)

    # --- HTML fallback for stars + languages ---
    if not got_api:
        try:
            page, names = 1, 0
            while page <= 5:
                h = http(f"https://github.com/{USER}?tab=repositories&type=source&page={page}")
                blocks = h.split('itemprop="name codeRepository"')[1:]
                if not blocks:
                    break
                for b in blocks:
                    names += 1
                    lm = re.search(r'itemprop="programmingLanguage">([^<]+)', b[:3000])
                    if lm:
                        d["langs"][lm.group(1)] = d["langs"].get(lm.group(1), 0) + 100
                    sm = re.search(r'/stargazers"[^>]*>.*?([\d,]+)\s*</a>', b[:3000], re.S)
                    if sm:
                        d["stars"] += int(sm.group(1).replace(",", ""))
                if 'rel="next"' not in h:
                    break
                page += 1
        except Exception as e:
            print("  ! repo scrape failed:", e, file=sys.stderr)

    # --- contribution calendar (HTML) ---
    try:
        h = http(f"https://github.com/users/{USER}/contributions")
        tips = dict(re.findall(r'for="(contribution-day-component-\d+-\d+)"[^>]*>([^<]*)<', h))
        cells = []
        for td in re.findall(r"<td[^>]*data-date[^>]*>", h):
            date = re.search(r'data-date="([^"]+)"', td).group(1)
            cid = re.search(r'id="contribution-day-component-(\d+)-(\d+)"', td)
            lvl = int(re.search(r'data-level="(\d)"', td).group(1))
            row, col = int(cid.group(1)), int(cid.group(2))
            m = re.match(r"(\d+) contribution", tips.get(f"contribution-day-component-{row}-{col}", ""))
            cells.append(dict(date=date, row=row, col=col, level=lvl, count=int(m.group(1)) if m else 0))
        cells.sort(key=lambda c: c["date"])
        d["days"] = cells
        d["year_total"] = sum(c["count"] for c in cells)
    except Exception as e:
        print("  ! contribution scrape failed:", e, file=sys.stderr)

    if not d["commits"]:
        d["commits"] = d["year_total"]  # fallback when the search API is unavailable
    return d


def streaks(days):
    counts = [c["count"] for c in days]
    if not counts:
        return 0, 0
    longest = run = 0
    for v in counts:
        run = run + 1 if v > 0 else 0
        longest = max(longest, run)
    i = len(counts) - 1
    if counts[i] == 0:
        i -= 1  # today may not have contributions yet
    cur = 0
    while i >= 0 and counts[i] > 0:
        cur += 1
        i -= 1
    return cur, longest


def fmt(n):
    return f"{n/1000:.1f}k".replace(".0k", "k") if n >= 10000 else f"{n:,}"


# ───────────────────────────── shared UI pieces ─────────────────────────────
def section_title(cx_or_x, y, title, glyph, centered=False, width=W):
    """Section header with glyph, title and a fading line (like the reference image)."""
    size = 24
    tw = est(title, size, 0.52)
    if centered:
        total = 34 + tw
        x0 = cx_or_x - total / 2
        out = (f'<rect x="30" y="{y-1}" width="{x0-30-14:.0f}" height="2" fill="url(#gLineL)" rx="1"/>'
               f'<rect x="{x0+total+14:.0f}" y="{y-1}" width="{W-30-(x0+total+14):.0f}" height="2" fill="url(#gLineR)" rx="1"/>')
        out += f'<g transform="translate({x0:.0f} {y-14})">{glyph}</g>'
        out += txt(x0 + 36, y + 8, title, size, "#ffffff", 600, fit=tw)
        return out
    x0 = cx_or_x
    out = f'<g transform="translate({x0} {y-13})">{glyph}</g>'
    out += txt(x0 + 32, y + 7, title, 20, "#ffffff", 600, fit=est(title, 20, 0.52))
    lx = x0 + 32 + est(title, 20, 0.52) + 14
    out += f'<rect x="{lx}" y="{y-1}" width="{width}" height="2" fill="url(#gLineR)" rx="1"/>'
    return out


def g_person(c="#c4b5fd"):
    return (f'<circle cx="13" cy="9" r="5" fill="none" stroke="{c}" stroke-width="2"/>'
            f'<path d="M3 25c1-6 5-8.5 10-8.5S22 19 23 25" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round"/>')


def g_orbit(c="#67e8f9"):
    return (f'<circle cx="13" cy="13" r="3" fill="{c}"/><ellipse cx="13" cy="13" rx="11" ry="4.5" fill="none" stroke="{c}" stroke-width="1.6"/>'
            f'<ellipse cx="13" cy="13" rx="11" ry="4.5" fill="none" stroke="{c}" stroke-width="1.6" transform="rotate(60 13 13)"/>'
            f'<ellipse cx="13" cy="13" rx="11" ry="4.5" fill="none" stroke="{c}" stroke-width="1.6" transform="rotate(-60 13 13)"/>')


def g_chart(c="#a78bfa"):
    return (f'<path d="M2 22L9 12l5 5 9-13" fill="none" stroke="{c}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="M17 4h6v6" fill="none" stroke="{c}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>')


def g_flame(c="#fb923c", s=1.0):
    return f'<path transform="scale({s})" d="M13 1c1.5 6-5 9-5 15a7 7 0 0 0 14 0c0-3-1.5-5-3-7 0 3-1.5 4.5-3 4.5 1.5-5 0-9-3-12.5z" fill="{c}"/>'


def g_calendar(c="#f472b6"):
    return (f'<rect x="3" y="5" width="20" height="18" rx="3" fill="none" stroke="{c}" stroke-width="2"/>'
            f'<path d="M3 11h20M9 2v6M17 2v6" stroke="{c}" stroke-width="2" stroke-linecap="round"/>'
            f'<rect x="7" y="14" width="4" height="3" fill="{c}"/><rect x="13" y="14" width="4" height="3" fill="{c}"/><rect x="7" y="19" width="4" height="2" fill="{c}"/>')


def g_snake(c="#e879f9"):
    return (f'<path d="M3 20c4-10 8 6 12-4s5-6 8-10" fill="none" stroke="{c}" stroke-width="2.6" stroke-linecap="round"/>'
            f'<circle cx="23" cy="6" r="2.2" fill="{c}"/>')


def g_rocket(c="#f472b6"):
    return (f'<path d="M13 2c5 3 7 9 5 15h-10c-2-6 0-12 5-15z" fill="none" stroke="{c}" stroke-width="2" stroke-linejoin="round"/>'
            f'<circle cx="13" cy="10" r="2.4" fill="{c}"/><path d="M8 17l-4 5 5-1M18 17l4 5-5-1M11 20l2 4 2-4" fill="none" stroke="{c}" stroke-width="2" stroke-linejoin="round"/>')


def g_link(c="#67e8f9"):
    return (f'<path d="M11 15a5 5 0 0 0 7 0l4-4a5 5 0 0 0-7-7l-1.5 1.5M15 11a5 5 0 0 0-7 0l-4 4a5 5 0 0 0 7 7l1.5-1.5" '
            f'fill="none" stroke="{c}" stroke-width="2.2" stroke-linecap="round"/>')


def star_path(cx, cy, r, rot=-90, inner=0.45, n=5):
    pts = []
    for i in range(n * 2):
        rr = r if i % 2 == 0 else r * inner
        a = math.radians(rot + i * 180 / n)
        pts.append(f"{cx + rr * math.cos(a):.2f},{cy + rr * math.sin(a):.2f}")
    return " ".join(pts)


def sparkle(cx, cy, r, fill="#ffffff"):
    return (f'<path d="M{cx} {cy-r}Q{cx} {cy} {cx+r} {cy}Q{cx} {cy} {cx} {cy+r}Q{cx} {cy} {cx-r} {cy}Q{cx} {cy} {cx} {cy-r}Z" fill="{fill}"/>')


# ───────────────────────────── hero + badges ─────────────────────────────
def build_hero(d):
    rnd = random.Random(21)
    o = []
    o.append('<clipPath id="clipHero"><rect width="1024" height="272"/></clipPath><g clip-path="url(#clipHero)">')
    o.append('<rect width="1024" height="272" fill="url(#gSky)"/>')
    # stars
    for i in range(95):
        x, y = rnd.uniform(0, 1024), rnd.uniform(0, 200) ** 1.0
        r = rnd.choice([.6, .8, 1, 1.2, 1.6])
        op = rnd.uniform(.35, .95)
        tw = ""
        if i % 3 == 0:
            tw = (f'<animate attributeName="opacity" values="{op:.2f};.15;{op:.2f}" dur="{rnd.uniform(2.2,5):.1f}s" '
                  f'begin="{rnd.uniform(0,3):.1f}s" repeatCount="indefinite"/>')
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#ffffff" opacity="{op:.2f}">{tw}</circle>')
    for (x, y, r, c) in [(120, 88, 5, "#f0abfc"), (640, 34, 4, "#67e8f9"), (905, 44, 3.5, "#ffffff"), (330, 30, 3, "#c4b5fd"),
                         (960, 120, 4, "#f0abfc"), (56, 150, 3.5, "#67e8f9")]:
        o.append(f'<g opacity=".9">{sparkle(x, y, r, c)}'
                 f'<animate attributeName="opacity" values=".9;.25;.9" dur="3.6s" begin="{rnd.uniform(0,2):.1f}s" repeatCount="indefinite"/></g>')
    # meteors
    for (x1, y1, x2, y2, w) in [(112, 52, 44, 84, 1.8), (700, 20, 640, 46, 1.6), (930, 20, 870, 52, 1.3)]:
        o.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#bfe9ff" stroke-width="{w}" stroke-linecap="round" opacity=".9"/>'
                 f'<line x1="{x1}" y1="{y1}" x2="{x1+(x1-x2)*1.6:.0f}" y2="{y1+(y1-y2)*1.6:.0f}" stroke="#bfe9ff" stroke-width="{w*.6:.1f}" stroke-linecap="round" opacity=".18"/>')
    # sun / moon
    o.append('<circle cx="838" cy="168" r="112" fill="url(#rGlow)"/>')
    o.append('<circle cx="838" cy="168" r="46" fill="url(#rSun)"/>')
    o.append('<circle cx="838" cy="168" r="46" fill="none" stroke="#ffd0f0" stroke-opacity=".5" stroke-width="1.5"/>')
    # mountains
    o.append('<path d="M0 205L44 178L82 200L138 152L196 198L252 172L318 214L392 186L452 222L536 196L610 226L690 208L772 228L880 210L1024 214V272H0Z" fill="url(#gMount1)"/>')
    o.append('<path d="M0 214L38 196L70 212L118 176L170 214L214 200L280 238L360 218L430 246L520 230L610 252L700 236L790 248L900 238L1024 232V272H0Z" fill="url(#gMount2)"/>')
    o.append('<path d="M0 205L44 178L82 200L138 152L196 198L252 172L318 214L392 186L452 222L536 196L610 226L690 208L772 228L880 210L1024 214" fill="none" stroke="#a78bfa" stroke-opacity=".45" stroke-width="1.2"/>')
    o.append('<path d="M0 250C140 236 260 258 420 252C600 244 760 262 1024 246V272H0Z" fill="#0b0828"/>')
    # rock + figure
    o.append('<path d="M756 244L786 216L838 206L900 210L936 226L968 248V272H756Z" fill="#0a0724"/>')
    o.append('<path d="M786 216L838 206L900 210L936 226" fill="none" stroke="#ff8ad8" stroke-opacity=".55" stroke-width="1.6"/>')
    o.append('<g fill="#080520" stroke="#ff8ad8" stroke-opacity=".55" stroke-width="1">'
             '<circle cx="884" cy="145" r="12"/>'
             '<path d="M871 141q3-14 17-13 10 2 10 12-8-6-16-5-6 1-11 6z"/>'
             '<path d="M870 158q-12 8-14 30l-3 22h34l3-12q10-2 24-14l2 8 4-2-1-14q-8 6-22 6-4-14-12-20-8-4-15-4z"/>'
             '<path d="M856 210l18-4 28 4 24-8 6 8-30 12h-46z"/></g>')
    o.append('</g>')
    # fade into page
    o.append('<rect y="222" width="1024" height="50" fill="url(#gFade)"/>')

    # ── texts ──
    o.append(txt(30, 36, "< Dream \u2022 Code \u2022 Build />", 14.5, "#a5b4fc", 500, family=MONO, extra='opacity=".95"', fit=190))
    o.append(txt(512, 70, "Hey there, I'm", 36, "#f5f3ff", 300, "middle", extra='letter-spacing="1"'))
    name_fit = est(DISPLAY_NAME, 88, .62)
    o.append(f'<g filter="url(#glow)">{txt(512, 146, DISPLAY_NAME, 88, "url(#gTitle)", 800, "middle", fit=name_fit)}</g>')
    o.append('<path d="M448 160Q520 176 640 150" fill="none" stroke="url(#gSwoosh)" stroke-width="3.2" stroke-linecap="round"/>'
             '<path d="M512 170Q560 176 600 166" fill="none" stroke="url(#gSwoosh)" stroke-width="1.8" stroke-linecap="round" opacity=".8"/>')
    o.append(f'<g filter="url(#glow)">{txt(756, 92, "</>", 34, "#4ee1ff", 700, "middle", family=MONO)}</g>')
    # subtitle pill
    o.append('<rect x="240" y="184" width="544" height="38" rx="19" fill="#0a0826" fill-opacity=".85" stroke="url(#gPill)" stroke-width="2" filter="url(#glowS)"/>')
    o.append(sparkle(268, 203, 9, "#ffffff"))
    o.append(txt(290, 208, TAGLINE, 12.5, "#e0e7ff", 500, family=MONO, fit=470))
    o.append('<rect x="766" y="194" width="2" height="18" fill="#e0e7ff"><animate attributeName="opacity" values="1;0;1" dur="1.1s" repeatCount="indefinite"/></rect>')

    # ── badge pills ──
    pills = [
        (d["followers"], "Followers", "gPinkBorder", "gh"),
        (d["stars"], "Stars", "gCyanBorder", "star"),
        (d["repos"], "Repositories", "gPinkBorder", "repo"),
    ]
    pw, ph, gap = 214, 58, 30
    x = (W - (3 * pw + 2 * gap)) / 2
    for val, label, grad, kind in pills:
        o.append(f'<rect x="{x:.0f}" y="252" width="{pw}" height="{ph}" rx="29" fill="#0c0930" fill-opacity=".9" stroke="url(#{grad})" stroke-width="2" filter="url(#glowS)"/>')
        cx, cy = x + 38, 281
        if kind == "gh":
            o.append(icon("github", cx - 15, cy - 15, 30, "#ffffff"))
        elif kind == "star":
            o.append(f'<polygon points="{star_path(cx, cy, 15, inner=.48)}" fill="#a5b4fc" stroke="#22d3ee" stroke-width="1.5" stroke-linejoin="round"/>')
        else:
            o.append(f'<path transform="translate({cx-14} {cy-14}) scale(1.16)" d="M3 5a2 2 0 0 1 2-2h13v15H5.5a1.5 1.5 0 0 0 0 3H18v1H5.5A3.5 3.5 0 0 1 2 18V5.5z" fill="none" stroke="#e879f9" stroke-width="1.8"/>')
        o.append(txt(x + 74, 276, fmt(val), 17, "#f5d0fe" if grad == "gPinkBorder" else "#a5f3fc", 700))
        o.append(txt(x + 74, 296, label, 12.5, "#a1a1c5", 400))
        x += pw + gap
    return "".join(o)


# ───────────────────────────── about me ─────────────────────────────
def about_icon(kind, x, y):
    s = {
        "laptop": '<rect x="2.5" y="3" width="13" height="9" rx="1.5" fill="none" stroke="#38bdf8" stroke-width="1.7"/><path d="M0.8 14.6h16.4" stroke="#38bdf8" stroke-width="1.9" stroke-linecap="round"/>',
        "sprout": '<path d="M9 16.5V9" stroke="#4ade80" stroke-width="1.7" stroke-linecap="round"/><path d="M9 9C9 5 6 3 2.5 3.5 2.5 7 5 9 9 9Z" fill="#4ade80"/><path d="M9 11.5C9 7.5 11.5 5.5 15.5 6 15.5 9.5 13 11.5 9 11.5Z" fill="#22c55e"/>',
        "target": '<circle cx="9" cy="9" r="7.3" fill="none" stroke="#f472b6" stroke-width="1.6"/><circle cx="9" cy="9" r="4" fill="none" stroke="#f472b6" stroke-width="1.6"/><circle cx="9" cy="9" r="1.4" fill="#f472b6"/>',
        "palette": '<circle cx="9" cy="9" r="7.6" fill="#e879f9"/><circle cx="5.6" cy="7.6" r="1.5" fill="#06051b"/><circle cx="9.2" cy="4.8" r="1.5" fill="#06051b"/><circle cx="12.6" cy="8" r="1.5" fill="#06051b"/><circle cx="10.6" cy="12.6" r="1.7" fill="#06051b"/>',
        "brain": '<path d="M6.2 3.2a2.9 2.9 0 0 1 5.6 0 3 3 0 0 1 3.2 3.6 3 3 0 0 1-1.3 5.4 3 3 0 0 1-5.7 1.6 3 3 0 0 1-5.7-1.6A3 3 0 0 1 3 6.8 3 3 0 0 1 6.2 3.2Z" fill="#f472b6"/><path d="M9 4v11" stroke="#06051b" stroke-width="1" opacity=".5"/>',
        "hands": '<path d="M1 7.5l4-3 4 1.6 4-1.6 4 3-3.2 5-2.3-1.8-2 2-2.2-1.4-1.9 1.6z" fill="#c084fc"/>',
        "bolt": '<path d="M10.5 1L3 10.2h5l-1 6.8 8-10.2h-5z" fill="#fbbf24"/>',
    }[kind]
    return f'<g transform="translate({x} {y})">{s}</g>'


def build_about(y0, d):
    o = []
    X0, X1 = 30, 994
    h = 390
    o.append(f'<rect x="{X0}" y="{y0}" width="{X1-X0}" height="{h}" rx="14" fill="#100b32" fill-opacity=".72" stroke="url(#gBorder)" stroke-width="1.6"/>')
    o.append(f'<g transform="translate(52 {y0+14})">{g_person()}</g>')
    o.append(txt(90, y0 + 36, "About Me", 26, "#ffffff", 600, fit=110))
    o.append(f'<rect x="216" y="{y0+27}" width="330" height="2" fill="url(#gLineR)" rx="1"/>')
    o.append(f'<text x="52" y="{y0+72}" font-family="{SANS}" font-size="17" fill="#ffffff" font-weight="500">Hi, I\'m <tspan fill="#22d3ee" font-weight="700">{esc(DISPLAY_NAME)}</tspan></text>')
    para = [f"I'm a {ROLE} passionate about creating modern,",
            "responsive, and engaging digital experiences. I love turning",
            "ideas into real, functional, and beautiful websites and applications."]
    for i, line in enumerate(para):
        o.append(txt(52, y0 + 98 + i * 20, line, 14, "#d4d4e8", 400, fit=est(line, 14, .5)))
    rows = [
        ("laptop", "Currently working on", WORKING_ON, 232),
        ("sprout", "Currently learning", LEARNING, 232),
        ("target", "Interested in", INTERESTS, 232),
        ("palette", "I enjoy combining design + development", None, 0),
        ("brain", "Always improving my problem-solving skills", None, 0),
        ("hands", "Open to collaboration on exciting projects", None, 0),
        ("bolt", "Fun fact:", FUN_FACT, 160),
    ]
    ry = y0 + 158
    for kind, label, value, vx in rows:
        o.append(about_icon(kind, 52, ry - 9))
        o.append(txt(84, ry + 5, label, 14, "#d4d4e8", 400, fit=est(label, 14, .5)))
        if value:
            o.append(txt(84 + est(label, 14, .5) + 9, ry + 5, value, 14, "#22d3ee", 500, fit=est(value, 14, .5)))
        ry += 26
    o.append(txt(50, y0 + 378, "\u201c", 46, "#e879f9", 700, family="Georgia,serif"))
    o.append(txt(80, y0 + 368, QUOTE, 14.5, "#e5e7eb", 400, extra='font-style="italic"', fit=est(QUOTE, 14.5, .47)))
    o.append(txt(80 + est(QUOTE, 14.5, .47) + 8, y0 + 380, "\u201d", 40, "#e879f9", 700, family="Georgia,serif"))

    # ── illustration ──
    ix, iy, iw, ih = 564, y0 + 40, 402, 274
    rnd = random.Random(5)
    s = [f'<clipPath id="clipRoom"><rect x="0" y="0" width="{iw}" height="{ih}" rx="12"/></clipPath>',
         f'<g transform="translate({ix} {iy})"><g clip-path="url(#clipRoom)">',
         f'<rect width="{iw}" height="{ih}" fill="url(#gRoom)"/>',
         '<circle cx="330" cy="30" r="90" fill="url(#rGlow)" opacity=".5"/><circle cx="60" cy="150" r="80" fill="url(#rGlowC)"/>']
    # window with skyline
    s.append('<rect x="12" y="12" width="236" height="158" rx="4" fill="url(#gCity)"/>')
    x = 12
    while x < 244:
        bw = rnd.randint(14, 30)
        bh = rnd.randint(40, 120)
        bw = min(bw, 248 - x)
        s.append(f'<rect x="{x}" y="{170-bh}" width="{bw}" height="{bh}" fill="#150a3c"/>')
        for wy in range(170 - bh + 6, 166, 9):
            for wx in range(x + 3, x + bw - 4, 7):
                if rnd.random() < .5:
                    c = rnd.choice(["#fde68a", "#f9a8d4", "#67e8f9", "#fbcfe8"])
                    s.append(f'<rect x="{wx}" y="{wy}" width="3" height="4" fill="{c}" opacity=".9"/>')
        x += bw + 2
    s.append('<rect x="12" y="12" width="236" height="158" rx="4" fill="none" stroke="#7c3aed" stroke-width="2.5"/>'
             '<path d="M130 12v158M12 91h236" stroke="#7c3aed" stroke-width="2" opacity=".9"/>')
    # bokeh
    for _ in range(14):
        s.append(f'<circle cx="{rnd.uniform(10,240):.0f}" cy="{rnd.uniform(20,160):.0f}" r="{rnd.uniform(2,6):.1f}" fill="{rnd.choice(["#f472b6","#22d3ee","#c084fc"])}" opacity=".16"/>')
    # desk
    s.append(f'<rect y="212" width="{iw}" height="{ih-212}" fill="#0f0828"/><rect y="211" width="{iw}" height="2.5" fill="#7c3aed" opacity=".8"/>')
    # laptop glow + laptop
    s.append('<rect x="58" y="96" width="190" height="112" rx="8" fill="#22d3ee" opacity=".18" filter="url(#blur10)"/>')
    s.append('<rect x="62" y="96" width="182" height="112" rx="6" fill="#0b0722" stroke="#8b5cf6" stroke-width="2.4"/>')
    cols = ["#f472b6", "#22d3ee", "#a78bfa", "#fde047", "#4ade80", "#e0e7ff"]
    for i in range(10):
        ind = rnd.choice([0, 0, 10, 20, 30])
        s.append(f'<rect x="{72+ind}" y="{106+i*10}" width="{rnd.randint(30,100)}" height="3.4" rx="1.7" fill="{rnd.choice(cols)}" opacity=".9"/>')
        if rnd.random() < .5:
            s.append(f'<rect x="{72+ind+rnd.randint(40,110)}" y="{106+i*10}" width="{rnd.randint(14,34)}" height="3.4" rx="1.7" fill="{rnd.choice(cols)}" opacity=".8"/>')
    s.append('<path d="M46 208H262L278 222H30Z" fill="#241256" stroke="#8b5cf6" stroke-width="1.8" stroke-linejoin="round"/><path d="M120 215h68" stroke="#6d28d9" stroke-width="2" stroke-linecap="round"/>')
    # plant
    s.append('<path d="M273 168h32l-5 42h-22z" fill="#3b1d8a" stroke="#7c3aed" stroke-width="1.2"/>')
    for ang, c in [(-38, "#22c55e"), (-12, "#4ade80"), (14, "#16a34a"), (40, "#22c55e"), (0, "#86efac")]:
        s.append(f'<ellipse cx="289" cy="140" rx="7" ry="28" fill="{c}" transform="rotate({ang} 289 168)" opacity=".95"/>')
    # mug
    s.append('<rect x="14" y="222" width="46" height="46" rx="6" fill="#2a1568" stroke="#8b5cf6" stroke-width="1.8"/>'
             '<path d="M60 232q17 0 17 14t-17 14" fill="none" stroke="#8b5cf6" stroke-width="5"/>')
    s.append(txt(37, 251, "</>", 13, "#4ee1ff", 700, "middle", family=MONO))
    # headphones
    s.append('<path d="M322 262q0-46 32-46t32 46" fill="none" stroke="#3a1d8a" stroke-width="9" stroke-linecap="round"/>'
             '<ellipse cx="322" cy="256" rx="12" ry="18" fill="#2a1568" stroke="#e879f9" stroke-width="2"/>'
             '<ellipse cx="386" cy="256" rx="12" ry="18" fill="#2a1568" stroke="#e879f9" stroke-width="2"/>')
    # handwritten sign
    s.append('<g transform="rotate(-9 350 100)" font-family="' + SCRIPT + '" font-style="italic">')
    for i, (line, c) in enumerate([("Better", "#ddd6fe"), ("Code", "#c4b5fd"), ("Bigger", "#e9d5ff"), ("Dreams.", "#f0abfc")]):
        s.append(f'<text x="352" y="{52+i*30}" font-size="28" fill="{c}" text-anchor="middle">{line}</text>')
    s.append('<path d="M318 156q30-7 62-2" fill="none" stroke="#f472b6" stroke-width="2.4" stroke-linecap="round"/>')
    s.append('<path d="M372 18l4 9 6-6 3 9h-16z" fill="#f0abfc"/></g>')
    s.append('</g>')
    s.append(f'<rect width="{iw}" height="{ih}" rx="12" fill="none" stroke="url(#gBorder)" stroke-width="1.6"/></g>')
    o.extend(s)

    # focus / passion pills
    py = y0 + 372
    for px, top, bottom, kind in [(584, "Focus", "Development", "t"), (778, "Passion", "Creativity", "h")]:
        o.append(f'<rect x="{px}" y="{py-40}" width="182" height="46" rx="23" fill="#120d3a" stroke="#4c3a9e" stroke-width="1.3"/>')
        if kind == "t":
            o.append(f'<g transform="translate({px+12} {py-31})"><circle cx="14" cy="14" r="13" fill="#ec4899"/><circle cx="14" cy="14" r="8" fill="none" stroke="#fff" stroke-width="1.6"/><circle cx="14" cy="14" r="3.4" fill="#fff"/></g>')
        else:
            o.append(f'<g transform="translate({px+12} {py-31})"><circle cx="14" cy="14" r="13" fill="#ec4899"/><path d="M14 21l-6.2-5.8a3.8 3.8 0 0 1 5.4-5.4l.8.8.8-.8a3.8 3.8 0 0 1 5.4 5.4z" fill="#fff"/></g>')
        o.append(txt(px + 50, py - 22, top, 10.5, "#a78bfa", 400))
        o.append(txt(px + 50, py - 7, bottom, 14, "#ffffff", 600))
    return "".join(o)


# ───────────────────────────── tech stack ─────────────────────────────
def tech_card(x, y, w, title, glyph, items):
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="112" rx="9" fill="#100b32" fill-opacity=".7" stroke="#4b3aa8" stroke-opacity=".9" stroke-width="1.3"/>']
    o.append(f'<g transform="translate({x+12} {y+8}) scale(.82)">{glyph}</g>')
    o.append(txt(x + 38, y + 26, title, 13, "#f5f3ff", 600, fit=est(title, 13, .52)))
    n = len(items)
    step = (w - 24) / n
    for i, (key, label) in enumerate(items):
        cx = x + 12 + step * (i + .5)
        o.append(icon(key, cx - 14, y + 46, 28))
        o.append(txt(cx, y + 96, label, 8.5, "#a1a1c5", 400, "middle"))
    return "".join(o)


def build_tech(y0):
    o = [section_title(W / 2, y0, "Tech Stack", '<circle cx="13" cy="13" r="11" fill="none" stroke="#67e8f9" stroke-width="2"/><path d="M8 14l3.5 3.5L19 9" fill="none" stroke="#67e8f9" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>', centered=True)]
    cy = y0 + 28
    langs = [("html", "HTML"), ("css", "CSS"), ("js", "JS"), ("ts", "TS"), ("python", "Python"), ("php", "PHP")]
    fw = [("react", "React"), ("next", "Next.js"), ("node", "Node.js"), ("express", "Express"), ("bootstrap", "Bootstrap"), ("tailwind", "Tailwind")]
    db = [("mysql", "MySQL"), ("mongodb", "MongoDB"), ("firebase", "Firebase"), ("supabase", "Supabase"), ("laravel", "Laravel")]
    tools = [("git", "Git"), ("github", "GitHub"), ("vscode", "VS Code"), ("figma", "Figma"), ("photoshop", "Ps"), ("illustrator", "Ai")]
    g_lang = '<path d="M9 5L3 13l6 8M17 5l6 8-6 8" fill="none" stroke="#a78bfa" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'
    g_db = ('<ellipse cx="13" cy="6" rx="9" ry="3.6" fill="none" stroke="#67e8f9" stroke-width="2"/>'
            '<path d="M4 6v14c0 2 4 3.6 9 3.6s9-1.6 9-3.6V6M4 13c0 2 4 3.6 9 3.6s9-1.6 9-3.6" fill="none" stroke="#67e8f9" stroke-width="2"/>')
    g_tools = ('<rect x="3" y="4" width="20" height="14" rx="2.5" fill="none" stroke="#f0abfc" stroke-width="2"/>'
               '<path d="M9 23h8M13 18v5" stroke="#f0abfc" stroke-width="2" stroke-linecap="round"/><circle cx="13" cy="11" r="2.4" fill="#f0abfc"/>')
    x = 30
    for title, glyph, items, w in [("Languages", g_lang, langs, 224), ("Frameworks & Libraries", g_orbit("#67e8f9"), fw, 268),
                                   ("Databases & Backend", g_db, db, 224), ("Design & Tools", g_tools, tools, 224)]:
        o.append(tech_card(x, cy, w, title, glyph, items))
        x += w + 8
    return "".join(o)


# ───────────────────────────── stats row ─────────────────────────────
LANG_COLORS = {"JavaScript": "#f7c948", "TypeScript": "#38bdf8", "HTML": "#f97316", "CSS": "#a855f7", "Python": "#22d3ee",
               "PHP": "#8e93d0", "Java": "#f43f5e", "C++": "#ec4899", "C": "#94a3b8", "Vue": "#4ade80", "Other": "#6366f1"}


def build_stats(y_title, d):
    o = []
    py, ph = y_title + 18, 136
    x1, w1 = 30, 380
    x2, w2 = 424, 220
    x3, w3 = 658, 336
    o.append(section_title(x1, y_title, "GitHub Stats", g_chart(), width=x1 + w1 - (x1 + 32 + est("GitHub Stats", 20, .52) + 14) - 6))
    o.append(section_title(x2, y_title, "GitHub Streak", g_flame("#fb923c", .95), width=w2 - 32 - est("GitHub Streak", 20, .52) - 14 - 4))
    o.append(section_title(x3, y_title, "Contribution Graph", g_calendar(), width=w3 - 32 - est("Contribution Graph", 20, .52) - 14))
    for x, w in [(x1, w1), (x2, w2), (x3, w3)]:
        o.append(f'<rect x="{x}" y="{py}" width="{w}" height="{ph}" rx="10" fill="#100b32" fill-opacity=".72" stroke="url(#gBorder)" stroke-width="1.5"/>')

    # ── panel 1: numbers + donut ──
    o.append(txt(x1 + 18, py + 26, USER, 15, "#22d3ee", 700, fit=est(USER, 15, .55)))
    stat_rows = [("Total Commits", d["commits"], "#f472b6", "commit"), ("Repositories", d["repos"], "#f0abfc", "repo"),
                 ("Pull Requests", d["prs"], "#f472b6", "pr"), ("Issues", d["issues"], "#f472b6", "issue")]
    ry = py + 52
    for label, val, c, kind in stat_rows:
        if kind == "commit":
            o.append(f'<circle cx="{x1+27}" cy="{ry-4}" r="5" fill="none" stroke="{c}" stroke-width="2"/><path d="M{x1+18} {ry-4}h4M{x1+32} {ry-4}h4" stroke="{c}" stroke-width="2"/>')
        elif kind == "repo":
            o.append(f'<rect x="{x1+20}" y="{ry-11}" width="14" height="14" rx="2.5" fill="none" stroke="{c}" stroke-width="2"/><path d="M{x1+24} {ry-6}h6" stroke="{c}" stroke-width="2"/>')
        elif kind == "pr":
            o.append(f'<circle cx="{x1+22}" cy="{ry-8}" r="2.6" fill="none" stroke="{c}" stroke-width="1.8"/><circle cx="{x1+22}" cy="{ry+1}" r="2.6" fill="none" stroke="{c}" stroke-width="1.8"/><circle cx="{x1+33}" cy="{ry+1}" r="2.6" fill="none" stroke="{c}" stroke-width="1.8"/><path d="M{x1+22} {ry-5.4}v4M{x1+33} {ry-1.6}v-5q0-3-3-3h-3" fill="none" stroke="{c}" stroke-width="1.8"/>')
        else:
            o.append(f'<circle cx="{x1+27}" cy="{ry-4}" r="7.5" fill="none" stroke="{c}" stroke-width="2"/><circle cx="{x1+27}" cy="{ry-4}" r="1.8" fill="{c}"/>')
        o.append(txt(x1 + 46, ry, label, 13, "#e5e7eb", 400, fit=est(label, 13, .5)))
        o.append(txt(x1 + 156, ry, fmt(val), 13, "#a5b4fc", 500))
        ry += 25
    # donut
    cx, cy, r, sw = x1 + 262, py + 78, 27, 12
    o.append(txt(cx, py + 26, "Most Used Language", 11, "#e5e7eb", 400, "middle", fit=112))
    langs = sorted(d["langs"].items(), key=lambda kv: -kv[1])
    total = sum(v for _, v in langs) or 1
    top = langs[:4]
    other = sum(v for _, v in langs[4:])
    segs = [(k, v) for k, v in top] + ([("Other", other)] if other else [])
    if not segs:
        segs = [("Other", 1)]
    C = 2 * math.pi * r
    cum = 0.0
    for k, v in segs:
        ln = C * v / total
        col = LANG_COLORS.get(k, "#6366f1")
        gap = min(2.5, ln * .3)
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-dasharray="{max(ln-gap,0.1):.2f} {C-max(ln-gap,0.1):.2f}" stroke-dashoffset="{-cum:.2f}" transform="rotate(-90 {cx} {cy})"/>')
        cum += ln
    lab = {"JavaScript": "JS", "TypeScript": "TS"}.get(segs[0][0], segs[0][0][:4])
    o.append(txt(cx, cy + 4.5, lab, 12.5, "#ffffff", 700, "middle"))
    ly = py + 52
    for k, v in segs[:5]:
        o.append(f'<circle cx="{x1+304}" cy="{ly-3.5}" r="3.6" fill="{LANG_COLORS.get(k, "#6366f1")}"/>')
        o.append(txt(x1 + 313, ly, k, 10.5, "#d4d4e8", 400, fit=est(k, 10.5, .5)))
        ly += 17

    # ── panel 2: streak ──
    cur, longest = streaks(d["days"])
    fx, fy = x2 + 20, py + 26
    o.append(f'<circle cx="{fx+22}" cy="{fy+30}" r="30" fill="url(#rGlow)"/>')
    o.append(f'<g transform="translate({fx} {fy}) scale(1.75)" filter="url(#glowS)">'
             '<path d="M13 1c1.5 6-5 9-5 15a7 7 0 0 0 14 0c0-3-1.5-5-3-7 0 3-1.5 4.5-3 4.5 1.5-5 0-9-3-12.5z" fill="url(#gFlame)"/>'
             '<path d="M14 12c.5 3-2.6 4-2.6 7a2.6 2.6 0 0 0 5.2 0c0-1.6-1-2.4-1.6-3.8-.4 1.3-.7 1.8-1 1.8z" fill="#fde68a" opacity=".9"/></g>')
    o.append(txt(x2 + 96, py + 62, fmt(cur), 22, "#ffffff", 700))
    o.append(txt(x2 + 96, py + 82, "Days", 13, "#a1a1c5", 400))
    o.append(txt(x2 + 18, py + 106, f"Longest Streak:  {longest}", 11.5, "#d4d4e8", 400, fit=est(f"Longest Streak:  {longest}", 11.5, .5)))
    fl = min(cur, 10)
    for i in range(10):
        col = "#fb7185" if i < fl else "#3b2a6a"
        o.append(f'<g transform="translate({x2+18+i*19} {py+114}) scale(.42)" opacity="{1 if i < fl else .8}">{g_flame(col, 1)}</g>')

    # ── panel 3: heat-map ──
    days = d["days"]
    gx, gy = x3 + 16, py + 40
    pitch_x = (w3 - 32) / 52
    cw, chh, pitch_y = pitch_x * .8, 8.0, 9.4
    palette = ["#221b48", "#5b21b6", "#a21caf", "#db2777", "#f9a8d4"]
    last_month, lastx = None, -99
    for c in days:
        x = gx + c["col"] * pitch_x
        y = gy + c["row"] * pitch_y
        o.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{cw:.2f}" height="{chh}" rx="1.4" fill="{palette[c["level"]]}"/>')
        if c["row"] == 0:
            mon = c["date"][5:7]
            if mon != last_month:
                if x - lastx > 20:
                    o.append(txt(x, py + 30, ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][int(mon) - 1], 8.5, "#a1a1c5", 400))
                    lastx = x
                last_month = mon
    if not days:
        o.append(txt(x3 + w3 / 2, py + 70, "Contribution data unavailable", 12, "#a1a1c5", 400, "middle"))
    ly = py + ph - 14
    o.append(txt(gx, ly + 4, "Less", 9.5, "#a1a1c5", 400))
    for i, c in enumerate(palette):
        o.append(f'<rect x="{gx+30+i*13}" y="{ly-4}" width="10" height="10" rx="2" fill="{c}"/>')
    o.append(txt(gx + 30 + 5 * 13 + 4, ly + 4, "More", 9.5, "#a1a1c5", 400))
    return "".join(o), py + ph


# ───────────────────────────── snake panel ─────────────────────────────
def build_snake(y_title, d):
    o = [section_title(30, y_title, "Contribution Snake", g_snake(), width=W - 60 - 32 - est("Contribution Snake", 20, .52) - 14)]
    py, ph = y_title + 18, 104
    o.append(f'<rect x="30" y="{py}" width="964" height="{ph}" rx="10" fill="#100b32" fill-opacity=".72" stroke="url(#gBorder)" stroke-width="1.5"/>')
    palette = ["#2a2160", "#6d28d9", "#a21caf", "#db2777", "#f9a8d4"]
    cells = {(c["row"], c["col"]): c["level"] for c in d["days"]}
    gx, gy, pitch = 50, py + 10, 12.2
    for col in range(52):
        for row in range(7):
            lv = cells.get((row, col), 0)
            o.append(f'<circle cx="{gx+col*pitch:.1f}" cy="{gy+row*pitch:.1f}" r="{1.9 if lv==0 else 2.6}" fill="{palette[lv]}" opacity="{.55 if lv==0 else .95}"/>')
    # the snake
    n = 70
    pts = []
    for i in range(n):
        t = i / (n - 1)
        x = 70 + t * 560
        y = py + 10 + 3 * pitch + math.sin(t * math.pi * 3.2) * 2.4 * pitch
        pts.append((x, y))
    for i, (x, y) in enumerate(pts):
        t = i / (n - 1)
        if t < .45:
            col = "#ec4899"
        elif t < .75:
            col = "#22d3ee"
        else:
            col = "#f472b6"
        rad = 2.6 + 3.4 * t
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rad:.1f}" fill="{col}"><animate attributeName="r" values="{rad:.1f};{rad*1.35:.1f};{rad:.1f}" dur="2.4s" begin="{i*0.05:.2f}s" repeatCount="indefinite"/></circle>')
    hx, hy = pts[-1]
    o.append(f'<circle cx="{hx+4:.1f}" cy="{hy:.1f}" r="9" fill="#f472b6" filter="url(#glowS)"/><circle cx="{hx+7:.1f}" cy="{hy-2:.1f}" r="1.8" fill="#06051b"/>')
    o.append(f'<path d="M{hx-4:.0f} {hy-8:.0f}l3-7 4 4 4-6 3 8z" fill="#f0abfc" stroke="#fdf4ff" stroke-width=".6"/>')
    # info box
    o.append(f'<rect x="704" y="{py+12}" width="276" height="{ph-24}" rx="8" fill="#0a0826" stroke="#3b2f88" stroke-width="1.2"/>')
    o.append(icon("github", 720, py + 24, 20, "#ffffff"))
    o.append(txt(748, py + 39, "GitHub Action", 12.5, "#22d3ee", 500))
    o.append(txt(720, py + 60, "This section is generated by a GitHub Action", 10.5, "#c7c7e0", 400, fit=236))
    o.append(txt(720, py + 76, "workflow and refreshes automatically every day.", 10.5, "#c7c7e0", 400, fit=236))
    return "".join(o), py + ph


# ───────────────────────────── top-level composition ─────────────────────────────
def build_top(d):
    body = [build_hero(d)]
    y = 332
    body.append(build_about(y, d))
    y_tech = y + 390 + 44
    body.append(build_tech(y_tech))
    y_stats = y_tech + 28 + 112 + 40
    stats, y_end = build_stats(y_stats, d)
    body.append(stats)
    y_snake = y_end + 40
    snake, y_end2 = build_snake(y_snake, d)
    body.append(snake)
    h = y_end2 + 22
    return svg_doc(W, h, "".join(body))


# ───────────────────────────── separate (clickable) pieces ─────────────────────────────
def header_svg(title, glyph):
    return svg_doc(W, 56, section_title(30, 30, title, glyph, width=W - 60 - 32 - est(title, 20, .52) - 14))


def project_card(p):
    w, h = 502, 100
    o = [f'<rect x="8" y="6" width="{w-16}" height="{h-12}" rx="12" fill="#100b32" fill-opacity=".85" stroke="url(#gBorder)" stroke-width="1.5"/>']
    o.append('<rect x="24" y="22" width="56" height="56" rx="12" fill="#150f42" stroke="#5b3fd0" stroke-width="1.4"/>')
    o.append('<path d="M45 40l-8 10 8 10M59 40l8 10-8 10M54 36l-4 28" fill="none" stroke="#22d3ee" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" filter="url(#glowS)"/>')
    o.append(txt(96, 36, p["name"], 15.5, "#22d3ee", 700, fit=est(p["name"], 15.5, .53)))
    o.append(txt(96, 55, p["desc"], 11, "#b9b9d6", 400, fit=min(est(p["desc"], 11, .5), 350)))
    x = 96
    for tg in p["tags"]:
        tw = est(tg, 10, .55) + 18
        o.append(f'<rect x="{x}" y="64" width="{tw}" height="18" rx="9" fill="#1a1250" stroke="#4b3aa8" stroke-width="1"/>')
        o.append(txt(x + tw / 2, 76.5, tg, 10, "#a5b4fc", 500, "middle"))
        x += tw + 8
    o.append('<circle cx="460" cy="50" r="15" fill="none" stroke="#7c3aed" stroke-width="1.4"/>'
             '<path d="M455 43l8 7-8 7" fill="none" stroke="#e879f9" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>')
    return svg_doc(w, h, "".join(o), bg=False)


def social_button(key, label):
    w, h = 150, 52
    grads = {
        "linkedin": ("#0a66c2", "#1e8de0"), "x": ("#0b0b12", "#1c1c28"), "instagram": ("#f09433", "#bc1888"),
        "tiktok": ("#0b0b12", "#1c1c28"), "youtube": ("#ff1a1a", "#c4171b"), "gmail": ("#8b5cf6", "#c026d3"),
    }
    a, b = grads[key]
    extra = f'<linearGradient id="bt" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>'
    stroke = "#ffffff" if key in ("x", "tiktok") else "none"
    body = (f'<rect x="3" y="4" width="{w-6}" height="{h-8}" rx="22" fill="url(#bt)" stroke="{stroke}" stroke-opacity=".35" stroke-width="1.2"/>')
    color = {"tiktok": "#ffffff", "gmail": "#ffffff"}.get(key, "#ffffff")
    body += icon(key, 20, 14, 24, color)
    body += txt(54, 31, label, 12.5, "#ffffff", 700, fit=est(label, 12.5, .55))
    return svg_doc(w, h, body, extra_defs=extra, bg=False)


def build_footer():
    w, h = 1024, 190
    rnd = random.Random(9)
    o = [f'<rect width="{w}" height="{h}" fill="{BG}"/>',
         '<linearGradient id="gFoot" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#06051b"/><stop offset="1" stop-color="#1c0d4a"/></linearGradient>',
         f'<rect width="{w}" height="{h}" fill="url(#gFoot)"/>']
    for _ in range(40):
        o.append(f'<circle cx="{rnd.uniform(0,w):.0f}" cy="{rnd.uniform(0,120):.0f}" r="{rnd.choice([.7,1,1.4])}" fill="#fff" opacity="{rnd.uniform(.3,.9):.2f}"/>')
    for (x, y, r, c) in [(100, 60, 5, "#f0abfc"), (560, 40, 4, "#67e8f9"), (700, 96, 3.5, "#f0abfc"), (420, 24, 3, "#fff")]:
        o.append(f'<g>{sparkle(x, y, r, c)}<animate attributeName="opacity" values="1;.3;1" dur="3.4s" repeatCount="indefinite"/></g>')
    # hills
    o.append('<path d="M0 132C120 96 240 96 360 122S600 150 720 118 900 92 1024 112V190H0Z" fill="url(#gHill2)" opacity=".9"/>')
    o.append('<path d="M0 156C140 126 300 132 430 150S700 168 820 140 950 128 1024 138V190H0Z" fill="url(#gHill1)" opacity=".95"/>')
    o.append('<path d="M0 176C200 160 380 172 560 176S860 170 1024 164V190H0Z" fill="#0c0730"/>')
    o.append(f'<text x="470" y="86" font-family="{SCRIPT}" font-style="italic" font-size="42" fill="url(#gThanks)" text-anchor="middle" transform="rotate(-3 470 86)" filter="url(#glowS)" textLength="330" lengthAdjust="spacingAndGlyphs">Thanks for visiting!</text>')
    o.append('<path d="M470 128l-15-14a8.5 8.5 0 0 1 12-12l3 3 3-3a8.5 8.5 0 0 1 12 12z" fill="#f472b6" filter="url(#glowS)"/>')
    o.append('<path d="M380 100q90 16 180 0" fill="none" stroke="#e879f9" stroke-width="1.6" stroke-linecap="round" opacity=".7"/>')
    # astronaut
    o.append('<g transform="translate(884 42)">'
             '<rect x="-40" y="62" width="76" height="40" rx="6" fill="#171040"/>'
             '<path d="M-30 56h58l6 26h-70z" fill="#ffffff"/>'
             '<rect x="-14" y="66" width="34" height="4" rx="2" fill="#c4b5fd"/>'
             '<rect x="-2" y="26" width="46" height="46" rx="14" fill="#e9e5ff"/>'
             '<rect x="-16" y="30" width="20" height="36" rx="8" fill="#b8b0f0"/>'
             '<circle cx="24" cy="12" r="26" fill="#f3f0ff"/>'
             '<ellipse cx="30" cy="12" rx="17" ry="14" fill="url(#rVisor)" stroke="#a78bfa" stroke-width="2"/>'
             '<ellipse cx="25" cy="7" rx="5" ry="3" fill="#fff" opacity=".55"/>'
             '<rect x="-22" y="72" width="66" height="34" rx="4" fill="#100a30" stroke="#8b5cf6" stroke-width="1.6" transform="rotate(-8 10 90)"/>'
             '<rect x="-10" y="80" width="30" height="3" rx="1.5" fill="#22d3ee" transform="rotate(-8 10 90)"/>'
             '<rect x="-10" y="88" width="20" height="3" rx="1.5" fill="#f472b6" transform="rotate(-8 10 90)"/></g>')
    return svg_doc(w, h, "".join(o), bg=False)


def main():
    ASSETS.mkdir(exist_ok=True)
    print(f"Collecting data for {USER} ...")
    d = collect()
    print(f"  followers={d['followers']} repos={d['repos']} stars={d['stars']} commits={d['commits']} "
          f"prs={d['prs']} issues={d['issues']} days={len(d['days'])} langs={dict(list(d['langs'].items())[:5])}")
    (ASSETS / "profile-top.svg").write_text(build_top(d), encoding="utf-8")
    (ASSETS / "header-projects.svg").write_text(header_svg("Featured Projects", g_rocket()), encoding="utf-8")
    (ASSETS / "header-connect.svg").write_text(header_svg("Connect With Me", g_link()), encoding="utf-8")
    for i, p in enumerate(PROJECTS, 1):
        (ASSETS / f"project-{i}.svg").write_text(project_card(p), encoding="utf-8")
    for key, label, _ in SOCIALS:
        (ASSETS / f"social-{key}.svg").write_text(social_button(key, label), encoding="utf-8")
    (ASSETS / "footer.svg").write_text(build_footer(), encoding="utf-8")
    write_readme()
    print("Done.")


def write_readme():
    cards = []
    for i, p in enumerate(PROJECTS, 1):
        cards.append(f'<a href="{p["url"]}"><img src="assets/project-{i}.svg" width="49%" alt="{esc(p["name"])} \u2014 {esc(p["desc"])}"/></a>')
    row1 = "\n  ".join(cards[:2])
    row2 = "\n  ".join(cards[2:])
    btns = "\n  ".join(
        f'<a href="{url}"><img src="assets/social-{key}.svg" height="42" alt="{label}"/></a>' for key, label, url in SOCIALS)
    readme = f"""<!--
  This profile is drawn with generated SVGs (see /scripts/generate_profile.py).
  Edit text/links at the top of that script, then run it (or wait for the daily workflow).
-->
<div align="center">

<img src="assets/profile-top.svg" width="100%" alt="Hey there, I'm {DISPLAY_NAME} \u2014 {ROLE}. About me, tech stack, GitHub stats, streak, contribution graph and contribution snake."/>

<img src="assets/header-projects.svg" width="100%" alt="Featured Projects"/>

{row1}
<br/>
{row2}

<img src="assets/header-connect.svg" width="100%" alt="Connect With Me"/>

{btns}

<img src="assets/footer.svg" width="100%" alt="Thanks for visiting!"/>

</div>

<!--
  Plain-text summary for screen readers and search:
  {DISPLAY_NAME} ({USER}) \u2014 {ROLE}. Currently working on {WORKING_ON}; learning {LEARNING}.
  Stack: HTML, CSS, JavaScript, React, Vite, Firebase, Supabase, Git.
-->
"""
    (ROOT / "README.md").write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    main()
