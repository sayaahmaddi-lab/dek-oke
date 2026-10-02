<?php
// =============================================================
// Endpoint: deklarasi konflik kepentingan -> tabel `deklarasi_konflik`
// =============================================================
require_once __DIR__ . '/db.php';
header('Content-Type: application/json; charset=utf-8');
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    http_response_code(405);
    echo json_encode(['ok' => false, 'message' => 'Metode tidak diizinkan.']);
    exit;
}
$d = [];
foreach (baca_body_json() as $k => $v) {
    $k = preg_replace('/[^A-Za-z0-9_]/', '', (string)$k);
    $d[$k] = is_string($v) ? trim($v) : $v;
}
$kurang=[]; foreach(['nama','nip'] as $f) if(empty($d[$f])) $kurang[]=$f;
if($kurang){ http_response_code(422); echo json_encode(['ok'=>false,'message'=>'Kolom wajib belum diisi: '.implode(', ',$kurang)]); exit; }
function bersihkan_ttd(?string $ttd): ?string {
    if ($ttd===null||$ttd==='') return null;
    if (mb_strlen($ttd)>5*1024*1024) return null;
    if (!preg_match('#^data:image/(png|jpeg|jpg);base64,[A-Za-z0-9+/=]+$#',$ttd)) return null;
    return $ttd;
}
$nilai=[
    'nama'=>mb_substr($d['nama']??'',0,150),
    'nip'=>mb_substr($d['nip']??'',0,50),
    'jabatan'=>mb_substr($d['jabatan']??'',0,150),
    'unit_kerja'=>mb_substr($d['unit_kerja']??'',0,150),
    'perangkat'=>mb_substr($d['perangkat']??'',0,150),
    'atasan_nama'=>mb_substr($d['atasan_nama']??'',0,150),
    'atasan_nip'=>mb_substr($d['atasan_nip']??'',0,50),
    'atasan_jabatan'=>mb_substr($d['atasan_jabatan']??'',0,150),
    'atasan_unit'=>mb_substr($d['atasan_unit']??'',0,150),
    'atasan_perangkat'=>mb_substr($d['atasan_perangkat']??'',0,150),
    'tanggal_isi'=>mb_substr($d['tanggal_isi']??'',0,50),
    'jenis_konflik'=> $d['jenis_konflik']??null,
    'sumber_konflik'=>$d['sumber_konflik']??null,
    'uraian'=>$d['uraian']??null,
    'pengendalian'=>$d['pengendalian']??null,
    'ttd'=>bersihkan_ttd($d['ttd']??null),
    'ttd_nama'=>mb_substr($d['ttd_nama']??'',0,150),
    'ttd_nip'=>mb_substr($d['ttd_nip']??'',0,50),
];
foreach(['jenis_konflik','sumber_konflik','uraian','pengendalian'] as $b){
    if($nilai[$b]!==null&&$nilai[$b]!==''){ json_decode($nilai[$b]); if(json_last_error()!==JSON_ERROR_NONE) $nilai[$b]=null; }
}
$sql='INSERT INTO deklarasi_konflik
            (nama,nip,jabatan,unit_kerja,perangkat,atasan_nama,atasan_nip,atasan_jabatan,atasan_unit,atasan_perangkat,tanggal_isi,jenis_konflik,sumber_konflik,uraian,pengendalian,ttd,ttd_nama,ttd_nip)
        VALUES
            (:nama,:nip,:jabatan,:unit_kerja,:perangkat,:atasan_nama,:atasan_nip,:atasan_jabatan,:atasan_unit,:atasan_perangkat,:tanggal_isi,:jenis_konflik,:sumber_konflik,:uraian,:pengendalian,:ttd,:ttd_nama,:ttd_nip)';
try{
    $pdo=db(); $st=$pdo->prepare($sql); $st->execute($nilai);
    echo json_encode(['ok'=>true,'message'=>'Data berhasil disimpan.','id'=>(int)$pdo->lastInsertId()]);
}catch(PDOException $e){ http_response_code(500); echo json_encode(['ok'=>false,'message'=>'Gagal menyimpan: '.$e->getMessage()]); }
