import time
import os
from openai import OpenAI
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

if os.environ.get("OPENAI_API_KEY") is None:
    raise EnvironmentError("OPENAI_API_KEY environment variable not set")
    
client = OpenAI()

def format_text_file(source_file: str, target_file: str):
    """
    Formats a TEXT snippet file from into HTML using OpenAI API.

    Args:
        source_file (str): Path to input TEXT file
        target_file (str): Path to output HTML file
    """

    source_path = Path(source_file)
    target_path = Path(target_file)

    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source_file}")

    html_content = source_path.read_text(encoding="utf-8")
    
    prompt = f"""
You must return strictly valid HTML.
No markdown formatting.
No backticks.
No commentary.

Format the following TEXT snippet into basic HTML, using only <h1>, <h2>, <p>, <ul>, <ol>, <li>, and <hr> tags to represent paragraphs, lists, and sections.

Add some basic css classes in a <style> block with simple styling for the elements to make it look nice, but do not use any external CSS or JavaScript. 

The color scheme should be a dark background with light text, and the font should be a clean, modern sans-serif.

The output should be a self-contained HTML page.

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

    raw_folder = os.path.join(os.path.dirname(__file__), "..", "formatting", "raw")
    formatted_folder = os.path.join(os.path.dirname(__file__), "..", "formatting", "formatted")

    tasks = []
    
    files = os.listdir(raw_folder)
    files.sort()
    for file in files:
        if file.endswith(".txt") and not os.path.exists(os.path.join(formatted_folder, file)):
            print(file)
            tasks.append((
                os.path.join(raw_folder, file),
                os.path.join(formatted_folder, file.rsplit(".",1)[0] + ".html"),
            ))

            #format_text_file(os.path.join(raw_folder, file), os.path.join(formatted_folder, file))

    # Adjust max_workers to control parallelism (5–10 is usually safe)
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [
            executor.submit(format_text_file, src, dst)
            for src, dst in tasks
        ]

        for future in as_completed(futures):
            try:
                x = future.result()
            except Exception as e:
                print(f"Error: {e}")

    end = time.time()
    print("Completed in", (end-start), "seconds.")
