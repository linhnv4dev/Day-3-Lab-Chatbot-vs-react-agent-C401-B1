"""
Shared prompts for comparing the baseline chatbot and later agent versions.

Keep this file phase-neutral so the same prompts can be reused for:
- Phase 1: Chatbot baseline
- Phase 3+: ReAct Agent comparisons
"""

import sys

COMPARISON_PROMPTS = [
    {
        "id": "book_meeting_schedule",
        "label": "Book lịch meeting",
        "prompt": (
            "Đặt giúp tôi một cuộc họp với Minh Anh, Tuấn Khoa, và Hà Linh vào tuần tới. Tìm khung giờ mà cả 3 người đều rảnh, đặt cuộc họp với tiêu đề 'Team Meeting', và gửi email mời họp từ địa chỉ organizer@company.vn"
        ),
        "goal": "Kiem tra kha nang xu ly bai toan nhieu buoc va tinh toan tong hop.",
    },
    # {
    #     "id": "cheapest_laptop_vat",
    #     "label": "Tim gia re nhat roi cong VAT",
    #     "prompt": (
    #         "Hãy tìm sản phẩm laptop rẻ nhất trong cửa hàng, sau đó tính giá cuối cùng "
    #         "nếu cộng thêm 10% thuế VAT."
    #     ),
    #     "goal": "Kiem tra kha nang tim kiem thong tin truoc khi suy luan tiep.",
    # },
    # {
    #     "id": "stock_check_alternative",
    #     "label": "Kiem tra ton kho va de xuat thay the",
    #     "prompt": (
    #         "Kiểm tra xem cửa hàng còn đủ 3 tai nghe Sony WH-1000XM5 không. "
    #         "Nếu không đủ, hãy đề xuất phương án thay thế và tính tổng chi phí dự kiến."
    #     ),
    #     "goal": "Kiem tra xu ly dieu kien va phuong an thay the.",
    # },
    # {
    #     "id": "compare_purchase_options",
    #     "label": "So sanh hai phuong an mua hang",
    #     "prompt": (
    #         "So sánh 2 phương án mua hàng sau và cho biết phương án nào rẻ hơn: "
    #         "mua 1 MacBook Air với mã SAVE10, hoặc mua 2 iPad với mã STUDENT, "
    #         "đều giao đến Đà Nẵng."
    #     ),
    #     "goal": "Kiem tra kha nang so sanh da phuong an thay vi chi tra loi mot ve.",
    # },
    # {
    #     "id": "budget_bundle",
    #     "label": "Chon combo trong ngan sach",
    #     "prompt": (
    #         "Tôi có ngân sách 30 triệu. Hãy chọn giúp tôi một combo gồm điện thoại, "
    #         "tai nghe và phí giao hàng sao cho không vượt ngân sách, rồi giải thích cách bạn tính."
    #     ),
    #     "goal": "Kiem tra kha nang lap ke hoach va rang buoc ngan sach.",
    # },
]


def get_all_prompts():
    return COMPARISON_PROMPTS


def get_prompt_by_id(prompt_id: str):
    for item in COMPARISON_PROMPTS:
        if item["id"] == prompt_id:
            return item
    raise KeyError(f"Unknown prompt id: {prompt_id}")


def _safe_print(text: str):
    try:
        sys.stdout.write(text + "\n")
    except UnicodeEncodeError:
        sys.stdout.buffer.write((text + "\n").encode("utf-8"))
    finally:
        sys.stdout.flush()


if __name__ == "__main__":
    for item in COMPARISON_PROMPTS:
        _safe_print(f"[{item['id']}] {item['prompt']}")
        