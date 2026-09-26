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
    r"konsistensi lintas sumber naik dari 0,524 menjadi 0,975|"
    r"AMI\) partisi akhir pada 2\.329 citra BDC berlabel mencapai 0,917|"
    r"hanya 20 seed memilih tepat 16 dan 27 seed memilih K sedikitnya 18|"
    r"CMRE menaikkan xsrc fusi dari 0,524 menjadi 0,975|"
    r"Perbaikan xsrc juga tampak pada Iliev \(0,803 menjadi 0,885\) dan Shubha \(0,356 menjadi 0,956\)|"
    r"Office-Home menunjukkan kondisi tanpa perbaikan|"
    r"partisi antar-seed hanya mencapai rerata ARI 0,861"
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
        "Foto sampah elektronik dari sumber berbeda dapat tampak lebih mirip menurut latar dan resolusinya daripada menurut jenis perangkatnya. "
        "Penelitian ini menguji persoalan tersebut pada 3.792 citra utama BDC dengan embedding SigLIP2, Perception Encoder, dan DINOv3. "
        "Cross-Model Residual Erasure (CMRE) mengurangi arah dominan pada residu embedding model visi-bahasa yang tidak terprediksi dari DINOv3, tanpa memakai label objek atau proksi gaya. "
        "Jumlah kelompok dipilih dengan SCMax, partisi dibentuk melalui Spectral clustering, dan citra di luar kelompok yang dikenal ditandai memakai jarak tetangga terdekat. "
        "Pada data pengembangan, konsistensi lintas sumber naik dari 0,524 menjadi 0,975; Adjusted Mutual Information (AMI) partisi akhir pada 2.329 citra BDC berlabel mencapai 0,917. "
        "Selisih terhadap INLP yang memerlukan proksi gaya tidak signifikan pada uji ini. Audit 100 seed SCMax mempertahankan median K = 16, tetapi hanya 20 seed memilih tepat 16 dan 27 seed memilih K sedikitnya 18. Pada set Iliev dengan protokol terkunci, konsistensi mencapai 0,885 dibanding 0,803 tanpa CMRE; pada set konfirmasi Shubha yang lebih kecil, nilainya 0,956 dibanding 0,356. "
        "Enam belas kelompok akhir memisahkan beberapa subtipe baterai, perangkat berlayar, dan mesin cuci. Deteksi kategori baru mencapai AUROC 0,994 pada Shubha, tetapi uji tersebut hanya mencakup dua kelas di luar kategori. "
        "Temuan ini menunjukkan bahwa pengurangan bias sumber membantu pengelompokan lintas foto, sedangkan ketahanan pada foto rumah tangga Indonesia masih perlu diuji."
    ),
    26: "Kata kunci: sampah elektronik; pengelompokan tanpa label; bias sumber foto; representasi visual; deteksi kategori baru",
    28: "PENDAHULUAN",
    29: (
        "Dunia menghasilkan 62 juta ton sampah elektronik pada 2022. Dari jumlah itu, 22,3% tercatat dikumpulkan dan didaur ulang secara layak (Baldé et al., 2024). "
        "Di Indonesia, timbulan pada 2021 diperkirakan sekitar 2 juta ton, sementara bagian yang dikelola dengan baik baru 17,4% (Defitri, 2022). "
        "Angka tersebut menjadikan pemilahan awal penting: perangkat yang tampak serupa dapat memerlukan penanganan berbeda."
    ),
    30: (
        "Aki dan kaca tabung CRT mengandung timbal; baterai litium dapat terbakar ketika rusak; beberapa lampu serta layar lama mengandung merkuri. "
        "Peraturan Pemerintah Nomor 27 Tahun 2020 mengatur sampah yang mengandung bahan berbahaya dan beracun sebagai sampah spesifik (Pemerintah Republik Indonesia, 2020). "
        "Karena itu, salah mengenali perangkat pada tahap pemilahan dapat berdampak pada keselamatan pembongkaran dan pilihan jalur pengolahan."
    ),
    31: (
        "Foto dapat membantu petugas atau warga mengenali jenis perangkat sebelum memilahnya. Akan tetapi, citra produk, foto objek dengan latar beragam, dan foto lapangan memiliki ciri akuisisi yang berbeda. "
        "Model yang belajar dari kemiripan visual mungkin mengikuti perbedaan tersebut, bukan identitas perangkat. "
        "Pelabelan manual seluruh citra mahal, sedangkan kategori yang ditentukan sejak awal dapat melewatkan subtipe penting. Penelitian ini menilai apakah pengelompokan tanpa label dapat mengurangi kedua kendala itu."
    ),
    32: (
        "Penelitian terdahulu memberi titik banding yang berbeda (Tabel 1). Gundupalli et al. (2018) memilah fraksi material melalui citra termal, tetapi memerlukan kamera khusus. "
        "Islam et al. (2023) serta Rajeev et al. (2025) memperoleh hasil klasifikasi dan deteksi yang baik untuk kelas yang telah ditetapkan, dengan kebutuhan label saat pelatihan. "
        "YODO menelusuri laptop di lini pembongkaran tanpa label (Zhou et al., 2023). DECMCV mengelompokkan sampah umum tanpa label dan mencatat gangguan akibat perbedaan gaya foto, tetapi menyisihkan citra yang tidak disepakati antarmetode (Huang et al., 2025). "
        "Dengan demikian, hasil pada satu sumber atau satu jenis perangkat belum menjawab apakah kelompok bertahan ketika objek yang sama difoto dengan cara berbeda."
    ),
    36: (
        "Masalah penelitian dirumuskan dalam empat pertanyaan. Pertama, apakah representasi visual lebih dipengaruhi sumber foto daripada jenis perangkat? Kedua, dapatkah pengaruh tersebut dikurangi tanpa label atau proksi gaya? "
        "Ketiga, apakah kelompok yang terbentuk cukup stabil dan dapat ditafsirkan setelah jumlah kelompok dipilih tanpa label? Keempat, apakah foto dari sumber lain dan perangkat di luar kategori dapat ditangani tanpa membentuk ulang kelompok?"
    ),
    37: (
        "Untuk menjawabnya, penelitian ini memakai citra utama BDC untuk menemukan kelompok, lalu menilai hasilnya pada data eksternal dengan representasi dan partisi yang dibekukan. "
        "Label nama berkas hanya dipakai setelah pengelompokan untuk menafsirkan hasil; pemetaan ke kategori WEEE juga dilakukan setelah kelompok terbentuk. "
        "CMRE diusulkan sebagai modifikasi proyeksi residu antarmodel: embedding model visi-bahasa diprediksi dari DINOv3, kemudian arah dominan pada bagian yang tidak terprediksi diproyeksikan keluar. "
        "SCMax memilih jumlah kelompok, Spectral clustering membentuk partisi, dan skor tetangga terdekat menandai citra yang belum terwakili. "
        "Kontribusi yang diuji ialah pengukuran bias sumber, pengurangan bias tanpa proksi, serta evaluasi lintas sumber dan kategori baru. Hasilnya dimaksudkan sebagai dasar penelitian pemilahan berbasis foto, belum sebagai sistem siap pakai."
    ),
    39: "METODOLOGI",
    40: "2.1 Data dan pemisahan peran dataset",
    41: (
        "Data utama berasal dari 3.961 citra e-waste BDC. Deduplikasi perceptual hash dengan batas jarak Hamming 6 menyisakan 3.604 citra latih unik. "
        "Sebanyak 188 citra uji penyisihan ditambahkan memakai prediksi pengklasifikasi SigLIP2 dari babak sebelumnya, tanpa label panitia, sehingga data utama berisi 3.792 citra. "
        "Sebagai pemeriksaan, seluruh pipeline dijalankan kembali hanya pada 3.604 citra latih: xsrc tetap 0,975 dan kesesuaian partisi dengan hasil utama mencapai ARI 0,93 pada citra latih. "
        "Nama berkas menyediakan label objek yang valid bagi 2.329 citra dalam sepuluh kelas. Dua entri bernama upload dikeluarkan dari evaluasi kelas, sedangkan 1.461 citra tidak memiliki label nama berkas. Label tidak dipakai untuk ekstraksi fitur, pemilihan K, atau pembentukan cluster."
    ),
    42: (
        "Tujuh set data publik tambahan memiliki peran evaluasi yang berbeda (Tabel 2). Citra eksternal diproyeksikan ke kelompok yang telah dibentuk dari data utama; tidak ada pelatihan ulang atau pengelompokan ulang. "
        "Duplikat terhadap BDC dibuang dengan perceptual hash. Audit menemukan 55% citra Kaan beririsan dengan BDC sebelum pembersihan, sehingga langkah ini diperlukan untuk mencegah kebocoran evaluasi. "
        "Protokol serta pemetaan kelas Iliev dan Shubha ditetapkan sebelum data diunduh. Sebaliknya, xsrc BDC dipakai untuk membandingkan lebih dari 40 varian metode; nilainya harus dibaca sebagai hasil pengembangan, bukan estimasi generalisasi independen. "
        "Office-Home digunakan hanya untuk pengujian sesuai lisensi riset nonkomersial."
    ),
    46: (
        "Pemeriksaan awal memperlihatkan perbedaan antarsumber yang besar. Sebanyak 66% citra BDC berukuran paling tinggi 200 piksel, dan citra produk Kaan juga banyak berupa gambar kecil berlatar putih. "
        "Foto objek Bangladesh umumnya sekitar 640 piksel dengan latar beragam, sedangkan foto lapangan GIZ mendekati 1.000 piksel. "
        "Perbedaan resolusi dan latar pada objek yang sama menjadi alasan untuk menguji konsistensi lintas sumber, bukan hanya kemurnian kelompok pada BDC."
    ),
    51: "2.2 Landasan metode",
    52: (
        "SigLIP2 dan Perception Encoder memakai pelatihan visi-bahasa yang menghubungkan citra dengan teks, sebagaimana dijelaskan oleh Tschannen et al. (2025) dan Bolya et al. (2025). "
        "DINOv3 mempelajari representasi visual tanpa pasangan teks (Siméoni et al., 2025). "
        "Penelitian ini menggunakan encoder citra yang dibekukan. Perbedaan tujuan prapelatihan menjadi alasan membandingkan representasi tunggal dan fusi; hasil pada tugas lain tidak dianggap sebagai bukti ketahanan terhadap sumber foto."
    ),
    53: (
        "Ciri resolusi, latar, atau pencahayaan dapat menjadi jalan pintas bagi model ketika berkorelasi dengan kelas pada data latih (Geirhos et al., 2020). "
        "HEX memakai statistik tekstur GLCM sebagai representasi pembantu lalu memproyeksikan fitur menjauhi subruangnya (Wang et al., 2019). UMFC memperkirakan bias domain dari fitur visual dan transisi domain teks tanpa label kategori (Liang et al., 2024). "
        "Ravfogel et al. (2020) memakai probe berulang untuk atribut yang ditentukan melalui INLP. Belrose et al. (2023) menghapus konsep target secara linear melalui LEACE. "
        "CMRE mengubah dasar pemilihan arah: residu prediksi embedding visi-bahasa dari acuan DINOv3 dihitung pada citra utama, lalu arah PCA residu yang dominan diproyeksikan keluar. Prosedur ini tidak membutuhkan label gaya atau statistik tekstur yang dirancang di muka; residu tidak dijamin hanya memuat gaya foto."
    ),
    54: (
        "Spectral clustering mempartisi graf tetangga terdekat melalui vektor eigen Laplacian (Ng et al., 2002). "
        "SCMax aslinya menggabungkan clustering hierarkis dengan skor konsensus tetangga untuk memilih jumlah kelompok (Zhang et al., 2026). "
        "Penelitian ini memakai keluaran K dari SCMax, lalu membentuk partisi akhir secara terpisah dengan Spectral clustering; hierarki SCMax bukan taksonomi keluaran penelitian. "
        "Untuk citra baru, jarak ke tetangga terdekat pada data utama dipakai sebagai skor deteksi di luar distribusi (Sun et al., 2022)."
    ),
    55: "2.3 Rancangan metode",
    56: (
        "Alur penelitian terdiri atas deduplikasi dan ekstraksi embedding, pengurangan arah residu dengan CMRE, fusi fitur, pemilihan K oleh SCMax, partisi Spectral, serta evaluasi kelompok dan deteksi kategori baru. "
        "Semua keputusan pembentukan kelompok memakai citra dan embedding data utama; label objek baru dibuka pada tahap evaluasi."
    ),
    61: (
        "Citra dideduplikasi, diubah ukurannya sesuai model, lalu diproses dalam orientasi asli dan horizontal flip; kedua embedding dirata-rata. "
        "SigLIP2-So400m dan PE-Core-G dipilih sebagai model visi-bahasa, sedangkan DINOv3-H+ menjadi acuan visual tanpa supervisi bahasa. "
        "Pada setiap model visi-bahasa, regresi ridge memprediksi embedding V dari embedding DINOv3 S. Residu R menampung bagian V yang tidak terprediksi (Persamaan 1). "
        "PCA pada R menghasilkan arah dominan U_r (Persamaan 2), lalu proyeksi pada Persamaan 3 mengeluarkan arah itu dari V. "
        "Arah residu tidak diasumsikan seluruhnya sebagai gaya foto; sebagian informasi objek mungkin ikut terbuang. Karena itu, pengaruh CMRE dinilai dengan metrik objek dan lintas sumber."
    ),
    65: (
        "Banyaknya arah yang dihapus ditentukan tanpa label dari 50% varians residu, dengan batas 64 komponen; pada data ini r mencapai batas tersebut. Parameter ridge memakai nilai baku α = 1. "
        "DINOv3-H+ dipilih sebagai acuan karena prediksi silang embedding VLM-nya tinggi di antara model SSL yang dapat dijalankan: R² ridge 0,403, dibanding 0,434 pada DINOv3-7B yang memerlukan GPU A100. "
        "Kedua embedding visi-bahasa hasil CMRE digabung dengan DINOv3, direduksi menjadi 32 dimensi melalui PCA, kemudian dinormalisasi (Persamaan 4). "
        "Istilah erasure dalam CMRE merujuk pada proyeksi arah residu, bukan klaim bahwa identitas sumber telah hilang dari embedding."
    ),
    67: (
        "SCMax mula-mula dijalankan pada embedding hasil fusi dengan sembilan seed; median K = 16 ditetapkan untuk partisi akhir. Setelah pilihan itu dibekukan, SCMax diulang dengan seed 0–99 pada data dan embedding yang sama sebagai audit kestabilan pemilihan K. Setiap K pilihan dievaluasi dengan Spectral clustering dan proyeksi citra eksternal yang sama; audit ini tidak mengulang ekstraksi fitur atau bootstrap data. "
        "Spectral clustering membentuk partisi pada graf 15 tetangga terdekat. Nama kelompok dan hubungannya dengan kategori WEEE ditentukan setelah partisi dibekukan melalui pemeriksaan citra. "
        "Sebagai analisis hierarki tambahan, centroid dari 16 kelompok akhir digabung secara agglomerative dengan average linkage dan jarak kosinus; prosedur ini tidak mengubah partisi Spectral maupun pemilihan K oleh SCMax. "
        "Untuk citra baru, pusat kelompok terdekat memberi penempatan awal. Skor OOD dihitung dari jarak ke tetangga ke-10 pada data utama dan dibandingkan dengan persentil ke-95 skor data utama (Persamaan 5). "
        "Ekstraksi fitur dijalankan pada GPU cloud dan tahap clustering pada CPU."
    ),
    69: "2.4 Protokol dan metrik evaluasi",
    70: (
        "Eksperimen disusun mengikuti empat pertanyaan penelitian. Representasi tunggal dibandingkan untuk mengukur bias sumber; fusi mentah, INLP, LEACE, dan CMRE menguji pengurangan bias; beberapa algoritma clustering membandingkan partisi pada fitur yang sama; Iliev, Shubha, dan Office-Home menguji transfer setelah pipeline dibekukan. "
        "K-Means, Ward, GMM, TEMI, TURTLE, dan protokol DECMCV dipakai sebagai pembanding sesuai peran masing-masing. Perbandingan metode pada K tetap memakai reduksi PCA-32 dan K = 16; audit SCMax memakai K pilihan tiap seed. "
        "Sapuan parameter r, K, dan jumlah tetangga dilaporkan sebagai sensitivitas; metrik pada data pengembangan tidak dipakai untuk mengklaim validasi independen."
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
        "Dalam perbandingan representasi tunggal dengan protokol seragam, SigLIP2 dan CLIP hanya menempatkan sekitar 37% foto objek Bangladesh ke kelompok acuan citra produk Kaan dari kelas yang sama. DINOv3-H+ mencapai 0,86. "
        "Pada pasangan model lain yang data pelatihannya sejenis, MetaCLIP berbasis pasangan citra-teks menghasilkan xsrc 0,20, sedangkan Web-DINO tanpa pasangan teks mencapai 0,70. Kedua encoder dideskripsikan oleh Xu et al. (2024) dan Fan et al. (2025). "
        "Perbedaan ini konsisten dengan dugaan bahwa supervisi bahasa dapat memperkuat ciri jenis foto. Namun arsitektur dan data pelatihan kedua model tidak sepenuhnya identik, sehingga hasil tersebut belum mengisolasi pengaruh supervisi bahasa."
    ),
    80: (
        "Kesesuaian terhadap label BDC pada audit awal belum menangkap persoalan ini: NMI objek fusi mentah mencapai 0,948 pada penghitungan awal, tetapi xsrc hanya 0,524. "
        "Nilai NMI tersebut memakai 2.331 entri nama berkas sebelum dua entri upload dipisahkan dari sepuluh kelas objek; karena itu angka tersebut digunakan hanya sebagai diagnostik awal. "
        "Perbedaan hasil dalam dan lintas sumber menunjukkan perlunya pengujian transfer, bukan hanya kesesuaian terhadap label BDC."
    ),
    85: "3.2 Pengaruh CMRE terhadap konsistensi lintas sumber",
    86: (
        "Pada partisi K = 16, CMRE menaikkan xsrc fusi dari 0,524 menjadi 0,975. NMI objek pada data eksternal naik dari 0,789 menjadi 0,859, dan seluruh citra tetap diberi kelompok (Tabel 4). "
        "AMI partisi akhir pada sepuluh label objek BDC mencapai 0,917. Rerata xsrc tidak menutupi variasi kelas: baterai mencapai 0,920, keyboard dan mouse 1,000, ponsel 0,981, serta PCB 0,977. "
        "INLP dengan proksi gaya mencapai xsrc yang sama; uji ini belum dapat membedakan kinerja keduanya atau membuktikan kesetaraan. LEACE dengan proksi mencapai 0,792. "
        "Pada embedding CMRE yang sama, TURTLE menghasilkan 0,790, TEMI 0,590, dan protokol DECMCV 0,910 dengan cakupan 81% citra; perbedaan cakupan perlu diperhatikan ketika membandingkan skor. "
        "Uji bootstrap berpasangan 2.000 kali menunjukkan selisih positif terhadap fusi mentah dan DINOv3 saja pada BDC, Iliev, dan Shubha (p < 0,001). Interval selisih terhadap INLP memuat nol. "
        "Manfaat praktis CMRE pada pengujian ini ialah tidak perlunya mendefinisikan proksi gaya foto sebelum proyeksi."
    ),
    88: "Tabel 4. Perbandingan metode pada K = 16 di data pengembangan",
    89: (
        "xsrc adalah rerata makro lima kelas Kaan-Bangladesh; NMI objek eksternal memakai 1.869 citra dari lima kelas bersama pada Kaan, Bangladesh, dan Karan. "
        "Cakupan menunjukkan bagian citra yang tetap diberi kelompok; n.d. berarti NMI belum dihitung dalam arsip pembanding, bukan bernilai nol. "
        "Metode bertanda † dijalankan pada embedding CMRE yang sama dengan K = 16 dan rerata tiga seed. DECMCV membuang citra yang tidak disepakati, sehingga xsrc-nya perlu dibaca bersama cakupan 81%."
    ),
    91: (
        "Probe linear membantu membaca perubahan pada embedding, tanpa menjadi bukti tunggal mekanismenya. Ketika probe dilatih pada citra produk Kaan dan diuji pada foto objek Bangladesh, akurasi objek naik dari 0,944 menjadi 0,983 setelah CMRE. "
        "Arah yang dihapus berkorelasi dengan resolusi (|ρ| hingga 0,68) dan proporsi latar putih (0,39). Namun probe sumber tetap mencapai 0,96-0,99; informasi sumber masih ada, hanya pengaruhnya terhadap kelompok yang berkurang. "
        "Acuan berlabel ConvNeXt V2 justru menurunkan xsrc menjadi 0,384. Pada sembilan pasangan model, manfaat CMRE berasosiasi dengan besarnya jejak gaya awal (Spearman 0,78), sedangkan model yang sejak awal tahan bias tidak selalu terbantu."
    ),
    92: (
        "Pada Iliev, yang pemetaan kelas dan metriknya dikunci sebelum data diunduh, xsrc eksternal mencapai 0,885 dengan interval kepercayaan 95% sebesar 0,864-0,908; fusi mentah mencapai 0,803 dan DINOv3 saja 0,755. Purity pada set ini 0,939. "
        "Iliev kemudian dipakai memilih skor OOD, sehingga statusnya sebagai set terkunci berlaku untuk evaluasi clustering, bukan untuk OOD. "
        "Pada Shubha, set konfirmasi awal berisi 300 crop, xsrc naik dari 0,356 pada fusi mentah menjadi 0,956 (interval 0,924-0,983) setelah CMRE. "
        "Office-Home memberi kondisi pembanding: fusi mentah sudah memiliki xsrc 0,865 dan CMRE menghasilkan 0,864, sementara silhouette naik dari 0,39 menjadi 0,48. "
        "Dengan demikian, peningkatan terbesar muncul ketika bias sumber awal memang kuat; hasil Office-Home tidak mendukung klaim bahwa CMRE selalu memperbaiki transfer."
    ),
    97: "3.3 Pemilihan jumlah kelompok dan sensitivitas parameter",
    98: (
        "Audit 100 seed SCMax menghasilkan median K = 16 dan modus 17. Frekuensinya: K = 13 (2 seed), 14 (10), 15 (20), 16 (20), 17 (21), 18 (14), 19 (10), 20 (2), dan 21 (1). Partisi final tetap memakai K = 16 yang telah dipilih dari sembilan seed awal; audit tambahan ini tidak dipakai memilih ulang K. "
        "Ketika Spectral mengikuti K pilihan masing-masing seed, xsrc mencapai 0,923 ± 0,098 (rerata ± simpangan baku; median 0,975; rentang 0,596–0,988), sedangkan NMI objek eksternal 0,854 ± 0,022. ARI antarpasangan 100 partisi rerata 0,861 ± 0,110. Pada 27 seed yang memilih K sedikitnya 18, xsrc hanya 0,596–0,794; pada K = 13–17 nilainya 0,972–0,988. Sebaran antar-seed ini menunjukkan ketidakpastian algoritmik pada data tetap, bukan interval kepercayaan generalisasi. "
        "Partisi Spectral pada K yang berbeda dijalankan secara terpisah, sehingga kemiripan K = 13 dan K = 16 tidak boleh disebut hierarki bersarang. "
        "Hierarki tambahan dibangun sesudah partisi K = 16 melalui penggabungan centroid. Empat penggabungan awal ialah dua jenis mesin cuci, dua baterai perangkat, dua pemutar audio, lalu dua televisi. Keempat cabang pulih pada 200 dari 200 bootstrap yang mempertahankan anggota tiap cluster; uji ini belum menilai kestabilan jika SCMax dan Spectral dijalankan ulang."
    ),
    99: (
        "Uji sensitivitas menunjukkan xsrc 0,97-0,99 untuk r = 16-64, tetapi 0,449 pada r = 4 dan 0,821 pada r = 128. Nilai α dari 0,01 sampai 1 memberi xsrc 0,975-0,983, lalu menurun pada α yang lebih besar. "
        "Pada K = 16, Spectral menghasilkan xsrc 0,975, dibanding K-Means 0,949, GMM 0,926, dan Ward 0,836. K-Means justru memiliki silhouette sedikit lebih tinggi (0,398 dibanding 0,364), kembali menunjukkan keterbatasan indeks internal untuk bias sumber. "
        "Pada graf Spectral dengan 15-30 tetangga, xsrc berada pada 0,975-0,988; pemakaian 5-10 tetangga menurunkannya ke sekitar 0,91. "
        "Dengan K dibekukan pada 16, empat seed tambahan Spectral menghasilkan ARI 1,00 terhadap partisi final; angka itu tidak mencakup variasi K dari SCMax. Sebelas dari 16 kelompok mencapai Jaccard bootstrap sedikitnya 0,85."
    ),
    104: "3.4 Penafsiran kelompok dan batas taksonomi",
    105: (
        "Tabel 5 memuat isi dominan, jumlah citra, kestabilan, dan penafsiran penanganan untuk keenam belas kelompok. "
        "Nama kelompok berasal dari pemeriksaan citra setelah partisi selesai; nama tersebut tidak menjadi target model. "
        "Pemetaan WEEE dan B3 digunakan untuk membaca kegunaan kelompok, bukan sebagai label pelatihan."
    ),
    113: (
        "Empat pasangan pertama pada hierarki centroid mempunyai hubungan visual yang mudah dibaca: mesin cuci bukaan atas dan depan, baterai laptop dan baterai kecil, dua jenis pemutar audio, serta TV CRT dan layar datar. "
        "Pada potongan 12 kelompok, penggabungan pasangan tersebut mempertahankan purity BDC 0,993 pada 2.329 citra berlabel dan xsrc 0,975. Pada potongan delapan kelompok, purity turun menjadi 0,796 karena kategori berbeda mulai bergabung. "
        "Ini mendukung penggunaan hierarki dangkal sebagai ringkasan, bukan klaim bahwa seluruh pohon mencerminkan taksonomi penanganan. "
        "Kelompok C9 didominasi laptop meskipun nama berkas BDC mengaitkannya dengan keyboard; 96,7% foto laptop Iliev masuk ke kelompok itu. "
        "Pada citra Iliev yang dikenali, kesesuaian kelompok dengan kategori EU-6 mencapai 79%, dibanding 19% pada 100.000 penggabungan acak dengan ukuran grup sama (p < 0,001). "
        "Namun jarak antarpusat kelompok dalam satu kategori WEEE tidak lebih kecil dari acak (p = 0,46). Kategori WEEE karena itu lebih tepat diperlakukan sebagai lapisan interpretasi setelah clustering."
    ),
    114: (
        "Kesalahan lintas sumber tetap ada. Dari 449 foto objek Bangladesh pada lima kelas bersama, 12 tidak masuk kelompok mayoritas citra produk Kaan: tujuh baterai masuk kelompok aki, tiga PCB masuk baterai ponsel, dan dua ponsel masuk baterai. "
        "Beberapa stop kontak juga masuk C0, kemungkinan karena bentuk kotak dan terminal logamnya. Foto tumpukan campuran banyak terkumpul pada C15 bersama papan sirkuit. "
        "Kelompok aki, CRT, dan baterai kecil memiliki Jaccard bootstrap 0,71-0,82, lebih rendah daripada kelompok lain. Dengan demikian, kemurnian agregat yang tinggi tidak menghapus kebutuhan meninjau kelompok yang kecil dan bentuk objek yang saling menyerupai."
    ),
    115: "3.5 Deteksi perangkat di luar kategori",
    116: (
        "Jarak ke tetangga terdekat menghasilkan AUROC OOD 0,937 pada Iliev, dibanding 0,868 untuk jarak ke pusat kelompok. Iliev dipakai memilih skor ini, sehingga angka tersebut merupakan hasil pengembangan OOD. "
        "Pada Shubha, AUROC mencapai 0,994 dengan interval kepercayaan 95% sebesar 0,984-0,999, tetapi hanya dua kelas di luar kategori yang tersedia. "
        "Ambang persentil ke-95 menandai 94% foto lampu Bangladesh yang tidak terwakili pada BDC, sekaligus keliru menandai 13% foto objek Bangladesh dari kelas dikenal. "
        "Di Iliev, AC ditandai pada 97% foto, kulkas 83%, serta setrika, kipas angin, lampu LED, dan dispenser air masing-masing 100%; pemutar MP3 portabel juga sering ditandai karena kelas pemutar BDC didominasi perangkat yang lebih besar."
    ),
    117: (
        "Sebanyak 44,5% foto lapangan GIZ melewati ambang OOD. Di antara foto yang ditandai, banyak terdapat AC, kulkas, dan kompresor, jenis perangkat yang tidak terdapat dalam kelompok utama BDC. "
        "Temuan ini menunjukkan fungsi praktis alarm kategori baru, tetapi proporsi yang ditandai sendiri bukan ukuran akurasi karena tidak semua foto GIZ memiliki padanan label yang lengkap. "
        "Foto yang ditandai perlu diperiksa petugas sebelum diberi arahan penanganan."
    ),
    122: "3.6 Hubungan dengan studi terdahulu dan penggunaan di Indonesia",
    123: (
        "DECMCV telah melaporkan bahwa perbedaan gaya foto mengganggu pengelompokan sampah (Huang et al., 2025). Penelitian ini menambahkan ukuran konsistensi lintas sumber dan menguji proyeksi residu sebagai cara mengurangi gangguan tersebut tanpa membuang citra. "
        "Dibanding studi klasifikasi terawasi seperti Islam et al. (2023), persoalan yang ditangani berbeda: kategori belum ditetapkan saat pembentukan kelompok. Karena itu, akurasi klasifikasi pada satu dataset tidak dapat dibandingkan langsung dengan xsrc penelitian ini. "
        "Pemisahan subtipe perangkat konsisten dengan pengamatan Zhou et al. (2025) tentang kegunaan tipe produk dalam pembongkaran, tetapi relevansi operasional tiap kelompok masih memerlukan penilaian ahli pengelolaan e-waste."
    ),
    124: (
        "Dalam konteks Indonesia, hasil ini dapat menjadi bahan awal bagi alat bantu triase foto di bank sampah atau tempat pengumpulan. Sistem semacam itu perlu menampilkan kelompok yang diperkirakan, skor ketidakpastian, serta pilihan pemeriksaan manual untuk foto yang ditandai OOD. "
        "Versi cepat dengan SigLIP2 dan DINOv3 memproses sekitar 20 citra per detik pada GPU L4, dibanding 3,4 citra per detik untuk pipeline penuh; xsrc-nya 0,951 pada BDC, 0,860 pada Iliev, dan 0,922 pada Shubha. "
        "Angka ini menunjukkan pilihan biaya komputasi dan kinerja, bukan pengukuran pada ponsel. Uji pada foto rumah tangga Indonesia dan pemeriksaan jalur penanganan oleh petugas tetap diperlukan sebelum penerapan."
    ),
    126: (
        "Batas utama penelitian terletak pada protokol data. BDC digunakan berulang kali untuk memilih varian, sehingga xsrc 0,975 bersifat optimistis. Iliev memberi uji clustering terkunci, sedangkan Shubha baru mencakup 300 crop. Belum ada foto yang diambil langsung dari rumah tangga atau bank sampah di Indonesia. "
        "Dari sisi metode, selisih CMRE terhadap INLP belum signifikan pada metrik utama, dan manfaat CMRE bergantung pada kekuatan model SSL acuan; dengan DINOv3-B, xsrc hanya 0,593. Informasi sumber masih terbaca oleh probe. Pada audit 100 seed, SCMax memilih K antara 13 dan 21; 27 seed dengan K sedikitnya 18 menghasilkan xsrc paling tinggi 0,794. Audit itu mengulang seed pada embedding tetap, bukan ekstraksi dan pemilihan model penuh. Bootstrap hierarki belum mencakup pelatihan ulang pipeline. "
        "Selisih kecil antara xsrc v4 tersimpan dan hitung ulang belum diisolasi penyebab teknisnya. "
        "Deteksi OOD memakai satu ambang global yang menandai 13% foto objek Bangladesh dari kelas dikenal. Hasil eksternal juga dipengaruhi kesesuaian definisi kelas: pemutar MP3 dan TV Iliev tidak selalu sepadan dengan kelompok BDC."
    ),
    128: "PENUTUP",
    129: (
        "Representasi visual pada data ini memang peka terhadap sumber foto: SigLIP2 dan CLIP memberi xsrc sekitar 0,37, sedangkan DINOv3-H+ mencapai 0,86 pada audit awal. "
        "CMRE menaikkan xsrc fusi dari 0,524 menjadi 0,975; AMI partisi akhir pada sepuluh kelas BDC adalah 0,917. Perbaikan xsrc juga tampak pada Iliev (0,803 menjadi 0,885) dan Shubha (0,356 menjadi 0,956), sementara Office-Home menunjukkan kondisi tanpa perbaikan. "
        "Median sembilan seed awal SCMax memilih K = 16. Audit 100 seed memberi median yang sama, tetapi partisi antar-seed hanya mencapai rerata ARI 0,861; kestabilan jumlah kelompok masih menjadi batas metode. Kelompok akhir memisahkan beberapa subtipe perangkat; hierarki centroid pascacluster berguna sampai penggabungan awal, sedangkan cabang atas tidak selalu sejalan dengan kategori penanganan. "
        "Deteksi OOD kNN mencapai AUROC 0,994 pada Shubha dengan dua kelas baru dan tetap menghasilkan alarm palsu pada 13% foto Bangladesh dari kelas dikenal. "
        "Dengan bukti saat ini, pipeline merupakan dasar eksplorasi kategori dan triase foto, belum pengganti penilaian petugas pada konteks Indonesia."
    ),
    130: (
        "Pengujian berikutnya perlu mengumpulkan foto langsung dari rumah tangga dan bank sampah Indonesia, terutama perangkat penukar suhu dan foto tumpukan yang kurang terwakili. "
        "Pemetaan kategori harus dikunci sebelum data tersebut dinilai agar estimasi transfer tidak kembali menjadi hasil pengembangan. "
        "Ablasi yang memisahkan efek regresi, proyeksi residu, dan model acuan diperlukan untuk menjelaskan kontribusi CMRE. "
        "Variasi K dapat diuji dengan mengulangi seluruh pipeline pada sampel baru, bukan hanya bootstrap centroid; ambang OOD per kelompok juga perlu dikalibrasi pada set pengembangan terpisah. "
        "Untuk pemakaian pada perangkat terbatas, versi cepat SigLIP2 dan DINOv3 dapat menjadi titik awal distilasi serta pengukuran latensi yang sesungguhnya."
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
        "ambang varians, tetapi PCA hanya menghitung 64 komponen. Dengan demikian, 64 arah "
        "yang benar-benar diproyeksikan. Audit ini belum mengukur variasi dari ekstraksi "
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
