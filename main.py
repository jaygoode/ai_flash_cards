import os
import subprocess

import anki_api_handler
import file_handler
import helpers
from typing import Dict

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

    if config["options"]["use_readymade_deck"].lower() in ["yes", "y"]:
        print(
            f"Using readymade deck: {config['options']['readymade_deck_name']}. No new cards will be created."
        )
        cards = file_handler.read_json_file(
            config["filepaths"]["readymade_deck_fp"]
        )
        if not cards:
            print("No cards found in the readymade deck file.")
            exit(1)
        print(f"Cards found: {len(cards)}")
        print(f"Adding cards to deck: {config['options']['readymade_deck_name']}")
        anki_api_handler.add_cards(config['options']["readymade_deck_name"], cards)
    else:    
        options: Dict[str, str] = helpers.get_settings(config["options"]["use_inputs"], config)
        filename:str = ""
        for chunk in file_handler.chunk_text(options["topic"]):
            filename = helpers.generate_cards(options, config, prompts, chunk)
        cards = file_handler.read_json_file(filename)
        anki_api_handler.add_cards(options["deck_name"], cards)

        print(
            f'''card creation done! deck name: {options["deck_name"]}, topic: {options["topic"]}, cards created: {len(cards)}'''
        )
