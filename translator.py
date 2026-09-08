import time
from deep_translator import GoogleTranslator


def translate_transcript(
    raw_segments: list, 
    target_lang: str = "ar", 
    source_lang: str = "hi", 
    max_retries: int = 3
) -> list:
    """
    Translates transcript segments robustly using deep-translator.
    Includes explicit source language routing, session re-use, and retry backoff loops.
    """
    if not raw_segments:
        return []

    print(f"[+] Translating {len(raw_segments)} segments ({source_lang} -> {target_lang})...")
    
    # Passing explicit source_lang avoids Google's rate-limited auto-detect API
    translator = GoogleTranslator(source=source_lang, target=target_lang)
    translated_data = []

    for idx, seg in enumerate(raw_segments):
        original_text = seg.get("text", "").strip()
        translated_text = original_text

        if original_text:
            # Retry loop for segment
            for attempt in range(max_retries):
                try:
                    res = translator.translate(original_text)
                    if res and isinstance(res, str) and "Error 500" not in res:
                        translated_text = res
                        break
                    else:
                        raise ValueError("Received invalid or error string from endpoint")
                except Exception as e:
                    if attempt < max_retries - 1:
                        # Wait before retrying (0.5s, 1.0s, 1.5s)
                        time.sleep(0.5 * (attempt + 1))
                    else:
                        print(f"[!] Segment {idx+1}/{len(raw_segments)} failed after {max_retries} attempts. Keeping original.")
                        translated_text = original_text

        duration = round(seg["end"] - seg["start"], 2)
        char_count = len(translated_text)

        translated_data.append({
            "start": seg["start"],
            "end": seg["end"],
            "duration": duration,
            "original_text": original_text,
            "translated_text": translated_text,
            "text": translated_text,  # For generate_srt compatibility
            "char_count": char_count,
            "is_too_long": char_count > int(duration * 17) if duration > 0 else False
        })

        # Mild delay between requests
        time.sleep(0.05)

    print("[✓] Translation complete!")
    return translated_data