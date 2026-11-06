# Laporan Bug

Bug 1 sampai 6 ada di lexer dan parser. Bagian "Akar masalah" ditulis berdasarkan
pemahaman kami terhadap Crafting Interpreters. Penggunaan AI dicatat di `docs/LOG_AI.md`.

---

## Bug 1: Keyword huruf kecil tidak dikenali

**Ditemukan oleh:** Firon Fariz S · **Diperbaiki oleh:** Firon Fariz S

**Gejala.** Input `select a from t where a = 1` menghasilkan token IDENT semua. Akibatnya
parser menganggap `where` sebagai alias tabel `t`. Padahal SPESIFIKASI.md bagian 2.2
menyatakan keyword tidak peka huruf besar/kecil dan nilainya selalu huruf besar.

**Reproduksi minimal.**
```sql
select 1 from t where a = 1
```

**Akar masalah.** Fungsi `_word` mengecek `text in KEYWORDS` dengan teks persis seperti
yang ditulis. Isi KEYWORDS huruf besar semua, jadi `select` tidak pernah cocok. Menurut
Bab 4, keyword dibaca seperti identifier biasa, lalu dicocokkan ke tabel keyword. Pencocokan
itu harus memakai bentuk yang sudah dinormalisasi (huruf besar). Gejalanya muncul di parser:
`where` bertipe IDENT, dan `_alias()` menerima IDENT sebagai alias, sehingga `where` tertelan.
Jadi sumber salahnya di lexer, tetapi parser yang kelihatan error.

**Perbaikan.** File `crud/lexer.py`, fungsi `_word`. Teks diubah ke huruf besar sebelum
dicek ke KEYWORDS. Token keyword memakai nilai huruf besar, sedangkan IDENT tetap memakai
teks asli. Alternatif: mengubah isi KEYWORDS menjadi huruf kecil. Tidak kami pilih karena
KEYWORDS termasuk API publik (spek bagian 7) dan nilai token harus huruf besar.

**Test regresi.** `test_regresi_lexer_keyword_uppercase`

Sebelum perbaikan (gagal):
```text
AssertionError: assert 'select' == 'SELECT'
```
Sesudah perbaikan (lulus):
```text
test_regresi_lexer_keyword_uppercase ... PASSED
```

**Peran AI.** AI membantu menunjuk bahwa lexer memperlakukan keyword huruf kecil sebagai
IDENT sehingga `where` tertelan sebagai alias. Kami memverifikasi dengan test di atas yang
gagal sebelum perbaikan dan lulus sesudahnya.

---

## Bug 2: `''` di dalam string memecah token

**Ditemukan oleh:** Firon Fariz S · **Diperbaiki oleh:** Firon Fariz S

**Gejala.** `'O''Brien'` menjadi dua token STRING (`O` dan `Brien`). Spek 2.4 meminta
satu token bernilai `O'Brien`.

**Reproduksi minimal.**
```sql
select 'O''Brien'
```

**Akar masalah.** Kode lama menganggap kutip pertama yang ditemui pasti kutip penutup.
Padahal kutip bisa berarti penutup, atau bisa separuh dari tanda `''`. Untuk membedakannya
lexer perlu melihat satu karakter ke depan (`_peek`), seperti `_peek(1)` yang dipakai pada
angka desimal. Tanpa itu, string terpotong, lalu dua token STRING berurutan membuat
parser salah baca atau error.

**Perbaikan.** File `crud/lexer.py`, fungsi `_string`. Saat bertemu `'`, jika karakter
berikutnya juga `'`, keduanya dikonsumsi dan satu `'` ditambahkan ke nilai string.
Alternatif: memproses `''` di parser. Tidak kami pilih karena mengolah isi literal adalah
tugas lexer.

**Test regresi.** `test_regresi_lexer_string_quote_escape`

Sebelum perbaikan (gagal):
```text
AssertionError: assert len(toks) == 1 (ditemukan 2 token: 'O' dan 'Brien')
```
Sesudah perbaikan (lulus):
```text
test_regresi_lexer_string_quote_escape ... PASSED
```

**Peran AI.** AI membantu merancang penggunaan lookahead di `_string`. Kami memverifikasi
dengan test yang memastikan nilai token akhir tepat `O'Brien`.

---

## Bug 3: `<>` terpecah menjadi `<` dan `>`

**Ditemukan oleh:** Firon Fariz S · **Diperbaiki oleh:** Firon Fariz S

**Gejala.** `a <> b` menghasilkan token `<` lalu `>`, sehingga parser error. Spek 2.5
meminta lexer mengambil operator terpanjang yang cocok.

**Reproduksi minimal.**
```sql
select 1 from t where a <> b
```

**Akar masalah.** Setelah membaca `<`, kode lama hanya mencoba mencocokkan `=`, jadi `>`
dibiarkan menjadi token berikutnya. Aturan yang benar adalah *maximal munch* (Bab 4):
kalau beberapa lexeme cocok, ambil yang paling panjang. Cabang `<` harus mencoba `<=` dan
`<>`. Akibatnya, parser membaca `a <` lalu menemukan `>` di tempat yang seharusnya ada
ekspresi, dan melaporkan error.

**Perbaikan.** File `crud/lexer.py`, cabang `<`: ditambahkan pencocokan `>` sehingga
menghasilkan token `<>`. Alternatif: membiarkan lexer apa adanya dan menggabungkan `<` dan
`>` di parser. Tidak kami pilih karena itu menambal gejala di tahap yang salah.

**Test regresi.** `test_edge_case_lexer_maximal_munch_operator`

Sebelum perbaikan (gagal):
```text
AssertionError: assert '<>' in ops (ditemukan operator '<' dan '>')
```
Sesudah perbaikan (lulus):
```text
test_edge_case_lexer_maximal_munch_operator ... PASSED
```

**Peran AI.** AI membantu memeriksa cabang `<` dan menjelaskan prinsip maximal munch.
Kami memverifikasi dengan test token `<>`.

---

## Bug 4: AND dan OR berada di satu tingkat presedensi

**Ditemukan oleh:** Firon Fariz S · **Diperbaiki oleh:** Firon Fariz S

**Gejala.** `a=1 OR b=2 AND c=3` terbaca sebagai `(a=1 OR b=2) AND c=3`. Menurut spek 3.1,
AND lebih kuat daripada OR, jadi yang benar adalah `a=1 OR (b=2 AND c=3)`.

**Reproduksi minimal.**
```sql
select 1 from t where a=1 or b=2 and c=3
```

**Akar masalah.** Kode lama memakai satu loop untuk AND dan OR, sehingga keduanya dianggap
setara dan dikelompokkan dari kiri. Di recursive descent (Bab 6), presedensi ditentukan oleh
urutan pemanggilan fungsi: operator yang lebih lemah ada di fungsi luar dan memanggil fungsi
untuk operator yang lebih kuat. Jadi `_or` harus memanggil `_and`, dan `_and` memanggil
`_not`. Bug ini berbahaya karena hasilnya tetap sah secara sintaks dan tidak ada error,
tetapi maknanya berubah diam-diam, dan pohon yang diterima resolver ikut salah.

**Perbaikan.** File `crud/parser.py`: `_logical` dipecah menjadi `_or` (memanggil `_and`)
dan `_and` (memanggil `_not`). Alternatif: precedence climbing dengan tabel prioritas.
Tidak kami pilih karena bagian parser lainnya memakai pola satu fungsi per tingkat.

**Test regresi.** `test_regresi_parser_and_lebih_kuat_dari_or`

Sebelum perbaikan (gagal):
```text
AssertionError: assert w.op == 'OR' (ditemukan w.op == 'AND')
```
Sesudah perbaikan (lulus):
```text
test_regresi_parser_and_lebih_kuat_dari_or ... PASSED
```

**Peran AI.** AI membantu memecah `_logical` menjadi `_or`, `_and`, dan `_not` sesuai pola
Bab 6. Kami memverifikasi bentuk pohon dengan assert `w.op == "OR"` dan
`w.right.op == "AND"`.

---

## Bug 5: Error recovery membuang semua token sampai akhir file

**Ditemukan oleh:** Firon Fariz S · **Diperbaiki oleh:** Firon Fariz S

**Gejala.** Satu statement yang rusak membuat semua statement valid sesudahnya hilang.
Spek bagian 6 meminta token dibuang sampai dan termasuk `;` berikutnya, lalu parsing lanjut.

**Reproduksi minimal.**
```sql
select from t; select 1 from x;
```

**Akar masalah.** `_synchronize` lama berisi `while not self._at_end(): self._advance()`,
yaitu membuang semua token sampai EOF. Menurut Bab 6 (panic mode), setelah error parser
membuang token sampai titik sinkronisasi yang aman, lalu melanjutkan. Menurut spek, titik
itu adalah `;` dan `;` ikut dibuang. Karena kode lama tidak punya titik berhenti, fungsi
yang seharusnya memulihkan parser malah membuatnya berhenti. Hasilnya satu error dan tidak
ada statement lanjutan.

**Perbaikan.** File `crud/parser.py`, fungsi `_synchronize`: token dimajukan sampai token
`;` terkonsumsi. Alternatif: berhenti di keyword awal statement (SELECT, INSERT, dan
seterusnya). Tidak kami pilih karena spek menetapkan `;` sebagai titik sinkronisasi.

**Test regresi.** `test_edge_case_parser_panic_mode_recovery` dan
`test_regresi_parser_panic_mode_dua_statement_rusak`

Sebelum perbaikan (gagal):
```text
AssertionError: assert len(script.statements) == 1 (ditemukan 0 statement valid)
```
Sesudah perbaikan (lulus):
```text
test_regresi_parser_panic_mode_dua_statement_rusak ... PASSED
```

**Peran AI.** AI membantu menunjuk bahwa `_synchronize` tidak punya titik berhenti dan
menyarankan berhenti di `;`. Kami memverifikasi dengan test satu error dengan satu statement
valid sesudahnya, dan dua statement rusak berturut-turut.

---

## Bug 6: `LEFT OUTER JOIN` ditolak

**Ditemukan oleh:** Firon Fariz S · **Diperbaiki oleh:** Firon Fariz S

**Gejala.** `LEFT OUTER JOIN` menghasilkan error "diharapkan JOIN, ditemukan 'OUTER'",
padahal grammar menerima `"LEFT" [ "OUTER" ]`.

**Reproduksi minimal.**
```sql
select 1 from a left outer join b on a.id = b.id
```

**Akar masalah.** Setelah membaca `LEFT`, kode lama langsung memanggil
`_expect_kw("JOIN")`. Grammar punya bagian opsional `[ "OUTER" ]`, dan di recursive descent
bagian opsional ditulis sebagai `if match(...)`. Bagian itu tidak ada di kode, jadi fungsi
`_join` menerima lebih sedikit daripada grammar. Akibatnya SQL yang sah ditolak (false
rejection). Prinsipnya, setiap fungsi parser harus menerima tepat bahasa yang ditulis di
grammar (Bab 6).

**Perbaikan.** File `crud/parser.py`, fungsi `_join`: setelah `LEFT`, `OUTER` dicocokkan
secara opsional. `OUTER` tanpa `LEFT` tetap ditolak sesuai grammar.

**Test regresi.** `test_regresi_parser_left_outer_join`

Sebelum perbaikan (gagal):
```text
ParseError: Baris 1, kolom 23: diharapkan JOIN, ditemukan 'OUTER'
```
Sesudah perbaikan (lulus):
```text
test_regresi_parser_left_outer_join ... PASSED
```

**Peran AI.** AI membantu menunjuk bahwa `_join` tidak menangani `OUTER` opsional.
Kami memverifikasi bahwa `LEFT OUTER JOIN` kini ter-parse sebagai `Join(kind='LEFT')`.

## Fitur yang dilengkapi (bukan bug)

- **T1: `INSERT ... SELECT` (parser).** [ISI singkat: apa yang diubah di `_insert`.]
  Test: `test_fitur_insert_select_dukungan_spesifikasi`.
- **T3: komentar blok `/* ... */` (lexer).** Penutup dicari sebagai pasangan `*/`. Komentar
  yang tidak ditutup menjadi LexError, dan komentar boleh berisi `*`.
  Test: `test_regresi_lexer_komentar_blok_dengan_bintang_dan_tak_tertutup`.