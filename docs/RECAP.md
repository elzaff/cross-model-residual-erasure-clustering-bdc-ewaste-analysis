# RECAP LENGKAP — Semifinal BDC Satria Data 2026 (clustering citra e-waste)
Terakhir diperbarui: 23 September 2026. Deadline karya ilmiah: **28 September 2026, 16.00 WIB**.
File ini untuk melanjutkan di chat baru. Baca bagian 0 dan 9 dulu.

---

## 0. TL;DR status sekarang
- **Pipeline final (v3):** CMRE(SigLIP2-So400m | DINOv3-H+) + CMRE(PE-Core-G | DINOv3-H+) + DINOv3-H+ → fusi L2 → PCA-32 → **Spectral-kNN (n_neighbors=15), K=13**. K dipilih oleh **SCMax** (AAAI-26), median dari 3 seed. Tanpa label, tanpa proksi gaya, tanpa teks.
- **Hasil final v3** (`results/modal/final_v3/`, CI bootstrap 95%):
  - konsistensi lintas sumber **0,978** [0,965–0,989]
  - purity BDC **0,992** [0,988–0,996], purity eksternal 0,978
  - NMI objek eksternal 0,890 [0,877–0,902]
  - stabilitas antar-seed 1,00; konsensus 3 algoritma 76,1%; OOD GIZ 44,1%
- **UPDATE 23 Sep (ronde 5, lihat bagian 3 poin 10):** SCMax 9 seed memberi median **K=16**, jadi kandidat final sekarang v4 (`final_v4/`, xsrc 0,975). Baseline DINOv3 saja 0,776. Aturan r sebenarnya r=64. CMRE tidak menghapus informasi sumber, hanya mengurangi dominasinya.
- **AUDIT 27 Sep:** daftar K per seed dan ringkasan 100 seed SCMax sebelum audit telah diganti pada `results/modal/scmax_100_source_audit_report.md`; sembilan seed tetap memberi median K=16, sedangkan 100 seed memberi median 16,5. Nilai 3-seed di bagian kronologi bawah adalah catatan historis, bukan hasil audit terakhir. Audit kode dan DIVIDE ada di `results/classic/author_code_audit.md`.
- **PAPER FINAL (24 Sep): `paper_draft/Karya_Ilmiah_BDC2026.docx` + `.pdf`** (template resmi, 22 halaman termasuk sampul, 7 gambar, 5 tabel, 6 persamaan, abstrak 242 kata). Dibangun ulang dengan `python code/make_figures.py && python code/build_paper.py`. Masih perlu diisi user: **tautan repositori** (Lampiran) dan **verifikasi ID kelompok** (dipakai SD2026040000100 dari nama file submission penyisihan).
- Paper lama (`paper_draft/karya_ilmiah_draft_v2.*`) sudah usang. Isinya masih pipeline lama (INLP, K=16, konsistensi 0,945).
- **Dokumen diskusi untuk teman** (artifact): https://claude.ai/artifact/R1wZBCXYPV4PiBoXnDqBov. Isinya belum mencakup kontrol data, SCMax, dan final v3.
- Modal profil **apasijannn: $20,19** dari batas $30. Biaya sesi Claude pertama sekitar $940.

---

## 1. Soal dan aturan (WAJIB dipatuhi)
- Soalnya **clustering tanpa label** citra e-waste, lalu ditulis sebagai karya ilmiah dengan template panitia (template belum ditemukan di laptop). Yang dinilai: pola, makna cluster, dan justifikasi.
- Tiga dokumen wajib: (1) PDF metodologi babak penyisihan, (2) link video verifikasi yang bisa diakses publik (kalau tidak, nilai 0), (3) karya ilmiah.
- **Input model hanya gambar.** Tidak boleh ada teks, prompt, caption, atau WordNet. Metode berbasis teks (SEM, CUBIC, dan sejenisnya) dilarang.
- **Label data uji tidak boleh dipakai.** File `satdat_asli/BDC2026/GT*.csv`, `gt.csv`, dan `inshallah_groundtruth.csv` jangan pernah dibuka. Subset e-waste dari data uji diambil **hanya** dari prediksi SigLIP2 milik tim (`submission_SD2026040000100.csv`, predicted==1).
- Label nama berkas BDC dan label folder dataset eksternal hanya dipakai untuk evaluasi, setelah clustering selesai.
- **Komputasi berat tidak boleh di lokal** ("GAUSAH JALANIN DI LOKAL"). Pakai Modal atau Kaggle. Unduh bobot model lewat **CPU**.
- **Modal:** jalankan `modal billing report --for 'this month'` dulu, dan jaga tiap profil di bawah $30. Profil yang boleh dipakai hanya **apasijannn** ("jangan di fatih, siti, rafli"). Profil fazle, honeylim3sour, endercreeper7590, dan berlianasrlta sudah di atas $30.
- Pakai `MSYS_NO_PATHCONV=1` di Git Bash dan `modal run --detach`. Volume: `bdc-max` (/data, /out, /hf, /giz).
- ⚠️ Token Hugging Face pernah ditempel di chat. **Cabut token itu.** Pakai secret Modal `huggingface-secret`.

## 2. Data
- **D_main = 3.792 citra**: 3.604 dari train BDC (setelah dedup pHash, Hamming ≤ 6) ditambah 188 e-waste dari data uji.
- **Data eksternal, hanya untuk evaluasi** (diproyeksikan ke centroid setelah clustering): Kaan (1.794, foto katalog), Bangladesh (480, foto HP amatir), Karan/battery (499), GIZ (1.000, foto lapangan).
- Audit: 55% Kaan dan 72% PlusYaml adalah duplikat BDC, jadi dedup wajib.
- **Metrik utama, konsistensi lintas sumber (xsrc):** proporsi foto Bangladesh yang masuk ke cluster mayoritas foto Kaan untuk kelas yang sama, pada 5 kelas bersama (baterai, keyboard, ponsel, mouse, PCB). Metrik lain: src|obj (NMI cluster–sumber di dalam kelas; makin kecil makin baik), purity BDC dan eksternal, NMI objek eksternal, stabilitas, silhouette.
- **Proksi gaya** (hanya untuk metode berproksi): latar putih × 3 tingkat resolusi = 6 grup.

## 3. Kronologi eksperimen
1. **Pilot lokal** (RTX 3050, 4 model, K=14) → paper v1, sudah usang.
2. **Kaggle** gagal (limit 429 dari HF). Pindah ke **Modal apasijannn**.
3. **Audit 17 backbone** (`rq_max.py`). Model visi-bahasa bias, DINOv3 tahan. INLP tanpa label memperbaiki VLM, dan hasilnya tahan di 5 proksi. Proksi tekstur AdaIN lemah, jadi bias berasal dari *genre akuisisi*.
4. **Paper v2**: SigLIP2+INLP ⊕ DINOv3-H+ +INLP, Spectral K=16. xsrc 0,945, purity 0,984. Lebih baik dari TURTLE (0,704), TEMI (tidak stabil), dan DECMCV (membuang 20–34% data).
5. **Ronde 1 novelty** (`rq_novel.py`, `results/modal/novel_results.csv`):
   - **M1 CMRE** 0,951, tanpa proksi, setara INLP.
   - M5 LEACE 0,957.
   - Yang gugur: M2 CCE, M3 TURTLE-SI, M4 graf lintas gaya (sensitif terhadap α).
6. **Ronde 2** (`rq_novel2.py`, `embed_fg.py`, `novel2_results.csv`):
   - CMRE di 7 pasangan model: bekerja pada VLM kontrastif besar (SigLIP2, PE-Core, CLIP-ConvNeXt; dengan acuan DINOv3-7B CMRE 0,923 vs INLP 0,739), **gagal** pada CLIP-L (0,763) dan AIMv2 (0,751).
   - **CMRE(SigLIP2) + CMRE(PE) + DINOv3 = 0,975.**
   - Yang gugur: multi-acuan, graf hubness, head TURTLE/SCAN/DMoN, dan masking latar (≤ 0,75).
7. **Ronde 3** (`rq_final2.py`, `embed_meta.py`, `final2_results.csv`):
   - **Kontrol data**, data sejenis dan ukuran sama (protokol Tabel 2): Web-DINO 300M 0,696 vs **MetaCLIP-L 0,200** (src|obj 0,108 vs 0,535); Web-DINO 1B 0,632 vs **MetaCLIP-H 0,357**. Setelah INLP, MetaCLIP-L 0,704 dan MetaCLIP-H 0,640, sedangkan Web-DINO tidak berubah. **Kesimpulan: supervisi bahasa menambah bias sumber yang linear, bukan data.** Catatan: data tidak identik (MC-2B vs fullcc2.5b).
   - CMRE dengan acuan dari data sejenis: pasangan L 0,828 > INLP 0,810; pasangan H 0,602 < INLP 0,685.
   - **Pembanding adil 3 model** (K=16): CMRE 0,975 = INLP ×3 0,975. **Kenaikan dari paper v2 berasal dari PE-Core, bukan CMRE.** Nilai CMRE adalah setara INLP tanpa proksi, dengan silhouette dan NMI objek terbaik. LEACE ×3 0,792 (metode berproksi tidak stabil); fusi mentah 0,524.
   - **Masalah pemilihan K:** tidak ada K yang lolos stabilitas bootstrap ≥ 0,95. Aturan silhouette memilih **K=20**, yang ternyata jelek (xsrc 0,596). Karena itu dicari cara pemilihan K yang lebih berprinsip.
8. **Ronde 4, SCMax** (`rq_scmax.py`, `code/pipeline/scmax/` berisi kode resmi berlisensi MIT, `scmax_results.csv`, `scmax_levels.csv`):
   - SCMax (Zhang dkk., AAAI-26): autoencoder, penggabungan tetangga terdekat bertingkat, lalu skor konsensus NNC antara representasi asli dan representasi yang diganggu secara contrastive. Pengaturan default penulis, 3 seed.
   - **Fitur CMRE:** tingkat sekitar [220, 55, 13–16]; K pilihan 13, 16, 13 → **median 13**. Hibrida (Spectral dengan K dari SCMax) memberi xsrc 0,978.
   - **INLP ×3:** K pilihan 18, 20, 18 (hibrida 0,771). **Fusi mentah:** K 19, 22, 19 (0,23–0,38, dengan NNC tinggi 0,92).
   - **Kesimpulan:** SCMax pada fitur yang masih bias justru menemukan struktur sumber foto, jadi **CMRE harus jalan sebelum SCMax**.
9. **Finalisasi v3** (stage `final3`, K_OVERRIDE=13, `final_max.py` dengan FINAL_TAG=_v3): hasilnya di bagian 0. Uji ketahanan di K=13:
   - n_neighbors 5/10/15/20/30 → 0,980 / 0,983 / 0,978 / **0,839** / 0,953
   - K-Means 0,972 (NMI objek eksternal 0,964), Ward 0,979 (src|obj 0,021), GMM 0,934 (tidak stabil)
   - **Hasil tidak bergantung pada algoritma clustering.**

10. **Ronde 5, perbaikan metodologi (23 Sep; `code/pipeline/rq_fix.py`, `results/modal/fix_results.csv`, `fix_diag_joined.csv`, `final_v4/`).** Semua metrik dirata-rata dari 3 seed Spectral.
   - **Baseline dengan protokol final (K=13):** usulan 0,982; DINOv3-H+ saja 0,776 (baterai 0,23); DINOv3-7B saja 0,839; DINOv3-B saja 0,876; **versi ringan CMRE(PE)+DINOv3 0,962** vs PE+DINOv3 mentah 0,710 (mouse 0,00). Jadi fusi 3 model memang perlu, dan CMRE punya efek kausal yang jelas.
   - **Bug deskripsi:** aturan "50% variansi" tidak pernah terpicu, karena PCA residu dibatasi 64 komponen dan 64 komponen itu < 50%. Akibatnya r = 64 di semua eksperimen lama. Sapuan r: 4 → 0,449; 8 → 0,773; **16–64 → 0,97–0,99 (plateau)**; 128 → 0,821; 256 → 0,808. Ambang yang dihitung benar: 0,3 (r=27/34) → 0,968; 0,5 (r=71/91) → 0,969; 0,7 → 0,818. Paper harus menulis r=64 (atau ambang 0,3–0,5) beserta plateau-nya.
   - **Probe:** probe linear supervised bisa menebak sumber (Kaan vs Bangladesh) dengan akurasi sekitar 0,99 di SEMUA representasi, termasuk CMRE dan INLP. **CMRE tidak menghapus informasi sumber.** Yang dilakukannya: transfer objek Kaan→Bangladesh naik (PCA-32: fusi 0,944 → 0,983; PE 0,946 → 0,992), dan homofili sumber kNN turun sedikit (fusi 0,996 → 0,964; tingkat acak 0,56). Klaim yang benar: dominasi sumber berkurang relatif terhadap pemisahan objek, sehingga partisi tingkat kelas tidak bergantung pada sumber.
   - **Anjloknya n_neighbors ≥ 20 (0,83–0,85) hanya terjadi di kelas baterai.** Metrik lenient (cluster mayoritas label BDC = kelasnya) memberi 0,969–0,985 di semua nn. Foto baterai Bangladesh masuk ke cluster *baterai lain*, jadi ini pecahan subtipe, bukan salah objek. Apakah itu subtipe atau gaya harus dicek di galeri.
   - **Stabilitas bootstrap K** 10–20 berada di 0,86–0,94 (K=13: 0,906). Tidak ada K yang menonjol.
   - **Audit ulang SCMax 9 seed** dengan pengaturan seed kode penulis: K = 13, 17, 16, 16, 19, 16, 15, 19, 19 → **median 16**. Hasil 100 seed memberi median 16,5; perincian ada di `results/modal/scmax_100_source_audit_report.md`. Hibrida: K 13/15/16 → 0,975–0,978; K=19 → 0,794 (baterai).
   - **Diagnostik "kapan CMRE bekerja" (9 pasangan):** prediktor terbaik tanpa label adalah probe proksi gaya pada VLM (Spearman 0,78 dengan kenaikan). AIMv2 bukan kegagalan karena AIMv2 memang tidak bias (xsrc 0,84 > DINOv3 0,76). Kegagalan sesungguhnya: CLIP-L (+0,005) dan MetaCLIP-H|Web-DINO-1B (−0,10).
   - **Final v4 (K=16, fitur v3 yang sama):** purity BDC 0,992 [0,989–0,996], purity eksternal 0,983, **xsrc 0,975 [0,958–0,989]**, NMI 0,859, stabilitas seed 1,0, konsensus 78,3%, OOD GIZ 42,5%. Profil: 3 cluster baterai (C0 campur lampu dan GIZ; C1 dan C4 thumbnail berlatar putih, konsensus C1 = 0), player 2, TV 2 (CRT vs layar datar?), mesin cuci 2, keyboard 2 (C9 97% tanpa label, kemungkinan laptop), PCB C15 (640 foto, 442 GIZ).
   - **DIPUTUSKAN (24 Sep): partisi utama K=16 (v4), K=13 sebagai tingkat kasar.** Galeri v4 sudah dicek, pecahannya karena jenis objek, bukan gaya foto:
     - C0 aki/baterai timbal-asam (ada beberapa stop kontak nyasar)
     - C1 baterai pack laptop
     - C4 baterai HP/kamera (sel pipih Li-ion, plus AA)
     - C2 turntable; C5 CD player/boombox/radio
     - C3 TV CRT (banyak foto lapangan); C7 LCD/monitor layar datar
     - C9 **laptop** (di nama berkas BDC berlabel "keyboard"; foto amatir, banyak jepretan berulang)
     - C6 mesin cuci bukaan atas / tabung ganda; C8 mesin cuci front-load
     - C10 keyboard; C11 microwave; C12 printer; C13 mouse; C14 smartphone (hampir semua foto HP amatir)
     - C15 PCB dan tumpukan scrap campuran (kabel, HDD, papan)
     - Galeri ambiguous: baterai laptop, HP jadul (feature phone), PC desktop/monitor CRT, tumpukan campuran. Kategori yang tidak punya cluster sendiri.
     - OOD GIZ: **AC (unit indoor/outdoor), kulkas, dan tumpukan logam.** Kategori alat penukar suhu (WEEE kategori 1) tidak ada di BDC.

11. **PROTOKOL VALIDASI ILIEV — DIKUNCI 24 Sep, sebelum data diunduh atau dilihat.** Hasil apa pun dilaporkan apa adanya, dan pipeline tidak boleh diubah setelah melihat hasilnya.
   - **Data:** Roboflow `electronic-waste-detection/e-waste-dataset-r0ojc` (Iliev, CC BY 4.0, 77 kelas, tag UNU-KEY). Unduh ke volume Modal lewat CPU, pakai secret `roboflow-secret` (dibuat user).
   - **Crop:** hanya citra dengan 1 anotasi, ambil bbox-nya, sisi terpendek ≥ 64 px, dan maksimal 30 per kelas (seed 0). Dedup pHash (Hamming ≤ 6) terhadap BDC, Kaan, Bangladesh, Karan, dan GIZ.
   - **Pipeline beku v4:** CMRE(SigLIP2|DINOv3-H+) + CMRE(PE|DINOv3-H+) + DINOv3-H+, r=64, TTA flip, PCA-32 di-fit pada D_main, centroid K=16 dari `final_v4/assignments.csv`. Iliev hanya **diproyeksikan** ke centroid terdekat. Ambang OOD sama dengan final_max.
   - **Pemetaan kelas (ditulis sebelum melihat hasil):** Battery→battery; Smartphone, Bar-Phone→mobile; Computer-Keyboard→keyboard; Computer-Mouse→mouse; PCB→pcb; Microwave→microwave; Printer→printer; Washing-Machine→washing_machine; CRT-TV, Flat-Panel-TV→television; Music-Player→player. **Subtipe:** CRT-TV→C3, Flat-Panel-TV→C7, Laptop→C9. Semua kelas lain dianggap di luar BDC (OOD).
   - **Metrik:**
     - (a) xsrc 10 kelas: proporsi Iliev per kelas yang masuk cluster mayoritas Kaan untuk kelas itu, lalu dirata-rata. Plus versi lenient: cluster mayoritas label BDC = kelasnya.
     - (b) purity Iliev pada kelas yang sama.
     - (c) akurasi subtipe (CRT→C3, Flat→C7, Laptop→C9).
     - (d) OOD: AUROC skor jarak ke centroid, kelas BDC vs non-BDC, plus laju OOD per kelas (AC, kulkas, kipas, setrika, lampu).
     - (e) UNU-KEY mayoritas per cluster, lalu dipetakan ke EU-6.
     - (f) pembanding dengan protokol yang sama: fusi mentah, DINOv3-H+ saja, INLP ×3, versi ringan CMRE(PE)+DINOv3.
     - CI bootstrap 95% dengan resampling citra Iliev.
   - **HASIL ILIEV (24 Sep; `results/modal/iliev_*.csv`; kode `prep_new.py`, `embed_new.py`, `rq_iliev.py`).** Roboflow versi 44, 69 kelas, 1.751 crop setelah dedup. Kontrol embedding: kosinus ≥ 0,9988; z reproduksi v4 selisih 2e-05.
     - **Usulan v4:** xsrc10 **0,885 [0,864–0,908]**, lenient **0,930 [0,914–0,948]**, purity **0,939 [0,913–0,964]**, OOD AUROC **0,868 [0,843–…]**, laju OOD kelas BDC 9,6% vs kelas non-BDC 49,4%.
     - **Pembanding:** fusi mentah 0,803 (mobile 0,00, mouse 0,63); DINOv3 saja 0,755 (baterai 0,00); INLP×3 0,887 (setara); ringan 0,882. Urutannya bertahan: usulan > mentah (+0,08) dan > DINOv3 (+0,13).
     - **Subtipe:** Laptop→C9 **0,967**, Flat-TV→C7 0,833, CRT-TV→C3 0,667. Penemuan laptop tervalidasi di data baru.
     - **Kelas lemah:** player 0,30 (Music-Player di Iliev adalah pemutar MP3/portable dan masuk ke C14 ponsel; BDC player adalah turntable/CD, jadi ini soal pemetaan kelas) dan TV 0,58 (CRT masuk C3, bukan cluster mayoritas Kaan; di metrik lenient benar).
     - **OOD:** AC 83%, kulkas 90%, setrika 80% ditolak, jadi interpretasi GIZ (celah kategori penukar suhu) terkonfirmasi. Tapi **C0 (cluster aki) menjadi "penarik" benda asing**: lampu, e-bike, oksimeter, dan sebagainya masuk ke C0 dengan OOD 0%. Ambang global gagal untuk cluster yang heterogen. Fusi mentah punya AUROC lebih tinggi (0,94). Perbaikan (ambang per cluster) = future work, TIDAK boleh diklaim karena sudah melihat data uji.
     - **EU-6 per cluster** (`iliev_cluster_eu6.csv`): C3/C7/C9 layar (0,95–1,0), C8 besar (0,94), C10/C13 IT kecil (1,0), C14 IT (0,71), C15 komponen (0,73), C6 → freezer ikut masuk (bentuk mirip mesin cuci bukaan atas).
   - **HASIL OFFICE-HOME** (`officehome_results.csv`, 2.917 citra, 20 kelas, K=20): SigLIP2 mentah 0,691, PE 0,817, DINOv3 0,761, **fusi mentah 0,865, INLP×3 0,870, CMRE 0,864** (silhouette 0,391 → 0,481), ringan 0,809. **CMRE tidak menambah** karena fusi di sini memang sudah tidak bias (dom|obj 0,07). SCMax: mentah [18, 20, 19], INLP [22, 19, 21], CMRE [21, 21, 16]. Semuanya dekat 20, jadi klaim "CMRE harus sebelum SCMax" **hanya berlaku bila fitur bias** (BDC), tidak general.
   - **RONDE 7 (24 Sep; `rq_fix2.py`, `fix2_results.csv`, `fix2_jaccard.csv`). Iliev sekarang DINYATAKAN set pengembangan**, jadi klaim akhir butuh set uji segar (kandidat: Roboflow Shubha, CC BY 4.0, belum diunduh).
     - **OOD kNN (Sun dkk. 2022, k=10, PCA-32 usulan) menggantikan jarak centroid:** AUROC 0,868 → **0,937**; benda asing yang terserap C0 35% → **2,5%**; benda non-BDC yang ditandai 49% → **90%**. Harganya: alarm palsu Kaan 1,3% → 3,0%, Bangladesh 11,6% → 13,1%, kelas BDC di Iliev 9,6% → 12,3%, GIZ 42,5% → 44,5%. Stabil untuk k 5–20 (0,932–0,937). kNN pada fusi mentah 0,927, jadi usulan + kNN > mentah.
     - **Sensitivitas pemetaan Iliev:** protokol terkunci 0,885 → tanpa Music-Player (beda definisi) 0,950 → ditambah subtipe TV 0,987.
     - **CMRE lalu INLP:** BDC 0,983 (CMRE 0,975; INLP 0,980), Iliev 0,903 (0,885; 0,887). Terbaik di dua data, tapi membutuhkan proksi lagi, jadi disajikan sebagai varian opsional dan bukti bahwa CMRE dan INLP saling melengkapi.
     - **Jaccard per cluster (Hennig):** 11 dari 16 cluster ≥ 0,85 (sangat stabil; C11–C13 = 1,0). Yang lemah: C0 aki 0,71, C3 CRT 0,79, C4 baterai HP 0,82, C7 layar datar 0,85, C15 PCB 0,85. Ketidakstabilan terlokalisasi di cluster baterai/CRT/buangan.
   - **PROTOKOL UJI SHUBHA — DIKUNCI 24 Sep sebelum unduh** (set uji segar untuk perbaikan ronde 7). Data: Roboflow `shubha-to6ii/e-waste-1sn3k` versi terbaru (CC BY 4.0). Crop: 1 anotasi, sisi terpendek ≥ 64 px, maksimal 60 per kelas (seed 0), dedup pHash ≤ 6 terhadap items.csv DAN crop Iliev. **Pemetaan:** Mouse→mouse, Keyboard→keyboard, Mobile→mobile, PCB→pcb (in-dist); Remote, Dryer, Headphone, Modem, Pendrive = OOD; Computer dan Electronics dikeluarkan (ambigu). **Pipeline beku:** v4 (K=16), skor OOD **kNN k=10 PCA-32** (dipilih di Iliev) vs centroid v4 sebagai pembanding, ambang persentil 95 D_main. **Metrik:** xsrc4 vs cluster mayoritas Kaan, lenient, purity, OOD AUROC dan laju tandai in/out, varian (usulan, CMRE+INLP, INLP×3, fusi mentah, DINOv3 saja) pada xsrc4, CI bootstrap 95%.
   - **HASIL SHUBHA (uji segar; `shubha_results.csv`, `rq_shubha.py`).** Versi 2 hanya punya 7 kelas; 300 crop lolos (Headphone, Keyboard, Mobile, Mouse, Remote masing-masing 60; PCB/Dryer/Modem/Pendrive tidak ada yang lolos filter). Kontrol embedding OK.
     - **Usulan v4:** xsrc (3 kelas) **0,956 [0,924–0,983]**, lenient 0,994, purity 1,0.
     - **OOD kNN: AUROC 0,994 [0,984–0,999] vs centroid 0,941**; Remote dan Headphone 100% ditandai (centroid 77,5%); in-dist ditandai 9,4% (centroid 6,1%). **Perbaikan OOD kNN TERKONFIRMASI di data segar.**
     - **Fusi mentah 0,356** (ponsel 0,07, mouse 0,10): bias sumber sangat parah di data ini, dan CMRE memulihkannya ke 0,956. DINOv3 saja 0,889.
     - **CMRE lalu INLP 0,967 vs INLP ×3 0,972**: keunggulan kombinasi di Iliev **tidak berulang**. Klaim "kombinasi terbaik" gugur; ketiganya setara.
     - Keterbatasan uji ini: hanya 3 kelas in-dist dan 2 kelas OOD.
   - **Office-Home** (awalnya menunggu izin unduh) menyusul secara terpisah: pipeline dijalankan ulang (mentah / INLP / CMRE / SCMax), domain Product vs Real World, sekitar 18 kelas elektronik.

## 4. Cluster K=13 (DUGAAN dari label; galeri belum dilihat)
Galeri ada di volume `/out/final_v3/gallery/`. Profil cluster: `results/modal/final_v3/cluster_profile.csv`.

| C | n | Dugaan isi | Catatan |
|---|---|---|---|
| C0 | 70 | baterai (aki?) | konsensus 0 |
| C1 | 115 | mesin cuci (tabung ganda?) | konsensus 0 |
| C2 | 191 | mesin cuci (front-load?) | |
| C3 | 277 | "keyboard", 97% tanpa label | **kemungkinan laptop** |
| C4 | 215 | baterai | eksternal juga berisi bola lampu |
| C5 | 264 | pemutar CD/radio dan turntable | tergabung |
| C6 | 404 | TV (CRT dan layar datar?) | 150 foto GIZ |
| C7 | 275 | microwave | |
| C8 | 294 | printer | |
| C9 | 373 | keyboard | |
| C10 | 291 | mouse | |
| C11 | 366 | ponsel | |
| C12 | 657 | PCB dan tumpukan e-waste | 683 foto GIZ, 304 OOD |

Saran historis ronde awal: sajikan taksonomi **dua tingkat**, K=13 sebagai partisi utama dan **K=16 sebagai sub-tingkat**. Audit terbaru memilih K=16 sebagai partisi final. K=16 mempertahankan pemisahan CRT vs layar datar, CD/radio vs turntable, dan 3 jenis baterai.

## 5. Klaim novelty (sudah dicek ke literatur)
- **Baru:**
  - (1) **CMRE**: model SSL sebagai acuan untuk membersihkan embedding VLM, tanpa label, proksi, maupun teks. Pembanding terdekat, UMFC 2024, tidak memakai model kedua dan dibuat untuk klasifikasi.
  - (2) Masalah dan metrik bias sumber untuk clustering e-waste.
  - (3) Temuan empiris: VLM bias sedangkan SSL tahan. Ini berlawanan dengan literatur 2025, dan **dikonfirmasi kontrol data MetaCLIP vs Web-DINO**.
  - (4) Kombinasi **CMRE → SCMax**: fitur dibersihkan dulu, baru pemilihan K otomatis bekerja.
- **Bukan baru (harus disitasi):** INLP, LEACE, HEX (2019), fair clustering (CVPR 2020), deconfounding embedding dokumen (2025), resolusi sebagai sidik jari dataset (2026), SCMax itu sendiri, TURTLE, TEMI, SCAN, DMoN, Spectral.
- **Kalimat novelty:** "CMRE menghapus bias sumber tanpa label dan tanpa proksi dengan memakai model self-supervised sebagai acuan; dikombinasikan dengan SCMax untuk menentukan jumlah cluster tanpa label."
- **Judul yang direkomendasikan:** "Clustering Citra Limbah Elektronik Tanpa Label yang Tahan Bias Sumber Foto melalui Penghapusan Residu Lintas Model". Versi Inggris: "Source-Bias-Robust Unsupervised Clustering of E-Waste Images via Cross-Model Residual Erasure".
- **Penilaian:** lomba sekitar 8/10, konferensi utama sekitar 5/10, SINTA S2 peluang tinggi, S1 peluang sedang.

## 6. Status 8 kelemahan (dari kritik yang kamu bagikan)
| # | Kelemahan | Status |
|---|---|---|
| 7 | Bergantung pada Spectral dan K | ✅ Teratasi: K dari SCMax; K-Means, Ward, dan Spectral setara; graf stabil di 4 dari 5 nilai |
| 1 | CMRE belum terbukti menghapus bias | ⚠️ Sebagian: kontrol data sudah; **probe label sumber pada residu belum** |
| 3 | Bergantung pada acuan DINO | ⚠️ Sebagian: acuan yang lebih bias melemahkan CMRE |
| 8 | Risiko overfitting eksperimen | ⚠️ Diredam dengan aturan tanpa label dan pelaporan hasil yang gagal; tetap harus diakui |
| 2 | Tidak universal (CLIP-L, AIMv2) | ❌ Belum ada diagnostik "kapan CMRE bekerja" |
| 4 | Aturan 50% variansi heuristik | ❌ Hanya ada bukti stabil untuk r ≥ 8 |
| 5 | Satu domain | ❌ Office-Home belum diuji |
| 6 | Pipeline berat | ❌ Versi ringan (PE + DINOv3) belum diuji |
Kelemahan lain: evaluasi eksternal kecil (5 kelas, 480 foto); konsensus turun ke 76%; OOD GIZ naik ke 44%.

## 7. Dataset tambahan yang diusulkan (BELUM diunduh, perlu izin user)
- **RecyBat24** (Scientific Data 2025): baterai pouch, prismatic, dan silinder. Menguji klaim pemisahan jenis baterai. Sekitar $0,3.
- **XBAT+** (Scientific Data 2026): 3.045 citra perangkat berbaterai dari fasilitas daur ulang. Uji foto lapangan. Sekitar $0,5.
- **Office-Home** (CVPR 2017; bukan e-waste): domain *Product* vs *Real World*, sekitar 18 kelas elektronik. Uji generalisasi ke domain lain. Sekitar $1–1,5. Lisensi riset non-komersial.
- Cek lisensi masing-masing dan aturan lomba soal data eksternal.

## 8. Peta file
- **Kode** (`code/pipeline/`):
  - `modal_app.py` (stage: extract, extra, analyze, finalize, extra2, novel, novel2, final2, scmax, final3, prefetch_meta)
  - `embed_kg.py`, `embed_extra.py`, `embed_style.py`, `embed_fg.py`, `embed_meta.py`
  - `common.py`, `rq1_metrics.py`, `rq_max.py`, `final_max.py` (mendukung `FINAL_TAG`)
  - `rq_extra.py`, `rq_novel.py`, `rq_novel2.py`, `rq_final2.py` (mendukung `K_OVERRIDE`), `rq_scmax.py`
  - `scmax/` (kode resmi SCMax, MIT)
- **Hasil** (`results/modal/`):
  - `max_*.csv`, `final/` (paper v2, K=16), `final_v3/` (**final, K=13**)
  - `novel_results.csv`, `novel2_results.csv`, `final2_results.csv`, `scmax_results.csv`, `scmax_levels.csv`, `fg_examples.jpg`
- **Log:** `results/logs/modal_*.log`
- **Paper:** `paper_draft/karya_ilmiah_draft_v2.{md,docx}` (usang, perlu ditulis ulang). Paper acuan ada di `paper/`, termasuk `03669-AAAI26.ZhangL-ML.pdf` (SCMax).
- **Memory Claude:** `bdc-semifinal-direction.md`, berisi semua ronde.

## 9. TODO untuk chat berikutnya (urutan disarankan)
1. **Eksperimen, maksimal 1 hari:**
   - probe label sumber pada residu CMRE dan diagnostik kapan CMRE bekerja (#1, #2);
   - sapuan r dan aturan alternatif (#4);
   - versi ringan PE + DINOv3 (#6);
   - RecyBat24, XBAT+, Office-Home **setelah user mengizinkan unduhan** (#5).
   - Opsional: SCMax dengan seed tambahan; stabilitas bootstrap K=13; TURTLE, TEMI, dan DECMCV diulang di pipeline baru.
2. **Lihat galeri final_v3 dan K=16**, lalu beri nama cluster dan petakan ke WEEE.
3. **Tulis ulang paper** dengan pipeline CMRE + SCMax, kontrol data, pembanding adil, uji ketahanan, hasil yang gagal, dan kelemahan eksplisit. Pindahkan ke template panitia.
4. Perbarui `code/README.md` dan artifact dokumentasi.
5. Tugas user: PDF metodologi penyisihan, video verifikasi (publik), cabut token HF, cek aturan panitia soal data eksternal dan publikasi.

## 3.12 Ronde 8 (24 Sep): analisis tambahan, BELUM masuk paper (`results/modal/r8/`, kode `stack.py`, `rq_r8.py`, `rq_d1.py`, `rq_gallery.py`, `make_r8_figures.py`, `reproduce.py`)
- **C1 bootstrap berpasangan Δxsrc (v4 − pembanding, 2000×):** vs fusi mentah BDC +0,45 [0,43; 0,48], Iliev +0,08 [0,06; 0,11], Shubha +0,60 [0,56; 0,64]; vs DINOv3 saja +0,22 / +0,13 / +0,07, semua p<0,001. vs INLP×3 dan vs ringan: tidak berbeda (CI melewati 0; INLP sedikit lebih tinggi di BDC/Shubha). Klaim: CMRE ≈ INLP tanpa proxy.
- **C2 per kelas:** kelemahan v4 di Iliev player 0,30 dan TV 0,58 (masalah pemetaan kelas/subtipe); BDC battery 0,92.
- **C3 apa yang dibuang CMRE:** 64 arah = ~50% (SigLIP2) / 45% (PE) energi. Arah dibuang berkorelasi dengan resolusi (|ρ| s.d. 0,68) dan latar putih (0,39). Probe gaya: mentah 0,70 → disimpan 0,62; objek tetap 0,99/0,98; sumber tetap ~0,96–0,99 (konsisten: sumber tidak dihapus, dominasinya berkurang). Lembar contoh `c3_*_pc1_{low,high}.jpg`.
- **C4 K13→K16:** 14/16 kelompok mewarisi ≥97% dari satu induk; yang terbelah: aki (0,67 dari induk baterai) dan TV layar datar (0,80). Laptop berasal dari induk berlabel "keyboard" (laptop di BDC berlabel keyboard). `c4_hierarchy.png`.
- **C5 kegagalan Bangladesh:** hanya 12/449: battery 7 → Aki, pcb 3 → baterai ponsel, mobile 2. `c5_failures.jpg`.
- **C6 heatmap:** 15/16 kelompok ≥ 0,9 satu label BDC. `c6_heatmap.png`.
- **C7 WEEE vs penggabungan acak (100k permutasi):** silhouette 6 grup WEEE 0,178 vs acak 0,144 (p=0,01); Iliev in-distribution: kategori EU-6 crop = kategori grup kelompoknya 0,79 vs acak 0,19 (p<0,001); jarak centroid intra-grup tidak beda (p=0,46); Ward-6 vs WEEE ARI 0,15 (p=0,09).
- **C8 α Ridge:** α 0,01–1 stabil (BDC 0,975–0,983, Iliev 0,885–0,898, Shubha 0,956–0,961); α ≥ 10 turun (α=1000 BDC 0,74). α=1 TIDAK diganti (memilih dari set uji = mengintip).
- **C9 waktu:** CPU 32 core: CMRE + fusi 0,86 s, klaster + proyeksi 0,18 s, Spectral 0,16 s, kNN-OOD 0,05 s (INLP×3 7,6 s). L4: SigLIP2 41 img/s (dengan flip), DINOv3-H+ + PE-Core-G 3,7 img/s (PE-Core-G gigantic = bottleneck).
- **D1 (fitur v4, K=16, 3 seed):** Spectral usulan xsrc BDC/Iliev/Shubha 0,975/0,885/0,956, seed ARI 1,0; TURTLE 0,79/0,74/0,54 (ARI 0,97); TEMI 0,59/0,64/0,71 (ARI 0,42); DECMCV 0,91/0,81/0,95 (cakupan 81%).
- **D4 referensi lain (BDC):** CMRE naik terhadap mentah untuk semua referensi SSL: DINOv3-7B 0,983 (terbaik), H+ 0,975, Web-DINO-300M 0,930, 1B 0,917, DINOv2-L 0,777, ConvNeXt-L 0,726, DINOv3-L 0,596, B 0,593. Referensi supervised ConvNeXt V2-H GAGAL (0,384 < mentah 0,480) → referensi harus SSL berskala besar.
- **reproduce.py:** ARI 1,0000 vs submisi, xsrc 0,975; OOD Bangladesh 18,3% pada 480 foto (RECAP lama 13,1% = subset lain? cek sebelum ditulis).
- E1/E4: `code/requirements.txt`, `code/.gitignore`, `code/LICENSE` (MIT), tabel dataset di `code/README.md`. A5 scan: tidak ada token/GT di `code/`.
- **Ronde 8b (`rq_r8b.py`, `r8b_*.csv`):**
  - #3 OOD Bangladesh BUKAN inkonsisten: 13,1% = alarm palsu pada 449 foto kelas BDC; 31 foto lampu Bangladesh (bukan kelas BDC) 93,5% ditandai tidak dikenal (bukti OOD tambahan). `reproduce.py` kini mencetak keduanya.
  - #1 Pemilihan referensi tanpa label: aturan "referensi SSL dengan R² Ridge (CV, VLM ← referensi) tertinggi" memilih DINOv3-7B (R² 0,434, xsrc 0,983) lalu DINOv3-H+ (0,403, xsrc 0,975) = dua terbaik sesungguhnya. Spearman R² vs xsrc pada 8 referensi SSL 0,69; silhouette hanya 0,38; stabilitas seed = 1,0 semua (tidak informatif). H+ dipilih atas 7B karena biaya (7B butuh A100). Referensi supervised dikecualikan secara prinsip (R² 0,392 tapi gagal, xsrc 0,384).
  - #2 Varian cepat tanpa PE-Core-G: embedding L4 SigLIP2 42,8 img/s + DINOv3-H+ 39,9 img/s → ~20 img/s gabungan vs ~3,4 img/s v4 (≈6× lebih cepat). CMRE(SigLIP2)+DINOv3: xsrc 0,951/0,860/0,922 (Δ vs v4 −0,02 s.d. −0,03, CI tidak melewati 0), AUROC OOD Iliev sama 0,937, lampu 93,5%. Fusi mentah cepat runtuh (0,555/0,835/0,378).
  - #188 Tanpa 188 citra uji (`rq_notest.py`, `r8c_notest.csv`): hanya 3.604 train → xsrc BDC 0,975, Iliev 0,895, Shubha 0,950, purity 0,991; ARI vs v4 0,934 (train) dan 0,970 (188 uji). Area abu-abu aturan tertutup.
  - Paper: revisi metodologi 2 batch (37 penggantian di `build_paper.py`): setara INLP, definisi erasure, aturan r/α/acuan tanpa label, kronologi K, xsrc-eks, status Iliev (dev untuk OOD), Shubha "konfirmasi awal", BDC = set pengembangan, Tabel 4 pakai angka D1, sapuan r/nn penuh, H1 sebagai hipotesis, bukti segmentasi, jumlah set validasi diseragamkan, kalimat 188 uji. Belum: potong ke ≤ 20 halaman dan item non-metodologi.
- **24 Sep sore:** PDF lengkap 27 hlm (batch 3: versi cepat, uji WEEE, analisis kegagalan, subbab 3.7 Keterbatasan, Lampiran Tabel 6–7 + Gambar 8–9, Gambar 6/7b dari galeri bebas wajah, overclaim "kimia baterai" dihapus). Dashboard diperbarui (galeri bersih, CMRE cepat, OOD Bangladesh tanpa lampu + baris lampu, panel "Pemeriksaan setelah partisi final dibekukan"). Folder `github_repo/` = subset siap upload (README hasil + tim, LICENSE MIT, .gitignore, reproduce.py teruji ARI 1,0). RECAP, BIKOM, bimbingan, template TIDAK ikut.
