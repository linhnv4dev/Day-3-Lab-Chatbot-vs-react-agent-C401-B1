import os
import datetime
import argparse
import sys
from typing import Iterable, Optional

from promt import get_all_prompts, get_prompt_by_id
from src.agent.agent import ReActAgent
from src.chatbot import ChatbotBaseline
from src.core.provider_factory import create_provider
from src.tools.registry import get_tools


"""
python run_prompts.py --list-prompts
python run_prompts.py --mode chatbot
python run_prompts.py --mode chatbot --prompt-id multi_step_checkout
python run_prompts.py --mode chatbot --prompt-id multi_step_checkout --prompt-id budget_bundle
python run_prompts.py --mode agent --prompt-id multi_step_checkout
"""


CHATBOT_SYSTEM_PROMPT = (
    "You are a helpful chatbot. Answer clearly and directly. "
    "Do not simulate tool usage or hidden reasoning steps."
)


def safe_print(text: str, stream=None):
    stream = stream or sys.stdout
    try:
        stream.write(text + "\n")
    except UnicodeEncodeError:
        if hasattr(stream, "buffer"):
            stream.buffer.write((text + "\n").encode("utf-8"))
        else:
            raise
    finally:
        stream.flush()


def resolve_prompts(prompt_ids: Optional[Iterable[str]] = None):
    if not prompt_ids:
        return get_all_prompts()
    return [get_prompt_by_id(prompt_id) for prompt_id in prompt_ids]


def build_runner(mode: str, llm):
    if mode == "chatbot":
        return ChatbotBaseline(llm=llm)
    if mode == "agent":
        return ReActAgent(llm=llm, tools=get_tools())
    raise ValueError(f"Unsupported mode: {mode}")


def execute_prompt(mode: str, runner, prompt: str):
    if mode == "chatbot":
        return runner.ask(prompt, system_prompt=CHATBOT_SYSTEM_PROMPT)
    if mode == "agent":
        return runner.run(prompt)
    raise ValueError(f"Unsupported mode: {mode}")


def run_comparison(mode: str, prompt_ids=None, runner=None):
    selected_prompts = resolve_prompts(prompt_ids)
    active_runner = runner

    if active_runner is None:
        llm = create_provider()
        active_runner = build_runner(mode, llm)

    results = []
    for item in selected_prompts:
        response = execute_prompt(mode, active_runner, item["prompt"])
        history = getattr(active_runner, "history", None)
        if history is not None:
            history = list(history)
            
        results.append(
            {
                **item,
                "mode": mode,
                "response": response,
                "history": history,
            }
        )

    return results


def list_prompts():
    for item in get_all_prompts():
        safe_print(f"[{item['id']}] {item['label']}")
        safe_print(f"Prompt: {item['prompt']}")
        safe_print(f"Goal: {item['goal']}")
        safe_print("")


def main():
    parser = argparse.ArgumentParser(description="Run shared prompts in chatbot or agent mode.")
    parser.add_argument("--mode", choices=["chatbot", "agent"], required=False)
    parser.add_argument(
        "--prompt-id",
        action="append",
        dest="prompt_ids",
        help="Prompt id from promt.py. Repeat to run multiple prompts.",
    )
    parser.add_argument(
        "--list-prompts",
        action="store_true",
        help="List available prompt ids and exit.",
    )
    args = parser.parse_args()

    if args.list_prompts:
        list_prompts()
        return

    if not args.mode:
        parser.error("--mode is required unless --list-prompts is used.")

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, f"{args.mode}-{timestamp}.log")
    
    with open(log_file_path, "w", encoding="utf-8") as log_file:
        def log_and_print(text: str):
            safe_print(text)
            log_file.write(text + "\n")
            log_file.flush()

        log_and_print(f"Starting {args.mode} run at {timestamp}")
        log_and_print("=" * 50)

        results = run_comparison(mode=args.mode, prompt_ids=args.prompt_ids)

        for item in results:
            log_and_print(f"[{item['mode']}] {item['id']} - {item['label']}")
            log_and_print(f"User Prompt: {item['prompt']}")
            log_and_print("-" * 20 + " CONVERSATION " + "-" * 20)
            
            if item.get("history"):
                for step_idx, step in enumerate(item["history"], 1):
                    log_and_print(f"--- Step {step_idx} ---")
                    if 'thought_action' in step:
                        log_and_print(f"{step['thought_action']}")
                    if 'observation' in step:
                        log_and_print(f"Observation: {step['observation']}")
                        
            log_and_print("-" * 20 + " END CONVERSATION " + "-" * 20)
            log_and_print(f"Final Response: {item['response']}")
            log_and_print("=" * 50)
            log_and_print("")

    print(f"Run completed. Logs saved to: {log_file_path}")

if __name__ == "__main__":
    main()
