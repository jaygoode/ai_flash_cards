import requests
import os
import ollama
from ollama import ChatResponse 

def prompt_ai(ai, 
    prompt: str,
    model: str = "llama2",
    system_prompt: str = "you are a senior level professional related to the questioned asked of you.",
) -> str:
    # Example usage
    api_key = os.getenv("OPENAI_API_KEY")  # or load from secure storage
    if ai == "openai":
        return call_openai(model, api_key, prompt)
    elif ai == "ollama":
        return call_ollama(model, prompt)


def call_ollama( 
    prompt: str,
    model: str = "llama2",
    system_prompt: str = "you are a senior level professional related to the questioned asked of you.",
) -> str:
    # Example usage
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
            raise  

    return response["message"]["content"]

def call_openai(model, api_key, prompt):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# Example usage
api_key = os.getenv("OPENAI_API_KEY")  # or load from secure storage
print(call_openai(model, api_key, "Explain spaced repetition in 2 sentences."))