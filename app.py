import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader

# 1. Tampilan Profesional (Branding)
st.set_page_config(page_title="Zyrex AI Pro", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stChatMessage { border-radius: 10px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# 2. Inisialisasi API
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Kunci API belum disetel!")
    st.stop()

# 3. Sidebar: Fitur Tambahan & Upload File
with st.sidebar:
    st.divider()
    st.markdown("### 📞 087879358671 Hubungi Pengembang")
    st.write("Dibuat oleh: [Zyrex]")
    st.write("Versi: 1.0 Pro")
    
    uploaded_file = st.file_uploader("Upload PDF untuk dianalisis", type="pdf")
    
    if st.button("Hapus Riwayat Chat"):
        st.session_state.messages = []
        st.rerun()

# 4. Logika Membaca PDF
pdf_text = ""
if uploaded_file:
    reader = PdfReader(uploaded_file)
    for page in reader.pages:
        pdf_text += page.extract_text()
    st.sidebar.success("Dokumen berhasil dibaca!")

# 5. Sistem Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Apa yang bisa saya bantu hari ini?"):
    # Gabungkan teks PDF ke dalam instruksi jika ada
    context = f"\n\nKonteks Dokumen: {pdf_text}" if pdf_text else ""
    full_prompt = f"Gunakan Bahasa Indonesia yang profesional. {context}\n\nUser: {prompt}"

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": full_prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.5
        )
        response = chat_completion.choices[0].message.content
        st.markdown(response)
        
    st.session_state.messages.append({"role": "assistant", "content": response})
