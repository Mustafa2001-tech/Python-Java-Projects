import streamlit as st
import yt_dlp
import whisper
from fpdf import FPDF
import os

# Set up Whisper (use "tiny" or "base" for free cloud hosting)
@st.cache_resource
def load_model():
    return whisper.load_model("base")

model = load_model()

def create_pdf(title, text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.multi_cell(0, 10, title, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    pdf.output("transcript.pdf")
    return "transcript.pdf"

st.title("🎬 Video to PDF Transcriber")

# Option 1: URL Link
link = st.text_input("Paste Video Link (YouTube, TikTok, X, etc.)")

# Option 2: Physical Upload
uploaded_file = st.file_uploader("Or Upload Video Physically", type=["mp4", "mov", "mkv", "mp3"])

if st.button("Generate Transcript"):
    audio_path = None
    title = "Transcript"

    if uploaded_file:
        audio_path = "temp_video"
        with open(audio_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        title = uploaded_file.name
    elif link:
        with st.spinner("Downloading audio..."):
            ydl_opts = {'format': 'm4a/bestaudio', 'outtmpl': 'temp_audio.%(ext)s'}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=True)
                audio_path = ydl.prepare_filename(info)
                title = info.get('title', 'Video')

    if audio_path:
        with st.spinner("Transcribing (this may take a minute)..."):
            result = model.transcribe(audio_path)
            pdf_file = create_pdf(title, result["text"])
            
            with open(pdf_file, "rb") as f:
                st.download_button("📩 Download PDF Transcript", f, file_name=f"{title}.pdf")
