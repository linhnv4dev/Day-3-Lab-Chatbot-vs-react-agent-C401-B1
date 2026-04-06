import os
import sys
import unittest


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ToolsRegistryTests(unittest.TestCase):
    def test_get_tools_exposes_clear_tool_metadata(self):
        from src.tools.registry import get_tools

        tools = get_tools()

        self.assertGreaterEqual(len(tools), 5)
        tool_names = {tool["name"] for tool in tools}
        self.assertEqual(
            tool_names,
            {
                "find_product",
                "find_cheapest_product",
                "check_stock",
                "get_discount",
                "calc_shipping",
            },
        )

        for tool in tools:
            self.assertIn("description", tool)
            self.assertTrue(tool["description"].strip())
            self.assertIn("function", tool)
            self.assertTrue(callable(tool["function"]))

    def test_find_cheapest_product_returns_laptop_option(self):
        from src.tools.registry import execute_tool

        result = execute_tool("find_cheapest_product", category="laptop")

        self.assertIn("Laptop", result)
        self.assertIn("price", result.lower())

    def test_check_stock_reports_available_quantity(self):
        from src.tools.registry import execute_tool

        result = execute_tool("check_stock", item_name="Sony WH-1000XM5")

        self.assertIn("Sony WH-1000XM5", result)
        self.assertIn("stock", result.lower())

    def test_get_discount_returns_known_coupon(self):
        from src.tools.registry import execute_tool

        result = execute_tool("get_discount", coupon_code="WINNER")

        self.assertIn("WINNER", result)
        self.assertIn("10%", result)

    def test_calc_shipping_returns_hanoi_shipping_cost(self):
        from src.tools.registry import execute_tool

        result = execute_tool("calc_shipping", weight_kg=1.2, destination="Hanoi")

        self.assertIn("Hanoi", result)
        self.assertIn("shipping", result.lower())

    def test_execute_tool_raises_for_unknown_tool(self):
        from src.tools.registry import execute_tool

        with self.assertRaises(KeyError):
            execute_tool("missing_tool")


if __name__ == "__main__":
    unittest.main()
