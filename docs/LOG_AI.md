# Log Penggunaan AI

Catat setiap penggunaan AI atau coding agent yang memengaruhi kode atau laporan.

| No | Siapa | Prompt / tugas (ringkas) | Hasil: diterima, diubah, atau ditolak | Alasan | Cara verifikasi |
| --- | --- | --- | --- | --- | --- |

| 1 |Firon Fariz S |Bagaimana cara kita bisa memperhatikan bug yang ada didalam program sehingga lebih mudah dipahami dan juga dianalisis ketika kita diminta untuk scanning dan memperbaiki bug tersebut sesuai dengan spesifikasi yang diberikan oleh client |diterima |Karena AI tersebut membantu saya dalam mempermudah mencari bug dimana AI selalu menitik beratkan semua program ke spesifikasi dari program tersebut dimana spesifikasi merupakan kunci acuan kebenaran (ground truth) dari proyek ini sehingga kalo semisalkan sudah tidak sesuai maka itu sudah terhitung menjadi bug. Jadi disarankan untuk melakukan test satu persatu sesuai  dengan fungsi yang ada di program crud lalu dicocokan dengan input dan output yang ada di test.py | lakukan pengecekan secara berkala satu persatu dari setiap test jika ada bagian yang mengalami error di terminal maka itu bisa dikatakan bug ketika dicek error pada bagian tersebut kita perlu melihat spesifikasi dari client ketika itu melanggar spesifikasi maka perlu dilakukan perbaikan pada logika pemrogramannya agar sesuai dengan spesifikasi client |

| 2 | Firon Fariz S | Apa itu kasus tepi dan mengapa ia sangat penting untuk test tambahan | diterima | karena dari kasus tepi input yang muncul biasanya berada di batas atau di luar kondisi normal, yaitu situasi yang jarang terpikir saat menulis kode, sehingga bug sering bersembunyi di sana. | Coba berpikir secara logika lalu lakukan prompting apakah kasus yang saya pikirkan ini salah satu dari kasus tepi atau itu memang kasus normal yang sudah sering terjadi |

|3| Firon Fariz S|Jelaskan mengenai tugas besar PLP berikut karena saya masih merasa ambigu dengan cara pengerjaan tugas besar tersebut serta langkah langkah praktis dalam melakukan modul ini |diterima|karena saya dan rekan saya masih bingung dalam pembagian karena disarankan untuk tidak membagi modul sama rata melainkan untuk dikerjakan secara bertahap dan bersama sedangkan kami tidak selalu bersama jadi lebih baiknya bagaimana|dicocokan dengan pembagian modul dan juga spesifikasinya |

| 4 | Firon Fariz S | Saran test tambahan untuk mengetest bug dan juga mengetahui apakah bug itu berhasil diperbaiki atau tidak | diterima | saya masih bingung ingin menambahkan test apalagi karena saya sudah melihat ada test khusu lexer dll sehingga saya belum bisa berpikir secara kritis bagaimana jenis test yang perlu dilakukan apalagi test kasus tepi | melihat test yang sudah ada sebelumnya lalu bertanya kepada AI apakah test yang saya pikirkan ini termasuk test baru dan juga lebih kritis dari test yang sebelumnya sudah ada |

| 5 | Firon Fariz S | Perbaikan bug dimana pengecekan sebuah token jika dia tidak uppercase| diterima| keyword harus huruf besar jika misalkan ada select dengan huruf kecil dia akan bingun masuk kemana | mengubah semua huruf menjadi kapita atau upper case setelah itu dilihat konteksnya apakah dia masuk ke keywords atau identifier |

| 6 | Firon Fariz S | Minta saran pembagian kerja berdua | diterima | AI menyarankan hulu (lexer, parser) vs hilir (resolver, analyzer) plus kami tetap pair programming sesuai saran ibu untuk dikerjakan bersama | Saling menjelaskan bagian masing-masing dan melakukan commit dari kedua anggota di Git |

| 7 | Firon Fariz | Analisis lexer.py: `''` di dalam string | diterima | AI menunjuk `_string` berhenti di kutip pertama tanpa lookahead | Test `'O''Brien'` menjadikan hasil token menjadi O'Brein |

| 8 | Firon Fariz S | Analisis lexer.py: `<>` terpecah | diterima | AI menunjuk pelanggaran maximal munch pada cabang `<` | Test `a<>b` gagal lalu lulus [TEMPEL hasil]; dicek juga `<=`, `>=`, `!=` |

| 9 | Firon Fariz S | Implementasi komentar blok `/* */` | diterima | dari hasil prompt saya AI memberi kode dengan analogi kami cek penutup harus pasangan `*/`, bukan `*` saja | Test: berisi `*`, `/*/` dan jika tidak tertutup maka ia masuk menjadi LexError |

| 10 | Firon| Menganalisis error LexError: komentar blok belum didukung dari traceback | diterima | Perlu memahami cara membaca alur Traceback Python dari bawah ke atas. | Cara verifikasi | Membaca pesan error dan mencocokkannya dengan baris raise LexError pada crud/lexer.py |

**Refleksi (3-5 kalimat).** Di bagian mana AI paling membantu? Di mana AI keliru atau
menyesatkan, dan bagaimana kalian mengetahuinya?
