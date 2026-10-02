# Laporan Akhir — Pengembangan Aplikasi Dek-Oke (TA 2026)

Folder ini memuat **Laporan Akhir** pelaksanaan pengembangan Aplikasi Deklarasi
Konflik Kepentingan (Dek-Oke) untuk Dinas Komunikasi dan Informatika Kabupaten
Aceh Tengah.

| Berkas | Keterangan |
|---|---|
| `Laporan-Akhir-Dek-Oke-2026.docx` | Dokumen laporan siap edit & cetak (Word, A4, Times New Roman 12) |
| `generate_laporan.py` | Skrip pembuat dokumen (butuh `pip install python-docx`) |
| `img/` | Tangkapan layar aplikasi yang dipakai pada bagian 3.2 |

## Cara membuat ulang dokumen

```bash
pip install python-docx
python generate_laporan.py     # menghasilkan Laporan-Akhir-Dek-Oke-2026.docx
```

## Struktur dokumen

- Halaman judul: **LAPORAN AKHIR — Pengembangan Aplikasi Deklarasi Konflik
  Kepentingan — Kabupaten Aceh Tengah** (Pemerintah Kabupaten Aceh Tengah,
  Dinas Komunikasi dan Informatika, Tahun 2026)
- Daftar isi
- **1. Pendahuluan** — 1.1 Latar Belakang; 1.2 Dasar Hukum; 1.3 Maksud dan
  Sasaran; 1.4 Waktu Pelaksanaan Pekerjaan
- **2. Ruang Lingkup Pekerjaan** — 2.1 Analisis; 2.2 Desain; 2.3 Spesifikasi Teknis
- **3. Hasil Pelaksanaan Kegiatan** — 3.1 Hasil Kegiatan; 3.2 Tampilan Aplikasi
  yang Dikembangkan (9 gambar)
- **4. Serahan Pekerjaan**
- **5. Penutup** (memuat rekomendasi tindak lanjut)
- Lembar pengesahan (Kepala Dinas dan PPTK)

## Cara mengambil ulang tangkapan layar

Tangkapan layar pada `img/` diambil langsung dari aplikasi (bukan rekayasa
gambar) dengan data contoh. Alur pengambilan:

1. Jalankan server statis dari akar repo: `python3 -m http.server 8000`
2. Buka aplikasi dengan peramban headless, isi formulir dengan data contoh,
   dan ambil tangkapan layar halaman beranda, formulir, konfirmasi, login, serta
   dasbor administrator.

Catatan: pada dasbor administrator, permintaan ke `/api/*` disimulasikan
(mock) dengan data contoh karena aplikasi memerlukan basis data produksi.

## Bagian yang perlu diisi/diverifikasi sebelum ditandatangani

1. **Bagian 1.2** — nomor Peraturan Bupati tentang Penjabaran APBK 2026.
2. **Bagian 1.4** — tanggal mulai dan berakhirnya pelaksanaan pekerjaan serta
   kolom **Realisasi** tiap tahapan (sesuai berita acara).
3. **Lembar pengesahan** — tanggal, nama, dan NIP; sesuaikan penandatangan
   (Kepala Dinas dan PPTK/Inspektur) dengan ketentuan yang berlaku.
4. **Bagian 3.2** — gambar dapat diganti dengan tangkapan layar dari
   lingkungan produksi setelah aplikasi dipasang (mis. setelah go-live).
