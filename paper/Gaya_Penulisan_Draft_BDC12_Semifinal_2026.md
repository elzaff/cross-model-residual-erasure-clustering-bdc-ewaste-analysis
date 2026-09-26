# Catatan Gaya Penulisan Draft BDC12 Semifinal Satria Data 2026

Sumber: [Draft BDC12 Semifinal Satria Data 2026.docx](<Draft BDC12 Semifinal Satria Data 2026.docx>). Catatan ini mendeskripsikan **cara naskah menyusun dan menyampaikan penelitian**, bukan mengadopsi metode, angka, atau kesimpulan HyMVD sebagai hasil penelitian lain. Pengamatan struktur, format, dan persamaan berasal dari isi serta struktur Word; tampilan halaman tidak dirender ulang.

## 1. Watak umum naskah

Naskah berbentuk karya ilmiah kompetisi yang formal, padat, dan berbasis bukti. Narasi utamanya bukan sekadar “metode kami lebih baik”, melainkan: **data punya masalah tertentu → analisis awal memperlihatkan masalah itu → desain metode mengikuti temuan → hasil diuji dengan pembanding kuat → keunggulan dan batasnya dijelaskan**. Penulis cenderung menahan klaim sebab-akibat ketika eksperimen belum memisahkan kontribusi tiap komponen.

Suara penulis impersonal: “penelitian ini”, “hasil menunjukkan”, “dilakukan”, “digunakan”, “diperoleh”. Tidak mengandalkan cerita personal atau promosi. Istilah teknis bahasa Inggris dipertahankan ketika merupakan nama metode/metrik, sering dicetak miring dalam badan teks; penjelasan hubungan antarkonsep tetap berbahasa Indonesia.

## 2. Arsitektur dokumen

| Bagian | Fungsi retoris dan pola isi |
|---|---|
| Sampul | Identitas kompetisi/kode tim, judul lengkap, elemen grafis. Judul muncul lagi sebelum abstrak. |
| Abstrak dan kata kunci | Satu paragraf panjang yang memuat masalah, tujuan, data dan model, alasan metode, pipeline, hasil kuantitatif utama, pembanding, temuan konseptual, dan simpulan. Lima kata kunci sesudahnya. |
| 1. Pendahuluan | Latar belakang → rumusan masalah → batasan masalah → manfaat penelitian. |
| 2. Metodologi | Ikhtisar tujuh tahap, dataset/protokol, EDA, representasi multi-view, pembelajaran hiperbolik, penemuan komunitas, validasi, baseline, dan validasi eksternal. |
| 3. Hasil dan Pembahasan | Mengikuti urutan metode: EDA, representasi, taksonomi, validitas/baseline, transfer eksternal, novelty/error, lalu sintesis umum. |
| 4. Penutup | Kesimpulan merangkum jawaban penelitian dan angka utama; saran menyebut eksperimen lanjutan yang spesifik. |
| Referensi dan Lampiran | Daftar pustaka alfabetis dengan DOI/URL; lampiran sesudah referensi. |

Bab utama memakai judul kapital seperti **PENDAHULUAN**, subbab bernomor `1.1`, dan sub-subbab `2.4.1`. Abstrak, referensi, dan lampiran berdiri di luar penomoran subbab. Struktur ini memberi pembaca jalur yang sama dari pertanyaan ke metode lalu bukti.

## 3. Alur argumen per bagian

### Abstrak

Urutannya cukup tetap: urgensi e-waste → tujuan *unsupervised* → ukuran data dan tiga model → hasil EDA sebagai alasan desain → cara pembelajaran dan pengelompokan → keluaran taksonomi → angka transfer eksternal terhadap baseline → nuansa hasil → simpulan. Angka pembanding disajikan berpasangan, misalnya 91,1% versus 62,4% dan selisih 28,7 *percentage points*. Abstrak sudah mengungkap temuan utama, bukan hanya janji penelitian.

### Pendahuluan

Empat langkahnya jelas:

1. Mulai dari masalah makro yang terukur: volume e-waste dan persentase pengelolaan formal, disertai sumber.
2. Tunjukkan pekerjaan terdahulu beserta hasilnya, lalu batasnya bagi pertanyaan riset ini: deteksi/klasifikasi *supervised* memerlukan kelas dan label yang sudah ditetapkan.
3. Uraikan alasan data tanpa label lebih rumit: kemiripan bisa berasal dari perangkat, bentuk, komponen, fungsi, atau konteks foto.
4. Perkenalkan HyMVD sebagai jawaban terhadap kebutuhan multi-view, multi-scale, dan hierarki; sebut rencana evaluasi sejak awal.

Rumusan masalah berisi empat pertanyaan berurutan: apakah struktur visual ada, bagaimana menyatukan representasi, bagaimana membentuk taksonomi, dan apakah struktur bertahan secara semantik di data eksternal. Batasan masalah memisahkan input, peran label, penamaan pasca-clustering, serta penggunaan data eksternal. Manfaat dibagi menjadi metodologis dan praktis, dengan bahasa “dapat menjadi dasar”, bukan klaim sistem siap pakai.

### Metodologi

Bagian metode dimulai dengan **mengapa** pilihan desain masuk akal berdasarkan EDA, baru **bagaimana** langkah teknisnya dijalankan. Peta tujuh tahap dan diagram alur muncul sebelum rincian. Setiap subbagian memiliki satu tugas: karakter data, diagnostik, ekstraksi fitur, pembelajaran, fusi, komunitas, validasi, atau pembanding.

Pola paragraf metode: nyatakan operasi → sebut input/representasi → jelaskan tujuan operasi → jelaskan batas protokol atau metrik yang menilainya. Contoh: Hopkins statistic dipakai untuk kecenderungan clustering; *controlled downsampling* untuk memisahkan dampak resolusi dari gaya sumber; Jaccard tetangga untuk melihat komplementaritas model. Istilah seperti Lorentz manifold, exponential/logarithmic map, Fréchet mean, InfoNCE, HHSW, dan Leiden dijelaskan dalam relasi ke fungsi masing-masing, bukan hanya didaftar.

Persamaan Word digunakan pada definisi representasi, geometri, objektif, jadwal pelatihan, dan fusi. Teks sebelum/sesudah persamaan menjelaskan peran variabel dan operasi. Berkas memuat 13 objek matematika OOXML; sebagian simbol tidak muncul dalam ekstraksi teks biasa, sehingga pembacaan rumus harus melalui Word/objek persamaan.

Protokol evaluasi ditegaskan berulang: data utama untuk *discovery*; label kategori tidak membentuk cluster; interpretasi semantik setelah partisi dibekukan; data eksternal hanya untuk validasi *frozen* tanpa *retraining*, *reclustering*, atau *semantic remapping*. Pengulangan ini berfungsi menjaga batas klaim dan mencegah dugaan *information leakage*.

Baseline memakai representasi dasar yang sama dan pipeline pembanding yang serius. Indikator internal tidak direduksi menjadi satu skor: stabilitas seed, perubahan resolusi/parameter, tetangga, dukungan HDBSCAN, dan hubungan parent-child dibaca bersama. Evaluasi eksternal menggunakan metrik transfer semantik, novelty, serta audit kesalahan.

### Hasil dan pembahasan

Setiap hasil umumnya mengikuti pola **temuan numerik → interpretasi → kaitan dengan keputusan metode/literatur → batas interpretasi**. Contoh §3.1: Hopkins ≈0,80 mendukung struktur nonacak; Jaccard tetangga yang rendah mendukung informasi antarmodel yang komplementer; downsampling dengan Recall@1 ≈97–98% melemahkan penjelasan bahwa pemisahan hanya akibat resolusi.

Bagian hasil tidak memaksa semua metrik menguntungkan usulan. Pada §3.4 baseline Euclidean diakui lebih stabil dalam beberapa indikator, sementara HyMVD lebih baik pada indikator lain. Pada §3.5 peningkatan Micro/Macro Top-1 dijelaskan bersama pengecualian kelas Mobile. Pada §3.6 novelty dipisahkan dari *distribution shift*, lalu kesalahan dirinci menurut pasangan kelas, jumlah kasus, dan penyebab visualnya.

Pembahasan umum menyatukan hasil menjadi pesan yang lebih luas: stabilitas internal penting tetapi tidak cukup untuk menjamin transfer semantik; struktur laten dan identitas semantik tidak selalu identik; sinyal jarak Euclidean dan margin family hiperbolik dapat saling melengkapi. Kalimat pembatas penting: perbandingan dua pipeline penuh **tidak membuktikan** peningkatan berasal dari curvature hiperbolik saja (§3.5). Ini contoh disiplin klaim yang layak dipertahankan.

### Penutup

Kesimpulan kembali ke urutan pertanyaan penelitian: struktur data, integrasi multi-view, bentuk taksonomi, stabilitas/transfer eksternal. Hasil kunci diulang secukupnya dengan angka. Saran bukan “perlu penelitian lebih lanjut” yang umum; naskah menyebut dataset lebih besar dan beragam, *geometry-only ablation*, serta uji kecepatan/komputasi dan objek baru pada sistem nyata. Terdapat satu komentar redaksi di DOCX yang secara eksplisit meminta kesimpulan menjawab rumusan masalah.

## 4. Pilihan bahasa dan nada

- **Formal, deskriptif, berhati-hati.** Kata seperti “menunjukkan”, “mengindikasikan”, “mendukung”, “konsisten dengan”, dan “dapat” menghubungkan bukti ke interpretasi. Hubungan sebab-akibat yang belum diisolasi tidak dinyatakan sebagai kepastian.
- **Bahasa Indonesia sebagai kerangka, istilah internasional untuk konsep baku.** Misalnya *foundation model*, *multi-view*, *neighborhood*, *semantic transfer*, *frozen*, dan *out-of-taxonomy*. Akronim dijabarkan saat awal, lalu dipakai konsisten: EDA, MLP, HDBSCAN, AUROC, AUPRC.
- **Paragraf membawa satu langkah alasan.** Awal paragraf menyatakan temuan/tujuan, tengah memuat angka atau prosedur, akhir menyatakan arti atau transisi. Penghubung yang sering dipakai: “Oleh karena itu”, “Namun”, “Sebaliknya”, “Dengan demikian”, “Selain itu”, “Secara keseluruhan”.
- **Angka terikat pada pembanding dan satuan.** Desimal memakai koma (`0,922`, `91,1%`), ribuan memakai titik (`4.162`), dan selisih persentase disebut *percentage points* bila memang selisih dua persentase. Banyak pernyataan menyebut ukuran sampel atau jumlah kasus.
- **Nama metode tepat dan peran tiap metode dibedakan.** Leiden membentuk komunitas utama; HDBSCAN memberi bukti densitas; baseline Euclidean membandingkan; validasi eksternal menguji transfer. Tidak menyamakan label pasca-hoc dengan input pelatihan.
- **Sitasi dekat klaim yang didukung.** Pola penulis–tahun dalam kalimat dan tanda kurung, misalnya `Im et al. (2025)` atau `(Mettes et al., 2024)`. Literatur dipakai untuk landasan geometri, metrik, dan batas definisi OOD/open-set; hasil eksperimen sendiri ditopang angka/tabel/gambar naskah.

## 5. Tabel, gambar, dan referensi silang

- Gambar bernomor per bab: `Gambar 2.1`, `Gambar 3.5`. Teks memperkenalkan gambar sebelum/di sekitar tampilannya; caption singkat menerangkan isi. Gambar mencakup alur metode, contoh variasi data, arsitektur, distribusi, retrieval, proyeksi/taksonomi, perbandingan kelas, dan contoh salah klasifikasi.
- Tabel bernomor per bab: `Tabel 3.1` sampai `Tabel 3.3`. Caption muncul sebelum tabel. Kolom lazimnya **indikator/metrik → baseline → metode usulan** agar pembandingan dapat dibaca langsung.
- Grafik dan tabel tidak dibiarkan berbicara sendiri. Paragraf setelahnya menyebut nilai penting, menjelaskan arah perbedaan, lalu membahas mengapa itu relevan. Per-kelas dan kasus gagal dipakai untuk menguji kesimpulan agregat.
- Referensi berurutan alfabetis dengan nama penulis, tahun, judul, venue/penerbit bila tersedia, dan DOI/URL. Secara umum menyerupai gaya author–date/APA; formatnya belum sepenuhnya seragam, jadi cek aturan sitasi lomba saat membuat naskah final.

## 6. Format Word yang teramati

- Kertas A4 potret, margin kiri/kanan/atas/bawah sekitar **3 cm**; dua section, dengan sampul dipisahkan dari badan tulisan.
- Judul sampul tebal dan rata tengah, **18 pt**; judul diulang rata tengah sebelum abstrak. Heading bab kapital dan tebal, subbab bernomor dan tebal, sub-subbab bernomor dengan penekanan lebih ringan.
- Ukuran teks bawaan **12 pt**, spasi baris bawaan **1,5**, paragraf umumnya rata kiri-kanan dan banyak memakai inden baris pertama. Istilah asing banyak diberi *italic*; hasil/metode tertentu diberi **bold** secara selektif.
- Font tidak dikunci seragam dalam style `Normal`: tema Word menunjuk Calibri, sedangkan beberapa run ditetapkan Times New Roman 12 pt. Jika membuat dokumen baru, tetapkan satu font sesuai panduan lomba alih-alih meniru ketidakkonsistenan ini.
- Sampul memakai elemen grafis dan identitas kompetisi; footer section badan memuat nomor halaman/identitas kompetisi. Warna atau kualitas tata letak halaman tidak dinilai di sini karena DOCX tidak dirender ulang.

## 7. Hal yang layak ditiru dan yang perlu dibersihkan

**Pertahankan:** logika EDA → desain, baseline kuat, pemisahan discovery/evaluasi, protokol *frozen*, angka yang dibandingkan secara adil, pengakuan hasil yang kalah, analisis per kelas dan kesalahan, serta klaim terbatas sesuai ablation yang benar-benar ada.

**Jangan menyalin begitu saja:** metode HyMVD, 4.162 citra, 19/13/10 kelompok, atau angka 91,1% sebagai hasil penelitian lain. Penamaan teknis dan gaya harus disesuaikan dengan pipeline dan data sendiri.

**Rapikan saat menjadikannya acuan:** istilah Indonesia–Inggris belum selalu konsisten (`Explorasi`/`Eksplorasi`, `Analisa`/`Analisis`); ada pengulangan kalimat pembuka pada §2.4.3 dan §2.4.4; label `Micro Top-1` dan `Macro Top-1` muncul dua kali di Tabel 3.2 sehingga perlu dicek terhadap metrik asli; penulisan judul pada sampul dan awal badan berbeda kapitalisasi `pada/Pada`; beberapa spasi, sitasi, dan istilah tampak belum disunting final. Ini ciri draf, bukan gaya yang sebaiknya direplikasi.

## 8. Pedoman praktis bila gaya ini diterapkan ke paper lain

1. Tulis satu kalimat tesis: masalah data yang terukur, desain yang menjawabnya, pembanding utama, dan batas klaim.
2. Susun pertanyaan penelitian yang masing-masing punya eksperimen dan hasil di bagian berikutnya.
3. Buka metode dengan temuan diagnostik data; jelaskan fungsi tiap komponen, bukan hanya nama model.
4. Nyatakan kapan label dan data eksternal digunakan; bekukan protokol sebelum menilai hasil luar.
5. Sajikan hasil dalam urutan metode, dengan angka → tafsir → pengecualian → batas kesimpulan.
6. Bandingkan dengan baseline yang memakai input dan protokol setara; sertakan metrik agregat, per kelas, dan kegagalan.
7. Akhiri dengan jawaban eksplisit terhadap rumusan masalah dan saran eksperimen yang mengisolasi ketidakpastian tersisa.
