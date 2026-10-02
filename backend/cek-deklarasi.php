<?php
require_once __DIR__ . '/db.php';
header('Content-Type: application/json; charset=utf-8');
$id=intval($_GET['id'] ?? 0); $nip=trim($_GET['nip'] ?? '');
try{
  $pdo=db();
  if($id){ $st=$pdo->prepare('SELECT id,nama,nip,status,tanggal_isi,created_at FROM deklarasi_konflik WHERE id=:id'); $st->execute(['id'=>$id]); $row=$st->fetch(); if(!$row){http_response_code(404); echo json_encode(['ok'=>false,'message'=>'Data tidak ditemukan']); exit;} echo json_encode(['ok'=>true,'data'=>['id'=>$row['id'],'nama'=>$row['nama'],'namaSam'=>mb_substr($row['nama'],0,2).'***','nipSam'=>mb_substr($row['nip'],0,4).'***'.mb_substr($row['nip'],-3),'status'=>$row['status'],'tanggal_isi'=>$row['tanggal_isi'],'created_at'=>$row['created_at']]]); exit; }
  if($nip!==''){ $st=$pdo->prepare('SELECT id,nama,nip,status,tanggal_isi,created_at FROM deklarasi_konflik WHERE nip=:nip ORDER BY created_at DESC, id DESC LIMIT 5'); $st->execute(['nip'=>$nip]); $rows=$st->fetchAll(); if(!$rows){http_response_code(404); echo json_encode(['ok'=>false,'message'=>'Tidak ada data']); exit;} $data=array_map(fn($r)=>['id'=>$r['id'],'nama'=>mb_substr($r['nama'],0,2).'***','status'=>$r['status'],'tanggal_isi'=>$r['tanggal_isi'],'created_at'=>$r['created_at']], $rows); echo json_encode(['ok'=>true,'data'=>$data,'total'=>count($data)]); exit; }
  http_response_code(400); echo json_encode(['ok'=>false,'message'=>'Sertakan ?id= atau ?nip=']);
}catch(PDOException $e){ http_response_code(500); echo json_encode(['ok'=>false,'message'=>$e->getMessage()]); }
