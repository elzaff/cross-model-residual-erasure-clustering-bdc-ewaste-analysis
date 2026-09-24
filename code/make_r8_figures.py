"""Round-8 figures from the saved partitions (light, CPU): C4 K=13 -> K=16 refinement, C6 cluster x filename-label heatmap.
Reads results/modal/final_v3|final_v4/assignments.csv, writes results/modal/r8/c4_hierarchy.png, c6_heatmap.png, c4_split.csv."""
import os, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); R = f"{ROOT}/results/modal"; O = f"{R}/r8"; os.makedirs(O, exist_ok=True)
plt.rcParams.update({"font.family": "Times New Roman", "font.size": 9})
NAMES = ["Aki", "Baterai laptop", "Turntable", "TV CRT", "Baterai ponsel/kamera", "Pemutar CD/radio", "Mesin cuci atas", "TV layar datar",
         "Mesin cuci depan", "Laptop", "Keyboard", "Microwave", "Printer", "Mouse", "Ponsel", "PCB/campuran"]
LAB = {"battery": "baterai", "keyboard": "keyboard", "microwave": "microwave", "mobile": "ponsel", "mouse": "mouse", "pcb": "PCB",
       "player": "pemutar", "printer": "printer", "television": "televisi", "washing_machine": "mesin cuci"}
a3, a4 = [pd.read_csv(f"{R}/final_{v}/assignments.csv", dtype={"id": str}) for v in ("v3", "v4")]
m = a4[a4.set == "main"][["id", "cluster", "posthoc_label"]].merge(a3[a3.set == "main"][["id", "cluster"]], on="id", suffixes=("16", "13"))
comma = lambda v, d=2: f"{v:.{d}f}".replace(".", ",")

# ---- C4: each K=16 cluster's parent at K=13 and the share it inherits
ct = pd.crosstab(m.cluster13, m.cluster16); par = ct.idxmax(0); share = ct.max(0) / ct.sum(0)
lab13 = {k: LAB.get(pd.Series(v).mode()[0], "?") for k, v in m[m.posthoc_label.notna()].groupby("cluster13").posthoc_label}
S = pd.DataFrame(dict(k16=range(16), nama16=NAMES, induk13=par.values, induk13_label=[lab13.get(p, "?") for p in par.values], porsi=share.values.round(3)))
S.to_csv(f"{O}/c4_split.csv", index=False); print(S.to_string(index=False))
order13 = sorted(ct.index, key=lambda k: par[par == k].index.min() if (par == k).any() else 99); y13 = {k: i for i, k in enumerate(order13)}
sy = lambda i, n: 1 - i / (n - 1)
fig, ax = plt.subplots(figsize=(5.9, 5.2))
for k13 in ct.index:
    for k16 in ct.columns:
        w = ct.loc[k13, k16] / ct[k16].sum()
        if w >= 0.05: ax.plot([0, 1], [sy(y13[k13], len(y13)), sy(k16, 16)], color="#2b6a43", alpha=min(1, 0.15 + w), lw=0.4 + 3 * w)
for k, i in y13.items(): ax.text(-0.02, sy(i, len(y13)), f"K13-{k} ({lab13.get(k, '?')}, n={ct.loc[k].sum()})", ha="right", va="center", fontsize=7.5)
for k in range(16): ax.text(1.02, sy(k, 16), f"C{k} {NAMES[k]} (n={ct[k].sum()})", ha="left", va="center", fontsize=7.5)
ax.set_xlim(-0.9, 1.9); ax.axis("off"); ax.set_title("Pemecahan kelompok K = 13 menjadi K = 16 (garis: porsi citra ≥ 5%)", fontsize=9)
fig.savefig(f"{O}/c4_hierarchy.png", dpi=300, bbox_inches="tight"); plt.close(fig)

# ---- C6: cluster x BDC filename label, row-normalised (only labelled training images)
L = m[m.posthoc_label.notna() & (m.posthoc_label != "")]; H = pd.crosstab(L.cluster16, L.posthoc_label.map(LAB), normalize="index")
fig, ax = plt.subplots(figsize=(5.9, 5.0)); ax.imshow(H.values, cmap="Greens", vmin=0, vmax=1, aspect="auto")
ax.set_xticks(range(H.shape[1]), H.columns, rotation=40, ha="right"); ax.set_yticks(range(len(H)), [f"C{k} {NAMES[k]}" for k in H.index])
for i in range(H.shape[0]):
    for j in range(H.shape[1]):
        if H.values[i, j] >= 0.02: ax.text(j, i, comma(H.values[i, j]), ha="center", va="center", fontsize=6.5, color="white" if H.values[i, j] > 0.6 else "black")
ax.set_xlabel("Label nama berkas BDC (hanya evaluasi)"); ax.set_title("Komposisi label per kelompok (proporsi baris)", fontsize=9)
fig.savefig(f"{O}/c6_heatmap.png", dpi=300, bbox_inches="tight"); plt.close(fig)
print("labelled", len(L), "| clusters with max share >= 0.9:", int((H.max(1) >= 0.9).sum()), "/", len(H))
