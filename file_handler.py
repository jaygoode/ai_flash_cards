import docx
import psutil
import json
import re
import yaml
import os
import csv
import pdfplumber

def create_json_file(text:str):
    pattern = re.compile(r'\[.*?\]', re.DOTALL)
    match = pattern.search(text)
    if match:
        json_str = match.group(0)
        json_str.replace("\\", "").replace("\n", "").replace("  ", "")
        # Load the JSON string to Python object
        data = json.loads(json_str)

        # Save to a JSON file
        with open('cards.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        print("JSON successfully extracted and saved to 'task_plan.json'")
    else:
        print("No JSON found in the text.")


def read_json_file(filepath:str) -> dict:
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def read_yaml_file(filepath:str) -> dict:
    with open(filepath, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data

def write_to_yaml_file(data:dict, filepath:str) -> None:
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
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read()

def read_docx(filepath):
    doc = docx.Document(filepath)
    return "\n".join([para.text for para in doc.paragraphs])

def read_pdf(filepath):
    text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ''
    return text

def read_csv(filepath):
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        return "\n".join([", ".join(row) for row in reader])

handlers = {
    'txt': read_txt,
    'docx': read_docx,
    'pdf': read_pdf,
    'csv': read_csv,
}
