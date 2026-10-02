#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generator LAPORAN AKHIR
Pengembangan Aplikasi Deklarasi Konflik Kepentingan (Dek-Oke)
Kabupaten Aceh Tengah — Dinas Komunikasi dan Informatika — Tahun 2026

Menghasilkan: Laporan-Akhir-Dek-Oke-2026.docx
Cara pakai:   python generate_laporan.py
Butuh:        pip install python-docx
"""

import os

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

# =====================================================================
# PARAMETER
# =====================================================================
PARAM = {
    "judul": "PENGEMBANGAN APLIKASI DEKLARASI KONFLIK KEPENTINGAN",
    "sub_judul": "KABUPATEN ACEH TENGAH",
    "instansi": "PEMERINTAH KABUPATEN ACEH TENGAH",
    "opd": "DINAS KOMUNIKASI DAN INFORMATIKA",
    "tahun": "2026",
    "aplikasi": "Dek-Oke",
}

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
OUT = os.path.join(HERE, "Laporan-Akhir-Dek-Oke-2026.docx")
LOGO = os.path.join(HERE, "..", "..", "assets", "logo-aceh-tengah.png")

FONT = "Times New Roman"
doc = Document()

# ---------------------------------------------------------------------
# Pengaturan halaman & gaya
# ---------------------------------------------------------------------
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.top_margin, sec.bottom_margin = Cm(2.5), Cm(2.5)
sec.left_margin, sec.right_margin = Cm(3.0), Cm(2.5)
sec.header_distance, sec.footer_distance = Cm(1.2), Cm(1.2)

normal = doc.styles["Normal"]
normal.font.name = FONT
normal.font.size = Pt(12)
_rpr = normal.element.get_or_add_rPr()
_rfonts = _rpr.get_or_add_rFonts()
for _a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
    _rfonts.set(qn(_a), FONT)
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.line_spacing = 1.15

for _s in ("List Bullet", "List Number", "Table Grid"):
    try:
        _st = doc.styles[_s]
        _st.font.name = FONT
        _st.font.size = Pt(11)
    except KeyError:
        pass


# ---------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------
def _fix(paragraph, size=None, bold=None):
    for run in paragraph.runs:
        run.font.name = FONT
        if size:
            run.font.size = Pt(size)
        if bold is not None:
            run.bold = bold
        r = run._element.get_or_add_rPr()
        rf = r.get_or_add_rFonts()
        for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
            rf.set(qn(a), FONT)
    return paragraph


def p(text="", size=12, bold=False, italic=False, align="just", space_after=6,
      space_before=0, indent_left=None, line=1.15):
    par = doc.add_paragraph()
    par.add_run(text)
    par.alignment = {"just": WD_ALIGN_PARAGRAPH.JUSTIFY, "center": WD_ALIGN_PARAGRAPH.CENTER,
                     "left": WD_ALIGN_PARAGRAPH.LEFT, "right": WD_ALIGN_PARAGRAPH.RIGHT}[align]
    pf = par.paragraph_format
    pf.space_after, pf.space_before, pf.line_spacing = Pt(space_after), Pt(space_before), line
    if indent_left:
        pf.left_indent = Cm(indent_left)
    _fix(par, size=size, bold=bold)
    if italic:
        for r in par.runs:
            r.italic = True
    return par


def p_mixed(parts, size=12, align="just", space_after=6, indent_left=None):
    par = doc.add_paragraph()
    for text, bold in parts:
        par.add_run(text).bold = bold
    par.alignment = {"just": WD_ALIGN_PARAGRAPH.JUSTIFY, "center": WD_ALIGN_PARAGRAPH.CENTER,
                     "left": WD_ALIGN_PARAGRAPH.LEFT}[align]
    pf = par.paragraph_format
    pf.space_after = Pt(space_after)
    if indent_left:
        pf.left_indent = Cm(indent_left)
    _fix(par, size=size)
    return par


def bab(nomor, judul):
    par = doc.add_paragraph()
    par.paragraph_format.space_before, par.paragraph_format.space_after = Pt(14), Pt(6)
    par.paragraph_format.keep_with_next = True
    par.add_run(f"{nomor}. {judul.upper()}").bold = True
    _fix(par, size=13, bold=True)
    return par


def sub(nomor, judul, space_before=8):
    par = doc.add_paragraph()
    par.paragraph_format.space_before, par.paragraph_format.space_after = Pt(space_before), Pt(4)
    par.paragraph_format.keep_with_next = True
    par.add_run(f"{nomor} {judul}").bold = True
    _fix(par, size=12, bold=True)
    return par


def bullets(items, num=False, size=11):
    for it in items:
        par = doc.add_paragraph(style="List Number" if num else "List Bullet")
        if isinstance(it, tuple):
            par.add_run(it[0]).bold = True
            par.add_run(it[1])
        else:
            par.add_run(it)
        par.paragraph_format.space_after = Pt(2)
        par.paragraph_format.line_spacing = 1.15
        _fix(par, size=size)


def shade(cell, fill="D9D9D9"):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), fill)
    cell._tc.get_or_add_tcPr().append(shd)


def table(headers, rows, widths, size=10.5, align_center_cols=(), align_right_cols=()):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    hdr = t.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ""
        par = hdr[i].paragraphs[0]
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.paragraph_format.space_after = Pt(2)
        par.add_run(h).bold = True
        _fix(par, size=size, bold=True)
        shade(hdr[i])
    trpr = t.rows[0]._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader")
    th.set(qn("w:val"), "true")
    trpr.append(th)
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ""
            par = cells[i].paragraphs[0]
            par.paragraph_format.space_after = Pt(2)
            par.paragraph_format.line_spacing = 1.0
            if i in align_center_cols:
                par.alignment = WD_ALIGN_PARAGRAPH.CENTER
            elif i in align_right_cols:
                par.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            par.add_run(str(val))
            _fix(par, size=size)
    for r in t.rows:
        for i, w in enumerate(widths):
            r.cells[i].width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return t


def gambar(nama, caption, lebar=15.0):
    """Sisipkan gambar tangkapan layar beserta keterangan."""
    path = os.path.join(IMG, nama)
    par = doc.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    par.paragraph_format.space_before = Pt(6)
    par.paragraph_format.space_after = Pt(2)
    par.paragraph_format.keep_with_next = True
    if os.path.exists(path):
        par.add_run().add_picture(path, width=Cm(lebar))
    else:
        par.add_run("[gambar tidak ditemukan: " + nama + "]")
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_after = Pt(12)
    cap.add_run(caption).italic = True
    _fix(cap, size=10.5)
    for r in cap.runs:
        r.italic = True
    return par


def ttd_blok(kolom_kiri, kolom_kanan):
    kolom = (kolom_kiri, kolom_kanan)
    t = doc.add_table(rows=1, cols=2)
    t.autofit = False
    for idx, blok in enumerate(kolom):
        cell = t.rows[0].cells[idx]
        cell.width = Cm(7.75)
        cell.text = ""
        first = True
        for line in blok:
            par = cell.paragraphs[0] if first else cell.add_paragraph()
            first = False
            par.alignment = WD_ALIGN_PARAGRAPH.CENTER
            par.paragraph_format.space_after = Pt(2)
            par.add_run(line[0]).bold = line[1]
            _fix(par, size=12)
        for _ in range(4):
            par = cell.add_paragraph()
            par.alignment = WD_ALIGN_PARAGRAPH.CENTER
            par.paragraph_format.space_after = Pt(2)
    return t


def nomor_halaman(paragraph):
    run = paragraph.add_run()
    for el, attr in (("w:fldChar", "begin"), ("w:instrText", None), ("w:fldChar", "end")):
        node = OxmlElement(el)
        if el == "w:fldChar":
            node.set(qn("w:fldCharType"), attr)
        else:
            node.set(qn("xml:space"), "preserve")
            node.text = "PAGE"
        run._r.append(node)
    _fix(paragraph, size=9)


# ---------------------------------------------------------------------
# Kepala & kaki halaman
# ---------------------------------------------------------------------
h = sec.header.paragraphs[0]
h.alignment = WD_ALIGN_PARAGRAPH.CENTER
h.add_run(f"Laporan Akhir Pengembangan Aplikasi Dek-Oke — {PARAM['opd'].title()} TA {PARAM['tahun']}")
_fix(h, size=9)
for r in h.runs:
    r.italic = True

f = sec.footer.paragraphs[0]
f.alignment = WD_ALIGN_PARAGRAPH.CENTER
_fix(f, size=9)
f.add_run("Halaman ")
nomor_halaman(f)

# =====================================================================
# HALAMAN JUDUL
# =====================================================================
if os.path.exists(LOGO):
    lp = doc.add_paragraph()
    lp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    lp.paragraph_format.space_after = Pt(6)
    lp.add_run().add_picture(LOGO, width=Cm(3.0))

p("LAPORAN AKHIR", size=18, bold=True, align="center", space_before=8, space_after=14)
p(PARAM["judul"], size=15, bold=True, align="center", space_after=4)
p(PARAM["sub_judul"], size=15, bold=True, align="center", space_after=120)

p(PARAM["instansi"], size=14, bold=True, align="center", space_after=2)
p(PARAM["opd"], size=14, bold=True, align="center", space_after=2)
p("TAHUN " + PARAM["tahun"], size=14, bold=True, align="center")

doc.add_page_break()

# =====================================================================
# DAFTAR ISI (sederhana)
# =====================================================================
p("DAFTAR ISI", size=13, bold=True, align="center", space_after=12)
_daftar = [
    ("1.", "Pendahuluan"),
    ("", "1.1. Latar Belakang"),
    ("", "1.2. Dasar Hukum"),
    ("", "1.3. Maksud dan Sasaran"),
    ("", "1.4. Waktu Pelaksanaan Pekerjaan"),
    ("2.", "Ruang Lingkup Pekerjaan"),
    ("", "2.1. Analisis"),
    ("", "2.2. Desain"),
    ("", "2.3. Spesifikasi Teknis"),
    ("3.", "Hasil Pelaksanaan Kegiatan"),
    ("", "3.1. Hasil Kegiatan"),
    ("", "3.2. Tampilan Aplikasi yang Dikembangkan"),
    ("4.", "Serahan Pekerjaan"),
    ("5.", "Penutup"),
]
for nomor, judul in _daftar:
    par = doc.add_paragraph()
    par.paragraph_format.space_after = Pt(4)
    if not nomor:
        par.paragraph_format.left_indent = Cm(0.8)
    par.add_run(f"{nomor} {judul}")
    _fix(par, size=12, bold=False)

doc.add_page_break()

# =====================================================================
# 1. PENDAHULUAN
# =====================================================================
bab("1", "Pendahuluan")

sub("1.1.", "Latar Belakang")
p("Konflik kepentingan adalah kondisi Pejabat Pemerintahan yang memiliki kepentingan pribadi "
  "untuk menguntungkan diri sendiri dan/atau orang lain dalam penggunaan wewenang, sehingga dapat "
  "memengaruhi netralitas dan kualitas keputusan dan/atau tindakan yang dibuat dan/atau dilakukannya. "
  "Konflik kepentingan yang tidak dikelola dengan baik berpotensi menimbulkan praktik korupsi, kolusi, "
  "dan nepotisme (KKN), serta menurunkan kepercayaan publik terhadap penyelenggaraan pemerintahan.")
p("Peraturan Menteri Pendayagunaan Aparatur Negara dan Reformasi Birokrasi Nomor 17 Tahun 2024 "
  "tentang Pengelolaan Konflik Kepentingan mewajibkan setiap instansi pemerintah membangun dan "
  "melaksanakan Sistem Pengelolaan Konflik Kepentingan, yang meliputi pencatatan Daftar Kepentingan "
  "Pribadi, Deklarasi Konflik Kepentingan, pengendalian konflik kepentingan, pengendalian melalui masa "
  "tunggu (cooling period), serta pelatihan dan konsultasi. Pencatatan Daftar Kepentingan Pribadi "
  "dilaksanakan secara berkala, sekurang-kurangnya 1 (satu) kali dalam 1 (satu) tahun, dan dimuat "
  "dalam sistem informasi instansi.")
p("Sebelumnya, pengelolaan konflik kepentingan di lingkungan Pemerintah Kabupaten Aceh Tengah "
  "dilaksanakan secara manual menggunakan formulir kertas dan lembar kerja elektronik yang belum "
  "terintegrasi. Kondisi tersebut menimbulkan kendala berupa risiko kehilangan dokumen, proses "
  "rekapitulasi yang lambat, ketiadaan pemantauan status penanganan secara terpusat, keharusan "
  "kehadiran fisik untuk tanda tangan, kesulitan penelusuran (audit trail), serta pemborosan kertas "
  "dan ruang penyimpanan.")
p("Menindaklanjuti hal tersebut, pada Tahun Anggaran 2026 dilaksanakan kegiatan pengembangan "
  "Aplikasi Deklarasi Konflik Kepentingan (Dek-Oke) berbasis web yang dapat diakses melalui peramban, "
  "dilengkapi tanda tangan digital, penyimpanan basis data, serta kanal pengelolaan oleh administrator. "
  "Kegiatan ini mendukung pencapaian indikator Sistem Pemerintahan Berbasis Elektronik (SPBE), Zona "
  "Integritas menuju Wilayah Bebas dari Korupsi (ZI-WBK), dan program Kabupaten/Kota Cerdas.")
p("Laporan Akhir ini disusun sebagai bentuk pertanggungjawaban atas pelaksanaan pekerjaan, yang "
  "memuat ruang lingkup pekerjaan, hasil pelaksanaan, serahan pekerjaan, serta kendala dan "
  "rekomendasi tindak lanjut.")

sub("1.2.", "Dasar Hukum")
bullets([
    "Undang-Undang Nomor 28 Tahun 1999 tentang Penyelenggaraan Negara yang Bersih dan Bebas dari "
    "Korupsi, Kolusi, dan Nepotisme;",
    "Undang-Undang Nomor 31 Tahun 1999 tentang Pemberantasan Tindak Pidana Korupsi sebagaimana telah "
    "diubah dengan Undang-Undang Nomor 20 Tahun 2001;",
    "Undang-Undang Nomor 30 Tahun 2014 tentang Administrasi Pemerintahan (Pasal 42 sampai dengan "
    "Pasal 45 mengenai larangan dan pelaporan konflik kepentingan);",
    "Undang-Undang Nomor 5 Tahun 2014 tentang Aparatur Sipil Negara sebagaimana telah diubah dengan "
    "Undang-Undang Nomor 20 Tahun 2023;",
    "Undang-Undang Nomor 27 Tahun 2022 tentang Pelindungan Data Pribadi;",
    "Peraturan Pemerintah Nomor 94 Tahun 2021 tentang Disiplin Pegawai Negeri Sipil;",
    "Peraturan Pemerintah Nomor 12 Tahun 2019 tentang Pengelolaan Keuangan Daerah;",
    "Peraturan Presiden Nomor 95 Tahun 2018 tentang Sistem Pemerintahan Berbasis Elektronik "
    "sebagaimana dilengkapi dengan Peraturan Presiden Nomor 132 Tahun 2022 tentang Arsitektur Sistem "
    "Pemerintahan Berbasis Elektronik Nasional;",
    "Peraturan Menteri Pendayagunaan Aparatur Negara dan Reformasi Birokrasi Nomor 17 Tahun 2024 "
    "tentang Pengelolaan Konflik Kepentingan;",
    "Peraturan Menteri Pendayagunaan Aparatur Negara dan Reformasi Birokrasi Nomor 59 Tahun 2020 "
    "tentang Pemantauan dan Evaluasi Sistem Pemerintahan Berbasis Elektronik;",
    "Peraturan Menteri Dalam Negeri Nomor 77 Tahun 2020 tentang Pedoman Teknis Pengelolaan Keuangan "
    "Daerah;",
    "Peraturan Bupati Aceh Tengah Nomor ……… Tahun " + PARAM["tahun"] + " tentang Penjabaran Anggaran "
    "Pendapatan dan Belanja Kabupaten Tahun Anggaran " + PARAM["tahun"] + ";",
    "Dokumen Pelaksanaan Anggaran Satuan Kerja Perangkat Daerah (DPA-SKPD) Dinas Komunikasi dan "
    "Informatika Kabupaten Aceh Tengah Tahun Anggaran " + PARAM["tahun"] + ".",
], num=True)

sub("1.3.", "Maksud dan Sasaran")
p_mixed([("Maksud. ", True),
         ("Laporan Akhir ini disusun sebagai bentuk pertanggungjawaban pelaksanaan kegiatan "
          "pengembangan Aplikasi Dek-Oke pada Tahun Anggaran 2026, serta sebagai dokumen serah terima "
          "hasil pekerjaan kepada Dinas Komunikasi dan Informatika Kabupaten Aceh Tengah.", False)])
p_mixed([("Sasaran. ", True), ("Sasaran yang hendak dicapai adalah:", False)])
bullets([
    "tersedianya aplikasi Dek-Oke yang berfungsi dan dapat digunakan untuk pengisian Daftar "
    "Kepentingan Pribadi serta Deklarasi Konflik Kepentingan secara daring;",
    "tersedianya kanal pengelolaan dan pemantauan bagi administrator pada Inspektorat Kabupaten "
    "Aceh Tengah;",
    "terlaksananya alih pengetahuan berupa dokumentasi dan manual penggunaan aplikasi;",
    "terpenuhinya aspek keamanan aplikasi serta pelindungan data pribadi pegawai.",
], num=True)

sub("1.4.", "Waktu Pelaksanaan Pekerjaan")
p("Pelaksanaan pekerjaan dilaksanakan selama 2 (dua) bulan (8 minggu) terhitung sejak "
  "…… ……………… " + PARAM["tahun"] + " sampai dengan …… ……………… " + PARAM["tahun"] +
  ", dengan tahapan sebagai berikut:")
table(
    ["No.", "Tahapan Pekerjaan", "Jadwal", "Realisasi", "Keterangan"],
    [
        ["1", "Persiapan dan analisis kebutuhan", "Minggu ke-1 s.d. ke-2", "……/……/" + PARAM["tahun"], "Selesai"],
        ["2", "Perancangan sistem (desain)", "Minggu ke-2 s.d. ke-3", "……/……/" + PARAM["tahun"], "Selesai"],
        ["3", "Pengembangan dan penyempurnaan aplikasi", "Minggu ke-3 s.d. ke-6", "……/……/" + PARAM["tahun"], "Selesai"],
        ["4", "Pengujian dan perbaikan", "Minggu ke-6 s.d. ke-7", "……/……/" + PARAM["tahun"], "Selesai"],
        ["5", "Pelatihan/sosialisasi dan go-live", "Minggu ke-7 s.d. ke-8", "……/……/" + PARAM["tahun"], "Selesai"],
        ["6", "Pemeliharaan, dukungan teknis, dan serah terima", "Minggu ke-7 s.d. ke-8", "……/……/" + PARAM["tahun"], "Selesai"],
    ],
    widths=[1.0, 5.8, 3.2, 2.6, 1.9],
    align_center_cols=(0, 2, 3, 4),
)
p("Catatan: kolom realisasi diisi sesuai tanggal penyelesaian masing-masing tahapan yang "
  "dituangkan dalam berita acara.", size=10.5, italic=True)

# =====================================================================
# 2. RUANG LINGKUP PEKERJAAN
# =====================================================================
bab("2", "Ruang Lingkup Pekerjaan")
p("Ruang lingkup pekerjaan pengembangan Aplikasi Dek-Oke meliputi kegiatan analisis, desain, "
  "pengembangan, pengujian, penerapan pada lingkungan produksi, pelatihan, serta pemeliharaan dan "
  "dukungan teknis. Uraian pelaksanaan masing-masing lingkup pekerjaan adalah sebagai berikut.")

sub("2.1.", "Analisis")
p("Tahap analisis dilaksanakan untuk mengidentifikasi kebutuhan pengguna, kebutuhan fungsional dan "
  "non-fungsional aplikasi, kebutuhan data, serta kebutuhan infrastruktur. Kegiatan yang dilaksanakan "
  "meliputi:")
bullets([
    ("Identifikasi kebutuhan regulasi: ", "mengkaji Permen PANRB Nomor 17 Tahun 2024 beserta "
     "ketentuan terkait lainnya untuk memastikan seluruh informasi yang wajib dicatat dan "
     "dideklarasikan tersedia pada formulir aplikasi."),
    ("Identifikasi kebutuhan pengguna: ", "menginventarisasi kebutuhan pegawai/pejabat pemerintahan "
     "selaku pengisi formulir, administrator pada Inspektorat selaku pengelola data, serta pimpinan "
     "selaku pengguna laporan."),
    ("Identifikasi kebutuhan data: ", "menetapkan struktur data isian formulir (identitas, Bagian "
     "A–F, deklarasi konflik kepentingan, tanda tangan digital) serta kebutuhan rekapitulasi dan "
     "ekspor data."),
    ("Identifikasi kebutuhan keamanan: ", "menganalisis risiko kebocoran data pribadi, penyalahgunaan "
     "akses administrator, dan serangan umum pada aplikasi web."),
    ("Identifikasi kebutuhan infrastruktur: ", "menetapkan kebutuhan hosting, basis data, nama "
     "domain, dan sertifikat keamanan (TLS/SSL)."),
    ("Penetapan kebutuhan fungsional: ", "menuangkan hasil analisis ke dalam daftar kebutuhan "
     "fungsional aplikasi sebagaimana tabel berikut."),
], num=True)
table(
    ["No.", "Kode", "Kebutuhan Fungsional", "Prioritas"],
    [
        ["1", "KF-01", "Pengisian Formulir Daftar Kepentingan Pribadi (identitas dan Bagian A–F)",
         "Wajib"],
        ["2", "KF-02", "Pengisian Formulir Deklarasi Konflik Kepentingan (identitas, atasan pejabat, "
                       "jenis dan sumber konflik, uraian, usulan pengendalian)", "Wajib"],
        ["3", "KF-03", "Penambahan baris isian pada tabel secara dinamis", "Wajib"],
        ["4", "KF-04", "Penyimpanan sementara isian di peramban agar data tidak hilang", "Wajib"],
        ["5", "KF-05", "Tanda tangan digital (mouse/layar sentuh) dengan fungsi undo dan hapus", "Wajib"],
        ["6", "KF-06", "Penyimpanan data ke basis data melalui kanal daring", "Wajib"],
        ["7", "KF-07", "Konfirmasi kepada pengisi bahwa data berhasil direkam", "Wajib"],
        ["8", "KF-08", "Cetak/ekspor dokumen formulir ukuran A4", "Wajib"],
        ["9", "KF-09", "Autentikasi administrator dan pembatasan hak akses", "Wajib"],
        ["10", "KF-10", "Rekapitulasi, pencarian, dan penyaringan data", "Wajib"],
        ["11", "KF-11", "Tampilan lembar isian read-only siap cetak bagi administrator", "Wajib"],
        ["12", "KF-12", "Pengelolaan status penanganan dan catatan administrator", "Wajib"],
        ["13", "KF-13", "Ekspor data rekapitulasi (CSV)", "Wajib"],
        ["14", "KF-14", "Pencatatan log aktivitas penting (audit trail)", "Disarankan"],
    ],
    widths=[1.0, 1.8, 10.4, 2.3],
    align_center_cols=(0, 1, 3),
)
p("Hasil analisis juga menetapkan kebutuhan non-fungsional, antara lain: aplikasi berbasis web tanpa "
  "pemasangan perangkat lunak pada komputer pengguna, kompatibel dengan peramban modern, responsif "
  "pada komputer maupun telepon pintar, menggunakan komunikasi terenkripsi, serta menyediakan "
  "pencadangan data secara berkala.")

sub("2.2.", "Desain")
p("Berdasarkan hasil analisis, disusun desain sistem yang mencakup arsitektur aplikasi, alur data, "
  "desain antarmuka, desain basis data, dan desain keamanan.")
p_mixed([("a. Arsitektur aplikasi. ", True),
         ("Aplikasi dirancang dengan arsitektur tiga lapis (three-tier) yang memisahkan antarmuka "
          "pengguna, logika aplikasi, dan basis data, sehingga mudah dipelihara dan dikembangkan. "
          "Aplikasi dapat dijalankan pada dua mode penerapan, yaitu mode daring pada layanan awan "
          "(Vercel + PostgreSQL/Neon) dan mode lokal pada server instansi (Apache/PHP + MySQL).", False)], indent_left=0.5)
table(
    ["No.", "Lapisan", "Komponen", "Fungsi"],
    [
        ["1", "Antarmuka (client)", "Halaman HTML, CSS, dan JavaScript pada peramban",
         "Menampilkan formulir, menerima isian, menggambar tanda tangan digital, dan menampilkan "
         "konfirmasi serta halaman administrator."],
        ["2", "Logika aplikasi", "API (fungsi serverless Node.js atau layanan PHP)",
         "Memvalidasi isian, memproses autentikasi administrator, menyimpan dan membaca data, serta "
         "menghasilkan berkas ekspor."],
        ["3", "Data", "Basis data relasional (PostgreSQL/MySQL)",
         "Menyimpan data isian formulir, tanda tangan digital, status penanganan, dan catatan "
         "administrator."],
    ],
    widths=[1.0, 3.2, 4.6, 6.7],
    align_center_cols=(0,),
)
p_mixed([("b. Alur data. ", True),
         ("Alur pengisian dimulai dari pengguna mengakses halaman formulir, mengisi data, "
          "membubuhkan tanda tangan digital, kemudian mengirim data melalui kanal daring. Server "
          "memvalidasi dan menyimpan data ke basis data, lalu mengembalikan konfirmasi kepada "
          "pengguna bahwa data berhasil direkam. Administrator mengakses halaman pengelolaan untuk "
          "melakukan rekapitulasi, menelusuri detail lembar isian, menetapkan status dan catatan, "
          "serta mengekspor data.", False)], indent_left=0.5)
p_mixed([("c. Desain antarmuka. ", True),
         ("Antarmuka dirancang menyerupai lembar formulir resmi instansi, menggunakan tata letak "
          "ukuran A4, sehingga hasil cetakan memiliki tampilan yang sama dengan formulir asli. "
          "Antarmuka administrator dirancang berupa dasbor dengan kartu ringkasan, penyaring data, "
          "tabel rekapitulasi, serta tombol tindakan pada setiap baris data.", False)], indent_left=0.5)
p_mixed([("d. Desain basis data. ", True),
         ("Basis data dirancang menggunakan dua tabel utama dengan struktur sebagai berikut.", False)], indent_left=0.5)
table(
    ["No.", "Tabel", "Kolom Utama", "Keterangan"],
    [
        ["1", "pengisian",
         "id; nama; nip; pangkat; jabatan; perangkat; unit_kerja; tanggal_isi; bagian_a s.d. "
         "bagian_f; ttd; ttd_nama; ttd_nip; status; catatan_admin; created_at",
         "Menyimpan isian Formulir Daftar Kepentingan Pribadi. Bagian A–F disimpan dalam format "
         "terstruktur (JSON) agar jumlah baris isian fleksibel."],
        ["2", "deklarasi_konflik",
         "id; nama; nip; jabatan; unit_kerja; perangkat; atasan_nama; atasan_nip; atasan_jabatan; "
         "atasan_unit; atasan_perangkat; tanggal_isi; jenis_konflik; sumber_konflik; uraian; "
         "pengendalian; ttd; ttd_nama; ttd_nip; status; catatan_admin; created_at",
         "Menyimpan Formulir Deklarasi Konflik Kepentingan beserta identitas atasan pejabat yang "
         "dituju."],
    ],
    widths=[1.0, 3.4, 6.2, 4.9],
    align_center_cols=(0,),
    size=10,
)
p_mixed([("e. Desain keamanan. ", True),
         ("Desain keamanan mencakup penggunaan komunikasi terenkripsi (HTTPS/TLS), penyimpanan kata "
          "sandi administrator dalam bentuk hash, autentikasi berbasis token pada kanal pengelolaan, "
          "pembatasan percobaan login, penggunaan parameter terikat pada query basis data, "
          "pembersihan input untuk mencegah eksekusi skrip, pembatasan ukuran data tanda tangan, "
          "serta pencadangan basis data secara berkala.", False)], indent_left=0.5)

sub("2.3.", "Spesifikasi Teknis")
p("Spesifikasi teknis aplikasi yang dikembangkan adalah sebagai berikut:")
table(
    ["No.", "Komponen", "Spesifikasi"],
    [
        ["1", "Antarmuka pengguna", "HTML5, CSS3, JavaScript (tanpa kerangka kerja tambahan), "
                                    "dirancang responsif dan mendukung pengisian melalui layar sentuh"],
        ["2", "Tanda tangan digital", "Kanvas tanda tangan pada peramban; data disimpan dalam format "
                                      "citra (PNG) dengan pembatasan ukuran maksimum 5 MB"],
        ["3", "Logika aplikasi (mode daring)", "Node.js 24 pada fungsi serverless layanan awan, "
                                               "menggunakan modul konektor basis data PostgreSQL"],
        ["4", "Logika aplikasi (mode lokal)", "PHP 8 dengan PDO pada web server Apache (mis. XAMPP)"],
        ["5", "Basis data (mode daring)", "PostgreSQL (layanan Neon) dengan koneksi terenkripsi"],
        ["6", "Basis data (mode lokal)", "MySQL/MariaDB dengan penyimpanan karakter utf8mb4"],
        ["7", "Autentikasi administrator", "Kata sandi tersimpan dalam bentuk hash (bcrypt) dan token "
                                           "akses (JWT HS256) dengan masa berlaku terbatas; "
                                           "pembatasan percobaan login"],
        ["8", "Format dokumen keluaran", "Dokumen ukuran A4 dengan tata letak menyerupai formulir "
                                         "asli, dapat dicetak atau disimpan sebagai PDF; ekspor data "
                                         "rekapitulasi dalam format CSV"],
        ["9", "Kebutuhan peramban", "Google Chrome, Microsoft Edge, Mozilla Firefox, atau Safari "
                                    "versi terkini"],
        ["10", "Kebutuhan infrastruktur", "Layanan hosting aplikasi, basis data, nama domain resmi, "
                                          "dan sertifikat keamanan (TLS/SSL) yang aktif"],
        ["11", "Pencadangan data", "Pencadangan basis data otomatis minimal 1 (satu) kali sehari "
                                   "beserta prosedur pemulihan data"],
        ["12", "Keamanan aplikasi", "HTTPS/TLS, parameter terikat pada query, pembersihan input, "
                                    "pembatasan akses berbasis peran, dan log aktivitas"],
    ],
    widths=[1.0, 4.4, 10.1],
    align_center_cols=(0,),
)

# =====================================================================
# 3. HASIL PELAKSANAAN KEGIATAN
# =====================================================================
bab("3", "Hasil Pelaksanaan Kegiatan")

sub("3.1.", "Hasil Kegiatan")
p("Pelaksanaan kegiatan pengembangan Aplikasi Dek-Oke telah menghasilkan keluaran sebagai berikut:")
table(
    ["No.", "Keluaran", "Volume", "Status"],
    [
        ["1", "Aplikasi Dek-Oke berbasis web dengan halaman beranda dan tautan menuju formulir",
         "1 aplikasi", "Tersedia"],
        ["2", "Modul Formulir Daftar Kepentingan Pribadi (identitas dan Bagian A–F) beserta pernyataan",
         "1 modul", "Tersedia"],
        ["3", "Modul Formulir Deklarasi Konflik Kepentingan (identitas, atasan pejabat, jenis dan "
              "sumber konflik, uraian, serta usulan pengendalian)", "1 modul", "Tersedia"],
        ["4", "Fitur tanda tangan digital dengan fungsi undo dan hapus", "1 fitur", "Tersedia"],
        ["5", "Fitur penyimpanan sementara isian (autosave) di peramban", "1 fitur", "Tersedia"],
        ["6", "Fitur konfirmasi pengisian berhasil direkam kepada pengisi", "1 fitur", "Tersedia"],
        ["7", "Fitur cetak/ekspor dokumen formulir ukuran A4", "1 fitur", "Tersedia"],
        ["8", "Modul administrator: login, rekapitulasi, pencarian, detail lembar isian, pengelolaan "
              "status dan catatan, serta ekspor data CSV", "1 modul", "Tersedia"],
        ["9", "Basis data pengisian dan deklarasi konflik kepentingan beserta indeks pencarian",
         "1 basis data", "Tersedia"],
        ["10", "Dukungan dua mode penerapan, yaitu daring (layanan awan) dan lokal (server instansi)",
         "2 mode", "Tersedia"],
        ["11", "Dokumentasi penggunaan bagi pegawai dan administrator", "2 dokumen", "Tersedia"],
        ["12", "Laporan Akhir pelaksanaan pekerjaan", "1 dokumen", "Tersedia"],
    ],
    widths=[1.0, 9.6, 2.4, 2.5],
    align_center_cols=(0, 2, 3),
)
p("Hasil pengujian fungsi menunjukkan bahwa seluruh kebutuhan fungsional wajib (KF-01 sampai dengan "
  "KF-13) telah berfungsi sebagaimana mestinya, meliputi pengisian formulir, penyimpanan data, "
  "penampilan kembali tanda tangan digital pada lembar isian, pencetakan dokumen ukuran A4, "
  "autentikasi administrator, serta rekapitulasi dan ekspor data. Adapun kebutuhan fungsional "
  "KF-14 (log aktivitas) telah disediakan secara terbatas dan direkomendasikan untuk diperluas pada "
  "pengembangan berikutnya.")
p("Keunggulan hasil pengembangan antara lain:")
bullets([
    "formulir digital telah disusun mengikuti format formulir resmi dan substansi Permen PANRB "
    "Nomor 17 Tahun 2024;",
    "pengisian dapat dilakukan tanpa kehadiran fisik karena tanda tangan dibubuhkan secara digital;",
    "isian tidak hilang apabila pengguna berpindah halaman atau koneksi terputus sementara, karena "
    "tersimpan sementara di peramban;",
    "administrator dapat melihat lembar isian persis seperti formulir asli, lengkap dengan tanda "
    "tangan, dan siap dicetak;",
    "aplikasi dapat dijalankan pada layanan awan maupun pada server milik instansi sesuai kebutuhan;",
    "alur pengisian sederhana sehingga tidak memerlukan pelatihan teknis yang panjang bagi pengguna.",
], num=True)
p("Adapun kendala yang dihadapi selama pelaksanaan pekerjaan serta langkah penanganannya adalah "
  "sebagai berikut:")
table(
    ["No.", "Kendala", "Langkah Penanganan"],
    [
        ["1", "Data isian dan tanda tangan digital berukuran besar sehingga berpotensi membebani "
              "penyimpanan basis data",
         "Diterapkan pembatasan ukuran data tanda tangan dan pemangkasan area goresan sebelum data "
         "disimpan."],
        ["2", "Perbedaan lingkungan penerapan (server instansi dan layanan awan) menyebabkan perbedaan "
              "kanal penyimpanan data",
         "Dikembangkan penyesuaian kanal penyimpanan secara otomatis disertai mekanisme cadangan "
         "apabila kanal utama tidak tersedia."],
        ["3", "Kebutuhan penyesuaian format formulir dengan ketentuan terbaru pengelolaan konflik "
              "kepentingan",
         "Dilakukan penyesuaian berkelanjutan terhadap struktur isian formulir dan penambahan "
         "Formulir Deklarasi Konflik Kepentingan."],
    ],
    widths=[1.0, 6.8, 7.7],
    align_center_cols=(0,),
)

sub("3.2.", "Tampilan Aplikasi yang Dikembangkan")
p("Berikut ini ditampilkan hasil pengembangan aplikasi. Tangkapan layar diambil langsung dari "
  "aplikasi dengan menggunakan data contoh.")

gambar("01-beranda.png", "Gambar 1. Halaman beranda aplikasi Dek-Oke")
gambar("02-formulir-dkp.png", "Gambar 2. Formulir Daftar Kepentingan Pribadi (identitas dan Bagian A–B)")
gambar("03-formulir-dkp-ttd.png", "Gambar 3. Pernyataan dan pembubuhan tanda tangan digital")
gambar("04-konfirmasi.png", "Gambar 4. Konfirmasi bahwa data yang dimasukkan berhasil direkam")
gambar("05-formulir-deklarasi.png", "Gambar 5. Formulir Deklarasi Konflik Kepentingan (identitas dan jenis/sumber konflik)")
gambar("06-deklarasi-uraian.png", "Gambar 6. Bagian uraian dan bentuk pengendalian konflik kepentingan")
gambar("07-login-admin.png", "Gambar 7. Halaman login administrator")
gambar("08-admin-pengisian.png", "Gambar 8. Dasbor administrator — rekapitulasi Daftar Kepentingan Pribadi")
gambar("09-admin-deklarasi.png", "Gambar 9. Dasbor administrator — rekapitulasi Deklarasi Konflik Kepentingan")

# =====================================================================
# 4. SERAHAN PEKERJAAN
# =====================================================================
bab("4", "Serahan Pekerjaan")
p("Serahan pekerjaan (deliverables) yang diserahkan kepada Dinas Komunikasi dan Informatika "
  "Kabupaten Aceh Tengah adalah sebagai berikut:")
table(
    ["No.", "Jenis Serahan", "Bentuk/Format", "Jumlah", "Keterangan"],
    [
        ["1", "Kode sumber aplikasi (source code) beserta repositori",
         "Berkas elektronik pada repositori", "1 paket",
         "Diserahkan beserta riwayat perubahan (version control) dan hak akses pengelolaan."],
        ["2", "Aplikasi pada lingkungan produksi", "Aplikasi web aktif", "1 aplikasi",
         "Dapat diakses melalui alamat/domain yang ditetapkan."],
        ["3", "Basis data dan skema tabel", "Skrip basis data (SQL) dan basis data aktif", "1 paket",
         "Meliputi tabel pengisian dan deklarasi_konflik beserta indeks."],
        ["4", "Akun dan hak akses pengelolaan", "Akun administrator, akun basis data, akses hosting",
         "1 paket", "Diserahkan melalui berita acara serah terima."],
        ["5", "Manual penggunaan bagi pegawai", "Dokumen elektronik (PDF/DOCX) dan halaman bantuan",
         "1 dokumen", "Memuat tata cara pengisian formulir dan pembubuhan tanda tangan."],
        ["6", "Manual penggunaan bagi administrator", "Dokumen elektronik (PDF/DOCX)", "1 dokumen",
         "Memuat tata cara login, rekapitulasi, pengelolaan status, dan ekspor data."],
        ["7", "Dokumentasi teknis aplikasi", "Dokumen elektronik (PDF/DOCX)", "1 dokumen",
         "Memuat arsitektur, struktur data, dan petunjuk pemeliharaan."],
        ["8", "Laporan Akhir dan berita acara", "Dokumen elektronik dan cetak", "1 paket",
         "Meliputi berita acara pengujian, serah terima, dan penyelesaian pekerjaan."],
    ],
    widths=[1.0, 4.4, 3.6, 1.8, 4.7],
    align_center_cols=(0, 3),
    size=10,
)
p("Seluruh serahan pekerjaan telah diperiksa kesesuaiannya dengan ruang lingkup pekerjaan dan "
  "dinyatakan lengkap, serta dituangkan dalam Berita Acara Serah Terima Pekerjaan.")

# =====================================================================
# 5. PENUTUP
# =====================================================================
bab("5", "Penutup")
p("Pelaksanaan kegiatan pengembangan Aplikasi Deklarasi Konflik Kepentingan (Dek-Oke) pada Tahun "
  "Anggaran 2026 telah selesai dilaksanakan sesuai ruang lingkup pekerjaan yang ditetapkan. Aplikasi "
  "telah berfungsi untuk pengisian Daftar Kepentingan Pribadi dan Deklarasi Konflik Kepentingan "
  "secara daring, dilengkapi tanda tangan digital, penyimpanan basis data, kanal pengelolaan bagi "
  "administrator, serta dokumentasi penggunaan.")
p("Aplikasi ini diharapkan dapat mempercepat dan mempermudah pelaksanaan kewajiban pencatatan "
  "kepentingan pribadi serta deklarasi konflik kepentingan bagi ASN dan Pejabat Pemerintahan di "
  "lingkungan Pemerintah Kabupaten Aceh Tengah, sekaligus memudahkan Inspektorat Kabupaten Aceh "
  "Tengah dalam melakukan rekapitulasi, pemantauan, dan analisis risiko konflik kepentingan.")
p("Untuk menjamin keberlanjutan pemanfaatan aplikasi, disampaikan rekomendasi sebagai berikut:")
bullets([
    "melaksanakan sosialisasi dan pelatihan penggunaan aplikasi kepada seluruh perangkat daerah "
    "secara terjadwal;",
    "menetapkan kebijakan internal mengenai kewajiban pengisian, jadwal pengisian berkala, serta "
    "tata kelola data konflik kepentingan;",
    "melaksanakan pemeliharaan rutin, pemantauan kinerja aplikasi, dan pencadangan data secara "
    "berkala;",
    "melakukan evaluasi pemanfaatan aplikasi secara berkala sebagai dasar penyusunan rencana "
    "pengembangan tahun anggaran berikutnya;",
    "mengembangkan integrasi dengan sistem kepegawaian dan pemanfaatan tanda tangan elektronik "
    "tersertifikasi pada tahap pengembangan selanjutnya;",
    "memperluas cakupan fitur log aktivitas (audit trail) dan pelaporan statistik untuk mendukung "
    "pengawasan.",
], num=True)
p("Demikian Laporan Akhir ini disusun sebagai bentuk pertanggungjawaban pelaksanaan kegiatan dan "
  "menjadi acuan bagi pemeliharaan serta pengembangan aplikasi pada masa yang akan datang.")

# --- lembar pengesahan
doc.add_page_break()
p("Laporan Akhir ini disahkan pada tanggal …… ……………… " + PARAM["tahun"] + ".", align="left", space_after=18)
ttd_blok([
    ("Mengetahui,", False),
    ("Kepala Dinas Komunikasi dan Informatika", False),
    ("Kabupaten Aceh Tengah", False),
    ("", False), ("", False), ("", False),
    ("……………………………………", True),
    ("NIP. ……………………………………", False),
], [
    ("Takengon, …… ……………… " + PARAM["tahun"], False),
    ("Pejabat Pelaksana Teknis Kegiatan (PPTK)", False),
    ("Sub Kegiatan Koordinasi dan Fasilitasi", False),
    ("Penyelenggaraan Kabupaten/Kota Cerdas", False),
    ("", False), ("", False),
    ("……………………………………", True),
    ("NIP. ……………………………………", False),
])

doc.save(OUT)
print("Berhasil dibuat:", OUT)
