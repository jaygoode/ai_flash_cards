from tenacity import retry, stop_after_attempt, wait_fixed

import ai_handler
import file_handler


def get_settings(use_inputs, config, file_handler):
    """
    Gather configuration options either from user input or a provided config file.

    Args:
        use_inputs (bool): If True, prompts the user for input. If False, loads settings from `config`.
        config (dict): Configuration dictionary containing default options and file paths.
        file_handler (module): Module for reading input text files.

    Returns:
        dict: A dictionary containing configuration options such as:
            - topic (str): The topic(s) for the flashcard deck.
            - use_file (str): Whether to use a file for text content ("Y"/"N").
            - deck_name (str): Name of the deck to be created.
            - card_amount (str): Number of cards to generate.
            - text (str): Text description or content to base the cards on.
    """
    options = {}
    if use_inputs:
        options["topic"] = input("deck topic(s): ")
        options["use_file"] = input("use file to base cards on? (Y/N): ")
        options["deck_name"] = input("deck name: ")
        options["card_amount"] = str(input("amount of cards to generate: "))
        options["text"] = input(
            "further description for what the cards should be based on (or leave empty): "
        )
    else:
        options["topic"] = config["options"]["topic"]
        options["use_file"] = config["options"]["use_file"]
        options["deck_name"] = config["options"]["deck_name"]
        options["card_amount"] = config["options"]["card_amount"]
        options["text"] = config["options"]["text"]

    if options["use_file"].lower() in ["yes", "y"]:
        if use_inputs:
            filename_key = input("yaml filename key value: ")
            filepath = config["filepaths"][filename_key]
        else:
            filepath = config["filepaths"]["text_file"]

        options["text"] = "create cards based on this text: \n"
        options["text"] += file_handler.read_file(filepath)

    return options


@retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
def generate_cards(options, config, prompts, chunk):
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

    filled_prompt = (
        prompts["generate_flashcards"]
        .replace("{{topic}}", options["topic"])
        .replace("{{text}}", chunk)
        .replace("{{card_amount}}", options["card_amount"])
    )
    print(f'''topic:{options["topic"]}, card amount: {options["card_amount"]}''')
    cards_to_add_response = ai_handler.prompt_ai(filled_prompt, model=config["model"])
    raw_json_str = file_handler.extract_json(
        cards_to_add_response
    )  # extract the json part of LLM response
    list_of_cards_dicts = file_handler.format_and_split_cards(raw_json_str)
    filename = file_handler.append_to_json_file(
        list_of_cards_dicts, options["topic"], options["deck_name"]
    )

    # if config["simple_reply_format"]: #add enums for different response types?
    #     cleaned_card_json_str = file_handler.clean_malformed_json(raw_json_str)
    #     deck_dict = file_handler.text_to_dict(cards_to_add) #extract the json part of LLM response
    #     if not deck_dict:
    #         raise Exception
    #     filename = file_handler.change_to_json_format(cleaned_card_json_str, options["topic"], options["deck_name"])
    #     if not filename:
    #         raise Exception

    return filename
