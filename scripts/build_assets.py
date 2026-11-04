#!/usr/bin/env python3
"""Render the static profile SVGs into assets/ in the Coldbit pixel style.

  pip install fonttools brotli
  python scripts/build_assets.py
"""
import os, random

from coldbit import *  # noqa: F403  (tokens + primitives)

OUT = os.path.join(os.path.dirname(__file__), "..", "assets")
W = 1200          # every full-width asset
WIN = W - 8       # window width (8 px hard shadow)
random.seed(2018)


def write(name, content):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  {name:<22} {len(content.encode()) / 1024:6.1f} kB")


def reveal_css(name="rv", dur=".01s"):
    # content stays visible if animations never run (backwards fill only during the delay)
    return f"@keyframes {name}{{from{{opacity:0}}to{{opacity:1}}}} .{name}{{animation:{name} {dur} steps(1) backwards}}"


# ── hero ─────────────────────────────────────────────────────────────────────
def hero():
    H = 440
    body_top, body_bot = 33, H - 8
    b = []
    b.append(f'<clipPath id="body"><rect x="3" y="{body_top}" width="{WIN - 6}" height="{body_bot - body_top - 3}"/></clipPath>')
    b.append('<g clip-path="url(#body)">')
    b.append(grid_dots(0, body_top, WIN, body_bot - body_top))
    # stepped pixel snow
    for _ in range(34):
        x = random.randrange(8, WIN - 8, 4)
        s = random.choice((4, 4, 4, 6, 8))
        d = random.uniform(7, 13)
        col = random.choice((ICE_LIGHT, ICE, BIT_GLOW, ICE_MID))
        b.append(f'<rect class="flake" x="{x}" y="{body_top - 10}" width="{s}" height="{s}" fill="{col}" opacity=".55" '
                 f'style="animation:fall {d:.1f}s steps(24) {-random.uniform(0, d):.1f}s infinite"/>')
    b.append("</g>")

    # left column
    b.append(label(56, 104, "Developer · est. 2018"))
    nm = "JAKUB TENK"
    b.append(text(64, 204, nm, 88, ICE_SHADOW, font="px", weight=700))
    b.append(text(56, 196, nm, 88, ICE_LIGHT, font="px", weight=700))
    b.append(text(56, 252, "AI-first software engineer · finance & ERP automation", 21, FG))
    b.append(text(56, 286, "@DrGumik · coldbit.cz · ailin.cz", 18, MUTED))

    # prompt box with stepped typewriter (SMIL, discrete)
    bx, by, bw, bh = 56, 310, 664, 60
    b.append(f'<rect x="{bx + 5}" y="{by + 5}" width="{bw}" height="{bh}" fill="{ICE_SHADOW}"/>')
    b.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="{BACKGROUND}"/>')
    b.append(f'<rect x="{bx + 1.5}" y="{by + 1.5}" width="{bw - 3}" height="{bh - 3}" fill="none" stroke="{BORDER}" stroke-width="3"/>')
    b.append(text(bx + 20, by + 38, "❯", 20, ICE))
    msgs = ["designing systems — AI agents write the code",
            "building Ailin.cz: AI accounting over Abra Flexi",
            "migrating ledgers, wiring integrations",
            "running Proxmox clusters, keeping backups boring"]
    cw, tx, T, slot, typing, hold = 12.0, bx + 46, 16.0, 4.0, 1.6, 3.5
    cur_t, cur_x = [0.0], [tx]
    for i, m in enumerate(msgs):
        n = len(m)
        times, widths = [0.0], [0.0]
        t0 = i * slot
        for k in range(1, n + 1):
            times.append(t0 + typing * k / n); widths.append(k * cw)
            cur_t.append(t0 + typing * k / n); cur_x.append(tx + k * cw)
        times.append(t0 + hold); widths.append(0.0)
        cur_t.append(t0 + hold); cur_x.append(tx)
        kt = ";".join(f"{t / T:.4f}" for t in times)
        vals = ";".join(f"{w:g}" for w in widths)
        init = n * cw if i == 0 else 0
        b.append(f'<clipPath id="m{i}"><rect x="{tx}" y="{by + 10}" height="{bh - 20}" width="{init:g}">'
                 f'<animate attributeName="width" dur="{T}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{kt}" values="{vals}"/>'
                 f'</rect></clipPath>')
        b.append(text(tx, by + 38, m, 20, FG, extra=f'clip-path="url(#m{i})"'))
    pairs = sorted(zip(cur_t, cur_x))
    kt = ";".join(f"{t / T:.4f}" for t, _ in pairs)
    vals = ";".join(f"{x:g}" for _, x in pairs)
    b.append(f'<rect x="{tx}" y="{by + 20}" width="11" height="22" fill="{ICE}" class="blink">'
             f'<animate attributeName="x" dur="{T}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{kt}" values="{vals}"/></rect>')

    # right: player HUD
    hx, hy, hw, hh = 776, 70, 364, 330
    rows = [("CLASS", "ARCHITECT"), ("GUILD", "COLDBIT"), ("QUEST", "AILIN.CZ"), ("SINCE", "2018"), ("STATUS", "TOKEN BURNING")]
    hud = []
    for i, (k, v) in enumerate(rows):
        y = hy + 86 + i * 40
        hud.append(text(hx + 22, y, k, 16, MUTED, font="px", weight=400, spacing=0.18))
        hud.append(text(hx + 130, y + 1, v, 22, ICE_LIGHT if i < 4 else ICE, font="px", weight=400, spacing=0.06))
    hud.append(f'<rect x="{hx + hw - 36}" y="{hy + 86 + 4 * 40 - 15}" width="12" height="12" fill="{BIT_GLOW}" class="blink"/>')
    ey = hy + hh - 52
    hud.append(text(hx + 22, ey + 15, "EXP", 16, MUTED, font="px", weight=400, spacing=0.18))
    sx, segs, sw, gap = hx + 80, 12, 18, 3
    full = segs * (sw + gap) - gap
    vals = ";".join(str(k * (sw + gap)) for k in range(segs + 1)) + f";{full}"
    hud.append(f'<rect x="{sx}" y="{ey}" width="{full}" height="18" fill="{BACKGROUND}"/>')
    hud.append(f'<rect x="{sx}" y="{ey}" width="{(segs - 3) * (sw + gap)}" height="18" fill="{ICE}">'
               f'<animate attributeName="width" dur="5s" repeatCount="indefinite" calcMode="discrete" values="{vals}"/></rect>')
    for k in range(1, segs):
        hud.append(f'<rect x="{sx + k * (sw + gap) - gap}" y="{ey}" width="{gap}" height="18" fill="{PANEL_HIGH}"/>')
    b.append(window(hx, hy, hw, hh, "PLAYER_1.SAV", "\n".join(hud), high=True, shadow=6, bar=34))

    css = (BLINK_CSS + f" @keyframes fall{{to{{transform:translateY({H}px)}}}}")
    return svg(W, H, window(0, 0, WIN, H - 8, "COLDBIT.EXE — @DRGUMIK", "\n".join(b)), css,
               "Jakub Tenk — AI-first software engineer, finance & ERP automation")


# ── about ────────────────────────────────────────────────────────────────────
def about():
    def sp(s, c):
        return f'<tspan fill="{c}">{esc(s)}</tspan>'
    K, ID, KEY, STR, NUM, CM, P = ICE, FG, ICE_LIGHT, ICE_MID, BIT_GLOW, MUTED, MUTED

    def kv(k, v, comment=None, num=False):
        pad = " " * (10 - len(k))
        val = sp(v, NUM) if num else sp(f'"{v}"', STR)
        return sp(k, KEY) + sp(":" + pad, P) + val + sp(",", P) + (sp("  // " + comment, CM) if comment else "")

    lines = [
        (0, sp("❯ ", ICE) + sp("cat about.ts", FG)),
        (0, sp("const ", K) + sp("jakub", ID) + sp(" = {", P)),
        (1, kv("role", "Head of Development & ICT @ Virtual CV Lead")),
        (1, kv("freelance", "Coldbit — custom software, automation, AI training")),
        (1, kv("building", "Ailin.cz — multi-tenant AI accounting SaaS")),
        (1, sp("domain", KEY) + sp(":    [", P) + sp('"finance"', STR) + sp(", ", P) + sp('"accounting"', STR) + sp(", ", P) + sp('"ERP / Abra Flexi"', STR) + sp("],", P)),
        (1, kv("workflow", "I architect & review — AI agents write the code")),
        (1, kv("coding", "2018", "writing code & running servers since", num=True)),
        (1, kv("based", "Czechia (CET)")),
        (0, sp("} ", P) + sp("satisfies ", K) + sp("Developer", ID) + sp(";", P)),
        (0, sp("❯ ", ICE)),
    ]
    H = 86 + 32 * len(lines) + 10
    b = []
    for i, (ind, l) in enumerate(lines):
        y = 92 + i * 32
        b.append(f'<text x="{36 + ind * 44}" y="{y}" class="mono rv" font-size="20" font-weight="400" '
                 f'style="animation-delay:{0.2 + i * 0.22:.2f}s">{l}</text>')
    last = 92 + (len(lines) - 1) * 32
    b.append(f'<rect x="{36 + 2 * 12:.1f}" y="{last - 18}" width="12" height="24" fill="{ICE}" class="blink"/>')
    return svg(W, H, window(0, 0, WIN, H - 8, "ABOUT.TS — ~/drgumik", "\n".join(b)), BLINK_CSS + reveal_css(),
               "about.ts — Jakub Tenk")


# ── quest log ────────────────────────────────────────────────────────────────
QUESTS = [
    ("2018", "HELLO, WORLD", "First lines of code while studying automation systems."),
    ("2019", "GAME SERVERS", "Founded PvPWorld (Minecraft) & 24KRolePlay (FiveM): team of 10+, custom anti-cheat."),
    ("2022", "COLDBIT", "Went self-employed: custom software, automation, networking. Software engineering at FAV ZČU."),
    ("2023", "DYPE", "DevOps & IT admin: integration platform, accounting automation."),
    ("2025", "VIRTUAL CV LEAD", "Head of Development & ICT: server cluster, network, backups."),
    ("2025", "AILIN.CZ", "Started building an AI accounting SaaS on top of Abra Flexi."),
    ("2026", "SHIPPED", "Ailin runs in production. Klára, an AI coach, won best semester project at FAV ZČU."),
]


def quest_log():
    top, step = 96, 72
    H = top + step * len(QUESTS) + 4
    b = []
    tx = 150
    for y in range(top - 6, top + step * (len(QUESTS) - 1), 12):
        b.append(f'<rect x="{tx + 5}" y="{y}" width="6" height="6" fill="{BORDER}"/>')
    for i, (yr, title, desc) in enumerate(QUESTS):
        y = top + i * step
        now = i == len(QUESTS) - 1
        g = [text(56, y + 7, yr, 22, ICE_LIGHT if now else ICE, weight=700),
             f'<rect x="{tx + 3}" y="{y - 3}" width="16" height="16" fill="{ICE_SHADOW}"/>',
             f'<rect x="{tx}" y="{y - 6}" width="16" height="16" fill="{BIT_GLOW if now else ICE}"' + (' class="blink"/>' if now else "/>"),
             text(190, y + 7, title, 22, FG, font="px", weight=400, spacing=0.08),
             text(190, y + 34, desc, 16, MUTED)]
        if now:
            g.append(label(190 + text_width(title, 22, "px400", 0.08) + 16, y + 6, "now", 15, ICE))
        else:
            g.append(text(190 + text_width(title, 22, "px400", 0.08) + 16, y + 6, "✓", 18, ICE_SHADOW, weight=700))
        b.append(f'<g class="rv" style="animation-delay:{0.25 + i * 0.3:.2f}s">' + "".join(g) + "</g>")
    return svg(W, H, window(0, 0, WIN, H - 8, "QUEST_LOG.TXT — since 2018", "\n".join(b)), BLINK_CSS + reveal_css(),
               "Quest log: milestones since 2018")


def wrap(s, width, size, key="mono400"):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_width(t, size, key) > width and cur:
            lines.append(cur); cur = w
        else:
            cur = t
    return lines + [cur]


# ── workflow ─────────────────────────────────────────────────────────────────
ICONS = {
    "arch": ["...xx...", "..xxxx..", ".xxxxxx.", "xxxxxxxx", ".x.xx.x.", ".x.xx.x.", ".x.xx.x.", "xxxxxxxx"],
    "data": [".xxxxxx.", "x......x", ".xxxxxx.", "x......x", ".xxxxxx.", "x......x", "x......x", ".xxxxxx."],
    "bot": ["...xx...", "...xx...", "xxxxxxxx", "x......x", "x.x..x.x", "x......x", "x.xxxx.x", "xxxxxxxx"],
    "shield": ["xxxxxxxx", "x......x", "x.....xx", "x....x.x", "xx..x..x", ".xxx..x.", "..x..x..", "...xx..."],
}


def workflow():
    H = 340
    nodes = [(170, "01", "arch", "ARCHITECTURE", "systems, boundaries\n& trade-offs"),
             (455, "02", "data", "DATA MODEL & SPECS", "schemas, contracts\n& edge cases"),
             (740, "03", "bot", "AI AGENTS BUILD", "Claude Code, Codex\n& Antigravity"),
             (1025, "04", "shield", "REVIEW & HARDEN", "code review, tests\n& security")]
    b = [label(40, 78, "How I ship · human-in-the-loop, agent-powered", 17, MUTED)]
    ny, ns = 124, 64
    cy = ny + ns // 2
    for x in range(nodes[0][0] + 44, nodes[-1][0] - 40, 14):
        b.append(f'<rect x="{x}" y="{cy - 3}" width="6" height="6" fill="{BORDER}"/>')
    span = nodes[-1][0] - nodes[0][0] - 84
    for d in (0, 2):
        b.append(f'<rect x="{nodes[0][0] + 42}" y="{cy - 5}" width="10" height="10" fill="{BIT_GLOW}" '
                 f'style="animation:pkt 4s steps(36) {-d}s infinite"/>')
    for i, (x, num, icon, title, desc) in enumerate(nodes):
        b.append(f'<rect x="{x - ns // 2 + 6}" y="{ny + 6}" width="{ns}" height="{ns}" fill="{ICE_SHADOW}"/>')
        b.append(f'<rect x="{x - ns // 2}" y="{ny}" width="{ns}" height="{ns}" fill="{PANEL_HIGH}"/>')
        b.append(f'<rect x="{x - ns // 2 + 1.5}" y="{ny + 1.5}" width="{ns - 3}" height="{ns - 3}" fill="none" stroke="{ICE}" stroke-width="3" class="pulse" style="animation-delay:{i * .5}s"/>')
        b.append(pixels(ICONS[icon], x - 20, ny + 12, 5, {"x": ICE_LIGHT}))
        b.append(text(x, ny - 14, num, 16, ICE, font="px", weight=400, anchor="middle", spacing=0.18))
        b.append(text(x, ny + ns + 44, title, 20, FG, font="px", weight=400, anchor="middle", spacing=0.08))
        for j, l in enumerate(desc.split("\n")):
            b.append(text(x, ny + ns + 70 + j * 22, l, 15, MUTED, anchor="middle"))
    css = (f"@keyframes pkt{{to{{transform:translateX({span}px)}}}}"
           f" @keyframes pulse{{50%{{stroke:{ICE_SHADOW}}}}} .pulse{{animation:pulse 2s steps(1) infinite}}")
    return svg(W, H, window(0, 0, WIN, H - 8, "HOW_I_SHIP.SH", "\n".join(b)), css,
               "How I ship: architecture, data model & specs, AI agents build, review & harden")


# ── project cards ────────────────────────────────────────────────────────────
def card(name, title, kicker, desc, tags, link, w, flagship=False):
    inner = w - 8
    pad = 28
    lines = wrap(desc, inner - 2 * pad, 16 if flagship else 15)
    ny = 124 if flagship else 112
    dy = ny + 38
    lh = 26 if flagship else 24
    chip_y = dy + lh * (len(lines) - 1) + 22
    ch, end = chips(pad, chip_y, tags, inner - 2 * pad)
    H = end + 28 + 8
    b = []
    if flagship:
        s, cwid = chip(pad, 56, "IN PRODUCTION", 14, solid=True)
        b.append(s)
        b.append(label(pad + cwid + 16, 77, kicker, 16, MUTED))
    else:
        b.append(label(pad, 74, kicker, 16, MUTED))
    fs = 44 if flagship else 33
    b.append(text(pad + fs // 11, ny + fs // 11, name, fs, ICE_SHADOW, font="px", weight=400))
    b.append(text(pad, ny, name, fs, ICE_LIGHT, font="px", weight=400))
    for i, l in enumerate(lines):
        b.append(text(pad, dy + i * lh, l, 16 if flagship else 15, FG))
    b.append(ch)
    b.append(text(inner - pad, 77 if flagship else 74, link + " ↗", 15, ICE, anchor="end"))
    return svg(w, H, window(0, 0, inner, H - 8, title, "\n".join(b), high=flagship, buttons=flagship), "",
               f"{name} — {desc}")


def projects():
    write("card-ailin.svg", card(
        "Ailin.cz", "AILIN.CZ — FLAGSHIP", "AI accounting SaaS",
        "Multi-tenant AI accounting on top of Abra Flexi: invoicing, cashflow, CRM, projects and a built-in mail client. "
        "Vision-LLM document extraction (ISDOC-aware), automatic payment matching, workflow rules and export to Flexi, "
        "with guard hooks that keep production accounting data safe. Architected by me, implemented by AI agents.",
        ["Next.js 16", "React 19", "TypeScript", "PostgreSQL", "Prisma", "OpenRouter", "Abra Flexi API"],
        "ailin.cz", W, flagship=True))
    small = 392
    write("card-coldbit.svg", card("Coldbit", "COLDBIT.CZ", "Freelance",
          "Custom software, automation, Abra Flexi migrations, MCP servers and AI training.",
          ["TypeScript", "Python", "MCP"], "coldbit.cz", small))
    write("card-rtk.svg", card("rtk", "RTK — FORK", "Rust · CLI",
          "CLI proxy that cuts LLM token usage by 60–90 % on common dev commands. Windows port.",
          ["Rust", "CLI", "LLM"], "repo", small))
    write("card-tex.svg", card("tex-compiler", "TEX-COMPILER", "Open source",
          "All-in-one online LaTeX editor & compiler that runs in the browser.",
          ["TypeScript", "LaTeX"], "repo", small))


# ── inventory (tech stack as a 9-slot hotbar grid) ───────────────────────────
ITEMS = [("TS", "TypeScript"), ("NX", "Next.js"), ("RE", "React"), ("ND", "Node.js"), ("PY", "Python"),
         ("RS", "Rust"), ("PG", "PostgreSQL"), ("PR", "Prisma"), ("DK", "Docker"),
         ("LX", "Linux"), ("PM", "Proxmox"), ("TL", "Tailscale"), ("AF", "Abra Flexi"), ("MC", "MCP"),
         ("CC", "Claude Code"), ("CX", "Codex"), ("AG", "Antigravity"), ("GT", "Git")]


def inventory():
    cols, slot, gap = 9, 112, 12
    gx = (WIN - (cols * slot + (cols - 1) * gap)) // 2
    gy = 100
    rows = (len(ITEMS) + cols - 1) // cols
    H = gy + rows * (slot + gap) + 24
    b = [label(gx, 78, f"Inventory · {len(ITEMS)} items", 17, MUTED)]
    ramp = (ICE_LIGHT, ICE, ICE_MID)
    for i, (mono, name) in enumerate(ITEMS):
        x, y = gx + (i % cols) * (slot + gap), gy + (i // cols) * (slot + gap)
        b.append(f'<rect x="{x}" y="{y}" width="{slot}" height="{slot}" fill="{BACKGROUND}"/>'
                 f'<rect x="{x}" y="{y}" width="{slot}" height="4" fill="{BORDER}"/><rect x="{x}" y="{y}" width="4" height="{slot}" fill="{BORDER}"/>'
                 f'<rect x="{x}" y="{y + slot - 4}" width="{slot}" height="4" fill="{PANEL_HIGH}"/><rect x="{x + slot - 4}" y="{y}" width="4" height="{slot}" fill="{PANEL_HIGH}"/>')
        b.append(text(x + slot / 2, y + 63, mono, 44, ramp[i % 3], font="px", weight=400, anchor="middle"))
        b.append(text(x + slot / 2, y + 92, name, 14 if len(name) < 11 else 12, MUTED, anchor="middle"))
    # moving selection frame (stepped, discrete)
    pos = [(gx + (i % cols) * (slot + gap) - 6, gy + (i // cols) * (slot + gap) - 6) for i in range(len(ITEMS))]
    vals = ";".join(f"{x} {y}" for x, y in pos)
    b.append(f'<g><animateTransform attributeName="transform" type="translate" dur="{len(ITEMS) * 0.8}s" '
             f'repeatCount="indefinite" calcMode="discrete" values="{vals}"/>'
             f'<rect x="1.5" y="1.5" width="{slot + 9}" height="{slot + 9}" fill="none" stroke="{BIT_GLOW}" stroke-width="3"/></g>')
    return svg(W, H, window(0, 0, WIN, H - 8, "INVENTORY.DAT", "\n".join(b)), "", "Tech stack inventory")


# ── link buttons ─────────────────────────────────────────────────────────────
def button(s):
    tw = text_width(s, 18, "px400", 0.16)
    w, h = int(tw + 44), 44
    body = (f'<rect x="5" y="5" width="{w}" height="{h}" fill="{ICE_SHADOW}"/>'
            f'<rect x="0" y="0" width="{w}" height="{h}" fill="{ICE}"/>'
            f'<rect x="0" y="0" width="{w}" height="4" fill="{ICE_LIGHT}"/>'
            + text(22, 29, s, 18, ON_ICE, font="px", weight=400, spacing=0.16))
    return svg(w + 5, h + 5, body, "", s)


# ── footer ───────────────────────────────────────────────────────────────────
def footer():
    H = 120
    b = []
    for i, x in enumerate(range(0, W, 24)):
        hgt = random.choice((16, 16, 24, 24, 32, 40))
        b.append(f'<rect x="{x}" y="{H - hgt}" width="24" height="{hgt}" fill="{ICE_SHADOW}"/>')
        b.append(f'<rect x="{x}" y="{H - hgt}" width="24" height="6" fill="{ICE_LIGHT}"/>')
        if i % 5 == 2:
            b.append(f'<rect x="{x + 8}" y="{H - hgt - 18}" width="6" height="6" fill="{BIT_GLOW}" class="tw" style="animation-delay:{(i % 7) * .3:.1f}s"/>')
    s = "[ EOF ]  COLDBIT · EST. 2018"
    tw = text_width(s, 19, "px400", 0.18)
    b.append(text(W / 2 - tw / 2, 40, s, 19, MUTED, font="px", weight=400, spacing=0.18))
    b.append(f'<rect x="{W / 2 + tw / 2 + 6:.0f}" y="25" width="12" height="18" fill="{ICE}" class="blink"/>')
    css = BLINK_CSS + " @keyframes tw{50%{opacity:.15}} .tw{animation:tw 1.4s steps(1) infinite}"
    return svg(W, H, "\n".join(b), css, "EOF — Coldbit, est. 2018")


if __name__ == "__main__":
    write("hero.svg", hero())
    write("about.svg", about())
    write("quest-log.svg", quest_log())
    write("workflow.svg", workflow())
    projects()
    write("inventory.svg", inventory())
    write("btn-coldbit.svg", button("COLDBIT.CZ"))
    write("btn-ailin.svg", button("AILIN.CZ"))
    write("btn-x.svg", button("X · @DRGUMIK"))
    write("footer.svg", footer())
