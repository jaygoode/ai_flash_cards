import os
import subprocess
import anki_handler
import file_handler
import helpers
from typing import Dict
import platform 
import glob 

def create_from_deck_json(config, os_name):
    print(
        f"Using readymade deck: {config['options']['readymade_deck_name']}. No new cards will be created."
    )
    cards = file_handler.read_json_file(
        config["filepaths"][os_name]["decks_path"] + config["options"]["readymade_deck_name"] + ".json"
    )
    if not cards:
        print("No cards found in the readymade deck file.")
        exit(1)
    print(f"Cards found: {len(cards)}")
    print(f"Adding cards to deck: {config['options']['readymade_deck_name']}")
    anki_handler.add_cards(config['options']["readymade_deck_name"], cards)

def create_deck_with_ai(config):
    options: Dict[str, str] = helpers.get_settings(config["options"]["use_inputs"], config)
    filename:str = ""
    for chunk in file_handler.chunk_text(options["topic"]):
        filename = helpers.generate_cards(options, config, prompts, chunk)
    cards = file_handler.read_json_file(filename)
    anki_handler.add_cards(options["deck_name"], cards)

    print(
        f'''card creation done! deck name: {options["deck_name"]}, topic: {options["topic"]}, cards created: {len(cards)}'''
    )



if __name__ == "__main__":
    os_name = platform.system().lower()
    config = file_handler.read_yaml_file("config.yaml")
    prompts = file_handler.read_yaml_file(config["filepaths"][os_name]["prompts_fp"])
    anki_handler.start_anki(os_name, config)

    if config["options"]["use_readymade_deck"].lower() in ["yes", "y"]:
        create_from_deck_json(config, os_name)
    else:    
        create_from_deck_json(config, os_name)
