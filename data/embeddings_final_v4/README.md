# Embedding final v4

Diunduh dari volume Modal `bdc-max` pada 25 September 2026. Semua matriks memakai urutan baris yang sama dengan `items.csv` (`id` 0–7564).

| File | Isi | Bentuk | Tipe |
|---|---|---:|---|
| `emb_siglip2.npy` / `emb_siglip2_flip.npy` | SigLIP2-So400m, citra asli / horizontal flip | 7565 × 1152 | float16 |
| `emb_pecoreg.npy` / `emb_pecoreg_flip.npy` | PE-Core-G, citra asli / horizontal flip | 7565 × 1536 | float16 |
| `emb_dinov3hp.npy` / `emb_dinov3hp_flip.npy` | DINOv3-H+, citra asli / horizontal flip | 7565 × 1280 | float16 |
| `emb_aimv2.npy` / `emb_aimv2_flip.npy` | AIMv2-L, citra asli / horizontal flip; tambahan untuk eksperimen fusi | 7565 × 1024 | float16 |
| `z_final_v4.npy` | Fitur gabungan CMRE + PCA-32; input clustering final | 7565 × 32 | float32 |

Untuk mencoba algoritma clustering pada representasi final, gunakan `z_final_v4.npy`. Untuk membandingkan representasi per model, gabungkan pasangan asli/flip dengan normalisasi L2 seperti di pipeline. `final_config_v4.json` mencatat konfigurasi final (K=16).

`items.csv` adalah manifest; baris ke-i cocok dengan baris ke-i di setiap matriks. Jangan urutkan atau acak salah satunya secara terpisah. Baris `set == "main"` (3.792 citra) adalah subset yang dipakai pipeline untuk fitting cluster; `set == "ext"` (3.773 citra) adalah data eksternal. `posthoc_label` hanya untuk evaluasi, jangan dipakai sebagai fitur clustering.

Embedding AIMv2 diunduh dari volume `bdc-max` pada 26 September 2026. SHA-256 manifest di volume cocok dengan `items.csv` lokal. Hasil perbandingan fusi ada di `results/modal/aimv2_fusion_results.csv` dan `results/modal/aimv2_external_results.csv`.

`assignments_final_v4.csv` menyimpan hasil partisi final sebagai pembanding.

Catatan reproduksi: `final_config_v4.json` mempertahankan indeks ambang varians lama `r_siglip2 = r_pecore = 65`. Karena PCA hanya menghitung 64 komponen, proyeksi yang benar-benar diterapkan memakai 64 arah untuk keduanya (`effective_r_*`). Audit selisih hasil hitung ulang dicatat di `results/modal/aimv2_fusion_report.md`.
