import os
from dotenv import load_dotenv


OPENAI_COMPATIBLE_PROVIDERS = {"openai", "nine_router"}


def create_provider():
    """
    Build the configured LLM provider from environment variables.

    Supported providers:
    - openai
    - nine_router (OpenAI-compatible gateway)
    - google
    - local
    """
    load_dotenv()

    provider_name = os.getenv("DEFAULT_PROVIDER", "openai").strip().lower()
    model_name = os.getenv("DEFAULT_MODEL", "gpt-4o").strip()

    if provider_name in OPENAI_COMPATIBLE_PROVIDERS:
        from src.core.openai_provider import OpenAIProvider

        api_key = os.getenv("API_KEY") or os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("BASE_URL")

        return OpenAIProvider(
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
            provider_name=provider_name,
        )

    if provider_name == "google":
        from src.core.gemini_provider import GeminiProvider

        return GeminiProvider(
            model_name=model_name,
            api_key=os.getenv("GEMINI_API_KEY"),
        )

    if provider_name == "local":
        from src.core.local_provider import LocalProvider

        return LocalProvider(
            model_path=os.getenv("LOCAL_MODEL_PATH", "./models/Phi-3-mini-4k-instruct-q4.gguf")
        )

    raise ValueError(
        "Unsupported DEFAULT_PROVIDER. Expected one of: "
        "openai, nine_router, google, local."
    )
