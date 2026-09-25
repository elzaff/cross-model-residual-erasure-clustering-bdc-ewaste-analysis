# Embedding final v4

Diunduh dari volume Modal `bdc-max` pada 25 September 2026. Semua matriks memakai urutan baris yang sama dengan `items.csv` (`id` 0–7564).

| File | Isi | Bentuk | Tipe |
|---|---|---:|---|
| `emb_siglip2.npy` / `emb_siglip2_flip.npy` | SigLIP2-So400m, citra asli / horizontal flip | 7565 × 1152 | float16 |
| `emb_pecoreg.npy` / `emb_pecoreg_flip.npy` | PE-Core-G, citra asli / horizontal flip | 7565 × 1536 | float16 |
| `emb_dinov3hp.npy` / `emb_dinov3hp_flip.npy` | DINOv3-H+, citra asli / horizontal flip | 7565 × 1280 | float16 |
| `z_final_v4.npy` | Fitur gabungan CMRE + PCA-32; input clustering final | 7565 × 32 | float32 |

Untuk mencoba algoritma clustering pada representasi final, gunakan `z_final_v4.npy`. Untuk membandingkan representasi per model, gabungkan pasangan asli/flip dengan normalisasi L2 seperti di pipeline. `final_config_v4.json` mencatat konfigurasi final (K=16).

`items.csv` adalah manifest; baris ke-i cocok dengan baris ke-i di setiap matriks. Jangan urutkan atau acak salah satunya secara terpisah. Baris `set == "main"` (3.792 citra) adalah subset yang dipakai pipeline untuk fitting cluster; `set == "ext"` (3.773 citra) adalah data eksternal. `posthoc_label` hanya untuk evaluasi, jangan dipakai sebagai fitur clustering.

`assignments_final_v4.csv` menyimpan hasil partisi final sebagai pembanding.
