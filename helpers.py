def get_settings(use_inputs, config, file_handler):
    options = {}
    if use_inputs:
        options["topic"] = input("deck topic(s): ")
        options["use_file"] = input("use file to base cards on? (Y/N): ")
        options["deck_name"] = input("deck name: ")
        options["card_amount"] = str(input("amount of cards to generate: "))
        options["text"] = input(
            "further description for what the cards should be based on (or leave empty): "
        )
    else:
        options["topic"] = config["options"]["topic"]
        options["use_file"] = config["options"]["use_file"]
        options["deck_name"] = config["options"]["deck_name"]
        options["card_amount"] = config["options"]["card_amount"]
        options["text"] = config["options"]["text"]

    if options["use_file"].lower() in ["yes", "y"]:
        if use_inputs:
            filename_key = input("yaml filename key value: ")
            filepath = config["filepaths"][filename_key]
        else:
            filepath = config["filepaths"]["text_file"]

        options["text"] = "create cards based on this text: \n"
        options["text"] += file_handler.read_file(filepath)

    return options