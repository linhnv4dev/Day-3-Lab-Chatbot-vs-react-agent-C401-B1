import argparse
import sys

from src.chatbot import ChatbotBaseline
from src.core.provider_factory import create_provider


DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful chatbot. Answer clearly and directly. "
    "Do not simulate tool usage or hidden reasoning steps."
)


def print_answer(answer: str, stream=None):
    stream = stream or sys.stdout
    message = f"Assistant: {answer}\n"

    try:
        stream.write(message)
    except UnicodeEncodeError:
        if hasattr(stream, "buffer"):
            stream.buffer.write(message.encode("utf-8"))
        else:
            raise
    finally:
        stream.flush()


def main():
    parser = argparse.ArgumentParser(description="Phase 1 chatbot baseline")
    parser.add_argument(
        "prompt",
        nargs="?",
        help="User prompt for the chatbot baseline",
    )
    args = parser.parse_args()

    prompt = args.prompt or input("User: ").strip()
    if not prompt:
        raise ValueError("Prompt cannot be empty.")

    provider = create_provider()
    chatbot = ChatbotBaseline(llm=provider)
    answer = chatbot.ask(prompt, system_prompt=DEFAULT_SYSTEM_PROMPT)

    print_answer(answer)


if __name__ == "__main__":
    main()
