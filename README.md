# demo-ai

Example scripts for text-to-html formatting, english-to-spanish translation, text-to-speech generation, and MP3 audio analysis.

Scripts in the ```src/scripts``` folder

You will need to set an environment variable named ```OPENAI_API_KEY``` with your authorization key for OpenAI's APIs for the examples to work.

## Setup

```
pip install -r requirements.txt
```

## Running Scripts

```
python ./src/scripts/format_text.py
python ./src/scripts/process_audio.py -i ./src/audio/blog_post.mp3
python ./src/scripts/translate_text.py
python ./src/scripts/tts_convert.py
python ./src/scripts/tts_convert_with_feeling
python ./src/scripts/tts_convert_weather.py
```

*Have fun!*