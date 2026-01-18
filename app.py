import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
from supabase import create_client
import base64
import edge_tts
import asyncio
import datetime

# --- 1. KONEKSI DATABASE (SUPABASE) ---
# Pastikan SUPABASE_URL dan SUPABASE_KEY sudah ada di Streamlit Secrets
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# --- 2. FUNGSI DATABASE ---
def simpan_ke_db(user, tanya, jawab):
    """Menyimpan chat ke tabel riwayat_obrolan"""
    try:
        data = {"username": user, "pesan": tanya, "jawaban": jawab}
        supabase.table("riwayat_obrolan").insert(data).execute()
    except:
        pass

def ambil_riwayat_db():
    """Mengambil chat lama agar tidak hilang saat refresh"""
    try:
        res = supabase.table("riwayat_obrolan").select("*").order("created_at", desc=False).execute()
        return res.data
    except:
        return []

# --- 3. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="New AI PRO", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1a1c23; color: white; }
    .stChatMessage { border-radius: 20px; padding: 15px; margin-bottom: 10px; border: 1px solid #30363d; }
    .btn-donasi {
        background-color: #ffd700; color: black; border-radius: 10px;
        padding: 10px; text-align: center; font-weight: bold;
        text-decoration: none; display: block; margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Fungsi Suara
async def generate_speech(text):
    communicate = edge_tts.Communicate(text, "id-ID-ArdiNeural", rate="-15%")
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# --- 4. INISIALISASI STATE & DATABASE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    # AMBIL DATA DARI DATABASE SAAT PERTAMA KALI DIBUKA
    data_lama = ambil_riwayat_db()
    for d in data_lama:
        st.session_state.messages.append({"role": "user", "content": d["pesan"]})
        st.session_state.messages.append({"role": "assistant", "content": d["jawaban"]})

if "chat_count" not in st.session_state:
    st.session_state.chat_count = 0

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("New AI PRO")
    
    st.subheader("🔑 Aktivasi Akun")
    kode_input = st.text_input("Masukkan Kode Pro", type="password")
    is_pro = (kode_input == "NEWAI2026")
    
    if is_pro:
        st.success("Mode Pro Aktif!")
    else:
        st.info(f"Kuota Gratis: {st.session_state.chat_count}/7")
    
    st.divider()
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")
    uploaded_image = st.file_uploader("Upload Gambar", type=["jpg", "jpeg", "png"])
    
    # Tombol Admin Rahasia
    st.divider()
    if st.checkbox("Mode Admin"):
        pw = st.text_input("Pass Admin", type="password")
        if pw == "ADMIN99":
            st.write("Akses Dashboard Aktif")
            if st.button("Cek Database Terkini"):
                st.table(ambil_riwayat_db())

    st.markdown('<a href="https://saweria.co/NewAI" class="btn-donasi">☕ Donasi & Kode Pro</a>', unsafe_allow_html=True)

# --- 6. TAMPILAN CHAT ---
st.title("⚡ New AI PRO")

for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 7. PROSES INPUT ---
if prompt := st.chat_input("Ketik pesan Anda..."):
    if not is_pro and st.session_state.chat_count >= 7:
        st.error("⚠️ Kuota habis! Masukkan Kode Pro.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # Logika Vision (Gambar)
            if uploaded_image:
                base64_image = encode_image(uploaded_image)
                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}],
                    model="llama-3.2-11b-vision-preview",
                )
            # Logika Text/PDF
            else:
                context = ""
                if uploaded_file:
                    reader = PdfReader(uploaded_file)
                    for page in reader.pages: context += page.extract_text()
                
                msg_history = [{"role": "system", "content": f"Konteks PDF: {context}"}]
                msg_history.extend(st.session_state.messages)
                
                completion = client.chat.completions.create(
                    messages=msg_history,
                    model="llama-3.3-70b-versatile",
                )
            
            response = completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.chat_count += 1
            
            # SIMPAN KE DATABASE (TIDAK HILANG SAAT REFRESH)
            simpan_ke_db(kode_input if kode_input else "Guest", prompt, response)
            
            # Suara otomatis
            try:
                audio_bytes = asyncio.run(generate_speech(response))
                st.audio(audio_bytes, format="audio/mp3", autoplay=True)
            except: pass
