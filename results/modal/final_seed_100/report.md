# Audit 100 seed: pemilihan K dan clustering final CMRE v4

**Kesimpulan:** Partisi final pada **K tetap 16** terulang tepat pada 100 seed Spectral-kNN (0–99). Sebaliknya, seed **SCMax untuk memilih K** menghasilkan K=13–21 dan kualitas partisi yang berubah. Dua uji ini menjawab sumber variasi yang berbeda.

## A. Pemilihan K oleh SCMax (hasil terdahulu, diaudit ulang)

Sumber: [`scmax_results_100_source_audit.csv`](../scmax_results_100_source_audit.csv) dan [`scmax_100_source_audit_report.md`](../scmax_100_source_audit_report.md). Ada 100 seed unik, 0–99, semuanya menghasilkan K valid. Fitur CMRE dibekukan; SCMax memakai pengaturan seed sesuai kode penulis. Hybrid Spectral memakai `random_state=0` setiap kali, K mengikuti pilihan SCMax.

| K pilihan | Banyak seed |
|---:|---:|
| 13 | 1 |
| 14 | 12 |
| 15 | 17 |
| 16 | 20 |
| 17 | 22 |
| 18 | 13 |
| 19 | 11 |
| 20 | 3 |
| 21 | 1 |

K median 16,5; modus 17. K final 16 terpilih pada 20/100 seed. xsrc hybrid rata-rata 0,919 ± 0,103, rentang 0,596–0,988. ARI partisi hybrid antarpasangan seed (4.950 pasangan) rata-rata 0,860 ± 0,110, rentang 0,649–1,000; ARI terhadap partisi final K=16 rata-rata 0,874 ± 0,110, rentang 0,705–1,000. Nilai terendah berkaitan dengan K=20–21 (xsrc 0,596); K=17 menghasilkan xsrc 0,988 dan ARI sekitar 0,800 terhadap K=16. Ini **sensitivitas pemilihan K**, bukan ketidakstabilan Spectral pada K tetap.

## B. Clustering final v4 pada K tetap 16 (audit baru)

Skrip: [`final_100_seed_audit.py`](../../../code/pipeline/final_100_seed_audit.py). Input sama dengan `final_max.py`: [`z_final_v4.npy`](../z_final_v4.npy), 7.565 × 32 fitur PCA; 3.792 foto `D_main`; 15 tetangga; `SpectralClustering(n_clusters=16, affinity="nearest_neighbors", assign_labels="cluster_qr")`. Setiap seed 0–99 dipakai sebagai `random_state` clustering. Seed 0 cocok **label demi label** dengan [`final_v4/assignments.csv`](../final_v4/assignments.csv). Foto eksternal dikirim ke centroid cluster utama seperti pipeline final.

| Ukuran | Hasil 100 seed |
|---|---:|
| Berhasil / gagal / warning | 100 / 0 / 0 |
| Cluster terisi pada setiap run | 16 |
| Ukuran cluster terkecil–terbesar | 70–640 foto, sama di semua run |
| Partisi label unik | 1 |
| ARI terhadap partisi final | 1,000 pada semua seed |
| ARI antarpasangan seed (4.950 pasangan) | 1,000 pada semua pasangan |
| Jaccard per cluster setelah pencocokan optimal | 1,000 untuk semua 16 cluster pada semua seed |
| Perubahan ukuran cluster maksimum | 0 foto |
| xsrc / purity BDC / purity eksternal | 0,975411 / 0,992278 / 0,983051 pada semua seed |
| NMI objek eksternal | 0,858603 pada semua seed |

Tidak ada seed terburuk yang berbeda: seluruh 100 label utama identik, sehingga pemetaan centroid, ukuran, dan komposisi cluster juga identik. Failures dan error tercatat per seed dalam [`runs.csv`](runs.csv); label utama dalam [`main_labels.npy`](main_labels.npy); seluruh ARI pasangan dalam [`pairwise_ari.csv`](pairwise_ari.csv). Eksekusi memakai CPU lokal; **biaya Modal baru $0**.

## Batas inferensi

Ini 100 variasi seed pada **embedding, PCA, sampel, dan K yang sama**. Ini tidak mengulang ekstraksi fitur, fitting CMRE, resampling data, atau pelatihan backbone 100 kali. Nilai xsrc yang identik adalah konsistensi algoritmik bersyarat pada input beku, bukan interval kepercayaan generalisasi ataupun 100 dataset uji independen. Laporan A menunjukkan keputusan K masih peka terhadap seed SCMax; pemilihan K=16 tetap perlu dijelaskan sebagai keputusan protokol final.

Versi lokal saat audit: scikit-learn 1.7.2, NumPy 2.3.5, SciPy 1.16.2, pandas 3.0.3. SHA-256 fitur `z_final_v4.npy`: `4f48ffa397ff97cd1016f7454889e385e120983783da553b7f0b090bb9571d99`; assignment final: `bab4fb4cb42fb58a53bcceb3ed0349213e09f8403b16fe097b9a34aeec7e43a1`.

**Kalimat siap pakai untuk paper:** “Pada fitur CMRE/PCA-32 beku dan K=16, 100 pengulangan Spectral-kNN dengan seed 0–99 menghasilkan partisi identik tanpa kegagalan (ARI antarpasangan 1,000; Jaccard setiap cluster 1,000). Audit terpisah terhadap 100 seed pemilihan K oleh SCMax menghasilkan K=13–21, dengan K=16 pada 20 seed dan ARI antarpasangan partisi hybrid rata-rata 0,860. Dengan demikian, variasi utama pada pengaturan ini muncul dari pemilihan K, sedangkan clustering pada K tetap stabil. Pengujian ini tidak mencakup variasi data atau pelatihan ulang backbone.”
