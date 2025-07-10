import requests
import json

ANKI_CONNECT_URL = "http://localhost:8765"


def invoke(action, params={}):
    try:
        return requests.post(
            ANKI_CONNECT_URL, json={"action": action, "version": 6, "params": params}
        ).json()
    except:
        print("anki api invoke failed.")


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
        try:
            note = {
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
 