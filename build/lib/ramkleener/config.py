import json
import os
from pathlib import Path

from ramkleener.lists import NEVER_KILL_DEFAULT, SAFE_TO_KILL

# Config loader and helper utilities for ramkleener.
# Default values used when config file is missing or invalid.
# ── Default config values ────────────────────────────────────
DEFAULT_CONFIG = {
    "user_protected": [],
    "user_kill_list": [],
    "threshold_mb": 100
}

CONFIG_DIR  = Path.home() / ".ramkleener"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config() -> dict:
    """
    Reads config.json if it exists.
    If missing, corrupted, or wrong type, returns DEFAULT_CONFIG silently.
    """
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # FIX 1: Ensure data is actually a dictionary
        if not isinstance(data, dict):
            return DEFAULT_CONFIG.copy()

        # Fill in any missing keys with defaults
        for key, value in DEFAULT_CONFIG.items():
            if key not in data:
                data[key] = value

        return data

    except (json.JSONDecodeError, OSError):
        return DEFAULT_CONFIG.copy()


def save_config(config: dict) -> bool:
    """
    Writes config to ~/.ramkleener/config.json.
    Creates the directory if it doesn't exist.
    """
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        return True

    except OSError:
        return False


def get_protected_set(config: dict) -> set:
    """
    Returns NEVER_KILL_DEFAULT + valid user_protected entries.
    """
    # Merge built-in protected names with user-provided overrides.
    raw_list = config.get("user_protected", [])
    if not isinstance(raw_list, list):
        raw_list = []
        
    user = {str(name).lower() for name in raw_list}
    return NEVER_KILL_DEFAULT | user


def get_kill_set(config: dict) -> set:
    """
    Returns SAFE_TO_KILL + valid user_kill_list entries.
    """
    # Include extra kill candidates from the user's config.
    raw_list = config.get("user_kill_list", [])
    if not isinstance(raw_list, list):
        raw_list = []
        
    user = {str(name).lower() for name in raw_list}
    return SAFE_TO_KILL | user


def get_threshold(config: dict) -> float:
    """
    Returns threshold_mb from config.
    Falls back to default if missing or invalid.
    """
    try:
        return float(config.get("threshold_mb", DEFAULT_CONFIG["threshold_mb"]))
    except (TypeError, ValueError):
        return float(DEFAULT_CONFIG["threshold_mb"])