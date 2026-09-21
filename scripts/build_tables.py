"""Render the live stats block inside README.md.

Why this exists: the charts were images, and an image is opaque. A table
written as markdown is real text -- selectable, searchable, diffable,
readable by a screen reader, and it picks up GitHub's own light/dark theme
for free. It is exactly as "live" as the SVG was, because the same
scheduled workflow regenerates it; the liveness was never in the format,
it was in the job.

Bars are drawn with block glyphs inside code spans, so alignment holds in
any proportional theme. This uses no Mermaid and no HTML, only markdown
GitHub has always rendered, so there is no version to guess at.

The block is delimited by markers and everything between them is replaced,
so hand edits elsewhere in the README survive.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_dashboard import fetch, human_bytes, seed, shape

START = "<!-- STATS:START -->"
END = "<!-- STATS:END -->"
LIVE_MARK = "<!-- generated: live -->"
SPARK = "▁▂▃▄▅▆▇█"
FULL, EMPTY_C = "█", "·"


def bar(value, peak, width=22):
    """A proportional bar in block glyphs, padded so every row aligns."""
    if not peak:
        return EMPTY_C * width
    n = max(1, int(round(width * value / float(peak)))) if value else 0
    return FULL * n + EMPTY_C * (width - n)


def num(n):
    return "—" if n is None else "{:,}".format(n)


def render(d):
    """The whole live block: headline figures, then the repositories.

    Deliberately short. The month, weekday and language breakdowns were
    dropped because they said more about the generator than about the work.
    """
    L = []
    a = L.append
    a(LIVE_MARK if d["live"] else "<!-- generated: seed -->")
    a("")
    a("| | past year |")
    a("|---|--:|")
    a("| contributions | **%s** |" % num(d["contribs"]))
    a("| commits | **%s** |" % num(d["commits"]))
    a("| public repos | **%s** |" % num(d["repos"]))
    a("| longest streak | **%s** days |" % num(d["best"]))
    a("")

    rows = d.get("repo_rows") or []
    if rows:
        top = rows[0][2] or 1
        login = os.environ.get("PROFILE_LOGIN", "BladedGoose13")
        a("| repo | language | | size | |")
        a("|---|---|---|--:|--:|")
        for name, lang, size, stars in rows:
            a("| [%s](https://github.com/%s/%s) | %s | `%s` | %s | %s |"
              % (name, login, name, lang, bar(size, top, 14), human_bytes(size),
                 ("\u2605 %d" % stars) if stars else ""))
    return "\n".join(L).rstrip()


def guard_readme(readme, live, force):
    """Refuse to replace a live stats block with seed placeholders.

    Matters most in CI: the live fetch falls back to the seed on any API
    error, so without this a transient failure would quietly commit empty
    figures over real ones. An unstamped block predates the marker, so its
    origin cannot be read off it -- unknown counts as live, because
    refusing a harmless overwrite costs one --force while allowing a
    harmful one destroys committed data.
    """
    if live or force or not os.path.exists(readme):
        return
    with open(readme, encoding="utf-8") as fh:
        body = fh.read()
    stamped_seed = "<!-- generated: seed -->" in body
    if (LIVE_MARK in body) or (START in body and not stamped_seed):
        raise SystemExit(
            "refusing to overwrite the live stats block with seed data in "
            + readme + "\n\nIf the live fetch failed above, fix that rather than "
            "committing\nplaceholders. Pass --force only if replacing it is intended.")


def inject(text, block, start, end, readme):
    i, j = text.find(start), text.find(end)
    if i == -1 or j == -1:
        raise SystemExit("markers %s / %s not found in %s" % (start, end, readme))
    return text[:i + len(start)] + "\n\n" + block + "\n\n" + text[j:]


if __name__ == "__main__":
    token = os.environ.get("GITHUB_TOKEN", "")
    data = None
    if token and "--seed" not in sys.argv:
        try:
            data = shape(fetch(token))
        except Exception as exc:                 # noqa: BLE001 - degrade, never fail
            print("live fetch failed (%s); using seed" % exc, file=sys.stderr)
    if data is None:
        data = seed()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    readme = os.path.join(root, "README.md")
    guard_readme(readme, data["live"], "--force" in sys.argv)
    out = open(readme, encoding="utf-8").read()
    out = inject(out, render(data), START, END, readme)
    with open(readme, "w", encoding="utf-8") as fh:
        fh.write(out)
    print("updated README.md stats block (live=%s)" % data["live"])

    manifest = os.environ.get("ASSET_MANIFEST")
    if manifest:                                  # append, so both steps stage
        with open(manifest, "a", encoding="utf-8") as fh:
            fh.write("README.md\n")
