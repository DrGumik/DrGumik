#!/usr/bin/env python3
"""Generate Coldbit-styled profile stat cards (icy pixel-art) from the GitHub GraphQL API.

Usage:
  pip install fonttools brotli
  GITHUB_TOKEN=... python scripts/stats.py --user DrGumik --out dist
  python scripts/stats.py --demo --out dist      # offline preview with fake data
"""
import argparse, datetime as dt, json, os, random, sys, urllib.request

sys.path.insert(0, os.path.dirname(__file__))
from coldbit import *  # noqa: E402,F403  (tokens + primitives)

HALF = 596  # two cards side by side

QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    pullRequests { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100, privacy: PUBLIC) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      totalPullRequestContributions
      totalPullRequestReviewContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount date } }
      }
    }
  }
}"""


def fetch(user, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": user}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "profile-stats"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(f"GraphQL error: {data['errors']}")
    return data["data"]["user"]


def demo():
    today = dt.date.today()
    start = today - dt.timedelta(days=364)
    weeks, week = [], []
    for i in range(365):
        d = start + dt.timedelta(days=i)
        c = 0 if random.random() < 0.3 else int(random.expovariate(1 / 6))
        week.append({"date": d.isoformat(), "contributionCount": c})
        if len(week) == 7:
            weeks.append({"contributionDays": week}); week = []
    if week:
        weeks.append({"contributionDays": week})
    langs = [("TypeScript", "#3178c6", 600), ("Python", "#3572A5", 220), ("Rust", "#dea584", 120),
             ("JavaScript", "#f1e05a", 80), ("Java", "#b07219", 50), ("Shell", "#89e051", 20)]
    return {
        "followers": {"totalCount": 7}, "pullRequests": {"totalCount": 41},
        "repositories": {"totalCount": 11, "nodes": [{"stargazerCount": 1, "languages": {"edges": [
            {"size": s, "node": {"name": n, "color": c}} for n, c, s in langs]}}]},
        "contributionsCollection": {
            "totalCommitContributions": 1312, "restrictedContributionsCount": 640,
            "totalPullRequestContributions": 38, "totalPullRequestReviewContributions": 12,
            "contributionCalendar": {"totalContributions": 2104, "weeks": weeks}}}


def streaks(days):
    days = sorted(days, key=lambda d: d["date"])
    longest = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] > 0 else 0
        longest = max(longest, run)
    current = 0
    for i, d in enumerate(reversed(days)):
        if d["contributionCount"] > 0:
            current += 1
        elif i == 0:  # today without contributions doesn't break the streak yet
            continue
        else:
            break
    return current, longest


REVEAL = "@keyframes rv{from{opacity:0}to{opacity:1}} .rv{animation:rv .01s steps(1) backwards}"


def fmt(n):
    return f"{n / 1000:.1f}k" if n >= 10000 else f"{n:,}".replace(",", " ")


def stats_card(u):
    cc = u["contributionsCollection"]
    days = [d for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    cur, longest = streaks(days)
    stars = sum(r["stargazerCount"] for r in u["repositories"]["nodes"])
    items = [
        ("contributions/yr", fmt(cc["contributionCalendar"]["totalContributions"]), ICE_LIGHT),
        ("commits/yr", fmt(cc["totalCommitContributions"] + cc["restrictedContributionsCount"]), ICE_LIGHT),
        ("pull requests", fmt(u["pullRequests"]["totalCount"]), ICE_LIGHT),
        ("stars earned", fmt(stars), ICE),
        ("longest streak", f"{longest}d", ICE),
        ("current streak", f"{cur}d", BIT_GLOW if cur else ICE),
    ]
    b = []
    for i, (lab, val, col) in enumerate(items):
        x, y = 30 + (i % 3) * 182, 112 + (i // 3) * 92
        b.append(f'<g class="rv" style="animation-delay:{.15 + i * .12:.2f}s">'
                 + text(x, y, val, 38, col, weight=700)
                 + text(x, y + 26, lab, 14, MUTED) + "</g>")
    if cur:
        b.append(f'<rect x="{HALF - 8 - 40}" y="{192}" width="10" height="10" fill="{BIT_GLOW}" class="blink"/>')
    H = 250
    return svg(HALF, H, window(0, 0, HALF - 8, H - 8, "TELEMETRY.LOG", "\n".join(b), buttons=False),
               BLINK_CSS + REVEAL, "GitHub stats")


def langs_card(u):
    agg = {}
    for r in u["repositories"]["nodes"]:
        for e in r["languages"]["edges"]:
            n = e["node"]["name"]
            agg[n] = agg.get(n, 0) + e["size"]
    top = sorted(agg.items(), key=lambda kv: -kv[1])[:6]
    total = sum(v for _, v in top) or 1
    ramp = [ICE_LIGHT, ICE, ICE_MID, ICE_SHADOW, BIT_GLOW, MUTED]
    # 28 pixel blocks, apportioned by share (largest remainder)
    nblk, bw, gap, bx = 28, 16, 3, 30
    raw = [nblk * v / total for _, v in top]
    alloc = [int(r) for r in raw]
    for i in sorted(range(len(raw)), key=lambda i: -(raw[i] - alloc[i]))[: nblk - sum(alloc)]:
        alloc[i] += 1
    b, k = [], 0
    for li, n in enumerate(alloc):
        for _ in range(n):
            b.append(f'<rect class="rv" style="animation-delay:{k * .04:.2f}s" x="{bx + k * (bw + gap)}" y="64" '
                     f'width="{bw}" height="20" fill="{ramp[li]}"/>')
            k += 1
    for i, (name, v) in enumerate(top):
        x, y = 30 + (i % 2) * 278, 124 + (i // 2) * 36
        b.append(f'<rect x="{x}" y="{y - 13}" width="14" height="14" fill="{ramp[i]}"/>'
                 + text(x + 24, y, name, 16, FG)
                 + text(x + 250, y, f"{100 * v / total:.1f}%", 14, MUTED, anchor="end"))
    H = 250
    return svg(HALF, H, window(0, 0, HALF - 8, H - 8, "LANGUAGES.CFG", "\n".join(b), buttons=False),
               REVEAL, "Top languages in public repositories")


def activity_card(u):
    weeks = u["contributionsCollection"]["contributionCalendar"]["weeks"][-52:]
    vals = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in weeks]
    W, H = 1200, 300
    L, base, top = 34, 238, 84
    n, mx = len(vals), max(vals) or 1
    colw = (W - 8 - 2 * L) / n
    bw, blk, bgap = max(int(colw) - 5, 6), 8, 2
    peak = max(range(n), key=lambda i: vals[i])
    b = [label(L, 70, "Weekly contributions · last 12 months", 16, MUTED),
         text(W - 8 - L, 70, f"updated {dt.date.today().isoformat()}", 13, MUTED, anchor="end"),
         f'<rect x="{L}" y="{base + 3}" width="{W - 8 - 2 * L}" height="3" fill="{BORDER}"/>']
    for i, v in enumerate(vals):
        x = L + i * colw
        nb = 0 if v == 0 else max(1, round((v / mx) * (base - top) / (blk + bgap)))
        g = []
        for j in range(nb):
            y = base - (j + 1) * (blk + bgap) + bgap
            col = BIT_GLOW if i == peak and j == nb - 1 else (ICE_LIGHT if j == nb - 1 else ICE_MID if j > nb / 2 else ICE_SHADOW)
            g.append(f'<rect x="{x:.0f}" y="{y}" width="{bw}" height="{blk}" fill="{col}"/>')
        if g:
            b.append(f'<g class="rv" style="animation-delay:{i * .03:.2f}s">' + "".join(g) + "</g>")
    px = L + peak * colw
    ptop = base - max(1, round((vals[peak] / mx) * (base - top) / (blk + bgap))) * (blk + bgap)
    b.append(text(min(px + bw + 8, W - 200), ptop + 6, f"◂ peak {vals[peak]}/wk", 13, BIT_GLOW, cls="rv", extra='style="animation-delay:1.8s"'))
    last = None
    for i, w in enumerate(weeks):
        m = dt.date.fromisoformat(w["contributionDays"][0]["date"]).strftime("%b").upper()
        if m != last and i < n - 2:
            b.append(text(L + i * colw, base + 26, m, 14, MUTED, font="px", weight=400, spacing=0.12))
            last = m
    return svg(W, H, window(0, 0, W - 8, H - 8, "ACTIVITY.DAT", "\n".join(b)), REVEAL,
               "Weekly contributions over the last 12 months")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default=os.environ.get("GITHUB_REPOSITORY_OWNER", "DrGumik"))
    ap.add_argument("--out", default="dist")
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()
    u = demo() if a.demo else fetch(a.user, os.environ["GITHUB_TOKEN"])
    os.makedirs(a.out, exist_ok=True)
    for name, content in (("stats.svg", stats_card(u)), ("languages.svg", langs_card(u)), ("activity.svg", activity_card(u))):
        with open(os.path.join(a.out, name), "w", encoding="utf-8") as f:
            f.write(content)
    print("written to", a.out)


if __name__ == "__main__":
    main()
