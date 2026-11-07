# Laporan Akhir

## 1. Hasil evaluasi

Tempel keluaran `python evaluate.py` setelah `data/ground_truth.csv` dilengkapi.

```text
Dievaluasi: audit.sql, campuran_error.sql, laporan_penjualan.sql, pemeliharaan.sql (27 triple)

Metode   Precision  Recall     F1
parser        1.00    1.00   1.00
regex         0.65    0.81   0.72

[regex]
  salah ditemukan (FP): ('audit.sql', 16, 'sesi', 'R')
  salah ditemukan (FP): ('campuran_error.sql', 4, 'pesanan', 'R')
  salah ditemukan (FP): ('campuran_error.sql', 8, 'keranjang', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'pelanggan', 'D')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'pelanggan', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'pesanan', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'rahasia', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 15, 'pesanan', 'R')
  salah ditemukan (FP): ('pemeliharaan.sql', 2, 'crm.alamat', 'R')
  salah ditemukan (FP): ('pemeliharaan.sql', 2, 'crm.pelanggan', 'R')
  salah ditemukan (FP): ('pemeliharaan.sql', 2, 'pelanggan_lama', 'U')
  salah ditemukan (FP): ('pemeliharaan.sql', 15, 'crm.alamat', 'R')
  terlewat (FN):       ('audit.sql', 2, 'pesanan', 'R')
  terlewat (FN):       ('laporan_penjualan.sql', 3, 'pelanggan', 'R')
  terlewat (FN):       ('laporan_penjualan.sql', 3, 'pesanan', 'R')
  terlewat (FN):       ('pemeliharaan.sql', 3, 'crm.alamat', 'R')
  terlewat (FN):       ('pemeliharaan.sql', 3, 'crm.pelanggan', 'R')

```

## 2. Tiga kasus di mana regex salah

Untuk tiap kasus: SQL-nya, kesalahan regex, dan mengapa parser benar (kaitkan dengan konsep
lexing, parsing, atau resolusi).

1. **Komentar dan isi string dianggap perintah SQL**
   - SQL:
     ```sql
     -- DELETE FROM pelanggan   (baris ini komentar, bukan perintah)
     SELECT p.nama, SUM(o.total) AS omzet
     FROM pelanggan p
     JOIN pesanan o ON o.pelanggan_id = p.id
     WHERE o.status = 'LUNAS' AND o.catatan <> 'FROM rahasia'
     ```
   - Regex: membaca teks apa adanya. Kata `DELETE` di komentar    dianggap perintah, jadi muncul `pelanggan D` yang sebenarnya tidak ada. Tulisan `FROM rahasia` di dalam string dianggap tabel, jadi muncul `rahasia R`. Nomor barisnya juga salah (baris 2, seharusnya baris 3). `pemeliharaan.sql` sama: `UPDATE pelanggan_lama` di komentar dianggap perintah `U`.
   - Parser: komentar dibuang, dan isi string hanya dianggap satu teks biasa. Jadi tidak
     ada `pelanggan D` dan tidak ada tabel `rahasia`.
   - Kenapa beda: lexer (Bab 4) membuang komentar dan membungkus string jadi satu token, jadi isinya tidak pernah dibaca sebagai SQL. Regex tidak punya tahap ini.

2. **`DELETE FROM` ikut dihitung sebagai baca**
   - SQL: `DELETE FROM sesi s WHERE s.kedaluwarsa < :sekarang;`
   - Regex: mengira semua kata `FROM` berarti baca. Jadi `DELETE FROM sesi` dicatat `sesi D` dan juga `sesi R`. Yang `R` salah.
   - Parser: hanya `sesi D`.
   - Kenapa beda: parser mengenali statement ini sebagai `DELETE` dari bentuk pohonnya (Bab 5), lalu memberi `D`. Regex hanya melihat kata `FROM`, tanpa tahu statement itu apa.

3. **Statement yang salah tulis tetap dihitung**
   (`campuran_error.sql` baris 4)
   - SQL: `SELECT id nama, FROM pesanan;`
   - Regex: tetap mencatat `pesanan R`, padahal statement ini salah (setelah koma harus ada nama kolom lagi).
   - Parser: melaporkan satu error dan statement ini tidak dihitung. Statement sesudahnya tetap diproses.
   - Kenapa beda: parser memeriksa aturan penulisan (grammar), sedangkan regex hanya mencari pola kata. Setelah error, parser membuang token sampai tanda `;` lalu lanjut (panic mode, Bab 6), jadi satu kesalahan tidak merusak statement lain.

## 3. Batas pendekatan kami

Minimal tiga hal yang **tidak bisa** ditangani dengan benar oleh tool ini meskipun semua bug
sudah diperbaiki. Untuk tiap batas: contoh SQL atau situasinya, akibatnya pada CRUD matrix,
dan informasi apa yang dibutuhkan untuk mengatasinya.

1. **SQL Dinamis (Dynamic SQL / Query dari Variabel)**
   - **Contoh SQL / Situasi:** Query yang dirangkai dari string/variabel, contohnya `EXEC('UPDATE ' + @nama_tabel + ' SET status = ''LUNAS''')`.
   - **Akibat pada CRUD Matrix:** Karena tool kita bekerja secara *statis* (hanya membaca teks SQL sebelum dijalankan), nama tabel di dalam variabel `@nama_tabel` tidak bisa ditebak oleh parser. Akibatnya, perintah `UPDATE` ini **sama sekali tidak tercatat** di matriks CRUD.
   - **Informasi yang Dibutuhkan:** Perlu log eksekusi query saat aplikasi berjalan (*runtime query log*) atau analisis pada kode program aplikasi tempat string SQL tersebut dirangkai.

2. **Penggunaan Tanda Bintang (`SELECT *`) Tanpa Skema Database**
   - **Contoh SQL / Situasi:** Query `SELECT * FROM pelanggan p JOIN pesanan o ON p.id = o.pelanggan_id`.
   - **Akibat pada CRUD Matrix:** Tool kita hanya tahu kalau tabel `pelanggan` dan `pesanan` dibaca (**Read/R**), tapi **tidak tahu kolom apa saja** yang sebenarnya diambil. Kalau aplikasi butuh rincian akses sampai tingkat nama kolom (*column-level CRUD*), informasi ini bakal hilang.
   - **Informasi yang Dibutuhkan:** Butuh skema struktur database (DDL / metadata tabel) untuk memecah tanda bintang `*` menjadi daftar nama kolom aslinya (`id`, `nama`, `tanggal`, dll).

3. **Panggilan Stored Procedure atau Database View**
   - **Contoh SQL / Situasi:** Perintah `CALL sp_proses_bayar()` atau `SELECT * FROM v_laporan_penjualan`.
   - **Akibat pada CRUD Matrix:** Tool kita cuma bisa mencatat nama pemanggilan prosedur `sp_proses_bayar` atau view `v_laporan_penjualan`. Operasi ke tabel asli di dalam prosedur tersebut (misalnya di dalam `sp_proses_bayar` sebenarnya ada perintah `UPDATE pesanan` dan `INSERT pembayaran`) **tidak terdeteksi**.
   - **Informasi yang Dibutuhkan:** Perlu berkas kode sumber (DDL) dari Stored Procedure atau View tersebut supaya parser bisa masuk dan membedah query yang ada di dalamnya secara rekursif.

## 4. Pembagian kerja

**Pembagian awal.** Kami membagi kerja berdasarkan urutan pipeline. Firon Fariz S mengerjakan bagian awal, yaitu lexer dan parser. Raza Mulki F mengerjakan bagian lanjutan, yaitu resolver, analyzer, dan pelabelan data. Kami memilih pembagian ini karena
bug di lexer dan parser akan menurunkan kesalahan ke tahap berikutnya. Dengan begitu, lexer dan parser diperbaiki lebih dulu.

**Yang dikerjakan Firon Fariz S.**
- Memperbaiki enam bug di lexer dan parser (keyword huruf kecil, `''` di string, `<>`,
  presedensi AND/OR, error recovery, dan `LEFT OUTER JOIN`).
- Menyelesaikan TODO T1 (`INSERT ... SELECT`) dan T3 (komentar blok).
- Menulis test regresi dan kasus tepi untuk bagian tersebut.

**Yang dikerjakan Raza Mulki F.**
- Memperbaiki empat bug di resolver dan analyzer: `_lookup` mencari alias dari scope
  terluar (bukan terdalam), `_delete` lupa menutup scope dengan `_pop()`, subquery di
  `UPDATE` ditandai `U` (seharusnya `R`), dan `INSERT ... SELECT` membuat resolver dan
  analyzer crash karena `Insert.values` bernilai `None`.
- Menyelesaikan TODO T2 (resolusi kolom tanpa qualifier di resolver).
- Melabeli `ground_truth.csv` untuk `audit.sql` dan `pemeliharaan.sql` (17 triple) dari
  SPESIFIKASI bagian 5, lalu menjalankan `evaluate.py`.
- Menulis test regresi dan kasus tepi untuk bagian resolver dan analyzer.
- Menulis LAPORAN_BUG untuk bug di bagian tersebut.

**Yang dikerjakan bersama.**
- Membaca `SPESIFIKASI.md` dan menjalankan semua perintah awal (pytest, CLI, `--ast`).
- Menyusun dokumen: laporan bug, kartu desain, laporan akhir, dan log AI.
- Latihan demo.

**Cara kami memastikan keduanya paham seluruh kode.**
- Setelah selesai satu bagian, kami saling menjelaskan hasilnya. 
- Kami saling membaca kode sebelum commit. 
- Kami bertukar peran untuk memeriksa ulang bagian satunya.
- Saat latihan demo, kami saling bertanya seperti dosen: "kenapa test ini gagal di kode lama?" dan "apa yang dihasilkan lexer untuk input ini?".
- Kedua anggota punya commit di riwayat Git.
