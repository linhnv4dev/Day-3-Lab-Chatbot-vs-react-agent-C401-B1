import os
import sys
import unittest


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.llm_provider import LLMProvider


class ScriptedProvider(LLMProvider):
    def __init__(self, responses):
        super().__init__(model_name="fake-agent-model", api_key=None)
        self.responses = list(responses)
        self.calls = []

    def generate(self, prompt, system_prompt=None):
        self.calls.append({"prompt": prompt, "system_prompt": system_prompt})
        content = self.responses.pop(0)
        return {
            "content": content,
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 12,
                "total_tokens": 22,
            },
            "latency_ms": 50,
            "provider": "fake-provider",
        }

    def stream(self, prompt, system_prompt=None):
        yield ""


class CaptureTracker:
    def __init__(self):
        self.calls = []

    def track_request(self, provider, model, usage, latency_ms):
        self.calls.append(
            {
                "provider": provider,
                "model": model,
                "usage": usage,
                "latency_ms": latency_ms,
            }
        )


class CaptureLogger:
    def __init__(self):
        self.events = []

    def log_event(self, event_type, data):
        self.events.append({"event_type": event_type, "data": data})


class ReActAgentTests(unittest.TestCase):
    def test_agent_returns_final_answer_without_tool(self):
        from src.agent.agent import ReActAgent

        llm = ScriptedProvider(
            [
                "Thought: This is simple.\nFinal Answer: Xin chao tu agent.",
            ]
        )

        agent = ReActAgent(llm=llm, tools=[], max_steps=3)
        answer = agent.run("Noi xin chao")

        self.assertEqual(answer, "Xin chao tu agent.")
        self.assertEqual(len(llm.calls), 1)
        self.assertIn("Final Answer", llm.calls[0]["system_prompt"])

    def test_agent_executes_tool_then_finishes(self):
        from src.agent.agent import ReActAgent
        from src.tools.registry import get_tools

        llm = ScriptedProvider(
            [
                (
                    "Thought: I need the stock first.\n"
                    "Action: check_stock(item_name=\"Sony WH-1000XM5\")"
                ),
                (
                    "Thought: I now know the inventory.\n"
                    "Final Answer: Sony WH-1000XM5 con 2 san pham trong kho."
                ),
            ]
        )

        agent = ReActAgent(llm=llm, tools=get_tools(), max_steps=3)
        answer = agent.run("Kiem tra ton kho Sony WH-1000XM5")

        self.assertEqual(answer, "Sony WH-1000XM5 con 2 san pham trong kho.")
        self.assertEqual(len(llm.calls), 2)
        self.assertIn("Observation: Stock for Sony WH-1000XM5: 2 units available.", llm.calls[1]["prompt"])
        self.assertNotIn("999", llm.calls[1]["prompt"])
        self.assertNotIn("Final Answer:", llm.calls[1]["prompt"])

    def test_agent_prioritizes_real_tool_execution_over_hallucinated_observation(self):
        from src.agent.agent import ReActAgent
        from src.tools.registry import get_tools

        llm = ScriptedProvider(
            [
                (
                    "Thought: I should check stock.\n"
                    "Action: check_stock(item_name=\"Sony WH-1000XM5\")\n"
                    "Observation: Stock: 999 units available\n"
                    "Final Answer: Sony WH-1000XM5 con 999 san pham."
                ),
                (
                    "Thought: I now trust the real tool output.\n"
                    "Final Answer: Sony WH-1000XM5 con 2 san pham trong kho."
                ),
            ]
        )

        agent = ReActAgent(llm=llm, tools=get_tools(), max_steps=3)
        answer = agent.run("Kiem tra ton kho Sony WH-1000XM5")

        self.assertEqual(answer, "Sony WH-1000XM5 con 2 san pham trong kho.")
        self.assertEqual(len(llm.calls), 2)
        self.assertIn("Observation: Stock for Sony WH-1000XM5: 2 units available.", llm.calls[1]["prompt"])

    def test_execute_tool_parses_keyword_arguments(self):
        from src.agent.agent import ReActAgent
        from src.tools.registry import get_tools

        agent = ReActAgent(llm=ScriptedProvider([]), tools=get_tools())
        result = agent._execute_tool("calc_shipping", "weight_kg=1.2, destination=\"Hanoi\"")

        self.assertIn("Shipping to Hanoi", result)

    def test_execute_tool_supports_common_argument_aliases(self):
        from src.agent.agent import ReActAgent
        from src.tools.registry import get_tools

        agent = ReActAgent(llm=ScriptedProvider([]), tools=get_tools())
        result = agent._execute_tool(
            "calc_shipping",
            "weight_kg=0.3, destination_city=\"Ho Chi Minh City\"",
        )

        self.assertIn("Shipping to Ho Chi Minh City", result)

    def test_agent_tracks_metrics_and_logs_steps(self):
        import src.agent.agent as agent_module
        from src.agent.agent import ReActAgent
        from src.tools.registry import get_tools

        original_tracker = agent_module.tracker
        original_logger = agent_module.logger
        capture_tracker = CaptureTracker()
        capture_logger = CaptureLogger()
        agent_module.tracker = capture_tracker
        agent_module.logger = capture_logger

        try:
            llm = ScriptedProvider(
                [
                    "Thought: Done.\nFinal Answer: Ket qua agent.",
                ]
            )
            agent = ReActAgent(llm=llm, tools=get_tools(), max_steps=2)

            answer = agent.run("Tra loi nhanh")

            self.assertEqual(answer, "Ket qua agent.")
            self.assertEqual(len(capture_tracker.calls), 1)
            self.assertEqual(
                [event["event_type"] for event in capture_logger.events],
                ["AGENT_START", "AGENT_STEP", "AGENT_END"],
            )
            self.assertEqual(capture_logger.events[-1]["data"]["response"], "Ket qua agent.")
        finally:
            agent_module.tracker = original_tracker
            agent_module.logger = original_logger

    def test_agent_logs_tool_call_and_result(self):
        import src.agent.agent as agent_module
        from src.agent.agent import ReActAgent
        from src.tools.registry import get_tools

        original_logger = agent_module.logger
        capture_logger = CaptureLogger()
        agent_module.logger = capture_logger

        try:
            llm = ScriptedProvider(
                [
                    "Thought: Need stock.\nAction: check_stock(item_name=\"Sony WH-1000XM5\")",
                    "Final Answer: Done.",
                ]
            )
            agent = ReActAgent(llm=llm, tools=get_tools(), max_steps=2)

            answer = agent.run("Kiem tra ton kho")

            self.assertEqual(answer, "Done.")
            self.assertIn("TOOL_CALL", [event["event_type"] for event in capture_logger.events])
            self.assertIn("TOOL_RESULT", [event["event_type"] for event in capture_logger.events])
        finally:
            agent_module.logger = original_logger


if __name__ == "__main__":
    unittest.main()
