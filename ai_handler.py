import subprocess
import file_handler
from enum import Enum, auto

import concurrent.futures
import ollama

def ask_model(prompt, model="llama2"):
    return ollama.chat(model=model, messages=[
        {'role': 'user', 'content': prompt}
    ])['message']['content']


# with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
#     results = list(executor.map(ask_model, prompts))

# for result in results:
#     print(result)


config = file_handler.read_yaml_file("config.yaml")


def prompt_ai(system_prompt, model="llama2"):
    print(f"[*] Sending request to Ollama {model} model...")

    result = subprocess.run(
        ["ollama", "run", model, system_prompt],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    if result.returncode != 0:
        raise RuntimeError(f"Ollama error:\n{result.stderr}")

    return result.stdout.strip()
