import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
import base64
import edge_tts
import asyncio
import io

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="New AI PRO", page_icon="⚡", layout="wide")

# Custom CSS (Ikon Garis Tiga & Gaya Chat)
st.markdown("""
    <style>
    [data-testid="stSidebarCollapseIcon"] svg { display: none; }
    [data-testid="stSidebarCollapseIcon"]::before {
        content: '☰'; font-size: 26px; color: white; cursor: pointer;
        display: block; padding-top: 5px;
    }
    [data-testid="stSidebar"] { background-color: #1a1c23; color: white; }
    .stChatMessage { border-radius: 20px; padding: 15px; margin-bottom: 10px; border: 1px solid #30363d; }
    .btn-donasi {
        background-color: #ffd700; color: black; border-radius: 10px;
        padding: 10px; text-align: center; font-weight: bold;
        text-decoration: none; display: block; margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Fungsi untuk menghasilkan suara Manusia (Pria - Ardi) yang Kalem/Slow
async def generate_speech(text):
    # Menggunakan suara Pria Indonesia (ArdiNeural)
    # Rate -15% agar bicara lebih kalem dan tidak seperti robot
    communicate = edge_tts.Communicate(text, "id-ID-ArdiNeural", rate="-15%")
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# 2. INISIALISASI API
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 3. SIDEBAR
with st.sidebar:
    # Logo robot tetap dipertahankan namun judul diubah
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
    st.title("New AI PRO")
    st.caption("v 2.5.0 - Natural Voice & Vision")
    st.divider()
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")
    uploaded_image = st.file_uploader("Upload Gambar", type=["jpg", "jpeg", "png"])
    if st.button("✨ Percakapan Baru", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_count = 0
        st.rerun()
    st.divider()
    st.markdown('<a href="https://saweria.co/NewAI" class="btn-donasi">☕ Upgrade Pro / Donasi</a>', unsafe_allow_html=True)

# 4. LOGIKA ANALISIS PDF
pdf_text = ""
if uploaded_file:
    reader = PdfReader(uploaded_file)
    for page in reader.pages:
        pdf_text += page.extract_text()

# 5. HALAMAN UTAMA
st.title("⚡ New AI PRO")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Halo! Saya New AI PRO. Ada yang bisa saya bantu hari ini?"}]

# Menampilkan Riwayat Chat & Tombol Speaker
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            # Tombol Speaker di bawah jawaban
            if st.button(f"🎙️ Dengarkan", key=f"voice_{i}"):
                with st.spinner("Menyiapkan suara..."):
                    audio_bytes = asyncio.run(generate_speech(message["content"]))
                    st.audio(audio_bytes, format="audio/mp3", autoplay=True)

# 6. PROSES INPUT
if prompt := st.chat_input("Ketik pesan Anda di sini..."):
    if st.session_state.get('chat_count', 0) >= 7:
        st.error("⚠️ Kuota gratis New AI PRO habis.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            if uploaded_image:
                base64_image = encode_image(uploaded_image)
                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}],
                    model="llama-3.2-11b-vision-preview",
                )
            else:
                context = f"Konteks PDF: {pdf_text}\n\n" if pdf_text else ""
                completion = client.chat.completions.create(
                    messages=[{"role": "system", "content": "Kamu adalah New AI PRO, asisten profesional yang cerdas dan ramah."}, {"role": "user", "content": context + prompt}],
                    model="llama-3.3-70b-versatile",
                )
            
            response = completion.choices[0].message.content
            st.markdown(response)
            
            # Autoplay suara untuk jawaban terbaru (Suara Pria Slow)
            try:
                audio_bytes = asyncio.run(generate_speech(response))
                st.audio(audio_bytes, format="audio/mp3", autoplay=True)
            except:
                pass
            
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.chat_count = st.session_state.get('chat_count', 0) + 1
