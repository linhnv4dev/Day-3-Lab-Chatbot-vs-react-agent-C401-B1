import os
import sys
import unittest


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class FakeChatbotRunner:
    def __init__(self):
        self.calls = []

    def ask(self, prompt, system_prompt=None):
        self.calls.append({"prompt": prompt, "system_prompt": system_prompt})
        return f"chatbot::{prompt}"


class FakeAgentRunner:
    def __init__(self):
        self.calls = []

    def run(self, prompt):
        self.calls.append({"prompt": prompt})
        return f"agent::{prompt}"


class RunPromptsTests(unittest.TestCase):
    def test_resolve_prompts_keeps_requested_order(self):
        from run_prompts import resolve_prompts

        prompts = resolve_prompts(["budget_bundle", "multi_step_checkout"])

        self.assertEqual(
            [item["id"] for item in prompts],
            ["budget_bundle", "multi_step_checkout"],
        )

    def test_run_comparison_dispatches_to_chatbot(self):
        from run_prompts import run_comparison

        fake_runner = FakeChatbotRunner()

        results = run_comparison(
            mode="chatbot",
            prompt_ids=["multi_step_checkout"],
            runner=fake_runner,
        )

        self.assertEqual(len(fake_runner.calls), 1)
        self.assertEqual(fake_runner.calls[0]["prompt"], results[0]["prompt"])
        self.assertIsNotNone(fake_runner.calls[0]["system_prompt"])
        self.assertEqual(results[0]["response"], f"chatbot::{results[0]['prompt']}")

    def test_run_comparison_dispatches_to_agent(self):
        from run_prompts import run_comparison

        fake_runner = FakeAgentRunner()

        results = run_comparison(
            mode="agent",
            prompt_ids=["budget_bundle"],
            runner=fake_runner,
        )

        self.assertEqual(fake_runner.calls, [{"prompt": results[0]["prompt"]}])
        self.assertEqual(results[0]["response"], f"agent::{results[0]['prompt']}")


if __name__ == "__main__":
    unittest.main()
