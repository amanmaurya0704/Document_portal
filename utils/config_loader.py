from pathlib import Path
import yaml

def load_config() -> dict:
    # Construct an absolute path to the config file
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config
