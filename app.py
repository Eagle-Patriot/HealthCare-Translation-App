# Database
import sqlite3

import bcrypt
import requests
import streamlit as st

conn = sqlite3.connect('data.db')
c = conn.cursor()

# Functions
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


# Title
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
        create_usertable()
        result = login_user(username,password)
        if result:
            st.success("Logged In as {}".format(username))
            
            # # Language Selection
            st.subheader("🌐 Language Selection")
            source_lang = st.selectbox("Select Input Language", ["English (en)"])
            target_lang = st.selectbox("Select Output Language", ["French (fr)", "Spanish (es)", "German (de)","English (en)"])

            # Audio Upload
            st.subheader("🎤 Upload Your Audio")
            uploaded_file = st.file_uploader("Choose a WAV or MP3 file", type=["wav", "mp3"])

            st.sidebar.title("Welcome")
            st.sidebar.title("ℹ️ Instructions")
            st.sidebar.markdown("1. Upload an audio file.")
            st.sidebar.markdown("2. Click the 'Transcribe' button.")
            st.sidebar.markdown("3. Wait for the transcription to complete.")

            if uploaded_file:
                st.audio(uploaded_file, format='audio/mp3')
                
                # Transcription Button
                if st.button("🔍 Transcribe"):
                    with st.spinner("Transcribing... ⏳"):
                        files = {"file": ("audio.mp3", uploaded_file.getvalue(), "audio/mpeg")}
                        response = requests.post("http://0.0.0.0:8000/transcribe/", files=files)
                        transcript = response.json().get("transcript", "Error transcribing")
                    
                    st.success("✅ Transcription Complete!")
                    st.text_area("📜 Transcription", transcript)

                    # Translation Section
                    st.subheader("🌍 Translation")
                    with st.spinner("Translating... 🔄"):
                        translate_response = requests.post("http://0.0.0.0:8000/translate/", json={"text": transcript, "target_lang": target_lang})
                        translation = translate_response.json().get("translation", "Error translating")

                    st.success("✅ Translation Complete!")
                    st.text_area("🔠 Translated Text", translation)
                    st.balloons()
                
                # Speak Button
                if st.button("🔊 Speak"):
                    with st.spinner("Generating Speech... 🔊"):
                        files = {"file": ("audio.mp3", uploaded_file.getvalue(), "audio/mpeg")}
                        response = requests.post("http://0.0.0.0:8000/transcribe/", files=files)
                        transcript = response.json().get("transcript", "Error transcribing")
                        trans = requests.post("http://0.0.0.0:8000/translate/", json={"text": transcript, "target_lang": target_lang})
                        translayed = trans.json().get("translation", "Error translating")
                        audio_response = requests.get(f"http://0.0.0.0:8000/speak/?text={translayed}")
                        with open("output.mp3", "wb") as f:
                            f.write(audio_response.content)
                            
                    st.success("✅ Speech Ready!")
                    st.audio("output.mp3", format="audio/mp3")

                    # Fireworks Effect
                    st.snow()  # Change to st.balloons() or st.snow() for effect
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