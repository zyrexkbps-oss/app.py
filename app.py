import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
import streamlit_authenticator as stauth

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Genius Pro AI", page_icon="⚡", layout="wide")

# --- SISTEM LOGIN ---
# Data User (Nama, Username, Password)
# Nanti Anda bisa mengganti password ini
names = ["Admin Genius", "Member Pro"]
usernames = ["admin", "member"]
passwords = ["admin123", "pro123"] # Password sederhana untuk test

# Hash password (keamanan)
hashed_passwords = stauth.Hasher(passwords).generate()

authenticator = stauth.Authenticate(
    names, usernames, hashed_passwords,
    "genius_pro_cookie", "signature_key", cookie_expiry_days=30
)

# Menampilkan Form Login
name, authentication_status, username = authenticator.login("Masuk ke Genius Pro AI", "main")

# --- LOGIKA APLIKASI ---
if authentication_status:
    # JIKA BERHASIL LOGIN, JALANKAN SEMUA KODE ANDA
    
    # Custom CSS
    st.markdown("""
        <style>
        [data-testid="stSidebar"] { background-color: #1a1c23; color: white; }
        .stChatMessage { border-radius: 20px; padding: 15px; margin-bottom: 10px; border: 1px solid #30363d; }
        </style>
        """, unsafe_allow_html=True)

    # 2. INISIALISASI API
    if "GROQ_API_KEY" in st.secrets:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    else:
        st.error("Kunci API belum disetel di Secrets!")
        st.stop()

    # 3. SIDEBAR
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
        st.title(f"Halo, {name}")
        st.caption("v 2.0.1 - Member Access")
        
        st.divider()
        st.subheader("📁 Fitur Cerdas")
        uploaded_file = st.file_uploader("Upload PDF untuk Analisis", type="pdf")
        
        if st.button("✨ Percakapan Baru", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        st.divider()
        # Tombol Logout
        authenticator.logout("Keluar Sistem", "sidebar")

    # 4. LOGIKA ANALISIS DOKUMEN
    pdf_text = ""
    if uploaded_file:
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            pdf_text += page.extract_text()
        st.toast("Dokumen Berhasil Dimuat!", icon='✅')

    # 5. HALAMAN UTAMA
    st.title("⚡ Genius Pro AI")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": f"Halo {name}! Ada yang bisa saya bantu hari ini?"}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ketik pesan Anda di sini..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            context = f"Konteks Dokumen: {pdf_text}\n\n" if pdf_text else ""
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Kamu adalah Genius Pro, asisten AI profesional terbaik."},
                    {"role": "user", "content": context + prompt}
                ],
                model="llama-3.3-70b-versatile",
            )
            response = chat_completion.choices[0].message.content
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

elif authentication_status == False:
    st.error("Username atau Password salah.")
elif authentication_status == None:
    st.warning("Silakan masukkan Username dan Password Anda untuk memulai.")
    st.info("Hubungi Admin untuk mendapatkan akun akses.")
    
