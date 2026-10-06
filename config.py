import os
from pathlib import Path

# Configuration de l'API
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8080")

# Chemins de l'application
BASE_DIR = Path(__file__).resolve().parent
UI_DIR = BASE_DIR / "ui"
