import os
import argparse
import json

from faster_whisper import WhisperModel
from openai import OpenAI

if os.environ.get("OPENAI_API_KEY") is None:
    raise EnvironmentError("OPENAI_API_KEY environment variable not set")

parser = argparse.ArgumentParser(
description="TagTheWord.org Sermon Parser",
formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('-i','--input-file', required=True, help="MP3 file to parse")
parser.add_argument('-m','--model', default="tiny", help="Whisper Model (tiny, base, etc.)")
parser.add_argument('-t','--compute-type', default="int8", help="Whisper Model Compute Type")
parser.add_argument('-f','--transcript-file', default=None, help="Transcript file")
parser.add_argument('-o','--output-file', default=None, help="Output file (json)")
parser.add_argument('-r','--retry', action="store_true", help="Force reprocessing of transcript")

ARGS = parser.parse_args()

audio_file_name = ARGS.input_file
if "." not in audio_file_name:
    print("Invalid input file.")
    quit()

file_path = ARGS.transcript_file if ARGS.transcript_file is not None else audio_file_name.rsplit(".",1)[0] + ".txt"
whisper_model_name = ARGS.model
compute_type = ARGS.compute_type
output_file_name = ARGS.output_file if ARGS.output_file is not None else audio_file_name.rsplit(".",1)[0] + ".json"

if ARGS.retry and os.path.exists(file_path):
    print(f"Removing existing transcript file {file_path} due to --retry flag.")
    os.remove(file_path)

prompt_text = """
You must return strictly valid JSON.
No markdown formatting.
No backticks.
No commentary.
The first character must be { and the last character must be }.

Task:
The attached file is a transcript of a Jeep enthusiast youtube video.
Extract from the transcript a post title and additional materials in the following format.

Example JSON format:
{
    "title": "{extracted_title}",
    "summary": "{3-4 sentence summary of the subject of the video}",
    "intro": "{160 character introduction to the message for social media, text-only}",
    "main_points": [],
    "target_audience": {
        "age_range": "{age range of the intended audience, e.g. '18-35'}",
        "demographics": "{any relevant demographic information about the intended audience, e.g. 'college students', 'working professionals', 'retirees'}"
    },
    "parts": [
        { "part_name": "{name of part mentioned}", "description": {short description of part}, "url": "{url to purchase if known else leave empty}" }
    ],
    "citations": [
        { "type": "{article|book|other|statistic}", "author": "{originating author or publisher}", "title": "{name of source}", "url": "{url of source}" }
    ],
    "tags": [],
    "warnings": [],
    "risks": [],
    "tone": "{tone of the video, e.g. 'fun', 'serious', 'apologetic'}",
    "content_density": {content_density_score_as_integer_from_1_to_10},
}

Required:
- Title must be no more than 35 characters
- Do not repeat parts or citations
- Add relevant categorical and topical tags to the "tags" array.
- Add any callouts from the content that may be inaccurate or cause confusion to viewers.
- Add any notes about the content that include sensitive cultural issues, mental or emotional issues (abuse, suicide, trauma), or otherwise inappropriate content to the "warnings" array.
- Add simplified main points to the "main_points" array.
"""

if not os.path.exists(file_path):
    try:
        print("Loading transcription model.")
        model = WhisperModel(whisper_model_name, compute_type=compute_type)

        print("Transcribing audio.")
        segments, info = model.transcribe(audio_file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            for segment in segments:
                f.write(segment.text + "\n")
    except:
        if os.path.exists(file_path):
            os.remove(file_path)

        raise

if not os.path.exists(file_path):
    print("Transcription file not found.  Exiting.")
    quit(1)

try:
    print("Processing transcription.")
    client = OpenAI()

    uploaded_file = client.files.create(
        file=open(file_path, "rb"),
        purpose="assistants"
    )

    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt_text},
                    {
                        "type": "input_file",
                        "file_id": uploaded_file.id,
                    },
                ],
            }
        ],
    )

    print("== OUTPUT ===============================")
    # Always print to the screen)
    print(response.output_text)

    if output_file_name is not None:
        response_json = json.loads(response.output_text)
        response_json["file"] = os.path.basename(audio_file_name)
        with open(output_file_name, "w", encoding="UTF-8") as fp:
            json.dump(response_json, fp, indent=4)
except:
    if os.path.exists(output_file_name):
        os.remove(output_file_name)

    raise


