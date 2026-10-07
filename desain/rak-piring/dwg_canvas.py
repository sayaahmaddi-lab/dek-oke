#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dwg_canvas.py - kanvas gambar teknik mini.
Menghasilkan SVG (vektor, satuan mm) dan PNG (raster) dari kode gambar yang sama.
Semua koordinat dalam milimeter kertas.
"""
import math, os
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
FONT_REG = os.path.join(FONT_DIR, "DejaVuSans.ttf")
FONT_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")

# Palet warna
C_LINE   = "#1a1a1a"   # garis utama
C_THIN   = "#5a5a5a"   # garis tipis / bantu
C_DIM    = "#0f5fa8"   # garis ukur
C_TXT    = "#111111"
C_WOOD   = "#efe0bd"   # permukaan kayu
C_WOOD2  = "#e2cda0"
C_EDGE   = "#b08b4f"   # tebal papan (potongan)
C_BACK   = "#f4f2ec"   # panel belakang
C_PLATE  = "#dbe6ef"   # piring
C_PLATE2 = "#a7bccd"
C_GLASS  = "#d6ecf3"
C_GLASS2 = "#8fbccb"
C_METAL  = "#f0f0f0"
C_ACCENT = "#b4472c"


def _esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


class Canvas:
    def __init__(self, w_mm, h_mm, ppm=4.5):
        self.w, self.h, self.ppm = float(w_mm), float(h_mm), float(ppm)
        self.px = int(round(self.w * self.ppm))
        self.py = int(round(self.h * self.ppm))
        self.img = Image.new("RGB", (self.px, self.py), "white")
        self.d = ImageDraw.Draw(self.img)
        self.sv = []          # potongan svg
        self._fonts = {}

    # ---------- utilitas ----------
    def _f(self, size_mm, bold=False):
        key = (round(size_mm, 2), bold)
        if key not in self._fonts:
            px = max(6, int(round(size_mm * self.ppm)))
            self._fonts[key] = ImageFont.truetype(FONT_BOLD if bold else FONT_REG, px)
        return self._fonts[key]

    def _px(self, x):
        return x * self.ppm

    # ---------- bentuk dasar ----------
    def rect(self, x0, y0, x1, y1, fill=None, stroke=None, sw=0.3, dash=None):
        if x1 < x0: x0, x1 = x1, x0
        if y1 < y0: y0, y1 = y1, y0
        if stroke:
            self.sv.append(
                f'<rect x="{x0:.2f}" y="{y0:.2f}" width="{abs(x1-x0):.2f}" height="{abs(y1-y0):.2f}" '
                f'fill="{fill or "none"}" stroke="{stroke}" stroke-width="{sw}"'
                + (f' stroke-dasharray="{dash}"' if dash else '') + '/>')
        else:
            self.sv.append(
                f'<rect x="{x0:.2f}" y="{y0:.2f}" width="{abs(x1-x0):.2f}" height="{abs(y1-y0):.2f}" '
                f'fill="{fill or "none"}"/>')
        if fill:
            self.d.rectangle([self._px(x0), self._px(y0), self._px(x1), self._px(y1)], fill=fill)
        if stroke:
            self._rect_outline(x0, y0, x1, y1, stroke, sw, dash)

    def _rect_outline(self, x0, y0, x1, y1, stroke, sw, dash):
        w = max(1, int(round(sw * self.ppm)))
        if dash:
            for (a, b) in [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)),
                           ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]:
                self.dashline(a, b, stroke, sw, dash)
        else:
            self.d.rectangle([self._px(x0), self._px(y0), self._px(x1), self._px(y1)],
                             outline=stroke, width=w)

    def poly(self, pts, fill=None, stroke=None, sw=0.3, close=True, dash=None):
        p = [(round(x, 2), round(y, 2)) for x, y in pts]
        d_attr = f' stroke-dasharray="{dash}"' if dash else ''
        self.sv.append('<polygon points="' + ' '.join(f'{x},{y}' for x, y in p) + '"'
                       f' fill="{fill or "none"}"'
                       + (f' stroke="{stroke}" stroke-width="{sw}"{d_attr}' if stroke else '')
                       + '/>')
        if fill:
            self.d.polygon([(self._px(x), self._px(y)) for x, y in p], fill=fill)
        if stroke:
            if dash:
                pts2 = p + [p[0]] if close else p
                for i in range(len(pts2) - 1):
                    self.dashline(pts2[i], pts2[i + 1], stroke, sw, dash)
            else:
                w = max(1, int(round(sw * self.ppm)))
                if close:
                    self.d.line([(self._px(x), self._px(y)) for x, y in p] + [(self._px(p[0][0]), self._px(p[0][1]))],
                                fill=stroke, width=w, joint="curve")
                else:
                    self.d.line([(self._px(x), self._px(y)) for x, y in p], fill=stroke, width=w, joint="curve")

    def line(self, p0, p1, stroke=C_LINE, sw=0.3, dash=None):
        d_attr = f' stroke-dasharray="{dash}"' if dash else ''
        self.sv.append(f'<line x1="{p0[0]:.2f}" y1="{p0[1]:.2f}" x2="{p1[0]:.2f}" y2="{p1[1]:.2f}" '
                       f'stroke="{stroke}" stroke-width="{sw}"{d_attr} stroke-linecap="round"/>')
        if dash:
            self.dashline(p0, p1, stroke, sw, dash)
        else:
            w = max(1, int(round(sw * self.ppm)))
            self.d.line([self._px(p0[0]), self._px(p0[1]), self._px(p1[0]), self._px(p1[1])],
                        fill=stroke, width=w)

    def dashline(self, p0, p1, stroke, sw, dash):
        """dash = (panjang, jarak) dalam mm"""
        dl, gl = dash if isinstance(dash, (tuple, list)) else (float(dash), float(dash) * 0.7)
        x0, y0 = p0; x1, y1 = p1
        total = math.hypot(x1 - x0, y1 - y0)
        if total <= 0:
            return
        ux, uy = (x1 - x0) / total, (y1 - y0) / total
        w = max(1, int(round(sw * self.ppm)))
        t = 0.0
        while t < total:
            t2 = min(t + dl, total)
            self.d.line([self._px(x0 + ux * t), self._px(y0 + uy * t),
                         self._px(x0 + ux * t2), self._px(y0 + uy * t2)], fill=stroke, width=w)
            t = t2 + gl

    def circle(self, cx, cy, r, fill=None, stroke=None, sw=0.3, dash=None):
        self.ellipse(cx, cy, r, r, fill, stroke, sw, dash)

    def ellipse(self, cx, cy, rx, ry, fill=None, stroke=None, sw=0.3, dash=None, n=72):
        if stroke:
            d_attr = f' stroke-dasharray="{dash}"' if dash else ''
            self.sv.append(f'<ellipse cx="{cx:.2f}" cy="{cy:.2f}" rx="{rx:.2f}" ry="{ry:.2f}" '
                           f'fill="{fill or "none"}" stroke="{stroke}" stroke-width="{sw}"{d_attr}/>')
        else:
            self.sv.append(f'<ellipse cx="{cx:.2f}" cy="{cy:.2f}" rx="{rx:.2f}" ry="{ry:.2f}" fill="{fill or "none"}"/>')
        if fill:
            self.d.ellipse([self._px(cx - rx), self._px(cy - ry), self._px(cx + rx), self._px(cy + ry)], fill=fill)
        if stroke:
            if dash:
                pts = [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n))
                       for i in range(n + 1)]
                for i in range(n):
                    self.dashline(pts[i], pts[i + 1], stroke, sw, dash)
            else:
                w = max(1, int(round(sw * self.ppm)))
                self.d.ellipse([self._px(cx - rx), self._px(cy - ry), self._px(cx + rx), self._px(cy + ry)],
                               outline=stroke, width=w)

    def arc(self, box, start, end, stroke=C_LINE, sw=0.3):
        x0, y0, x1, y1 = box
        self.sv.append(f'<path d="M {x0:.2f} {y0:.2f} A {abs(x1-x0)/2:.2f} {abs(y1-y0)/2:.2f} 0 0 0 {x1:.2f} {y1:.2f}" '
                       f'fill="none" stroke="{stroke}" stroke-width="{sw}"/>')
        w = max(1, int(round(sw * self.ppm)))
        self.d.arc([self._px(box[0]), self._px(box[1]), self._px(box[2]), self._px(box[3])],
                   start, end, fill=stroke, width=w)

    def text(self, x, y, s, size=3.0, anchor="lm", color=C_TXT, bold=False, bg=None):
        f = self._f(size, bold)
        fam = "DejaVu Sans, Arial, Helvetica, sans-serif"
        weight = "bold" if bold else "normal"
        s_esc = _esc(s)
        ta = {"l": "start", "m": "middle", "r": "end"}[anchor[0]]
        va = {"t": "hanging", "m": "central", "b": "baseline", "a": "baseline"}[anchor[1]]
        fs = f'<text x="{x:.2f}" y="{y:.2f}" font-family="{fam}" font-size="{size}" font-weight="{weight}" ' \
             f'fill="{color}" text-anchor="{ta}" dominant-baseline="{va}">{s_esc}</text>'
        bg_svg = f'<rect x="{x:.2f}" y="{y-size*0.75:.2f}" width="{len(s)*size*0.62:.2f}" height="{size*1.4:.2f}" fill="white"/>' if bg else ''
        self.sv.append(bg_svg + fs)
        if bg:
            tw = self.d.textlength(s, font=f)
            bx0 = {"l": x, "m": x - tw / self.ppm / 2, "r": x - tw / self.ppm}[anchor[0]]
            self.d.rectangle([self._px(bx0 - 0.4), self._px(y - size * 0.8),
                              self._px(bx0 + tw / self.ppm + 0.4), self._px(y + size * 0.8)], fill=bg)
        self.d.text((self._px(x), self._px(y)), s, font=f, fill=color, anchor=anchor)

    def hatch(self, x0, y0, x1, y1, spacing=1.6, color="#9a9a9a", sw=0.22, angle=45):
        """arsir 45 derajat dalam kotak (koordinat kertas, y ke bawah)"""
        self._clip_hatch(x0, y0, x1, y1, x0, y0, x1, y1, spacing, color, sw, angle)

    def hatch_poly(self, pts, spacing=1.6, color="#9a9a9a", sw=0.22, angle=45):
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
        # sederhana: arsir kotak pembatas, lalu tutup dengan path (bukan untuk bentuk rumit)
        self._clip_hatch(x0, y0, x1, y1, x0, y0, x1, y1, spacing, color, sw, angle)

    def _clip_hatch(self, bx0, by0, bx1, by1, cx0, cy0, cx1, cy1, spacing, color, sw, angle):
        """Arsir di dalam kotak pembatas bx (clip sederhana ke cx)."""
        s = math.tan(math.radians(angle))
        # garis: y = s*(x - bx0) + k, k dari -(bx1-bx0)*s sampai (by1-by0)
        k0 = -(bx1 - bx0) * s - spacing
        k1 = (by1 - by0) + spacing
        k = k0
        while k <= k1:
            # cari x pada y=cy0 dan y=cy1
            xa = (cy0 - by0 - k) / s + bx0
            xb = (cy1 - by0 - k) / s + bx0
            p0 = (xa, cy0); p1 = (xb, cy1)
            # potong ke [cx0,cx1]
            if p0[0] > p1[0]:
                p0, p1 = p1, p0
            x0 = max(p0[0], cx0); x1 = min(p1[0], cx1)
            if x1 - x0 > 0.3:
                # hitung ulang y untuk x0 dan x1
                ya = by0 + k + s * (x0 - bx0)
                yb = by0 + k + s * (x1 - bx0)
                self.line((x0, ya), (x1, yb), stroke=color, sw=sw)
            k += spacing

    def save_svg(self, path, title="gambar"):
        head = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}mm" height="{self.h}mm" '
                f'viewBox="0 0 {self.w} {self.h}">\n'
                f'<title>{_esc(title)}</title>\n'
                f'<rect width="{self.w}" height="{self.h}" fill="white"/>\n')
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(head + "\n".join(self.sv) + "\n</svg>\n")

    def save_png(self, path):
        self.img.save(path, optimize=True)


# ------------------------------------------------------------------
class View:
    """Transformasi koordinat model (mm) -> koordinat kertas (mm).

    mode='front' : (x, z)  x kanan, z naik
    mode='side'  : (y, z)  y = jarak dari muka belakang (0=belakang, makin besar ke depan)
    mode='plan'  : (x, y)  y = jarak dari muka belakang, makin ke bawah di kertas
    """
    def __init__(self, canvas, origin, scale, mode, ox=0.0, oy=0.0):
        self.c = canvas
        self.ox, self.oy = origin       # titik acuan gambar di kertas (mm)
        self.s = scale                  # 1/6 = skala 1:6
        self.mode = mode
        self.X = ox                     # offset model
        self.Y = oy

    def __call__(self, a, b):
        ax, by = (a - self.X) * self.s, (b - self.Y) * self.s
        if self.mode == 'front':
            return (self.ox + ax, self.oy - by)
        if self.mode == 'side':
            return (self.ox + ax, self.oy - by)
        if self.mode == 'plan':
            return (self.ox + ax, self.oy + by)
        raise ValueError(self.mode)

    def L(self, a0, b0, a1, b1, **kw):
        self.c.line(self(a0, b0), self(a1, b1), **kw)

    def R(self, a0, b0, a1, b1, **kw):
        p0 = self(a0, b0); p1 = self(a1, b1)
        self.c.rect(p0[0], p0[1], p1[0], p1[1], **kw)

    def P(self, pts, **kw):
        self.c.poly([self(*p) for p in pts], **kw)

    def T(self, a, b, s, **kw):
        p = self(a, b)
        self.c.text(p[0], p[1], s, **kw)

    def ln(self, mm):
        return mm * self.s
