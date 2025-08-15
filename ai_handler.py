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
) -> Card:
    
    ai_providers = {
        AIProvider.OPENAI: ChatOpenAI,                           # GPT-4, GPT-3.5
        AIProvider.OLLAMA: ChatOllama,                           # Local LLaMA, Mistral, Gemma, etc.
        AIProvider.ANTHROPIC: ChatAnthropic,                     # Claude 3 series
        AIProvider.GOOGLE: ChatGoogleGenerativeAI,               # Gemini Pro
        AIProvider.MISTRAL: ChatMistralAI,                        # Mixtral, Mistral Instruct
        AIProvider.HUGGINGFACE: HuggingFaceEndpoint,             # HF models
        # AIProvider.OPENROUTER: Custom integration via OpenAI-compatible endpoint
}

    llm_class = ai_providers.get(ai_provider)
    if not llm:
        raise ValueError(f"Unknown AI provider: {ai_provider}")

    # Call function with correct arguments
    if ai_provider == AIProvider.OPENAI:
        llm = llm_class(model_name=model, openai_api_key=api_key, temperature=0)
    elif ai_provider == AIProvider.OLLAMA:
        llm = llm_class(model=model)
    else:
        raise ValueError(f"Unknown AI provider: {ai_provider}")

    parser = PydanticOutputParser(pydantic_object=Card)

    # System message for behavior/context
    system_msg = SystemMessagePromptTemplate.from_template(system_prompt)

    # User (human) message
    human_msg = HumanMessagePromptTemplate.from_template(template=prompt)

    # Combine system + human messages
    chat_prompt = ChatPromptTemplate.from_messages([system_msg, human_msg])

    formatted_prompt = chat_prompt.format_prompt(
        topic=prompt,
        format_instructions=parser.get_format_instructions()
    )

    # Provider selection
    if ai_provider == AIProvider.OPENAI:
        api_key = os.getenv("OPENAI_API_KEY")
        llm = ChatOpenAI(model_name=model, openai_api_key=api_key, temperature=0)
    elif ai_provider == AIProvider.OLLAMA:
        llm = ChatOllama(model=model)
    else:
        raise ValueError(f"Unknown AI provider: {ai_provider}")

    # AI call + parsing
    response = llm(formatted_prompt.to_messages())
    card = parser.parse(response.content)
    return card