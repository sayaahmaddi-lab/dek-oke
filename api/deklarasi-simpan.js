// =============================================================
// POST /api/deklarasi-simpan - simpan deklarasi konflik kepentingan
// Body: { nama, nip, jabatan, unit_kerja, perangkat, atasan_*...,
//         tanggal_isi, bagian_a..bagian_f (JSON string), ttd, ttd_nama, ttd_nip }
// =============================================================
const { handleOptions, readJsonBody, query, json } = require('./_lib');

module.exports = async (req, res) => {
  if (handleOptions(req, res)) return;

  if (req.method !== 'POST') {
    return json(res, 405, { ok: false, message: 'Metode tidak diizinkan. Gunakan POST.' });
  }

  let body;
  try { body = await readJsonBody(req); }
  catch { return json(res, 400, { ok: false, message: 'Body JSON tidak valid' }); }

  // Sanitasi key
  const d = {};
  for (const k in body) {
    const cleanK = String(k).replace(/[^A-Za-z0-9_]/g, '');
    d[cleanK] = typeof body[k] === 'string' ? String(body[k]).trim() : body[k];
  }

  // Validasi wajib
  const kurang = [];
  if (!d.nama) kurang.push('nama');
  if (!d.nip)  kurang.push('nip');
  if (kurang.length) {
    return json(res, 422, { ok: false, message: 'Kolom wajib belum diisi: ' + kurang.join(', ') });
  }

  // TTD validasi
  function bersihkanTtd(v) {
    if (!v) return null;
    const s = String(v);
    if (s.length > 5 * 1024 * 1024) return null; // 5 MB
    if (!/^data:image\/(png|jpeg|jpg);base64,[A-Za-z0-9+/=]+$/.test(s)) return null;
    return s;
  }

  const nilai = {
    nama:             String(d.nama || '').slice(0,150),
    nip:              String(d.nip || '').slice(0,50),
    jabatan:          String(d.jabatan || '').slice(0,150),
    unit_kerja:       String(d.unit_kerja || '').slice(0,150),
    perangkat:        String(d.perangkat || '').slice(0,150),
    atasan_nama:      String(d.atasan_nama || '').slice(0,150),
    atasan_nip:       String(d.atasan_nip || '').slice(0,50),
    atasan_jabatan:   String(d.atasan_jabatan || '').slice(0,150),
    atasan_unit:      String(d.atasan_unit || '').slice(0,150),
    atasan_perangkat: String(d.atasan_perangkat || '').slice(0,150),
    tanggal_isi:      String(d.tanggal_isi || '').slice(0,50),
    jenis_konflik:    d.jenis_konflik != null ? String(d.jenis_konflik) : null,
    sumber_konflik:   d.sumber_konflik != null ? String(d.sumber_konflik) : null,
    uraian:           d.uraian != null ? String(d.uraian) : null,
    pengendalian:     d.pengendalian != null ? String(d.pengendalian) : null,
    ttd:         bersihkanTtd(d.ttd || null),
    ttd_nama:    String(d.ttd_nama || '').slice(0,150),
    ttd_nip:     String(d.ttd_nip || '').slice(0,50),
  };

  // Pastikan bagian_a..f valid JSON jika tidak kosong
  for (const k of ['jenis_konflik','sumber_konflik','uraian','pengendalian']) {
    if (nilai[k]) {
      try { JSON.parse(nilai[k]); } catch { nilai[k] = null; }
    }
  }

  try {
    const sql = `INSERT INTO deklarasi_konflik
      (nama, nip, jabatan, unit_kerja, perangkat,
       atasan_nama, atasan_nip, atasan_jabatan, atasan_unit, atasan_perangkat,
       tanggal_isi, jenis_konflik, sumber_konflik, uraian, pengendalian,
       ttd, ttd_nama, ttd_nip)
      VALUES
      ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17,$18)
      RETURNING id`;
    const params = [
      nilai.nama, nilai.nip, nilai.jabatan, nilai.unit_kerja, nilai.perangkat,
      nilai.atasan_nama, nilai.atasan_nip, nilai.atasan_jabatan, nilai.atasan_unit, nilai.atasan_perangkat,
      nilai.tanggal_isi, nilai.jenis_konflik, nilai.sumber_konflik, nilai.uraian, nilai.pengendalian,
      nilai.ttd, nilai.ttd_nama, nilai.ttd_nip
    ];
    const r = await query(sql, params);
    const id = r.rows[0]?.id;
    return json(res, 200, { ok: true, message: 'Data berhasil disimpan.', id });
  } catch (e) {
    console.error('simpan error', e);
    let msg;
    if (e.code === '42P01' || /relation .* does not exist/i.test(e.message || '')) {
      msg = 'Tabel "deklarasi_konflik" belum ada di database Neon. Buka Neon → SQL Editor → jalankan isi file neon-schema.sql (lihat PANDUAN.md langkah A1 poin 4), atau jalankan perintah: npm run setup-db. Setelah itu coba simpan ulang.';
    } else if ((e.message || '').includes('DATABASE_URL')) {
      msg = e.message;
    } else {
      msg = 'Gagal menyimpan: ' + (e.message || 'unknown');
    }
    return json(res, 500, { ok: false, message: msg });
  }
};
