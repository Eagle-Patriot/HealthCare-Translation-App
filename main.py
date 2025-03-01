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
    """
    Transcribes an audio file using OpenAI Whisper API with optimized prompt engineering.

    Args:
        file (UploadFile): The audio file to transcribe. Supported formats: MP3, WAV, FLAC, etc.

    Returns:
        dict: A dictionary containing the transcript or an error message.
    """
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
    """
    Translates text from any language to the target language using OpenAI's GPT-4 model.

    Args:
        text (str): The text to translate.
        target_lang (str): The ISO 639-1 language code of the target language (e.g., "es" for Spanish, "fr" for French).

    Returns:
        dict: A dictionary containing the translation.  Returns an error message if something goes wrong.
    """
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
            temperature=0.2, # Lower temperature for more consistent results
            max_tokens=500  # Adjust as needed
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
        print(f"Translation error: {e}") # Log the error for debugging
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@app.get("/speak/")
async def text_to_speech(text: str, filename: str = "speech.mp3"):
    """
    Converts text to speech using OpenAI's Text-to-Speech API.

    Args:
        text (str): The text to convert to speech.
        filename (str): The name of the output audio file. Defaults to "speech.mp3".

    Returns:
        FileResponse: An MP3 file containing the synthesized speech.

    Raises:
        HTTPException: If there's an error during text-to-speech conversion.
    """
    try:
        print(f"Received TTS request: {text}")  # ✅ Debugging log
        # Create a temporary file path
        temp_dir = tempfile.gettempdir()
        speech_file_path = Path(temp_dir) / filename

        # Generate speech using OpenAI API
        response = openai.audio.speech.create(
            model="tts-1",
            voice="alloy",  # Change voice if needed (alloy, echo, fable, onyx, nova, shimmer)
            input= text
        )

        response.stream_to_file(speech_file_path)

        # Return the audio file as a response
        return FileResponse(speech_file_path, media_type="audio/mpeg", filename=filename)

    except Exception as e:
        print(f"Text-to-speech error: {e}")
        raise HTTPException(status_code=500, detail=f"Text-to-speech conversion failed: {str(e)}")



