import streamlit as st
from groq import Groq

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Asisten AI Profesional", page_icon="⚡")

# Perbaikan kode desain (CSS) yang menyebabkan error sebelumnya
st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ Asisten AI Profesional")

# 2. Koneksi ke API (Otomatis dari Secrets)
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.warning("Silakan masukkan API Key di menu Secrets Streamlit.")
    st.stop()

# 3. Sistem Memori (Agar AI Nyambung Diajak Bicara)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Kamu adalah asisten AI yang cerdas dan selalu menjawab dalam Bahasa Indonesia yang profesional namun ramah."}
    ]

# 4. Sidebar untuk Fitur Tambahan
with st.sidebar:
    st.header("Pengaturan")
    if st.button("Hapus Riwayat Percakapan"):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()

# 5. Menampilkan Riwayat Chat
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 6. Input Pengguna dan Respon AI
if prompt := st.chat_input("Tanyakan sesuatu..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # AI akan merespon berdasarkan seluruh riwayat (Memory)
        chat_completion = client.chat.completions.create(
            messages=st.session_state.messages,
            model="llama-3.3-70b-versatile",
            temperature=0.7
        )
        response = chat_completion.choices[0].message.content
        st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
