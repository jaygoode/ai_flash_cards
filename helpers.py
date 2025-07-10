def get_settings(use_inputs, config, file_handler):
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

def generate_cards(options, config, prompts, anki_api_handler, file_handler, ai_handler):
    filled_prompt = (
        prompts["generate_flashcards"]
        .replace("{{topic}}", options["topic"])
        .replace("{{text}}", chunk)
        .replace("{{card_amount}}", options["card_amount"])
    )
    cards_to_add = ai_handler.prompt_ai(filled_prompt, model=config["model"])

    raw_json_str = file_handler.extract_json(cards_to_add) #extract the json part of LLM response

    if not raw_json_str:
        None

    cleaned_card_json_str = file_handler.clean_malformed_json(raw_json_str) 
    list_of_cards_dicts = file_handler.format_and_split_cards(raw_json_str) 
    breakpoint()
    filename = file_handler.append_to_json_file(list_of_cards_dicts, options["topic"], options["deck_name"])
    if not filename:
        None
    anki_api_handler.add_cards(options["deck_name"], file_handler.read_json_file(filename))