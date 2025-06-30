import docx
import psutil
import json
import re
import yaml
import os
import csv
import pdfplumber
import tiktoken


def create_json_file(text: str):
    pattern = re.compile(r"\[.*?\]", re.DOTALL)
    match = pattern.search(text)
    if match:
        raw_json_str = match.group(0)
        cleaned_json_str = clean_malformed_json(raw_json_str)
        try:
            data = json.loads(cleaned_json_str)
        except:
            breakpoint()

        with open("cards.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print("JSON successfully extracted and saved to 'cards.json'")
    else:
        print("No JSON found in the text.")


def clean_malformed_json(json_str):
    json_str = json_str.replace("\\", "").replace("\n", "").replace("  ", "")
    # Replace ellipses `...` with a placeholder
    json_str = json_str.replace("...", "[truncated]")

    # Replace smart quotes (optional, in case of Word copy-paste)
    json_str = json_str.replace("“", '"').replace("”", '"')

    # Escape unescaped inner quotes (e.g. inside values)
    def escape_inner_quotes(match):
        return f'"{match.group(1).replace('"', '\\"')}"'

    # This ensures all string values are properly quoted and escaped
    json_str = re.sub(r'"([^"]*?[^\\])"', escape_inner_quotes, json_str)

    # Remove trailing commas before closing brackets/braces
    json_str = re.sub(r",\s*(\]|\})", r"\1", json_str)

    return json_str


def read_json_file(filepath: str) -> dict:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def read_yaml_file(filepath: str) -> dict:
    with open(filepath, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data


def write_to_yaml_file(data: dict, filepath: str) -> None:
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            existing_data = yaml.safe_load(f) or {}
    else:
        existing_data = {}

    existing_data.update(data)

    with open(filepath, "w") as f:
        yaml.dump(existing_data, f)


def is_anki_running():
    for proc in psutil.process_iter(attrs=["name", "exe", "cmdline"]):
        try:
            if "anki" in proc.info["name"].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


def read_file(filepath):
    filetype = filepath.split(".")[-1].lower()

    handler = handlers.get(filetype)
    if handler:
        return handler(filepath)
    else:
        print(f"Filetype '{filetype}' is not supported. Please use another filetype.")


def read_txt(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        return file.read()


def read_docx(filepath):
    doc = docx.Document(filepath)
    return "\n".join([para.text for para in doc.paragraphs])


def read_pdf(filepath):
    text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text


def read_csv(filepath):
    with open(filepath, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        return "\n".join([", ".join(row) for row in reader])


handlers = {
    "txt": read_txt,
    "docx": read_docx,
    "pdf": read_pdf,
    "csv": read_csv,
}


def chunk_text(text, max_tokens=3000, model_name="gpt-3.5-turbo"):
    """
    Splits text into chunks that fit within the max_tokens limit.
    Returns a list of text chunks.

    Args:
        text (str): The full text to split.
        max_tokens (int): Maximum tokens per chunk (adjust to model's limit minus response).
        model_name (str): Model used to select tokenizer (supports OpenAI tokenizer names).
    """
    enc = tiktoken.encoding_for_model(model_name)

    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        tokens = enc.encode(" ".join(current_chunk))
        if len(tokens) > max_tokens:
            current_chunk.pop()
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks
