# Database
import sqlite3

import bcrypt
import requests
import streamlit as st
from audio_recorder_streamlit import audio_recorder

conn = sqlite3.connect('data.db')
c = conn.cursor()


def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT NOT NULL,password TEXT NOT NULL)')

def add_userdata(username, password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    c.execute('INSERT INTO userstable(username, password) VALUES (?, ?)', (username, hashed_password))
    conn.commit()

def login_user(username, password):
    c.execute('SELECT password FROM userstable WHERE username = ?', (username,))
    data = c.fetchone()
    if data and bcrypt.checkpw(password.encode('utf-8'), data[0]):
        return True
    return False

# App Title
st.title('Healthcare Translation App')

menu = ["Home", "Login", "SignUp"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Home":
    st.subheader("Welcome to the Healthcare Translation App")
    st.text("Login or Sign Up to get started")
elif choice == "Login":
    st.subheader("Login Section")
    username = st.text_input("User Name")
    password = st.text_input("Password", type='password')
    if st.checkbox("Login"):
        # create_usertable()
        result = login_user(username,password)
        if result:
            st.success(f"Logged In as {username}")
            
            # Language Selection
            st.subheader("Language Selection")
            target_lang = st.selectbox("Select Output Language", ["French (fr)", "Spanish (es)", "German (de)","English (en)"])

            # Initialize session state variables
            if "transcript" not in st.session_state:
                st.session_state["transcript"] = None
            if "translation" not in st.session_state:
                st.session_state["translation"] = None

            # File Upload
            st.subheader("🎤 Upload Your Audio")
            uploaded_file = st.file_uploader("Choose a WAV or MP3 file", type=["wav", "mp3"])
            
            st.sidebar.title("Welcome")
            st.sidebar.title("Instructions")
            st.sidebar.markdown("1. Upload an audio file.")
            st.sidebar.markdown("2. Click the 'Transcribe' button.")
            st.sidebar.markdown("3. Wait for the transcription to complete.")
            st.sidebar.markdown("4. Click the 'Translate' button.")
            st.sidebar.markdown("5. Wait for the translation to complete.")
            st.sidebar.markdown("6. Click the 'Speak' button to hear the translation.")

            if uploaded_file:
                st.audio(uploaded_file, format="audio/mp3")
                
                if st.button("🔍 Transcribe File"):
                    with st.spinner("Transcribing..."):
                        files = {"file": ("audio.mp3", uploaded_file.getvalue(), "audio/mpeg")}
                        response = requests.post("https://healthcare-translation-app-0isa.onrender.com/transcribe/", files=files)
                        transcript = response.json().get("transcript", "Error transcribing")

                    st.success("Transcription Complete!")
                    st.text_area("Transcription", transcript)
                    st.session_state["transcript"] = transcript

            # Live Audio Recording Section
            st.subheader("🎙️ Record Your Voice")
            recorded_audio = audio_recorder("Click to record", pause_threshold=5.0)

            if recorded_audio:
                st.audio(recorded_audio, format="audio/wav")

                if st.button("Transcribe Recorded Audio"):
                    with st.spinner("Transcribing..."):
                        files = {"file": ("audio.wav", recorded_audio, "audio/wav")}
                        response = requests.post("https://healthcare-translation-app-0isa.onrender.com/transcribe/", files=files)
                        transcript = response.json().get("transcript", "Error transcribing")

                    st.success("Transcription Complete!")
                    st.text_area("Transcription", transcript)
                    st.session_state["transcript"] = transcript

            #Translation Section (Only enable if transcription is done)
            if st.session_state["transcript"]:
                st.subheader("Translation")
                if st.button("Translate"):
                    with st.spinner("Translating..."):
                        translate_response = requests.post(
                            "https://healthcare-translation-app-0isa.onrender.com/translate/", 
                            json={"text": st.session_state["transcript"], "target_lang": target_lang}
                        )
                        translation = translate_response.json().get("translation", "Error translating")

                    st.success("Translation Complete!")
                    st.text_area("Translated Text", translation)
                    st.session_state["translation"] = translation

            #Text-to-Speech Section (Only enable if translation is done)
            if st.session_state["translation"] and st.button("🔊 Speak"):
                with st.spinner("Generating Speech..."):
                    encoded_text = requests.utils.quote(st.session_state["translation"])
                    audio_response = requests.get(f"https://healthcare-translation-app-0isa.onrender.com/speak/?text={encoded_text}")

                    with open("output.mp3", "wb") as f:
                        f.write(audio_response.content)

                st.success("Speech Ready!")
                st.audio("output.mp3", format="audio/mp3")
                st.balloons()

        else:
            st.warning("Incorrect Username/Password")

    
elif choice == "SignUp":
    st.subheader("Create An Account")
    new_user = st.text_input("Username")
    new_password = st.text_input("Password", type='password')
    
    if st.button("Sign Up"):
        create_usertable()
        add_userdata(new_user,new_password)
        st.success("Account Created Successfully")
        st.info("Go to Login Menu to Login")