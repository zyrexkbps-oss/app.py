import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader

# 1. KONFIGURASI HALAMAN & TEMA (Branding)
st.set_page_config(
    page_title="ZYREX New AI", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk tampilan premium dan modern
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #1a1c23;
        color: white;
    }
    .stChatMessage {
        border-radius: 20px;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid #30363d;
    }
    /* Tombol Khusus Monetisasi */
    .btn-donasi {
        background-color: #ffd700;
        color: black;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        font-weight: bold;
        text-decoration: none;
        display: block;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. INISIALISASI API
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Kunci API belum disetel di Secrets!")
    st.stop()

# 3. SIDEBAR (Menu Utama & Monetisasi)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
    st.title("Genius Pro")
    st.caption("v 2.0.1 - Premium Access")
    
    st.divider()
    
    # Fitur Analisis Dokumen
    st.subheader("📁 Fitur Cerdas")
    uploaded_file = st.file_uploader("Upload PDF untuk Analisis", type="pdf")
    
    # Kontrol Percakapan
    st.subheader("⚙️ Pengaturan")
    if st.button("✨ Percakapan Baru", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_count = 0 # Reset kuota chat
        st.rerun()
    
    st.divider()
    
    # --- BAGIAN MONETISASI ---
    st.subheader("💰 Dukung Kami")
    st.write("Dapatkan akses tanpa batas (Kuota Unlimited) dengan mendukung kami.")
    # Ganti link di bawah dengan link Saweria/Trakteer/WhatsApp Anda
    st.markdown('<a href="https://saweria.co/username_anda" class="btn-donasi">☕ Traktir Kopi / Upgrade Pro</a>', unsafe_allow_html=True)
    
    st.divider()
    st.info("AI ini menggunakan model Llama-3 untuk respon super cepat.")

# 4. LOGIKA ANALISIS DOKUMEN
pdf_text = ""
if uploaded_file:
    reader = PdfReader(uploaded_file)
    for page in reader.pages:
        pdf_text += page.extract_text()
    st.toast("Dokumen Berhasil Dimuat!", icon='✅')

# 5. HALAMAN UTAMA
st.title("⚡ ZYREX New AI")

# Inisialisasi kuota chat (Limit 5 pesan untuk pengguna gratis)
if "chat_count" not in st.session_state:
    st.session_state.chat_count = 0

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Halo! Saya ZYREX New AI. Ada yang bisa saya bantu hari ini?"}
    ]

# Menampilkan Riwayat Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. PROSES INPUT & LIMITASI
if prompt := st.chat_input("Ketik pesan Anda di sini..."):
    
    # Cek Kuota Chat (Monetisasi)
    if st.session_state.chat_count >= 5:
        st.error("⚠️ Kuota chat gratis Anda telah habis (Maks 5 pesan).")
        st.info("Silakan klik tombol 'Traktir Kopi' di sidebar untuk membuka akses unlimited atau hubungi Admin.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            context = f"Konteks Dokumen: {pdf_text}\n\n" if pdf_text else ""
            
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Kamu adalah ZYREX New AI, asisten AI profesional terbaik yang ramah dan solutif dalam Bahasa Indonesia."},
                    {"role": "user", "content": context + prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.6
            )
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.chat_count += 1 # Tambah hitungan chat
