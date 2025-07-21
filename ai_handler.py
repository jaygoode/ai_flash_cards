import ollama
from ollama import ChatResponse 

def prompt_ai(
    prompt: str,
    model: str = "llama2",
    system_prompt: str = "you are a senior level professional related to the questioned asked of you.",
) -> str:
    try:
        response: ChatResponse = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            stream=False
        )  # type: ignore
    except Exception as err:
        if "try pulling" in str(err).lower():
            print(f"[!] Model '{model}' not found. Pulling it now...")
            ollama.pull(model)
            response = ollama.chat(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                stream=False
            )  # type: ignore
        else:
            raise  # re-raise original exception with context

    # Extract and return the actual content string from the response
    return response["message"]["content"]

# with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
#     results = list(executor.map(ask_model, prompts))

# for result in results:
#     print(result)


# config = file_handler.read_yaml_file("config.yaml")


# def prompt_ai(system_prompt, model="llama2"):
#     print(f"[*] Sending request to Ollama {model} model...")

#     result = subprocess.run(
#         ["ollama", "run", model, system_prompt],
#         capture_output=True,
#         text=True,
#         encoding="utf-8",
#     )

#     if result.returncode != 0:
#         raise RuntimeError(f"Ollama error:\n{result.stderr}")

#     return result.stdout.strip()
