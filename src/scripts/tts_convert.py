import os
import json
import sys
import time
from pathlib import Path
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

if os.environ.get("OPENAI_API_KEY") is None:
    raise EnvironmentError("OPENAI_API_KEY environment variable not set")

def text_file_to_audio(
    text: str, 
    output_file_name: str,
    model: str = "tts-1",  # change to "tts-1" for cheaper output
    voice: str = "onyx"
):
    """
    Reads text from a file and produces an audio narration.
    """

    if text is None or text.strip() == "":
        raise FileNotFoundError(f"No text found")

    full_text = text

    client = OpenAI()

    dname = os.path.dirname(output_file_name)
    os.makedirs(dname, exist_ok=True)

    try:
        with client.audio.speech.with_streaming_response.create(
            model=model,
            voice=voice,
            input=full_text
        ) as response:
            response.stream_to_file(output_file_name)

        audio = MP3(output_file_name, ID3=EasyID3)
        audio["title"] = "Sample Audio"
        audio["artist"] = "hyker06"
        audio.save()

        print(f"Audio written to: {output_file_name}")
    except:
        print("Failed:", output_file_name)
        if os.path.exists(output_file_name):
            os.remove(output_file_name)
        raise

def get_book(books, bookkey):
    for item in books:
        if item.get("bookkey") == bookkey:
            return item

    return {}

if __name__ == "__main__":
    
    start = time.time()

    text_file = os.path.join(os.path.dirname(__file__), "..", "speech", "text.txt")
    output_file_name = os.path.join(os.path.dirname(__file__), "..", "speech", "output.mp3")

    with open(text_file, "r", encoding="utf-8") as f:
        text = f.read()

    text_file_to_audio(text, output_file_name)

    end = time.time()
    print("Finished in",(end-start),"seconds")
