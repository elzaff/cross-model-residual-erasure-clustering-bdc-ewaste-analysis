"""Builds the final paper into the official BDC template (keeps its cover, styles, numbering and page setup).
Inline markup in text: **bold**, *italic*, ^{superscript}, _{subscript}. Equations are converted to native Word
math with pandoc. Output: paper_draft/Karya_Ilmiah_BDC2026.docx"""
import copy, os, re, subprocess, tempfile, zipfile
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm
from docx.text.paragraph import Paragraph
from lxml import etree

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE, OUT = f"{ROOT}/Template BDC Satria Data 2026.docx", f"{ROOT}/paper_draft/Karya_Ilmiah_BDC2026.docx"
FIG = f"{ROOT}/paper_draft/fig"
MATH = "http://schemas.openxmlformats.org/officeDocument/2006/math"

TEAM_ID = "SD2026040000100"
TITLE = ("UNSUPERVISED DISCOVERY KATEGORI SAMPAH ELEKTRONIK DARI CITRA MULTI-SUMBER MENGGUNAKAN CROSS-MODEL RESIDUAL ERASURE "
         "DAN SPECTRAL CLUSTERING BERBASIS CONSENSUS MAXIMIZATION")
SUBTITLE = "Studi Kasus Pemilahan Sampah Spesifik di Indonesia"

doc = Document(TEMPLATE)
P = doc.paragraphs
EX = {k: copy.deepcopy(P[i]._p) for k, i in dict(blank=21, abs_head=24, abstract=25, kw=27, h1=29, sub=37, body=30, eq=39,
                                                 figcap=44, tabcap=49).items()}
body = doc.element.body
SECT = body[-1]


# ---------------------------------------------------------------- low-level helpers
def strip(p):
    """Remove all runs/markers from a cloned paragraph, keep pPr; return (p, base run properties)."""
    rpr = p.find(".//" + qn("w:r") + "/" + qn("w:rPr"))
    base = copy.deepcopy(rpr) if rpr is not None else OxmlElement("w:rPr")
    for el in list(p):
        if el.tag != qn("w:pPr"):
            p.remove(el)
    for tag in ("w:b", "w:i", "w:vertAlign"):
        for e in base.findall(qn(tag)):
            base.remove(e)
    return p, base


def run(base, text, bold=False, italic=False, va=None, size=None, font=None):
    r = OxmlElement("w:r"); rpr = copy.deepcopy(base)
    if font:
        f = rpr.find(qn("w:rFonts"))
        if f is None: f = OxmlElement("w:rFonts"); rpr.insert(0, f)
        for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"): f.set(qn(a), font)
    if bold: rpr.append(OxmlElement("w:b"))
    if italic: rpr.append(OxmlElement("w:i"))
    if va:
        v = OxmlElement("w:vertAlign"); v.set(qn("w:val"), va); rpr.append(v)
    if size:
        for tag in ("w:sz", "w:szCs"):
            e = rpr.find(qn(tag))
            if e is None: e = OxmlElement(tag); rpr.append(e)
            e.set(qn("w:val"), str(int(size * 2)))
    r.append(rpr)
    for i, chunk in enumerate(text.split("\t")):
        if i: r.append(OxmlElement("w:tab"))
        if chunk:
            t = OxmlElement("w:t"); t.text = chunk; t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve"); r.append(t)
    return r


TOKEN = re.compile(r"(\*\*.+?\*\*|\*.+?\*|\^\{.+?\}|_\{.+?\})")
def runs(p, base, text, size=None, bold_all=False):
    for tok in TOKEN.split(text):
        if not tok: continue
        if tok.startswith("**"): p.append(run(base, tok[2:-2], bold=True, size=size))
        elif tok.startswith("*"): p.append(run(base, tok[1:-1], italic=True, bold=bold_all, size=size))
        elif tok.startswith("^{"): p.append(run(base, tok[2:-1], va="superscript", bold=bold_all, size=size))
        elif tok.startswith("_{"): p.append(run(base, tok[2:-1], va="subscript", bold=bold_all, size=size))
        else: p.append(run(base, tok, bold=bold_all, size=size))
    return p


def emit(el): SECT.addprevious(el); return el


def ppr_set(p, tag, **attrs):
    ppr = p.find(qn("w:pPr")); e = ppr.find(qn(tag))
    if e is None: e = OxmlElement(tag); ppr.append(e)
    for k, v in attrs.items(): e.set(qn(k), str(v))
    return e


def set_ind(p, **attrs):
    ppr = p.find(qn("w:pPr")); old = ppr.find(qn("w:ind"))
    if old is not None: ppr.remove(old)
    ind = OxmlElement("w:ind"); ppr.append(ind)
    for k, v in attrs.items(): ind.set(qn(f"w:{k}"), str(v))


def para(kind, text="", size=None, align=None, bold_all=False):
    p, base = strip(copy.deepcopy(EX[kind]))
    if align: ppr_set(p, "w:jc", **{"w:val": align})
    return emit(runs(p, base, text, size=size, bold_all=bold_all))


def blank(): return para("blank")
def h1(text): blank(); return para("h1", text)
def sub(text):
    p, base = strip(copy.deepcopy(EX["sub"])); ppr = p.find(qn("w:pPr")); ppr.remove(ppr.find(qn("w:numPr")))
    return emit(runs(p, base, text, bold_all=True))
def keep_next(p): ppr_set(p, "w:keepNext"); return p


# ---------------------------------------------------------------- equations, figures, tables
EQ_N = [0]
def equation(latex):
    with tempfile.TemporaryDirectory() as d:
        open(f"{d}/e.md", "w", encoding="utf-8").write(f"$$\n{latex}\n$$\n")
        subprocess.run(["pandoc", f"{d}/e.md", "-o", f"{d}/e.docx"], check=True)
        om = etree.fromstring(zipfile.ZipFile(f"{d}/e.docx").read("word/document.xml")).find(f".//{{{MATH}}}oMath")
    EQ_N[0] += 1
    p, base = strip(copy.deepcopy(EX["eq"]))
    p.append(run(base, "\t")); p.append(copy.deepcopy(om)); p.append(run(base, f"\t({EQ_N[0]})"))
    return emit(p)


FIG_N, TAB_N = [0], [0]
def figure(fname, caption, width=15.0):
    FIG_N[0] += 1; blank()
    p, _ = strip(copy.deepcopy(EX["figcap"])); emit(p); keep_next(p)
    Paragraph(p, doc._body).add_run().add_picture(f"{FIG}/{fname}", width=Cm(width))
    c, base = strip(copy.deepcopy(EX["figcap"]))
    c.append(run(base, f"Gambar {FIG_N[0]}.", bold=True)); runs(c, base, " " + caption)
    emit(c); blank()


def border(el, side, sz=6):
    b = OxmlElement(f"w:{side}")
    for k, v in (("w:val", "single"), ("w:sz", sz), ("w:space", 0), ("w:color", "000000")): b.set(qn(k), str(v))
    el.append(b)


def table(caption, header, rows, widths, align=None, size=9.5, note=None):
    TAB_N[0] += 1; blank()
    c, base = strip(copy.deepcopy(EX["tabcap"])); runs(c, base, f"Tabel {TAB_N[0]}. {caption}"); emit(keep_next(c))
    t = doc.add_table(rows=1 + len(rows), cols=len(header))
    tbl = t._tbl; tpr = tbl.tblPr
    for e in list(tpr):
        if e.tag in (qn("w:tblStyle"), qn("w:tblBorders"), qn("w:tblW"), qn("w:jc"), qn("w:tblLayout")): tpr.remove(e)
    tw = OxmlElement("w:tblW"); tw.set(qn("w:w"), str(int(sum(widths) * 567))); tw.set(qn("w:type"), "dxa"); tpr.append(tw)
    jc = OxmlElement("w:jc"); jc.set(qn("w:val"), "center"); tpr.append(jc)
    lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "fixed"); tpr.append(lay)
    tb = OxmlElement("w:tblBorders"); border(tb, "top", 8); border(tb, "bottom", 8); tpr.append(tb)
    grid = tbl.tblGrid
    for gc, w in zip(grid.findall(qn("w:gridCol")), widths): gc.set(qn("w:w"), str(int(w * 567)))
    align = align or ["left"] + ["center"] * (len(header) - 1)
    for ri, row in enumerate([header] + rows):
        tr = t.rows[ri]._tr; trpr = tr.get_or_add_trPr()
        if ri == 0: trpr.append(OxmlElement("w:tblHeader"))
        trpr.append(OxmlElement("w:cantSplit"))
        for ci, text in enumerate(row):
            cell = t.rows[ri].cells[ci]; cell.width = Cm(widths[ci])
            tcpr = cell._tc.get_or_add_tcPr()
            if ri == 0:
                tb2 = OxmlElement("w:tcBorders"); border(tb2, "bottom", 6); tcpr.append(tb2)
            mar = OxmlElement("w:tcMar")
            for side in ("left", "right"):
                m = OxmlElement(f"w:{side}"); m.set(qn("w:w"), "57"); m.set(qn("w:type"), "dxa"); mar.append(m)
            tcpr.append(mar)
            p = cell.paragraphs[0]._p; p.getparent().remove(p)
            q, qb = strip(copy.deepcopy(EX["body"]))
            ppr_set(q, "w:spacing", **{"w:line": 240, "w:lineRule": "auto", "w:after": 0, "w:before": 0}); set_ind(q, left=0, firstLine=0)
            ppr_set(q, "w:jc", **{"w:val": align[ci] if ri else "center"})
            cell._tc.append(runs(q, qb, str(text), size=size, bold_all=(ri == 0)))
    SECT.addprevious(tbl)
    if note:
        n, nb = strip(copy.deepcopy(EX["body"])); ppr_set(n, "w:spacing", **{"w:line": 240, "w:lineRule": "auto", "w:after": 0})
        set_ind(n, left=0, firstLine=0); emit(runs(n, nb, note, size=9))
    blank()


def references(items):
    for it in items:
        p, base = strip(copy.deepcopy(EX["body"]))
        set_ind(p, left=567, hanging=567); ppr_set(p, "w:jc", **{"w:val": "left"})
        emit(runs(p, base, it))


def code(lines):
    for ln in lines:
        p, base = strip(copy.deepcopy(EX["body"]))
        ppr_set(p, "w:spacing", **{"w:line": 240, "w:lineRule": "auto", "w:after": 0}); ppr_set(p, "w:jc", **{"w:val": "left"})
        set_ind(p, left=0, firstLine=0); p.append(run(base, ln if ln else " ", size=7.5, font="Consolas")); emit(p)


def set_text(p, text, bold=False):
    el, base = strip(p._p)
    el.append(run(base, text, bold=bold))


# ---------------------------------------------------------------- cover and title page
for t in P[0]._p.iter(qn("w:t")):  # text box on the cover (drawing + VML fallback); 10 pt so the ID fits the fixed box
    if "ID" in (t.text or ""):
        t.text = f"ID Kelompok: {TEAM_ID}"
        rpr = t.getparent().find(qn("w:rPr"))
        for tag in ("w:sz", "w:szCs"):
            e = rpr.find(qn(tag)) if rpr is not None else None
            if e is not None: e.set(qn("w:val"), "20")
    elif "Kelompok" in (t.text or ""): t.text = ""
set_text(P[4], TITLE, bold=True); set_text(P[5], SUBTITLE, bold=True); set_text(P[20], TITLE, bold=True)
start = P[20]._p
for el in list(body)[list(body).index(start) + 1:]:
    if el is not SECT: body.remove(el)
para("abstract", SUBTITLE, align="center")
blank()

# ---------------------------------------------------------------- abstract
para("abs_head", "Abstrak", bold_all=True)
para("abstract",
     "Indonesia menghasilkan sekitar 2 juta ton sampah elektronik (e-waste) per tahun, tetapi baru 17,4% yang dikelola dengan baik. "
     "Pemilahan menjadi titik lemah: masyarakat sulit mengenali jenis e-waste beserta jalur penanganannya, sementara foto e-waste di dunia nyata "
     "berasal dari sumber yang sangat beragam, mulai dari katalog daring, kamera ponsel, hingga tumpukan di pengepul. Penelitian ini menemukan "
     "bahwa model fondasi visi-bahasa cenderung mengelompokkan foto berdasarkan cara foto itu diambil, bukan berdasarkan bendanya. Kami mengusulkan "
     "pipeline clustering tanpa label yang tahan terhadap bias sumber foto. Tiga model fondasi (SigLIP2, Perception Encoder, dan DINOv3) mengekstraksi "
     "fitur dari 3.792 citra e-waste BDC. Metode baru *Cross-Model Residual Erasure* (CMRE) menghapus arah dominan pada bagian embedding visi-bahasa yang "
     "tidak dapat dijelaskan oleh model *self-supervised*, sehingga dominasi ciri sumber foto berkurang tanpa label maupun proksi gaya. Jumlah kelompok ditentukan otomatis dengan SCMax, pengelompokan "
     "dilakukan dengan Spectral clustering, dan objek di luar kategori ditandai melalui deteksi *out-of-distribution* berbasis tetangga terdekat. "
     "Pipeline menghasilkan 16 kelompok bermakna, antara lain tiga kelompok baterai dengan jalur penanganan berbeda, TV CRT yang terpisah dari layar datar, serta "
     "kategori laptop yang tidak tercantum pada label panitia. Konsistensi lintas sumber naik dari 0,52 menjadi 0,98 dengan purity 0,99 dan "
     "stabilitas antar-seed 1,00, setara dengan metode yang memerlukan proksi gaya. Hasil ini bertahan pada set uji Iliev yang protokolnya dikunci "
     "sebelum data dilihat (0,89 dibandingkan 0,80 tanpa CMRE) dan terkonfirmasi awal pada set kecil Shubha (0,96 dibandingkan 0,36), serta "
     "kategori baru seperti AC, kulkas, dan setrika dikenali sebagai “tidak dikenal” dengan AUROC 0,94 pada set pengembangan dan 0,99 pada uji segar. Hasil ini menjadi fondasi sistem pemilahan e-waste berbasis foto ponsel bagi masyarakat, bank sampah, dan pengepul di Indonesia.")
blank()
para("kw", "**Kata kunci:** sampah elektronik; clustering tanpa label; bias sumber foto; model fondasi; deteksi out-of-distribution")

# ---------------------------------------------------------------- 1. PENDAHULUAN
h1("PENDAHULUAN")
para("body",
     "Sampah elektronik (*electronic waste*, e-waste) adalah perangkat listrik dan elektronik yang telah dibuang, mulai dari ponsel dan baterai hingga "
     "televisi dan mesin cuci. Pada 2022 dunia menghasilkan 62 juta ton e-waste, dan hanya 22,3% yang terdokumentasi dikumpulkan serta didaur ulang "
     "secara layak (Baldé et al., 2024). Di Indonesia, timbulan e-waste mencapai 2 juta ton pada 2021 dan baru sekitar 17,4% yang berhasil dikelola "
     "dengan baik; sisanya tersimpan di rumah atau tercampur dengan sampah lain, sementara timbulannya diproyeksikan mencapai 3.200 kiloton pada 2040 "
     "(Defitri, 2022).")
para("body",
     "Dampaknya serius karena e-waste mengandung bahan berbahaya dan beracun (B3): timbal pada kaca tabung CRT dan aki, merkuri pada lampu dan layar "
     "LCD generasi lama, serta baterai litium yang mudah terbakar bila rusak. Di negara berkembang, termasuk Indonesia, sebagian besar e-waste mengalir "
     "ke sektor informal yang membongkar perangkat tanpa perlindungan memadai (Baldé et al., 2024). Karena itu, Peraturan Pemerintah Nomor 27 Tahun "
     "2020 menggolongkan sampah yang mengandung B3 sebagai sampah spesifik yang pengelolaannya harus dipisahkan dari sampah biasa (Pemerintah Republik "
     "Indonesia, 2020).")
para("body",
     "Kunci pengelolaan yang lebih baik adalah pemilahan sejak awal, karena setiap kelompok perangkat memiliki jalur penanganan berbeda: baterai harus "
     "dilepas sebelum pencacahan, kaca CRT memerlukan perlakuan khusus, dan papan sirkuit (PCB) mengandung logam bernilai tinggi. Namun masyarakat awam "
     "umumnya tidak mengetahui kategori e-waste dan jalur penanganannya hanya dari melihat bendanya. Sistem berbasis foto kamera ponsel dapat "
     "menjembatani hal ini. Tantangannya, foto e-waste di dunia nyata berasal dari sumber yang sangat beragam, seperti foto katalog berlatar putih, "
     "foto ponsel di lantai rumah, dan foto tumpukan di pengepul, sedangkan pelabelan manual ribuan foto mahal. Pendekatan tanpa label (clustering) "
     "memungkinkan struktur kategori ditemukan langsung dari data, sehingga manusia cukup menamai belasan kelompok alih-alih melabeli ribuan foto.")
para("body",
     "Tabel 1 merangkum penelitian terdahulu. Gundupalli et al. (2018) memilah fraksi e-waste menjadi logam, PCB, plastik, dan kaca dari citra termal "
     "dengan akurasi 84–96%, tetapi memerlukan kamera termal yang tidak dimiliki masyarakat. Islam et al. (2023) mengklasifikasi delapan jenis perangkat "
     "dengan akurasi 96%, dan Rajeev et al. (2025) mendeteksi tujuh jenis komponen dengan YOLOv8 (presisi 0,832; mAP50 0,821). Keduanya terawasi: "
     "kategori ditetapkan sejak awal, memerlukan label, dan dievaluasi pada data dari sumber yang sama. Pendekatan tanpa label masih jarang. Zhou et al. "
     "(2023) melakukan penelusuran e-waste tanpa label, tetapi terbatas pada laptop di lini pembongkaran. DECMCV (Huang et al., 2025) mengelompokkan "
     "sampah umum tanpa label dengan akurasi 93,78% pada TrashNet dan secara eksplisit menyebut perbedaan gaya foto sebagai kendala, tetapi "
     "menanganinya dengan membuang citra yang tidak disepakati beberapa algoritma. Tinjauan terhadap 147 studi AI untuk e-waste juga menyimpulkan "
     "bahwa ketersediaan data dan generalisasi lintas kondisi adalah tantangan utama bidang ini (Jano et al., 2026).")
table("Ringkasan penelitian terdahulu",
      ["Studi", "Data dan metode", "Hasil", "Keterbatasan"],
      [["Gundupalli et al. (2018)", "Citra termal LWIR; fitur intensitas; 4 fraksi material", "Akurasi 84–96%", "Butuh kamera termal; bukan foto biasa"],
       ["Islam et al. (2023), EWasteNet", "8 jenis perangkat; transformer DeiT dua aliran (terawasi)", "Akurasi 96%", "Butuh label; kategori tetap; satu sumber data"],
       ["Rajeev et al. (2025)", "700 citra, 7 jenis komponen; YOLOv5/v7/v8", "YOLOv8: presisi 0,832; mAP50 0,821", "Terawasi; skala komponen; data kecil"],
       ["Zhou et al. (2023), YODO", "Penelusuran WEEE tanpa label di lini pembongkaran", "Retrieval laptop tanpa label", "Satu jenis produk; lingkungan terkendali"],
       ["Huang et al. (2025), DECMCV", "Sampah umum; ConvNeXt + ViT kontrastif; voting multi-clustering", "Akurasi 93,78% (TrashNet)", "Membuang data yang tidak disepakati; bias gaya belum diukur"],
       ["**Penelitian ini**", "3.792 citra BDC + 7 set validasi; CMRE + SCMax + Spectral + OOD kNN (tanpa label)", "xsrc 0,98; purity 0,99; uji terkunci 0,89; AUROC OOD 0,99 (uji segar)", "Lihat Bagian 3.6"]],
      [3.0, 4.6, 3.2, 4.2], align=["left", "left", "left", "left"])
para("body",
     "Dari kajian tersebut terlihat tiga celah penelitian. *Pertama*, sebagian besar metode terawasi dan terikat pada kategori yang ditentukan di awal, "
     "sehingga tidak dapat menemukan kategori baru dan tidak tahu kapan sebuah objek berada di luar kategorinya. *Kedua*, evaluasi umumnya dilakukan "
     "pada data dari sumber yang sama dengan data latih, padahal foto dari masyarakat akan diambil dengan ponsel dan kondisi yang berbeda. *Ketiga*, "
     "belum ada studi yang mengukur apakah model mengelompokkan foto berdasarkan objek atau berdasarkan sumber fotonya. Audit awal kami menunjukkan "
     "bahwa masalah ini nyata: data BDC merupakan gabungan foto katalog 150 piksel berlatar putih, foto ponsel, dan foto web, dan model visi-bahasa "
     "paling mutakhir hanya menempatkan 37–46% foto ponsel ke kelompok yang sama dengan foto katalog objek sejenis (Bagian 3.1).")
para("body",
     "Penelitian ini mengusulkan pipeline pengelompokan e-waste tanpa label yang tahan terhadap bias sumber foto sehingga dapat diterapkan pada foto "
     "kamera ponsel masyarakat. Inti kebaruannya adalah **Cross-Model Residual Erasure (CMRE)**: bagian embedding model visi-bahasa yang tidak dapat "
     "dijelaskan oleh model *self-supervised* DINOv3 diuraikan dengan PCA, lalu arah-arah utamanya (yang terbukti berkaitan dengan resolusi dan latar "
     "foto) diproyeksikan keluar, tanpa label, teks, maupun proksi gaya buatan manusia. Jumlah kelompok ditentukan otomatis dengan SCMax (Zhang et al., 2026), dan objek di luar kategori ditandai melalui deteksi "
     "*out-of-distribution* (OOD) berbasis tetangga terdekat (Sun et al., 2022) sebagai komponen pendukung. Tujuan penelitian ini adalah (1) menemukan kelompok e-waste yang bermakna bagi jalur "
     "penanganan tanpa label, (2) mencapai konsistensi lintas sumber yang tinggi dan terbukti pada data uji independen, serta (3) mengenali objek di luar "
     "kategori yang dipelajari. Hipotesis yang diuji adalah: **H1**, model visi-bahasa lebih bias sumber daripada model *self-supervised*; **H2**, CMRE "
     "meningkatkan konsistensi lintas sumber tanpa label maupun proksi; **H3**, pada fitur yang telah dibersihkan, jumlah kelompok dapat dipilih tanpa "
     "label dan kelompoknya bermakna; serta **H4**, objek di luar kategori dapat dikenali. Hasilnya diharapkan menjadi fondasi sistem pemilahan berbasis "
     "foto bagi masyarakat, bank sampah, dan pengepul, sekaligus mendukung pelaksanaan PP 27/2020. Bagian 2 menguraikan data dan metode, Bagian 3 "
     "menyajikan hasil dan pembahasan, dan Bagian 4 memuat kesimpulan serta rekomendasi.")

# ---------------------------------------------------------------- 2. METODOLOGI
h1("METODOLOGI")
sub("2.1\tDataset dan Karakteristik Data")
para("body",
     "Data utama (D_{main}) berasal dari folder e-waste data latih babak penyisihan BDC sebanyak 3.961 citra. Deduplikasi *perceptual hash* (pHash, "
     "jarak Hamming ≤ 6) menyisakan 3.604 citra unik. Sebanyak 188 citra e-waste dari data uji penyisihan dipilah otomatis dengan pengklasifikasi "
     "SigLIP2 buatan tim pada babak penyisihan (hanya prediksi, tanpa label panitia), sehingga D_{main} berjumlah 3.792 citra. Untuk menghilangkan keraguan pemakaian informasi data uji, pipeline juga dijalankan ulang hanya dengan 3.604 citra latih: xsrc tetap 0,975 (Iliev 0,895; Shubha 0,950), purity 0,991, dan partisinya hampir sama (ARI 0,93 pada citra latih dan 0,97 pada 188 citra uji). Label nama berkas "
     "tersedia untuk 2.331 citra dalam 10 kelas (baterai, keyboard, microwave, ponsel, mouse, PCB, pemutar audio, printer, televisi, dan mesin cuci; "
     "145–298 citra per kelas sehingga relatif seimbang), sedangkan 1.461 citra tidak berlabel. Label tersebut tidak pernah menjadi input model dan "
     "hanya dipakai untuk evaluasi setelah clustering selesai.")
para("body",
     "Untuk menguji ketahanan dan generalisasi, digunakan tujuh set data publik tambahan (Tabel 2). Seluruhnya hanya dipakai untuk evaluasi: citranya "
     "diproyeksikan ke pusat kelompok setelah clustering selesai dan tidak ikut membentuk kelompok. Duplikat terhadap BDC dibuang dengan pHash; audit "
     "menemukan 55% citra Kaan merupakan duplikat BDC, sehingga tanpa langkah ini evaluasi akan bocor. Set uji Iliev dan Shubha disiapkan dengan "
     "protokol yang dikunci sebelum data diunduh, termasuk pemetaan kelas dan metriknya, agar tidak ada keputusan metode yang dipengaruhi data uji. Sebaliknya, BDC berstatus set pengembangan: lebih dari 40 "
     "varian dibandingkan pada xsrc BDC sehingga angka BDC bersifat optimistis, dan bukti generalisasi berasal dari Iliev dan Shubha.")
table("Sumber data yang digunakan",
      ["Sumber", "Jumlah", "Jenis foto", "Peran", "Lisensi"],
      [["BDC (latih + uji penyisihan)", "3.792", "katalog, ponsel, web", "data utama (clustering)", "panitia"],
       ["Kaan, Waste Classification (Kaggle)", "1.794", "katalog", "evaluasi objek", "CDLA-Permissive-1.0"],
       ["Custom Bangladeshi E-Waste (Mendeley)", "480", "foto ponsel", "evaluasi lintas sumber", "CC BY 4.0"],
       ["Garbage Classification, baterai (Kaggle)", "499", "web", "evaluasi objek", "Apache 2.0"],
       ["GIZ E-Waste Database (Hugging Face)", "1.000", "foto lapangan", "uji OOD lapangan", "CC BY 4.0"],
       ["E-Waste Dataset, Iliev (Roboflow)", "1.751 (69 kelas)", "campuran", "uji terkunci", "CC BY 4.0"],
       ["E-waste, Shubha (Roboflow)", "300 (3 kelas dikenal + 2 OOD)", "campuran", "uji segar", "CC BY 4.0"],
       ["Office-Home (Venkateswara et al., 2017)", "2.917 (20 kelas)", "produk vs foto nyata", "uji domain lain", "riset non-komersial"]],
      [5.2, 2.3, 2.6, 2.9, 2.0], align=["left", "center", "left", "left", "left"])
para("body",
     "Gambar 1 memperlihatkan karakteristik data yang menjadi akar masalah. Foto BDC dan Kaan didominasi thumbnail sekitar 150 piksel dengan banyak "
     "latar putih (66% citra BDC berukuran ≤ 200 piksel), sedangkan foto ponsel Bangladesh berukuran sekitar 640 piksel tanpa latar putih dan foto "
     "lapangan GIZ sekitar 1.000 piksel. Objek yang sama tampil sangat berbeda antarsumber; perbedaan inilah yang dapat “menipu” model sehingga "
     "mengelompokkan foto berdasarkan cara pengambilannya.")
figure("fig1_data.png", "Karakteristik data: (a) contoh objek yang sama dari berbagai sumber dan (b) sebaran resolusi serta latar putih per sumber.", width=13.5)
sub("2.2\tDasar Teori")
para("body",
     "**Model fondasi.** Ekstraksi fitur memakai model yang telah dilatih pada ratusan juta citra. Model visi-bahasa (*vision-language model*, VLM) "
     "seperti SigLIP2 (Tschannen et al., 2025) dan Perception Encoder (Bolya et al., 2025) dilatih mencocokkan citra dengan keterangan teksnya sehingga "
     "kaya makna semantik, sedangkan model *self-supervised* (SSL) seperti DINOv3 (Siméoni et al., 2025) belajar hanya dari citra. Pada penelitian ini "
     "hanya menara citra yang dipakai; tidak ada teks yang masuk ke model.")
para("body",
     "**Bias sumber.** Model dapat memanfaatkan “jalan pintas”, yaitu ciri yang berkorelasi dengan data latih tetapi tidak relevan dengan tugas "
     "(Geirhos et al., 2020). Pada clustering, jalan pintas ini berupa ciri akuisisi seperti resolusi, latar, dan pencahayaan yang membuat foto dari "
     "sumber yang sama berkumpul meskipun objeknya berbeda. Metode penghapusan atribut seperti INLP (Ravfogel et al., 2020) dan LEACE (Belrose et al., "
     "2023) dapat menghapus informasi tersebut, tetapi memerlukan label atau proksi dari atribut yang ingin dihapus.")
para("body",
     "**Clustering dan deteksi OOD.** Spectral clustering membangun graf k-tetangga terdekat lalu mempartisinya melalui vektor eigen Laplacian graf "
     "(Ng et al., 2002) sehingga mampu menangkap kelompok berbentuk tidak bulat. SCMax (Zhang et al., 2026) menentukan jumlah kelompok tanpa label "
     "dengan menggabungkan tetangga terdekat secara bertingkat dan memilih tingkat yang paling konsisten antara representasi asli dan representasi yang "
     "diperturbasi. Deteksi OOD berbasis tetangga terdekat (Sun et al., 2022) menandai sampel yang jaraknya ke tetangga ke-k pada data acuan melebihi "
     "suatu ambang.")
sub("2.3\tMetode yang Diusulkan")
para("body", "Gambar 2 menunjukkan alur pipeline. Seluruh input model berupa citra; tidak ada teks, keterangan, maupun label yang digunakan dalam "
     "pembentukan kelompok.")
figure("fig2_flow.png", "Alur pipeline yang diusulkan. Kotak jingga menandai komponen inovasi.")
para("body",
     "**(1) Input dan pra-pemrosesan.** Citra dideduplikasi dengan pHash dan diubah ukurannya sesuai masing-masing model. Setiap citra diproses dua "
     "kali (asli dan dicerminkan horizontal) lalu embedding keduanya dirata-rata (*test-time augmentation*). Segmentasi tidak diperlukan karena sebagian "
     "besar citra memuat satu objek dominan dan model fondasi menghasilkan embedding global yang berfokus pada objek; uji penyamaran latar dengan segmentasi "
     "latar depan justru menurunkan xsrc menjadi 0,69–0,75. **(2) Ekstraksi fitur.** Tiga "
     "model dipakai: SigLIP2-So400m dan PE-Core-G (VLM) karena paling kaya semantik, serta DINOv3-H+ (SSL) karena paling tahan bias sumber berdasarkan "
     "audit terhadap 17 representasi (Bagian 3.1). **(3) CMRE.** Untuk setiap VLM, embedding V diprediksi dari embedding DINOv3 S melalui regresi ridge "
     "(Persamaan 1). Residu R, yaitu bagian VLM yang tidak dapat dijelaskan DINOv3, berisi ciri yang tidak dimiliki model SSL, termasuk jejak sumber "
     "foto. Arah utama residu U_{r} diperoleh dengan PCA (Persamaan 2) lalu dihapus dari embedding (Persamaan 3).")
equation(r"\hat{B}=\arg\min_{B}\lVert V-SB\rVert_{F}^{2}+\alpha\lVert B\rVert_{F}^{2}")
equation(r"R=V-S\hat{B},\qquad U_{r}=\mathrm{PCA}_{r}(R)")
equation(r"\tilde{v}=\frac{\left(I-U_{r}U_{r}^{\top}\right)v}{\left\lVert \left(I-U_{r}U_{r}^{\top}\right)v\right\rVert_{2}}")
para("body",
     "Nilai r ditetapkan dengan aturan tanpa label, yaitu jumlah arah yang menjelaskan 50% varians residu dengan batas 64 komponen; pada data ini "
     "batas tersebut tercapai sehingga r = 64. Nilai α = 1 adalah nilai bawaan ridge. Keduanya tidak dipilih dari metrik evaluasi, dan "
     "sensitivitasnya dilaporkan pada Bagian 3.3. Model acuan juga dipilih tanpa label: di antara delapan model SSL, DINOv3-7B dan DINOv3-H+ paling "
     "baik memprediksi embedding VLM (R² ridge 0,43 dan 0,40), dan DINOv3-H+ dipakai karena 7B memerlukan GPU A100. Istilah *erasure* merujuk "
     "pada penghapusan arah residu, bukan penghapusan informasi sumber. Karena acuannya adalah model lain, CMRE tidak memerlukan label objek maupun "
     "proksi gaya. "
     "**(4) Fusi dan reduksi.** Embedding SigLIP2 dan PE yang telah dibersihkan digabung dengan embedding DINOv3, direduksi menjadi 32 dimensi dengan "
     "PCA, lalu dinormalisasi (Persamaan 4).")
equation(r"z=\mathrm{PCA}_{32}\left(\left[\tilde{v}_{\mathrm{SigLIP2}};\,\tilde{v}_{\mathrm{PE}};\,s_{\mathrm{DINOv3}}\right]\right)")
para("body",
     "**(5) Penentuan K.** SCMax dijalankan dengan pengaturan bawaan penulisnya, dan median pilihan K antar-seed dipakai sebagai jumlah kelompok. "
     "Tiga seed awal memberi median 13; karena variasi antar-seed besar, jumlah seed ditambah menjadi 9 sehingga median menjadi 16. "
     "**(6) Clustering.** Spectral clustering dengan graf 15 tetangga terdekat. **(7) Output.** Setiap kelompok diinterpretasikan melalui galeri citra "
     "representatif dan dipetakan ke kategori WEEE (European Parliament and Council, 2012) serta kategori B3. Citra baru ditempatkan ke pusat kelompok "
     "terdekat dan ditandai “tidak dikenal” bila skor OOD kNN (Sun et al., 2022; Persamaan 5) melebihi persentil ke-95 skor pada D_{main}, dengan z_{(10)}(x) sebagai tetangga "
     "ke-10 dari x di D_{main}. Ekstraksi fitur dijalankan di GPU cloud (Modal, L4/A100) dan clustering di CPU; kode lengkap tersedia pada Lampiran.")
equation(r"s(x)=\left\lVert z(x)-z_{(10)}(x)\right\rVert_{2}")
sub("2.4\tSkenario Pengujian dan Metrik Evaluasi")
para("body",
     "Mengikuti alur hipotesis, pengujian, dan perbandingan, skenario pengujian mencakup: (a) perbandingan 17 representasi (H1); (b) perbandingan "
     "strategi pasca-pemrosesan, yaitu tanpa perlakuan, INLP, LEACE, dan CMRE (H2); (c) perbandingan metode clustering, yaitu Spectral, K-Means, "
     "Agglomerative-Ward, GMM, serta metode terbaru TEMI (Adaloglou et al., 2023), TURTLE (Gadetsky et al., 2024), dan protokol DECMCV (Huang et al., "
     "2025) (H3); (d) optimasi parameter K, r, dan jumlah tetangga graf; serta (e) validasi pada set uji terkunci Iliev, set uji segar Shubha, dan "
     "domain lain Office-Home (H2–H4). Semua pembanding memakai reduksi PCA-32 dan jumlah kelompok yang sama agar perbandingan adil.")
para("body",
     "Metrik dipilih untuk menjawab dua pertanyaan: apakah kelompok memisahkan objek dengan baik, dan apakah pemisahan itu bertahan ketika sumber foto "
     "berganti (Tabel 3). Metrik utama adalah konsistensi lintas sumber (xsrc) yang dirumuskan pada penelitian ini (Persamaan 6): untuk setiap kelas c "
     "pada himpunan kelas bersama 𝒞, dihitung proporsi foto dari sumber kedua A_{c} (misalnya foto ponsel) yang masuk ke kelompok mayoritas m_{c} dari "
     "foto katalog kelas yang sama.")
equation(r"\mathrm{xsrc}=\frac{1}{|\mathcal{C}|}\sum_{c\in\mathcal{C}}\frac{1}{|A_{c}|}\sum_{i\in A_{c}}\mathbf{1}\left[y_{i}=m_{c}\right]")
table("Metrik evaluasi",
      ["Metrik", "Yang diukur", "Rentang", "Makna nilai"],
      [["xsrc (utama)", "Objek sama dari sumber berbeda masuk kelompok yang sama", "0–1 (↑)", "1 = tidak terpengaruh sumber; rendah = kelompok mengikuti sumber foto"],
       ["Purity", "Kemurnian kelas di dalam kelompok", "0–1 (↑)", "1 = setiap kelompok hanya berisi satu kelas"],
       ["NMI objek", "Informasi bersama kelompok dan kelas", "0–1 (↑)", "1 = kelompok identik dengan kelas"],
       ["NMI sumber | objek", "Pengaruh sumber di dalam setiap kelas", "0–1 (↓)", "0 = sumber tidak memengaruhi kelompok"],
       ["Stabilitas", "ARI antar-seed; Jaccard bootstrap per kelompok", "0–1 (↑)", "≥ 0,85 = sangat stabil (Hennig, 2007)"],
       ["Silhouette, DB, CH", "Separasi internal tanpa label", "(↑), (↓), (↑)", "Tidak peka terhadap bias sumber"],
       ["AUROC OOD", "Pemisahan kategori dikenal dan kategori baru", "0,5–1 (↑)", "1 = sempurna; 0,5 = acak"]],
      [3.0, 4.9, 2.1, 5.0], align=["left", "left", "center", "left"])

# ---------------------------------------------------------------- 3. HASIL DAN PEMBAHASAN
h1("HASIL DAN PEMBAHASAN")
sub("3.1\tTemuan Awal: Model Mengelompokkan Cara Memotret, Bukan Benda (H1)")
para("body",
     "Gambar 3a membandingkan 12 representasi tunggal dengan protokol seragam. Model visi-bahasa, yang paling unggul pada banyak benchmark, justru "
     "paling rentan: SigLIP2 dan CLIP hanya menempatkan 37% foto ponsel ke kelompok yang sama dengan foto katalog objek sejenis, sedangkan DINOv3-H+ "
     "mencapai 0,86. Pola ini konsisten pada arsitektur ViT maupun CNN, sehingga penyebabnya terletak pada cara pelatihan. Uji terkendali memperkuat "
     "kesimpulan ini: dengan data pelatihan sejenis, MetaCLIP yang dilatih dengan bahasa (Xu et al., 2024) hanya mencapai 0,20, sedangkan Web-DINO "
     "tanpa bahasa (Fan et al., 2025) mencapai 0,70. Hipotesis kami, supervisi bahasa ikut mengajarkan informasi “jenis foto” (misalnya foto produk versus foto "
     "amatir) yang sering muncul dalam keterangan teks di internet; karena data pelatihan kedua model sejenis tetapi tidak identik, uji ini "
     "mendukung, bukan membuktikan, hipotesis tersebut.")
para("body",
     "Bias ini tidak terlihat oleh metrik biasa. Fusi mentah tiga model mencapai purity BDC tertinggi (0,994), tetapi xsrc-nya hanya 0,524. Gambar 3b "
     "memperlihatkan penyebabnya: foto ponsel (segitiga) membentuk pulau terpisah dari foto katalog (bulat) untuk objek yang sama. Setelah CMRE "
     "(Gambar 3c), keduanya menyatu per objek. Dengan demikian, **H1 diterima**.")
figure("fig3_bias.png", "Bias sumber foto: (a) konsistensi lintas sumber 12 representasi tunggal; (b–c) t-SNE foto katalog dan foto ponsel dari "
       "lima kelas bersama sebelum dan sesudah CMRE.", width=13.5)
sub("3.2\tCMRE Memulihkan Konsistensi Lintas Sumber (H2)")
para("body",
     "Tabel 4 merangkum perbandingan pada BDC dengan K = 16. CMRE menaikkan xsrc fusi dari 0,524 menjadi 0,975 (+0,45) tanpa menurunkan purity "
     "(0,992), serta mengungguli metode clustering terbaru pada fitur CMRE yang sama: TURTLE (0,790), TEMI (0,590, tidak stabil pada data "
     "sekecil ini), dan protokol DECMCV (0,910) yang hanya mengelompokkan 81% citra. Efek CMRE juga terlihat pada versi ringan dua model: tanpa CMRE xsrc pasangan PE dan DINOv3 hanya 0,630, "
     "sedangkan dengan CMRE menjadi 0,963. CMRE menyamai INLP (0,975), metode penghapusan bias yang memerlukan proksi gaya buatan manual, dan "
     "mengungguli LEACE (0,792). Uji bootstrap berpasangan (2.000 ulangan) menegaskan hal ini: selisih CMRE terhadap fusi mentah dan DINOv3 saja "
     "signifikan pada BDC, Iliev, dan Shubha (p < 0,001), sedangkan selisih terhadap INLP tidak signifikan (IK95% memuat nol). Jadi klaim yang "
     "tepat adalah kinerja setara INLP tanpa merancang proksi apa pun, sehingga lebih mudah diterapkan pada sumber foto baru yang cirinya belum "
     "diketahui.")
table("Perbandingan metode pada data BDC (K = 16)",
      ["Metode", "xsrc", "Purity BDC", "Purity eks.", "NMI objek", "Stabilitas", "Data"],
      [["Fusi mentah (tanpa perlakuan)", "0,524", "0,994", "0,972", "0,789", "1,00", "100%"],
       ["DINOv3-H+ saja", "0,758", "0,982", "0,967", "0,799", "1,00", "100%"],
       ["TURTLE (2024)^{†}", "0,790", "0,994", "–", "–", "0,97", "100%"],
       ["TEMI (2023)^{†}", "0,590", "0,808", "–", "–", "0,42", "100%"],
       ["Protokol DECMCV (2025)^{†}", "0,910", "0,988", "–", "–", "0,92", "81%"],
       ["LEACE ×3 (butuh proksi)", "0,792", "0,990", "0,977", "0,801", "1,00", "100%"],
       ["INLP ×3 (butuh proksi)", "0,975", "0,989", "0,982", "0,853", "1,00", "100%"],
       ["CMRE versi cepat: SigLIP2 + DINOv3", "0,951", "0,987", "–", "–", "1,00", "100%"],
       ["CMRE versi ringan: PE + DINOv3", "0,963", "0,992", "0,982", "0,852", "1,00", "100%"],
       ["**CMRE: SigLIP2 + PE + DINOv3 (usulan)**", "**0,975**", "**0,992**", "**0,983**", "**0,859**", "**1,00**", "**100%**"]],
      [5.4, 1.5, 1.7, 1.7, 1.6, 1.6, 1.5],
      note="^{†} Dijalankan pada fitur CMRE usulan yang sama, K = 16, dilatih hanya pada D_{main}, rata-rata 3 seed; Data = proporsi citra yang "
           "diberi kelompok. DINOv3-H+ saja memakai protokol usulan (Spectral, K = 16), sehingga berbeda dari angka audit seragam pada Bagian 3.1.")
para("body",
     "Mengapa CMRE bekerja? Uji *probe* linear menunjukkan informasi objek menjadi lebih mudah dipindahkan antarsumber setelah CMRE: pengklasifikasi yang "
     "dilatih pada foto katalog dan diuji pada foto ponsel naik akurasinya dari 0,944 menjadi 0,983. CMRE mengurangi dominasi ciri sumber terhadap "
     "struktur ketetanggaan sehingga kelompok terbentuk menurut objek. Arah yang dihapus berkorelasi dengan resolusi foto (|ρ| hingga 0,68) dan "
     "proporsi latar putih (0,39), sedangkan informasi sumber tidak hilang (probe sumber tetap 0,96–0,99); yang berkurang adalah dominasinya. "
     "Acuan harus model SSL: dengan acuan ConvNeXt V2 yang dilatih berlabel, xsrc justru turun ke 0,384. Diagnostik pada sembilan pasangan model menunjukkan manfaat CMRE sebanding dengan "
     "besarnya jejak gaya pada VLM (korelasi Spearman 0,78); pada model yang sudah tahan bias seperti AIMv2, CMRE tidak diperlukan.")
para("body",
     "Uji terpenting adalah pada data yang tidak pernah dipakai untuk memilih metode (Gambar 4). Pada set uji Iliev, yaitu 1.751 foto dari "
     "69 jenis perangkat dengan protokol dan pemetaan kelas yang dikunci sebelum data diunduh, CMRE mencapai xsrc-eks 0,885 [IK95% 0,864–0,908] dan purity "
     "0,939, di atas fusi mentah (0,803) dan DINOv3 saja (0,755). Di sini xsrc-eks adalah xsrc dengan foto set eksternal menggantikan foto "
     "Bangladesh; angka yang dilaporkan memakai pemetaan kelas yang dikunci, dan pemetaan alternatif hanya menjadi analisis sensitivitas. Iliev "
     "kemudian dipakai untuk memilih skor OOD, sehingga untuk OOD statusnya data pengembangan. Pada set uji segar Shubha yang kecil (300 crop, tiga "
     "kelas dikenal), yang kami anggap konfirmasi awal, fusi mentah runtuh ke 0,356 karena foto ponsel dan mouse "
     "masuk ke kelompok yang salah, sedangkan CMRE memulihkannya menjadi 0,956 [0,924–0,983] dengan purity 1,00. Pada Office-Home, fusi mentah memang "
     "sudah tidak bias (0,865) dan CMRE tetap setara (0,864) sambil memperbaiki silhouette dari 0,39 menjadi 0,48. Artinya, CMRE memperbaiki ketika bias "
     "ada dan tidak merusak ketika bias tidak ada. Dengan demikian, **H2 diterima**.")
figure("fig4_results.png", "Konsistensi lintas sumber pada data pengembangan dan tiga set validasi independen.", width=15.0)
sub("3.3\tPenentuan Jumlah Kelompok dan Ketahanan Parameter (H3)")
para("body",
     "Jumlah kelompok dipilih tanpa label oleh SCMax. Dari 9 seed, SCMax memilih K = 13 (dua kali), 15 (sekali), 16 (tiga kali), dan 19 (tiga kali), "
     "dengan median 16 (Gambar 5a). Pilihan ini berprinsip: aturan lama berbasis silhouette justru memilih K = 20 dengan xsrc hanya 0,596, sedangkan "
     "pada rentang K 12–17 kualitas tetap tinggi (xsrc ≥ 0,97; purity ≥ 0,99) sebelum menurun pada K ≥ 18 ketika kelompok baterai mulai terpecah lebih "
     "halus; K = 19, yang dipilih tiga seed, memberi xsrc 0,794. Tingkat hierarki SCMax juga memberi taksonomi dua tingkat yang alami: K = 13 "
     "sebagai tingkat kasar dan K = 16 sebagai tingkat halus, dengan 14 dari 16 kelompok K = 16 mewarisi ≥ 96% citranya dari satu kelompok K = 13.")
para("body",
     "Sebagai analisis sensitivitas (bukan dasar pemilihan), xsrc berada pada 0,97–0,99 untuk r = 16–64 tetapi turun di luar rentang itu (r = 4: 0,449; "
     "r = 8: 0,773; r = 128: 0,821; Gambar 5b), serta 0,975–0,983 untuk α = 0,01–1 lalu menurun pada α ≥ 10. Pada K = 16, Spectral clustering memberi xsrc tertinggi "
     "(0,975) dibanding K-Means (0,949), GMM (0,926), dan Ward (0,836) (Gambar 5c). K-Means memiliki silhouette sedikit lebih tinggi (0,398 dibanding "
     "0,364) tetapi xsrc lebih rendah, yang menegaskan bahwa indeks internal tidak dapat mendeteksi bias sumber sehingga metrik lintas sumber diperlukan. "
     "Untuk graf Spectral, xsrc bernilai 0,975–0,988 pada 15–30 tetangga tetapi 0,91 pada 5–10 tetangga (Gambar 5d); nilai 15 dipakai sejak ronde "
     "awal, bukan dipilih dari sapuan ini. Stabilitas antar-seed sempurna (ARI 1,00) dan 11 dari 16 "
     "kelompok tergolong sangat stabil secara bootstrap (Jaccard ≥ 0,85).")
figure("fig5_params.png", "Pemilihan K dan uji ketahanan: (a) kualitas partisi terhadap K beserta pilihan SCMax; (b) parameter r pada CMRE; "
       "(c) perbandingan algoritma pada K = 16; (d) jumlah tetangga graf Spectral.", width=13.5)
sub("3.4\tInterpretasi 16 Kelompok E-Waste")
para("body",
     "Gambar 6 menampilkan contoh citra tiap kelompok dan Tabel 5 memuat interpretasinya. Setiap kelompok konsisten secara visual dan dapat dipetakan ke "
     "jalur penanganan e-waste.")
figure("fig6_clusters.png", "Lima citra representatif dari setiap kelompok pada partisi final (K = 16).")
table("Interpretasi kelompok dan implikasi penanganannya",
      ["C", "Isi kelompok", "n", "Kategori WEEE / B3", "Jaccard", "Implikasi penanganan"],
      [["0", "Aki timbal-asam", "115", "baterai (B3)", "0,71", "timbal dan asam sulfat; daur ulang aki khusus"],
       ["1", "Baterai pack laptop", "70", "baterai Li-ion", "0,94", "risiko kebakaran; lepas sebelum pencacahan"],
       ["2", "Turntable", "111", "5 (peralatan kecil)", "0,96", "pembongkaran umum"],
       ["3", "TV/monitor CRT", "174", "2 (layar)", "0,79", "kaca bertimbal; perlakuan selektif"],
       ["4", "Baterai ponsel/kamera", "136", "baterai Li-ion kecil", "0,82", "titik kumpul baterai"],
       ["5", "Pemutar CD/radio", "153", "5 (peralatan kecil)", "0,97", "pembongkaran umum"],
       ["6", "Mesin cuci bukaan atas", "115", "4 (peralatan besar)", "0,98", "logam dan motor"],
       ["7", "TV/monitor layar datar", "263", "2 (layar)", "0,85", "lampu latar lama dapat mengandung merkuri"],
       ["8", "Mesin cuci front-load", "192", "4 (peralatan besar)", "0,99", "logam dan motor"],
       ["9", "Laptop", "277", "2 (layar)", "0,98", "baterai, layar, dan PCB bernilai"],
       ["10", "Keyboard", "320", "6 (TI kecil)", "0,90", "plastik dominan"],
       ["11", "Microwave", "275", "5 (peralatan kecil)", "1,00", "kapasitor tegangan tinggi"],
       ["12", "Printer", "294", "6 (TI kecil)", "1,00", "kartrid toner"],
       ["13", "Mouse", "291", "6 (TI kecil)", "1,00", "plastik dominan"],
       ["14", "Ponsel", "366", "6 (TI kecil)", "0,94", "baterai dan PCB bernilai"],
       ["15", "PCB dan tumpukan campuran", "640", "komponen", "0,85", "logam mulia; perlu pra-pemilahan"]],
      [0.8, 4.0, 1.1, 3.3, 1.5, 4.3], align=["center", "left", "center", "left", "center", "left"])
para("body",
     "Tiga temuan menonjol. *Pertama*, tingkat halus (K = 16) memecah tepat tiga kelompok induk dari tingkat kasar (K = 13) menjadi subtipe yang jalur "
     "penanganannya berbeda: baterai menjadi aki timbal-asam dan baterai Li-ion kecil, televisi menjadi CRT (kaca bertimbal) dan layar datar, serta "
     "pemutar audio menjadi turntable dan CD/radio. Bersama baterai pack laptop (C1), sistem memisahkan tiga kelompok baterai yang berbeda bentuk dan jalur penanganannya "
     "tanpa pernah diberi tahu. *Kedua*, kelompok C9 berisi laptop, padahal label nama berkas panitia menyebutnya “keyboard”; temuan ini tervalidasi "
     "pada data Iliev, dengan 96,7% foto laptop masuk ke C9. *Ketiga*, pemetaan ke kategori WEEE terkonfirmasi pada data Iliev yang memiliki kategori "
     "perangkat resmi: kelompok layar (C3, C7, C9) 95–100% berisi perangkat berlayar dan kelompok mesin cuci front-load (C8) 94% berisi peralatan besar. Uji permutasi (100.000 penggabungan acak dengan ukuran "
     "grup yang sama) menunjukkan kesesuaian ini bukan kebetulan: pada crop Iliev yang dikenali, kategori EU-6 sama dengan kategori grup kelompoknya "
     "pada 79% kasus, dibandingkan 19% untuk penggabungan acak (p < 0,001), dan silhouette enam grup WEEE (0,178) lebih tinggi dari rerata acak "
     "(0,144; p = 0,01). Jarak antarpusat kelompok dalam satu grup WEEE tidak lebih dekat daripada acak (p = 0,46), sehingga kategori WEEE lebih tepat "
     "dipandang sebagai lapisan penamaan di atas kelompok. Hierarki K = 13 ke K = 16 dan komposisi label per kelompok disajikan pada Lampiran "
     "(Gambar 8 dan 9): 15 dari 16 kelompok berisi ≥ 90% satu label BDC.")
para("body",
     "Kesalahan yang muncul juga dapat dijelaskan. Dari 449 foto ponsel Bangladesh pada lima kelas bersama, hanya 12 yang tidak masuk kelompok "
     "mayoritas foto katalog: tujuh baterai masuk kelompok aki, tiga PCB masuk kelompok baterai ponsel, dan dua foto ponsel masuk kelompok baterai. Beberapa foto stop kontak masuk ke kelompok aki (C0) karena bentuk kotak dan terminal logamnya mirip; "
     "foto tumpukan campuran terkumpul di C15 karena didominasi papan sirkuit; dan kelompok aki, CRT, serta baterai ponsel paling sensitif terhadap "
     "perubahan sampel (Jaccard 0,71–0,82) karena jumlah fotonya relatif sedikit dan variasi sudut pandangnya tinggi. Sebaliknya, kelompok ponsel (C14) "
     "yang sebagian besar berisi foto amatir memiliki kemurnian 99%, menunjukkan bahwa foto kamera ponsel masyarakat dapat dikelompokkan dengan benar. "
     "Dengan demikian, **H3 diterima**.")
sub("3.5\tMengenali yang Belum Dikenal: Deteksi OOD (H4)")
para("body",
     "Sistem pemilahan yang aman harus tahu kapan ia tidak tahu. Skor OOD berbasis tetangga terdekat meningkatkan AUROC dari 0,868 (jarak ke pusat "
     "kelompok) menjadi 0,937 pada data Iliev (karena itu Iliev menjadi set pengembangan untuk OOD), dan aturan ini terkonfirmasi awal pada uji segar Shubha dengan AUROC 0,994 [0,984–0,999], meskipun hanya dengan dua kelas OOD. Harganya, "
     "13% foto ponsel Bangladesh dari kelas yang dikenal ikut ditandai, sedangkan 94% foto lampu Bangladesh (kelas yang tidak ada di BDC) ditandai. Gambar 7a "
     "memperlihatkan perilakunya: kategori yang ada di BDC hampir tidak pernah ditandai (0–10%), sedangkan AC (97%), kulkas (83%), serta setrika, kipas "
     "angin, lampu LED, dan dispenser air (100%) ditandai sebagai kategori baru. Pemutar MP3 portabel juga ditandai (97%) karena “player” pada BDC berupa "
     "turntable dan pemutar CD.")
para("body",
     "Foto lapangan GIZ ditandai 44,5%, dan galerinya (Gambar 7b) didominasi AC, kulkas, dan kompresor, yaitu kategori WEEE 1 (alat penukar suhu) yang "
     "tidak ada pada data BDC. Ini insight penting bagi Indonesia: AC dan kulkas merupakan e-waste rumah tangga berukuran besar yang dapat mengandung "
     "refrigeran perusak ozon atau berpotensi pemanasan global tinggi, tetapi belum terwakili dalam data. Sistem tidak memaksakan foto tersebut ke "
     "kelompok yang salah, melainkan menandainya untuk ditinjau manusia. Dengan demikian, **H4 diterima**.")
figure("fig7_ood.png", "Perilaku open-set: (a) proporsi foto uji yang ditandai “tidak dikenal” per kategori; (b) contoh foto lapangan GIZ yang "
       "ditandai, didominasi AC dan kulkas.")
sub("3.6\tKaitan dengan Studi Terdahulu dan Implikasi bagi Indonesia")
para("body",
     "Hasil ini sejalan dengan DECMCV bahwa perbedaan gaya foto mengganggu pengelompokan sampah (Huang et al., 2025), dan melengkapinya dengan tiga hal: "
     "bias tersebut dapat diukur (xsrc), penyebabnya diduga berkaitan dengan supervisi bahasa, dan bias dapat dikurangi tanpa membuang data. Dibandingkan "
     "studi terawasi yang mencapai akurasi 96% pada satu sumber data (Islam et al., 2023), pendekatan ini tidak memerlukan label sama sekali dan diuji "
     "pada tujuh set data publik tambahan; manusia cukup menamai 16 kelompok. Temuan subtipe produk sejalan dengan pengamatan Zhou et al. (2025) bahwa tipe produk "
     "membentuk kelompok alami yang relevan bagi pembongkaran.")
para("body",
     "Bagi Indonesia, pipeline ini dapat menjadi dasar **asisten pemilahan berbasis foto**: warga, petugas bank sampah, atau pengepul memotret e-waste "
     "dengan ponsel; sistem menempatkannya ke salah satu dari 16 kelompok beserta jalur penanganannya (misalnya “baterai Li-ion: lepaskan dan setor ke "
     "titik kumpul B3”), atau menandainya “tidak dikenal” untuk dicek petugas. Pendekatan *cluster-then-label* juga memangkas biaya pelabelan karena "
     "3.792 foto cukup dinamai melalui 16 kelompok. Untuk perangkat dengan sumber daya terbatas tersedia versi cepat tanpa PE-Core-G, yaitu CMRE(SigLIP2) + DINOv3: ekstraksi fiturnya "
     "sekitar 20 citra/detik pada GPU L4, enam kali lebih cepat dari pipeline penuh (3,4 citra/detik), dengan xsrc 0,951 (Iliev 0,860; Shubha 0,922) "
     "dan AUROC OOD yang sama (0,937). Tahap setelah ekstraksi fitur hanya memerlukan sekitar 1 detik CPU untuk 3.792 citra. Beberapa "
     "aspek masih dapat dikembangkan: data belum memuat foto yang diambil langsung di Indonesia, pipeline tiga model masih memerlukan server GPU, dan "
     "kelompok baterai serta CRT paling sensitif terhadap variasi sampel. Ketiganya menjadi dasar rekomendasi pada Bagian 4.")

sub("3.7\tKeterbatasan")
para("body",
     "Beberapa keterbatasan perlu dicatat. (1) BDC adalah set pengembangan, sehingga xsrc 0,975 bersifat optimistis; bukti generalisasi "
     "berasal dari Iliev (0,885) dan Shubha yang masih kecil (300 crop). (2) CMRE setara, bukan lebih unggul, dibanding INLP, dan manfaatnya "
     "bersyarat: pada Office-Home yang tidak bias CMRE tidak menambah kinerja, dan acuannya harus model SSL berskala besar (dengan DINOv3-B xsrc "
     "hanya 0,593; Tabel 6). (3) Informasi sumber foto tidak terhapus (probe 0,96–0,99); yang berkurang hanya dominasinya. (4) SCMax memilih K "
     "13–19 antar-seed; K = 16 berasal dari median, dan K = 19 memberi xsrc 0,794. (5) Deteksi OOD menandai 13% foto ponsel dari kelas yang "
     "dikenal, dan ambangnya masih global, belum per kelompok. (6) Belum ada foto yang diambil langsung di Indonesia, dan pemetaan kelompok ke "
     "kategori WEEE dilakukan penulis setelah melihat galeri. (7) Hasil pada data eksternal bergantung pada pemetaan kelas: pemutar MP3 Iliev "
     "(0,30) dan TV (0,58) rendah karena definisi kelasnya berbeda dari BDC.")

# ---------------------------------------------------------------- 4. PENUTUP
h1("PENUTUP")
para("body",
     "Penelitian ini mengusulkan pipeline pengelompokan citra e-waste tanpa label yang tahan terhadap bias sumber foto, terdiri atas metode baru CMRE, "
     "penentuan jumlah kelompok otomatis SCMax, Spectral clustering, dan deteksi OOD berbasis tetangga terdekat. Berdasarkan pengujian pada 3.792 citra "
     "BDC dan tujuh set data publik tambahan (tiga di antaranya set validasi independen), diperoleh kesimpulan berikut. (1) Model visi-bahasa terbukti mengelompokkan menurut sumber foto (xsrc "
     "0,37–0,46), berbeda dengan DINOv3 (0,86). (2) CMRE menaikkan konsistensi lintas sumber dari 0,52 menjadi 0,98 dengan purity 0,99 dan stabilitas "
     "1,00, setara dengan metode berproksi tanpa memerlukan proksi dan unggul atas TURTLE, TEMI, dan DECMCV; hasilnya bertahan pada set uji terkunci "
     "(0,89) dan terkonfirmasi awal pada set uji segar (0,96). (3) Enam belas kelompok yang ditemukan bermakna bagi penanganan e-waste, termasuk tiga jenis baterai, CRT versus layar datar, dan "
     "kategori laptop yang tidak tercantum pada label. (4) Kategori baru seperti AC, kulkas, dan setrika dikenali melalui deteksi OOD kNN (AUROC 0,94 pada set pengembangan Iliev, 0,99 pada uji segar Shubha). Kebaruan "
     "utama penelitian ini adalah penggunaan model *self-supervised* sebagai acuan untuk membersihkan bias sumber pada model visi-bahasa tanpa label "
     "maupun proksi, beserta metrik lintas sumber untuk mengukurnya.")
para("body",
     "Rekomendasi yang diajukan adalah sebagai berikut. (1) **Pengumpulan data:** menghimpun foto e-waste rumah tangga Indonesia (kipas angin, rice "
     "cooker, setrika, charger, AC, dan kulkas) melalui bank sampah atau aplikasi pelaporan; foto bertanda “tidak dikenal” dapat menjadi prioritas "
     "pelabelan. (2) **Pengembangan sistem:** mengintegrasikan pipeline ke aplikasi ponsel yang menampilkan kelompok dan jalur penanganan, dengan "
     "distilasi ke model ringan agar dapat berjalan langsung di perangkat. (3) **Penelitian lanjutan:** memperluas taksonomi ke kategori penukar suhu "
     "dan lampu, menambahkan segmentasi untuk foto tumpukan, serta menguji CMRE pada domain sampah lain. (4) **Kebijakan:** taksonomi 16 kelompok yang "
     "terpetakan ke kategori WEEE dan B3 dapat menjadi acuan panduan pemilahan e-waste berbasis foto dalam pelaksanaan PP 27/2020.")

# ---------------------------------------------------------------- 5. REFERENSI
h1("REFERENSI")
references([
    "Adaloglou, N., Michels, F., Kalisch, H., & Kollmann, M. (2023). Exploring the limits of deep image clustering using pretrained models. "
    "*Proceedings of the British Machine Vision Conference (BMVC)*.",
    "Baldé, C. P., Kuehr, R., Yamamoto, T., et al. (2024). *The global e-waste monitor 2024*. International Telecommunication Union & United Nations "
    "Institute for Training and Research. https://ewastemonitor.info",
    "Belrose, N., Schneider-Joseph, D., Ravfogel, S., Cotterell, R., Raff, E., & Biderman, S. (2023). LEACE: Perfect linear concept erasure in closed "
    "form. *Advances in Neural Information Processing Systems, 36*.",
    "Bolya, D., et al. (2025). Perception Encoder: The best visual embeddings are not at the output of the network. *arXiv:2504.13181*.",
    "Defitri, M. (2022, 12 Oktober). *Pengelolaan sampah elektronik dan peraturannya di Indonesia*. Waste4Change. "
    "https://waste4change.com/blog/pengelolaan-sampah-elektronik-dan-peraturannya-di-indonesia/",
    "European Parliament and Council. (2012). Directive 2012/19/EU on waste electrical and electronic equipment (WEEE). *Official Journal of the "
    "European Union, L 197*.",
    "Fan, D., et al. (2025). Scaling language-free visual representation learning. *arXiv:2504.01017*.",
    "Gadetsky, A., Jiang, Y., & Brbić, M. (2024). Let go of your labels with unsupervised transfer. *Proceedings of the 41st International Conference on "
    "Machine Learning (ICML)*.",
    "Geirhos, R., Jacobsen, J.-H., Michaelis, C., Zemel, R., Brendel, W., Bethge, M., & Wichmann, F. A. (2020). Shortcut learning in deep neural "
    "networks. *Nature Machine Intelligence, 2*(11), 665–673.",
    "Gundupalli, S. P., Hait, S., & Thakur, A. (2018). Classification of metallic and non-metallic fractions of e-waste using thermal imaging-based "
    "technique. *Process Safety and Environmental Protection*. https://www.sciencedirect.com/science/article/abs/pii/S0957582018303434",
    "Hennig, C. (2007). Cluster-wise assessment of cluster stability. *Computational Statistics & Data Analysis, 52*(1), 258–271.",
    "Huang, K., Song, M., Ba, S., An, L., Liang, H., Deng, H., Liu, Y., Zhang, Z., & Zhou, C. (2025). Unsupervised waste classification by dual-encoder "
    "contrastive learning and multi-clustering voting (DECMCV). *arXiv:2503.02241*.",
    "Islam, N., Jony, M. M. H., Hasan, E., Sutradhar, S., Rahman, A., & Islam, M. M. (2023). EWasteNet: A two-stream data efficient image transformer "
    "approach for e-waste classification. *arXiv:2311.12823*.",
    "Jano, T., et al. (2026). Closing the loop: A systematic review of artificial intelligence in circular e-waste management. *Waste Management, 214*, "
    "115392.",
    "Ng, A. Y., Jordan, M. I., & Weiss, Y. (2002). On spectral clustering: Analysis and an algorithm. *Advances in Neural Information Processing "
    "Systems, 14*.",
    "Pemerintah Republik Indonesia. (2020). *Peraturan Pemerintah Nomor 27 Tahun 2020 tentang Pengelolaan Sampah Spesifik*.",
    "Rajeev, P. A., Dharewa, V., Lakshmi, D., et al. (2025). Advancing e-waste classification with customizable YOLO based deep learning models. "
    "*Scientific Reports, 15*, 18151. https://doi.org/10.1038/s41598-025-94772-x",
    "Ravfogel, S., Elazar, Y., Gonen, H., Twiton, M., & Goldberg, Y. (2020). Null it out: Guarding protected attributes by iterative nullspace "
    "projection. *Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics*, 7237–7256.",
    "Siméoni, O., et al. (2025). DINOv3. *arXiv:2508.10104*.",
    "Sun, Y., Ming, Y., Zhu, X., & Li, Y. (2022). Out-of-distribution detection with deep nearest neighbors. *Proceedings of the 39th International "
    "Conference on Machine Learning (ICML)*, 20827–20840.",
    "Tschannen, M., et al. (2025). SigLIP 2: Multilingual vision-language encoders with improved semantic understanding, localization, and dense "
    "features. *arXiv:2502.14786*.",
    "Venkateswara, H., Eusebio, J., Chakraborty, S., & Panchanathan, S. (2017). Deep hashing network for unsupervised domain adaptation. *Proceedings "
    "of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR)*, 5018–5027.",
    "Xu, H., et al. (2024). Demystifying CLIP data. *Proceedings of the International Conference on Learning Representations (ICLR)*.",
    "Zhang, L., Liu, S., Wang, S., Yu, S., Zhu, X., Li, M., & Liu, X. (2026). Parameter-free clustering via self-supervised consensus maximization. "
    "*Proceedings of the AAAI Conference on Artificial Intelligence (AAAI-26)*.",
    "Zhou, C., Sterkens, W., Díaz-Romero, D. J., Zaplana, I., & Peeters, J. (2023). You only demanufacture once (YODO): WEEE retrieval using "
    "unsupervised learning. *Resources, Conservation & Recycling, 190*, 106826.",
    "Zhou, C., Wu, Y., Sterkens, W., Vandewalle, P., Zhang, J., & Peeters, J. R. (2025). Multi-view graph transformer for WEEE classification and "
    "retrieval. *Resources, Conservation & Recycling, 215*, 108112.",
    "**Sumber data tambahan:** Kaan Erkez, Waste Classification Dataset (https://www.kaggle.com/datasets/kaanerkez/waste-classfication-dataset); "
    "Custom Bangladeshi E-Waste (https://data.mendeley.com/datasets/77383kmdnw/1); Karan Solanki, Garbage Classification "
    "(https://www.kaggle.com/datasets/karansolanki01/garbage-classification); GIZ, E-Waste Database (https://huggingface.co/datasets/GIZ/E-Waste-Database); "
    "Electronic Waste Detection (Iliev), E-Waste Dataset (https://universe.roboflow.com/electronic-waste-detection/e-waste-dataset-r0ojc); Shubha, "
    "E-waste Dataset (https://universe.roboflow.com/shubha-to6ii/e-waste-1sn3k); Office-Home (https://huggingface.co/datasets/flwrlabs/office-home).",
])

# ---------------------------------------------------------------- 6. LAMPIRAN
h1("LAMPIRAN")
para("body",
     "Kode lengkap (ekstraksi fitur, seluruh eksperimen, validasi, dan pembuatan gambar) tersedia pada repositori: **[TAUTAN REPOSITORI]**. "
     "Struktur utamanya: modal_app.py (orkestrasi komputasi cloud), embed_kg.py/embed_extra.py/embed_new.py (ekstraksi fitur), rq_max.py (audit 17 "
     "representasi), rq_final2.py (pembanding adil), rq_scmax.py (SCMax), rq_fix.py dan rq_fix2.py (uji ketahanan dan OOD), rq_iliev.py, rq_shubha.py, "
     "dan rq_officehome.py (validasi), final_max.py (partisi final dan galeri), rq_r8.py, rq_r8b.py, rq_d1.py, dan rq_notest.py (bootstrap berpasangan, "
     "aturan acuan tanpa label, pembanding pada fitur yang sama, dan uji tanpa data uji), make_figures.py (gambar), serta reproduce.py (reproduksi "
     "partisi final di CPU dalam kurang dari 1 menit). Implementasi inti pipeline "
     "(ewaste_cmre.py) disajikan berikut.")
src = open(f"{ROOT}/code/ewaste_cmre.py", encoding="utf-8").read()
core = src[src.index("import numpy"):src.index('if __name__')].rstrip().splitlines()  # module docstring and smoke test stay in the repo
code([ln for ln in core if ln.strip()])
table("CMRE dengan model acuan berbeda (BDC, K = 16), diurutkan menurut R² ridge tanpa label",
      ["Model acuan", "Jenis", "R² ridge", "xsrc mentah", "xsrc CMRE"],
      [["DINOv3-7B", "SSL", "0,434", "0,568", "0,983"], ["**DINOv3-H+ (usulan)**", "SSL", "0,403", "0,524", "**0,975**"],
       ["ConvNeXt V2-H", "berlabel", "0,392", "0,480", "0,384"], ["DINOv3-L", "SSL", "0,390", "0,550", "0,596"],
       ["Web-DINO-1B", "SSL", "0,382", "0,550", "0,917"], ["Web-DINO-300M", "SSL", "0,358", "0,591", "0,930"],
       ["DINOv2-L", "SSL", "0,351", "0,516", "0,777"], ["DINOv3-B", "SSL", "0,347", "0,481", "0,593"], ["DINOv3-ConvNeXt-L", "SSL", "0,345", "0,593", "0,726"]],
      [4.6, 2.2, 2.4, 2.6, 2.6], align=["left", "center", "center", "center", "center"],
      note="R² ridge: kemampuan acuan memprediksi embedding VLM (validasi silang 5 lipatan, tanpa label). Korelasi peringkat R² dengan xsrc pada "
           "delapan acuan SSL = 0,69; acuan berlabel dikecualikan secara prinsip.")
table("Uji bootstrap berpasangan: selisih xsrc usulan dikurangi pembanding [IK95%], 2.000 ulangan",
      ["Pembanding", "BDC", "Iliev", "Shubha"],
      [["Fusi mentah", "+0,451 [0,429; 0,476]", "+0,082 [0,057; 0,106]", "+0,600 [0,559; 0,637]"],
       ["DINOv3-H+ saja", "+0,217 [0,188; 0,244]", "+0,130 [0,113; 0,149]", "+0,067 [0,034; 0,105]"],
       ["INLP ×3 (butuh proksi)", "−0,008 [−0,021; 0,005]", "+0,003 [−0,017; 0,023]", "−0,017 [−0,037; 0,000]"],
       ["Versi ringan PE + DINOv3", "+0,006 [−0,010; 0,021]", "+0,003 [−0,008; 0,017]", "+0,011 [0,000; 0,029]"],
       ["Versi cepat SigLIP2 + DINOv3", "+0,024 [0,005; 0,047]", "+0,025 [0,009; 0,043]", "+0,033 [0,011; 0,061]"]],
      [4.6, 3.5, 3.5, 3.5], align=["left", "center", "center", "center"],
      note="Nilai positif berarti usulan lebih tinggi. Selisih terhadap INLP dan versi ringan tidak signifikan (interval memuat nol).")
figure("fig8_hierarchy.png", "Hierarki kelompok: pemecahan partisi K = 13 menjadi K = 16 (garis menunjukkan porsi citra ≥ 5%).", width=14.0)
figure("fig9_heatmap.png", "Komposisi label nama berkas BDC per kelompok (proporsi baris; label hanya dipakai untuk evaluasi).", width=13.5)

doc.save(OUT)
print("saved", OUT, "| figures", FIG_N[0], "| tables", TAB_N[0], "| equations", EQ_N[0])
