"""Copies the result images into dashboard/assets and writes dashboard/data.js from the real result CSVs.
Only the cluster names and handling notes (from the gallery review) and the published statistics are written by hand."""
import json, os, shutil
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R, PA, D = f"{ROOT}/results/modal", f"{ROOT}/results/modal/paper", f"{ROOT}/dashboard"
os.makedirs(f"{D}/assets", exist_ok=True)
# face-free galleries (no detected faces, not dark, >= 150 px; code/pipeline/rq_gallery.py)
for c in range(16): shutil.copy(f"{R}/r8/gallery_clean/c{c:02d}.jpg", f"{D}/assets/c{c:02d}.jpg")
shutil.copy(f"{R}/r8/gallery_clean/giz_ood.jpg", f"{D}/assets/giz_ood.jpg")
for k in ("bdc", "kaan", "bangla", "giz", "iliev", "shubha", "oh_product", "oh_realworld"): shutil.copy(f"{PA}/src_{k}.jpg", f"{D}/assets/src_{k}.jpg")

r3 = lambda v: round(float(v), 3)
mr = pd.read_csv(f"{R}/max_reps.csv").groupby("rep").xsrc_agree.mean()
backbones = [dict(name=n, fam=f, xsrc=r3(mr[n])) for n, f in (
    ("DINOv3-H+", "ssl"), ("DINOv3-B", "ssl"), ("DINOv3-7B", "ssl"), ("DINOv3-L", "ssl"), ("DINOv2-L", "ssl"), ("ConvNeXt V2-H (IN-22k)", "sup"),
    ("CLIP ConvNeXt-XXL", "vlm"), ("PE-Core-G", "vlm"), ("SigLIP2-giant", "vlm"), ("SigLIP2-So400m", "vlm"), ("CLIP-L/14", "vlm"))]

f2 = pd.read_csv(f"{R}/final2_results.csv").set_index("method"); fx = pd.read_csv(f"{R}/fix_results.csv").set_index("method")
il = pd.read_csv(f"{R}/iliev_results.csv").set_index("method"); sh = pd.read_csv(f"{R}/shubha_results.csv").set_index("method")
oh = pd.read_csv(f"{R}/officehome_results.csv").set_index("method")
ood_methods = pd.read_csv(f"{R}/fix2_results.csv").set_index("method")
fb = pd.read_csv(f"{R}/r8/r8b_fast.csv").set_index("variant").loc["cepat CMRE(SigLIP2)+DINOv3"]  # fast variant without PE-Core-G
datasets = [
    dict(id="bdc", name="BDC", role="data pengembangan", n=3792, metric="xsrc 5 kelas (citra produk Kaan vs foto objek Bangladesh), K = 16",
         raw=r3(f2.loc["FB fusi mentah sig+pe+dino", "xsrc_agree"]), dino=r3(fx.loc["BASE DINOv3-H+ saja K=16", "xsrc_agree"]),
         inlp=r3(f2.loc["FB INLP(sig)+INLP(pe)+INLP(dino)", "xsrc_agree"]), cmre=r3(f2.loc["FB CMRE(sig)+CMRE(pe)+dino [usulan]", "xsrc_agree"]),
         light=r3(fx.loc["BASE ringan CMRE(pe)+dinoH+ K=16", "xsrc_agree"]), ci="0,958 sampai 0,989", purity=0.992, fast=r3(fb.xsrc_BDC)),
    dict(id="iliev", name="Iliev", role="data pengembangan", n=1751, metric="xsrc 10 kelas; protokol awal dikunci sebelum data diunduh, lalu dipakai memilih setelan OOD",
         raw=r3(il.loc["fusi mentah", "xsrc10"]), dino=r3(il.loc["DINOv3-H+ saja", "xsrc10"]), inlp=r3(il.loc["INLP x3", "xsrc10"]),
         cmre=r3(il.loc["usulan v4", "xsrc10"]), light=r3(il.loc["ringan CMRE(pe)+dino", "xsrc10"]), ci="0,864 sampai 0,908", purity=r3(il.loc["usulan v4", "purity"]), fast=r3(fb.xsrc_Iliev)),
    dict(id="shubha", name="Shubha", role="uji segar", n=300, metric="xsrc 3 kelas sepadan yang tersedia (keyboard, ponsel, mouse); 3 dari 4 kelas rencana",
         raw=r3(sh.loc["fusi mentah", "xsrc4"]), dino=r3(sh.loc["DINOv3-H+ saja", "xsrc4"]), inlp=r3(sh.loc["INLP x3", "xsrc4"]),
         cmre=r3(sh.loc["usulan v4", "xsrc4"]), light=None, ci="0,924 sampai 0,983", purity=r3(sh.loc["usulan v4", "purity"]), fast=r3(fb.xsrc_Shubha)),
    dict(id="oh", name="Office-Home", role="domain lain", n=2917, metric="xsrc 20 kelas (Product vs Real World), K = 20",
         raw=r3(oh.loc["fusi mentah", "xsrc"]), dino=r3(oh.loc["DINOv3-H+ saja", "xsrc"]), inlp=r3(oh.loc["INLP x3", "xsrc"]),
         cmre=r3(oh.loc["usulan CMRE", "xsrc"]), light=r3(oh.loc["ringan CMRE(pe)+dino", "xsrc"]), ci=None, purity=r3(oh.loc["usulan CMRE", "purity"]), fast=None)]

ks = pd.read_csv(f"{PA}/ksweep.csv"); al = pd.read_csv(f"{PA}/algo16.csv").set_index("method"); rs = fx[fx.index.str.match(r"R r=")]
robust = dict(
    k=[dict(K=int(a.K), xsrc=r3(a.xsrc_agree), purity=r3(a.purity_bdc), sil=r3(a.sil)) for a in ks.itertuples()],
    scmax=[13, 16, 13, 16, 19, 16, 15, 19, 19],  # scmax_results.csv, CMRE features, 9 seeds
    r=[dict(r=int(v.r), xsrc=r3(v.xsrc_agree)) for v in rs.itertuples()],
    algo=[dict(name=n, xsrc=r3(al.loc[m, "xsrc_agree"]), purity=r3(al.loc[m, "purity_bdc"]), sil=r3(al.loc[m, "sil"]))
          for n, m in (("Spectral (usulan)", "Spectral-kNN nn=15 (v4)"), ("K-Means", "K-Means"), ("Ward", "Agglomerative-Ward"), ("GMM", "GMM (diag)"))])

J = pd.read_csv(f"{R}/fix2_jaccard.csv").sort_values("cluster").jaccard_mean.tolist()
C = [("Aki (baterai timbal-asam)", "baterai", True, "Mengandung timbal dan asam sulfat. Setor ke pengumpul aki khusus, jangan dibongkar sendiri.", "Baterai"),
     ("Baterai pack laptop", "baterai", True, "Sel Li-ion berisiko terbakar bila tertusuk. Lepas dari perangkat sebelum dicacah.", "Baterai laptop"),
     ("Turntable", "kecil", False, "Peralatan kecil. Plastik, logam, dan motor kecil dipisah saat pembongkaran.", "Pemutar audio"),
     ("TV/monitor CRT", "layar", True, "Kaca tabung mengandung timbal. Perlu perlakuan selektif, jangan dipecahkan.", "Televisi"),
     ("Baterai ponsel/kamera", "baterai", True, "Li-ion kecil. Kumpulkan di titik kumpul baterai terpisah.", "Baterai"),
     ("Pemutar CD/radio", "kecil", False, "Peralatan kecil. Bongkar untuk memisahkan PCB, logam, dan plastik.", "Pemutar audio"),
     ("Mesin cuci bukaan atas", "besar", False, "Peralatan besar. Logam dan motornya bernilai jual.", "Mesin cuci atas"),
     ("TV/monitor layar datar", "layar", True, "LCD lama dapat memakai lampu latar bermerkuri. Tangani sebagai layar.", "Televisi"),
     ("Mesin cuci front-load", "besar", False, "Peralatan besar. Logam dan motornya bernilai jual.", "Mesin cuci depan"),
     ("Laptop", "layar", True, "Ada baterai, layar, dan PCB bernilai. Lepas baterai lebih dulu.", "Laptop"),
     ("Keyboard", "ti", False, "TI kecil, dominan plastik.", "Keyboard"),
     ("Microwave", "kecil", True, "Kapasitor tegangan tinggi dapat menyimpan listrik. Dibongkar petugas terlatih.", "Microwave"),
     ("Printer", "ti", False, "TI kecil. Kartrid toner dipisah sebelum dicacah.", "Printer"),
     ("Mouse", "ti", False, "TI kecil, dominan plastik.", "Mouse"),
     ("Ponsel", "ti", True, "Baterai dan PCB bernilai. Baterai dilepas lebih dulu.", "Ponsel"),
     ("PCB dan tumpukan campuran", "komponen", True, "Papan sirkuit mengandung logam mulia dan B3. Perlu pra-pemilahan.", "PCB")]
N = pd.read_csv(f"{R}/final_v4/cluster_profile.csv").sort_values("cluster").n.tolist()
clusters = [dict(id=i, name=n, n=int(N[i]), cat=cat, b3=b3, handling=h, parent=p, jaccard=r3(J[i])) for i, (n, cat, b3, h, p) in enumerate(C)]
import ast
LABID = {"battery": "baterai", "keyboard": "keyboard", "microwave": "microwave", "mobile": "ponsel", "mouse": "mouse", "pcb": "PCB",
         "player": "pemutar", "printer": "printer", "television": "televisi", "washing_machine": "mesin cuci"}
for c, a in zip(clusters, pd.read_csv(f"{R}/final_v4/cluster_profile.csv").sort_values("cluster").itertuples()):
    top = ast.literal_eval(a.top_bdc); k = next(iter(top), None)  # evaluation labels of the labelled training photos only
    c.update(test_n=int(a.test_n), agree3=r3(a.agree3), white_bg=r3(a.white_bg), unlabeled=r3(a.unlabeled), giz_n=int(a.giz_n),
             top_label=LABID.get(k, "–"), top_share=r3(top[k]) if k else None)
# per-photo membership for download (no labels, no paths)
A4 = pd.read_csv(f"{R}/final_v4/assignments.csv", dtype={"id": str}); A4 = A4[A4.set == "main"]
pd.DataFrame(dict(id=A4.id, sumber=A4.source.map({"bdc": "latih", "bdc_test": "uji"}), kelompok=A4.cluster,
                  nama_kelompok=A4.cluster.map(lambda k: C[k][0]), kategori=A4.cluster.map(lambda k: C[k][1]),
                  sepakat_3_algoritma=(A4.consensus == 2).astype(int), jarak_ke_pusat=A4.dist.round(4))).to_csv(f"{D}/assets/kelompok_bdc.csv", index=False)

od = pd.read_csv(f"{PA}/ood_knn.csv")
def ood(s, n): return od[(od.set == s) & (od.name == n)].iloc[0]
ood_cases = (
    ("iliev", "Battery", "Baterai", True, "Iliev"), ("iliev", "Computer-Mouse", "Mouse", True, "Iliev"),
    ("iliev", "Smartphone", "Ponsel", True, "Iliev"), ("iliev", "Washing-Machine", "Mesin cuci", True, "Iliev"),
    ("iliev", "CRT-TV", "TV CRT", True, "Iliev"), ("iliev", "PCB", "PCB", True, "Iliev"),
    ("shubha", "Keyboard", "Keyboard (Shubha)", True, "Shubha"), ("iliev", "Air-Conditioner", "AC", False, "Iliev"),
    ("iliev", "Refrigerator", "Kulkas", False, "Iliev"), ("iliev", "Clothes-Iron", "Setrika", False, "Iliev"),
    ("iliev", "Floor-Fan", "Kipas angin", False, "Iliev"), ("iliev", "LED-Bulb", "Lampu LED", False, "Iliev"),
    ("iliev", "Cooled-Dispenser", "Dispenser air", False, "Iliev"), ("iliev", "Music-Player", "Pemutar MP3", False, "Iliev"),
    ("shubha", "Remote", "Remote (Shubha)", False, "Shubha"),
)
oodrows = []
for s, n, label, known, dataset in ood_cases:
    a = ood(s, n)
    oodrows.append(dict(label=label, known=known, flag=r3(a.flag), n=int(a.n), dataset=dataset))
oodrows += [
    dict(label="Headphone (Shubha)", known=False, flag=r3(sh.loc["usulan v4", "ood_Headphone"]), n=60, dataset="Shubha"),
]
sources = {s: dict(flag=r3(a.flag), n=int(a.n)) for s in ("kaan", "bangla", "karan", "giz") for a in [ood("sumber", s)]}
v4r = pd.read_csv(f"{R}/r8/r8b_fast.csv").set_index("variant").loc["usulan v4"]
sources["bangla"] = dict(flag=r3(v4r.flag_bangla_in), n=449)  # BDC classes only; the 31 lamp photos are a separate OOD row
oodrows.append(dict(label="Lampu (Bangladesh)", known=False, flag=r3(v4r.flag_bangla_bulb), n=31, dataset="Bangladesh"))
ood_v4 = ood_methods.loc["OOD kNN k=10 usulan PCA-32"]
ood_centroid = ood_methods.loc["OOD centroid (v4)"]
ood_shubha = sh.loc["usulan v4"]
ood_summary = dict(
    iliev=dict(n=1751, auc=r3(ood_v4.auroc), centroid_auc=r3(ood_centroid.auroc),
               in_flag=r3(ood_v4.iliev_in_flag), out_flag=r3(ood_v4.iliev_out_flag)),
    shubha=dict(n=300, known_classes=3, ood_classes=2, auc=r3(ood_shubha.knn_auroc),
                ci=[r3(ood_shubha.knn_auroc_lo), r3(ood_shubha.knn_auroc_hi)],
                in_flag=r3(ood_shubha.knn_flag_in), out_flag=r3(ood_shubha.knn_flag_out)))

tp = f"{R}/r8/bdc_tsne.csv"
if not os.path.exists(tp):  # t-SNE of the final PCA-32 features, the 3,792 BDC photos only (cached; under a minute on CPU)
    import numpy as np
    from sklearn.manifold import TSNE
    it = pd.read_csv(f"{R}/items.csv", dtype={"id": str}, keep_default_na=False); m = (it.set == "main").values
    xy = TSNE(2, perplexity=30, init="pca", random_state=0).fit_transform(np.load(f"{R}/z_final_v4.npy")[m])
    A = pd.read_csv(f"{R}/final_v4/assignments.csv", dtype={"id": str})[m]
    pd.DataFrame(dict(id=A.id.values, x=xy[:, 0], y=xy[:, 1], cluster=A.cluster.values, test=(A.source == "bdc_test").astype(int).values)).to_csv(tp, index=False)
cmap = [[round(a.x, 1), round(a.y, 1), int(a.cluster), int(a.test)] for a in pd.read_csv(tp).itertuples()]

ts = pd.read_csv(f"{PA}/tsne.csv")
tsne = [[r3(a.x_raw), r3(a.y_raw), r3(a.x_cmre), r3(a.y_cmre), a.label, a.source] for a in ts.itertuples()]

# ---- round 8: same-feature baselines, paired bootstrap, label-free reference rule, refit without the 188 test images
d1 = pd.read_csv(f"{R}/r8/d1_baselines.csv").groupby("method", sort=False).mean(numeric_only=True)
c1 = pd.read_csv(f"{R}/r8/c1_paired.csv"); rf = pd.read_csv(f"{R}/r8/r8b_reference_labelfree.csv"); d4 = pd.read_csv(f"{R}/r8/d4_reference.csv")
nt = pd.read_csv(f"{R}/r8/r8c_notest.csv").iloc[1]; ff = pd.read_csv(f"{R}/r8/r8b_fast.csv").set_index("variant")
SETS = ("BDC", "Iliev", "Shubha")
PN = {"fusi mentah": "Fusi mentah", "DINOv3-H+ saja": "DINOv3-H+ saja", "INLP x3": "INLP ×3 (butuh proksi)", "ringan CMRE(pe)+dino": "Versi ringan PE + DINOv3"}
paired = [dict(vs=PN[m], **{d: [r3(a.delta), r3(a.lo), r3(a.hi)] for d in SETS for a in [c1[(c1.vs == m) & (c1.set == d)].iloc[0]]}) for m in c1.vs.unique()]
fr = ff.loc["cepat CMRE(SigLIP2)+DINOv3"]
paired.append(dict(vs="Versi cepat SigLIP2 + DINOv3", **{d: [r3(-fr[f"delta_{d}"]), r3(-fr[f"hi_{d}"]), r3(-fr[f"lo_{d}"])] for d in SETS}))
extra = dict(
    baselines=[dict(name=n, xsrc=r3(a.xsrc_BDC), iliev=r3(a.xsrc_Iliev), shubha=r3(a.xsrc_Shubha), ari=r3(a.seed_ari), coverage=r3(a.coverage))
               for n, a in zip(("Spectral (usulan)", "TURTLE", "TEMI", "DECMCV"), d1.itertuples())],
    paired=paired,
    refs=[dict(name=a.ref, r2=r3(a.r2_ridge), xsrc=r3(a.xsrc_BDC), raw=r3(d4[(d4.ref == a.ref) & (d4.variant == "mentah")].xsrc_BDC.iloc[0]),
               ssl="supervisi" not in a.ref) for a in rf.sort_values("r2_ridge", ascending=False).itertuples()],
    notest=dict(bdc=r3(nt.xsrc_BDC), iliev=r3(nt.xsrc_Iliev), shubha=r3(nt.xsrc_Shubha), purity=r3(nt.purity_bdc), ari_train=r3(nt.ari_vs_v4_train), ari_test=r3(nt.ari_vs_v4_test)),
    speed=dict(full=3.4, fast=20.6, sig=42.8, dino=39.9))  # img/s on an L4 incl. flip TTA (embed_new.py bench runs)
data = dict(clusterMap=cmap, extra=extra, backbones=backbones, datasets=datasets, robust=robust, clusters=clusters, ood=oodrows, oodSources=sources, oodSummary=ood_summary, tsne=tsne)
with open(f"{D}/data.js", "w", encoding="utf-8") as fh:
    fh.write("// Generated by code/make_dashboard_data.py from results/modal/*.csv. Do not edit by hand.\n")
    fh.write("window.EWASTE = " + json.dumps(data, ensure_ascii=False) + ";\n")
print("data.js", round(os.path.getsize(f"{D}/data.js") / 1024), "KB |", len(tsne), "t-SNE points |", len(os.listdir(f"{D}/assets")), "assets")
