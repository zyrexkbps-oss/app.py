import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
import base64
import edge_tts
import asyncio
import io

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="New AI PRO", page_icon="⚡", layout="wide")

# Custom CSS
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

# Fungsi Suara Pria Slow
async def generate_speech(text):
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

# 3. SIDEBAR & LOGIKA PRO
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
    st.title("New AI PRO")
    
    # --- FITUR AKTIVASI PRO ---
    st.divider()
    st.subheader("🔑 Aktivasi Akun")
    kode_input = st.text_input("Masukkan Kode Pro", type="password", help="Dapatkan kode setelah donasi")
    
    # Cek apakah kode benar (Ganti 'NEWAI2026' dengan kode buatan Anda sendiri)
    is_pro = (kode_input == "NEWAI2026")
    
    if is_pro:
        st.success("Mode Pro Aktif! (Chat Tanpa Batas)")
    else:
        st.info("Mode Gratis: Batas 7 Pesan")
    
    st.divider()
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")
    uploaded_image = st.file_uploader("Upload Gambar", type=["jpg", "jpeg", "png"])
    
    if st.button("✨ Hapus Semua Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_count = 0
        st.rerun()
        
    st.divider()
    st.markdown('<a href="https://saweria.co/NewAI" class="btn-donasi">☕ Donasi & Dapatkan Kode Pro</a>', unsafe_allow_html=True)

# 4. MEMORI CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_count" not in st.session_state:
    st.session_state.chat_count = 0

# 5. HALAMAN UTAMA
st.title("⚡ New AI PRO")

for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            if st.button(f"🎙️ Dengarkan", key=f"voice_{i}"):
                with st.spinner("Menyiapkan suara..."):
                    audio_bytes = asyncio.run(generate_speech(message["content"]))
                    st.audio(audio_bytes, format="audio/mp3", autoplay=True)

# 6. PROSES INPUT & PEMBATASAN KUOTA
if prompt := st.chat_input("Ketik pesan Anda..."):
    # Cek kuota jika bukan user Pro
    if not is_pro and st.session_state.chat_count >= 7:
        st.error("⚠️ Kuota gratis habis! Silakan Donasi untuk mendapatkan Kode Pro.")
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
                context = ""
                if uploaded_file:
                    reader = PdfReader(uploaded_file)
                    for page in reader.pages: context += page.extract_text()
                
                msg_history = [{"role": "system", "content": "Kamu adalah New AI PRO."}]
                msg_history.extend(st.session_state.messages)
                
                completion = client.chat.completions.create(
                    messages=msg_history,
                    model="llama-3.3-70b-versatile",
                )
            
            response = completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.chat_count += 1
            
            # Suara otomatis
            try:
                audio_bytes = asyncio.run(generate_speech(response))
                st.audio(audio_bytes, format="audio/mp3", autoplay=True)
            except: pass
