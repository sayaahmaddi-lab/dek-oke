#!/usr/bin/env python3
"""
Membangun berkas Excel 'daftar desa + identitas operator' sesuai format image-1.png.

Format kolom (urut sesuai image-1.png):
    No | nama desa | domain | nomor telpon | email | nama lengkap | username

Pemakaian:
    python3 scripts/buat_daftar_operator.py                 # kerangka saja (header)
    python3 scripts/buat_daftar_operator.py data.json       # kerangka + data
    python3 scripts/buat_daftar_operator.py --keluaran X.xlsx data.json

Struktur data.json (array objek):
    [{"nama desa": "...", "domain": "...", "nomor telpon": "...",
      "email": "...", "nama lengkap": "...", "username": "..."}]

Catatan: seluruh sel ditulis sebagai TEKS agar NIK/nomor telepon/angka yang
berawalan nol tidak terpotong.
"""
import argparse
import json
import os
import sys

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

KOLOM = [
    ("No", 6),
    ("nama desa", 22),
    ("domain", 30),
    ("nomor telpon", 18),
    ("email", 30),
    ("nama lengkap", 24),
    ("username", 22),
]

# Kolom yang diketik manual meski isinya angka (jaga nol di depan).
KOLOM_TEKS = {"nomor telpon"}

JUDUL_HIJAU = PatternFill("solid", fgColor="1F7A3D")
TIPIS = Side(style="thin", color="B7C4B9")
BINGKAI = Border(left=TIPIS, right=TIPIS, top=TIPIS, bottom=TIPIS)


def bangun(baris_data, keluaran):
    wb = Workbook()
    ws = wb.active
    ws.title = "Daftar Operator Desa"

    # --- Baris header ---
    for idx, (nama, lebar) in enumerate(KOLOM, start=1):
        sel = ws.cell(row=1, column=idx, value=nama)
        sel.font = Font(bold=True, color="FFFFFF", size=11)
        sel.fill = JUDUL_HIJAU
        sel.alignment = Alignment(horizontal="center", vertical="center")
        sel.border = BINGKAI
        ws.column_dimensions[get_column_letter(idx)].width = lebar
    ws.row_dimensions[1].height = 24

    # --- Baris data ---
    for i, item in enumerate(baris_data, start=1):
        nilai = [i] + [item.get(nama, "") for nama, _ in KOLOM[1:]]
        for j, val in enumerate(nilai, start=1):
            sel = ws.cell(row=i + 1, column=j)
            nama_kolom = KOLOM[j - 1][0]
            if nama_kolom == "No" or nama_kolom in KOLOM_TEKS:
                sel.value = str(val) if val != "" else ""
            else:
                sel.value = val
            sel.border = BINGKAI
            sel.alignment = Alignment(
                horizontal="center" if nama_kolom == "No" else "left", vertical="center"
            )
            if nama_kolom in KOLOM_TEKS:
                sel.number_format = "@"
        ws.row_dimensions[i + 1].height = 18

    # --- Kenyamanan pemakaian ---
    ws.freeze_panes = "A2"
    if baris_data:
        ws.auto_filter.ref = f"A1:{get_column_letter(len(KOLOM))}{len(baris_data) + 1}"

    wb.save(keluaran)
    return keluaran


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data", nargs="?", help="berkas JSON berisi data (opsional)")
    ap.add_argument(
        "--keluaran",
        default="output/daftar-desa-operator.xlsx",
        help="lokasi berkas .xlsx keluaran",
    )
    args = ap.parse_args()

    baris = []
    if args.data:
        with open(args.data, encoding="utf-8") as fh:
            baris = json.load(fh)
        if isinstance(baris, dict):
            baris = baris.get("data", [])

    os.makedirs(os.path.dirname(args.keluaran) or ".", exist_ok=True)
    keluaran = bangun(baris, args.keluaran)
    print(f"OK -> {keluaran}  ({len(baris)} baris data + 1 baris header)")
    print("kolom: " + " | ".join(n for n, _ in KOLOM))
    return 0


if __name__ == "__main__":
    sys.exit(main())
