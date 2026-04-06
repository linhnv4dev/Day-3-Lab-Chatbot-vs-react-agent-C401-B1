import ast
import re
from typing import List, Dict, Any, Optional
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger
from src.telemetry.metrics import tracker
from datetime import datetime

class ReActAgent:
    """
    SKELETON: A ReAct-style Agent that follows the Thought-Action-Observation loop.
    Students should implement the core loop logic and tool execution.
    """
    
    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.history = []

    def get_system_prompt(self) -> str:
        tool_descriptions = "\n".join([f"- {t['name']}: {t['description']}" for t in self.tools])
        current_date = datetime.now().strftime("%Y-%m-%d")
        return f"""You are a helpful AI assistant with access to several tools.
Below are the available tools:
{tool_descriptions}

Important: The current date is {current_date}. Keep this in mind when dealing with scheduling such as 'next week' or 'tomorrow'.

When you need to use a tool, you MUST use the following format:
Thought: short reasoning about the next step
Action: tool_name(arg_name="value", other_arg=123)
Observation: tool result
... repeat if needed
Final Answer: the final answer for the user
Rules:
- If you need a tool, output exactly one Action line.
- Do not invent tools that are not listed.
- After receiving an Observation, continue reasoning from that observation.
- If you already have enough information, output Final Answer.
        """

    def run(self, user_input: str) -> str:
        logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})

        self.history = []
        current_prompt = user_input
        steps = 0

        while steps < self.max_steps:
            result = self.llm.generate(current_prompt, system_prompt=self.get_system_prompt())
            content = result["content"].strip()

            tracker.track_request(
                provider=result.get("provider", "unknown"),
                model=self.llm.model_name,
                usage=result.get("usage", {}),
                latency_ms=result.get("latency_ms", 0),
            )

            logger.log_event(
                "AGENT_STEP",
                {
                    "step": steps + 1,
                    "llm_output": content,
                },
            )

            action = self._extract_action(content)
            if action:
                tool_name, raw_args = action
                logger.log_event(
                    "TOOL_CALL",
                    {
                        "step": steps + 1,
                        "tool_name": tool_name,
                        "raw_args": raw_args,
                    },
                )
                observation = self._execute_tool(tool_name, raw_args)
                logger.log_event(
                    "TOOL_RESULT",
                    {
                        "step": steps + 1,
                        "tool_name": tool_name,
                        "observation": observation,
                    },
                )
                self.history.append(
                    {
                        "thought_action": self._sanitize_action_content(content, tool_name, raw_args),
                        "observation": observation,
                    }
                )
                current_prompt = self._build_followup_prompt(user_input)
            else:
                final_answer = self._extract_final_answer(content)
                if final_answer:
                    logger.log_event(
                        "AGENT_END",
                        {
                            "steps": steps + 1,
                            "response": final_answer,
                            "status": "completed",
                        },
                    )
                    return final_answer

                self.history.append(
                    {
                        "thought_action": content,
                        "observation": "No action provided. Please either call one tool or return Final Answer.",
                    }
                )
                current_prompt = self._build_followup_prompt(user_input)

            steps += 1

        timeout_response = "Agent stopped because it reached max_steps without producing a Final Answer."
        logger.log_event(
            "AGENT_END",
            {
                "steps": steps,
                "response": timeout_response,
                "status": "max_steps_exceeded",
            },
        )
        return timeout_response

    def _execute_tool(self, tool_name: str, args: str) -> str:
        for tool in self.tools:
            if tool["name"] == tool_name:
                try:
                    parsed_args = self._parse_action_args(args)
                    parsed_args = self._normalize_tool_args(tool_name, parsed_args)
                    return tool["function"](**parsed_args)
                except Exception as exc:
                    return f"Tool {tool_name} failed: {exc}"
        return f"Tool {tool_name} not found."

    def _extract_final_answer(self, text: str) -> Optional[str]:
        match = re.search(r"Final Answer:\s*(.+)", text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def _extract_action(self, text: str) -> Optional[tuple[str, str]]:
        match = re.search(r"Action:\s*([a-zA-Z_][a-zA-Z0-9_]*)\((.*)\)", text)
        if not match:
            return None
        return match.group(1), match.group(2).strip()

    def _parse_action_args(self, raw_args: str) -> Dict[str, Any]:
        if not raw_args:
            return {}

        call_node = ast.parse(f"f({raw_args})", mode="eval").body
        if not isinstance(call_node, ast.Call):
            raise ValueError("Invalid action arguments.")

        if call_node.args:
            raise ValueError("Only keyword arguments are supported in Action.")

        parsed_args = {}
        for keyword in call_node.keywords:
            if keyword.arg is None:
                raise ValueError("Unsupported unpacked keyword arguments.")
            try:
                val = ast.literal_eval(keyword.value)
            except Exception:
                try:
                    code = compile(ast.Expression(keyword.value), filename="<ast>", mode="eval")
                    val = eval(code, {"__builtins__": {}})
                except Exception as eval_exc:
                    raise ValueError(f"Could not parse argument {keyword.arg}: {eval_exc}")
            parsed_args[keyword.arg] = val
        return parsed_args

    def _normalize_tool_args(self, tool_name: str, parsed_args: Dict[str, Any]) -> Dict[str, Any]:
        normalized_args = dict(parsed_args)
        return normalized_args

    def _build_followup_prompt(self, user_input: str) -> str:
        lines = [f"User Question: {user_input}", ""]
        for item in self.history:
            lines.append(item["thought_action"])
            lines.append(f"Observation: {item['observation']}")
            lines.append("")
        lines.append("Continue from the latest observation. Return either one Action or Final Answer.")
        return "\n".join(lines)

    def _sanitize_action_content(self, content: str, tool_name: str, raw_args: str) -> str:
        thought_match = re.search(r"Thought:\s*(.+?)(?:\nAction:|$)", content, flags=re.DOTALL)
        thought_line = "Thought: Continuing with the next tool step."
        if thought_match:
            thought_line = f"Thought: {thought_match.group(1).strip()}"
        return f"{thought_line}\nAction: {tool_name}({raw_args})"
