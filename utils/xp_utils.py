import json
import os
import random

XP_FILE = "xp_data.json"

def load_xp_data():
    if os.path.exists(XP_FILE):
        with open(XP_FILE, "r") as f:
            return json.load(f)
    return {}

def save_xp_data(data):
    with open(XP_FILE, "w") as f:
        json.dump(data, f, indent=4)

def gain_xp():
    return random.randint(1, 5)
