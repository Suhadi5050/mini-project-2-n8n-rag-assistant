# Panduan Komprehensif n8n: Otomatisasi Workflow & AI RAG Assistant

Repositori ini berisi sekumpulan berkas yang dirancang untuk membangun aplikasi asisten cerdas berbasis Retrieval-Augmented Generation (RAG). Sistem ini memanfaatkan dokumen panduan teknis n8n sebagai basis pengetahuan agar AI dapat menjawab pertanyaan secara akurat dan sesuai dengan dokumentasi aslinya.

## Daftar Isi Berkas & Penjelasan Teknis

Berikut adalah rincian berkas-berkas di dalam repositori ini beserta penjelasan mendalam mengenai peran dan dokumentasi kodenya masing-masing:

### 1. `app.py` (Aplikasi Antarmuka Web Streamlit)
Berkas utama aplikasi web yang menggunakan framework Streamlit untuk mengatur antarmuka pengguna, pengaturan tema dinamis, sidebar interaktif, serta alur percabangan chat.
* **Docstring & Modul Utama**: Menangani konfigurasi halaman, state management (tema, font, riwayat sesi), dan CSS kustom dinamis berdasarkan preferensi pengguna.
* **Fungsi Utama (`siapkan_chatbot`)**: Menginisialisasi model, memuat dokumen knowledge base, membangun vector store, dan merakit *RAG chain*. Fungsi ini menggunakan dekorator `@st.cache_resource` agar proses berat hanya berjalan sekali di awal server menyala.
* **Fungsi `perlambat_stream`**: Mengatur jeda kemunculan potongan teks (*chunks*) dari stream LLM agar efek ketikan di antarmuka terasa lebih natural.

### 2. `rag_chatbot.py` (Skrip Inti RAG & Logika Backend)
Skrip backend yang menangani logika pemrosesan dokumen, pembuatan vector database (Chroma), konfigurasi model bahasa (Groq/HuggingFace), dan mekanisme pencarian berbasis RAG.
* **Docstring & Modul Utama**: Berbasis LangChain + Groq + ChromaDB lokal. Terbagi ke dalam blok model, prompt template, output parser, LCEL (`RunnableParallel`, `RunnablePassthrough`), data ingestion, dan RAG chain.
* **Fungsi `muat_dokumen(folder: str)`**: Memuat file PDF menggunakan `PyMuPDF4LLMLoader` dengan mode `"single"` dan `use_layout=False` untuk ekstraksi teks yang konsisten.
* **Fungsi `bangun_vectorstore(dokumen: list)`**: Memecah dokumen menjadi *chunks* via `RecursiveCharacterTextSplitter` lalu menyimpannya ke ChromaDB.
* **Fungsi `adalah_sapaan(teks: str)`**: Mendeteksi sapaan/salam cepat agar dapat direspons instan tanpa memicu pencarian dokumen RAG.
* **Blok Eksekusi `if __name__ == '__main__':`**: Memastikan skrip dapat dijalankan langsung di terminal untuk pengujian CLI mandiri, atau diimpor sebagai modul oleh `app.py` tanpa mengeksekusi blok interaktif secara otomatis.

### 3. `Panduan_Komprehensif_n8n_Tutorial_Lanjutan.pdf` (Knowledge Document)
Dokumen pengetahuan utama (*knowledge doc*) bagi sistem AI. Berisi materi pembahasan komprehensif mulai dari arsitektur n8n, kontrol alur, use case industri, deployment, keamanan, performa, hingga tutorial step-by-step yang menjadi sumber acuan jawaban bagi bot.

### 4. `requirements.txt`
Daftar pustaka atau dependensi Python yang diperlukan untuk menjalankan seluruh modul, mencakup `langchain-core`, `langchain-text-splitters`, `langchain-groq`, `langchain-huggingface`, `langchain-chroma`, `langchain-pymupdf4llm`, `sentence-transformers`, `chromadb`, `python-dotenv`, dan `groq`.

### 5. `style.css`
Berkas pengaturan gaya tampilan antarmuka (CSS) untuk menyesuaikan tema visual, warna latar belakang, gelembung chat, hingga panel samping agar selaras dengan skema warna aplikasi.

### 6. `system_prompt.md`
Berkas instruksi dasar dan batasan peran (*system prompt*) bagi asisten AI agar tetap fokus menjawab seputar materi n8n secara profesional dan objektif.

---

## Gambaran Umum Materi n8n di Knowledge Base

Materi yang dibahas di dalam dokumen referensi mencakup:
1. **Pengantar & Filosofi Otomatisasi**: Alasan kebutuhan otomatisasi dan posisi n8n di ekosistem modern.
2. **Arsitektur & Model Data**: Lapisan workflow, perbedaan webhook, polling, schedule, dan pengelolaan item data.
3. **Kontrol Alur & Transformasi**: Penggunaan expressions, normalisasi data, percabangan (IF/Switch), dan idempotensi.
4. **Penerapan Industri**: Studi kasus e-commerce, laporan eksekutif, HR, keuangan, hingga AI human-in-the-loop.
5. **Deployment & Infrastruktur**: Panduan instalasi lokal, Docker, dan VPS dengan manajemen database.
6. **Keamanan & Privasi**: Prinsip *least privilege*, manajemen kredensial, keamanan webhook, dan audit sistem.
7. **Performa & Skalabilitas**: Strategi data besar, pagination, batching, queue mode, dan rate limiting.
8. **Praktik Terbaik & Troubleshooting**: Konvensi penamaan, penanganan error bertingkat, dan diagnosis jaringan.

---

## Pemilihan Model, Kinerja & Estimasi Biaya (Rubrik Penilaian)

* **LLM Provider & Model:** Menggunakan model chat berperforma tinggi melalui infrastruktur API **Groq**.
* **Kualitas & Kecepatan:** Model Groq dirancang dengan arsitektur komputasi khusus yang menghasilkan latensi sangat rendah (*lightning-fast inference*). Fitur *streaming* teks di antarmuka Streamlit berjalan secara *real-time* tanpa jeda yang mengganggu.
* **Context Window:** Kapasitas *context window* yang besar memungkinkan model menampung banyak potongan konteks dokumen teknis secara bersamaan.
* **Temperatur:** Ditetapkan pada nilai `temperature = 0` untuk memastikan kepatuhan mutlak terhadap isi dokumen acuan serta meminimalisir risiko halusinasi data teknis.
* **Estimasi Biaya Operasional:**
  * **API LLM (Groq):** Sangat ekonomis. Pada tier pengembangan dan uji coba (*Free Tier / Developer Tier*), biaya per 1 juta token input/output berkisar antara **$0.05 hingga $0.10**, atau bahkan gratis untuk batas kuota harian tertentu. Jika diasumsikan rata-rata penggunaan harian mencapai 50.000 token, estimasi biaya bulanan kurang dari **$0.50 – $1.50 per bulan**.
  * **Vector Database & Hosting:** Menggunakan penyimpanan *in-memory* berbasis ChromaDB dengan *embedder* ONNX bawaan (`all-MiniLM-L6-v2`), sehingga **biaya infrastruktur database adalah $0 (gratis)**[cite: 2]. Pendekatan ini jauh lebih ringan tanpa beban *overhead* kuota memori fisik disk maupun dependensi eksternal tambahan.

---

## Cara Menjalankan Aplikasi

Pastikan seluruh pustaka telah terpasang dengan menjalankan perintah:
```bash
pip install -r requirements.txt
```

Terdapat dua cara berbeda untuk menjalankan program di dalam repositori ini:

1. **Menjalankan Melalui Terminal (CLI Mode)**:
   Jika Anda ingin menguji logika inti RAG atau berinteraksi langsung melalui baris perintah terminal tanpa antarmuka web, jalankan skrip backend secara langsung:
   ```bash
   python rag_chatbot.py
   ```
   *Catatan teknis*: Blok `if __name__ == '__main__':` di dalam skrip akan mendeteksi eksekusi langsung ini dan memicu fungsi interaktif berbasis terminal.

2. **Menjalankan Melalui Antarmuka Web (Streamlit UI)**:
   Jika Anda ingin menggunakan aplikasi berbasis web yang interaktif, jalankan berkas utama Streamlit:
   ```bash
   streamlit run app.py
   ```
   *Catatan teknis*: Saat dijalankan melalui perintah ini, `app.py` akan mengimpor modul dari `rag_chatbot.py`. Berkat adanya struktur `if __name__ == '__main__':` di file backend, kode interaktif terminal tidak akan berjalan ganda, melainkan hanya fungsi modul RAG yang dimuat ke dalam antarmuka web Streamlit.

---

## Test Set (5 Pertanyaan Uji & Evaluasi)

Sesuai dengan kriteria evaluasi tugas, berikut adalah pengujian sistem menggunakan 5 skenario pertanyaan uji:

1. **Pertanyaan 1 (Faktual / Ada dalam Dokumen):**
   * **Input:** "Apa saja lapisan arsitektur workflow di n8n?"
   * **Expected Output:** Menjelaskan lapisan-lapisan utama (Trigger, Ingestion, Validation, Transformation, Decision, Action, Observability).
   * **Status Evaluasi:** Berhasil dijawab secara akurat bersumber dari dokumen panduan.

2. **Pertanyaan 2 (Teknis / Konfigurasi):**
   * **Input:** "Bagaimana cara kerja expressions di n8n untuk memetakan data?"
   * **Expected Output:** Menjelaskan penggunaan tanda kurung kurawal ganda dan referensi data node sebelumnya.
   * **Status Evaluasi:** Berhasil dijawab dengan contoh sintaks yang tepat sesuai dokumen.

3. **Pertanyaan 3 (Studi Kasus / Praktis):**
   * **Input:** "Apa perbedaan utama antara webhook dan polling pada trigger n8n?"
   * **Expected Output:** Menjelaskan webhook sebagai metode *event-driven* berlatensi rendah dan polling sebagai pemeriksaan berkala.
   * **Status Evaluasi:** Berhasil dijawab dengan perbandingan yang jelas.

4. **Pertanyaan 4 (Pertanyaan di Luar Ruang Lingkup / Out-of-Scope):**
   * **Input:** "Berapa resep cara membuat nasi goreng khas Nusantara?"
   * **Expected Output:** Sistem menolak menjawab karena berada di luar cakupan materi n8n dan tidak ditemukan dalam dokumen acuan.
   * **Status Evaluasi:** Berhasil memicu sistem *guardrail* (aman dari halusinasi, sistem menyatakan informasi tidak ditemukan).

5. **Pertanyaan 5 (Uji Batas / Informasi Tidak Tersedia):**
   * **Input:** "Bagaimana cara integrasi n8n dengan perangkat keras IoT berbasis Arduino ESP32?"
   * **Expected Output:** Menampilkan pesan bahwa informasi tersebut tidak ditemukan dalam dokumen panduan n8n tanpa mengarang bebas.
   * **Status Evaluasi:** Berhasil mematuhi aturan anti-halusinasi dengan baik.
