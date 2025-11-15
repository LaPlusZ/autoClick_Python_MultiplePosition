import os
import json

PRESETS_FILE = "presets.json"

def load_presets():
    """Loads all presets from the JSON file and returns them."""
    presets = {}
    if os.path.exists(PRESETS_FILE):
        with open(PRESETS_FILE, "r") as file:
            try:
                presets = json.load(file)
            except json.JSONDecodeError:
                presets = {"default": []}  # Handle empty or corrupt file
    # Handles migration from the old single-file format
    elif os.path.exists("positions.json"):
        with open("positions.json", "r") as file:
            old_positions = json.load(file)
            presets = {"default": old_positions}
        save_presets(presets)  # Save in the new format
        os.remove("positions.json")

    if not presets:
        presets = {"default": []}
    
    return presets


def save_presets(presets_data):
    """Saves the entire provided presets dictionary to the file."""
    with open(PRESETS_FILE, "w") as file:
        json.dump(presets_data, file, indent=4)