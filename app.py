import streamlit as st
from groq import Groq

# Mengatur tampilan halaman
st.set_page_config(page_title="Asisten AI Zyrex", page_icon="🤖")
st.title("🤖 Asisten AI Bisnis")

# Mengambil API Key dari Secrets (otomatis)
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("API Key belum dipasang di Secrets!")
    st.stop()

# Memulai percakapan
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Halo! Saya asisten cerdas Anda. Ada yang bisa saya bantu hari ini?"}
    ]

# Menampilkan chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input dari pengguna
if prompt := st.chat_input("Ketik pesan Anda di sini..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Instruksi rahasia agar AI bicara bahasa Indonesia
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Kamu adalah asisten AI yang ramah dan selalu menjawab dalam Bahasa Indonesia."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
        )
        response = chat_completion.choices[0].message.content
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
