"""Render assets/dashboard.svg and assets/activity.svg from live GitHub data.

Generated and committed rather than pulled from a card service: at build
time the public instances of github-readme-stats (503), github-profile-trophy
(402) and github-readme-activity-graph (402) were all down, which turns a
profile into a wall of broken images. A committed SVG cannot rate-limit.

Usage
    GITHUB_TOKEN=... python scripts/build_dashboard.py      # live
    python scripts/build_dashboard.py --seed                # offline seed

The seed renders only facts that are known statically; anything derived from
the contribution calendar is shown as awaiting its first sync rather than
invented.
"""
import datetime as dt
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import charts as ch
from charts import F
from palette import (ACCENT, CARD, EDGE, INK, INK_2, INK_3, PAPER)

LOGIN = os.environ.get("PROFILE_LOGIN", "BladedGoose13")
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
        name stargazerCount pushedAt
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

# Public repositories only. This output is committed to a public repo, so no
# private repository name may ever appear in it.
SEED_REPOS = [
    ("QE-Workflow", "Gnuplot", 98780, 1),
    ("PathWise", "HTML", 13839, 1),
    ("STREAMLIT-Memorama", "Python", 2815, 0),
    ("ESG-Framework-LUMIO", "Other", 1460, 0),
    ("ThermoHub.Sim---V1.0", "Python", 429, 0),
    ("Portfolio", "HTML", 23, 0),
]


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


def longest_streak(days):
    best = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] > 0 else 0
        best = max(best, run)
    return best


def shape(user):
    repos = user["repositories"]["nodes"]
    lang = {}
    for r in repos:
        for e in r["languages"]["edges"]:
            lang[e["node"]["name"]] = lang.get(e["node"]["name"], 0) + e["size"]
    cc = user["contributionsCollection"]
    cal = cc["contributionCalendar"]
    weeks = [w["contributionDays"] for w in cal["weeks"]][-53:]
    days = [d for w in weeks for d in w]
    sizes = [(r["name"], sum(e["size"] for e in r["languages"]["edges"])) for r in repos]
    return {
        "live": True,
        "repos": user["repositories"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in repos),
        "commits": cc["totalCommitContributions"] + cc["restrictedContributionsCount"],
        "contribs": cal["totalContributions"],
        "best": longest_streak(days),
        "peak": max((d["contributionCount"] for d in days), default=0),
        "weeks": weeks,
        "langs": sorted(lang.items(), key=lambda kv: -kv[1]),
        "sizes": sorted(sizes, key=lambda kv: -kv[1])[:6],
        "mass": sum(lang.values()),
        "since": user["createdAt"][:4],
    }


def seed():
    repos = [(n, l, kb * 1024, s) for (n, l, kb, s) in SEED_REPOS]  # REST size is KB
    lang = {}
    for _, l, size, _ in repos:
        if l != "Other":
            lang[l] = lang.get(l, 0) + size
    return {
        "live": False,
        "repos": len(repos),
        "stars": sum(s for *_, s in repos),
        "commits": None, "contribs": None, "best": None, "peak": 0,
        "weeks": [],
        "langs": sorted(lang.items(), key=lambda kv: -kv[1]),
        "sizes": sorted([(n, sz) for (n, _, sz, _) in repos], key=lambda kv: -kv[1])[:6],
        "mass": sum(lang.values()),
        "since": "2024",
    }


def human(n):
    if n is None:
        return "—"
    if n >= 1_000_000:
        return "%.1fM" % (n / 1e6)
    if n >= 10_000:
        return "%.1fk" % (n / 1e3)
    return str(n)


def human_bytes(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return "%.0f %s" % (n, unit) if unit != "B" else "%d B" % n
        n /= 1024.0


def month_labels(weeks):
    """(index, 'mmm') for the first week of each month, deduped."""
    out, seen = [], set()
    for i, wk in enumerate(weeks):
        if not wk:
            continue
        m = dt.date.fromisoformat(wk[0]["date"]).strftime("%b").lower()
        if m not in seen:
            seen.add(m)
            out.append((i, m))
    return out


def head(o, w, title, note):
    o.append('<text x="24" y="30" font-family=%s font-size="17" font-weight="700" fill="%s">'
             '%s</text>' % (F, INK, title))
    o.append('<text x="%d" y="30" text-anchor="end" font-family=%s font-size="11.5" fill="%s">'
             '%s</text>' % (w - 24, F, INK_3, note))


def open_svg(w, h, label):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
            'role="img" aria-label="%s"><rect width="%d" height="%d" rx="16" fill="%s"/>'
            % (w, h, w, h, label, w, h, PAPER))


# --------------------------------------------------------------------------
def build_dashboard(d):
    W, H = 1200, 432
    now = dt.datetime.now(dt.timezone.utc)
    note = ("rebuilt %s" % now.strftime("%d %b %Y").lower()) if d["live"] else "awaiting first sync"
    o = [open_svg(W, H, "GitHub activity summary for %s" % LOGIN)]
    head(o, W, "at a glance", note)

    tiles = [("contributions", human(d["contribs"]), "past year"),
             ("commits", human(d["commits"]), "past year"),
             ("public repos", human(d["repos"]), "and counting"),
             ("longest streak", human(d["best"]), "days")]
    tw, gap = 279, 14
    for i, (lab, val, unit) in enumerate(tiles):
        o.append(ch.stat(20 + i * (tw + gap), 50, tw, lab, val, unit))

    # -- language share: part-to-whole, ordered by size -> sequential ramp --
    o.append(ch.card(20, 168, 460, 244, "what i write in", "share of source"))
    langs = d["langs"][:5]
    total = sum(v for _, v in langs) or 1
    o.append(ch.donut(128, 300, 72, 46,
                      [(n, v) for n, v in langs],
                      total_label=human_bytes(d["mass"])))
    o.append(ch.legend(232, 262,
                       [(n, "%.0f%%" % (100.0 * v / total)) for n, v in langs]))

    # -- cadence: trend over time, one series -----------------------------
    o.append(ch.card(494, 168, 686, 244, "when i actually commit", "weekly, past year"))
    weekly = [sum(x["contributionCount"] for x in wk) for wk in d["weeks"]]
    o.append(ch.area(560, 216, 580, 138, weekly,
                     x_labels=month_labels(d["weeks"])[::2]))
    o.append('</svg>')
    return "".join(o)


def build_activity(d):
    W, H = 1200, 510
    o = [open_svg(W, H, "Contribution calendar and repository sizes for %s" % LOGIN)]
    head(o, W, "the last year, day by day",
         "%d contributions" % d["contribs"] if d["contribs"] else "awaiting first sync")

    o.append(ch.card(20, 46, 1160, 190, "", ""))
    if d["weeks"]:
        gx, gy = 74, 92
        for i, lab in month_labels(d["weeks"]):
            o.append('<text x="%d" y="%d" font-family=%s font-size="10.5" fill="%s">%s</text>'
                     % (gx + i * 14, gy - 8, F, INK_3, lab))
        for wd, lab in ((1, "mon"), (3, "wed"), (5, "fri")):
            o.append('<text x="%d" y="%d" text-anchor="end" font-family=%s font-size="10" '
                     'fill="%s">%s</text>' % (gx - 8, gy + wd * 14 + 9, F, INK_3, lab))
        o.append(ch.heatmap(gx, gy, d["weeks"], d["peak"]))
        o.append(ch.heat_legend(1010, 198))
    else:
        o.append('<text x="74" y="140" font-family=%s font-size="13" fill="%s">the calendar '
                 'fills in on the first scheduled sync</text>' % (F, INK_3))

    o.append(ch.card(20, 252, 1160, 178, "what i’ve been building", "public repos by size"))
    o.append(ch.hbars(50, 306, 1100, d["sizes"], pitch=30, value_fmt=human_bytes))
    o.append('</svg>')
    return "".join(o)


if __name__ == "__main__":
    token = os.environ.get("GITHUB_TOKEN", "")
    data = None
    if token and "--seed" not in sys.argv:
        try:
            data = shape(fetch(token))
        except Exception as exc:                 # noqa: BLE001 - degrade, never fail the job
            print("live fetch failed (%s); using seed" % exc, file=sys.stderr)
    if data is None:
        data = seed()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for name, svg in (("dashboard", build_dashboard(data)), ("activity", build_activity(data))):
        dest = os.path.join(root, "assets", "%s.svg" % name)
        with open(dest, "w", encoding="ascii") as fh:
            fh.write(svg.encode("ascii", "xmlcharrefreplace").decode())
        print("wrote %s (%.1f KB, live=%s)" % (dest, len(svg.encode()) / 1024.0, data["live"]))
