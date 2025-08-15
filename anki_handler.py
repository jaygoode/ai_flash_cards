
import requests
import platform
import re
import os
from typing import Dict, Any

ANKI_CONNECT_URL = "http://localhost:8765"

def get_latest_anki_url() -> str:
    url = "https://api.github.com/repos/ankitects/anki/releases/latest"
    resp = requests.get(url)
    resp.raise_for_status()
    release = resp.json()
    
    # Determine OS-specific filename pattern
    system = platform.system()
    pattern = {
        "Windows": r"anki-launcher-.*-windows\.exe$",
        "Linux":   r"anki-launcher-.*-linux\.tar\.zst$",
        "Darwin":  r"anki-launcher-.*-mac\.dmg$",
    }.get(system)
    if not pattern:
        raise RuntimeError(f"No download pattern for OS: {system}")

    # Look for the matching download URL
    for asset in release["assets"]:
        name = asset.get("name", "")
        if re.search(pattern, name):
            return asset["browser_download_url"]
    raise RuntimeError("No matching Anki asset found")

def download_anki_installation_file(dest_folder: str) -> str:
    url = get_latest_anki_url()
    filename = os.path.basename(url)
    path = os.path.join(dest_folder, filename)
    print(f"Downloading {filename} from {url}...")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return path

def invoke(action: str, params: Dict[str, Any] = {}) -> Dict[str, Any]:
    try:
        return requests.post(
            ANKI_CONNECT_URL, json={"action": action, "version": 6, "params": params}
        ).json()
    except Exception:
        print("anki api invoke failed.")
        raise Exception("Failed to connect to Anki Connect API. Is Anki running?")


def ensure_deck_exists(deck_name: str):
    existing_decks = invoke("deckNames")["result"]
    if deck_name not in existing_decks:
        invoke("createDeck", {"deck": deck_name})
        print(f"Created deck: {deck_name}")
    else:
        print(f"Deck already exists: {deck_name}")


def add_cards(deck_name: str, cards: list[dict[str, str]]):
    ensure_deck_exists(deck_name)
    for card in cards:
        try:
            note: dict[str, Any] = {
                "deckName": deck_name,
                "modelName": "Basic",
                "fields": {"Front": card["front"], "Back": card["back"]},
                "tags": card.get("tags", []),
            }
            response = invoke("addNote", {"note": note})
            if response.get("error"):
                print(f"Failed to add card: {card['front']} → {response['error']}")
            else:
                print(f"Added card: {card['front']}")
        except Exception as err:
            print(f"failed to add card - {err}")
