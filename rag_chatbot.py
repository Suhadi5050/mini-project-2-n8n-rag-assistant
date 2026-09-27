import os
import glob

from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.documents import Document
from langchain_pymupdf4llm import PyMuPDF4LLMLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma


# ============================================================
# 1. KONFIGURASI
# ============================================================

CHAT_MODEL = "openai/gpt-oss-120b"
COLLECTION_NAME = "panduan_komprehensif_n8n"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
TOP_K = 3

KNOWLEDGE_DIR = "./knowledge_docs"
SYSTEM_PROMPT_PATH = "./system_prompt.md"


# ============================================================
# 2. SETUP MODEL
# ============================================================

def buat_model() -> ChatGroq:
    """Siapkan koneksi ke model chat lewat Groq."""
    return ChatGroq(
        model=CHAT_MODEL,
        temperature=0,
        reasoning_effort="low",
    )


# ============================================================
# 3. DATA INGESTION (Load -> Split -> Embed -> Store)
# ============================================================

def muat_dokumen(folder: str) -> list[Document]:
    """
    Load semua file .pdf di dalam folder menjadi list of Document 
    menggunakan PyMuPDF4LLMLoader.
    """
    daftar_dokumen = []
    path_file = sorted(glob.glob(os.path.join(folder, "*.pdf")))

    if not path_file:
        raise FileNotFoundError(
            f"Tidak ada file .pdf ditemukan di folder '{folder}'. "
            "Pastikan folder knowledge_docs/ berisi file sumber."
        )

    for path in path_file:
        loader = PyMuPDF4LLMLoader(file_path=path, mode="single", use_layout=False)
        daftar_dokumen.extend(loader.load())

    return daftar_dokumen


def bangun_vectorstore(dokumen: list) -> Chroma:
    """Ubah kumpulan Document menjadi vector store ChromaDB."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    potongan = splitter.split_documents(dokumen)

    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
    )
    vectorstore.reset_collection()
    vectorstore.add_documents(potongan)

    return vectorstore


# ============================================================
# 4. RAG CHAIN & SAPAAN
# ============================================================

kata_sapaan = {
    "halo", "haloo", "hallo", "halloo", "hai", "hay", "hey", "hi",
    "p", "hei", "hello", "selamat pagi", "selamat siang",
    "selamat sore", "selamat malam", "pagi", "siang", "sore", "malam",
    "assalamualaikum", "assalamu'alaikum", "assalamualaikum wr wb",
    "apa kabar", "halo min", "hai min", "permisi", "bang", "kak",
    "min", "bot", "halo bot",
}

respon_sapaan = (
    "Halo! 👋 Ada yang bisa saya bantu seputar n8n hari ini? "
    "Kamu bisa tanya soal arsitektur workflow, trigger, expressions, "
    "deployment, dan masih banyak lagi!"
)


def adalah_sapaan(teks: str) -> bool:
    """Cek apakah input user merupakan sapaan/salam biasa."""
    bersih = teks.lower().strip().rstrip("!?.,")
    return bersih in kata_sapaan


def format_docs(daftar_dokumen: list[Document]) -> str:
    """Gabungkan beberapa chunk hasil retrieval menjadi satu teks konteks."""
    return "\n\n".join(dok.page_content for dok in daftar_dokumen)


def muat_system_prompt(path: str) -> str:
    """Baca system prompt dari file .md terpisah."""
    with open(path, encoding="utf-8") as f:
        return f.read()


def buat_rag_chain(retriever, model: ChatGroq, system_prompt: str):
    """Satukan retriever, prompt, model, dan parser menjadi satu chain LCEL."""
    rag_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Konteks:\n{context}\n\nPertanyaan: {question}"),
    ])

    rag_chain = (
        RunnableParallel(
            context=retriever | format_docs,
            question=RunnablePassthrough(),
        )
        | rag_prompt
        | model
        | StrOutputParser()
    )
    return rag_chain


# ============================================================
# 5. PROGRAM UTAMA
# ============================================================

def main():
    load_dotenv()
    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError(
            "GROQ_API_KEY tidak ditemukan. Pastikan file .env ada di folder "
            "yang sama dengan script ini dan berisi GROQ_API_KEY=..."
        )

    print("Menyiapkan model...")
    model = buat_model()

    print(f"Memuat dokumen dari folder '{KNOWLEDGE_DIR}'...")
    dokumen = muat_dokumen(KNOWLEDGE_DIR)
    print(f"  -> {len(dokumen)} dokumen berhasil dimuat.")

    print("Membangun vector store dari dokumen...")
    vectorstore = bangun_vectorstore(dokumen)
    retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})

    print(f"Memuat system prompt dari '{SYSTEM_PROMPT_PATH}'...")
    system_prompt = muat_system_prompt(SYSTEM_PROMPT_PATH)
    
    print("Merakit RAG chain...")
    rag_chain = buat_rag_chain(retriever, model, system_prompt)

    print("\nRAG chatbot siap. Ketik pertanyaan, atau 'keluar' untuk berhenti.\n")

    while True:
        pertanyaan = input("Pertanyaan: ").strip()
        if pertanyaan.lower() in {"keluar", "exit", "quit"}:
            print("Sampai jumpa.")
            break
        if not pertanyaan:
            continue

        jawaban = rag_chain.invoke(pertanyaan)
        print(f"Jawaban : {jawaban}\n")


if __name__ == "__main__":
    main()