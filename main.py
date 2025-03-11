import os
import tempfile
from pathlib import Path

import openai
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from schema import TranslateRequest
from utils import envvars

openai.api_key = envvars.OPENAI_API_KEY

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        # Save the uploaded file temporarily
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as temp_file:
            temp_file.write(await file.read())
        
        # Open file for Whisper API
        with open(file_path, "rb") as audio_file:
            transcription = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                prompt="This is a high-quality transcription service. Ensure clarity, accuracy, and proper punctuation. Recognize medical terms, technical jargon, and conversational nuances.",
                response_format="text"
            )
        
        # Delete the temporary file after processing
        os.remove(file_path)
        
        print(f"Transcription: {transcription}")
        return JSONResponse(content={"transcript": transcription})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@app.post("/translate/")
async def translate_text(request: TranslateRequest):
    try:
        text = request.text
        target_lang = request.target_lang
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                "content": f"""You are a highly accurate and reliable translation engine.  
                Your task is to translate the user-provided text into the specified target language.  
                Preserve the original meaning and intent as closely as possible. Maintain the original style and tone, unless instructed otherwise. 
                If you encounter ambiguity, use your best judgment to provide the most likely and natural-sounding translation.
                Target language: {target_lang}
                Text to translate: {text}
                """
                }
            ],
            temperature=0.2, 
            max_tokens=500 
        )

        translation = response.choices[0].message.content.strip()

        if translation:
            print(f"Translation: {translation}")
            return {"translation": translation}
        else:
            raise HTTPException(
                status_code=500, 
                detail="Translation failed: No translation returned from the API."
            )

    except Exception as e:
        print(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@app.get("/speak/")
async def text_to_speech(text: str, filename: str = "speech.mp3"):
    try:
        print(f"Received TTS request: {text}")
        # Create a temporary file path
        temp_dir = tempfile.gettempdir()
        speech_file_path = Path(temp_dir) / filename

        # Generate speech using OpenAI API
        response = openai.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input= text
        )

        response.stream_to_file(speech_file_path)

        # Return the audio file as a response
        return FileResponse(speech_file_path, media_type="audio/mpeg", filename=filename)

    except Exception as e:
        print(f"Text-to-speech error: {e}")
        raise HTTPException(status_code=500, detail=f"Text-to-speech conversion failed: {str(e)}")