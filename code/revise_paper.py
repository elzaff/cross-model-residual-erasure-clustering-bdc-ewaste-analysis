"""Edit the current BDC 2026 manuscript while preserving tables and Word equations."""

from pathlib import Path
from copy import deepcopy
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt


HERE = Path(__file__).resolve().parents[1] / "paper"
SOURCE = HERE / "Karya_Ilmiah_BDC2026_sumber_revisi.docx"
TARGET = HERE / "Karya_Ilmiah_BDC2026_revisi_gaya_BDC12.docx"

TITLE = (
    "PENGELOMPOKAN SAMPAH ELEKTRONIK TANPA LABEL DARI CITRA MULTISUMBER "
    "DENGAN CROSS-MODEL RESIDUAL ERASURE DAN SPECTRAL CLUSTERING"
)

ENGLISH_TERMS = re.compile(
    r"\b(?:Cross-Model Residual Erasure|Spectral clustering|Perception Encoder|"
    r"Adjusted Mutual Information|Normalized Mutual Information|out-of-distribution|"
    r"perceptual hash|horizontal flip|average linkage|nearest-neighbou?r|fine-tuning|"
    r"self-supervised|vision-language|embedding(?:s)?|encoder(?:s)?|"
    r"clustering|cluster(?:s)?|centroid(?:s)?|bootstrap|silhouette|"
    r"pipeline|dataset|transformer|agglomerative|transfer|purity|"
    r"probe|ridge|seed(?:s)?|frozen|raw|flip|patch|token|crop(?:s)?|"
    r"style|baseline|domain|erasure|Spectral|cloud|random_state|fit)\b",
    re.IGNORECASE,
)


def polish_punctuation(text, sentence_mode):
    result = []
    parenthesis = bracket = 0
    i = 0
    while i < len(text):
        char = text[i]
        if char == ";":
            if bracket:
                result.append("–")
            elif parenthesis or not sentence_mode:
                result.append(",")
            else:
                result.append(".")
            i += 1
            while i < len(text) and text[i] == " ":
                i += 1
            if not bracket and i < len(text) and text[i] != ")":
                result.append(" ")
                if sentence_mode and not parenthesis and not bracket:
                    char = text[i].upper()
                    result.append(char)
                    i += 1
            continue
        result.append(char)
        if char == "(":
            parenthesis += 1
        elif char == ")":
            parenthesis -= 1
        elif char == "[":
            bracket += 1
        elif char == "]":
            bracket -= 1
        i += 1
    return "".join(result)


def italicize_english(paragraph):
    for run in list(paragraph.runs):
        matches = list(ENGLISH_TERMS.finditer(run.text))
        if not matches:
            continue
        original_text = run.text
        original_style = deepcopy(run._r.rPr)
        original_italic = run.italic
        parts = []
        start = 0
        for match in matches:
            if match.start() > start:
                parts.append((original_text[start:match.start()], False))
            parts.append((match.group(), True))
            start = match.end()
        if start < len(original_text):
            parts.append((original_text[start:], False))
        run.text = parts[0][0]
        run.italic = True if parts[0][1] else original_italic
        anchor = run._r
        for value, italic in parts[1:]:
            new_run = paragraph.add_run(value)
            anchor.addnext(new_run._r)
            if original_style is not None:
                new_run._r.insert(0, deepcopy(original_style))
            new_run.italic = True if italic else original_italic
            anchor = new_run._r


KEY_FINDINGS = re.compile(
    r"CMRE menaikkan konsistensi lintas sumber dari 0,524 menjadi 0,975|"
    r"Adjusted Mutual Information \(AMI\) pada 2\.329 citra BDC berlabel mencapai 0,917|"
    r"hanya 20 seed memilih angka itu|"
    r"CMRE menaikkan xsrc fusi dari 0,524 menjadi 0,975|"
    r"CMRE menaikkan xsrc BDC dari 0,524 menjadi 0,975|"
    r"xsrc Iliev naik dari 0,803 menjadi 0,885 dan Shubha dari 0,356 menjadi 0,956|"
    r"ARI antarpasangan partisi hanya 0,861"
)


def emphasize_findings(paragraph):
    for run in list(paragraph.runs):
        matches = list(KEY_FINDINGS.finditer(run.text))
        if not matches:
            continue
        original_text = run.text
        original_style = deepcopy(run._r.rPr)
        original_bold = run.bold
        parts = []
        start = 0
        for match in matches:
            if match.start() > start:
                parts.append((original_text[start:match.start()], False))
            parts.append((match.group(), True))
            start = match.end()
        if start < len(original_text):
            parts.append((original_text[start:], False))
        run.text = parts[0][0]
        run.bold = True if parts[0][1] else original_bold
        anchor = run._r
        for value, marked in parts[1:]:
            new_run = paragraph.add_run(value)
            anchor.addnext(new_run._r)
            if original_style is not None:
                new_run._r.insert(0, deepcopy(original_style))
            new_run.bold = True if marked else original_bold
            anchor = new_run._r

REWRITE = {
    4: TITLE,
    20: TITLE,
    24: (
        "Latar dan resolusi foto dapat membuat sampah elektronik sejenis terpisah saat dikelompokkan tanpa label. "
        "Kami menguji 3.792 citra BDC dengan embedding SigLIP2, Perception Encoder, dan DINOv3. "
        "Cross-Model Residual Erasure (CMRE) memproyeksikan keluar arah dominan dari bagian embedding visi-bahasa yang tidak dapat diprediksi DINOv3. Langkah ini tidak memerlukan label objek atau proksi gaya. "
        "SCMax memilih jumlah kelompok, Spectral clustering membentuk partisi, dan jarak tetangga terdekat menandai citra di luar cakupan kelompok. "
        "Pada data pengembangan, CMRE menaikkan konsistensi lintas sumber dari 0,524 menjadi 0,975. Adjusted Mutual Information (AMI) pada 2.329 citra BDC berlabel mencapai 0,917. "
        "CMRE tidak berbeda signifikan dari INLP yang memakai proksi gaya. Audit 100 seed SCMax memberi median K = 16, tetapi hanya 20 seed memilih angka itu. Pada Iliev, konsistensi naik dari 0,803 menjadi 0,885 dan pada Shubha dari 0,356 menjadi 0,956. "
        "Enam belas kelompok akhir memisahkan subtipe baterai, perangkat berlayar, dan mesin cuci. Deteksi kategori baru mencapai AUROC 0,994 pada Shubha yang hanya menyediakan dua kelas baru. "
        "Hasil ini berlaku untuk sumber foto yang diuji. Foto rumah tangga Indonesia masih memerlukan pengujian tersendiri."
    ),
    26: "Kata kunci: sampah elektronik; pengelompokan tanpa label; bias sumber foto; representasi visual; deteksi kategori baru",
    28: "PENDAHULUAN",
    29: (
        "Dunia menghasilkan 62 juta ton sampah elektronik pada 2022. Dari jumlah itu, 22,3% tercatat dikumpulkan dan didaur ulang secara layak (Baldé et al., 2024). "
        "Di Indonesia, perkiraan timbulan 2021 mencapai 2 juta ton dan 17,4% di antaranya dikelola dengan baik (Defitri, 2022). "
        "Pemilahan awal menentukan jalur pengolahan, padahal perangkat yang tampak serupa dapat mengandung bahan berbahaya yang berbeda."
    ),
    30: (
        "Aki dan kaca tabung CRT mengandung timbal; baterai litium dapat terbakar ketika rusak; beberapa lampu serta layar lama mengandung merkuri. "
        "Peraturan Pemerintah Nomor 27 Tahun 2020 mengatur sampah yang mengandung bahan berbahaya dan beracun sebagai sampah spesifik (Pemerintah Republik Indonesia, 2020). "
        "Karena itu, salah mengenali perangkat pada tahap pemilahan dapat berdampak pada keselamatan pembongkaran dan pilihan jalur pengolahan."
    ),
    31: (
        "Petugas dapat memakai foto untuk mengenali perangkat sebelum memilahnya. Citra produk berlatar putih, foto objek dengan latar beragam, dan foto lapangan memberi model ciri akuisisi yang berbeda. "
        "Jika model mengikuti ciri itu, perangkat sejenis dapat terpisah ke kelompok berbeda. Pelabelan manual ribuan foto memerlukan tenaga, sementara daftar kategori awal dapat melewatkan subtipe perangkat. "
        "Penelitian ini menguji pengelompokan tanpa label pada foto dari beberapa sumber."
    ),
    32: (
        "Gundupalli et al. (2018) memilah fraksi material dari citra termal yang memerlukan kamera khusus (Tabel 1). "
        "Islam et al. (2023) dan Rajeev et al. (2025) meneliti klasifikasi serta deteksi pada kelas yang telah ditetapkan dan memakai label saat pelatihan. "
        "YODO menelusuri laptop di lini pembongkaran tanpa label (Zhou et al., 2023). DECMCV mengelompokkan sampah umum tanpa label, tetapi membuang citra ketika metode-metodenya tidak sepakat. Penulisnya juga melaporkan gangguan akibat gaya foto (Huang et al., 2025). "
        "Studi tersebut belum mengukur apakah foto perangkat sejenis dari sumber berbeda tetap berada dalam kelompok yang sama."
    ),
    36: (
        "Masalah penelitian dirumuskan dalam empat pertanyaan. Pertama, apakah representasi visual lebih dipengaruhi sumber foto daripada jenis perangkat? Kedua, dapatkah pengaruh tersebut dikurangi tanpa label atau proksi gaya? "
        "Ketiga, apakah kelompok yang terbentuk cukup stabil dan dapat ditafsirkan setelah jumlah kelompok dipilih tanpa label? Keempat, apakah foto dari sumber lain dan perangkat di luar kategori dapat ditangani tanpa membentuk ulang kelompok?"
    ),
    37: (
        "Kami membentuk kelompok pada citra utama BDC, lalu menilai citra eksternal dengan representasi dan partisi yang sudah tetap. "
        "Label dari nama berkas dan kategori WEEE baru dipakai untuk menafsirkan kelompok setelah partisi selesai. "
        "CMRE memprediksi embedding visi-bahasa dari DINOv3 dan membuang arah dominan pada residunya. SCMax memilih K, Spectral clustering membentuk kelompok, dan jarak tetangga menandai citra di luar cakupan. "
        "Rancangan ini memungkinkan pengujian bias sumber tanpa proksi gaya, transfer antar sumber foto, dan deteksi kategori baru. Pemakaian untuk pemilahan nyata masih memerlukan pengujian pada foto dari Indonesia."
    ),
    39: "METODOLOGI",
    40: "2.1 Data dan pemisahan peran dataset",
    41: (
        "Dari 3.961 citra e-waste BDC, deduplikasi perceptual hash pada jarak Hamming 6 menyisakan 3.604 citra latih unik. "
        "Data utama juga mencakup 188 citra uji penyisihan yang dipilih berdasarkan prediksi pengklasifikasi SigLIP2 dari babak sebelumnya. Label panitia tidak tersedia pada tahap ini. Jumlah akhirnya 3.792 citra. "
        "Ketika seluruh pipeline diulang pada 3.604 citra latih saja, xsrc tetap 0,975 dan ARI terhadap partisi utama pada citra latih mencapai 0,93. "
        "Nama berkas memberi label objek valid untuk 2.329 citra dalam sepuluh kelas. Dua entri bernama upload dikeluarkan dari evaluasi kelas dan 1.461 citra tidak memiliki label nama berkas. "
        "Ekstraksi fitur, pemilihan K, dan pembentukan cluster tidak memakai label tersebut."
    ),
    42: (
        "Tujuh set data publik melengkapi evaluasi dengan peran yang berbeda (Tabel 2). Citra eksternal mendapat kelompok berdasarkan partisi BDC yang tetap, tanpa pelatihan ulang. "
        "Audit perceptual hash menemukan bahwa 55% citra Kaan beririsan dengan BDC. Duplikat itu dibuang sebelum evaluasi untuk mencegah kebocoran. "
        "Protokol dan pemetaan kelas Iliev serta Shubha ditetapkan sebelum data diunduh. Sebaliknya, lebih dari 40 varian metode dibandingkan memakai xsrc BDC, sehingga nilainya merupakan hasil pengembangan. "
        "Office-Home hanya dipakai untuk pengujian sesuai lisensi riset nonkomersial."
    ),
    46: (
        "Sebanyak 66% citra BDC berukuran paling tinggi 200 piksel. Banyak citra produk Kaan juga kecil dan berlatar putih. "
        "Foto objek Bangladesh umumnya sekitar 640 piksel dengan latar beragam, sedangkan foto lapangan GIZ mendekati 1.000 piksel. "
        "Perbedaan resolusi dan latar ini dapat mengubah ketetanggaan embedding meskipun jenis perangkat sama. Karena itu, evaluasi mengukur konsistensi lintas sumber selain kesesuaian kelompok pada BDC."
    ),
    51: "2.2 Landasan metode",
    52: (
        "SigLIP2 dan Perception Encoder belajar dari hubungan citra dan teks menurut Tschannen et al. (2025) dan Bolya et al. (2025). "
        "DINOv3 mempelajari representasi visual tanpa pasangan teks (Siméoni et al., 2025). "
        "Ketiga encoder citra tetap beku selama eksperimen. Perbandingan representasi tunggal dan fusi menguji apakah tujuan prapelatihan yang berbeda berkaitan dengan ketahanan terhadap sumber foto pada data penelitian ini."
    ),
    53: (
        "Ciri resolusi, latar, atau pencahayaan dapat menjadi jalan pintas bagi model ketika berkorelasi dengan kelas pada data latih (Geirhos et al., 2020). "
        "HEX memakai statistik tekstur GLCM sebagai representasi pembantu lalu memproyeksikan fitur menjauhi subruangnya (Wang et al., 2019). UMFC memperkirakan bias domain dari fitur visual dan transisi domain teks tanpa label kategori (Liang et al., 2024). "
        "Ravfogel et al. (2020) memakai probe berulang untuk atribut yang ditentukan melalui INLP. Belrose et al. (2023) menghapus konsep target secara linear melalui LEACE. "
        "CMRE memakai residu prediksi embedding visi-bahasa dari acuan DINOv3 untuk memilih arah proyeksi. PCA mencari arah dominan pada residu citra utama, lalu proyeksi mengeluarkan arah itu dari embedding visi-bahasa. "
        "Pemilihan arah ini tidak memerlukan label gaya atau statistik tekstur buatan. Residu dapat pula memuat informasi objek."
    ),
    54: (
        "Spectral clustering mempartisi graf tetangga terdekat melalui vektor eigen Laplacian (Ng et al., 2002). "
        "SCMax menggabungkan clustering hierarkis dan skor konsensus tetangga untuk memilih jumlah kelompok (Zhang et al., 2026). "
        "K keluaran SCMax menjadi input Spectral clustering untuk partisi akhir. Hierarki internal SCMax tidak dipakai sebagai taksonomi. "
        "Jarak citra baru ke tetangga terdekat pada data utama menjadi skor deteksi di luar distribusi (Sun et al., 2022)."
    ),
    55: "2.3 Rancangan metode",
    56: (
        "Deduplikasi dan ekstraksi embedding mendahului proyeksi CMRE. SCMax lalu memilih K pada fitur hasil fusi dan Spectral membentuk partisi. "
        "Evaluasi memeriksa kelompok dan kategori baru setelah partisi tetap. Label objek hanya dipakai pada tahap tersebut."
    ),
    61: (
        "Setelah deduplikasi, setiap model menerima citra pada ukuran inputnya dalam orientasi asli dan horizontal flip. Kedua embedding kemudian dirata-ratakan. "
        "SigLIP2-So400m dan PE-Core-G menyediakan representasi visi-bahasa. DINOv3-H+ menjadi acuan visual tanpa supervisi bahasa. "
        "Regresi ridge memprediksi embedding V dari embedding DINOv3 S untuk masing-masing model visi-bahasa. Selisih prediksi membentuk residu R (Persamaan 1). "
        "PCA mencari arah dominan U_r pada R (Persamaan 2), kemudian proyeksi mengeluarkan arah tersebut dari V (Persamaan 3). "
        "Residu dapat memuat informasi objek selain gaya foto. Kami menilai konsekuensi penghapusannya melalui metrik objek dan lintas sumber."
    ),
    65: (
        "Aturan tanpa label mengambil arah hingga 50% varians residu, dengan batas 64 komponen. Pada data ini r mencapai 64. Regresi ridge memakai α = 1. "
        "DINOv3-H+ menjadi acuan karena R² prediksi silang embedding VLM mencapai 0,403. DINOv3-7B sedikit lebih tinggi, 0,434, tetapi memerlukan GPU A100. "
        "Fusi menggabungkan dua embedding hasil CMRE dan embedding DINOv3. PCA mereduksinya menjadi 32 dimensi sebelum normalisasi (Persamaan 4). "
        "Istilah erasure menyebut proyeksi arah residu. Probe sumber masih dapat membaca informasi sumber setelah proyeksi."
    ),
    67: (
        "Kami menjalankan SCMax pada embedding fusi dengan sembilan seed dan memakai median K = 16 untuk partisi akhir. Audit berikutnya mengulang SCMax pada seed 0–99 dengan citra dan embedding tetap. "
        "Untuk setiap K terpilih, Spectral clustering membentuk partisi pada graf 15 tetangga, lalu citra eksternal diproyeksikan dengan cara yang sama. Audit ini tidak mengulang ekstraksi fitur atau pengambilan sampel data. "
        "Setelah partisi akhir tetap, kami memeriksa citra untuk menamai kelompok dan mengaitkannya dengan kategori WEEE. Kami juga menggabungkan centroid dari 16 kelompok memakai agglomerative average linkage dan jarak kosinus untuk membaca hubungan antarkelompok. Penggabungan ini tidak mengubah partisi Spectral atau K pilihan SCMax. "
        "Pusat kelompok terdekat menentukan penempatan citra baru. Jarak ke tetangga ke-10 pada data utama menjadi skor OOD, dengan persentil ke-95 skor data utama sebagai ambang (Persamaan 5). Ekstraksi fitur memakai GPU cloud dan clustering memakai CPU."
    ),
    69: "2.4 Protokol dan metrik evaluasi",
    70: (
        "Perbandingan representasi tunggal mengukur bias sumber. Fusi mentah, INLP, LEACE, dan CMRE menguji cara menguranginya. "
        "Pada fitur yang sama, kami membandingkan Spectral dengan K-Means, Ward, GMM, TEMI, TURTLE, dan protokol DECMCV. Iliev, Shubha, dan Office-Home menguji transfer setelah pipeline tetap. "
        "Perbandingan pada K tetap memakai PCA-32 dan K = 16, sementara audit SCMax memakai K pilihan tiap seed. Sapuan r dan jumlah tetangga mengukur kepekaan parameter. Skor BDC berasal dari proses pengembangan, sehingga tidak diperlakukan sebagai validasi independen."
    ),
    71: (
        "Penilaian dipisahkan menurut pertanyaan penelitian (Tabel 3). Konsistensi lintas sumber, xsrc (Persamaan 6), dihitung dari lima kelas yang sama pada citra produk Kaan dan foto objek Bangladesh. Untuk setiap kelas c, kelompok mayoritas Kaan menjadi acuan; proporsi Bangladesh yang masuk kelompok itu dirata-ratakan antarkelas. "
        "Nilai xsrc berada antara 0 dan 1, tetapi nilainya juga dapat tinggi bila kelompok terlalu sedikit. Karena itu, perbandingan metode turut menampilkan Normalized Mutual Information (NMI) objek pada 1.869 citra eksternal berlabel dari Kaan, Bangladesh, dan Karan serta proporsi citra yang diberi kelompok. "
        "AMI pada 2.329 citra BDC berlabel dipakai hanya untuk mengaudit partisi final setelah pilihan metode dibekukan. AMI menyesuaikan kesesuaian cluster dan kelas terhadap peluang acak; nilai 1 berarti identik dan nilai sekitar 0 berarti setara acak (Vinh et al., 2010). "
        "Kestabilan dibaca dari Jaccard bootstrap per kelompok dan sebaran K antarseed, sedangkan deteksi kategori baru dinilai melalui AUROC dan alarm palsu pada ambang yang telah ditetapkan. Indeks internal seperti silhouette dipakai sebagai diagnostik, bukan bukti kesamaan objek lintas sumber."
    ),
    74: "Tabel 3. Metrik inti sesuai pertanyaan penelitian dan batas interpretasinya",
    77: "HASIL DAN PEMBAHASAN",
    78: "3.1 Bias sumber pada representasi visual",
    79: (
        "Dengan protokol yang sama, SigLIP2 dan CLIP menempatkan sekitar 37% foto objek Bangladesh ke kelompok mayoritas citra produk Kaan dari kelas yang sama. DINOv3-H+ mencapai 0,86. "
        "MetaCLIP, yang belajar dari pasangan citra-teks, menghasilkan xsrc 0,20 (Xu et al., 2024). Web-DINO tanpa pasangan teks mencapai 0,70 (Fan et al., 2025). "
        "Pola tersebut sesuai dengan dugaan bahwa supervisi bahasa dapat memperkuat ciri sumber foto. Arsitektur dan data pelatihan kedua model belum sepenuhnya sepadan, sehingga perbandingan ini belum membuktikan penyebabnya."
    ),
    80: (
        "Fusi mentah mencapai NMI objek 0,948 pada audit BDC awal, tetapi xsrc hanya 0,524. NMI tersebut memakai 2.331 entri nama berkas sebelum dua entri upload dikeluarkan dari sepuluh kelas objek. "
        "Karena itu, angka NMI awal hanya menjadi diagnostik. Skor pada satu sumber tidak menggambarkan perilaku kelompok ketika sumber foto berubah."
    ),
    85: "3.2 Pengaruh CMRE terhadap konsistensi lintas sumber",
    86: (
        "Pada partisi K = 16, CMRE menaikkan xsrc fusi dari 0,524 menjadi 0,975. NMI objek pada data eksternal naik dari 0,789 menjadi 0,859, dan seluruh citra tetap diberi kelompok (Tabel 4). "
        "AMI pada 2.329 citra BDC berlabel mencapai 0,917. xsrc per kelas berkisar dari 0,920 untuk baterai hingga 1,000 untuk keyboard dan mouse. Ponsel mencapai 0,981 dan PCB 0,977. "
        "INLP dengan proksi gaya juga mencapai xsrc 0,975. Interval selisihnya memuat nol, sehingga uji ini belum membedakan kinerja CMRE dan INLP. LEACE dengan proksi mencapai 0,792. "
        "Pada embedding CMRE yang sama, TURTLE menghasilkan 0,790, TEMI 0,590, dan protokol DECMCV 0,910. DECMCV hanya mempertahankan 81% citra, sehingga skor itu memiliki cakupan berbeda. "
        "Dalam 2.000 bootstrap berpasangan, CMRE melampaui fusi mentah dan DINOv3 saja pada BDC, Iliev, dan Shubha (p < 0,001). CMRE mencapai hasil tersebut tanpa definisi proksi gaya foto."
    ),
    88: "Tabel 4. Perbandingan metode pada K = 16 di data pengembangan",
    89: (
        "xsrc adalah rerata makro lima kelas Kaan-Bangladesh; NMI objek eksternal memakai 1.869 citra dari lima kelas bersama pada Kaan, Bangladesh, dan Karan. "
        "Cakupan menunjukkan bagian citra yang tetap diberi kelompok; n.d. berarti NMI belum dihitung dalam arsip pembanding, bukan bernilai nol. "
        "Metode bertanda † dijalankan pada embedding CMRE yang sama dengan K = 16 dan rerata tiga seed. DECMCV membuang citra yang tidak disepakati, sehingga xsrc-nya perlu dibaca bersama cakupan 81%."
    ),
    91: (
        "Probe objek yang dilatih pada citra produk Kaan mencapai akurasi 0,944 pada foto objek Bangladesh sebelum CMRE dan 0,983 sesudahnya. "
        "Arah yang dibuang berkorelasi dengan resolusi (|ρ| hingga 0,68) dan proporsi latar putih (0,39). Probe sumber masih mencapai 0,96-0,99, sehingga CMRE tidak menghilangkan identitas sumber dari embedding. "
        "Ketika acuan diganti dengan ConvNeXt V2 berlabel, xsrc turun menjadi 0,384. Pada sembilan pasangan model, besar manfaat CMRE berkaitan dengan jejak gaya awal (Spearman 0,78). Korelasi ini membantu menafsirkan hasil, tetapi belum mengisolasi mekanisme proyeksi."
    ),
    92: (
        "Pada Iliev, xsrc CMRE mencapai 0,885 (IK95% 0,864-0,908), dibanding 0,803 untuk fusi mentah dan 0,755 untuk DINOv3 saja. Purity mencapai 0,939. Kami mengunci pemetaan kelas dan metrik Iliev sebelum mengunduh datanya. "
        "Iliev kemudian dipakai memilih skor OOD. Status uji terkunci karena itu hanya berlaku untuk evaluasi clustering. "
        "Pada 300 crop Shubha, CMRE menaikkan xsrc dari 0,356 menjadi 0,956 (IK95% 0,924-0,983). "
        "Office-Home menghasilkan pola berbeda. Fusi mentah sudah mencapai xsrc 0,865 dan CMRE memberi 0,864, walaupun silhouette naik dari 0,39 menjadi 0,48. "
        "Kenaikan xsrc terbesar muncul pada data dengan bias sumber awal yang kuat. Pada Office-Home, CMRE tidak memperbaiki transfer."
    ),
    97: "3.3 Pemilihan jumlah kelompok dan sensitivitas parameter",
    98: (
        "Dalam 100 seed, SCMax memilih K = 16 sebagai median dan K = 17 sebagai modus. Sebarannya ialah K = 13 (2 seed), 14 (10), 15 (20), 16 (20), 17 (21), 18 (14), 19 (10), 20 (2), dan 21 (1). Partisi final tetap memakai K = 16 dari sembilan seed awal. "
        "Jika Spectral mengikuti K setiap seed, rerata xsrc menjadi 0,923 ± 0,098, dengan median 0,975 dan rentang 0,596-0,988. NMI objek eksternal mencapai 0,854 ± 0,022 dan ARI antarpasangan partisi 0,861 ± 0,110. "
        "Pada 27 seed yang memilih K sedikitnya 18, xsrc berada pada 0,596-0,794. K = 13-17 memberi 0,972-0,988. Variasi ini berasal dari inisialisasi algoritma pada data tetap. "
        "Spectral membentuk partisi terpisah untuk setiap K, sehingga partisi K = 13 tidak menjadi induk partisi K = 16. Setelah partisi K = 16 tetap, kami menggabungkan centroid untuk analisis hierarki. "
        "Empat penggabungan pertama memasangkan dua jenis mesin cuci, dua baterai perangkat, dua pemutar audio, dan dua televisi. Keempat cabang muncul pada seluruh 200 bootstrap yang mempertahankan anggota cluster. Angka itu belum mencakup pengulangan SCMax atau Spectral pada sampel baru."
    ),
    99: (
        "Pada r = 16-64, xsrc berada pada 0,97-0,99. Nilainya turun menjadi 0,449 saat r = 4 dan 0,821 saat r = 128. α = 0,01-1 memberi xsrc 0,975-0,983, sebelum turun pada α yang lebih besar. "
        "Dengan K = 16, Spectral mencapai xsrc 0,975, K-Means 0,949, GMM 0,926, dan Ward 0,836. K-Means memiliki silhouette lebih tinggi daripada Spectral, 0,398 berbanding 0,364, meskipun xsrc-nya lebih rendah. "
        "Graf dengan 15-30 tetangga memberi xsrc 0,975-0,988. Pada 5-10 tetangga, nilainya sekitar 0,91. "
        "Empat seed Spectral tambahan pada K = 16 menghasilkan ARI 1,00 terhadap partisi final. Pemeriksaan ini tidak memasukkan variasi K dari SCMax. Sebelas dari 16 kelompok mencapai Jaccard bootstrap sedikitnya 0,85."
    ),
    104: "3.4 Penafsiran kelompok dan batas taksonomi",
    105: (
        "Tabel 5 merinci isi dominan, jumlah citra, kestabilan, dan kemungkinan penanganan keenam belas kelompok. "
        "Kami memberi nama kelompok setelah memeriksa citranya. Kategori WEEE dan B3 juga ditautkan setelah partisi selesai. Model tidak memakai nama atau kategori tersebut saat membentuk kelompok."
    ),
    113: (
        "Empat penggabungan awal pada hierarki centroid mempertemukan mesin cuci bukaan atas dan depan, baterai laptop dan baterai kecil, dua jenis pemutar audio, serta TV CRT dan layar datar. "
        "Potongan 12 kelompok mempertahankan purity BDC 0,993 pada 2.329 citra berlabel dan xsrc 0,975. Ketika jumlah kelompok turun ke delapan, purity menjadi 0,796 karena kategori perangkat berbeda mulai bergabung. "
        "Hierarki berguna untuk merangkum penggabungan awal, sedangkan cabang atas belum dapat ditafsirkan sebagai taksonomi penanganan. "
        "C9 didominasi laptop walaupun nama berkas BDC mengaitkannya dengan keyboard. Sebanyak 96,7% foto laptop Iliev masuk ke C9. "
        "Pada citra Iliev yang dikenali, 79% penempatan kelompok sesuai kategori EU-6. Angka itu 19% pada 100.000 penggabungan acak dengan ukuran grup sama (p < 0,001). "
        "Jarak antarpusat kelompok dalam satu kategori WEEE tidak lebih kecil dari acak (p = 0,46). Karena itu, kategori WEEE dipakai untuk interpretasi setelah clustering."
    ),
    114: (
        "Dari 449 foto objek Bangladesh pada lima kelas bersama, 12 gagal masuk kelompok mayoritas citra produk Kaan. Tujuh baterai masuk kelompok aki, tiga PCB masuk baterai ponsel, dan dua ponsel masuk baterai. "
        "Beberapa stop kontak masuk C0 bersama objek berbentuk kotak dengan terminal logam. Foto tumpukan campuran terkumpul pada C15 bersama papan sirkuit. "
        "Kelompok aki, CRT, dan baterai kecil memiliki Jaccard bootstrap 0,71-0,82, di bawah kelompok lain. Kesalahan tersebut tetap perlu diperiksa walaupun kemurnian agregat tinggi."
    ),
    115: "3.5 Deteksi perangkat di luar kategori",
    116: (
        "Pada Iliev, skor jarak tetangga terdekat mencapai AUROC OOD 0,937. Skor jarak ke pusat kelompok mencapai 0,868. Kami memilih skor pertama memakai Iliev, sehingga angka ini merupakan hasil pengembangan OOD. "
        "Pada Shubha, AUROC mencapai 0,994 (IK95% 0,984-0,999) dengan dua kelas baru yang tersedia. "
        "Ambang persentil ke-95 menandai 94% foto lampu Bangladesh yang tidak terwakili di BDC, tetapi juga salah menandai 13% foto Bangladesh dari kelas dikenal. "
        "Pada Iliev, alarm muncul pada 97% foto AC, 83% kulkas, dan seluruh foto setrika, kipas angin, lampu LED, serta dispenser air. Pemutar MP3 portabel juga sering memicu alarm karena kelompok pemutar BDC didominasi perangkat lebih besar."
    ),
    117: (
        "Ambang OOD menandai 44,5% foto lapangan GIZ. Foto yang ditandai mencakup banyak AC, kulkas, dan kompresor yang tidak terwakili dalam kelompok utama BDC. "
        "Persentase tersebut belum mengukur akurasi karena label GIZ tidak lengkap. Petugas perlu memeriksa foto beralarm sebelum menentukan jalur penanganan."
    ),
    122: "3.6 Hubungan dengan studi terdahulu dan penggunaan di Indonesia",
    123: (
        "Huang et al. (2025) melaporkan gangguan gaya foto pada DECMCV. CMRE menguji proyeksi residu untuk mengurangi gangguan tersebut tanpa membuang citra, lalu xsrc mengukur apakah perangkat sejenis tetap satu kelompok saat sumber foto berubah. "
        "Islam et al. (2023) menilai klasifikasi pada kategori yang telah ditentukan. Penelitian ini membentuk kelompok sebelum memakai label, sehingga akurasi klasifikasi mereka tidak sepadan dengan xsrc. "
        "Zhou et al. (2025) mengaitkan tipe produk dengan kebutuhan pembongkaran. Kelompok yang memisahkan subtipe perangkat di sini masih memerlukan penilaian ahli sebelum menjadi dasar penanganan."
    ),
    124: (
        "Alat bantu triase foto untuk bank sampah dapat menampilkan kelompok perkiraan, skor OOD, dan pilihan pemeriksaan manual. Foto beralarm memerlukan keputusan petugas. "
        "Versi cepat SigLIP2 dan DINOv3 memproses sekitar 20 citra per detik pada GPU L4, dibanding 3,4 untuk pipeline penuh. xsrc versi cepat mencapai 0,951 pada BDC, 0,860 pada Iliev, dan 0,922 pada Shubha. "
        "Kecepatan tersebut belum diukur pada ponsel. Penerapan di Indonesia masih memerlukan foto rumah tangga setempat dan pemeriksaan jalur penanganan oleh petugas."
    ),
    126: (
        "Kami memakai BDC untuk memilih lebih dari 40 varian. Karena itu, xsrc BDC 0,975 cenderung optimistis. Protokol clustering Iliev dikunci sebelum data diunduh, sedangkan Shubha hanya berisi 300 crop. Data belum memuat foto langsung dari rumah tangga atau bank sampah Indonesia. "
        "Selisih CMRE terhadap INLP pada metrik utama belum signifikan. Ketika DINOv3-H+ diganti DINOv3-B, xsrc turun menjadi 0,593. Probe masih dapat mengenali sumber foto setelah CMRE. "
        "Dalam audit 100 seed, SCMax memilih K antara 13 dan 21. Sebanyak 27 seed dengan K sedikitnya 18 menghasilkan xsrc paling tinggi 0,794. Audit ini memakai embedding tetap. Bootstrap hierarki juga mempertahankan anggota cluster, sehingga keduanya belum mengukur variasi seluruh pipeline pada sampel baru. "
        "Hasil hitung ulang v4 sedikit berbeda dari artefak tersimpan dan penyebab perbedaan fitur belum terisolasi. Ambang OOD global salah menandai 13% foto Bangladesh dari kelas dikenal. Pemutar MP3 dan TV Iliev juga tidak selalu sepadan dengan definisi kelas BDC."
    ),
    128: "PENUTUP",
    129: (
        "SigLIP2 dan CLIP memberi xsrc sekitar 0,37 pada audit awal, sedangkan DINOv3-H+ mencapai 0,86. Pada fusi tiga encoder, CMRE menaikkan xsrc BDC dari 0,524 menjadi 0,975 dan menghasilkan AMI 0,917 pada sepuluh kelas berlabel. "
        "xsrc Iliev naik dari 0,803 menjadi 0,885 dan Shubha dari 0,356 menjadi 0,956. Office-Home tetap sekitar 0,865. Kenaikan terbesar muncul pada data dengan bias sumber awal yang kuat. "
        "Sembilan seed awal memberi median K = 16. Audit 100 seed mempertahankan median itu, tetapi ARI antarpasangan partisi hanya 0,861. Enam belas kelompok akhir memisahkan beberapa subtipe perangkat. Penggabungan centroid menjelaskan pasangan awal, sedangkan cabang atas belum mengikuti kategori penanganan. "
        "Skor OOD kNN mencapai AUROC 0,994 pada Shubha yang memiliki dua kelas baru, sambil salah menandai 13% foto Bangladesh dari kelas dikenal. "
        "Hasil ini mendukung pemakaian kelompok sebagai bahan pemeriksaan foto oleh petugas. Evaluasi belum mencakup foto rumah tangga Indonesia."
    ),
    130: (
        "Pengujian lanjutan perlu mengumpulkan foto rumah tangga dan bank sampah Indonesia, terutama perangkat penukar suhu dan tumpukan campuran. Pemetaan kategori harus ditetapkan sebelum foto itu dinilai. "
        "Ablasi perlu memisahkan kontribusi regresi, proyeksi residu, dan pilihan model acuan. Untuk menilai kestabilan K, seluruh pipeline perlu diulang pada sampel citra baru. "
        "Kalibrasi ambang OOD per kelompok memerlukan data pengembangan terpisah. Versi cepat SigLIP2 dan DINOv3 juga perlu diuji latensinya pada perangkat sasaran sebelum dipakai di lapangan."
    ),
    165: (
        "Kode reproduksi untuk ekstraksi fitur, clustering, dan evaluasi tersedia di "
        "https://github.com/elzaff/cross-model-residual-erasure-clustering-bdc-ewaste. "
        "Cuplikan berikut memperlihatkan operasi inti."
    ),
}

FIGURE_PARAGRAPHS = {
    47, 48, 49, 50, 57, 58, 59, 60, 81, 82, 83, 84,
    93, 94, 95, 96, 100, 101, 102, 103, 106, 107, 108, 109,
    118, 119, 120, 121, 214, 215, 216, 217, 218, 219, 220, 221, 222,
}
CHAPTERS = {28, 39, 77, 128, 132, 164}
SUBCHAPTERS = {40, 51, 55, 69, 78, 85, 97, 104, 115, 122, 125}


def replace_paragraph(paragraph, value):
    paragraph.clear()
    run = paragraph.add_run(value)
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)


def main():
    doc = Document(SOURCE)
    paragraphs = list(doc.paragraphs)

    for index, value in REWRITE.items():
        replace_paragraph(paragraphs[index], value)

    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(12)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.space_after = Pt(0)
    for name, before in (("Heading 1", 10), ("Heading 2", 6)):
        style = doc.styles[name]
        style.font.name = "Times New Roman"
        style.font.size = Pt(12)
        style.font.bold = True
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(3)
        style.paragraph_format.keep_with_next = True

    for index in CHAPTERS:
        paragraphs[index].style = doc.styles["Heading 1"]
    for index in (132, 164):
        properties = paragraphs[index]._p.pPr
        if properties is not None and properties.numPr is not None:
            properties.remove(properties.numPr)
    paragraphs[164].paragraph_format.page_break_before = True
    for index in SUBCHAPTERS:
        paragraphs[index].style = doc.styles["Heading 2"]
    for index, title in ((36, "1.1 Rumusan masalah"), (37, "1.2 Tujuan dan batasan penelitian")):
        paragraph = paragraphs[index].insert_paragraph_before(title)
        paragraph.style = doc.styles["Heading 2"]
    citation = paragraphs[156].insert_paragraph_before(
        "Vinh, N. X., Epps, J., & Bailey, J. (2010). Information theoretic measures for clusterings comparison: "
        "Variants, properties, normalization and correction for chance. "
        "Journal of Machine Learning Research, 11, 2837–2854. https://jmlr.org/papers/v11/vinh10a.html"
    )
    citation.style = paragraphs[156].style
    for paragraph in (*paragraphs[133:163], citation):
        paragraph.paragraph_format.line_spacing = 1.15

    for index in FIGURE_PARAGRAPHS:
        element = paragraphs[index]._element
        element.getparent().remove(element)

    # The literature table should contain prior studies; own results appear later.
    table = doc.tables[0]
    own_row = table.rows[-1]._tr
    own_row.getparent().remove(own_row)

    metric_rows = [
        ("Metrik", "Pertanyaan dan data", "Rentang", "Makna dan batas"),
        ("xsrc makro", "Kesamaan kelompok lima kelas pada Kaan dan Bangladesh", "0–1; naik", "1: semua kelas cocok dengan kelompok acuan; baca bersama NMI dan cakupan."),
        ("NMI objek eksternal", "Kesesuaian kelompok dengan lima label objek pada 1.869 citra eksternal", "0–1; naik", "1: partisi identik; belum dikoreksi terhadap kecocokan acak."),
        ("AMI objek BDC", "Audit partisi akhir pada 2.329 citra berlabel dalam sepuluh kelas", "≈0 acak; maks. 1", "Nilai negatif mungkin; 1: partisi identik. Tidak dipakai memilih model."),
        ("Jaccard bootstrap", "Kestabilan anggota tiap kelompok saat data diambil ulang", "0–1; naik", "1: seluruh anggota pulih; sebaran per kelompok tetap perlu dilaporkan."),
        ("AUROC OOD dan alarm palsu", "Pemisahan kategori baru dari kategori dikenal pada citra eksternal", "0–1", "AUROC 0,5 setara acak; alarm palsu lebih kecil lebih baik pada ambang tetap."),
        ("Cakupan", "Proporsi citra yang memperoleh kelompok", "0–1; naik", "1: seluruh citra ditetapkan; penting bila suatu metode menolak citra."),
    ]
    comparison_rows = [
        ("Metode", "xsrc", "NMI objek ekst.", "Cakupan"),
        ("Fusi mentah", "0,524", "0,789", "100%"),
        ("DINOv3-H+", "0,758", "0,799", "100%"),
        ("TURTLE†", "0,790", "n.d.", "100%"),
        ("TEMI†", "0,590", "n.d.", "100%"),
        ("DECMCV†", "0,910", "n.d.", "81%"),
        ("LEACE×3", "0,792", "0,801", "100%"),
        ("INLP×3", "0,975", "0,853", "100%"),
        ("CMRE cepat", "0,951", "n.d.", "100%"),
        ("CMRE ringan", "0,963", "0,852", "100%"),
        ("CMRE usulan", "0,975", "0,859", "100%"),
    ]
    for table, values, widths in (
        (doc.tables[2], metric_rows, (Cm(3.0), Cm(4.6), Cm(2.1), Cm(5.3))),
        (doc.tables[3], comparison_rows, (Cm(6.5), Cm(2.5), Cm(3.5), Cm(2.5))),
    ):
        while len(table.rows) > len(values):
            table._tbl.remove(table.rows[-1]._tr)
        while len(table.rows) < len(values):
            table.add_row()
        for row_index, (row, values_row) in enumerate(zip(table.rows, values)):
            while len(row._tr.tc_lst) > len(values_row):
                row._tr.remove(row._tr.tc_lst[-1])
            for cell, value in zip(row.cells, values_row):
                cell.text = value
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.name = "Times New Roman"
                        run.font.size = Pt(9)
                        run.font.bold = row_index == 0
        while len(table._tbl.tblGrid.gridCol_lst) > len(values[0]):
            table._tbl.tblGrid.remove(table._tbl.tblGrid.gridCol_lst[-1])
        table.autofit = False
        for column, width in zip(table.columns, widths):
            column.width = width
            for cell in column.cells:
                cell.width = width

    for table in doc.tables:
        properties = table.rows[0]._tr.get_or_add_trPr()
        header = OxmlElement("w:tblHeader")
        header.set(qn("w:val"), "true")
        properties.append(header)

    for index in range(166, 207):
        paragraph = paragraphs[index]
        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        paragraph.paragraph_format.line_spacing = 1.0
        paragraph.paragraph_format.first_line_indent = Pt(0)
        for run in paragraph.runs:
            run.font.name = "Consolas"
            run.font.size = Pt(8)
    paragraphs[208].paragraph_format.page_break_before = True

    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            run.text = run.text.replace("—", ",").replace("–", "-")
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.text = run.text.replace("—", ",").replace("–", "-")

    doc.add_heading("Catatan reproduksi v4", level=2)
    note = doc.add_paragraph(
        "Audit 100 seed SCMax menggunakan embedding dan citra yang tetap. Median K = 16, "
        "tetapi hanya 20 seed memilih tepat K = 16. Sebanyak 27 seed memilih K sedikitnya 18 "
        "dan menghasilkan xsrc paling tinggi 0,794. Rerata ARI antarpasangan partisi adalah "
        "0,861. Sebaran ini menunjukkan kepekaan algoritmik terhadap seed, bukan interval "
        "kepercayaan akibat pengambilan sampel. Bootstrap berpasangan 2.000 kali mengambil "
        "ulang citra evaluasi per kelas tanpa mengulang ekstraksi embedding, CMRE, PCA, atau "
        "pemilihan K. Hitung ulang v4 menghasilkan xsrc BDC 0,970011, sedangkan artefak "
        "tersimpan mencatat 0,975411. Partisi 3.792 citra utama identik (ARI 1,000), "
        "sementara enam dari 3.773 citra luar berubah penempatan centroid. Penyebab teknis "
        "selisih fitur kecil ini belum terisolasi. Metadata lama mencatat r = 65 dari indeks "
        "ambang varians, tetapi PCA hanya menghitung 64 komponen. Jumlah arah yang "
        "diproyeksikan adalah 64. Audit ini belum mengukur variasi dari ekstraksi "
        "ulang, pengambilan sampel baru, atau pemilihan model."
    )
    note.paragraph_format.line_spacing = 1.0
    note.paragraph_format.space_after = Pt(2)
    for run in note.runs:
        run.font.size = Pt(8.5)

    reference_start = next(i for i, p in enumerate(doc.paragraphs) if p.text == "REFERENSI")
    appendix_start = next(i for i, p in enumerate(doc.paragraphs) if p.text == "LAMPIRAN")
    for index, paragraph in enumerate(doc.paragraphs):
        is_reference = reference_start < index < appendix_start
        is_code = any(run.font.name == "Consolas" for run in paragraph.runs)
        sentence_mode = not (is_reference or is_code or paragraph.text.startswith(("Kata kunci:", "Sumber data tambahan:")))
        for run in paragraph.runs:
            run.text = polish_punctuation(run.text, sentence_mode)
        if not is_reference and not is_code:
            emphasize_findings(paragraph)
            italicize_english(paragraph)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.text = polish_punctuation(run.text, False)
                    italicize_english(paragraph)

    doc.save(TARGET)
    print(TARGET)


if __name__ == "__main__":
    main()
