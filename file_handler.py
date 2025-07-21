import csv
import json
import os
import re

import docx
import pdfplumber
from psutil import process_iter, NoSuchProcess, AccessDenied, Process
import tiktoken
import yaml
from typing import List, Dict, Any, cast, Generator, Iterator

def format_and_split_cards(cards_json: str) -> List[Dict[str, str]]:
    """
    Parse a JSON-like string containing multiple card objects, extract valid cards, and return them as dictionaries.

    Args:
        cards_json (str): A string containing multiple JSON objects representing flashcards.

    Returns:
        list of dict: A list of card dictionaries each containing 'front', 'back', and 'tags' keys.

    Notes:
        - Skips cards missing any of the required keys: 'front', 'back', 'tags'.
        - Attempts to clean malformed JSON-like strings before parsing.
    """

    cards_as_dicts: List[Dict[str, str]] = []
    split_cards = re.findall(r"\{[^{}]*\}", cards_json)
    for card_str in split_cards:
        if not all(key in card_str for key in ["front", "back", "tags"]):
            print(f"card '{card_str}' is missing required keys and will be skipped.")
            continue

        card_str = card_str.strip()
        if card_str[-1] == ",":
            card_str = card_str[:-1]
        if card_str[-1] != "}":
            card_str = card_str + "}"
        if card_str[0] != "{":
            card_str = "{" + card_str
        if card_str == "{}":
            continue
        cards_as_dicts.append(json.loads(card_str))

    print(f"successfully formatted {len(cards_as_dicts)}/{len(split_cards)} cards")
    return cards_as_dicts


def create_json_file(filename: str) -> None:
    """
    Create an empty JSON file with an empty dictionary as its content.

    Args:
        filename (str): Path to the JSON file to create.

    Returns:
        None

    Side effects:
        Creates or overwrites the specified JSON file.
    """

    with open(filename, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=4)

    print(f"JSON successfully saved to '{filename}'")


def append_to_json_file(cards_dicts: List[Dict[str, str]], topic: str, deck_name: str) -> str:
    """
    Append a list of card dictionaries to a JSON file named using topic and deck name.

    Args:
        cards_dicts (list of dict): List of flashcard dictionaries to append.
        topic (str): Topic name used in filename.
        deck_name (str): Deck name used in filename.

    Returns:
        str: The filename to which cards were appended.

    Raises:
        ValueError: If existing file content is not a list.
    """

    filename = f"./decks/{topic}_{deck_name}.json"
    if not os.path.exists(filename):
        create_json_file(filename)
        existing_data: List[Dict[str, str]] = []
    else:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("Existing file is not a list.")
            existing_data = cast(List[Dict[str, str]], data)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)

    print(f"Appended {len(cards_dicts)} entries to '{filename}'")
    return filename


def extract_json(str:str):
    """
    Extract the first JSON array found within a string.

    Args:
        str (str): Input string that may contain a JSON array.

    Returns:
        str: Extracted JSON array string.

    Raises:
        Exception: If no JSON array is found in the input string.
    """

    pattern = re.compile(r"\[.*?\]", re.DOTALL)
    match = pattern.search(str)
    if match:
        return match.group(0)
    else:
        raise Exception


def clean_malformed_json(json_str:str):
    """
    Clean a malformed JSON string by fixing common issues like backslashes, smart quotes, trailing commas, and ellipses.

    Args:
        json_str (str): The malformed JSON string.

    Returns:
        str: The cleaned JSON string, ready for parsing.
    """

    # json_str = json_str.replace("\\", "").replace("\n", "").replace("  ", "")
    json_str = json_str.replace("\\", "").replace("  ", "")
    # Replace ellipses `...` with a placeholder
    json_str = json_str.replace("...", "[truncated]")

    # Replace smart quotes (optional, in case of Word copy-paste)
    json_str = json_str.replace("“", '"').replace("”", '"')

    # Escape unescaped inner quotes (e.g. inside values)
    def escape_inner_quotes(match: re.Match[str]) -> str:
        return f'''"{match.group(1).replace('"', '\\"')}"'''

    # This ensures all string values are properly quoted and escaped
    json_str = re.sub(r'"([^"]*?[^\\])"', escape_inner_quotes, json_str)

    # Remove trailing commas before closing brackets/braces
    json_str = re.sub(r",\s*(\]|\})", r"\1", json_str)

    return json_str


def text_to_dict(text:str) -> List[Dict[str, str]]:
    """
    Convert specially formatted plaintext flashcards into a list of card dictionaries.

    Args:
        text (str): Plaintext with blocks separated by double newlines; each block has lines like 'front: ...', 'back: ...', 'tags: ...'.

    Returns:
        list of dict: List of card dictionaries with keys 'front', 'back', and 'tags'.
    """

    cards:List[Dict[str, str]] = []
    for block in text.strip().split("\n\n"):
        lines = block.strip().splitlines()
        card = {
            "front": lines[0].split(":", 1)[1].strip(),
            "back": lines[1].split(":", 1)[1].strip(),
            "tags": lines[2].split(":", 1)[1].strip(),
        }
        cards.append(card)
    return cards


def read_json_file(filepath: str) -> Any:
    """
    Read and parse a JSON file.

    Args:
        filepath (str): Path to the JSON file.

    Returns:
        dict: Parsed JSON data.
    """

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def read_yaml_file(filepath: str) -> Any:
    """
    Read and parse a YAML file.

    Args:
        filepath (str): Path to the YAML file.

    Returns:
        dict: Parsed YAML data.
    """

    with open(filepath, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data


def write_to_yaml_file(data: List[Dict[str, str]], filepath: str) -> None:
    """
    Write or update a YAML file with the provided dictionary data.

    Args:
        data (dict): Data to write or merge into the YAML file.
        filepath (str): Path to the YAML file.

    Returns:
        None

    Notes:
        If the file exists, merges existing data with new data before saving.
    """
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            existing_data: List[Dict[str, str]] = yaml.safe_load(f) or []
    else:
        existing_data = []

    existing_data.extend(data)

    with open(filepath, "w") as f:
        yaml.dump(existing_data, f)


def is_anki_running()-> bool:
    """
    Check if the Anki application is currently running.

    Returns:
        bool: True if an Anki process is found, False otherwise.
    """
    def get_all_processes() -> Iterator[Process]:
        return process_iter()

    for proc in get_all_processes():
        try:
            if "anki" in proc.info["name"].lower():
                return True
        except (NoSuchProcess, AccessDenied):
            continue
    return False


def read_file(filepath:str) -> str | None:
    """
    Read a file based on its extension using appropriate handler functions.

    Args:
        filepath (str): Path to the file.

    Returns:
        str or None: File content as text if supported; otherwise None.

    Side effects:
        Prints an error message if the file type is unsupported.
    """

    filetype = filepath.split(".")[-1].lower()

    handler = handlers.get(filetype)
    if handler:
        return handler(filepath)
    else:
        print(f"Filetype '{filetype}' is not supported. Please use another filetype.")
        return None


def read_txt(filepath:str):
    """
    Read a plain text (.txt) file.

    Args:
        filepath (str): Path to the text file.

    Returns:
        str: File contents as a string.
    """

    with open(filepath, "r", encoding="utf-8") as file:
        return file.read()


def read_docx(filepath:str) -> str:
    """
    Read the text content from a Microsoft Word (.docx) file.

    Args:
        filepath (str): Path to the .docx file.

    Returns:
        str: Concatenated text content from all paragraphs.
    """

    doc = docx.Document(filepath)
    return "\n".join([para.text for para in doc.paragraphs])


def read_pdf(filepath:str):
    """
    Extract text content from a PDF file.

    Args:
        filepath (str): Path to the PDF file.

    Returns:
        str: Extracted text content from all pages.
    """

    text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text


def read_csv(filepath:str):
    """
    Read a CSV file and convert its contents into a string with rows joined by newlines.

    Args:
        filepath (str): Path to the CSV file.

    Returns:
        str: CSV contents as a string, rows separated by newlines and columns by commas.
    """
    with open(filepath, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        return "\n".join([", ".join(row) for row in reader])


handlers:dict[str, Any] = {
    "txt": read_txt,
    "docx": read_docx,
    "pdf": read_pdf,
    "csv": read_csv,
}


def chunk_text(text:str, max_tokens:int=3000)-> Generator[Any, Any, Any]:
    """
    Yield successive chunks of text, each fitting within a maximum token count.

    Args:
        text (str): The full text to split.
        max_tokens (int): Maximum number of tokens per chunk.

    Yields:
        str: Text chunks that do not exceed the max_tokens limit.

    Notes:
        Uses the 'cl100k_base' tokenizer from tiktoken to count tokens.
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
