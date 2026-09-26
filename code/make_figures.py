"""Figures for the final paper (reads the result CSVs / galleries produced on Modal; light local plotting only).
Writes paper_draft/fig/fig{1..7}_*.png at 300 dpi, 15 cm wide (A4 text width with 3 cm margins)."""
import os, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Patch
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R, PA, OUT = f"{ROOT}/results/modal", f"{ROOT}/results/modal/paper", f"{ROOT}/paper_draft/fig"
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"font.family": "Times New Roman", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titlesize": 9.5, "axes.titleweight": "bold", "legend.frameon": False})
W = 15 / 2.54
C = {"raw": "#9e9e9e", "dino": "#4c78a8", "inlp": "#b279a2", "cmre": "#e45756", "light": "#f58518", "vlm": "#e45756", "ssl": "#4c78a8", "sup": "#72b7b2"}
def save(fig, name): fig.savefig(f"{OUT}/{name}.png", dpi=300, bbox_inches="tight"); plt.close(fig)
def crop(path, n, w=200): im = Image.open(path).convert("RGB"); return np.asarray(im.crop((0, 0, min(im.width, int(w * n)), im.height)))

# ---- Fig 1: sources and data characteristics
fig = plt.figure(figsize=(W, W * 0.78)); gs = fig.add_gridspec(5, 2, height_ratios=[1, 1, 1, 1, 3.4], hspace=0.5, wspace=0.08)
rows = [("bdc", "BDC (data utama)"), ("iliev", "Iliev (uji terkunci)"), ("kaan", "Kaan (citra produk)"), ("shubha", "Shubha (uji segar)"),
        ("bangla", "Bangladesh (foto objek)"), ("oh_product", "Office-Home Product"), ("giz", "GIZ (foto lapangan)"), ("oh_realworld", "Office-Home Real World")]
for i, (k, t) in enumerate(rows):
    ax = fig.add_subplot(gs[i // 2, i % 2]); ax.imshow(crop(f"{PA}/src_{k}.jpg", 5)); ax.set_axis_off(); ax.set_title(t, fontsize=8, loc="left", pad=2)
it = pd.read_csv(f"{R}/items.csv"); it["side"] = it[["width", "height"]].max(axis=1)
it["src"] = it.source.replace({"bdc_test": "bdc"}); rng = np.random.default_rng(0)
ax = fig.add_subplot(gs[4, :])
for s, lab, col in (("bdc", "BDC", "#e45756"), ("kaan", "Kaan", "#4c78a8"), ("karan", "Karan", "#72b7b2"), ("bangla", "Bangladesh", "#f58518"), ("giz", "GIZ", "#54a24b")):
    d = it[it.src == s]
    ax.scatter(d.side * np.exp(rng.normal(0, .04, len(d))), d.border_white + rng.normal(0, .015, len(d)), s=3, alpha=.35, color=col,
               label=f"{lab} (n={len(d):,})".replace(",", "."), rasterized=True)
ax.set_xscale("log"); ax.set_xlabel("Resolusi sisi terpanjang (piksel, skala log)"); ax.set_ylabel("Proporsi tepi berlatar putih")
ax.legend(loc="center right", markerscale=4, fontsize=8); ax.set_title("(b) Sebaran karakteristik akuisisi per sumber", loc="left")
fig.text(0.0, 0.985, "(a) Objek yang sama (mouse) dari sumber berbeda; baris GIZ berisi foto lapangan acak", fontsize=9.5, weight="bold")
save(fig, "fig1_data")

# ---- Fig 2: flowchart
fig, ax = plt.subplots(figsize=(W, W * 0.62)); ax.set_xlim(0, 100); ax.set_ylim(0, 62); ax.set_axis_off()
def box(x, y, w, h, title, body, fc):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.5", fc=fc, ec="#333333", lw=0.8))
    ax.text(x + w / 2, y + h - 2.2, title, ha="center", va="top", weight="bold", fontsize=8.5)
    ax.text(x + w / 2, y + h - 6.4, body, ha="center", va="top", fontsize=7.3, linespacing=1.25)
def arrow(x1, y1, x2, y2): ax.annotate("", (x2, y2), (x1, y1), arrowprops=dict(arrowstyle="-|>", lw=1.1, color="#333333"))
G, B, O, Gr = "#eeeeee", "#dbe8f5", "#fde2c8", "#d9efd4"
box(0.5, 38, 22, 22, "1. Input", "3.604 citra e-waste\ndata latih BDC\n+ 188 citra uji\n(dipilah otomatis)", G)
box(26, 38, 22, 22, "2. Pra-pemrosesan", "deduplikasi pHash\n(Hamming ≤ 6)\nresize + flip (TTA)\ntanpa teks/label", B)
box(51.5, 38, 22, 22, "3. Ekstraksi fitur", "SigLIP2-So400m (VLM)\nPE-Core-G (VLM)\nDINOv3-H+ (SSL)\n→ embedding global", B)
box(77, 38, 22.5, 22, "4. CMRE (usulan)", "hapus residu VLM\nyang tak dijelaskan\nDINOv3 (r = 64)\n→ bias sumber turun", O)
box(77, 8, 22.5, 22, "5. Fusi + PCA-32", "gabung 3 embedding\nbersih, PCA-32,\nnormalisasi L2", B)
box(51.5, 8, 22, 22, "6. Penentuan K", "SCMax (AAAI-26)\n9 seed → median\nK = 16 (tingkat\nkasar K = 13)", O)
box(26, 8, 22, 22, "7. Clustering", "Spectral-kNN\n(n_neighbors = 15)\nK-Means, Ward, GMM\nsebagai pembanding", B)
box(0.5, 8, 22, 22, "8. Output", "16 cluster e-waste\n+ taksonomi WEEE/B3\n+ skor OOD kNN\n(\"tidak dikenal\")", Gr)
for a in ((22.9, 49, 25.6, 49), (48.4, 49, 51.1, 49), (73.9, 49, 76.6, 49), (88.2, 37.6, 88.2, 30.4), (76.6, 19, 73.9, 19), (51.1, 19, 48.4, 19), (25.6, 19, 22.9, 19)):
    arrow(*a)
ax.text(50, 3.2, "Validasi (hanya evaluasi, diproyeksikan ke centroid): Kaan, Bangladesh, Karan, GIZ · Iliev 69 kelas (protokol dikunci) · Shubha (uji segar) · Office-Home (domain lain)",
        ha="center", fontsize=7.3, style="italic", color="#444444")
save(fig, "fig2_flow")

# ---- Fig 3: source bias across backbones + t-SNE before/after CMRE
mr = pd.read_csv(f"{R}/max_reps.csv").groupby("rep").xsrc_agree.mean()
models = [("DINOv3-H+", "ssl"), ("DINOv3-B", "ssl"), ("DINOv3-7B", "ssl"), ("DINOv3-L", "ssl"), ("DINOv2-L", "ssl"), ("ConvNeXt V2-H (IN-22k)", "sup"),
          ("AIMv2-L", "vlm"), ("CLIP ConvNeXt-XXL", "vlm"), ("PE-Core-G", "vlm"), ("SigLIP2-giant", "vlm"), ("SigLIP2-So400m", "vlm"), ("CLIP-L/14", "vlm")]
fig = plt.figure(figsize=(W, W * 0.78)); gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.35], hspace=0.42, wspace=0.12)
ax = fig.add_subplot(gs[0, :]); y = np.arange(len(models))
ax.barh(y, [mr[m] for m, _ in models], color=[C[f] for _, f in models]); ax.set_yticks(y, [m.replace(" (IN-22k)", "") for m, _ in models], fontsize=7.5); ax.invert_yaxis()
for i, (m, _) in enumerate(models): ax.text(mr[m] + .01, i, f"{mr[m]:.2f}".replace(".", ","), va="center", fontsize=7)
ax.set_xlim(0, 1); ax.set_xlabel("Konsistensi lintas sumber (xsrc) — model tunggal tanpa perlakuan")
ax.legend(handles=[Patch(color=C["ssl"], label="Self-supervised (tanpa bahasa)"), Patch(color=C["sup"], label="Terawasi"), Patch(color=C["vlm"], label="Visi-bahasa")],
          loc="lower right", fontsize=7.5)
ax.set_title("(a) Model visi-bahasa cenderung mengelompokkan menurut sumber foto", loc="left")
ts = pd.read_csv(f"{PA}/tsne.csv"); cols = {"battery": "#e45756", "keyboard": "#4c78a8", "mobile": "#54a24b", "mouse": "#f58518", "pcb": "#b279a2"}
nm = {"battery": "baterai", "keyboard": "keyboard", "mobile": "ponsel", "mouse": "mouse", "pcb": "PCB"}
for j, (k, t) in enumerate((("raw", "(b) Fusi mentah: xsrc 0,52"), ("cmre", "(c) Setelah CMRE: xsrc 0,98"))):
    ax = fig.add_subplot(gs[1, j])
    for c, col in cols.items():
        for s, mk in (("kaan", "o"), ("bangla", "^")):
            d = ts[(ts.label == c) & (ts.source == s)]
            ax.scatter(d[f"x_{k}"], d[f"y_{k}"], s=6 if s == "kaan" else 11, marker=mk, color=col, alpha=.55 if s == "kaan" else .9,
                       edgecolor="none" if s == "kaan" else "black", linewidth=.3, label=nm[c] if s == "kaan" else None, rasterized=True)
    ax.set_xticks([]); ax.set_yticks([]); ax.set_title(t, loc="left")
    if j == 1: ax.legend(fontsize=7.5, loc="upper center", bbox_to_anchor=(-0.06, -0.03), ncol=5, markerscale=2)
fig.text(0.5, 0.015, "warna = objek; bulat = citra produk (Kaan); segitiga bergaris tepi = foto objek (Bangladesh)", ha="center", fontsize=7.5, style="italic")
save(fig, "fig3_bias")

# ---- Fig 4: xsrc across evaluation sets
sets = ["BDC\n(pengembangan)", "Iliev\n(uji terkunci)", "Shubha\n(uji segar)", "Office-Home\n(domain lain)"]
vals = {"Fusi mentah": [0.524, 0.803, 0.356, 0.865], "DINOv3-H+ saja": [0.758, 0.755, 0.889, 0.761], "INLP ×3 (butuh proksi)": [0.975, 0.887, 0.972, 0.870],
        "CMRE usulan (tanpa proksi)": [0.975, 0.885, 0.956, 0.864]}
cc = [C["raw"], C["dino"], C["inlp"], C["cmre"]]
fig, ax = plt.subplots(figsize=(W, W * 0.36)); x = np.arange(4); bw = 0.2
for i, (k, v) in enumerate(vals.items()):
    ax.bar(x + (i - 1.5) * bw, v, bw, color=cc[i], label=k)
    for xi, vi in zip(x + (i - 1.5) * bw, v): ax.text(xi, vi + .012, f"{vi:.2f}".replace(".", ","), ha="center", fontsize=6.3, rotation=90)
ax.set_xticks(x, sets); ax.set_ylim(0, 1.13); ax.set_ylabel("xsrc (↑ lebih baik)"); ax.legend(ncol=4, fontsize=7.3, loc="upper center", bbox_to_anchor=(0.5, 1.16))
save(fig, "fig4_results")

# ---- Fig 5: K choice and parameter robustness
ks, fx, al = pd.read_csv(f"{PA}/ksweep.csv"), pd.read_csv(f"{R}/fix_results.csv"), pd.read_csv(f"{PA}/algo16.csv")
fig, axs = plt.subplots(2, 2, figsize=(W, W * 0.8)); plt.subplots_adjust(hspace=0.8, wspace=0.32)
ax = axs[0, 0]; ax.plot(ks.K, ks.xsrc_agree, "-o", ms=3, color=C["cmre"], label="xsrc"); ax.plot(ks.K, ks.purity_bdc, "-s", ms=3, color=C["dino"], label="purity BDC")
ax.plot(ks.K, ks.sil * 2, "--", color="#666666", label="silhouette ×2"); ax.set_ylim(0.35, 1.04); ax.set_xlabel("Jumlah cluster K")
picks = pd.Series([13, 16, 13, 16, 19, 16, 15, 19, 19]).value_counts()
ax.scatter(picks.index, [0.4] * len(picks), s=picks.values * 28, marker="v", color=C["light"], label="pilihan SCMax (ukuran = jumlah seed)", zorder=3)
ax.axvline(16, color=C["cmre"], lw=.8, ls=":"); ax.legend(fontsize=6.5, loc="upper center", bbox_to_anchor=(.5, -.28), ncol=2)
ax.set_title("(a) Pemilihan K tanpa label (SCMax)", loc="left")
rr = fx[fx.method.str.match(r"R r=")]; ax = axs[0, 1]
ax.plot(rr.r, rr.xsrc_agree, "-o", ms=3.5, color=C["cmre"]); ax.set_xscale("log", base=2); ax.axvspan(16, 64, color=C["cmre"], alpha=.1)
ax.set_xticks([4, 8, 16, 32, 64, 128, 256], ["4", "8", "16", "32", "64", "128", "256"]); ax.set_ylim(0.4, 1.02)
ax.set_xlabel("Jumlah arah residu yang dihapus (r)"); ax.set_ylabel("xsrc")
ax.text(32, 0.5, "plateau\nr = 16–64", ha="center", fontsize=7.5, color=C["cmre"]); ax.set_title("(b) Sensitivitas parameter CMRE", loc="left")
ax = axs[1, 0]; a = al.set_index("method").loc[["Spectral-kNN nn=15 (v4)", "K-Means", "Agglomerative-Ward", "GMM (diag)"]]; x = np.arange(4)
for i, (col, nmx, c) in enumerate((("xsrc_agree", "xsrc", C["cmre"]), ("purity_bdc", "purity BDC", C["dino"]), ("ext_obj_nmi", "NMI objek", C["inlp"]))):
    ax.bar(x + (i - 1) * .26, a[col], .26, color=c, label=nmx)
ax.set_xticks(x, ["Spectral\n(usulan)", "K-Means", "Ward", "GMM"], fontsize=7.5); ax.set_ylim(0.6, 1.05)
ax.legend(fontsize=6.5, ncol=3, loc="upper center", bbox_to_anchor=(.5, 1.13)); ax.set_title("(c) Perbandingan algoritma (K = 16)", loc="left", pad=14)
ax = axs[1, 1]; nn = al[al.method.str.startswith("Spectral")].copy(); nn["nn"] = nn.method.str.extract(r"nn=(\d+)")[0].astype(int); nn = nn.sort_values("nn")
ax.plot(nn.nn, nn.xsrc_agree, "-o", ms=3.5, color=C["cmre"], label="xsrc"); ax.plot(nn.nn, nn.purity_bdc, "-s", ms=3.5, color=C["dino"], label="purity BDC")
ax.plot(nn.nn, nn.ari_v4, "-^", ms=3.5, color="#666666", label="ARI thd. partisi final"); ax.set_ylim(0.6, 1.02); ax.set_xlabel("n_neighbors graf kNN")
ax.legend(fontsize=6.5, loc="lower right"); ax.set_title("(d) Sensitivitas graf Spectral", loc="left")
save(fig, "fig5_params")

# ---- Fig 6: cluster gallery (5 representative images per cluster)
names = ["C0 · Aki (timbal-asam)", "C1 · Baterai pack laptop", "C2 · Turntable", "C3 · TV/monitor CRT", "C4 · Baterai ponsel/kamera", "C5 · Pemutar CD/radio",
         "C6 · Mesin cuci bukaan atas", "C7 · TV/monitor layar datar", "C8 · Mesin cuci front-load", "C9 · Laptop", "C10 · Keyboard", "C11 · Microwave",
         "C12 · Printer", "C13 · Mouse", "C14 · Ponsel", "C15 · PCB & tumpukan campuran"]
n16 = [115, 70, 111, 174, 136, 153, 115, 263, 192, 277, 320, 275, 294, 291, 366, 640]
PICK = {15: [0, 1, 2, 6, 9]}  # manual: other C15 tiles show stock watermarks or a person
fig = plt.figure(figsize=(W, W * 1.02)); gs = fig.add_gridspec(8, 2, hspace=0.42, wspace=0.05)
for c in range(16):
    g = Image.open(f"{R}/r8/gallery_clean/c{c:02d}.jpg").convert("RGB"); tw = g.width / 8  # face-free, >= 150 px, not dark (rq_gallery.py)
    tiles = [np.asarray(g.crop((int(i % 8 * tw), int(i // 8 * tw), int((i % 8 + 1) * tw), int((i // 8 + 1) * tw)))) for i in PICK.get(c, range(5))]
    ax = fig.add_subplot(gs[c % 8, c // 8]); ax.imshow(np.hstack(tiles)); ax.set_axis_off()
    ax.set_title(f"{names[c]} (n={n16[c]})", fontsize=7.8, loc="left", pad=1.5)
save(fig, "fig6_clusters")

# ---- Fig 7: open-set behaviour with kNN-OOD
od = pd.read_csv(f"{PA}/ood_knn.csv")
sel = [("iliev", "Battery", "Baterai"), ("iliev", "Computer-Mouse", "Mouse"), ("iliev", "Smartphone", "Ponsel"), ("iliev", "Washing-Machine", "Mesin cuci"),
       ("iliev", "CRT-TV", "TV CRT"), ("iliev", "PCB", "PCB"), ("shubha", "Keyboard", "Keyboard (Shubha)"),
       ("iliev", "Air-Conditioner", "AC"), ("iliev", "Refrigerator", "Kulkas"), ("iliev", "Clothes-Iron", "Setrika"), ("iliev", "Floor-Fan", "Kipas angin"),
       ("iliev", "LED-Bulb", "Lampu LED"), ("iliev", "Cooled-Dispenser", "Dispenser air"), ("iliev", "Music-Player", "Pemutar MP3"), ("shubha", "Remote", "Remote (Shubha)")]
v = [float(od[(od.set == s) & (od.name == n)].flag.iloc[0]) for s, n, _ in sel]; known = [i < 7 for i in range(len(sel))]
fig = plt.figure(figsize=(W, W * 0.62)); gs = fig.add_gridspec(1, 2, width_ratios=[1.05, 1], wspace=0.25)
ax = fig.add_subplot(gs[0]); y = np.arange(len(sel))
ax.barh(y, v, color=[C["dino"] if k else C["cmre"] for k in known]); ax.set_yticks(y, [t for *_, t in sel], fontsize=7.5); ax.invert_yaxis(); ax.set_xlim(0, 1.12)
for i, vi in enumerate(v): ax.text(vi + .02, i, f"{vi * 100:.0f}%", va="center", fontsize=7)
ax.set_xlabel("Proporsi ditandai \"tidak dikenal\""); ax.axhline(6.5, color="#999999", lw=.6, ls="--")
ax.legend(handles=[Patch(color=C["dino"], label="kategori ada di BDC"), Patch(color=C["cmre"], label="kategori baru")], fontsize=7, loc="upper center", bbox_to_anchor=(.45, -.14), ncol=2)
ax.set_title("(a) Deteksi OOD kNN pada data uji", loc="left")
ax = fig.add_subplot(gs[1]); g = Image.open(f"{R}/r8/gallery_clean/giz_ood.jpg").convert("RGB"); tw = g.width / 8
ax.imshow(np.asarray(g.crop((0, 0, int(tw * 4), g.height)))); ax.set_axis_off(); ax.set_title("(b) Foto lapangan GIZ yang ditandai", loc="left")
save(fig, "fig7_ood")
print("figures ->", OUT, sorted(os.listdir(OUT)))
