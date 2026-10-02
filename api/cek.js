// GET /api/cek?id=123 or ?nip=xxx  (publik, tanpa login)
// Mengembalikan status rekam agar pengisi bisa verifikasi tanpa akses admin
const { handleOptions, query, json } = require('./_lib');

module.exports = async (req, res) => {
  if (handleOptions(req, res)) return;
  if (req.method !== 'GET') return json(res, 405, { ok:false, message:'Gunakan GET. Contoh: /api/cek?id=123 atau /api/cek?nip=1987' });
  const url = new URL(req.url, `https://${req.headers.host || 'localhost'}`);
  const id = parseInt(url.searchParams.get('id') || req.query?.id || '0', 10);
  const nip = String(url.searchParams.get('nip') || req.query?.nip || '').trim().slice(0,50);

  try {
    if (id) {
      const r = await query('SELECT id, nama, nip, status, tanggal_isi, created_at FROM pengisian WHERE id=$1', [id]);
      if (!r.rowCount) return json(res, 404, { ok:false, message:'Data tidak ditemukan. Periksa ID.' });
      const row = r.rows[0];
      // samarkan nama & nip untuk privasi: tampil 2 huruf awal + ***
      const namaSam = row.nama ? row.nama.slice(0,2) + '***' : '-';
      const nipSam = row.nip ? row.nip.slice(0,4) + '***' + row.nip.slice(-3) : '-';
      return json(res, 200, { ok:true, data:{ id:row.id, nama:row.nama, namaSam, nipSam, nip: row.nip ? row.nip.slice(0,2)+'***' : '', status:row.status||'BARU', tanggal_isi:row.tanggal_isi, created_at:row.created_at }, message:'Data ditemukan.' });
    }
    if (nip) {
      const r = await query('SELECT id, nama, nip, status, tanggal_isi, created_at FROM pengisian WHERE nip=$1 ORDER BY created_at DESC, id DESC LIMIT 5', [nip]);
      if (!r.rowCount) return json(res, 404, { ok:false, message:'Tidak ada data untuk NIP tersebut.' });
      const data = r.rows.map(row => ({ id:row.id, nama:row.nama ? row.nama.slice(0,2)+'***' : '-', status:row.status||'BARU', tanggal_isi:row.tanggal_isi, created_at:row.created_at }));
      return json(res, 200, { ok:true, data, total:data.length, message:`Ditemukan ${data.length} rekaman.` });
    }
    return json(res, 400, { ok:false, message:'Sertakan ?id= atau ?nip= . Contoh: /api/cek?id=12' });
  } catch (e) {
    return json(res, 500, { ok:false, message:e.message });
  }
};
