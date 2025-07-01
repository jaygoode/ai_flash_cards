import docx
import psutil
import json
import re
import yaml
import os
import csv
import pdfplumber
import tiktoken

def format_and_split_cards(cards_json):
    split_cards = cards_json.split("\n")
    cards_as_dicts = []
    for card_str in split_cards:
        card_str = card_str.strip()
        try:
            if card_str[-1] == ",":
                card_str = card_str[:-1]
            if card_str[-1] != "}":
                card_str = card_str + "}"
            if card_str[0] != "{":
                card_str = "{" + card_str
            if card_str == "{}":
                continue
            cards_as_dicts.append(json.loads(card_str))
        except Exception as err:
            print(f"creating card dict failed. {err}")

    return cards_as_dicts

def create_json_file(filename:str) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=4)

    print(f"JSON successfully saved to '{filename}'")

def append_to_json_file(cards_dicts: list[dict], topic:str, deck_name:str) -> None:
    filename = f"./decks/{topic}_{deck_name}.json"
    
    if not os.path.exists(filename):
        create_json_file(filename)
        existing_data = []
    else:
        with open(filename, "r", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    raise ValueError("Existing file is not a list.")
            except Exception:
                existing_data = []
        
    existing_data.extend(cards_dicts)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)

    print(f"Appended {len(cards_dicts)} entries to '{filename}'")
    return filename

def extract_json(str):
    pattern = re.compile(r"\[.*?\]", re.DOTALL)
    match = pattern.search(str)
    if match:
        return match.group(0)
    else:
        print("No JSON found in the text. moving to next..")
    return False

def clean_malformed_json(json_str):
    # json_str = json_str.replace("\\", "").replace("\n", "").replace("  ", "")
    json_str = json_str.replace("\\", "").replace("  ", "")
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

def text_to_dict(text):
    cards = []
    for block in text.strip().split("\n\n"):
        lines = block.strip().splitlines()
        card = {
            "front": lines[0].split(":", 1)[1].strip(),
            "back": lines[1].split(":", 1)[1].strip(),
            "tags": lines[2].split(":", 1)[1].strip()
        }
        cards.append(card)
    return cards

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


def chunk_text(text, max_tokens=3000):
    """
    Yields text chunks that fit within the max_tokens limit.

    Args:
        text (str): The full text to split.
        max_tokens (int): Maximum tokens per chunk (adjust to model's limit minus response).
        model_name (str): Model used to select tokenizer (not currently used here).
    """
    enc = tiktoken.get_encoding("cl100k_base")
    words = text.split()
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        tokens = enc.encode(" ".join(current_chunk))
        if len(tokens) > max_tokens:
            current_chunk.pop()
            yield " ".join(current_chunk)
            current_chunk = [word]

    if current_chunk:
        yield " ".join(current_chunk)
