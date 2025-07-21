
import requests

ANKI_CONNECT_URL = "http://localhost:8765"
from typing import Dict, Any

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
