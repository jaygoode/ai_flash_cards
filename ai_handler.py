import os
import ast
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
from typing import Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from pathlib import Path
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
import platform 
from langchain_community.document_loaders import PyPDFLoader

class Card(BaseModel):
    question: str = Field(..., description="The question to be asked on the flashcard.")
    answer: str = Field(..., description="The answer to the question on the flashcard.")
    tags: list[str] = Field(default_factory=list, description="Tags associated with the flashcard for categorization.")
    deck_name: str = Field(..., description="The name of the Anki deck to which this card belongs.")
    model: str = Field(default="llama2", description="The AI model used to generate the card content.")

def vector_store_init():
    EMBEDDING_MODEL = "BAAI/bge-large-en"
    embeddings = 123
    
def call_ai(
    prompt: str,
    ai_provider: AIProvider,
    model: str = "llama2",
    system_prompt: str = "You are a senior-level professional related to the question.",
    temperature: float = 0.3,
    vector_store: Optional[Chroma] = None,
    k: int = 3
) -> Card:
    """
    Calls the selected AI provider and returns a list of flashcards.
    Each flashcard is a dict: {"front": ..., "back": ..., "tags": ...}
    """
        
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

    if vector_store:
        retriever = vector_store.as_retriever(search_kwargs={"k": k})
        context_docs = retriever.get_relevant_documents(prompt)
        context_text = "\n\n".join([doc.page_content for doc in context_docs])
        prompt = f"Context:\n{context_text}\n\nQuestion:\n{prompt}"

    # ---- prompt setup ----
    system_msg = SystemMessagePromptTemplate.from_template(template=system_prompt)
    human_msg = HumanMessagePromptTemplate.from_template(template=prompt)
    chat_prompt = ChatPromptTemplate.from_messages([system_msg, human_msg])

    parser = PydanticOutputParser(pydantic_object=Card)
    formatted_prompt = chat_prompt.format_prompt(
        topic=prompt,
        format_instructions=parser.get_format_instructions(),
    )

    # ---- AI call ----
    response = llm(formatted_prompt.to_messages())
    raw_output = response.content.strip()

    # ---- Parse safely into Python list ----
    try:
        flashcards = ast.literal_eval(raw_output)
    except Exception:
        raise ValueError(f"Model returned invalid flashcard list:\n{raw_output}")

    return flashcards

def init_vector_store(config:dict):
    os_name = platform.system().lower()
    docs = load_documents(config["filepaths"][os_name]["files_path"])

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.create_documents(docs)
    embeddings = OllamaEmbeddings(model="nomic-embed-text") #TODO needs dynamic embedding choices for all models
    return Chroma.from_documents(chunks, embeddings)

def load_documents(folder_path: str):
    folder = Path(folder_path)
    docs = []

    # ---- Load TXT files ----
    for file_path in folder.glob("*.txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        docs.append(Document(page_content=text, metadata={"source": str(file_path)}))

    # ---- Load PDF files ----
    for file_path in folder.glob("*.pdf"):
        loader = PyPDFLoader(str(file_path))
        pdf_docs = loader.load()  # returns a list of Documents (1 per page)
        for d in pdf_docs:
            d.metadata["source"] = str(file_path)
        docs.extend(pdf_docs)

    return docs