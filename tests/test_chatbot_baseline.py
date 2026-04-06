import os
import sys
import unittest
from io import BytesIO


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.llm_provider import LLMProvider


class FakeProvider(LLMProvider):
    def __init__(self):
        super().__init__(model_name="fake-model", api_key=None)
        self.calls = []

    def generate(self, prompt, system_prompt=None):
        self.calls.append({"prompt": prompt, "system_prompt": system_prompt})
        return {
            "content": "baseline response",
            "usage": {
                "prompt_tokens": 11,
                "completion_tokens": 7,
                "total_tokens": 18,
            },
            "latency_ms": 123,
            "provider": "fake-provider",
        }

    def stream(self, prompt, system_prompt=None):
        yield "baseline response"


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


class FailingUnicodeStream:
    def __init__(self):
        self.buffer = BytesIO()

    def write(self, _text):
        raise UnicodeEncodeError("cp1252", "ấ", 0, 1, "cannot encode")

    def flush(self):
        pass


class ChatbotBaselineTests(unittest.TestCase):
    def test_chatbot_returns_model_output(self):
        from src.chatbot import ChatbotBaseline

        bot = ChatbotBaseline(llm=FakeProvider())

        answer = bot.ask("Xin chao", system_prompt="Tra loi ngan gon")

        self.assertEqual(answer, "baseline response")
        self.assertEqual(
            bot.llm.calls,
            [{"prompt": "Xin chao", "system_prompt": "Tra loi ngan gon"}],
        )

    def test_chatbot_tracks_request_metrics(self):
        import src.chatbot as chatbot_module
        from src.chatbot import ChatbotBaseline

        original_tracker = chatbot_module.tracker
        original_logger = chatbot_module.logger
        capture_tracker = CaptureTracker()
        capture_logger = CaptureLogger()

        chatbot_module.tracker = capture_tracker
        chatbot_module.logger = capture_logger
        try:
            bot = ChatbotBaseline(llm=FakeProvider())

            answer = bot.ask("Kiem tra metric")

            self.assertEqual(answer, "baseline response")
            self.assertEqual(len(capture_tracker.calls), 1)
            self.assertEqual(
                capture_tracker.calls[0],
                {
                    "provider": "fake-provider",
                    "model": "fake-model",
                    "usage": {
                        "prompt_tokens": 11,
                        "completion_tokens": 7,
                        "total_tokens": 18,
                    },
                    "latency_ms": 123,
                },
            )
            self.assertEqual(
                [event["event_type"] for event in capture_logger.events],
                ["CHATBOT_START", "CHATBOT_END"],
            )
            self.assertEqual(
                capture_logger.events[1]["data"]["response"],
                "baseline response",
            )
        finally:
            chatbot_module.tracker = original_tracker
            chatbot_module.logger = original_logger

    def test_cli_print_answer_falls_back_for_unicode_output(self):
        import chatbot as chatbot_cli

        stream = FailingUnicodeStream()

        chatbot_cli.print_answer("Xin chào, rất vui được gặp bạn.", stream=stream)

        self.assertIn(
            "Assistant: Xin chào, rất vui được gặp bạn.",
            stream.buffer.getvalue().decode("utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
