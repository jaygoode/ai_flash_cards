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

def prompt_ai(
    prompt: str,
    model: str = "llama2",
    system_prompt: str = "you are a senior level professional related to the questioned asked of you.",
) -> str:
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
