import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
import streamlit_authenticator as stauth

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Genius Pro AI", page_icon="⚡", layout="wide")

# --- SISTEM LOGIN SEDERHANA ---
names = ["Admin Genius", "Pengguna Pro"]
usernames = ["admin", "user123"]
passwords = ["admin123", "user123"] # Ganti sesuai keinginan Anda

# Proses Autentikasi
authenticator = stauth.Authenticate(
    {"usernames": {usernames[i]: {"name": names[i], "password": passwords[i]} for i in range(len(usernames))}},
    "genius_pro_cookie", "auth_key", cookie_expiry_days=30
)

# Menampilkan Form Login (Menggunakan format versi terbaru)
result = authenticator.login()

# Periksa Status Login
if st.session_state["authentication_status"]:
    # --- JIKA BERHASIL LOGIN, TAMPILKAN APLIKASI ---
    
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
        st.title(f"Halo, {st.session_state['name']}")
        
        st.divider()
        st.subheader("📁 Fitur Analisis")
        uploaded_file = st.file_uploader("Upload PDF", type="pdf")
        
        if st.button("✨ Hapus Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
            
        st.divider()
        authenticator.logout("Keluar Sistem", "sidebar")

    # Konten Utama AI
    st.title("⚡ Genius Pro AI")
    
    # Inisialisasi API Groq
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Apa yang ingin Anda tanyakan?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
            )
            response = chat_completion.choices[0].message.content
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

elif st.session_state["authentication_status"] is False:
    st.error("Username/password salah")
elif st.session_state["authentication_status"] is None:
    st.warning("Silakan login untuk mengakses fitur Pro.")
    st.info("Gunakan User: admin | Pass: admin123 untuk mencoba.")
