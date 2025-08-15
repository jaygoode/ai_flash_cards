import requests
import os
import ollama
from ollama import ChatResponse 
from pydantic import BaseModel, Field
from langchain.chat_models import ChatOllama
from langchain.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers import PydanticOutputParser

class Card(BaseModel):
    question: str = Field(..., description="The question to be asked on the flashcard.")
    answer: str = Field(..., description="The answer to the question on the flashcard.")
    tags: list[str] = Field(default_factory=list, description="Tags associated with the flashcard for categorization.")
    deck_name: str = Field(..., description="The name of the Anki deck to which this card belongs.")
    model: str = Field(default="llama2", description="The AI model used to generate the card content.")
    # system_prompt: str = Field(
    #     default="You are a senior level professional related to the question asked of you.",
    #     description="System prompt for the AI model."
    # )

def prompt_ai(ai, 
    prompt: str,
    model: str = "llama2",
    system_prompt: str = "you are a senior level professional related to the questioned asked of you.",
) -> str:
<<<<<<< HEAD
    parser = PydanticOutputParser(pydantic_object=Card)
    message = HumanMessagePromptTemplate.from_template(template=prompt)
    chat_prompt = ChatPromptTemplate.from_messages(messages=[message])
    chat_prompt_with_values = chat_prompt.format_prompt(topic=prompt, format_instructions=parser.get_format_instructions())
    llm = ChatOllama(model=model)
    response = llm(chat_prompt_with_values.to_messages())
    data = parser.parse(response.content)
    print(data)
    breakpoint()

def prompt_ai_old(
=======
    # Example usage
    api_key = os.getenv("OPENAI_API_KEY")  # or load from secure storage
    if ai == "openai":
        return call_openai(model, api_key, prompt)
    elif ai == "ollama":
        return call_ollama(model, prompt)


def call_ollama( 
>>>>>>> main
    prompt: str,
    model: str = "llama2",
    system_prompt: str = "you are a senior level professional related to the questioned asked of you.",
) -> str:
<<<<<<< HEAD
=======
    # Example usage
>>>>>>> main
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