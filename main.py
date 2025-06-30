import ai_handler
import file_handler
import anki_api_handler
import subprocess
import os


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
        filename_key = input("yaml filename key value: ")
        filepath = config["filepaths"][filename_key]
        text = "create cards based on this text: \n"
        text += file_handler.read_file(filepath)
        chunked_text = file_handler.chunk_text(text, model_name=config["model"])

    # cards_to_add = [
    # {"front": "Capital of France?", "back": "Paris", "tags": topic},
    # {"front": "2 + 2", "back": "4", "tags": topic},
    # ]

    cards_total = []  # fix this
    for text_chunk in chunked_text:
        filled_prompt = (
            prompts["generate_flashcards"]
            .replace("{{topic}}", topic)
            .replace("{{text}}", text)
            .replace("{{card_amount}}", card_amount)
        )
        cards_to_add = ai_handler.prompt_ai(filled_prompt, model=config["model"])
        cards_total.append(cards_to_add)
    file_handler.create_json_file(cards_to_add)
    anki_api_handler.add_cards(deck_name, file_handler.read_json_file("cards.json"))
