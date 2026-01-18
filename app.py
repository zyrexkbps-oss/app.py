import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
import base64

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

# Fungsi bantuan untuk memproses gambar
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

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
    st.caption("v 2.1.0 - Vision Enabled")
    
    st.divider()
    
    # Fitur Analisis Dokumen & Gambar
    st.subheader("📁 Fitur Cerdas")
    uploaded_file = st.file_uploader("Upload PDF untuk Analisis", type="pdf")
    uploaded_image = st.file_uploader("Upload Gambar untuk Visi AI", type=["jpg", "jpeg", "png"])
    
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
    st.markdown('<a href="https://saweria.co/NewAI" class="btn-donasi">☕ Traktir Kopi / Upgrade Pro</a>', unsafe_allow_html=True)
    
    st.divider()
    st.info("AI ini menggunakan model Llama-3 & Vision untuk respon cerdas.")

# 4. LOGIKA ANALISIS DOKUMEN
pdf_text = ""
if uploaded_file:
    reader = PdfReader(uploaded_file)
    for page in reader.pages:
        pdf_text += page.extract_text()
    st.toast("Dokumen Berhasil Dimuat!", icon='✅')

# 5. HALAMAN UTAMA
st.title("⚡ ZYREX New AI")

# Inisialisasi kuota chat
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
    
    if st.session_state.chat_count >= 7:
        st.error("⚠️ Kuota chat gratis Anda telah habis (Maks 7 pesan).")
        st.info("Silakan klik tombol 'Traktir Kopi' di sidebar untuk membuka akses unlimited Agar kebutuhan yang sulit didapatkan bisa dengan mudah memberikan solusi terbaik.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # Jika ada gambar, gunakan model Vision
            if uploaded_image:
                base64_image = encode_image(uploaded_image)
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                            ]
                        }
                    ],
                    model="llama-3.2-11b-vision-preview",
                )
            # Jika tidak ada gambar, gunakan model teks biasa
            else:
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
        st.session_state.chat_count += 1
