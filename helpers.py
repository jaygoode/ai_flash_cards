from tenacity import retry, stop_after_attempt, wait_fixed

import ai_handler
import file_handler
from typing import Dict, Any
from enums import AIProvider


def get_settings(config: dict[str, Any]) -> dict[str, str]:
    """
    Gather configuration options either from user input or a provided config file.

    Args:
        use_inputs (bool): If True, prompts the user for input. If False, loads settings from `config`.
        config (dict): Configuration dictionary containing default options and file paths.
        file_handler (module): Module for reading input text files.

    Returns:
        dict: A dictionary containing configuration options such as:
            - topic (str): The topic(s) for the flashcard deck.
            - use_topic_file (str): Whether to use a file for text content ("Y"/"N").
            - deck_name (str): Name of the deck to be created.
            - card_amount (str): Number of cards to generate.
            - text (str): Text description or content to base the cards on.
    """
    options: Dict[str, str] = {}
    if config["options"]["use_inputs"].lower() in ["yes", "y"]:
        options["topic"] = input("deck topic(s): ")
        options["use_topic_file"] = input("use topic file to base cards on? (Y/N): ")
        options["deck_name"] = input("deck name: ")
        options["card_amount"] = str(input("amount of cards to generate: "))
        options["text"] = input(
            "further description for what the cards should be based on (or leave empty): "
        )
    else:
        options["topic"] = config["options"]["topic"]
        options["use_topic_file"] = config["options"]["use_topic_file"]
        options["deck_name"] = config["options"]["deck_name"]
        options["card_amount"] = config["options"]["card_amount"]
        options["text"] = config["options"]["text"]

    if config["options"]["use_topic_file"].lower() in ["yes", "y"]:
        if config["options"]["use_inputs"]:
            filename_key = input("yaml filename key value: ")
            filepath = config["filepaths"][filename_key]
        else:
            filepath = config["filepaths"]["text_file"]

        options["text"] = "create cards based on this text: \n"
        text = file_handler.read_file(filepath)
        if text is None:
            options["text"] += "No text found."
        else:
            options["text"] += text

    return options


@retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
def generate_cards(options: dict[str, str], config: dict[str, Any], prompts: dict[str, str], chunk: str) -> str:
    """
    Generate flashcards based on a given topic and text chunk using AI prompts.

    This function fills a template prompt with user options and a text chunk, sends it to an AI
    handler to generate flashcards, extracts and formats the resulting JSON, and appends
    the new cards to a JSON file. The operation is retried up to 5 times with a fixed 2-second wait on failure.

    Args:
        options (dict): User-defined options including:
            - "topic" (str): The subject or theme for the flashcards.
            - "card_amount" (str or int): Number of cards to generate.
            - "deck_name" (str): Name of the deck file to append cards to.
        config (dict): Configuration dictionary for AI model and other settings, e.g.:
            - "model" (str): AI model name to be used for generating prompts.
        prompts (dict): Dictionary containing prompt templates, expects key:
            - "generate_flashcards" (str): Prompt template with placeholders {{topic}}, {{text}}, {{card_amount}}.
        chunk (str): A segment of text to be used as input content for flashcard generation.

    Returns:
        str: The filename of the JSON file where the generated flashcards were appended.

    Raises:
        Exception: If AI response JSON extraction or formatting fails (commented out logic indicates possible exceptions).

    Notes:
        The function uses exponential retry logic from the `retry` decorator to handle transient failures
        in AI prompt processing or file handling.
    """
    breakpoint()
    filled_prompt = (
        prompts["generate_flashcards"]
        .replace("{{topic}}", options["topic"])
        .replace("{{text}}", chunk)
        .replace("{{card_amount}}", options["card_amount"])
    )
    print(f'''topic:{options["topic"]}, card amount: {options["card_amount"]}''')
    ai_provider = AIProvider.OLLAMA #TODO ui input
    model = "mistral" #TODO ui input dropdown, or type it yourself
    #TODO this logic is a bit strange if using dropdowns, maybe a if else check for typing yourself or using specific model from list
    available_models  = config["providers"].get(ai_provider.value, {}).get("models", [])
    if model not in available_models:
        model = config["providers"].get(ai_provider.value, {}).get("default_model")
        print(f"Selected model not listed, defaulting to {model}...")

    cards_to_add_response = ai_handler.call_ai(filled_prompt, ai_provider, model=model, system_prompt=prompts["system_prompt"], temperature=config["ai_model_settings"]["temperature"])
    raw_json_str = file_handler.extract_json(
        cards_to_add_response
    ) 
    list_of_cards_dicts = file_handler.format_and_split_cards(raw_json_str)
    filename = file_handler.append_to_json_file(
        list_of_cards_dicts, options["topic"], options["deck_name"]
    )

    return filename
