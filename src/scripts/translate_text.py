import time
import os
from openai import OpenAI
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

if os.environ.get("OPENAI_API_KEY") is None:
    raise EnvironmentError("OPENAI_API_KEY environment variable not set")

client = OpenAI()

def translate_html_file(source_file: str, target_file: str):
    """
    Translates an HTML snippet file from English to Spanish using OpenAI API.

    Args:
        source_file (str): Path to input HTML file in English
        target_file (str): Path to output HTML file in Spanish
    """

    source_path = Path(source_file)
    target_path = Path(target_file)

    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source_file}")

    html_content = source_path.read_text(encoding="utf-8")
    
    prompt = f"""
Translate the following HTML from English to Spanish.

The English text comes from the United States Declaration of Independence.

Rules:
- Preserve all HTML tags and attributes exactly, except that you may restructure <p> to <ul> or </ol> where those would better represent the text
- Translate only visible text content
- Do not add, remove, reorder, or rename any elements
- Keep formatting, spacing, punctuation style, and line breaks the same where possible
- Use vocabulary and grammar suitable for educated native Spanish speakers
- Avoid archaic, overly literal, or excessively verbose Spanish
- Preserve theological meaning, emphasis, and argumentative structure
- Preserve metaphors and rhetorical devices where possible, adapting them naturally to Spanish
- Prefer clarity and precision over word-for-word correspondence
- Do not simplify theological concepts
- Do not insert clarifying phrases that are not implicit in the original text
- Do not soften polemical or doctrinal statements
- Output ONLY the raw HTML
- Do NOT wrap the output in Markdown
- Do NOT include ```html or ``` or any code fences
- Do NOT include explanations or comments

Steps:
- 1. interpret the archaic English into modern English internally
- 2. translate into clear, natural, contemporary Spanish
- 3. review and correct any errors in translation 
- 3. Evaluate as an editor the result and adjust so that the final result achieves a "publication ready" output that accurately represents the original document's meaning and meets reasonable readability standards

HTML:
{html_content}
"""

    response = client.chat.completions.create(
        model="gpt-5.2",
        messages=[
            {"role": "system", "content": "You are a professional HTML translator."},
            {"role": "user", "content": prompt}
        ]
    )

    translated_html = response.choices[0].message.content.strip()

    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(translated_html, encoding="utf-8")

    print(f"Translated file saved to: {target_path}")

if __name__ == "__main__":
    start = time.time()

    en_folder = os.path.join(os.path.dirname(__file__), "..", "translation", "en")
    sp_folder = os.path.join(os.path.dirname(__file__), "..", "translation", "es")

    tasks = []
    
    files = os.listdir(en_folder)
    files.sort()
    for file in files:
        if file.endswith(".html") and not os.path.exists(os.path.join(sp_folder, file)):
            print(file)
            tasks.append((
                os.path.join(en_folder, file),
                os.path.join(sp_folder, file),
            ))

            #translate_html_file(os.path.join(en_folder, file), os.path.join(sp_folder, file))

    # Adjust max_workers to control parallelism (5–10 is usually safe)
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [
            executor.submit(translate_html_file, src, dst)
            for src, dst in tasks
        ]

        for future in as_completed(futures):
            try:
                x = future.result()
            except Exception as e:
                print(f"Error: {e}")

    end = time.time()
    print("Completed in", (end-start), "seconds.")
