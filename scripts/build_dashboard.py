"""Render assets/calendar.svg from live GitHub data.

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
from palette import ACCENT, INK, INK_2, INK_3, backdrop

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
    repo_rows = sorted(
        [(r["name"],
          r["languages"]["edges"][0]["node"]["name"] if r["languages"]["edges"] else "\u2014",
          sum(e["size"] for e in r["languages"]["edges"]),
          r["stargazerCount"]) for r in repos],
        key=lambda t: -t[2])
    by_month, order = {}, []
    wd_names = ("sun", "mon", "tue", "wed", "thu", "fri", "sat")
    by_wd = [0] * 7
    for d in days:
        key = d["date"][:7]
        if key not in by_month:
            by_month[key] = 0
            order.append(key)
        by_month[key] += d["contributionCount"]
        by_wd[d["weekday"]] += d["contributionCount"]
    months = [(dt.date.fromisoformat(k + "-01").strftime("%b").lower(), by_month[k])
              for k in order][-12:]
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
        "months": months,
        "repo_rows": repo_rows,
        "weekdays": list(zip(wd_names, by_wd)),
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
        "months": [],
        "repo_rows": sorted([(n, l, sz, st) for (n, l, sz, st) in repos],
                            key=lambda t: -t[2]),
        "weekdays": [],
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


# Set once in __main__; read by open_svg so each asset records whether it
# was drawn from live API data or from the offline seed.
DATA_SOURCE = "seed"


def open_svg(w, h, label, seed=0):
    """Open the canvas, lay the ground, declare the mark gradients."""
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
            'role="img" data-source="%s" aria-label="%s">%s%s'
            % (w, h, w, h, DATA_SOURCE, label, backdrop(w, h, seed), ch.bar_defs(seed)))


# --------------------------------------------------------------------------
def build_calendar(d):
    SEED = 4
    """The traditional contribution graph, full width."""
    W, H = 1200, 268
    cell, gap = 13, 4
    o = [open_svg(W, H, "A year of contributions, day by day, for %s" % LOGIN, SEED)]
    head(o, W, "the last year, day by day",
         ("%d contributions" % d["contribs"]) if d["contribs"] else "awaiting first sync")
    o.append(ch.card(16, 48, W - 32, 204, "", "", seed=SEED))
    gx, gy = 96, 96
    if d["weeks"]:
        for i, lab in month_labels(d["weeks"]):
            o.append('<text x="%d" y="%d" font-family=%s font-size="11" fill="%s">%s</text>'
                     % (gx + i * (cell + gap), gy - 10, F, INK_3, lab))
        for wd, lab in ((1, "mon"), (3, "wed"), (5, "fri")):
            o.append('<text x="%d" y="%d" text-anchor="end" font-family=%s font-size="10.5" '
                     'fill="%s">%s</text>' % (gx - 10, gy + wd * (cell + gap) + 11, F, INK_3, lab))
        o.append(ch.heatmap(gx, gy, d["weeks"], d["peak"], cell=cell, gap=gap))
        o.append(ch.heat_legend(W - 190, gy + 7 * (cell + gap) + 12, cell=cell, gap=gap))
    else:
        o.append('<text x="%d" y="%d" font-family=%s font-size="13" fill="%s">the calendar '
                 'fills in on the first scheduled sync</text>' % (gx, gy + 60, F, INK_3))
    o.append("</svg>")
    return "".join(o)


def is_live_on_disk(path):
    """Whether the file already there must be protected from seed output.

    An unstamped file predates the provenance attribute, so its origin
    cannot be read off it. Treat unknown as live: refusing a harmless
    overwrite costs one --force, while allowing a harmful one silently
    destroys a year of committed data. The ambiguity is self-clearing --
    the next live run stamps every asset.
    """
    if not os.path.exists(path):
        return False
    with open(path, encoding="utf-8", errors="replace") as fh:
        head = fh.read(4096)
    if 'data-source="live"' in head:
        return True
    if 'data-source="seed"' in head:
        return False
    return True


def guard(paths, live, force):
    """Refuse to replace live output with seed output.

    This matters in two places. Locally, running with --seed to check a
    layout would otherwise quietly reset committed assets to placeholders,
    and a later `git add -A` would ship that. In CI it matters more: the
    live fetch falls back to the seed on any API error, so a transient
    GraphQL failure would replace a real calendar with an empty one and
    commit it. Failing loudly is the correct outcome there.
    """
    if live or force:
        return
    clobbered = [p for p in paths if is_live_on_disk(p)]
    if clobbered:
        raise SystemExit(
            "refusing to overwrite live data with seed data:\n  "
            + "\n  ".join(clobbered)
            + "\n\nThe existing files were generated from the GitHub API. If the"
              "\nlive fetch failed above, fix that rather than committing seed"
              "\nplaceholders. Pass --force only if replacing them is intended.")


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
    DATA_SOURCE = "live" if data["live"] else "seed"
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    targets = [os.path.join(root, "assets", "calendar.svg")]
    guard(targets, data["live"], "--force" in sys.argv)
    written = []
    for name, svg in (("calendar", build_calendar(data)),):
        dest = os.path.join(root, "assets", "%s.svg" % name)
        with open(dest, "w", encoding="ascii") as fh:
            fh.write(svg.encode("ascii", "xmlcharrefreplace").decode())
        written.append(os.path.relpath(dest, root))
        print("wrote %s (%.1f KB, live=%s)" % (dest, len(svg.encode()) / 1024.0, data["live"]))

    # Record exactly what was written so the workflow stages these and only
    # these. The workflow used to name assets/dashboard.svg by hand, which
    # silently stopped matching when this script grew to four outputs -- the
    # other three were regenerated on every run and then thrown away, so they
    # sat frozen at their seed values in the repo.
    manifest = os.environ.get("ASSET_MANIFEST")
    if manifest:
        with open(manifest, "w", encoding="utf-8") as fh:
            fh.write("\n".join(written) + "\n")
