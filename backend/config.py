import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (one level above backend/)
_root = Path(__file__).parent.parent
load_dotenv(_root / ".env")

# --- Groq ---
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL: str = "llama-3.3-70b-versatile"

# --- MongoDB Atlas (optional) ---
# Set MONGODB_URI to an Atlas connection string to persist saved graphs/gaps.
# When unset, persistence falls back to an in-memory store (no-op across restarts).
MONGODB_URI: str = os.getenv("MONGODB_URI", "")
MONGODB_DB: str = os.getenv("MONGODB_DB", "anti_discovery_engine")

# --- Paper source: OpenAlex (no API key required) ---
# OpenAlex is fully open — no key, no signup. Providing an email puts requests
# in the faster "polite pool" (https://docs.openalex.org/how-to-use-the-api/rate-limits-and-authentication).
OPENALEX_BASE_URL: str = "https://api.openalex.org/works"
OPENALEX_MAILTO: str = os.getenv("OPENALEX_MAILTO", "calloolooh@gmail.com")
# Only keep OpenAlex concepts at or above this relevance score (0-1) and level.
OPENALEX_MIN_CONCEPT_SCORE: float = 0.3
OPENALEX_MIN_CONCEPT_LEVEL: int = 1  # skip ultra-generic level-0 roots
# Polite pool allows ~10 req/s; a small delay keeps us well within limits.
S2_RATE_LIMIT_DELAY: float = 0.2

# --- Graph builder ---
MIN_PAPER_COUNT: int = 2          # prune nodes below this
TARGET_MIN_NODES: int = 500
TARGET_MAX_NODES: int = 2000
TARGET_MIN_EDGES: int = 3000
TARGET_MAX_EDGES: int = 8000

# --- Paths ---
BACKEND_DIR: Path = Path(__file__).parent
DATA_DIR: Path = _root / "data"
CACHE_DIR: Path = BACKEND_DIR / "data" / "cache"
HISTORICAL_GAPS_PATH: Path = DATA_DIR / "historical_gaps.json"
EXAMPLE_GRAPH_PATH: Path = DATA_DIR / "example_graph.json"

CACHE_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# --- CORS ---
CORS_ORIGINS: list[str] = ["http://localhost:5173"]
