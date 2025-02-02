import json
from pathlib import Path

def load_provider_config():
    """Loads provider configuration from JSON file"""
    config_path = Path(__file__).parent.parent.parent / "data" / "providers.json"
    with open(config_path) as f:
        return json.load(f)
