import os
import shutil
from typing import List

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from core import extract_audio, generate_srt, transcribe_audio
from translator import translate_transcript

app = FastAPI(
    title="AI Dubbing Pipeline - Phase 2",
    description="Universal endpoint for video transcription and cross-lingual translation.",
    version="2.0.0"
)

class Segment(BaseModel):
    start: float
    end: float
    text: str

class TranslationRequest(BaseModel):
    target_lang: str = "es"
    segments: List[Segment]


@app.post("/transcribe-and-translate", summary="Universal Multi-Lingual Video Pipeline")
async def process_video_and_translate(
    file: UploadFile = File(...), 
    target_lang: str = Query("pa", description="Target ISO code e.g. pa, hi, es, lv, en, ar")
):
    temp_video = f"temp_{file.filename}"
    temp_audio = f"temp_{file.filename}.wav"
    
    try:
        # 1. Save uploaded file
        with open(temp_video, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. Extract Audio
        extract_audio(temp_video, temp_audio)
        
        # 3. Transcribe original spoken text (Auto-detects spoken language)
        raw_transcript, source_lang = transcribe_audio(temp_audio)
        
        # 4. Route to Translator IF target language differs from detected source language
        if source_lang.lower() == target_lang.lower():
            print("[+] Target language matches source language. Skipping translation step.")
            final_transcript = []
            for seg in raw_transcript:
                duration = round(seg["end"] - seg["start"], 2)
                char_count = len(seg["text"])
                final_transcript.append({
                    "start": seg["start"],
                    "end": seg["end"],
                    "duration": duration,
                    "original_text": seg["text"],
                    "translated_text": seg["text"],
                    "text": seg["text"],
                    "char_count": char_count,
                    "is_too_long": char_count > int(duration * 17) if duration > 0 else False
                })
        else:
            # Pass detected source_lang to eliminate 500 rate limits and auto-detect overhead
            final_transcript = translate_transcript(
                raw_transcript, 
                target_lang=target_lang, 
                source_lang=source_lang
            )
            
        # 5. Export Subtitle file
        srt_filename = f"{file.filename}_{target_lang}.srt"
        generate_srt(final_transcript, srt_filename)
        
        return {
            "filename": file.filename,
            "detected_source_lang": source_lang,
            "target_lang": target_lang,
            "translated_srt_file": srt_filename,
            "data": final_transcript
        }
        
    finally:
        if os.path.exists(temp_video):
            os.remove(temp_video)
        if os.path.exists(temp_audio):
            os.remove(temp_audio)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)