# KAK — Pengembangan Aplikasi Dek-Oke (TA 2026)

Folder ini memuat dokumen **Kerangka Acuan Kerja (KAK)** pengembangan aplikasi
Dek-Oke untuk Dinas Komunikasi dan Informatika Kabupaten Aceh Tengah.

| Berkas | Keterangan |
|---|---|
| `KAK-Dek-Oke-TA2026.docx` | Dokumen KAK siap edit & cetak (Word, A4, Times New Roman 12) |
| `generate_kak.py` | Skrip pembuat dokumen (butuh `pip install python-docx`) |

## Cara membuat ulang dokumen

```bash
pip install python-docx
python generate_kak.py     # menghasilkan KAK-Dek-Oke-TA2026.docx
```

Seluruh isi, angka RAB, dan tabel dikendalikan dari skrip tersebut (lihat variabel
`PARAM` dan bagian data tabel), sehingga perubahan dapat dilakukan sekali lalu
dokumen dibangun ulang.

## Bagian yang perlu diisi/diverifikasi sebelum ditandatangani

1. **Halaman sampul** — Program, Kode Rekening (sesuai DPA-SKPD).
2. **Lembar pengesahan** — nama, NIP, jabatan, dan tanggal; sesuaikan penandatangan
   (PPTK/Kepala Dinas/Inspektur) dengan ketentuan yang berlaku.
3. **Butir I.D (Sasaran)** — jumlah pengguna sasaran (diisi titik-titik) sesuai data
   BKPSDM.
4. **Butir I.E (Dasar Hukum)** — nomor Peraturan Bupati tentang Penjabaran APBK 2026.
5. **Butir VIII (Rincian Biaya)** — komposisi RAB dapat disesuaikan, dengan total
   tetap Rp 10.000.000.
6. **Butir VII (Jadwal)** — M-1 s.d. M-8 adalah minggu ke-1 s.d. ke-8; sesuaikan
   dengan tanggal kontrak.

## Isi dokumen (ringkas)

I. Pendahuluan (latar belakang, gambaran umum, maksud & tujuan, sasaran, dasar
hukum) · II. Penerima Manfaat · III. Hasil yang Diharapkan · IV. Ruang Lingkup dan
Spesifikasi Teknis · V. Metode Pelaksanaan dan Ketentuan Pembayaran · VI. Pelaksana
dan Penanggung Jawab · VII. Jadwal Pelaksanaan · VIII. Rincian Biaya ·
IX. Indikator Kinerja · X. Pelaporan, Monitoring, dan Evaluasi · XI. Kepemilikan
Hasil, Kerahasiaan, dan Pelindungan Data · XII. Penutup · Lampiran 1–3 (daftar
periksa uji terima, struktur data, alur proses).
