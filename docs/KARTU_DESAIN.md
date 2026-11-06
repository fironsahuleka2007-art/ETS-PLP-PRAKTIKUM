# Kartu Desain

Tuliskan lima keputusan desain penting dalam pekerjaan kalian. Untuk tiap keputusan, sebutkan
alternatif yang ditolak dan alasannya. Contoh topik (boleh memilih yang lain):

- bagaimana parser membedakan `*` sebagai "semua kolom" dan sebagai perkalian;
- di mana dan bagaimana presedensi `AND`/`OR` dinyatakan;
- mengapa error recovery berhenti di `;`, bukan di keyword `SELECT` berikutnya;
- urutan pencarian scope dan akibatnya pada shadowing serta correlated subquery;
- mengapa kolom tanpa qualifier hanya dilihat di scope terdalam, dan apa kelemahannya;
- bagaimana implementasi `INSERT ... SELECT` atau komentar blok kalian.


| No | Keputusan | Alternatif yang Ditolak | Alasan |
| --- | --- | --- | --- |
| 1 | Menentukan urutan presedensi `AND`/`OR` lewat pemanggilan fungsi berantai (`_or()` memanggil `_and()`). | Memakai tabel presedensi operator yang kompleks (*Pratt Parser*). | Tata bahasa SQL di spesifikasi ini masih tergolong simpel. Pakai pemanggilan fungsi rekursif biasa jauh lebih gampang dibaca, dicoding, dan langsung pas sama struktur parser yang udah dibuat dari awal. |
| 2 | Langsung menghapus/mengabaikan komentar blok `/* ... */` di modul Lexer. | Mengirim komentar sebagai token `COMMENT` ke Parser baru dihapus di sana. | Komentar sama sekali nggak dipakai buat ngebentuk pohon AST. Kalau dibuang dari awal pas pembacaan token (Lexer), Parser tinggal terima token bersih dan kodenya nggak makin ribet. |
| 3 | Kalau ada query yang *error*, parser loncat/melewati token sampai ketemu titik koma (`;`) (Panic Mode). | Loncat langsung ke kata kunci query berikutnya (seperti `SELECT` atau `INSERT`). | Titik koma (`;`) itu pemisah antar-query yang paling pasti. Kalau kita loncat ke kata `SELECT`, ditakutkan `SELECT` itu ternyata cuma subquery di dalam query yang lagi rusak, jadi malah bikin error parser makin ngacak. |
| 4 | Mengubah semua keyword SQL jadi huruf besar (UPPERCASE) sekaligus di tingkat Lexer. | Mengecek `.upper()` satu per satu di setiap fungsi Parser. | Mengubah sekali di awal jauh lebih efisien. Parser nggak perlu bolak-balik ngubah string jadi huruf besar tiap kali mau nyocokin kata kunci, jadi kodenya lebih rapi dan bebas dari bug lupa kapitalisasi. |
| 5 | Membedakan tanda `*` (perkalian vs `SELECT *`) berdasarkan alur fungsi grammar yang lagi jalan (`_select_list` vs `_multiplicative`). | Pakai variabel penanda global (*global flag*) di dalam kelas Parser. | Mengandalkan posisi fungsi jauh lebih aman daripada variabel penanda global yang riskan bikin bug *side-effect*. Jadi pas di posisi daftar kolom dibaca sebagai `ast.Star()`, sedangkan pas di perhitungan matematika dibaca sebagai operator perkalian `*`. |
