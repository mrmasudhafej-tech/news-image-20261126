#!/usr/bin/env python3
"""Deterministic newspaper front page for Thursday 26 November 2026.

Pure standard library: the picture is rasterised into an RGB buffer with a
hand-authored 5x7 bitmap font and encoded as PNG with zlib. No network, no
files read, no randomness, no time or environment dependence in the bytes
(the output directory alone comes from MAKEFUN_OUTPUT_DIR). Two runs
therefore write byte-identical output.
"""

import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (247, 241, 227)
INK = (22, 22, 22)
RED = (163, 22, 33)
NAVY = (27, 42, 74)
GREY = (92, 92, 88)
LIGHT = (255, 255, 255)

# ---------------------------------------------------------------- font ----
# Each glyph: 7 rows of 5 pixels, "#" = on. All copy is set in capitals,
# the newspaper style used throughout this page.
_G = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11100", "10010", "10001", "10001", "10001", "10010", "11100"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "•": ("00000", "00100", "01110", "01110", "01110", "00100", "00000"),
}
_G["’"] = _G["'"]
_G["—"] = _G["-"]
_G["–"] = _G["-"]

CW, CH = 5, 7


def text_width(text, scale):
    return sum((CW + 1) * scale for _ in text) - scale


def draw_text(buf, x, y, text, scale, color, bold=False):
    """Draw upper-cased text; returns the pixel width drawn."""
    cx = x
    for ch in text.upper():
        glyph = _G.get(ch, _G[" "])
        for row in range(CH):
            bits = glyph[row]
            for col in range(CW):
                if bits[col] == "1":
                    fill_rect(buf, cx + col * scale, y + row * scale,
                              scale, scale, color)
                    if bold:
                        fill_rect(buf, cx + col * scale + 1,
                                  y + row * scale, scale, scale, color)
        cx += (CW + 1) * scale
    return cx - x - scale


def draw_centred(buf, cx, y, text, scale, color, bold=False):
    w = text_width(text, scale)
    draw_text(buf, cx - w // 2, y, text, scale, color, bold=bold)
    return w


def wrap(text, max_w, scale):
    """Greedy word wrap returning a list of lines fitting max_w pixels."""
    words = text.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(buf, x, y, text, scale, color, max_w, leading, bold=False):
    yy = y
    for line in wrap(text, max_w, scale):
        draw_text(buf, x, yy, line, scale, color, bold=bold)
        yy += leading
    return yy


# ------------------------------------------------------------ raster ----

def new_canvas():
    return bytearray(PAPER * W * H)


def set_px(buf, x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i], buf[i + 1], buf[i + 2] = color


def fill_rect(buf, x, y, w, h, color):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    for yy in range(y0, y1):
        i = (yy * W + x0) * 3
        for xx in range(x0, x1):
            buf[i], buf[i + 1], buf[i + 2] = color
            i += 3


def hline(buf, x, y, w, color, thick=1):
    fill_rect(buf, x, y, w, thick, color)


def vline(buf, x, y, h, color, thick=1):
    fill_rect(buf, x, y, thick, h, color)


def line(buf, x0, y0, x1, y1, color, thick=1):
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    x, y = x0, y0
    while True:
        fill_rect(buf, x, y, thick, thick, color)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy


def fill_circle(buf, cx, cy, r, color):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                set_px(buf, xx, yy, color)


def fill_ellipse(buf, cx, cy, rx, ry, color):
    for yy in range(cy - ry, cy + ry + 1):
        for xx in range(cx - rx, cx + rx + 1):
            if ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1.0:
                set_px(buf, xx, yy, color)


def fill_poly(buf, pts, color):
    """Scanline polygon fill; pts are (x, y) in order."""
    ys = [p[1] for p in pts]
    for yy in range(min(ys), max(ys) + 1):
        xs = []
        n = len(pts)
        for i in range(n):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % n]
            if (y0 <= yy < y1) or (y1 <= yy < y0):
                xs.append(x0 + (yy - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            for xx in range(int(xs[i]), int(xs[i + 1]) + 1):
                set_px(buf, xx, yy, color)


def encode_png(buf):
    raw = bytearray()
    stride = W * 3
    for yy in range(H):
        raw.append(0)
        raw += buf[yy * stride:(yy + 1) * stride]
    data = zlib.compress(bytes(raw), 9)

    def chunk(kind, payload):
        c = struct.pack(">I", len(payload)) + kind + payload
        return c + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", data)
    png += chunk(b"IEND", b"")
    return png


# -------------------------------------------------------- pictures ----

def draw_storm(buf, x, y, w, h):
    """Nor'easter over a city skyline; a parade balloon droops, deflated."""
    bands = [(18, 30, 58), (30, 46, 78), (48, 66, 96), (66, 84, 112)]
    bh = h // len(bands)
    for i, col in enumerate(bands):
        fill_rect(buf, x, y + i * bh, w, bh + 1, col)
    for cx, cy, rx, ry in ((x + 130, y + 34, 120, 22), (x + 250, y + 24, 90, 18),
                           (x + 620, y + 42, 150, 24), (x + 800, y + 28, 100, 20),
                           (x + 470, y + 48, 110, 20)):
        fill_ellipse(buf, cx, cy, rx, ry, (120, 132, 150))
        fill_ellipse(buf, cx, cy + 7, rx - 20, ry - 5, (96, 110, 128))
    for i in range(40):
        rx = x + 12 + (i * 53) % (w - 24)
        ry = y + 8 + (i * 37) % (h - 60)
        line(buf, rx, ry, rx - 9, ry + 18, (168, 186, 205), 2)
    heights = (86, 64, 100, 54, 78, 96, 58, 90, 70, 98, 56, 82)
    bx = x + 8
    bw = (w - 16) // len(heights)
    for i, hh in enumerate(heights):
        top = y + h - 40 - hh
        fill_rect(buf, bx + i * bw, top, bw - 6, hh + 40, (12, 18, 32))
        for wy in range(top + 12, y + h - 46, 24):
            for wx in range(bx + i * bw + 6, bx + (i + 1) * bw - 10, 16):
                if (wx + wy) % 3 == 0:
                    fill_rect(buf, wx, wy, 5, 6, (240, 196, 90))
    # Deflated balloon: sagging, seams showing, basket hanging below.
    bcx, bcy = x + 290, y + 58
    fill_ellipse(buf, bcx, bcy, 96, 38, (178, 34, 48))
    fill_ellipse(buf, bcx, bcy - 10, 76, 28, (198, 58, 70))
    fill_ellipse(buf, bcx - 44, bcy + 14, 36, 14, (150, 24, 40))
    vline(buf, bcx - 34, bcy - 34, 66, (140, 22, 36), 2)
    vline(buf, bcx + 34, bcy - 34, 66, (140, 22, 36), 2)
    line(buf, bcx - 58, bcy + 30, bcx - 80, bcy + 62, (230, 230, 230), 2)
    line(buf, bcx + 58, bcy + 30, bcx + 82, bcy + 62, (230, 230, 230), 2)
    line(buf, bcx, bcy + 36, bcx, bcy + 62, (230, 230, 230), 2)
    fill_rect(buf, bcx - 22, bcy + 62, 44, 16, (90, 60, 30))
    fill_rect(buf, x, y + h - 12, w, 12, (10, 14, 24))


def draw_fire(buf, x, y, w, h):
    """Tall flames behind a tanker silhouette on a dark road."""
    fill_rect(buf, x, y, w, h, (28, 20, 18))
    base = y + h - 30
    flame_w = w
    for pts, col in (
        ([(x + 8, base), (x + 40, y + 8), (x + 78, y + 34), (x + 118, y + 4),
          (x + 158, y + 36), (x + 200, y + 8), (x + 244, y + 34), (x + 288, y + 10),
          (x + 330, y + 36), (x + 372, y + 14), (x + 408, y + 38),
          (x + 436, base)], (196, 38, 20)),
        ([(x + 44, base), (x + 70, y + 30), (x + 106, y + 48), (x + 142, y + 24),
          (x + 184, y + 50), (x + 224, y + 28), (x + 264, y + 50), (x + 308, y + 28),
          (x + 348, y + 50), (x + 384, y + 30), (x + 404, base)], (238, 116, 22)),
        ([(x + 92, base), (x + 112, y + 48), (x + 148, y + 62), (x + 186, y + 42),
          (x + 226, y + 64), (x + 264, y + 44), (x + 302, y + 62),
          (x + 330, base)], (248, 196, 60)),
    ):
        # Scale the wide flame sketch onto this panel's width.
        scaled = [(x + (px - x) * flame_w // 460, py) for px, py in pts]
        fill_poly(buf, scaled, col)
    # Tanker: low silhouette across the bottom of the flames.
    ty = base - 18
    fill_rect(buf, x + 24, ty, 250, 18, (168, 168, 164))
    fill_rect(buf, x + 24, ty, 250, 4, (120, 120, 116))
    fill_rect(buf, x + 276, ty + 4, 48, 14, (140, 40, 30))
    fill_rect(buf, x + 282, ty + 6, 16, 8, (180, 210, 230))
    for wx in (x + 60, x + 126, x + 192, x + 252, x + 300):
        fill_circle(buf, wx, base - 1, 8, (16, 16, 16))
        fill_circle(buf, wx, base - 1, 3, (110, 110, 110))
    fill_rect(buf, x, base + 8, w, 5, (200, 190, 60))
    fill_rect(buf, x, base + 14, w, h - (base + 14 - y), (20, 20, 20))


def draw_rock(buf, x, y, r, body, crater):
    fill_circle(buf, x, y, r, body)
    fill_ellipse(buf, x - r // 3, y - r // 4, r // 2, r // 3, crater)
    fill_ellipse(buf, x + r // 2, y + r // 3, r // 4, r // 5, crater)
    fill_circle(buf, x + r // 4, y - r // 2, 4, crater)
    for dx, dy in ((-r, -r // 2), (r + 8, r // 2), (-r - 6, r // 2)):
        fill_circle(buf, x + dx, y + dy, 4, body)


# ------------------------------------------------------------- page ----

def rule(buf, x, y, w, color, thick=3):
    hline(buf, x, y, w, color, thick)


def story(buf, x, y, kicker_text, head, text, col_w, pic=None, pic_h=0):
    """One column story; returns the y below it. pic draws at head+body gap."""
    draw_text(buf, x, y, kicker_text, 2, RED, bold=True)
    y += 22
    draw_text(buf, x, y, head, 3, INK, bold=True)
    y += 30
    if pic is not None:
        pic(buf, x, y, col_w, pic_h)
        y += pic_h + 6
    y = draw_para(buf, x, y, text, 2, INK, col_w, 20)
    return y


def build():
    buf = new_canvas()
    mx = 28
    cw_total = W - 2 * mx

    # Masthead: title, then date and subtitle on separate, spaced lines.
    rule(buf, mx, 16, cw_total, INK, 6)
    draw_centred(buf, W // 2, 26, "THE WORLD TODAY", 7, INK, bold=True)
    rule(buf, mx, 86, cw_total, INK, 2)
    draw_centred(buf, W // 2, 94, "THURSDAY 26 NOVEMBER 2026", 3, RED)
    draw_centred(buf, W // 2, 120,
                 "THE DAY'S NEWS FROM AROUND THE WORLD, IN ONE PAGE", 2, INK)
    rule(buf, mx, 140, cw_total, INK, 6)

    # Lead headline and deck.
    y = 150
    y = draw_para(buf, mx, y, "STORM GROUNDS THE", 6, INK, cw_total, 46,
                  bold=True)
    y = draw_para(buf, mx, y, "THANKSGIVING PARADE", 6, INK, cw_total, 46,
                  bold=True)
    y += 4
    y = draw_para(buf, mx, y,
                  "New York's 100th Macy's parade moves to Saturday, its "
                  "first postponement ever, as a nor'easter brings gusts of "
                  "up to 65 mph and coastal flooding to the East Coast.",
                  2, INK, cw_total, 21)
    y += 6
    # Lead picture with caption strip.
    pic_h = 150
    draw_storm(buf, mx, y, cw_total, pic_h)
    cap_y = y + pic_h
    fill_rect(buf, mx, cap_y, cw_total, 24, INK)
    draw_text(buf, mx + 10, cap_y + 5,
              "BALLOONS DEFLATED IN NEW YORK AS THE STORM CLOSED IN.", 2,
              LIGHT)
    y = cap_y + 32

    # Middle columns: two stories each, single-line heads, measured ends.
    rule(buf, mx, y, cw_total, INK, 2)
    y += 10
    mid_top = y
    gutter = 24
    col_w = (cw_total - gutter) // 2
    lx, rx = mx, mx + col_w + gutter
    vline(buf, mx + col_w + gutter // 2, mid_top, 360, GREY, 1)

    left_end = story(
        buf, lx, mid_top, "NORTH KOREA", "KIM URGES NUCLEAR BUILD-UP",
        "Kim Jong Un urged tactical nuclear weapons to be deployed across "
        "more domains, state media KCNA reported, and said nuclear-material "
        "output was expanding.", col_w)
    left_end += 8
    rule(buf, lx, left_end, col_w, GREY, 1)
    left_end = story(
        buf, lx, left_end + 12, "UKRAINE WAR", "UKRAINE HITS 5 WARPLANES",
        "Ukraine said it struck the Savasleyka airbase east of Moscow, "
        "damaging three MiG-31 jets and two Su-34 bombers. Libya said two "
        "naval officers died of wounds from a Ukrainian drone attack on a "
        "Russian warship there.", col_w)

    right_end = story(
        buf, rx, mid_top, "EGYPT", "CAIRO TANKER FIRE KILLS 31",
        "At least 31 people were killed and 21 injured when a fuel tanker "
        "overturned and burst into flames on Cairo's Ring Road in Warraq. "
        "The toll is preliminary.", col_w,
        pic=draw_fire, pic_h=68)
    right_end += 8
    rule(buf, rx, right_end, col_w, GREY, 1)
    right_end = story(
        buf, rx, right_end + 12, "TRADE", "US TARIFFS HIT 14 PARTNERS",
        "Washington proposed new tariffs on 14 partners, including China "
        "and the EU, after a probe into excess factory capacity. China "
        "faces 20%.",
        col_w)

    # Bottom strip: three briefs, heads in red, placed below the columns.
    y = max(left_end, right_end) + 12
    rule(buf, mx, y, cw_total, INK, 2)
    y += 10
    box_w = (cw_total - 2 * gutter) // 3
    briefs = [
        ("KOREA RATE TO 3.25%",
         "Bank of Korea lifts its rate, resuming tightening."),
        ("13 DEAD IN MINE SEARCH",
         "Rescuers seek 13 trapped in an illegal gold mine in West Java; "
         "13 dead."),
        ("ASTEROID CRATER SEEN",
         "ESA's Hera sees Dimorphos flattened by a stadium-sized crater."),
    ]
    for i, (head, txt) in enumerate(briefs):
        bx = mx + i * (box_w + gutter)
        draw_text(buf, bx, y, head, 2, RED, bold=True)
        draw_para(buf, bx, y + 20, txt, 2, INK, box_w, 20)
        if i < 2:
            vline(buf, bx + box_w + gutter // 2, y, 72, GREY, 1)
    y += 84

    # Footer: sources line, clear of the briefs.
    rule(buf, mx, y + 6, cw_total, INK, 2)
    draw_centred(buf, W // 2, y + 14,
                 "REPORTED 26 NOVEMBER 2026 - SOURCES: REUTERS, AP, BBC, "
                 "AL JAZEERA, ESA", 2, INK)
    return buf


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    png = encode_png(build())
    with open(os.path.join(out_dir, "entry.png"), "wb") as fh:
        fh.write(png)


if __name__ == "__main__":
    main()
