import file_handler, ai_handler
from tenacity import retry, stop_after_attempt, wait_fixed

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

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def generate_cards(options, config, prompts, chunk):
    filled_prompt = (
        prompts["generate_flashcards"]
        .replace("{{topic}}", options["topic"])
        .replace("{{text}}", chunk)
        .replace("{{card_amount}}", options["card_amount"])
    )
    cards_to_add_response = ai_handler.prompt_ai(filled_prompt, model=config["model"])
    raw_json_str = file_handler.extract_json(cards_to_add_response) #extract the json part of LLM response

    list_of_cards_dicts = file_handler.format_and_split_cards(raw_json_str) 
    filename = file_handler.append_to_json_file(list_of_cards_dicts, options["topic"], options["deck_name"])
    
    # if config["simple_reply_format"]: #add enums for different response types?
    #     cleaned_card_json_str = file_handler.clean_malformed_json(raw_json_str) 
    #     deck_dict = file_handler.text_to_dict(cards_to_add) #extract the json part of LLM response
    #     if not deck_dict:
    #         raise Exception
    #     filename = file_handler.change_to_json_format(cleaned_card_json_str, options["topic"], options["deck_name"])
    #     if not filename:
    #         raise Exception
        
    return filename