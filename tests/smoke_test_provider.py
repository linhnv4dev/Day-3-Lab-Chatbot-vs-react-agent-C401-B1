import os
import sys
from dotenv import load_dotenv


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.provider_factory import create_provider


def main():
    load_dotenv()

    provider = create_provider()
    prompt = input("You: ")

    print("--- Provider Smoke Test ---")
    print(f"Provider: {os.getenv('DEFAULT_PROVIDER')}")
    print(f"Model: {provider.model_name}")
    print(f"Prompt: {prompt}")

    result = provider.generate(prompt)
    print("Response:", result["content"])
    print("Usage:", result["usage"])
    print("Latency (ms):", result["latency_ms"])


if __name__ == "__main__":
    main()
