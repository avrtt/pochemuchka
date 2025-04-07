from dataclasses import dataclass, field
import json
import os
from utils_general import parse_bool

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMP_SCRIPTS_DIR = os.environ.get(
    "POCHEMUCHKA_TEMP_SCRIPTS_DIR", os.path.join(BASE_DIR, "temp_scripts")
)
SAVE_PROMPTS_LOCALLY = os.environ.get("POCHEMUCHKA_SAVE_PROMPTS_LOCALLY", False)
ENVIRONMENT = os.environ.get("POCHEMUCHKA_ENVIRONMENT", "prod")
DEFAULT_MAX_BUDGET = os.environ.get("POCHEMUCHKA_DEFAULT_MAX_BUDGET", 16000)
DEFAULT_SAMPLE_MIN_BUDGET = os.environ.get("POCHEMUCHKA_DEFAULT_ANSWER_BUDGET", 3000)
DEFAULT_PROMPT_BUDGET = os.environ.get(
    "POCHEMUCHKA_DEFAULT_PROMPT_BUDGET", DEFAULT_MAX_BUDGET - DEFAULT_SAMPLE_MIN_BUDGET
)
EXPECTED_MIN_BUDGET_FOR_VALUABLE_INPUT = os.environ.get(
    "POCHEMUCHKA_EXPECTED_MIN_BUDGET_FOR_VALUABLE_INPUT", 100
)
SAFE_GAP_TOKENS: int = os.environ.get("POCHEMUCHKA_SAFE_GAP_TOKENS", 100)
SAFE_GAP_PER_MSG: int = os.environ.get("POCHEMUCHKA_SAFE_GAP_PER_MSG", 4)
DEFAULT_ENCODING = "cl100k_base"
USE_API_SERVICE = parse_bool(os.environ.get("POCHEMUCHKA_USE_API_SERVICE", True))
POCHEMUCHKA_API_URI = os.environ.get("POCHEMUCHKA_API_URI")
CACHE_PROMPT_FOR_EACH_SECONDS = int(
    os.environ.get("POCHEMUCHKA_CACHE_PROMPT_FOR_EACH_SECONDS", 5 * 60)
)
RECEIVE_PROMPT_FROM_SERVER = parse_bool(
    os.environ.get("POCHEMUCHKA_RECEIVE_PROMPT_FROM_SERVER", True)
)
PIPE_PROMPTS = {}
FALLBACK_MODELS = []

@dataclass
class Secrets:
    API_TOKEN: str = field(default_factory=lambda: os.getenv("POCHEMUCHKA_API_TOKEN"))
    OPENAI_API_KEY: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    CLAUDE_API_KEY: str = field(default_factory=lambda: os.getenv("CLAUDE_API_KEY"))
    GEMINI_API_KEY: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY"))
    NEBIUS_API_KEY: str = field(default_factory=lambda: os.getenv("NEBIUS_API_KEY"))
    CUSTOM_API_KEY: str = field(default_factory=lambda: os.getenv("CUSTOM_API_KEY"))
    OPENAI_ORG: str = field(default_factory=lambda: os.getenv("OPENAI_ORG"))
    azure_keys: dict = field(
        default_factory=lambda: json.loads(
            os.getenv("azure_keys", os.getenv("AZURE_OPENAI_KEYS", os.getenv("AZURE_KEYS", "{}")))
        )
    )
