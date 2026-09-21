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
R_START = "<!-- REPOS:START -->"
R_END = "<!-- REPOS:END -->"
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


def render_kpi(d):
    """The headline figures, as HTML rather than markdown.

    This block is injected into a <td> so it can sit beside the tool
    badges. GitHub does parse markdown inside block-level HTML, but a
    table nested that way is the one construct that cannot be checked
    outside GitHub itself -- and the content is generated either way, so
    emitting HTML costs nothing and removes the doubt entirely. It renders
    with the same styling as the markdown tables around it.
    """
    L = [LIVE_MARK if d["live"] else "<!-- generated: seed -->", ""]
    a = L.append
    a("<table>")
    a('<tr><td colspan="2"><sub><b>past year</b></sub></td></tr>')
    # Only the figure is bold; the unit stays plain, so the column reads as
    # numbers with a suffix rather than four bolded phrases.
    for label, value, unit in (("contributions", num(d["contribs"]), ""),
                               ("commits", num(d["commits"]), ""),
                               ("public repos", num(d["repos"]), ""),
                               ("longest streak", num(d["best"]), " days")):
        a('<tr><td>%s</td><td align="right"><b>%s</b>%s</td></tr>' % (label, value, unit))
    a("</table>")
    return "\n".join(L)


def render_repos(d):
    """Public repositories, widest first. Markdown -- it runs full width."""
    rows = d.get("repo_rows") or []
    if not rows:
        return ""
    top = rows[0][2] or 1
    login = os.environ.get("PROFILE_LOGIN", "BladedGoose13")
    L = ["| repo | language | | size | |", "|---|---|---|--:|--:|"]
    for name, lang, size, stars in rows:
        L.append("| [%s](https://github.com/%s/%s) | %s | `%s` | %s | %s |"
                 % (name, login, name, lang, bar(size, top, 14), human_bytes(size),
                    ("\u2605 %d" % stars) if stars else ""))
    return "\n".join(L)


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


def inject(text, block, start, end, readme, required=True):
    """Replace everything between a marker pair, leaving the rest alone.

    Absent markers mean two different things, so they are treated
    differently. Both gone is an editorial decision -- the repo table was
    cut from the README by hand, and a generator has no business putting
    it back every night -- so an optional block is skipped. Exactly one
    gone is an accident: an edit that swallowed the opening marker and
    left the closing one. That is worth failing on, because silently
    writing nothing would leave a dead marker in the file forever.
    """
    i, j = text.find(start), text.find(end)
    if i == -1 and j == -1:
        if required:
            raise SystemExit("markers %s / %s not found in %s" % (start, end, readme))
        return text
    if i == -1 or j == -1:
        raise SystemExit(
            "half a marker pair in %s: found %s but not %s.\n\nOne of the two was"
            " removed by hand. Restore it to bring the block back,\nor remove the"
            " other one too to drop the block for good."
            % (readme, end if i == -1 else start, start if i == -1 else end))
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
    out = inject(out, render_kpi(data), START, END, readme)
    # Optional: the README currently has no repo table, and re-adding both
    # markers anywhere in it is all it takes to get one back.
    out = inject(out, render_repos(data), R_START, R_END, readme, required=False)
    with open(readme, "w", encoding="utf-8") as fh:
        fh.write(out)
    print("updated README.md stats block (live=%s)" % data["live"])

    manifest = os.environ.get("ASSET_MANIFEST")
    if manifest:                                  # append, so both steps stage
        with open(manifest, "a", encoding="utf-8") as fh:
            fh.write("README.md\n")
