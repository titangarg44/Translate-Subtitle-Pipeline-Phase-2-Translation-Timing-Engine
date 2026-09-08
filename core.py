import os
from moviepy import VideoFileClip
from faster_whisper import WhisperModel


def extract_audio(video_path: str, output_audio_path: str = "temp_audio.wav") -> str:
    """Extracts audio track from video with exact 16kHz sample rate alignment."""
    print(f"[+] Extracting audio from {video_path}...")
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(
        output_audio_path, 
        fps=16000, 
        nbytes=2, 
        codec="pcm_s16le",
        ffmpeg_params=["-ac", "1", "-async", "1"]
    )
    clip.close()
    print(f"[✓] Audio written to {output_audio_path}")
    return output_audio_path


def transcribe_audio(audio_path: str, model_size: str = "small") -> tuple[list, str]:
    """
    Transcribes audio in ANY spoken language into its native script.
    Returns: (transcript_data, detected_language_code)
    """
    print(f"[+] Loading Whisper Model ({model_size})...")
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    
    print("[+] Transcribing original speech...")
    OFFSET_SECONDS = 0.3
    
    # Always transcribe natively (Whisper auto-detects source language)
    segments, info = model.transcribe(
        audio_path,
        task="transcribe",
        beam_size=5,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500)
    )
    
    detected_lang = info.language
    print(f"[✓] Detected spoken language: '{detected_lang}' ({info.language_probability * 100:.1f}% confidence)")
    
    transcript_data = []
    for segment in segments:
        text = segment.text.strip()
        start_time = round(max(0.0, segment.start + OFFSET_SECONDS), 2)
        end_time = round(segment.end + OFFSET_SECONDS, 2)
        
        transcript_data.append({
            "start": start_time,
            "end": end_time,
            "text": text
        })
        
    return transcript_data, detected_lang


def format_timestamp(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    msecs = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{msecs:03d}"


def generate_srt(transcript_data: list, output_filename: str = "subtitles.srt") -> str:
    """Generates standard .srt subtitles safely accepting 'text' or 'translated_text'."""
    with open(output_filename, "w", encoding="utf-8") as f:
        for idx, segment in enumerate(transcript_data, start=1):
            start_str = format_timestamp(segment["start"])
            end_str = format_timestamp(segment["end"])
            
            text_content = segment.get("translated_text") or segment.get("text", "")
            text = str(text_content).strip()
            
            f.write(f"{idx}\n{start_str} --> {end_str}\n{text}\n\n")
            
    print(f"[✓] Subtitle file generated: {output_filename}")
    return output_filename