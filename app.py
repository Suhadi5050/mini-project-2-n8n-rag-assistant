import os
import time
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from rag_chatbot import (
    KNOWLEDGE_DIR,
    SYSTEM_PROMPT_PATH,
    TOP_K,
    buat_model,
    muat_dokumen,
    bangun_vectorstore,
    muat_system_prompt,
    buat_rag_chain,
    adalah_sapaan,
    respon_sapaan,
)


# ============================================================
# 1. PENGATURAN HALAMAN
# ============================================================

st.set_page_config(
    page_title="Asisten Panduan n8n",
    page_icon="🤖",
    layout="wide",
)


# ============================================================
# 2. STATE MANAGEMENT
# ============================================================

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark"

if "theme_color" not in st.session_state:
    st.session_state.theme_color = "Ungu Pastel"

if "font_size" not in st.session_state:
    st.session_state.font_size = "Sedang"

if "riwayat" not in st.session_state:
    st.session_state.riwayat = []

if "sessions" not in st.session_state:
    st.session_state.sessions = []

if "bookmarks" not in st.session_state:
    st.session_state.bookmarks = []

if "welcome_shown" not in st.session_state:
    st.session_state.welcome_shown = False


# ============================================================
# 3. KONFIGURASI WARNA, FONT & CSS
# ============================================================

COLOR_MAP = {
    "Ungu Pastel": {
        "primary": "#581C87",
        "accent": "#8B5CF6",
        "soft_bg": "#3B115B",
        "bubble_user": "#3A1E6B",
        "bubble_bot": "#1F172E",
    },
    "Hijau Botol": {
        "primary": "#064E3B",
        "accent": "#10B981",
        "soft_bg": "#0D382B",
        "bubble_user": "#0D3B2E",
        "bubble_bot": "#13221C",
    },
    "Merah Marun": {
        "primary": "#7F1D1D",
        "accent": "#EF4444",
        "soft_bg": "#5A1313",
        "bubble_user": "#581C1C",
        "bubble_bot": "#231212",
    },
    "Biru Tua": {
        "primary": "#1E3A8A",
        "accent": "#3B82F6",
        "soft_bg": "#14275E",
        "bubble_user": "#1A365D",
        "bubble_bot": "#0F172A",
    },
    "Abu Klasik": {
        "primary": "#1F2937",
        "accent": "#6B7280",
        "soft_bg": "#111827",
        "bubble_user": "#374151",
        "bubble_bot": "#111827",
    },
}

FONT_SIZE_MAP = {
    "Kecil": "13px",
    "Sedang": "15px",
    "Besar": "17px",
}

active_colors = COLOR_MAP.get(st.session_state.theme_color, COLOR_MAP["Ungu Pastel"])
active_font_size = FONT_SIZE_MAP.get(st.session_state.font_size, "15px")

app_bg = "#0E1117"
app_text = "#F0F6FC"
panel_bg = "#121A17"
muted_text = "#A8B3BF"
sidebar_bg = active_colors["soft_bg"]

dynamic_css = f"""
<style>
    :root {{
        --app-bg: {app_bg};
        --app-text: {app_text};
        --panel-bg: {panel_bg};
        --muted-text: {muted_text};
        --primary-color: {active_colors['primary']};
        --accent-color: {active_colors['accent']};
        --sidebar-bg: {sidebar_bg};
        --bubble-user: {active_colors['bubble_user']};
        --bubble-bot: {active_colors['bubble_bot']};
        --base-font-size: {active_font_size};
    }}
</style>
"""

CSS_PATH = Path(__file__).with_name("style.css")
if CSS_PATH.exists():
    dynamic_css += f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>"

st.markdown(dynamic_css, unsafe_allow_html=True)


# ============================================================
# 4. CEK API KEY
# ============================================================

load_dotenv()
if not os.getenv("GROQ_API_KEY"):
    st.error(
        "GROQ_API_KEY belum diisi. Cek file .env (di laptop) "
        "atau menu Secrets (di Streamlit Cloud)."
    )
    st.stop()


# ============================================================
# 5. INISIALISASI CHATBOT
# ============================================================

@st.cache_resource(show_spinner="Menyiapkan chatbot, mohon tunggu sebentar...")
def siapkan_chatbot():
    model = buat_model()
    dokumen = muat_dokumen(KNOWLEDGE_DIR)
    vectorstore = bangun_vectorstore(dokumen)
    retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})
    system_prompt = muat_system_prompt(SYSTEM_PROMPT_PATH)
    return buat_rag_chain(retriever, model, system_prompt)


rag_chain = siapkan_chatbot()


def perlambat_stream(stream, jeda=0.02):
    for potongan in stream:
        time.sleep(jeda)
        yield potongan


# ============================================================
# 5B. KOMPONEN TAMPILAN (HTML)
# ============================================================

def render_header_pesan(nama, waktu):
    st.markdown(
        f"<div style='font-size: 0.8rem; color: var(--muted-text); margin-bottom: 0.3rem; font-weight: 600;'>"
        f"{nama} <span style='font-weight: normal; opacity: 0.7; margin-left: 0.5rem;'>• {waktu}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )


def render_workspace_dan_status():
    st.markdown("<div style='margin-top: 3rem;'></div>", unsafe_allow_html=True)
    st.divider()

    st.markdown(
        """
        <div style="font-size: 0.85rem; color: var(--muted-text);">
            <p style="margin-bottom: 0.4rem; font-weight: bold; color: var(--app-text);">📁 Workspace</p>
            <ul style="list-style-type: none; padding-left: 0; margin: 0; line-height: 1.6;">
                <li>📚 Dokumentasi lokal</li>
                <li>🧠 Knowledge Base</li>
                <li>⚙️ Konfigurasi</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem; color: var(--muted-text);">
            <span>🟢 AI Online</span>
            <span>v1.0.0</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption("🔍 Sumber: Dokumen Panduan Lokal")


def render_welcome_header():
    st.markdown(
        """
        <div style="text-align: center; padding: 1.5rem 1rem 0.5rem 1rem; max-width: 700px; margin: 0 auto;">
            <div style="font-size: 2.8rem; margin-bottom: 0.3rem;">🤖</div>
            <h2 style="font-size: 1.8rem; margin-bottom: 0.3rem; color: var(--app-text);">👋 Selamat datang di Asisten Panduan n8n</h2>
            <p style="color: var(--muted-text); font-size: 1rem; line-height: 1.5; margin-bottom: 1rem;">
                Saya dapat membantu Anda mengeksplorasi arsitektur workflow, expressions, konfigurasi node, integrasi API, deployment, debugging, hingga best practices.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_capability_chips():
    st.markdown(
        """
        <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; margin-bottom: 1.2rem;">
            <span style="background-color: rgba(139, 92, 246, 0.15); color: var(--accent-color); padding: 5px 12px; border-radius: 20px; font-size: 0.82rem; border: 1px solid rgba(139, 92, 246, 0.3);">⚡ Workflow</span>
            <span style="background-color: rgba(139, 92, 246, 0.15); color: var(--accent-color); padding: 5px 12px; border-radius: 20px; font-size: 0.82rem; border: 1px solid rgba(139, 92, 246, 0.3);">🔧 Expressions</span>
            <span style="background-color: rgba(139, 92, 246, 0.15); color: var(--accent-color); padding: 5px 12px; border-radius: 20px; font-size: 0.82rem; border: 1px solid rgba(139, 92, 246, 0.3);">🧩 Nodes</span>
            <span style="background-color: rgba(139, 92, 246, 0.15); color: var(--accent-color); padding: 5px 12px; border-radius: 20px; font-size: 0.82rem; border: 1px solid rgba(139, 92, 246, 0.3);">🐞 Debugging</span>
            <span style="background-color: rgba(139, 92, 246, 0.15); color: var(--accent-color); padding: 5px 12px; border-radius: 20px; font-size: 0.82rem; border: 1px solid rgba(139, 92, 246, 0.3);">🚀 Deployment</span>
            <span style="background-color: rgba(139, 92, 246, 0.15); color: var(--accent-color); padding: 5px 12px; border-radius: 20px; font-size: 0.82rem; border: 1px solid rgba(139, 92, 246, 0.3);">🔌 API</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# 6. POP-UP SAMBUTAN
# ============================================================

@st.dialog("🤖 Selamat Datang di Asisten n8n!")
def show_welcome_dialog():
    st.markdown(
        """
        Halo! Senang bisa membantu Anda menguasai **n8n**, mulai dari arsitektur workflow,
        penggunaan *expressions*, integrasi node, hingga strategi *deployment* skala produksi.

        Silakan atur tema warna dan ukuran font di menu pengaturan pojok kanan atas, lalu mulai
        ketik pertanyaan Anda atau pilih topik cepat di halaman utama. 🚀
        """
    )
    if st.button("Mulai Percakapan Sekarang", use_container_width=True, type="primary"):
        st.session_state.welcome_shown = True
        st.rerun()


if not st.session_state.welcome_shown:
    show_welcome_dialog()


# ============================================================
# 7. HEADER UTAMA & PENGATURAN
# ============================================================

col_title, col_settings = st.columns([3, 1])

with col_title:
    st.markdown("# Asisten Panduan Komprehensif n8n")

with col_settings:
    with st.popover("⚙️ Pengaturan Tampilan"):
        st.markdown("### Kustomisasi Tampilan")

        st.markdown("**Tema Warna Soft**")
        new_color = st.radio(
            "Tema Warna Soft",
            list(COLOR_MAP.keys()),
            index=list(COLOR_MAP.keys()).index(st.session_state.theme_color),
            key="radio_theme_color",
            label_visibility="collapsed",
        )
        if new_color != st.session_state.theme_color:
            st.session_state.theme_color = new_color
            st.rerun()

        st.divider()

        st.markdown("**Ukuran Font Teks**")
        new_font = st.radio(
            "Ukuran Font Teks",
            list(FONT_SIZE_MAP.keys()),
            index=list(FONT_SIZE_MAP.keys()).index(st.session_state.font_size),
            key="radio_font_size",
            label_visibility="collapsed",
        )
        if new_font != st.session_state.font_size:
            st.session_state.font_size = new_font
            st.rerun()

st.caption(
    "Tanyakan apa saja seputar n8n, arsitektur workflow, expressions, "
    "deployment, dan best practices."
)


# ============================================================
# 8. SIDEBAR
# ============================================================

with st.sidebar:
    st.header("⚙️ Navigasi & Riwayat")

    if st.button("➕ Mulai Percakapan Baru", use_container_width=True):
        if st.session_state.riwayat:
            session_title = st.session_state.riwayat[0]["isi"][:30] + "..."
            st.session_state.sessions.append({
                "id": time.time(),
                "title": session_title,
                "riwayat": list(st.session_state.riwayat),
            })
        st.session_state.riwayat = []
        st.rerun()

    st.divider()

    st.subheader("📜 Riwayat Chat")
    if not st.session_state.sessions and not st.session_state.riwayat:
        st.caption("Belum ada riwayat percakapan tersimpan.")
    else:
        if st.session_state.riwayat:
            active_title = st.session_state.riwayat[0]["isi"][:30] + "..."
            st.markdown(f"**💬 [Aktif]** {active_title}")

        for idx, sess in enumerate(st.session_state.sessions[::-1]):
            col_s1, col_s2 = st.columns([4, 1])
            with col_s1:
                if st.button(
                    f"💬 {sess['title']}",
                    key=f"sess_{idx}",
                    use_container_width=True,
                ):
                    st.session_state.riwayat = sess["riwayat"]
                    st.rerun()
            with col_s2:
                if st.button("🗑️", key=f"del_sess_{idx}", help="Hapus sesi ini"):
                    real_index = len(st.session_state.sessions) - 1 - idx
                    st.session_state.sessions.pop(real_index)
                    st.rerun()

    st.divider()

    st.subheader("🔖 Bookmark Tersimpan")
    if not st.session_state.bookmarks:
        st.caption("Belum ada pesan yang di-bookmark.")
    else:
        for b_idx, bm in enumerate(st.session_state.bookmarks):
            with st.expander(f"Pesan #{b_idx + 1} ({bm['role']})"):
                st.write(bm["isi"])
                if st.button("Hapus", key=f"del_bm_{b_idx}"):
                    st.session_state.bookmarks.pop(b_idx)
                    st.rerun()

    st.divider()

    if st.session_state.riwayat:
        export_text = "\n\n".join(
            [f"**{p['role'].upper()}**: {p['isi']}" for p in st.session_state.riwayat]
        )
        st.download_button(
            label="📥 Ekspor Riwayat (.md)",
            data=export_text,
            file_name="riwayat_n8n_chat.md",
            mime="text/markdown",
            use_container_width=True,
        )

    render_workspace_dan_status()


# ============================================================
# 9. TAMPILAN UTAMA & CHAT
# ============================================================

selected_prompt = None

if not st.session_state.riwayat:
    render_welcome_header()
    render_capability_chips()

    st.markdown(
        "<p style='text-align: center; font-weight: 600; font-size: 0.95rem; "
        "color: var(--app-text); margin-bottom: 0.5rem;'>"
        "💡 Pilih Topik Pertanyaan Cepat:</p>",
        unsafe_allow_html=True,
    )

    col_q1, col_q2 = st.columns(2)
    with col_q1:
        if st.button(
            "⚡ Apa saja 7 lapisan arsitektur workflow di n8n?",
            use_container_width=True,
        ):
            selected_prompt = "Apa saja 7 lapisan arsitektur workflow di n8n?"
        if st.button(
            "🔧 Bagaimana cara kerja expressions & transformasi data?",
            use_container_width=True,
        ):
            selected_prompt = "Bagaimana cara kerja expressions & transformasi data di n8n?"
    with col_q2:
        if st.button(
            "🚀 Bagaimana rekomendasi deployment untuk produksi?",
            use_container_width=True,
        ):
            selected_prompt = "Bagaimana rekomendasi deployment n8n untuk skala produksi?"
        if st.button(
            "🛠️ Tips debugging & mengatasi error pada node",
            use_container_width=True,
        ):
            selected_prompt = "Bagaimana tips debugging dan cara mengatasi error pada node n8n?"
    st.divider()

for idx, pesan in enumerate(st.session_state.riwayat):
    role = pesan["role"]
    waktu = pesan.get("waktu", datetime.now().strftime("%H:%M"))

    if role == "user":
        avatar = "👤"
        nama_pengirim = "Anda"
    else:
        avatar = "🤖"
        nama_pengirim = "Asisten n8n AI"

    with st.chat_message(role, avatar=avatar):
        render_header_pesan(nama_pengirim, waktu)
        st.markdown(pesan["isi"])

        if role == "assistant":
            st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
            col_a1, col_a2, col_a3 = st.columns([1, 1, 2])

            with col_a1:
                if st.button(
                    "🔖 Simpan",
                    key=f"bm_{idx}",
                    help="Bookmark pesan ini",
                    use_container_width=True,
                ):
                    if pesan not in st.session_state.bookmarks:
                        st.session_state.bookmarks.append(pesan)
                        st.success("Berhasil di-bookmark!")
                        st.rerun()
                    else:
                        st.info("Pesan sudah ada di bookmark.")
            with col_a2:
                if st.button(
                    "👍",
                    key=f"like_{idx}",
                    help="Jawaban membantu",
                    use_container_width=True,
                ):
                    st.toast("Terima kasih atas feedback positif Anda!", icon="❤️")
            with col_a3:
                if st.button(
                    "👎 Kurang tepat",
                    key=f"dislike_{idx}",
                    help="Beri tahu jika jawaban kurang akurat",
                    use_container_width=True,
                ):
                    st.toast("Feedback dicatat untuk perbaikan.", icon="⚠️")


# ============================================================
# 10. PROSES INPUT PERTANYAAN
# ============================================================

pertanyaan = st.chat_input("Tulis pertanyaan Anda di sini...")

if selected_prompt:
    pertanyaan = selected_prompt

if pertanyaan:
    waktu_sekarang = datetime.now().strftime("%H:%M")

    with st.chat_message("user", avatar="👤"):
        render_header_pesan("Anda", waktu_sekarang)
        st.markdown(pertanyaan)

    st.session_state.riwayat.append({
        "role": "user",
        "isi": pertanyaan,
        "waktu": waktu_sekarang,
    })

    if adalah_sapaan(pertanyaan):
        waktu_jawab = datetime.now().strftime("%H:%M")
        with st.chat_message("assistant", avatar="🤖"):
            render_header_pesan("Asisten n8n AI", waktu_jawab)
            st.markdown(respon_sapaan)
        jawaban = respon_sapaan
    else:
        waktu_jawab = datetime.now().strftime("%H:%M")
        with st.chat_message("assistant", avatar="🤖"):
            render_header_pesan("Asisten n8n AI", waktu_jawab)

            with st.status("🧠 Memproses permintaan...", expanded=True) as status:
                st.write("◌ Sedang menganalisis pertanyaan...")
                time.sleep(0.8)

                st.write("📚 Mencari informasi dari knowledge base...")
                time.sleep(1.0)

                st.write("✦ Menyusun jawaban...")
                time.sleep(0.6)

                status.update(label="✅ Selesai!", state="complete", expanded=False)

            jawaban_stream = st.write_stream(
                perlambat_stream(rag_chain.stream(pertanyaan))
            )

            kalimat_penutup = (
                "\n\n---  \n*Ada hal lain seputar arsitektur, expressions, node, "
                "atau deployment n8n yang ingin kita bahas lebih lanjut?*"
            )
            st.markdown(kalimat_penutup)

            jawaban = jawaban_stream + kalimat_penutup

    st.session_state.riwayat.append({
        "role": "assistant",
        "isi": jawaban,
        "waktu": waktu_jawab,
    })
    st.rerun()