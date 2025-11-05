import os


def get_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


# ThingSpeak configuration
# IMPORTANT: Do not hardcode your write key; supply via environment variable.
THINGSPEAK_WRITE_API: str = get_env("THINGSPEAK_WRITE_API", None)
THINGSPEAK_READ_API: str | None = os.getenv("THINGSPEAK_READ_API")
THINGSPEAK_CHANNEL_ID: str | None = os.getenv("THINGSPEAK_CHANNEL_ID", "3148931")
THINGSPEAK_URL: str = os.getenv("THINGSPEAK_URL", "https://api.thingspeak.com/update")

# Camera configuration
CAMERA_INDEX: int = int(os.getenv("CAMERA_INDEX", "0"))

# Detection configuration
SLOT_BOXES = [
    (50, 100, 200, 250),   # Slot 1
    (250, 100, 400, 250),  # Slot 2
    (450, 100, 600, 250),  # Slot 3
    (650, 100, 800, 250),  # Slot 4
]
FILLED_THRESHOLD: float = float(os.getenv("FILLED_THRESHOLD", "0.4"))

# Update intervals (seconds)
DETECT_INTERVAL: float = float(os.getenv("DETECT_INTERVAL", "0.2"))
THINGSPEAK_MIN_INTERVAL: int = int(os.getenv("THINGSPEAK_MIN_INTERVAL", "15"))

# Visualization toggle (for local debug)
SHOW_WINDOW: bool = os.getenv("SHOW_WINDOW", "0") in ("1", "true", "True")


