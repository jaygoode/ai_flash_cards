import ai_handler
import file_handler
import anki_api_handler
import subprocess
import os
import re

if __name__ == "__main__":
    config = file_handler.read_yaml_file("config.yaml")
    prompts = file_handler.read_yaml_file(config["filepaths"]["prompts_fp"])

    if (
        os.path.exists(config["filepaths"]["anki_path"])
        and not file_handler.is_anki_running()
    ):
        subprocess.Popen([config["filepaths"]["anki_path"]])
        print("Anki launched!")
    else:
        print("Opening Anki failed. Might already be running.")

    use_inputs = False

    if use_inputs:
        topic = input("deck topic(s): ")
        use_file = input("use file to base cards on? (Y/N): ")
        deck_name = input("deck name: ")
        card_amount = str(input("amount of cards to generate: "))
        text = input(
            "further description for what the cards should be based on (or leave empty): "
        )
    else:
        topic = config["options"]["topic"]
        use_file = config["options"]["use_file"]
        deck_name = config["options"]["deck_name"]
        card_amount = config["options"]["card_amount"]
        text = config["options"]["text"]


    if use_file.lower() is any(["yes", "y"]):
        if use_inputs:
            filename_key = input("yaml filename key value: ")
            filepath = config["filepaths"][filename_key]
        else:
            filepath = config["filepaths"]["text_file"]

        text = "create cards based on this text: \n"
        text += file_handler.read_file(filepath)

    # cards_to_add = [
    # {"front": "Capital of France?", "back": "Paris", "tags": topic},
    # {"front": "2 + 2", "back": "4", "tags": topic},
    # ]

    json_str_cards = []
    #calculate the amount of cards needed per chunk, we cant use yield in this case.. prompt ai should maybe just generate one card per prompt. instead of generating 20 and one has a structure error which crashes the whole batch., or we split them before sending to json formatter
    for chunk in file_handler.chunk_text(text):
        filled_prompt = (
            prompts["generate_flashcards"]
            .replace("{{topic}}", topic)
            .replace("{{text}}", chunk)
            .replace("{{card_amount}}", card_amount)
        )
        cards_to_add = ai_handler.prompt_ai(filled_prompt, model=config["model"])

        raw_json_str = file_handler.extract_json(cards_to_add) #extract the json part of LLM response

        if not raw_json_str:
            continue

        cleaned_card_json_str = file_handler.clean_malformed_json(raw_json_str) 
        list_of_cards_dicts = file_handler.format_and_split_cards(raw_json_str) 

        filename = file_handler.append_to_json_file(list_of_cards_dicts, topic, deck_name)
        if not filename:
            continue
        anki_api_handler.add_cards(deck_name, file_handler.read_json_file(filename))
        
        # if config["simple_reply_format"]: #add enums for different response types?
        #     deck_dict = file_handler.text_to_dict(cards_to_add) #extract the json part of LLM response
        #     if not deck_dict:
        #         continue
        #     filename = file_handler.change_to_json_format(cleaned_card_json_str, topic, deck_name)
        #     if not filename:
        #         continue
        #     anki_api_handler.add_cards(deck_name, file_handler.read_json_file(filename))

    print("card creation done!")
