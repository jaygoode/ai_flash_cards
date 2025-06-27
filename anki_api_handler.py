import requests
import json

ANKI_CONNECT_URL = "http://localhost:8765"

def invoke(action, params={}):
    return requests.post(ANKI_CONNECT_URL, json={
        "action": action,
        "version": 6,
        "params": params
    }).json()

def ensure_deck_exists(deck_name):
    existing_decks = invoke("deckNames")["result"]
    if deck_name not in existing_decks:
        invoke("createDeck", {"deck": deck_name})
        print(f"Created deck: {deck_name}")
    else:
        print(f"Deck already exists: {deck_name}")

def add_cards(deck_name, cards):
    ensure_deck_exists(deck_name)
    for card in cards:
        note = {
            "deckName": deck_name,
            "modelName": "Basic",
            "fields": {
                "Front": card["front"],
                "Back": card["back"]
            },
            "tags": card.get("tags", [])
        }
        response = invoke("addNote", {"note": note})
        if response.get("error"):
            print(f"Failed to add card: {card['front']} → {response['error']}")
        else:
            print(f"Added card: {card['front']}")

# Example usage:
cards_to_add = [
    {"front": "Capital of France?", "back": "Paris", "tags": ["geography"]},
    {"front": "2 + 2", "back": "4", "tags": ["math"]},
    {"front": "Python creator?", "back": "Guido van Rossum"}
]

