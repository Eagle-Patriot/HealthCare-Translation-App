# Healthcare Translation App

## Introduction
The **Healthcare Translation App** is a powerful tool designed to facilitate seamless communication in healthcare settings by transcribing, translating, and synthesizing speech from audio recordings. This application is built using **FastAPI**, **Streamlit**, **OpenAI Whisper API**, and **Text-to-Speech (TTS) API**.

## Features
- 🎤 **Transcription:** Convert speech from an uploaded audio file into text.
- 🌍 **Translation:** Translate the transcribed text into multiple languages.
- 🔊 **Text-to-Speech:** Generate speech audio from the translated text.
- 🔐 **User Authentication:** Secure login and signup functionality.
- 📡 **API Integration:** Uses OpenAI APIs for transcription, translation, and speech synthesis.

## Tech Stack
- **Backend:** FastAPI
- **Frontend:** Streamlit
- **Database:** SQLite
- **APIs Used:** OpenAI Whisper API, OpenAI GPT-4 API, OpenAI TTS API

## Installation

### 1️⃣ Clone the repository
```sh
$ git clone https://github.com/yourusername/healthcare-translation-app.git
$ cd healthcare-translation-app
```

### 2️⃣ Create a virtual environment
```sh
$ python3 -m venv venv
$ source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3️⃣ Install dependencies
```sh
$ pip install -r requirements.txt
```

### 4️⃣ Set up environment variables
Create a `.env` file and add your OpenAI API key:
```env
OPENAI_API_KEY=your_api_key_here
```

### 5️⃣ Run the FastAPI backend
```sh
$ uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 6️⃣ Run the Streamlit frontend
```sh
$ streamlit run app.py
```

## API Endpoints

### 🎤 Transcription API (`/transcribe/`)
**Method:** `POST`

**Description:** Converts an uploaded audio file into text.

**Request:**
```sh
curl -X POST -F "file=@audio.mp3" http://127.0.0.1:8000/transcribe/
```

**Response:**
```json
{
  "transcript": "Hello, how are you?"
}
```

### 🌍 Translation API (`/translate/`)
**Method:** `POST`

**Description:** Translates text into the specified target language.

**Request:**
```sh
curl -X POST http://127.0.0.1:8000/translate/ \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello, how are you?", "target_lang": "fr"}'
```

**Response:**
```json
{
  "translation": "Bonjour, comment allez-vous?"
}
```

### 🔊 Text-to-Speech API (`/speak/`)
**Method:** `GET`

**Description:** Converts translated text into an MP3 audio file.

**Request:**
```sh
curl -o output.mp3 "http://127.0.0.1:8000/speak/?text=Bonjour%20comment%20allez-vous"
```

## Usage
1. **Sign up or log in** to the Streamlit app.
2. **Upload an audio file** (MP3, WAV, etc.).
3. **Select a target language** and **click "Translate"**.
4. **Click "Transcribe"** to convert speech to text.
5. **Click "Speak"** to generate speech from the translated text.

## Deployment
This application can be deployed using **Render, Heroku, or AWS**. To deploy on **Render**, follow these steps:

1. Create a new service on [Render](https://render.com/).
2. Select the GitHub repository.
3. Set environment variables (`OPENAI_API_KEY`).
4. Deploy and test the API.

---
🚀 **Start using the Healthcare Translation App today!**

