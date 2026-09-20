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
SPARK = "▁▂▃▄▅▆▇█"
FULL, EMPTY_C = "█", "·"


def bar(value, peak, width=22):
    """A proportional bar in block glyphs, padded so every row aligns."""
    if not peak:
        return EMPTY_C * width
    n = max(1, int(round(width * value / float(peak)))) if value else 0
    return FULL * n + EMPTY_C * (width - n)


def spark(values):
    if not values:
        return ""
    mx = max(values) or 1
    return "".join(SPARK[min(len(SPARK) - 1, int(v / mx * (len(SPARK) - 1) + 0.5))]
                   for v in values)


def num(n):
    return "—" if n is None else "{:,}".format(n)


def render(d):
    L = []
    a = L.append

    a("| | past year |")
    a("|---|--:|")
    a("| contributions | **%s** |" % num(d["contribs"]))
    a("| commits | **%s** |" % num(d["commits"]))
    a("| public repos | **%s** |" % num(d["repos"]))
    a("| longest streak | **%s** days |" % num(d["best"]))
    a("")

    if d["months"]:
        a("**by month** &nbsp; `%s` &nbsp; peak **%d**"
          % (spark([v for _, v in d["months"]]), max(v for _, v in d["months"])))
        a("")

    if d["weekdays"]:
        peak = max(v for _, v in d["weekdays"]) or 1
        a("| day | | |")
        a("|---|---|--:|")
        for name, v in d["weekdays"]:
            a("| %s | `%s` | %d |" % (name, bar(v, peak), v))
        a("")

    langs = d["langs"][:5]
    total = sum(v for _, v in langs) or 1
    if langs:
        a("| language | | share |")
        a("|---|---|--:|")
        for name, v in langs:
            a("| %s | `%s` | %.0f%% |" % (name, bar(v, langs[0][1]), 100.0 * v / total))
        a("")
        a("<sub>%s of source across %s public repos</sub>"
          % (human_bytes(d["mass"]), num(d["repos"])))
        a("")

    if d["sizes"]:
        top = d["sizes"][0][1] or 1
        a("| repo | | size |")
        a("|---|---|--:|")
        for name, v in d["sizes"][:6]:
            a("| [%s](https://github.com/%s/%s) | `%s` | %s |"
              % (name, os.environ.get("PROFILE_LOGIN", "BladedGoose13"), name,
                 bar(v, top), human_bytes(v)))
    return "\n".join(L).rstrip()


def inject(readme, block):
    s = open(readme, encoding="utf-8").read()
    i, j = s.find(START), s.find(END)
    if i == -1 or j == -1:
        raise SystemExit("markers %s / %s not found in %s" % (START, END, readme))
    return s[:i + len(START)] + "\n\n" + block + "\n\n" + s[j:]


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
    out = inject(readme, render(data))
    with open(readme, "w", encoding="utf-8") as fh:
        fh.write(out)
    print("updated README.md stats block (live=%s)" % data["live"])

    manifest = os.environ.get("ASSET_MANIFEST")
    if manifest:                                  # append, so both steps stage
        with open(manifest, "a", encoding="utf-8") as fh:
            fh.write("README.md\n")
