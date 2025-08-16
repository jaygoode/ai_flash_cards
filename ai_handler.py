import requests
import os
import ollama
from ollama import ChatResponse 
from pydantic import BaseModel, Field
from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.output_parsers import PydanticOutputParser
from enums import AIProvider
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mistralai import ChatMistralAI
from langchain_huggingface import HuggingFaceEndpoint

class Card(BaseModel):
    question: str = Field(..., description="The question to be asked on the flashcard.")
    answer: str = Field(..., description="The answer to the question on the flashcard.")
    tags: list[str] = Field(default_factory=list, description="Tags associated with the flashcard for categorization.")
    deck_name: str = Field(..., description="The name of the Anki deck to which this card belongs.")
    model: str = Field(default="llama2", description="The AI model used to generate the card content.")

    
def call_ai(
    prompt: str,
    ai_provider: AIProvider,
    model: str = "llama2",
    system_prompt: str = "You are a senior-level professional related to the question.",
    temperature: float = 0.3
) -> Card:
    """Calls the selected AI provider and returns a parsed Card object."""

    # ---- prompt setup ----
    system_msg = SystemMessagePromptTemplate.from_template(template=system_prompt)
    human_msg = HumanMessagePromptTemplate.from_template(template=prompt)
    chat_prompt = ChatPromptTemplate.from_messages([system_msg, human_msg])

    parser = PydanticOutputParser(pydantic_object=Card)
    formatted_prompt = chat_prompt.format_prompt(
        topic=prompt,
        format_instructions=parser.get_format_instructions(),
    )

    # ---- provider registry ----
    provider_factories = {
        AIProvider.OPENAI: lambda: ChatOpenAI(
            model_name=model,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            temperature=temperature,
        ),
        AIProvider.OLLAMA: lambda: ChatOllama(model=model),
        AIProvider.ANTHROPIC: lambda: ChatAnthropic(
            model=model,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=temperature,
        ),
        AIProvider.GOOGLE: lambda: ChatGoogleGenerativeAI(
            model=model,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=temperature,
        ),
        AIProvider.MISTRAL: lambda: ChatMistralAI(
            model=model,
            mistral_api_key=os.getenv("MISTRAL_API_KEY"),
            temperature=temperature,
        ),
        AIProvider.HUGGINGFACE: lambda: HuggingFaceEndpoint(
            repo_id=model,
            huggingfacehub_api_token=os.getenv("HUGGINGFACE_API_KEY"),
        ),
        AIProvider.OPENROUTER: lambda: ChatOpenAI(
            model_name=model,
            openai_api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
            temperature=temperature,
        ),
    }

    # ---- LLM instantiation ----
    if ai_provider not in provider_factories:
        raise ValueError(f"Unknown AI provider: {ai_provider}")

    llm = provider_factories[ai_provider]()

    # ---- AI call + parsing ----
    response = llm(formatted_prompt.to_messages())
    card = parser.parse(response.content)
    return card