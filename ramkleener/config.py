# ============================================================
#  config.py — RamKleener Configuration Loader & Validator
#  v1.3 Safety Architecture: PROTECTED wins all conflicts.
# ============================================================

import json
import os
from pathlib import Path

# Importing the hardcoded sets from lists.py
from ramkleener.lists import PROTECTED, SAFE_TO_KILL

CONFIG_DIR = Path.home() / ".ramkleener"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "user_protected": [],
    "user_kill_list": [],
    "threshold_mb": 50
}

MIN_THRESHOLD_MB = 10


def ensure_config_exists():
    """Checks for config directory/file; creates defaults if missing."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
        except OSError as e:
            print(f"[config] ERROR: Could not create config file: {e}")


def load_config():
    """
    Reads config.json and enforces v1.3 Meta rules:
    1. Case-insensitivity and .exe normalization.
    2. Conflict check: PROTECTED takes priority over Kill List.
    3. Threshold clamping: Minimum 10 MB.
    """
    ensure_config_exists()

    # Default fallback if file is unreadable
    raw = DEFAULT_CONFIG.copy()

    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if isinstance(data, dict):
                    raw = data
            except json.JSONDecodeError:
                print("[config] WARNING: config.json is corrupted. Using defaults.")

    # 1. Process User Protected List
    user_protected = set()
    for name in raw.get("user_protected", []):
        # Cast to string to prevent crashes on non-string JSON values
        cleaned = str(name).lower().strip().removesuffix(".exe")
        user_protected.add(cleaned)

    # 2. Process User Kill List with Conflict Validation
    # Combined protection = Hardcoded + User Overrides
    combined_protected = PROTECTED | user_protected
    user_kill_list = set()

    for name in raw.get("user_kill_list", []):
        cleaned = str(name).lower().strip().removesuffix(".exe")
        
        # CORE RULE: If it's protected, it CANNOT be in the kill list
        if cleaned in combined_protected:
            print(f"[config] SAFETY TRIGGER: '{cleaned}' is PROTECTED. Ignoring kill request.")
        else:
            user_kill_list.add(cleaned)

    # 3. Threshold Clamping (v1.3 Meta: Minimum 10MB)
    raw_threshold = raw.get("threshold_mb", DEFAULT_CONFIG["threshold_mb"])
    
    try:
        threshold_mb = int(raw_threshold)
        if threshold_mb < MIN_THRESHOLD_MB:
            # We don't print a warning here to keep the UI clean, just silent clamp
            threshold_mb = MIN_THRESHOLD_MB
    except (ValueError, TypeError):
        threshold_mb = DEFAULT_CONFIG["threshold_mb"]

    return {
        "user_protected": user_protected,
        "user_kill_list": user_kill_list,
        "threshold_mb": threshold_mb
    }


def get_effective_lists(config):
    """
    Merges hardcoded lists with the validated user config.
    Used by scanner.py to decide what to flag and what to ignore.
    """
    effective_protected = PROTECTED | config["user_protected"]
    effective_kill_list = SAFE_TO_KILL | config["user_kill_list"]
    
    return effective_protected, effective_kill_list