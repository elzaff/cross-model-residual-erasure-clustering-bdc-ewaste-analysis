# Kode — Semifinal BDC Satria Data 2026: clustering citra e-waste yang tahan bias sumber foto

Pipeline final: **CMRE(SigLIP2-So400m | DINOv3-H+) + CMRE(PE-Core-G | DINOv3-H+) + DINOv3-H+ → PCA-32 →
SCMax (K = 16) → Spectral-kNN → OOD kNN**. Input model hanya citra; label hanya dipakai untuk evaluasi.

```
code/
  ewaste_cmre.py          implementasi inti yang ringkas (CMRE, fusi, clustering, OOD kNN) + uji mandiri
  reproduce.py            reproduksi partisi final di CPU dari z_final_v4.npy (< 1 menit, tanpa GPU/model)
  make_r8_figures.py      gambar ronde 8: hierarki K=13→16, heatmap kelompok × label
  make_figures.py         seluruh gambar paper dari CSV hasil → paper_draft/fig/
  build_paper.py          menyusun karya ilmiah ke template resmi BDC → paper_draft/Karya_Ilmiah_BDC2026.docx
  pipeline/               eksperimen lengkap (dijalankan di Modal; volume `bdc-max`)
    modal_app.py          orkestrasi; setiap tahap = satu `--stage`
    embed_kg.py, embed_extra.py, embed_new.py   ekstraksi fitur (TTA flip) dan statistik gaya piksel
    common.py, rq1_metrics.py                   loader, PCA, metrik (xsrc, purity, NMI kondisional)
    rq_max.py             audit 17 representasi (H1)
    rq_final2.py          pembanding adil (INLP, LEACE, fusi mentah) dan kontrol data MetaCLIP vs Web-DINO
    rq_scmax.py           pemilihan K dengan SCMax (kode resmi di scmax/, lisensi MIT)
    rq_fix.py, rq_fix2.py uji ketahanan: baseline, probe, sapuan r / n_neighbors / K, Jaccard, OOD kNN
    prep_new.py           menyiapkan set validasi (Iliev, Shubha, Office-Home) dengan protokol terkunci
    rq_iliev.py, rq_shubha.py, rq_officehome.py validasi eksternal
    final_max.py          partisi final, CI bootstrap, konsensus, galeri
    paper_assets.py       contoh citra, t-SNE, perbandingan algoritma K = 16, OOD per kelas
    stack.py              gabungan D_main + eksternal + Iliev + Shubha dengan fitur v4 (dipakai ronde 8)
    rq_r8.py              ronde 8: bootstrap berpasangan, xsrc per kelas, apa yang dibuang CMRE, uji WEEE, alpha, waktu, referensi lain
    rq_d1.py              TURTLE / TEMI / DECMCV pada fitur v4
    rq_gallery.py         galeri tanpa wajah + audit wajah
```

## Menjalankan ulang
```bash
cd code/pipeline
export MODAL_PROFILE=<profil> MSYS_NO_PATHCONV=1
modal run --detach modal_app.py --stage all            # ekstraksi fitur (GPU) + audit 17 representasi
modal run --detach modal_app.py --stage final2         # pembanding adil + kontrol data
modal run --detach modal_app.py --stage scmax          # SCMax 3 seed pertama
modal run --detach modal_app.py --stage scmax_seeds    # audit awal: 9 seed; median K = 16
modal run --detach modal_app.py --stage final4         # partisi final K = 16 → /out/final_v4
modal run --detach modal_app.py --stage fix            # baseline, probe, sapuan parameter
modal run --detach modal_app.py --stage fix2           # OOD kNN, Jaccard per kelompok
modal run --detach modal_app.py --stage iliev          # validasi terkunci (butuh secret roboflow-secret)
modal run --detach modal_app.py --stage shubha         # uji segar
modal run --detach modal_app.py --stage officehome     # domain lain
modal run --detach modal_app.py --stage paper          # aset gambar
modal run --detach modal_app.py --stage r8             # analisis ronde 8 (CPU)
modal run --detach modal_app.py --stage d1             # TURTLE/TEMI/DECMCV (L4)
modal run --detach modal_app.py --stage gallery        # galeri tanpa wajah
modal run --detach modal_app.py --stage bench          # throughput embedding di L4
modal volume get bdc-max /out ../../results/modal      # unduh hasil
cd .. && python make_figures.py && python build_paper.py
python ewaste_cmre.py                                   # uji mandiri implementasi inti
python reproduce.py                                     # reproduksi CPU: ARI 1,0 vs submisi, xsrc 0,975
```

Hasil utama ada di `results/modal/` (`final_v4/`, `fix_results.csv`, `fix2_results.csv`, `iliev_results.csv`,
`shubha_results.csv`, `officehome_results.csv`, `paper/`). Label data uji panitia tidak pernah dibaca.

## Data
Tidak ada data yang didistribusikan ulang di repo ini. Jumlah = setelah dedup pHash (Hamming ≤ 6) terhadap BDC.
Label sumber eksternal hanya dipakai untuk evaluasi setelah clustering; label uji panitia tidak pernah dibaca.

| Set | Peran | Jumlah | Lisensi | Tautan |
|---|---|---|---|---|
| BDC Satria Data 2026 (latih + uji) | data clustering (D_main) | 3.792 | aturan lomba | panitia BDC |
| Kaan, Waste Classification | evaluasi objek (citra produk) | 1.794 | CDLA-Permissive-1.0 | https://www.kaggle.com/datasets/kaanerkez/waste-classfication-dataset |
| Custom Bangladeshi E-Waste | evaluasi lintas sumber (foto objek berlatar beragam) | 480 | CC BY 4.0 | https://data.mendeley.com/datasets/77383kmdnw/1 |
| Karan, Garbage Classification (baterai) | evaluasi objek | 499 | Apache 2.0 | https://www.kaggle.com/datasets/karansolanki01/garbage-classification |
| GIZ E-Waste Database | uji OOD foto lapangan | 1.000 | CC BY 4.0 | https://huggingface.co/datasets/GIZ/E-Waste-Database |
| Iliev, E-Waste Dataset (Roboflow v44) | validasi terkunci | 1.751 crop, 69 kelas | CC BY 4.0 | https://universe.roboflow.com/electronic-waste-detection/e-waste-dataset-r0ojc |
| Shubha, E-waste (Roboflow v2) | uji segar | 300 crop | CC BY 4.0 | https://universe.roboflow.com/shubha-to6ii/e-waste-1sn3k |
| Office-Home (Product, Real World) | uji domain lain | 2.917 | riset non-komersial | https://huggingface.co/datasets/flwrlabs/office-home |

Lisensi kode: MIT (`LICENSE`). Dependensi lokal: `requirements.txt`; image Modal dipin di `pipeline/modal_app.py`.


## Audit tambahan

Audit sensitivitas SCMax memakai 100 seed pada fitur CMRE yang sama. Median K = 16, modus K = 17, dan K = 16 terpilih 20/100 kali. xsrc hybrid 0.923 +/- 0.098; NMI eksternal 0.854 +/- 0.022; ARI antarpasangan partisi 0.861 +/- 0.110. Ini menguji variasi seed pada data tetap, bukan 100 sampel uji independen. Setelah batch hasil tersedia di results/modal, jalankan python code/pipeline/summarize_scmax_100.py untuk membuat ringkasan. Hasil lengkap ada di [laporan](../results/modal/scmax_100_report.md) dan [CSV](../results/modal/scmax_results_100.csv).

Hierarki agglomerative untuk partisi 16 kelompok dibuat post hoc dengan `python code/try_hierarchy.py`; hasil level dan merge tersimpan di `results/modal/hierarchy/`.
