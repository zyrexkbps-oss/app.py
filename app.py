import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
import base64
from gtts import gTTS
import io

# 1. KONFIGURASI HALAMAN & TEMA
st.set_page_config(
    page_title="ZYREX New AI", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS (Termasuk Ikon Garis Tiga & Gaya Chat)
st.markdown("""
    <style>
    [data-testid="stSidebarCollapseIcon"] svg { display: none; }
    [data-testid="stSidebarCollapseIcon"]::before {
        content: '☰';
        font-size: 26px;
        color: white;
        cursor: pointer;
        display: block;
        padding-top: 5px;
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

# Fungsi bantuan
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

def text_to_speech(text):
    tts = gTTS(text=text, lang='id')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp

# 2. INISIALISASI API
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Kunci API belum disetel!")
    st.stop()

# 3. SIDEBAR
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
    st.title("Genius Pro")
    st.caption("v 2.2.0 - Voice Enabled")
    st.divider()
    st.subheader("📁 Fitur Cerdas")
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")
    uploaded_image = st.file_uploader("Upload Gambar", type=["jpg", "jpeg", "png"])
    if st.button("✨ Percakapan Baru", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_count = 0
        st.rerun()
    st.divider()
    st.markdown('<a href="https://saweria.co/NewAI" class="btn-donasi">☕ Traktir Kopi / Upgrade Pro</a>', unsafe_allow_html=True)

# 4. LOGIKA ANALISIS PDF
pdf_text = ""
if uploaded_file:
    reader = PdfReader(uploaded_file)
    for page in reader.pages:
        pdf_text += page.extract_text()
    st.toast("PDF Terbaca!", icon='✅')

# 5. HALAMAN UTAMA
st.title("⚡ ZYREX New AI")

if "chat_count" not in st.session_state:
    st.session_state.chat_count = 0
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Halo! Saya ZYREX New AI. Ada yang bisa saya bantu?"}]

# Menampilkan Riwayat Chat & Tombol Suara
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            if st.button(f"🔊 Dengarkan", key=f"speak_{i}"):
                with st.spinner("Menyiapkan suara..."):
                    audio_data = text_to_speech(message["content"])
                    st.audio(audio_data, format="audio/mp3", autoplay=True)

# 6. PROSES INPUT
if prompt := st.chat_input("Ketik pesan Anda..."):
    if st.session_state.chat_count >= 7:
        st.error("⚠️ Kuota gratis habis (Maks 7 pesan).")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            if uploaded_image:
                base64_image = encode_image(uploaded_image)
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}],
                    model="llama-3.2-11b-vision-preview",
                )
            else:
                context = f"Konteks PDF: {pdf_text}\n\n" if pdf_text else ""
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "system", "content": "Kamu adalah ZYREX New AI."}, {"role": "user", "content": context + prompt}],
                    model="llama-3.3-70b-versatile",
                )
            
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            
            # Tambahkan tombol suara setelah jawaban muncul
            audio_data = text_to_speech(response)
            st.audio(audio_data, format="audio/mp3")
            
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.chat_count += 1
