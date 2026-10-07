#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_rak_piring.py
Gambar kerja RAK PIRING & GELAS box 600 x 800 x 450 mm.

PRINSIP RANCANGAN (v5 - final):
  * Piring disimpan BERDIRI, menghadap ke depan, dan BERSANDAR ke dinding belakang
    (seperti pigura bersandar di dinding) -> stabil, tidak bisa menggelinding.
  * Alas/bibir bawah piring masuk ke ALUR SISIR di permukaan papan rak
    (alur 12 x 8 mm, panjang 44 mm, jarak 25 mm) -> piring tidak bisa bergeser samping.
  * Sudut sandar muncul otomatis 10-17 derajat tergantung diameter piring.
  * 4 ukuran piring, 4 buah tiap ukuran = 16 piring; piring kecil di tepi, besar di tengah.
  * Kompartemen bawah 300 mm + lantai depan kompartemen atas -> untuk gelas/cangkir/mangkuk.
Output: SVG (vektor) + PNG di folder ./gambar
"""
import math, os
from dwg_canvas import (Canvas, View, C_LINE, C_THIN, C_DIM, C_TXT, C_WOOD, C_WOOD2, C_EDGE,
                        C_BACK, C_PLATE, C_PLATE2, C_GLASS, C_GLASS2, C_ACCENT)

# ======================================================================
# 1. ANGGARAN UKURAN
# ======================================================================
W, H, D, T = 600.0, 800.0, 450.0, 18.0
Z_BOT, Z_SHELF, Z_SH, Z_TOP = 18.0, 318.0, 336.0, 782.0
Z_LOW, Z_UP = Z_SHELF - Z_BOT, Z_TOP - Z_SH            # 300 ; 446
WALL = 18.0                                            # muka dalam dinding belakang
# alur sisir pada papan rak
SLOT_W, SLOT_D, SLOT_Y0, SLOT_Y1 = 12.0, 8.0, 38.0, 82.0
SLOT_C = (SLOT_Y0 + SLOT_Y1) / 2                       # 60 (pusat tapak piring)
SLOT_FLOOR = Z_SH - SLOT_D                             # 328
PITCH = 25.0
X0P = 112.5
PIRING_X = [X0P + PITCH * k for k in range(16)]
PIRING_D = [147, 147, 191, 191, 208, 208, 235, 235, 235, 235, 208, 208, 191, 191, 147, 147]
PIRING = [235, 208, 191, 147]                          # urutan ukuran (besar -> kecil)
KET = {235: "piring makan besar", 208: "piring makan", 191: "piring sedang", 147: "piring kecil / tatak"}
# pembatas (sekat visual) - di depan alur, tidak mengganggu piring
BATAS_X = [(150.0, 168.0), (291.0, 309.0), (432.0, 450.0)]
BATAS_Y0, BATAS_Y1 = 88.0, 172.0
LIP_Y0, LIP_Y1, LIP_H = 430.0, 450.0, 20.0
GLASS_D, GLASS_H = 70.0, 100.0
PAPER, PPM = (420.0, 297.0), 5.2


def fmt(v, dec=1):
    if abs(v - round(v)) < 0.05:
        return str(int(round(v)))
    return f"{v:.{dec}f}".replace(".", ",")


def lean_of(dia):
    """(sudut sandar derajat, tinggi puncak) untuk piring diameter dia"""
    sn = (SLOT_C - WALL) / dia
    th = math.degrees(math.asin(sn))
    return th, SLOT_FLOOR + dia * math.cos(math.radians(th))


# ======================================================================
# 2. PRIMITIF GAMBAR TEKNIK
# ======================================================================
def arrow(c, x, y, ang, L=2.6, Wd=1.0, col=C_DIM):
    a = math.radians(ang); ca, sa = math.cos(a), math.sin(a)
    c.poly([(x, y), (x - L * ca + Wd * sa, y - L * sa - Wd * ca),
            (x - L * ca - Wd * sa, y - L * sa + Wd * ca)], fill=col)


def dim_h(c, x0, x1, y, text=None, size=2.4, ext0=None, ext1=None, col=C_DIM, shift=None, dash_mid=False):
    if abs(x1 - x0) < 0.15:
        return
    if ext0 is not None:
        c.line((x0, ext0), (x0, y + 1.3), stroke=col, sw=0.16)
    if ext1 is not None:
        c.line((x1, ext1), (x1, y + 1.3), stroke=col, sw=0.16)
    c.line((x0, y), (x1, y), stroke=col, sw=0.2)
    arrow(c, x0, y, 180); arrow(c, x1, y, 0)
    if text is None:
        text = fmt(abs(x1 - x0))
    ty = y - 1.4
    if shift:
        c.line(((x0 + x1) / 2, y - 0.3), ((x0 + x1) / 2, shift + 0.6), stroke=col, sw=0.16)
        ty = shift
    c.text((x0 + x1) / 2, ty, text, size=size, anchor="mm", color=col, bg="white")


def dim_v(c, y0, y1, x, text=None, size=2.4, ext0=None, col=C_DIM, left=True, force=True):
    if abs(y1 - y0) < 0.15:
        return
    if ext0 is not None:
        c.line((ext0, y0), (x + (-1.3 if left else 1.3), y0), stroke=col, sw=0.16)
        c.line((ext0, y1), (x + (-1.3 if left else 1.3), y1), stroke=col, sw=0.16)
    c.line((x, y0), (x, y1), stroke=col, sw=0.2)
    arrow(c, x, y0, 270); arrow(c, x, y1, 90)
    if not text:
        text = fmt(abs(y1 - y0))
    c.text(x - 1.5 if left else x + 1.5, (y0 + y1) / 2, text, size=size,
           anchor="rm" if left else "lm", color=col, bg="white")


def leader(c, x0, y0, x1, y1, text, size=2.4, anchor="lm", col=C_TXT, sw=0.18):
    c.line((x0, y0), (x1, y1), stroke=col, sw=sw)
    c.circle(x0, y0, 0.5, fill=col)
    dx = 1.0 if anchor[0] == "l" else (-1.0 if anchor[0] == "r" else 0)
    c.text(x1 + dx, y1, text, size=size, anchor=anchor, color=col, bg="white")


def table(c, x, y, colw, rows, size=2.5, row_h=5.0, header_bg="#e8eef4", pad=1.3, aligns=None):
    n = len(rows); tw = sum(colw)
    c.rect(x, y, x + tw, y + row_h * n, fill="white", stroke=C_LINE, sw=0.25)
    for i in range(1, n):
        c.line((x, y + row_h * i), (x + tw, y + row_h * i), stroke="#c9c9c9", sw=0.18)
    cx = x
    for wc in colw[:-1]:
        cx += wc
        c.line((cx, y), (cx, y + row_h * n), stroke="#c9c9c9", sw=0.18)
    c.rect(x, y, x + tw, y + row_h, fill=header_bg, stroke=None)
    c.rect(x, y, x + tw, y + row_h, fill=None, stroke=C_LINE, sw=0.25)
    for r, row in enumerate(rows):
        cx = x
        for i, cell in enumerate(row):
            al = (aligns[i] if aligns else (["lm"] + ["mm"] * (len(row) - 2) + ["rm"])[i])
            px = {"lm": cx + pad, "mm": cx + colw[i] / 2, "rm": cx + colw[i] - pad}[al]
            c.text(px, y + row_h * (r + 0.5), str(cell), size=size, anchor=al,
                   bold=(r == 0), color=C_TXT)
            cx += colw[i]
    return y + row_h * n


def title_block(c, x0, y0, x1, y1, judul, sub, skala, lembar, ket="Satuan: mm"):
    c.rect(x0, y0, x1, y1, fill="white", stroke=C_LINE, sw=0.6)
    c.line((x0, y0 + 13), (x1, y0 + 13), stroke=C_LINE, sw=0.35)
    c.line((x0, y0 + 20.5), (x1, y0 + 20.5), stroke="#c9c9c9", sw=0.2)
    c.line((x0, y0 + 27.5), (x1, y0 + 27.5), stroke="#c9c9c9", sw=0.2)
    c.line((x0 + 96, y0), (x0 + 96, y1), stroke="#c9c9c9", sw=0.2)
    c.text(x0 + 3, y0 + 6.5, judul, size=5.4, anchor="lm", bold=True)
    c.text(x0 + 3, y0 + 16.6, sub, size=2.9, anchor="lm")
    c.text(x0 + 3, y0 + 24, ket, size=2.4, anchor="lm", color="#555")
    c.text(x0 + 99, y0 + 6.5, f"SKALA {skala}", size=3.0, anchor="lm", bold=True)
    c.text(x0 + 99, y0 + 16.6, f"TANGGAL  {lembar[0]}", size=2.5, anchor="lm")
    c.text(x0 + 99, y0 + 24, f"LEMBAR  {lembar[1]}", size=2.5, anchor="lm")


def notes_block(c, x, y, title, items, size=2.4, lh=3.8):
    c.text(x, y, title, size=3.2, anchor="lm", bold=True)
    yy = y + 4.8
    for it in items:
        c.text(x + 1.2, yy, "•", size=size, anchor="lm", color=C_ACCENT)
        c.text(x + 3.4, yy, it, size=size, anchor="lm")
        yy += lh
    return yy


def frame(c, judul, sub):
    c.rect(6, 6, PAPER[0] - 6, PAPER[1] - 6, fill=None, stroke=C_LINE, sw=0.7)
    c.rect(8.5, 8.5, PAPER[0] - 8.5, PAPER[1] - 8.5, fill=None, stroke=C_LINE, sw=0.25)
    c.text(14, 15.5, judul, size=5.6, anchor="lm", bold=True)
    c.text(14, 21.0, sub, size=2.7, anchor="lm", color="#444")
    c.line((14, 24.0), (PAPER[0] - 14, 24.0), stroke=C_LINE, sw=0.35)


def glass_front(c, V, xc, z0, dia=GLASS_D, h=GLASS_H, solid=True, fill=C_GLASS, zbase=None):
    db = dia * 0.7
    zb = z0 if zbase is None else zbase
    pts = [(xc - db / 2, zb), (xc + db / 2, zb), (xc + dia / 2, zb + h), (xc - dia / 2, zb + h)]
    stroke = C_GLASS2 if solid else "#a9bcc4"
    V.P(pts, fill=fill if solid else None, stroke=stroke, sw=0.2, dash=None if solid else (2.6, 1.8))
    if solid:
        V.L(xc - dia / 2, zb + h, xc + dia / 2, zb + h, stroke=stroke, sw=0.32)
        V.L(xc - dia * 0.4, zb + h * 0.7, xc + dia * 0.4, zb + h * 0.7, stroke=stroke, sw=0.15)


def bowl_front(c, V, xc, z0, dia, h, stack=2):
    for k in range(stack):
        z = z0 + k * h * 0.5
        pts = [(xc - dia / 2 * (1 - 0.1 * k), z + h * 0.22),
               (xc - dia / 2 * 0.6 * (1 - 0.1 * k), z),
               (xc + dia / 2 * 0.6 * (1 - 0.1 * k), z),
               (xc + dia / 2 * (1 - 0.1 * k), z + h * 0.22),
               (xc + dia / 2 * 0.76 * (1 - 0.1 * k), z + h * 0.72),
               (xc - dia / 2 * 0.76 * (1 - 0.1 * k), z + h * 0.72)]
        V.P(pts, fill="#f1efe9", stroke="#b6b3aa", sw=0.18)


# ======================================================================
# 3. TAMPAK DEPAN  (piring terlihat sebagai lingkaran - menghadap depan)
# ======================================================================
def draw_front(c, ox, oy, s, dims=True, labels=True):
    V = View(c, (ox, oy), s, 'front')
    # dinding belakang zona piring
    V.R(WALL, Z_SH, 582, Z_TOP, fill=C_BACK, stroke=None)
    # papan
    V.R(0, 0, 600, Z_BOT, fill=C_WOOD2, stroke=C_LINE, sw=0.35)
    V.R(0, Z_TOP, 600, H, fill=C_WOOD2, stroke=C_LINE, sw=0.35)
    V.R(18, Z_SHELF, 582, Z_SH, fill=C_WOOD, stroke=C_LINE, sw=0.35)
    for x0 in (0, 582):
        V.R(x0, 0, x0 + 18, H, fill=C_EDGE, stroke=C_LINE, sw=0.35)
    # pembatas (sekat visual) - di depan piring
    for (b0, b1) in BATAS_X:
        V.R(b0, Z_SH, b1, Z_TOP, fill=C_WOOD, stroke=C_LINE, sw=0.3)
    # piring (lingkaran, digambar dari kiri ke kanan)
    for x, dia in sorted(zip(PIRING_X, PIRING_D), key=lambda t: -t[1]):
        R = dia / 2
        zc = SLOT_FLOOR + R * math.cos(math.radians(lean_of(dia)[0]))
        p = V(x, zc)
        c.circle(p[0], p[1], V.ln(R), fill="#f4f8fb", stroke="#a9c2d3", sw=0.4)
    # lis depan
    V.R(18, Z_SH, 582, Z_SH + LIP_H, fill=C_WOOD, stroke=C_LINE, sw=0.3)
    V.R(18, Z_BOT, 582, Z_BOT + LIP_H, fill=C_WOOD, stroke=C_LINE, sw=0.3)
    # gelas pada kompartemen bawah + mangkuk
    for xc in (75, 150, 225):
        glass_front(c, V, xc, 0, zbase=Z_BOT + LIP_H)
    for xc in (345, 435, 525):
        bowl_front(c, V, xc, Z_BOT + LIP_H + 14, 92, 54, stack=2)
    # gelas pada lantai depan kompartemen atas (di depan piring)
    for xc in (215, 320, 425, 525):
        glass_front(c, V, xc, 0, zbase=Z_SH + LIP_H, fill="#e4f2f7")

    if labels:
        for gx, gt, zz in [(125.0, "ø147", 752), (225.0, "ø208", 752), (375.0, "ø208", 752),
                           (475.0, "ø147", 752), (175.0, "ø191", 730), (300.0, "ø235", 730),
                           (425.0, "ø191", 730)]:
            V.T(gx, zz, gt, size=2.5, anchor="mm", bold=True, color=C_ACCENT)
        V.T(300, 700, "tiap ukuran 4 buah  —  total 16 piring", size=2.2, anchor="mm", color="#777")
        V.T(150, 238, "gelas / cangkir", size=2.4, anchor="mm", color="#3d6b7d")
        V.T(430, 238, "mangkuk", size=2.4, anchor="mm", color="#7a7a72")
        V.T(300, 262, "kompartemen bawah tinggi 300 mm  —  gelas ø70 × 100 (2 baris)", size=2.3,
            anchor="mm", color="#666")
        leader(c, *V(60, 200), *V(20, 150), "", size=2)
        leader(c, *V(560, 400), *V(628, 430), "lis depan 20 mm", size=2.3, anchor="rm")
        leader(c, *V(444.5, 600), *V(628, 660), "pembatas 18 mm", size=2.3, anchor="rm")
        leader(c, *V(50, 340), *V(628, 330), "papan rak + alur sisir 16 buah", size=2.3, anchor="rm")
        c.text(*V(300, 950 - 800), "", size=2)

    if dims:
        p = lambda x, z: V(x, z)
        ytop = oy - V.ln(H) - 7.0
        xs = [0, 18, 150, 168, 291, 309, 432, 450, 582, 600]
        for i in range(len(xs) - 1):
            a, b = p(xs[i], 0)[0], p(xs[i + 1], 0)[0]
            if b - a < 5.0:
                dim_h(c, a, b, ytop, fmt(xs[i + 1] - xs[i]), size=2.0,
                      ext0=oy - V.ln(H) - 1.0, shift=ytop - 5.2)
            else:
                dim_h(c, a, b, ytop, fmt(xs[i + 1] - xs[i]), size=2.3, ext0=oy - V.ln(H) - 1.0)
        dim_h(c, p(0, 0)[0], p(600, 0)[0], oy + 7.0, "600", size=3.1, ext0=oy + 1.0)
        xl = ox - 9.5
        zs = [0, Z_BOT, Z_SHELF, Z_SH, Z_TOP, H]
        short = 0
        for i in range(len(zs) - 1):
            seg = zs[i + 1] - zs[i]
            xx = xl - (6.5 * short if seg < 25 else 0)
            if seg < 25:
                short += 1
            else:
                short = 0
            dim_v(c, p(0, zs[i])[1], p(0, zs[i + 1])[1], xx, fmt(seg), size=2.3, ext0=ox - 1.2)
        dim_v(c, p(0, 0)[1], p(0, H)[1], xl - 6.5 * short - 8, "800", size=3.1, ext0=ox - 1.2)
    return V


# ======================================================================
# 4. POTONGAN A-A  (bidang dalam: piring bersandar, gelas di bawah)
# ======================================================================
def draw_section(c, ox, oy, s, dims=True, labels=True, dia=235.0, xcut=262.5):
    V = View(c, (ox, oy), s, 'side')       # y=0 (belakang) di KIRI
    def cut(y0, y1, z0, z1, hatch=True, fill=C_WOOD2):
        V.R(y0, z0, y1, z1, fill=fill, stroke=C_LINE, sw=0.4)
        if hatch:
            p0, p1 = V(y0, z0), V(y1, z1)
            c.hatch(min(p0[0], p1[0]), min(p0[1], p1[1]), max(p0[0], p1[0]), max(p0[1], p1[1]),
                    spacing=2.0, color="#cbb98e", sw=0.16)
    cut(0, 450, 0, Z_BOT)                       # papan bawah
    cut(0, 450, Z_SHELF, Z_SH)                  # papan rak
    cut(0, 450, Z_TOP, H)                       # papan atas
    cut(0, 18, Z_SH, Z_TOP)                     # dinding belakang
    cut(LIP_Y0, LIP_Y1, Z_SH, Z_SH + LIP_H, hatch=False, fill=C_WOOD)     # lis atas
    cut(LIP_Y0, LIP_Y1, Z_BOT, Z_BOT + LIP_H, hatch=False, fill=C_WOOD)   # lis bawah
    # alur sisir (potongan memanjang) pada papan rak
    V.R(SLOT_Y0, SLOT_FLOOR, SLOT_Y1, Z_SH, fill="white", stroke=None)
    V.L(SLOT_Y0, Z_SH, SLOT_Y0, SLOT_FLOOR, stroke=C_LINE, sw=0.35)
    V.L(SLOT_Y0, SLOT_FLOOR, SLOT_Y1, SLOT_FLOOR, stroke=C_LINE, sw=0.35)
    V.L(SLOT_Y1, SLOT_FLOOR, SLOT_Y1, Z_SH, stroke=C_LINE, sw=0.35)
    # piring (potongan tipis miring) - ukuran besar & kecil
    for dd, dash, off in ((235.0, None, 0.0), (147.0, (3, 2), 5.0)):
        sn = (SLOT_C - WALL) / dd
        th = math.asin(sn)
        y_b, z_b = SLOT_C + off, SLOT_FLOOR
        y_t, z_t = WALL + off, SLOT_FLOOR + dd * math.cos(th)
        dy, dz = y_t - y_b, z_t - z_b
        L = math.hypot(dy, dz); uy, uz = dy / L, dz / L
        px_, pz_ = -uz, uy                       # tegak lurus
        tk = 1.5
        pts = [(y_b + px_ * tk, z_b + pz_ * tk), (y_b - px_ * tk, z_b - pz_ * tk),
               (y_t - px_ * tk, z_t - pz_ * tk), (y_t + px_ * tk, z_t + pz_ * tk)]
        if dash:
            V.P(pts, fill=None, stroke=C_PLATE2, sw=0.4, dash=dash)
        else:
            V.P(pts, fill=C_PLATE, stroke=C_PLATE2, sw=0.4)
    # gelas: kompartemen bawah (2 baris) + lantai depan atas
    for yg, solid in ((110, False), (330, True)):
        glass_front(c, V, yg, 0, solid=solid, zbase=Z_BOT + LIP_H)
    for yg in (205, 355):
        glass_front(c, V, yg, 0, zbase=Z_SH + LIP_H, fill="#e4f2f7")
    if labels:
        th, top = lean_of(235.0)
        c.text(*V(120, 700), "piring bersandar ke dinding belakang", size=2.5, anchor="mm", color="#444")
        leader(c, *V(SLOT_C - 2, SLOT_FLOOR + 4), *V(150, 275),
               "alur sisir 12 × 8 (tapak piring)", size=2.3, anchor="lm")
        leader(c, *V(WALL + 5, SLOT_FLOOR + 147 * math.cos(math.radians(16.6)) * 0.5),
               *V(150, 430), "piring ø147 (garis putus)", size=2.2, anchor="lm")
        c.text(*V(52, 470), f"{fmt(th, 1)}°", size=2.6, anchor="mm", color=C_ACCENT, bold=True)
        c.text(*V(300, 600), "gelas di lantai depan", size=2.2, anchor="mm", color="#3d6b7d")
        c.text(*V(220, 150), "gelas / cangkir", size=2.2, anchor="mm", color="#3d6b7d")
        c.text(*V(90, 150), "baris belakang", size=2.1, anchor="mm", color="#8a8a8a")
    if dims:
        xr = ox + V.ln(450) + 9.0
        zs = [0, Z_BOT, Z_SHELF, Z_SH, Z_TOP, H]
        short = 0
        for i in range(len(zs) - 1):
            seg = zs[i + 1] - zs[i]
            xx = xr + (6.5 * short if seg < 25 else 0)
            if seg < 25:
                short += 1
            else:
                short = 0
            dim_v(c, V(0, zs[i])[1], V(0, zs[i + 1])[1], xx, fmt(seg), size=2.3,
                  ext0=ox + V.ln(450) + 1.2, left=False)
        dim_v(c, V(0, 0)[1], V(0, H)[1], xr + 6.5 * short + 8, "800", size=3.1,
              ext0=ox + V.ln(450) + 1.2, left=False)
        yb = oy + 7.0
        dim_h(c, V(0, 0)[0], V(450, 0)[0], yb, "450", size=3.0, ext0=oy + 1.0)
        dim_h(c, V(SLOT_Y0, 0)[0], V(SLOT_Y1, 0)[0], yb, "44", size=2.2, ext0=oy + 0.5, shift=yb + 4.6)
        c.text(*V(80, 0), f"alur: tapak {fmt(SLOT_Y0)}–{fmt(SLOT_Y1)} mm dari muka belakang",
               size=2.1, anchor="lm", color=C_DIM, bg="white")
    return V


# ======================================================================
# 5. POTONGAN B-B  (tampak atas)
# ======================================================================
def draw_plan(c, ox, oy, s, dims=True, labels=True, zcut=390.0):
    V = View(c, (ox, oy), s, 'plan')       # y=0 (belakang) di ATAS
    V.R(0, 0, 18, 450, fill=C_EDGE, stroke=C_LINE, sw=0.35)
    V.R(582, 0, 600, 450, fill=C_EDGE, stroke=C_LINE, sw=0.35)
    V.R(WALL, 0, 582, WALL, fill=C_WOOD2, stroke=C_LINE, sw=0.3)      # dinding belakang
    V.R(WALL, WALL, 582, BATAS_Y0, fill="#f7f4ea", stroke=None)         # zona piring
    # alur sisir (16)
    for x in PIRING_X:
        V.R(x - SLOT_W / 2, SLOT_Y0, x + SLOT_W / 2, SLOT_Y1, fill="#e8d9b4", stroke=C_THIN, sw=0.25)
    # piring (potongan datar): garis lurus sepanjang tali busur pada zcut
    for x, dia in zip(PIRING_X, PIRING_D):
        th, _ = lean_of(dia)
        R = dia / 2
        zc = SLOT_FLOOR + R * math.cos(math.radians(th))
        y_at = SLOT_C - (zcut - SLOT_FLOOR) * (SLOT_C - WALL) / (dia * math.cos(math.radians(th)))
        if abs(zcut - zc) < R:
            half = math.sqrt(R * R - (zcut - zc) ** 2)
            V.R(x - half, y_at - 1.7, x + half, y_at + 1.7, fill="#cfe0ec", stroke="#7fa3bd", sw=0.35)
    # pembatas
    for (b0, b1) in BATAS_X:
        V.R(b0, BATAS_Y0, b1, BATAS_Y1, fill=C_WOOD, stroke=C_LINE, sw=0.3)
    # gelas lantai depan (terpotong)
    for yg in (230, 340):
        for xc in (205, 330, 455):
            p0, p1 = V(xc - GLASS_D / 2, yg - GLASS_D / 2), V(xc + GLASS_D / 2, yg + GLASS_D / 2)
            c.ellipse((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, (p1[0] - p0[0]) / 2, (p1[1] - p0[1]) / 2,
                      fill="#f2fafc", stroke=C_GLASS2, sw=0.25)
    # gelas kompartemen bawah (bayangan) + lis depan
    for yg in (170, 300):
        for xc in (70, 150):
            p0, p1 = V(xc - GLASS_D / 2, yg - GLASS_D / 2), V(xc + GLASS_D / 2, yg + GLASS_D / 2)
            c.ellipse((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, (p1[0] - p0[0]) / 2, (p1[1] - p0[1]) / 2,
                      stroke="#9db6c0", sw=0.2, dash=(2.2, 1.6))
    V.R(18, LIP_Y0, 582, LIP_Y1, fill=C_WOOD, stroke=C_LINE, sw=0.3)
    if labels:
        for gx, gt in [(125.0, "ø147"), (175.0, "ø191"), (225.0, "ø208"), (300.0, "ø235"),
                       (375.0, "ø208"), (425.0, "ø191"), (475.0, "ø147")]:
            V.T(gx, 10, gt, size=2.2, anchor="mm", bold=True, color=C_ACCENT)
        leader(c, *V(60, SLOT_Y0 + 2), *V(280, 56), "16 alur sisir (jarak pusat 25 mm)", size=2.2, anchor="mm")
        leader(c, *V(200, (BATAS_Y0 + BATAS_Y1) / 2), *V(60, 190), "pembatas 18 × 84", size=2.2, anchor="lm")
        c.text(*V(340, 300), "gelas di lantai depan", size=2.2, anchor="mm", color="#3d6b7d")
        c.text(*V(140, 240), "gelas kompartemen bawah", size=2.1, anchor="mm", color="#7d8f96")
        c.text(*V(300, 440), "lis depan (dipotong)", size=2.1, anchor="mm", color="#7a6a45")
        c.text(*V(300, 26), "zona piring (rel alur)", size=2.0, anchor="mm", color="#8a7a55")
    if dims:
        ytop = oy - 7.0
        xs = [0, 18, 150, 168, 291, 309, 432, 450, 582, 600]
        for i in range(len(xs) - 1):
            a, b = V(xs[i], 0)[0], V(xs[i + 1], 0)[0]
            if b - a < 5.0:
                dim_h(c, a, b, ytop, fmt(xs[i + 1] - xs[i]), size=2.0, ext0=oy - 1.0, shift=ytop - 5.2)
            else:
                dim_h(c, a, b, ytop, fmt(xs[i + 1] - xs[i]), size=2.3, ext0=oy - 1.0)
        dim_h(c, V(0, 0)[0], V(600, 0)[0], oy - 19.5, "600", size=3.0, ext0=oy - 1.0)
        xr = ox + V.ln(600) + 8.0
        for i, (y0, y1, tx) in enumerate([(WALL, SLOT_Y0, "18"), (SLOT_Y0, SLOT_Y1, "44"),
                                          (BATAS_Y0, BATAS_Y1, "84"), (LIP_Y0, LIP_Y1, "20")]):
            dim_v(c, V(0, y0)[1], V(0, y1)[1], xr + i * 7.0, tx, size=2.2,
                  ext0=ox + V.ln(600) + 1.0, left=False)
        dim_v(c, V(0, 0)[1], V(0, 450)[1], xr + 4 * 7.0 + 4, "450", size=2.9,
              ext0=ox + V.ln(600) + 1.0, left=False)
    return V


# ======================================================================
# 6. TAMPAK SERONG (3D)
# ======================================================================
class Obl:
    K = 0.3536
    def __init__(self, c, ox, oy, s):
        self.c, self.ox, self.oy, self.s = c, ox, oy, s
        self.k = self.K * s
    def P(self, x, y, z):
        d = D - y
        return (self.ox + self.s * x + self.k * d, self.oy - self.s * (z - 150) - self.k * d)
    def poly(self, pts, **kw):
        self.c.poly([self.P(*p) for p in pts], **kw)
    def box(self, x0, x1, y0, y1, z0, z1, top=C_WOOD, front=C_WOOD2, side=C_EDGE, sw=0.25,
            faces=("top", "back", "front"), front_all=False):
        if "top" in faces:
            self.poly([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], fill=top, stroke=C_LINE, sw=sw)
        if "back" in faces:
            self.poly([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], fill=side, stroke=C_LINE, sw=sw)
        if "front" in faces and (x1 >= 599 or front_all):
            self.poly([(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], fill=front, stroke=C_LINE, sw=sw)
    def circle(self, x_c, y_c, z_c, r, fill=C_PLATE, dashed=False):
        n = 40
        pts = [(x_c + r * math.cos(2 * math.pi * i / n), y_c, z_c + r * math.sin(2 * math.pi * i / n))
               for i in range(n + 1)]
        self.poly(pts, fill=fill, stroke=C_PLATE2, sw=0.25)
    def glass(self, x_c, y_c, z0, dia, h, fill=C_GLASS):
        n = 18
        circ = lambda rr, zz: [(x_c + rr * math.cos(2 * math.pi * i / n), y_c + rr * math.sin(2 * math.pi * i / n), zz)
                               for i in range(n + 1)]
        bx = [self.P(*p) for p in circ(dia * 0.36, z0)]
        tx = [self.P(*p) for p in circ(dia / 2, z0 + h)]
        il = min(range(len(bx)), key=lambda i: bx[i][0]); ir = max(range(len(bx)), key=lambda i: bx[i][0])
        jl = min(range(len(tx)), key=lambda i: tx[i][0]); jr = max(range(len(tx)), key=lambda i: tx[i][0])
        self.c.poly([bx[il], tx[jl], tx[jr], bx[ir]], fill=fill, stroke=C_GLASS2, sw=0.2)
        self.c.poly(tx, fill="#eaf6fa", stroke=C_GLASS2, sw=0.25)


def draw_oblique(c, ox, oy, s, labels=True):
    O = Obl(c, ox, oy, s)
    O.box(18, 582, 0, 18, Z_SH, Z_TOP, top=C_WOOD, front=C_BACK, side=C_BACK, sw=0.28)   # dinding belakang
    O.box(0, 600, 0, 450, 0, Z_BOT, top=C_WOOD, front=C_EDGE, side=C_EDGE, front_all=True)
    O.box(18, 582, LIP_Y0, LIP_Y1, Z_BOT, Z_BOT + LIP_H, top=C_WOOD, front=C_EDGE, side=C_EDGE, sw=0.25, front_all=True)
    for xc in (75, 150, 225):                                                            # gelas bawah
        O.glass(xc, 120, Z_BOT + LIP_H, GLASS_D, GLASS_H)
    O.box(18, 582, 0, 450, Z_SHELF, Z_SH, top=C_WOOD, front=C_EDGE, side=C_EDGE, sw=0.3, front_all=True)  # papan rak
    for x, dia in zip(PIRING_X, PIRING_D):                                                # piring
        th, _ = lean_of(dia)
        R = dia / 2
        zc = SLOT_FLOOR + R * math.cos(math.radians(th))
        yc = SLOT_C - R * math.sin(math.radians(th)) * 0.15
        O.circle(x, yc, zc, R)
    for (b0, b1) in BATAS_X:                                                              # pembatas
        O.box(b0, b0 + 18, BATAS_Y0, BATAS_Y1, Z_SH, Z_TOP, top=C_WOOD, front=C_WOOD2, side=C_EDGE,
              sw=0.25, front_all=True)
    for xc in (215, 320, 425):                                                            # gelas lantai depan
        O.glass(xc, 300, Z_SH, GLASS_D, GLASS_H)
    O.box(18, 582, LIP_Y0, LIP_Y1, Z_SH, Z_SH + LIP_H, top=C_WOOD, front=C_EDGE, side=C_EDGE, sw=0.25, front_all=True)
    O.box(0, 600, 0, 450, Z_TOP, H, top=C_WOOD, front=C_EDGE, side=C_EDGE, sw=0.35, front_all=True)
    O.box(0, 18, 0, 450, 0, H, top=C_EDGE, front=C_EDGE, side=C_EDGE, sw=0.3)
    O.box(582, 600, 0, 450, 0, H, top=C_EDGE, front=C_EDGE, side=C_EDGE, sw=0.3)
    if labels:
        pass


# ======================================================================
# 7. DETAIL
# ======================================================================
def detail_slot(c, ox, oy):
    """DETAIL A - potongan melintang alur sisir, 1:1"""
    s = 1.0
    V = View(c, (ox, oy), s, 'front')
    V.R(0, 0, 60, T, fill=C_WOOD, stroke=C_LINE, sw=0.4)
    p0, p1 = V(0, 0), V(60, T)
    c.hatch(min(p0[0], p1[0]), min(p0[1], p1[1]), max(p0[0], p1[0]), max(p0[1], p1[1]),
            spacing=2.6, color="#c9b184", sw=0.2)
    xc = 30.0
    V.R(xc - SLOT_W / 2, SLOT_D, xc + SLOT_W / 2, T, fill="white", stroke=C_LINE, sw=0.45)
    # bibir piring (3 mm) masuk ke alur
    V.P([(xc - 1.5, T + 20), (xc - 1.5, SLOT_D), (xc + 1.5, SLOT_D), (xc + 1.5, T + 20)],
        fill=C_PLATE, stroke=C_PLATE2, sw=0.35)
    dim_v(c, V(0, T)[1], V(0, SLOT_D)[1], ox - 7, "8", size=2.7)
    dim_v(c, V(0, SLOT_D)[1], V(0, 0)[1], ox - 7, "10", size=2.7)
    dim_v(c, V(0, T)[1], V(0, 0)[1], ox - 13.5, "18", size=2.7)
    dim_h(c, V(xc - SLOT_W / 2, 0)[0], V(xc + SLOT_W / 2, 0)[0], oy + 7.0, "12", size=2.5)
    dim_h(c, V(0, 0)[0], V(60, 0)[0], oy + 13.5, "60 (lebar gigi sisir 25 - 12)", size=2.5)
    c.text(ox + 30, oy - 24.0, "DETAIL A — alur dudukan bibir piring", size=2.9, anchor="mm", bold=True)
    c.text(ox + 30, oy - 20.2, "skala 1 : 1  •  alur 12 × 8 mm, jarak pusat 25 mm", size=2.15,
           anchor="mm", color="#555")
    leader(c, *V(xc + 1.5, SLOT_D + 6), *V(xc + 28, SLOT_D + 14), "bibir piring (3 mm)", size=2.15)


def detail_lean(c, ox, oy, s=0.5):
    """DETAIL B - piring bersandar ke dinding, 1:2 (jendela potong)"""
    V = View(c, (ox, oy), s, 'side', ox=0.0, oy=200.0)     # y -> kanan, z -> atas, acuan z=200
    # dinding belakang (potongan)
    p0, p1 = V(0, 250), V(18, 560)
    c.rect(p0[0], p0[1], p1[0], p1[1], fill=C_WOOD2, stroke=C_LINE, sw=0.5)
    c.hatch(p0[0], p0[1], p1[0], p1[1], spacing=2.4, color="#cbb98e", sw=0.2)
    # papan rak + alur
    p0, p1 = V(-25, Z_SHELF), V(150, Z_SH)
    c.rect(p0[0], p0[1], p1[0], p1[1], fill=C_WOOD2, stroke=C_LINE, sw=0.5)
    c.hatch(p0[0], p0[1], p1[0], p1[1], spacing=2.4, color="#cbb98e", sw=0.2)
    c.rect(*V(SLOT_Y0, SLOT_FLOOR), *V(SLOT_Y1, Z_SH), fill="white", stroke=C_LINE, sw=0.5)
    # piring (garis sandaran) untuk 235 dan 147
    for dd, dash in ((235.0, None), (147.0, (3, 2))):
        sn = (SLOT_C - WALL) / dd; th = math.asin(sn)
        y_b, z_b = SLOT_C, SLOT_FLOOR
        y_t, z_t = WALL, SLOT_FLOOR + dd * math.cos(th)
        dy, dz = y_t - y_b, z_t - z_b; L = math.hypot(dy, dz); uy, uz = dy / L, dz / L
        px_, pz_ = -uz, uy
        pts = [(y_b + px_ * 1.5, z_b + pz_ * 1.5), (y_b - px_ * 1.5, z_b - pz_ * 1.5),
               (y_t - px_ * 1.5, z_t - pz_ * 1.5), (y_t + px_ * 1.5, z_t + pz_ * 1.5)]
        V.P(pts, fill=C_PLATE if not dash else None, stroke=C_PLATE2, sw=0.5, dash=dash)
    # dimensi
    dim_h(c, V(18, 0)[0], V(SLOT_C, 0)[0], oy + 42, "42", size=2.6)
    dim_v(c, V(0, SLOT_FLOOR)[1], V(0, Z_SH)[1], ox - 8, "8", size=2.7)
    off = 0.0
    c.text(V(60, 300)[0], oy - 9.0, "DETAIL B — piring bersandar (sudut 10–17°)", size=2.9,
           anchor="mm", bold=True)
    c.text(V(60, 300)[0], oy - 4.8, "skala 1 : 2  •  bibir bawah di alur, puncak menempel dinding → stabil",
           size=2.15, anchor="mm", color="#555")
    c.text(V(SLOT_C, Z_SHELF)[0] + 3, oy + 38, "alur sisir", size=2.1, anchor="mm", color="#666")


def plate_chart(c, x0, cy, s=1 / 9):
    xx = x0
    c.text(x0 - 4, cy - 30, "DIAGRAM UKURAN PIRING (1 : 10)", size=2.7, anchor="lm", bold=True)
    for dia in PIRING:
        r = dia / 2 * s
        c.circle(xx + r, cy - r, r, fill="#f7f9fb", stroke=C_PLATE2, sw=0.5)
        c.text(xx + r, cy + 4.0, f"ø{fmt(dia)}", size=2.2, anchor="mm", color=C_ACCENT, bold=True)
        xx += dia * s + 6
    c.line((x0 - 3, cy), (xx - 2, cy), stroke=C_THIN, sw=0.3)


# ======================================================================
# 8. LEMBAR GAMBAR
# ======================================================================
def sheet1():
    c = Canvas(PAPER[0], PAPER[1], PPM)
    frame(c, "RAK PIRING & GELAS  —  BOX 600 × 800 × 450 mm",
          "Gambar kerja • plywood 18 mm • 16 piring (ø235 / 208 / 191 / 147) bersandar + gelas & mangkuk")
    Vf = draw_front(c, 34, 178, 1 / 6)
    # rangkaian ukuran vertikal tampak depan -> di KANAN gambar
    xr = 34 + 600 / 6 + 9.0
    zs = [0, Z_BOT, Z_SHELF, Z_SH, Z_TOP, H]; short = 0
    for i in range(len(zs) - 1):
        seg = zs[i + 1] - zs[i]
        xx = xr + (6.5 * short if seg < 25 else 0)
        if seg < 25:
            short += 1
        else:
            short = 0
        dim_v(c, Vf(0, zs[i])[1], Vf(0, zs[i + 1])[1], xx, fmt(seg), size=2.3, ext0=34 + 600 / 6 + 1.2, left=False)
    dim_v(c, Vf(0, 0)[1], Vf(0, H)[1], xr + 6.5 * short + 8, "800", size=3.1,
          ext0=34 + 600 / 6 + 1.2, left=False)
    Vs = draw_section(c, 216, 178, 1 / 6)
    # rangkaian ukuran vertikal potongan -> di KIRI gambar
    xl = 216 - 9.0
    zs = [0, Z_BOT, Z_SHELF, Z_SH, Z_TOP, H]; short = 0
    for i in range(len(zs) - 1):
        seg = zs[i + 1] - zs[i]
        xx = xl - (6.5 * short if seg < 25 else 0)
        if seg < 25:
            short += 1
        else:
            short = 0
        dim_v(c, Vs(0, zs[i])[1], Vs(0, zs[i + 1])[1], xx, fmt(seg), size=2.3, ext0=216 - 1.2)
    dim_v(c, Vs(0, 0)[1], Vs(0, H)[1], xl - 6.5 * short - 8, "800", size=3.1, ext0=216 - 1.2)
    draw_oblique(c, 318, 142, 1 / 11)
    c.text(34, 190, "TAMPAK DEPAN    skala 1 : 6", size=3.3, anchor="lm", bold=True)
    c.text(216, 190, "POTONGAN A-A    skala 1 : 6", size=3.3, anchor="lm", bold=True)
    c.text(360, 172, "TAMPAK SERONG (3D)", size=3.0, anchor="mm", bold=True)
    # tanda potongan A-A
    xA = 34 + (262.5 / 6)
    c.line((xA, 44), (xA, 34.5), stroke=C_LINE, sw=0.5)
    arrow(c, xA, 34.5, 90, L=3.6, Wd=1.3, col=C_LINE)
    c.text(xA + 2.2, 33.0, "A", size=3.4, anchor="lm", bold=True)
    notes_block(c, 34, 202, "CATATAN UMUM", [
        "Semua ukuran dalam milimeter (mm). Skala gambar utama 1 : 6.",
        "Bahan: plywood / multiplek 18 mm tahan air (meranti). 1 lembar 1220 × 2440 cukup.",
        "Piring disimpan BERDIRI menghadap ke depan, BERSANDAR ke dinding belakang (seperti pigura).",
        "Bibir bawah piring masuk ke ALUR SISIR 12 × 8 mm di papan rak → tidak bisa bergeser samping.",
        "Sudut sandar terjadi otomatis 10°–17° tergantung diameter piring (tidak perlu disetel).",
        "Alur sisir: 16 buah, jarak pusat 25 mm, digambar dulu dengan pensil sebelum di-router.",
        "Susunan: piring kecil (ø147) di kedua tepi, makin besar makin ke tengah (agar tidak menabrak dinding samping).",
        "Kompartemen bawah 300 mm + lantai depan kompartemen atas: gelas ø70 × 100, cangkir, mangkuk.",
        "Pembatas 18 mm di depan hanya pengelompokan visual — tidak mengganggu piring.",
        "Finishing 2–3 lapis vernis tahan air (termasuk dalam alur). Beri label ukuran tiap kelompok.",
        "Rak diletakkan di tempat berangin; bersihkan alur berkala agar tidak berjamur.",
    ], size=2.25, lh=3.6)
    ly = 262
    c.text(34, ly - 5.0, "LEGENDA", size=2.7, anchor="lm", bold=True)
    for i, (col, lab) in enumerate([(C_EDGE, "panel samping"), (C_WOOD, "kayu / plywood"), (C_PLATE, "piring"),
                                    (C_GLASS, "gelas"), ("#e8d9b4", "alur sisir")]):
        xx = 34 + i * 44
        c.rect(xx, ly, xx + 6.5, ly + 3.4, fill=col, stroke=C_THIN, sw=0.2)
        c.text(xx + 8.0, ly + 1.7, lab, size=2.2, anchor="lm")
    title_block(c, 262, 248, 408, 289, "RAK PIRING & GELAS",
                "Tampak depan • Potongan A-A • 3D", "1 : 6", ("07-10-2026", "1 dari 3"))
    c.save_svg(os.path.join(OUT, "01-tampak-umum.svg"), "Rak Piring - Tampak Umum")
    c.save_png(os.path.join(OUT, "01-tampak-umum.png"))


def sheet2():
    c = Canvas(PAPER[0], PAPER[1], PPM)
    frame(c, "UKURAN & DETAIL  —  RAK PIRING & GELAS",
          "Potongan B-B (tampak atas), detail alur & sandaran, diagram piring, tabel ukuran")
    draw_plan(c, 30, 56, 1 / 6)
    c.text(30, 137, "POTONGAN B-B  —  tampak atas (bidang potong 390 mm di atas papan rak)   1 : 6",
           size=3.2, anchor="lm", bold=True)
    c.text(30, 142, "piring tampak sebagai garis potong; gelas lantai depan tergambar penuh",
           size=2.2, anchor="lm", color="#555")
    plate_chart(c, 20, 180, s=1 / 9)
    notes_block(c, 30, 196, "MENGAPA BEGITU?", [
        "Bila piring dijejer menghadap depan tanpa sandaran → hanya 2 piring besar yang muat (600 mm).",
        "Dengan bersandar: 16 piring (4 tiap ukuran) + tetap lapang untuk gelas.",
        "Piring kecil wajib di tepi: bibir ø235 = 117,5 mm dari pusat → di tepi akan menabrak dinding.",
    ], size=2.2, lh=3.5)
    detail_slot(c, 46, 240)
    detail_lean(c, 260, 210, s=0.25)
    # tabel kanan
    c.text(176, 26, "TABEL UKURAN UTAMA", size=2.7, anchor="lm", bold=True)
    rows2 = [["UKURAN UTAMA", "NILAI"],
             ["Lebar × tinggi × dalam (luar)", "600 × 800 × 450 mm"],
             ["Tebal papan", "18 mm"],
             ["Tinggi kompartemen bawah", "300 mm"],
             ["Tinggi kompartemen atas", "446 mm"],
             ["Alur sisir (lebar × dalam × jumlah)", "12 × 8 mm, 16 buah"],
             ["Jarak pusat alur", "25 mm"],
             ["Posisi alur (dari muka belakang)", f"{fmt(SLOT_Y0)} – {fmt(SLOT_Y1)} mm"],
             ["Bibir bawah piring masuk alur", "8 mm"],
             ["Sudut sandar piring", "10° – 17°"],
             ["Kapasitas", "16 piring + 12–20 gelas"]]
    table(c, 176, 30, [66, 60], rows2, size=2.3, row_h=4.5, aligns=["lm", "rm"])
    c.text(176, 84, "TABEL KELOMPOK PIRING", size=2.7, anchor="lm", bold=True)
    rows = [["UKURAN", "JUMLAH", "POSISI (pusat, dari tepi kiri)", "PUNCAK PIRING", "SANDAR"]]
    data = [("ø 235", "4 buah", "262,5  •  287,5  •  312,5  •  337,5"),
            ("ø 208", "4 buah", "212,5  •  237,5  •  362,5  •  387,5"),
            ("ø 191", "4 buah", "162,5  •  187,5  •  412,5  •  437,5"),
            ("ø 147", "4 buah", "112,5  •  137,5  •  462,5  •  487,5")]
    for nm, jm, ps in data:
        th, top = lean_of(float(nm.replace("ø ", "").replace(",", ".")))
        rows.append([nm, jm, ps, f"{fmt(top)} mm", f"{fmt(th, 1)}°"])
    table(c, 176, 88, [18, 18, 62, 22, 16], rows, size=2.15, row_h=4.5,
          aligns=["lm", "mm", "lm", "mm", "mm"])
    c.text(176, 114, "PUSAT PIRING selalu di atas pusat alur; jarak antar piring 25 mm.", size=2.15,
           anchor="lm", color="#555")
    notes_block(c, 176, 126, "CATATAN DETAIL", [
        "Alur dibuat dengan router bit lurus 12 mm sedalam 8 mm, atau 2 kali potong gergaji bulat.",
        "Gunakan mal/jarak tetap 25 mm; tandai 16 garis tengah dulu di papan rak.",
        "Panjang alur 44 mm cukup untuk semua ukuran (tapak piring bergeser 49–67 mm dari belakang).",
        "Dinding belakang (564 × 446 × 18) adalah sandaran piring — permukaannya harus rata.",
        "Bila ingin lebih aman, tambah lapisan felt tipis 2 mm pada dinding tempat puncak piring menempel.",
    ], size=2.2, lh=3.5)
    title_block(c, 262, 248, 408, 289, "UKURAN & DETAIL",
                "Potongan B-B, detail alur, tabel", "1 : 6", ("07-10-2026", "2 dari 3"))
    c.save_svg(os.path.join(OUT, "02-ukuran-detail.svg"), "Rak Piring - Ukuran & Detail")
    c.save_png(os.path.join(OUT, "02-ukuran-detail.png"))


BAGIAN = [("A", "Panel samping kiri / kanan", 2, 800, 450),
          ("B", "Papan bawah, papan rak, papan atas", 3, 564, 450),
          ("C", "Dinding belakang (sandaran piring)", 1, 564, 446),
          ("D", "Pembatas / sekat depan", 3, 446, 84),
          ("E", "Lis depan (atas & bawah)", 2, 564, 20)]
LAYOUT = [("A1", 568, 0, 450, 800), ("A2", 568, 804, 450, 800),
          ("B1", 0, 0, 564, 450), ("B2", 0, 454, 564, 450), ("B3", 0, 908, 564, 450),
          ("C", 0, 1362, 564, 446),
          ("D1", 0, 1812, 84, 446), ("D2", 88, 1812, 84, 446), ("D3", 176, 1812, 84, 446),
          ("E1", 0, 2262, 564, 20), ("E2", 0, 2286, 564, 20)]


def nesting_map(c, ox, oy, s):
    w, l = 1220 * s, 2440 * s
    c.rect(ox, oy, ox + w, oy + l, fill="#fbfbf8", stroke=C_LINE, sw=0.5)
    c.rect(ox, oy, ox + 1018 * s, oy + 1812 * s, fill="#f2f0e8", stroke=None)
    for (code, x, y, ww, ll) in LAYOUT:
        x0, y0 = ox + x * s, oy + y * s
        x1, y1 = x0 + ww * s, y0 + ll * s
        fill = {"A": "#e6d7b8", "B": "#efe3c6", "C": "#e4d5b4", "D": "#ece0c0", "E": "#f5efdd"}[code[0]]
        c.rect(x0, y0, x1, y1, fill=fill, stroke="#8a7a55", sw=0.22)
        if ww * s > 5 and ll * s > 3.2:
            c.text((x0 + x1) / 2, (y0 + y1) / 2, code, size=2.4 if ww * s > 12 else 2.0,
                   anchor="mm", bold=True, color="#6b5b35")
    c.text(ox + w / 2, oy - 3.4, "DENAH PEMOTONGAN  —  1 lembar plywood 1220 × 2440 mm   (1 : 24)",
           size=2.9, anchor="mm", bold=True)
    c.text(ox + w / 2, oy + l + 3.6,
           "bahan terpakai 1,87 m² dari 2,98 m² (63%) • sisa ± 1,11 m² untuk cadangan / 3 pembatas tinggi",
           size=2.2, anchor="mm", color="#555")
    c.line((ox + w + 3, oy), (ox + w + 3, oy + l), stroke=C_DIM, sw=0.2)
    c.text(ox + w + 5, oy + l / 2, "2440 mm", size=2.2, anchor="lm", color=C_DIM)
    c.line((ox, oy + l + 7), (ox + w, oy + l + 7), stroke=C_DIM, sw=0.2)
    c.text(ox + w / 2, oy + l + 9.4, "1220 mm", size=2.2, anchor="mm", color=C_DIM)


def sheet3():
    c = Canvas(PAPER[0], PAPER[1], PPM)
    frame(c, "PEMBUATAN  —  RAK PIRING & GELAS 600 × 800 × 450 mm",
          "Daftar potongan, kebutuhan bahan, denah pemotongan, dan langkah perakitan")
    c.text(16, 30, "DAFTAR POTONGAN  (semua plywood 18 mm)", size=2.7, anchor="lm", bold=True)
    rows = [["KODE", "NAMA BAGIAN", "QTY", "UKURAN (P × L) mm"]]
    for (kode, nama, qty, p, l) in BAGIAN:
        rows.append([kode, nama, str(qty), f"{fmt(p)} × {fmt(l)}"])
    rows.append(["", "TOTAL BAHAN 18 mm", "", "1,87 m²"])
    table(c, 16, 33, [13, 92, 11, 64], rows, size=2.35, row_h=4.9, aligns=["mm", "lm", "mm", "mm"])
    c.text(16, 120, "1 lembar plywood 1220 × 2440 = 2,98 m²  •  terpakai 1,87 m² (63%)  •  sisa ± 1,11 m²",
           size=2.3, anchor="lm", color="#555")
    c.text(16, 128, "TAMBAHAN: 16 alur sisir 12 × 8 × 44 mm pada papan rak (jarak pusat 25 mm)",
           size=2.3, anchor="lm", color=C_ACCENT)
    c.text(16, 138, "BAHAN / AKSESORIS", size=2.7, anchor="lm", bold=True)
    rows2 = [["BAHAN / AKSESORIS", "JUMLAH", "KETERANGAN"],
             ["Plywood 18 mm (1220 × 2440)", "1 lembar", "terpakai 63%"],
             ["Lem kayu PVA", "± 500 gram", "semua sambungan"],
             ["Sekrup 4 × 50 mm kepala rata", "± 40 buah", "bor awal ø3 mm"],
             ["Sekrup 3 × 20 mm", "± 12 buah", "lis depan & pembatas"],
             ["Vernis / pelitur tahan air", "1 kaleng kecil", "2–3 lapis seluruh permukaan"],
             ["Karet alas / felt", "4 buah", "alas bawah rak"],
             ["Router bit lurus 12 mm", "1 buah", "untuk 16 alur sisir"]]
    table(c, 16, 141, [66, 32, 62], rows2, size=2.3, row_h=4.7, aligns=["lm", "mm", "lm"])
    nesting_map(c, 250, 34, 1 / 24)
    steps = ["Potong semua bagian A–E sesuai daftar. Amplas 120 → 240.",
             "Tandai 16 garis tengah alur pada papan rak: mulai 112,5 mm dari tepi kiri, selanjutnya setiap 25 mm.",
             "Buat alur 12 × 8 × 44 mm, dari 38 s.d. 82 mm diukur dari tepi belakang papan rak.",
             "Rakit bentuk U: papan bawah B + 2 panel samping A (lem + sekrup 4×50).",
             "Pasang lis depan E di bagian bawah (z 18–38) di antara panel samping.",
             "Pasang papan rak B pada ketinggian atas 336 mm dari alas (alur menghadap ke atas).",
             "Pasang dinding belakang C mulai z 336 sampai 782, menempel papan rak.",
             "Pasang 3 pembatas D (di depan, 88–172 mm dari muka belakang) dari papan rak ke papan atas.",
             "Pasang papan atas B (lem + sekrup dari atas). Pasang lis depan E yang kedua di z 336–356.",
             "Tutup kepala sekrup dengan dempul, amplas rata, bersihkan debu.",
             "Finishing 2–3 lapis vernis termasuk dasar alur. Pasang karet alas.",
             "Uji coba: masukkan piring ø235 pada alur tengah — puncaknya harus menempel dinding belakang."]
    c.text(16, 178, "LANGKAH PERAKITAN", size=3.3, anchor="lm", bold=True)
    y, col = 184, 0
    for i, txt in enumerate(steps):
        x = 16 + col * 122
        c.text(x + 0.4, y, f"{i+1}.", size=2.35, anchor="lm", bold=True, color=C_ACCENT)
        words, line1, line2 = txt.split(), "", ""
        for wd in words:
            if len(line1 + " " + wd) < 60 and not line2:
                line1 = (line1 + " " + wd).strip()
            else:
                line2 = (line2 + " " + wd).strip()
        c.text(x + 4.4, y, line1, size=2.3, anchor="lm")
        if line2:
            c.text(x + 4.4, y + 3.4, line2, size=2.3, anchor="lm")
        y += 7.4 if line2 else 4.6
        if i == 5:
            col, y = 1, 184
    notes_block(c, 16, 248, "CATATAN PENTING", [
        "Piring kecil (ø147) WAJIB di alur tepi (2 paling kiri & 2 paling kanan) agar tidak menabrak dinding samping.",
        "Kapasitas dapat diubah: 16 alur tetap, tinggal atur jumlah piring tiap ukuran.",
        "Hasil akhir: rak 600 × 800 × 450 mm berisi 16 piring + 12–20 gelas/mangkuk.",
    ], size=2.2, lh=3.4)
    title_block(c, 246, 248, 408, 289, "PEMBUATAN",
                "Daftar potongan, bahan, perakitan", "1 : 24", ("07-10-2026", "3 dari 3"))
    c.save_svg(os.path.join(OUT, "03-pembuatan.svg"), "Rak Piring - Pembuatan")
    c.save_png(os.path.join(OUT, "03-pembuatan.png"))


if __name__ == "__main__":
    OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gambar")
    os.makedirs(OUT, exist_ok=True)
    sheet1(); print("lembar 1 selesai")
    sheet2(); print("lembar 2 selesai")
    sheet3(); print("lembar 3 selesai")
