# Audit visual kelompok tambahan K=17

`k17_visual_audit.py` menjalankan Spectral-kNN pada `z_final_v4.npy` dengan K=17, seed 0, 15 tetangga, dan `cluster_qr`. ID foto dipetakan ke berkas asli melalui urutan `data/manifest.csv`; seluruh 3.792 ekstensi berkas dan keberadaan path cocok. Galeri mengambil 18 foto terdekat pusat, 30 foto acak (seed 2026), dan sampel menurut kelompok K=16 asal. Ini sampel untuk interpretasi, bukan pelabelan menyeluruh.

Kelompok tambahan K=17 (label komputasi 11) berisi 468 foto; 463 tidak memiliki label evaluasi. Foto dekat pusat menunjukkan tumpukan e-waste, halaman pengumpulan, dan banyak monitor CRT bekas. Sampel acak juga berisi monitor/TV tunggal, komputer dan keyboard, stopkontak, ponsel, serta beberapa foto tumpukan campuran. Anggotanya berasal terutama dari C15 K=16 (243 foto), C7 (64), C3 (60), C0 (48), dan C10 (44).

Pecahan C15 lainnya (label komputasi 16; 397 foto) pada sampel dekat pusat dan acak tampak didominasi PCB dan papan rangkaian. Dengan demikian, K=17 memisahkan foto PCB dari banyak adegan tumpukan/area pengumpulan yang sebelumnya bergabung di C15, sekaligus mengumpulkan foto konteks atau ambigu dari kelompok lain. Kelompok tambahan lebih tepat disebut **tumpukan e-waste/perangkat campuran yang perlu pra-pemilahan**, bukan kelas perangkat baru yang homogen. Karena mayoritas foto tidak berlabel dan hanya sampel yang diperiksa, nama ini bersifat interpretasi visual awal.

- `nearest_centroid.jpg`: 18 foto terdekat pusat kelompok tambahan.
- `random_30.jpg`: 30 foto acak dari kelompok tambahan.
- `by_k16_origin.jpg`: sampel menurut kelompok K=16 asal.
- `k17_group16_nearest.jpg` dan `k17_group16_random.jpg`: pembanding kelompok PCB K=17.
- `group11_members.csv`: seluruh 468 anggota dan jaraknya dari pusat.
