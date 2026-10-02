# -*- coding: utf-8 -*-
# Static figures that sit on a topic page after the step-through and "Say this".
# FIGS[topic_id] = html

INK = "#2B2B30"; GRAY = "#6B6B76"; FRAME = "#9A9AA6"
EXF, EXS = "#E2EFE3", "#A8CBAC"          # execution units (green, as on the classic slide)
REGF, REGS = "#C9DCF3", "#8FB0DA"        # registers  — closest, darkest blue
SHF, SHS = "#DCE8F7", "#A9C4E4"          # shared memory
L2F, L2S = "#F1F4F9", "#B9C6D8"          # L2 — hardware-managed, dashed
GLF, GLS = "#E3ECF8", "#A9C4E4"          # global memory (HBM)


def _t(x, y, s, cls="mt", anchor="middle", extra=""):
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}"{extra}>{s}</text>'


def _rect(x, y, w, h, f, s, rx=6, sw=1.2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{f}" stroke="{s}" stroke-width="{sw}"{d}/>'


def memhier_svg():
    o = []
    o.append('<defs><marker id="mh-arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
             'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#8B8B95"/></marker>'
             f'<marker id="mh-th" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" '
             f'orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker></defs>')

    # column headers
    o.append(_t(24, 26, "EXECUTION", "mcap", "start"))
    o.append(_t(220, 26, "MEMORY", "mcap", "start"))
    o.append(_t(826, 26, "hover any level to see what it owns", "mhint", "end"))

    # ---------------- left column: thread / thread block / grid
    # thread
    o.append('<g class="kx k-t">'
             f'<path d="M110,82 L110,118" stroke="{INK}" stroke-width="1.8" marker-end="url(#mh-th)"/>'
             + _t(110, 140, "thread", "mb")
             + _t(110, 155, "one instruction stream", "ms") + '</g>')
    # thread block: green box with 8 arrows (8 warps)
    arrows = "".join(
        f'<path d="M{66 + i * 12.6:.1f},183 L{66 + i * 12.6:.1f},199" stroke="{INK}" stroke-width="1.3" marker-end="url(#mh-th)"/>'
        for i in range(8))
    o.append('<g class="kx k-b">' + _rect(56, 178, 108, 28, EXF, EXS, 4) + arrows
             + _t(110, 226, "thread block", "mb")
             + _t(110, 241, "e.g. 256 threads = 8 warps", "ms") + '</g>')
    # grid: frame with 2x2 blocks
    gb = ""
    for (bx, by, lab) in [(63, 297, "block 0"), (113, 297, "block 1"), (63, 320, "block 2"), (113, 320, "block 3")]:
        gb += _rect(bx, by, 45, 19, EXF, EXS, 3, 1) + _t(bx + 22.5, by + 13, lab, "mxs")
    o.append('<g class="kx k-g">' + _rect(56, 290, 108, 56, "#fff", FRAME, 5, 1.1) + gb
             + _t(110, 366, "grid", "mb")
             + _t(110, 381, "every block of one launch", "ms") + '</g>')

    # connectors: who owns what
    def conn(x1, y1, x2, y2, key):
        return (f'<path class="kx {key}" d="M{x1},{y1} L{x2},{y2}" stroke="#8B8B95" stroke-width="1.3" '
                f'stroke-dasharray="4 3" fill="none" marker-end="url(#mh-arr)"/>')

    # ---------------- right: block 0 expanded
    o.append(f'<g class="kx">{_rect(220, 40, 394, 200, "#fff", FRAME, 8, 1.3)}'
             + _t(236, 60, "block 0", "mb", "start")
             + _t(598, 60, "placed on one SM — and stays there", "ms", "end") + '</g>')
    for (tx, lab) in [(236, "thread 0"), (352, "thread 1"), (496, "thread 255")]:
        o.append(f'<g class="kx k-t">{_rect(tx, 70, 104, 100, "#fff", FRAME, 6, 1.1)}'
                 + _t(tx + 52, 90, lab, "mt")
                 + _rect(tx + 10, 102, 84, 56, REGF, REGS, 5, 1.2)
                 + _t(tx + 52, 126, "registers", "mb")
                 + _t(tx + 52, 143, "private", "ms") + '</g>')
    o.append('<g class="kx">' + _t(478, 124, "…", "mdots") + '</g>')
    o.append(f'<g class="kx k-b">{_rect(236, 184, 364, 42, SHF, SHS, 6, 1.2)}'
             + _t(418, 201, "shared memory", "mb")
             + _t(418, 217, "seen by all 256 threads of block 0 · its slice of the SM’s 228 KB", "ms") + '</g>')

    # ---------------- right: collapsed blocks
    for (bx, lab) in [(630, "block 1"), (742, "block N")]:
        cx = bx + 42
        o.append(f'<g class="kx">{_rect(bx, 40, 84, 200, "#fff", FRAME, 8, 1.3)}'
                 + _t(cx, 60, lab, "mb")
                 + _rect(bx + 10, 70, 64, 100, "#fff", "#C9C9D1", 5, 1, "3 3")
                 + _t(cx, 116, "256", "ms") + _t(cx, 130, "threads", "ms") + '</g>')
        o.append(f'<g class="kx k-b">{_rect(bx + 10, 184, 64, 42, SHF, SHS, 6, 1.2)}'
                 + _t(cx, 201, "shared", "mt") + _t(cx, 217, "its own", "ms") + '</g>')
    o.append('<g class="kx">' + _t(728, 144, "…", "mdots") + '</g>')

    # ---------------- right: L2 and global memory
    o.append(f'<g class="kx k-g">{_rect(220, 254, 606, 34, L2F, L2S, 6, 1.2, "5 3")}'
             + _t(523, 275, "<tspan class=\"mb\">L2 cache</tspan>  ·  126 MB  ·  shared by all 148 SMs  ·  managed by hardware, never addressed directly", "mt")
             + '</g>')
    o.append(f'<g class="kx k-g">{_rect(220, 298, 606, 56, GLF, GLS, 7, 1.3)}'
             + _t(523, 321, "global memory  ·  HBM3e", "mb")
             + _t(523, 340, "up to 180 GB at ~8 TB/s  ·  every thread of every block can read and write it  ·  outlives the kernel", "ms")
             + '</g>')
    # connectors last, so they draw over the block frame
    o.append(conn(176, 116, 244, 128, "k-t"))
    o.append(conn(176, 196, 234, 203, "k-b"))
    o.append(conn(176, 318, 218, 324, "k-g"))
    return "".join(o)


MEMHIER_CSS = """
.figsec{margin:0 0 26px}
.figcard{border:1px solid var(--rule);border-radius:13px;background:#FCFCFD;overflow:hidden}
.figcard .fighead{padding:12px 16px 10px;border-bottom:1px solid var(--rule);background:var(--card)}
.figcard .fighead b{font-size:13.5px;display:block}
.figcard .fighead span{font-size:10.5px;color:var(--ink3);font-family:"IBM Plex Mono",ui-monospace,monospace}
.figstage{padding:12px 14px 8px}
.figstage svg{width:100%;height:auto;display:block}
.figcap{margin:2px 16px 14px;font-size:13.5px;line-height:1.55;color:var(--ink2);max-width:80ch}
.figcap b{color:var(--ink)}
.memfig text{font-family:"Source Sans 3",-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
.memfig .mt{font-size:12px;fill:#2B2B30}
.memfig .mb{font-size:12.5px;fill:#1D1D22;font-weight:650}
.memfig .ms{font-size:10.5px;fill:#5E5E68}
.memfig .mxs{font-size:9px;fill:#3D5A45}
.memfig .mcap{font-size:10px;fill:#8B8B95;letter-spacing:.09em;font-weight:600;font-family:"IBM Plex Mono",ui-monospace,monospace}
.memfig .mhint{font-size:10.5px;fill:#8B8B95;font-style:italic}
.memfig .mdots{font-size:20px;fill:#8B8B95}
.memfig .kx{transition:opacity .2s ease}
.memfig:has(.k-t:hover) .kx:not(.k-t),
.memfig:has(.k-b:hover) .kx:not(.k-b),
.memfig:has(.k-g:hover) .kx:not(.k-g){opacity:.16}
.mtwrap{overflow-x:auto;margin-top:14px;border:1px solid var(--rule);border-radius:11px}
.mtab{border-collapse:collapse;width:100%;min-width:640px;font-size:13.5px;line-height:1.45}
.mtab th{text-align:left;font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:10px;font-weight:600;
  letter-spacing:.06em;text-transform:uppercase;color:var(--ink3);background:#FAFAFB;padding:9px 12px;
  border-bottom:1px solid var(--rule)}
.mtab td{padding:9px 12px;border-bottom:1px solid var(--rule);vertical-align:top}
.mtab tr:last-child td{border-bottom:0}
.mtab td:first-child{font-weight:600;white-space:nowrap}
.mtab td:first-child i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:7px;
  vertical-align:-1px;border:1px solid}
.mtab .gotcha{color:#9A6B12}
.figsrc{font-size:11.5px;color:var(--ink3);margin:8px 2px 0}
.figsrc a{color:var(--ink2)}
@media (max-width:900px){.figstage{overflow-x:auto}.memfig{min-width:760px}}
"""


def _sw(f, s):
    return f'<i style="background:{f};border-color:{s}"></i>'


MEMHIER_TABLE = (
    '<div class="mtwrap"><table class="mtab"><thead><tr>'
    '<th>Memory</th><th>Who can see it</th><th>Lives as long as</th><th>On a B200</th><th>Rough cost</th>'
    '</tr></thead><tbody>'
    f'<tr><td>{_sw(REGF, REGS)}Registers</td><td>one thread</td><td>the thread</td>'
    '<td>64K × 32-bit per SM (256 KB), at most 255 per thread</td><td>fastest — read directly as instruction operands</td></tr>'
    f'<tr><td>{_sw("#fff", FRAME)}Local memory</td><td>one thread</td><td>the thread</td>'
    '<td>register spills and large per-thread arrays, physically in global memory</td>'
    '<td class="gotcha">as slow as global (cached in L1/L2) — “local” means private, not close</td></tr>'
    f'<tr><td>{_sw(SHF, SHS)}Shared memory</td><td>every thread in one block</td><td>the block</td>'
    '<td>228 KB per SM, up to 227 KB for one block; shares a 256 KB pool with L1</td><td>on-chip, tens of cycles</td></tr>'
    f'<tr><td>{_sw(L2F, L2S)}L2 cache</td><td>every SM on the GPU</td><td>managed by hardware</td>'
    '<td>126 MB</td><td>a few hundred cycles (~150 ns measured)</td></tr>'
    f'<tr><td>{_sw(GLF, GLS)}Global memory (HBM3e)</td><td>every thread of every block, and the host via copies</td>'
    '<td>until freed — survives across kernel launches</td><td>up to 180 GB, ~8 TB/s</td>'
    '<td>the slowest — what every optimisation tries to touch less</td></tr>'
    '</tbody></table></div>'
    '<p class="figsrc">Sizes from NVIDIA’s <a href="https://docs.nvidia.com/cuda/blackwell-tuning-guide" target="_blank" rel="noopener">Blackwell Tuning Guide</a> '
    '(compute capability 10.0) and the DGX B200 datasheet; L2 latency from '
    '<a href="https://chipsandcheese.com/p/nvidias-b200-keeping-the-cuda-juggernaut" target="_blank" rel="noopener">Chips and Cheese’s B200 measurements</a>. '
    'Cycle counts are orders of magnitude, not specs.</p>'
)

FIGS = {
    "b200-hardware":
        '<div class="figsec"><h2 class="sec">The memory hierarchy, in one picture</h2>'
        '<div class="figcard"><div class="fighead"><b>Who owns which memory</b>'
        '<span>the classic thread · block · grid diagram, with B200 numbers on it</span></div>'
        '<div class="figstage"><svg class="memfig" viewBox="0 0 850 392" xmlns="http://www.w3.org/2000/svg" '
        'role="img" aria-label="GPU memory hierarchy: each thread owns registers, each thread block owns a slice of shared memory on one SM, and every block in the grid shares L2 and global HBM memory.">'
        + memhier_svg() + '</svg></div>'
        '<p class="figcap">Read it as <b>ownership</b>: a thread owns its registers, a block owns its slice of shared memory, '
        'and the whole grid shares L2 and global memory. Each step down is <b>slower, larger, and visible to more threads</b> — '
        'which is why fast kernels stage data from global memory into shared memory once and reuse it from there. '
        'Block 0 cannot see block 1’s shared memory: ordinarily blocks only meet in global memory '
        '(thread block clusters are the exception — see “Going deeper”).</p></div>'
        + MEMHIER_TABLE + '</div>',
}
FIG_CSS = MEMHIER_CSS
