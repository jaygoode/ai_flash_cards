import ai_handler
import file_handler
import anki_api_handler
import subprocess
import os


if __name__ == "__main__":
    config = file_handler.read_yaml_file("config.yaml")
    prompts = file_handler.read_yaml_file(config["prompts_fp"])

    if os.path.exists(config["anki_path"]) and not file_handler.is_anki_running():
        subprocess.Popen([config["anki_path"]])
        print("Anki launched!")
    else:
        print("Opening Anki failed. Might already be running.")


    #options
    # topic = input("What topic do you want to base the cards on? (leave empty if you want to use another option for generation): ") # just an input?
    topic = "testingtopic"
    # use_file = input("use file to base cards on? (Y/N): ")
    use_file = "n"

    text = "None"
    if use_file.lower() is any(["yes", "y"]):
        filename_key = input("yaml filename key value: ")
        text = config[filename_key]

    # deck_name = input("deck name: ")
    deck_name = "test"

    # cards_to_add = [
    # {"front": "Capital of France?", "back": "Paris", "tags": topic},
    # {"front": "2 + 2", "back": "4", "tags": topic},
    # {"front": "Python creator?", "back": "Guido van Rossum", "tags": topic}
    # ]

    filled_prompt = prompts["generate_flashcards"].replace("{{topic}}", topic).replace("{{text}}", text)
    cards_to_add = ai_handler.prompt_ai(filled_prompt, model=config["model"])
    breakpoint()
    json_format = file_handler.create_json_file(cards_to_add)
    anki_api_handler.add_cards(deck_name, cards_to_add)