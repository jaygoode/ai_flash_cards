import ai_handler
import file_handler
import anki_api_handler
import subprocess
import os
import re
import helpers

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
    options = helpers.get_settings(use_inputs, config, file_handler=file_handler)
    
    # cards_to_add = [
    # {"front": "Capital of France?", "back": "Paris", "tags": topic},
    # {"front": "2 + 2", "back": "4", "tags": topic},
    # ]

    for chunk in file_handler.chunk_text(options["topic"]):
        filename = helpers.generate_cards(options, config, prompts, chunk)
    cards = file_handler.read_json_file(filename)
    anki_api_handler.add_cards(options["deck_name"], cards)

        
        

    print(f"card creation done! deck name: {options["deck_name"]}, topic: {options["topic"]}, cards created: {len(cards)}")
