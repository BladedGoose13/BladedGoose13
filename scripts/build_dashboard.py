"""Render assets/dashboard.svg from live GitHub data.

Why this exists instead of the usual third-party cards: at build time the
public instances of github-readme-stats (503 DEPLOYMENT_PAUSED),
github-profile-trophy (402 DEPLOYMENT_DISABLED) and
github-readme-activity-graph (402) were all down, which leaves a profile
full of broken images. Generating the panel here and committing the SVG
means the dashboard is a static asset GitHub serves itself -- it cannot
rate-limit, expire or 402.

Usage
    GITHUB_TOKEN=... python scripts/build_dashboard.py            # live
    python scripts/build_dashboard.py --seed                      # offline seed

The seed path renders the repository facts that are known statically and
marks the contribution panels as awaiting their first sync, so the asset is
never a lie about data it does not have.
"""
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette import (AMBER, BG0, BG1, BG2, CREAM, LINE, MONO, MUTED, PINE,
                     SAND, SANS, ramp)

LOGIN = os.environ.get("PROFILE_LOGIN", "BladedGoose13")
W, H = 1200, 556
API = "https://api.github.com/graphql"

QUERY = """
query($login:String!) {
  user(login:$login) {
    name login createdAt
    followers { totalCount }
    repositories(first:100, ownerAffiliations:OWNER, isFork:false,
                 privacy:PUBLIC,
                 orderBy:{field:PUSHED_AT, direction:DESC}) {
      totalCount
      nodes {
        name stargazerCount forkCount pushedAt
        languages(first:12, orderBy:{field:SIZE, direction:DESC}) {
          edges { size node { name } }
        }
      }
    }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount weekday } }
      }
    }
  }
}
"""

# Public repository facts, used by --seed only.
# Deliberately excludes the owner's private repositories: this file's output is
# committed to a public repo, so nothing private may appear in it.
SEED_REPOS = [
    ("QE-Workflow", "Gnuplot", 98780, 1),
    ("PathWise", "HTML", 13839, 1),
    ("STREAMLIT-Memorama", "Python", 2815, 0),
    ("ESG-Framework-LUMIO", "Other", 1460, 0),
    ("ThermoHub.Sim---V1.0", "Python", 429, 0),
    ("Portfolio", "HTML", 23, 0),
]


# --------------------------------------------------------------------------
# data
# --------------------------------------------------------------------------
def fetch(token):
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": "bearer " + token,
                 "Content-Type": "application/json",
                 "User-Agent": "profile-dashboard"})
    with urllib.request.urlopen(req, timeout=45) as r:
        payload = json.load(r)
    if "errors" in payload:
        raise RuntimeError(payload["errors"])
    return payload["data"]["user"]


def streaks(days):
    """(current, longest) run of consecutive days with >=1 contribution.

    Today is skipped when empty so an in-progress day never breaks the run.
    """
    best = cur = run = 0
    for i, d in enumerate(days):
        if d["contributionCount"] > 0:
            run += 1
            best = max(best, run)
        elif not (i == len(days) - 1):
            run = 0
        else:
            break
    for d in reversed(days):
        if d["contributionCount"] > 0:
            cur += 1
        elif cur or d is not days[-1]:
            break
    return cur, best


def shape(user):
    repos = user["repositories"]["nodes"]
    lang = {}
    for r in repos:
        for e in r["languages"]["edges"]:
            lang[e["node"]["name"]] = lang.get(e["node"]["name"], 0) + e["size"]
    cc = user["contributionsCollection"]
    cal = cc["contributionCalendar"]
    weeks = [[d for d in w["contributionDays"]] for w in cal["weeks"]]
    days = [d for w in weeks for d in w]
    cur, best = streaks(days)
    top = sorted(repos, key=lambda r: -sum(e["size"] for e in r["languages"]["edges"]))[:4]
    return {
        "live": True,
        "top": [(r["name"],
                 (r["languages"]["edges"][0]["node"]["name"]
                  if r["languages"]["edges"] else "--"),
                 sum(e["size"] for e in r["languages"]["edges"]),
                 r["stargazerCount"]) for r in top],
        "mass": sum(v for v in lang.values()),
        "repos": user["repositories"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in repos),
        "followers": user["followers"]["totalCount"],
        "commits": cc["totalCommitContributions"] + cc["restrictedContributionsCount"],
        "prs": cc["totalPullRequestContributions"],
        "contribs": cal["totalContributions"],
        "streak": cur,
        "best": best,
        "peak": max((d["contributionCount"] for d in days), default=0),
        "weeks": weeks,
        "langs": sorted(lang.items(), key=lambda kv: -kv[1]),
        "since": user["createdAt"][:4],
    }


def seed():
    # SEED_REPOS sizes come from the REST API, which reports KB; everything
    # downstream works in bytes.
    repos = [(n, l, kb * 1024, st) for (n, l, kb, st) in SEED_REPOS]
    lang = {}
    for _, l, size, _ in repos:
        if l != "Other":
            lang[l] = lang.get(l, 0) + size
    return {
        "live": False,
        "top": sorted(repos, key=lambda r: -r[2])[:4],
        "mass": sum(v for v in lang.values()),
        "repos": len(SEED_REPOS),
        "stars": sum(s for *_, s in SEED_REPOS),
        "followers": 6,
        "commits": None, "prs": None, "contribs": None,
        "streak": None, "best": None, "peak": 0,
        "weeks": [],
        "langs": sorted(lang.items(), key=lambda kv: -kv[1]),
        "since": "2024",
    }


# --------------------------------------------------------------------------
# svg helpers
# --------------------------------------------------------------------------
def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def human(n):
    if n is None:
        return "--"
    if n >= 1000000:
        return "%.1fM" % (n / 1e6)
    if n >= 10000:
        return "%.1fk" % (n / 1e3)
    return str(n)


def countup(x, y, value, size, fill, frames=13, dur=1.15, begin=0.35):
    """Numeric count-up built from <set> keyframes.

    SMIL cannot tween text content, so each intermediate value is its own
    <text> toggled on at its slot and off at the next. The final frame is
    authored visible with no hide, which is also what a renderer that ignores
    SMIL entirely will show -- so the true number is what appears either way.
    """
    if value is None or value < 8:
        return ('<text x="%d" y="%d" font-family=%s font-size="%d" font-weight="700" '
                'fill="%s">%s</text>' % (x, y, '"%s"' % SANS, size, fill, human(value)))
    out, step = [], dur / frames
    for i in range(frames):
        t = (i + 1) / frames
        v = int(round(value * (1 - (1 - t) ** 3)))          # ease-out cubic
        last = i == frames - 1
        vis = '1' if last else '0'
        node = ('<text x="%d" y="%d" font-family=%s font-size="%d" font-weight="700" '
                'fill="%s" opacity="%s">%s'
                % (x, y, '"%s"' % SANS, size, fill, vis, human(v)))
        node += '<set attributeName="opacity" to="1" begin="%.3fs"/>' % (begin + i * step)
        if not last:
            node += '<set attributeName="opacity" to="0" begin="%.3fs"/>' % (begin + (i + 1) * step)
        out.append(node + "</text>")
    return "".join(out)


def build(d):
    now = dt.datetime.now(dt.timezone.utc)
    o = []
    a = o.append
    a('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
      'role="img" aria-label="GitHub activity dashboard for %s">' % (W, H, W, H, LOGIN))

    a('<defs>')
    a('<linearGradient id="dbg" x1="0" y1="0" x2="1" y2="1">'
      '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (BG1, BG0))
    a('<linearGradient id="tile" x1="0" y1="0" x2="0" y2="1">'
      '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (BG2, BG1))
    a('<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">'
      '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (AMBER, BROWN_ACCENT))
    a('<clipPath id="dclip"><rect width="%d" height="%d" rx="14"/></clipPath>' % (W, H))
    a('</defs>')

    a('<g clip-path="url(#dclip)">')
    a('<rect width="%d" height="%d" fill="url(#dbg)"/>' % (W, H))

    # ---- header ----------------------------------------------------------
    a('<circle cx="34" cy="34" r="5" fill="%s"><animate attributeName="opacity" '
      'values="1;.25;1" dur="2.4s" repeatCount="indefinite"/></circle>' % AMBER)
    a('<circle cx="34" cy="34" r="5" fill="none" stroke="%s" stroke-width="1.2" opacity="0">'
      '<animate attributeName="r" values="5;14" dur="2.4s" repeatCount="indefinite"/>'
      '<animate attributeName="opacity" values=".7;0" dur="2.4s" repeatCount="indefinite"/></circle>' % AMBER)
    a('<text x="52" y="40" font-family=%s font-size="15" font-weight="700" fill="%s" '
      'letter-spacing="3.4">SYSTEMS DASHBOARD</text>' % ('"%s"' % SANS, CREAM))
    stamp = ("synced %s UTC &#183; regenerated daily"
             % now.strftime("%d %b %Y %H:%M")) if d["live"] else "awaiting first sync"
    a('<text x="%d" y="40" text-anchor="end" font-family=%s font-size="10.5" fill="%s" '
      'letter-spacing="1.4">%s</text>' % (W - 30, '"%s"' % MONO, MUTED, stamp))
    a('<path d="M30 56 H%d" stroke="%s" stroke-width="1"/>' % (W - 30, LINE))

    # ---- KPI tiles -------------------------------------------------------
    tiles = [("CONTRIBUTIONS", d["contribs"], "12 mo"),
             ("COMMITS", d["commits"], "12 mo"),
             ("REPOSITORIES", d["repos"], "public"),
             ("SOURCE MASS", None, human_bytes(d["mass"])),
             ("LONGEST STREAK", d["best"], "days")]
    tw, gap, x0, ty = 220, 12, 30, 76
    for i, (label, val, unit) in enumerate(tiles):
        x = x0 + i * (tw + gap)
        a('<g opacity="1"><animate attributeName="opacity" values="0;1" dur=".5s" '
          'begin="%.2fs" fill="freeze"/>' % (0.08 * i))
        a('<rect x="%d" y="%d" width="%d" height="92" rx="10" fill="url(#tile)" '
          'stroke="%s"/>' % (x, ty, tw, LINE))
        a('<rect x="%d" y="%d" width="3" height="92" rx="1.5" fill="%s" opacity=".95"/>'
          % (x, ty, ramp(0.36 + 0.13 * i)))
        a('<text x="%d" y="%d" font-family=%s font-size="9.5" fill="%s" letter-spacing="2">'
          '%s</text>' % (x + 18, ty + 25, '"%s"' % MONO, MUTED, label))
        if label == "SOURCE MASS":
            a('<text x="%d" y="%d" font-family=%s font-size="30" font-weight="700" '
              'fill="%s">%s</text>' % (x + 18, ty + 66, '"%s"' % SANS, CREAM, unit))
        else:
            a(countup(x + 18, ty + 66, val, 34, CREAM, begin=0.3 + 0.08 * i))
            a('<text x="%d" y="%d" text-anchor="end" font-family=%s font-size="9.5" '
              'fill="%s">%s</text>' % (x + tw - 16, ty + 66, '"%s"' % MONO, MUTED, unit))
        a('</g>')

    # ---- panel frames ----------------------------------------------------
    py, ph = 190, 214
    lw = 470
    rx0 = 30 + lw + 16
    rw = W - 30 - rx0
    for (px, pw, title, sub) in ((30, lw, "LANGUAGE MASS", "bytes across public repositories"),
                                 (rx0, rw, "CONTRIBUTION FIELD", "52 weeks &#183; daily resolution")):
        a('<rect x="%d" y="%d" width="%d" height="%d" rx="12" fill="%s" stroke="%s"/>'
          % (px, py, pw, ph, BG1, LINE))
        a('<text x="%d" y="%d" font-family=%s font-size="11.5" font-weight="700" fill="%s" '
          'letter-spacing="2.6">%s</text>' % (px + 20, py + 30, '"%s"' % SANS, SAND, title))
        a('<text x="%d" y="%d" text-anchor="end" font-family=%s font-size="9" fill="%s">%s</text>'
          % (px + pw - 18, py + 30, '"%s"' % MONO, MUTED, sub))

    # ---- language bars ---------------------------------------------------
    langs = d["langs"][:5]
    total = sum(v for _, v in langs) or 1
    by = py + 54
    for i, (name, size) in enumerate(langs):
        frac = size / total
        yy = by + i * 29
        col = ramp(0.18 + 0.72 * (i / max(1, len(langs) - 1)))
        a('<text x="%d" y="%d" font-family=%s font-size="11" fill="%s">%s</text>'
          % (30 + 20, yy + 4, '"%s"' % SANS, CREAM, esc(name)))
        a('<text x="%d" y="%d" text-anchor="end" font-family=%s font-size="10" fill="%s">'
          '%.1f%%</text>' % (30 + lw - 20, yy + 4, '"%s"' % MONO, MUTED, frac * 100))
        track = lw - 40
        a('<rect x="%d" y="%d" width="%d" height="6" rx="3" fill="%s"/>'
          % (50, yy + 12, track, BG2))
        bw = max(3, int(track * frac))
        a('<rect x="%d" y="%d" width="%d" height="6" rx="3" fill="%s">'
          '<animate attributeName="width" values="0;%d" dur=".9s" begin="%.2fs" '
          'fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1"/></rect>'
          % (50, yy + 12, bw, col, bw, 0.45 + 0.09 * i))
    a('<text x="%d" y="%d" font-family=%s font-size="9.5" fill="%s">total %s of source '
      '&#183; %d repositories &#183; building since %s</text>'
      % (50, py + ph - 16, '"%s"' % MONO, MUTED,
         human_bytes(total), d["repos"], d["since"]))

    # ---- contribution field ----------------------------------------------
    cell, cgap = 8, 2
    gx, gy = rx0 + 20, py + 56
    if d["weeks"]:
        weeks = d["weeks"][-53:]
        peak = max(1, d["peak"])
        for wi, week in enumerate(weeks):
            a('<g opacity="1"><animate attributeName="opacity" values="0;1" dur=".45s" '
              'begin="%.3fs" fill="freeze"/>' % (0.5 + wi * 0.009))
            for day in week:
                c = day["contributionCount"]
                wd = day["weekday"]
                fill = LINE if c == 0 else ramp(0.20 + 0.78 * min(1.0, (c / peak) ** 0.55))
                a('<rect x="%d" y="%d" width="%d" height="%d" rx="2" fill="%s"/>'
                  % (gx + wi * (cell + cgap), gy + wd * (cell + cgap), cell, cell, fill))
            a('</g>')
        # weekly cadence trace under the grid
        tops = [sum(x["contributionCount"] for x in w) for w in weeks]
        mx = max(tops) or 1
        ly, lh = gy + 7 * (cell + cgap) + 18, 42
        pts = [(gx + i * (cell + cgap) + cell / 2.0, ly + lh - (v / mx) * lh)
               for i, v in enumerate(tops)]
        dd = "M%.0f,%.0f" % pts[0] + "".join(" L%.0f,%.0f" % p for p in pts[1:])
        a('<path d="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-linejoin="round" '
          'stroke-dasharray="1400" stroke-dashoffset="0">'
          '<animate attributeName="stroke-dashoffset" values="1400;0" dur="1.9s" begin=".8s" '
          'fill="freeze"/></path>' % (dd, AMBER))
        a('<text x="%d" y="%d" font-family=%s font-size="9" fill="%s">weekly cadence '
          '&#183; peak %d/day &#183; longest streak %s d</text>'
          % (gx, ly + lh + 16, '"%s"' % MONO, MUTED, d["peak"], human(d["best"])))
    else:
        a('<g opacity=".5">')
        for wi in range(53):
            for wd in range(7):
                a('<rect x="%d" y="%d" width="%d" height="%d" rx="2" fill="%s"/>'
                  % (gx + wi * (cell + cgap), gy + wd * (cell + cgap), cell, cell, LINE))
        a('</g>')
        a('<text x="%d" y="%d" font-family=%s font-size="10" fill="%s">populated on the '
          'first scheduled sync</text>' % (gx, gy + 7 * (cell + cgap) + 30, '"%s"' % MONO, MUTED))


    # ---- active systems strip -------------------------------------------
    sy, sh = py + ph + 16, 112
    a('<rect x="30" y="%d" width="%d" height="%d" rx="12" fill="%s" stroke="%s"/>'
      % (sy, W - 60, sh, BG1, LINE))
    a('<text x="50" y="%d" font-family=%s font-size="11.5" font-weight="700" fill="%s" '
      'letter-spacing="2.6">ACTIVE SYSTEMS</text>' % (sy + 28, '"%s"' % SANS, SAND))
    a('<text x="%d" y="%d" text-anchor="end" font-family=%s font-size="9" fill="%s">'
      'largest tracked repositories &#183; %s stars &#183; %s followers</text>'
      % (W - 48, sy + 28, '"%s"' % MONO, MUTED, human(d["stars"]), human(d["followers"])))

    cwid, cgapx = 262, 14
    for i, (name, lang_name, size, stars) in enumerate(d["top"][:4]):
        cx = 50 + i * (cwid + cgapx)
        col = ramp(0.34 + 0.16 * i)
        a('<g opacity="1"><animate attributeName="opacity" values="0;1" dur=".5s" '
          'begin="%.2fs" fill="freeze"/>' % (0.9 + 0.1 * i))
        a('<rect x="%d" y="%d" width="%d" height="44" rx="8" fill="%s" stroke="%s"/>'
          % (cx, sy + 44, cwid, BG2, LINE))
        a('<circle cx="%d" cy="%d" r="3.5" fill="%s"/>' % (cx + 16, sy + 62, col))
        nm = name if len(name) <= 22 else name[:21] + "\u2026"
        a('<text x="%d" y="%d" font-family=%s font-size="11.5" fill="%s">%s</text>'
          % (cx + 28, sy + 66, '"%s"' % SANS, CREAM, esc(nm)))
        a('<text x="%d" y="%d" font-family=%s font-size="8.5" fill="%s">%s &#183; %s</text>'
          % (cx + 28, sy + 79, '"%s"' % MONO, MUTED, esc(lang_name), human_bytes(size)))
        if stars:
            a('<text x="%d" y="%d" text-anchor="end" font-family=%s font-size="9.5" '
              'fill="%s">&#9733; %d</text>' % (cx + cwid - 14, sy + 66, '"%s"' % MONO, AMBER, stars))
        a('</g>')

    a('</g>')
    a('<rect x=".75" y=".75" width="%.1f" height="%.1f" rx="14" fill="none" stroke="%s" '
      'stroke-width="1.5"/>' % (W - 1.5, H - 1.5, ramp(0.28)))
    a('</svg>')
    return "".join(o)


def human_bytes(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return "%.1f %s" % (n, unit)
        n /= 1024.0


BROWN_ACCENT = "#6B4E3A"

if __name__ == "__main__":
    token = os.environ.get("GITHUB_TOKEN", "")
    want_seed = "--seed" in sys.argv
    data = None
    if token and not want_seed:
        try:
            data = shape(fetch(token))
        except Exception as exc:                     # noqa: BLE001 - degrade, never fail the job
            print("live fetch failed (%s); falling back to seed" % exc, file=sys.stderr)
    if data is None:
        data = seed()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dest = os.path.join(root, "assets", "dashboard.svg")
    svg = build(data)
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print("wrote %s (%.1f KB, live=%s)" % (dest, len(svg.encode()) / 1024.0, data["live"]))
