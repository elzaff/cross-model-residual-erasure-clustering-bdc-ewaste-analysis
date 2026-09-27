# Audit partisi SCMax, Spectral, dan Ward

## Mekanisme

SCMax asli menghasilkan partisi bertingkat: modul `NeighborClustering.step` menghubungkan pusat kelompok ke tetangga terdekat dan memakai connected components untuk menggabungkannya. Autoencoder dan `BackFeature` memperbarui representasi di antara tingkat. Nilai NNC memilih satu partisi dari hierarki tersebut. Pipeline final mengambil **K** yang disarankan SCMax, tetapi membentuk **anggota kelompok baru** dengan Spectral-kNN pada CMRE/PCA-32. Jadi pipeline final adalah hibrida, bukan keluaran SCMax asli.

## Seluruh 100 seed Modal L4

| Tingkat penggabungan | Seed tersedia | K (rentang; median) | Rerata NNC | Rerata silhouette Euclidean | Rerata xsrc | Rerata purity BDC |
|---|---:|---|---:|---:|---:|---:|
| 1, paling halus | 100 | 188–234; 219 | 0,460 | 0,072 | 0,023 | 0,989 |
| 2 | 100 | 49–65; 58,5 | 0,599 | 0,211 | 0,168 | 0,984 |
| 3 | 100 | 13–21; 16,5 | 0,790 | 0,326 | 0,731 | 0,969 |
| 4, paling kasar | 55 | 4–9; 6 | 0,529 | 0,202 | 0,962 | 0,584 |

Tingkat keempat hanya ada pada 55 seed. xsrc yang tinggi pada tingkat sangat kasar bukan keberhasilan pengenalan objek: banyak kategori bergabung dan purity jatuh. Tabel lengkap ada di `levels_100_seeds.csv`.

Pada 20 seed yang memilih **K=16**, partisi SCMax asli memiliki rerata silhouette Euclidean **0,319**, xsrc **0,744**, purity BDC **0,965**, dan source conditional NMI **0,086**. Spectral pada K yang sama memberi **0,364**, **0,975**, **0,992**, dan **0,040**. Spectral memakai partisi deterministik yang sama pada seluruh 20 baris; baris itu bukan 20 ulangan Spectral independen. Perbandingan seluruh K ada di `native_vs_spectral_by_K.csv`. Keunggulan Spectral tidak berlaku untuk semua K dan semua metrik; pada K=20 xsrc asli SCMax **0,643**, Spectral **0,596**.

Sebagai pembanding pada **K=16**, Ward mendapat silhouette cosine **0,552** dan xsrc **0,836**, sedangkan Spectral mendapat **0,515** dan **0,975**. Silhouette tinggi pada embedding tidak otomatis berarti konsistensi lintas sumber tinggi.

## Audit keanggotaan satu seed lokal

Label per foto pada setiap tingkat Modal tidak tersimpan. Saat seed 1 dijalankan ulang dengan input yang sama pada RTX 3050 lokal, tingkat yang muncul adalah **230 → 58 → 14**, berbeda dari catatan Modal L4 **219 → 60 → 16 → 6**. Karena itu `seed1_levels.npz`, `seed1_partition_comparison.csv`, dan `seed1_local_metrics.csv` adalah ilustrasi run lokal, **bukan** rekonstruksi partisi Modal yang identik.

Pada tingkat lokal K=14, ARI partisi SCMax asli terhadap Spectral K=14 adalah **0,567**. Silhouette cosine pada ruang CMRE/PCA-32: SCMax asli **0,400**, Spectral **0,493**, Ward **0,539**. xsrc berturut-turut **0,882**, **0,972**, dan **0,836**. Satu kelompok SCMax lokal yang berisi 648 foto menyatukan bagian dari kelompok layar datar, CD/radio, turntable, CRT, dan aki pada partisi final; rincian irisan ada di `local_level2_native_vs_final16.csv`.

Silhouette cosine di atas dihitung pada **ruang CMRE/PCA-32 yang sama** untuk semua partisi. SCMax asli belajar representasi autoencoder tersendiri, sehingga perbandingan ini tidak mengisolasi efek algoritma clustering dari efek representasi. Untuk menghitung cosine silhouette persis pada partisi Modal, label per foto harus disimpan saat run Modal berikutnya.
