import streamlit as st
from groq import Groq
import os

st.title("Asisten AI Kilat (Groq)")

# Input API Key secara manual di web (agar aman)
api_key = st.sidebar.text_input("Masukkan Groq API Key", type="password")

if api_key:
    client = Groq(api_key=api_key)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Apa yang bisa saya bantu?"):
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
else:
    st.warning("Silakan masukkan API Key Groq Anda di kolom sebelah kiri.")
