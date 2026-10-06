#!/usr/bin/env python3
"""
Utilitas ekstraksi PDF untuk proyek dek-oke.

Memakai pdfplumber/pypdfium2 untuk:
  1. Mengambil teks mentah tiap halaman  -> <out>/<nama>.txt
  2. Mengambil tabel terdeteksi           -> <out>/<nama>.tables.json
  3. Merender tiap halaman ke PNG         -> <out>/pages/<nama>-pXX.png
     (berguna bila PDF hasil scan sehingga perlu dibaca visual/OCR)

Cara pakai:
    python3 scripts/pdf_extract.py file1.pdf file2.pdf --out extracted
"""
import argparse
import json
import os
import sys


def safe_name(path):
    base = os.path.basename(path)
    return os.path.splitext(base)[0].replace(" ", "_")


def render_page_png(page, dest):
    """Render satu halaman pdfplumber ke PNG (butuh pypdfium2 atau ghostscript)."""
    try:
        img = page.to_image(resolution=200, antialias=True)
        img.save(dest, format="PNG")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"    ! gagal render: {exc}", file=sys.stderr)
        return False


def main():
    ap = argparse.ArgumentParser(description="Ekstraksi teks/tabel/gambar dari PDF")
    ap.add_argument("pdfs", nargs="+", help="berkas PDF masukan")
    ap.add_argument("--out", default="extracted", help="folder keluaran")
    ap.add_argument("--no-pages", action="store_true", help="lewati render PNG")
    args = ap.parse_args()

    import pdfplumber  # impor lambat agar skrip cepat saat --help

    os.makedirs(args.out, exist_ok=True)
    pages_dir = os.path.join(args.out, "pages")
    if not args.no_pages:
        os.makedirs(pages_dir, exist_ok=True)

    ringkasan = []
    for pdf_path in args.pdfs:
        if not os.path.isfile(pdf_path):
            print(f"[LEWAT] tidak ada: {pdf_path}", file=sys.stderr)
            continue
        name = safe_name(pdf_path)
        print(f"[PDF] {pdf_path}")

        teks_semua, tabel_semua = [], []
        with pdfplumber.open(pdf_path) as pdf:
            n = len(pdf.pages)
            print(f"    halaman: {n}")
            for i, page in enumerate(pdf.pages, start=1):
                teks = page.extract_text() or ""
                teks_semua.append(f"===== {name} — HALAMAN {i}/{n} =====\n{teks}\n")
                for t in page.extract_tables() or []:
                    tabel_semua.append({"halaman": i, "baris": t})
                if not args.no_pages:
                    dest = os.path.join(pages_dir, f"{name}-p{i:02d}.png")
                    render_page_png(page, dest)

        txt_dest = os.path.join(args.out, f"{name}.txt")
        with open(txt_dest, "w", encoding="utf-8") as fh:
            fh.write("\n".join(teks_semua))

        json_dest = os.path.join(args.out, f"{name}.tables.json")
        with open(json_dest, "w", encoding="utf-8") as fh:
            json.dump(tabel_semua, fh, ensure_ascii=False, indent=2)

        n_char = sum(len(t) for t in teks_semua)
        print(f"    teks: {n_char} karakter -> {txt_dest}")
        print(f"    tabel: {len(tabel_semua)} -> {json_dest}")
        ringkasan.append(
            {"pdf": pdf_path, "halaman": n, "karakter": n_char, "tabel": len(tabel_semua)}
        )

    print("\n=== RINGKASAN ===")
    print(json.dumps(ringkasan, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
