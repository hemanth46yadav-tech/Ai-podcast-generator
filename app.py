import streamlit as st
import os

from src.script_generator import generate_podcast_script
from src.audio_generator import create_podcast_audio

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="AI Podcast Generator", 
    page_icon="🎧", 
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (PREMIUM UI) ---
st.markdown("""
<style>
    /* Main Background & Fonts */
    .stApp {
        background: radial-gradient(circle at top, #1a2235 0%, #0d1117 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Headers */
    h1 {
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #00C6FF, #0072FF, #8A2BE2);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        letter-spacing: -1px;
        animation: shine 3s linear infinite;
    }
    
    @keyframes shine {
        to {
            background-position: 200% center;
        }
    }
    
    .subtitle {
        text-align: center;
        color: #8b949e;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Buttons */
    div.stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #00C6FF 0%, #0072FF 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(0, 114, 255, 0.3);
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 114, 255, 0.5);
    }
    
    /* Transcript Cards */
    .host-card {
        background: rgba(0, 198, 255, 0.05);
        border-left: 4px solid #00C6FF;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
    }
    .host-card:hover { transform: translateX(5px); }
    
    .guest-card {
        background: rgba(138, 43, 226, 0.05);
        border-left: 4px solid #8A2BE2;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
    }
    .guest-card:hover { transform: translateX(5px); }
    
    /* 3D Rotating Microphone animation */
    .rotating-mic {
        font-size: 110px;
        display: block;
        text-align: center;
        margin: 0 auto 10px auto;
        animation: rotate3D 5s cubic-bezier(0.45, 0.05, 0.55, 0.95) infinite;
        filter: drop-shadow(0px 15px 15px rgba(0,198,255,0.4));
        transform-origin: center center;
    }
    @keyframes rotate3D {
        0% { transform: perspective(800px) rotateY(0deg) rotateX(10deg) rotateZ(0deg); }
        50% { transform: perspective(800px) rotateY(180deg) rotateX(25deg) rotateZ(5deg) scale(1.15); filter: drop-shadow(0px 35px 25px rgba(138,43,226,0.6)); }
        100% { transform: perspective(800px) rotateY(360deg) rotateX(10deg) rotateZ(0deg); }
    }
    
</style>
""", unsafe_allow_html=True)

# --- UI LAYOUT ---

# Top Header with Animation
st.markdown('<div class="rotating-mic">🎙️</div>', unsafe_allow_html=True)
st.markdown("<h1>Podcast AI Setup</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">Generate professional 2-person podcasts from any text prompt.</p>', unsafe_allow_html=True)


# Voice Selection Settings (Sidebar)
VOICES = {
    "Christopher (Deep, Authoritative)": "en-US-ChristopherNeural",
    "Jenny (Friendly, Conversational)": "en-US-JennyNeural",
    "Guy (Passionate, News)": "en-US-GuyNeural",
    "Aria (Positive, Confident)": "en-US-AriaNeural",
    "Andrew (Warm, Authentic)": "en-US-AndrewNeural",
    "Emma (Cheerful, Clear)": "en-US-EmmaNeural",
    "Steffan (Rational, News)": "en-US-SteffanNeural"
}

st.sidebar.markdown("### ⚙️ Studio Controls")
st.sidebar.markdown("Customize your hosts:")
host_voice_name = st.sidebar.selectbox("🎙️ Host Voice", list(VOICES.keys()), index=0)
guest_voice_name = st.sidebar.selectbox("🎙️ Guest Voice", list(VOICES.keys()), index=1)

host_voice_id = VOICES[host_voice_name]
guest_voice_id = VOICES[guest_voice_name]

st.sidebar.markdown("---")
st.sidebar.markdown("Powered by **Gemini 2.5** & **Edge TTS**")

# Input section
topic = st.text_input("What should the podcast be about?", placeholder="e.g. Why Python is great for AI, The history of Rome...")
st.markdown("<br>", unsafe_allow_html=True)

if st.button("Generate Podcast", type="primary"):
    if not topic.strip():
        st.error("Please enter a topic first.")
    else:
        # Step 1: Generate Script
        with st.spinner("✍️ Neural network is writing the script..."):
            script = generate_podcast_script(topic)
            
        if not script:
            st.error("Failed to generate script. Please try again.")
            st.stop()
            
        # Display the script with custom CSS styling
        st.subheader("📄 Studio Transcript")
        
        transcript_container = st.container()
        
        with transcript_container:
            for line in script:
                speaker = line.get("speaker")
                text = line.get("text")
                
                if speaker == "Host":
                    st.markdown(f'<div class="host-card"><strong>[ {speaker} ]</strong><br>{text}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="guest-card"><strong>[ {speaker} ]</strong><br>{text}</div>', unsafe_allow_html=True)
                
        # Step 2: Generate Audio
        with st.spinner("🎧 Synthesizing audio and mastering tracks..."):
            audio_path = create_podcast_audio(script, host_voice=host_voice_id, guest_voice=guest_voice_id, output_filename="streamlit_output.mp3")
            
        if not audio_path or not os.path.exists(audio_path):
            st.error("Failed to generate audio file.")
            st.stop()
            
        # Step 3: Present audio to user at the bottom
        with open(audio_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
            
        st.markdown("---")
        st.success("✅ Mastering complete! Listen below:")
        st.audio(audio_bytes, format="audio/mp3", loop=False, autoplay=False)
        st.balloons()
