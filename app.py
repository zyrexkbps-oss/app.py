import streamlit as st
from groq import Groq

# 1. Konfigurasi Tampilan Profesional
st.set_page_config(page_title="Asisten Pro AI", page_icon="⚡", layout="centered")

st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_input_冷静=True)

st.title("⚡ Asisten AI Profesional")
st.caption("Didukung oleh Llama 3 - Responsif & Cerdas")

# 2. Koneksi ke API (Otomatis dari Secrets)
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Kunci API tidak ditemukan di Secrets!")
    st.stop()

# 3. Sistem Memori (Agar AI Ingat Percakapan Sebelumnya)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Kamu adalah asisten AI profesional, sangat responsif, cerdas, dan membantu. Jawablah selalu dalam Bahasa Indonesia yang alami seperti manusia."}
    ]

# 4. Tombol Hapus Percakapan di Sidebar
with st.sidebar:
    st.title("Pengaturan")
    if st.button("Hapus Riwayat Chat"):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()
    st.info("AI ini memiliki memori jangka pendek selama sesi ini berlangsung.")

# 5. Menampilkan Chat
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 6. Logika Input & Respon Responsif
if prompt := st.chat_input("Tanyakan apa saja..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Mengirimkan seluruh riwayat pesan agar AI punya konteks (Memori)
        chat_completion = client.chat.completions.create(
            messages=st.session_state.messages,
            model="llama-3.3-70b-versatile",
            temperature=0.7, # Membuat jawaban lebih kreatif & manusiawi
            max_tokens=2048
        )
        response = chat_completion.choices[0].message.content
        st.markdown(response)
        
    st.session_state.messages.append({"role": "assistant", "content": response})
