# Group Report: Lab 3 - Production-Grade Agentic System

- **Team Name**: C401-B1
- **Team Members**: [Chu Thị Ngọc Huyền, Nguyễn Văn Lĩnh, Hứa Quang Linh, Nguyễn Thị Tuyết, Nguyễn Mai Phương, Chu Bá Tuấn Anh]
- **Deployment Date**: 2026-04-06

---

## 1. Executive Summary

Mục tiêu của nhóm là xây dựng một **ReAct Agent** có khả năng thực hiện tác vụ đa bước phức tạp: tìm khung giờ rảnh chung, đặt cuộc họp và gửi email mời họp — những việc mà chatbot thông thường không thể tự động thực hiện.

**Kết quả**: Trong test case chạy ngày 2026-04-06, Agent đã **hoàn thành 100%** pipeline (3 tool calls), trong khi Chatbot từ chối thực thi và chỉ đưa ra hướng dẫn thủ công.

- **Agent**: SUCCESS
- **Chatbot**: FAILED
- **Agent Steps**: 4 steps / 3 tools
- **Total Cost**: $0.1359

**Key Outcome**: Agent giải quyết hoàn toàn tác vụ đa bước (find free slot → book meeting → send invitation email) thông qua 3 lần gọi tool thực tế, trong khi Chatbot chỉ trả lời bằng hướng dẫn thủ công. Điều này chứng minh rõ ràng sự vượt trội của vòng lặp **Thought-Action-Observation** trong các tác vụ có tính liên kết cao.

---

## 2. System Architecture & Tooling

### 2.1 ReAct Loop Implementation

Agent được triển khai theo vòng lặp **ReAct (Thought-Action-Observation)** chuẩn. Ở mỗi bước, LLM sẽ sinh ra:

- **Thought**: Lý luận nội tâm
- **Action**: Gọi một tool
  Sau đó nhận **Observation** (kết quả từ tool) và tiếp tục vòng lặp hoặc đưa ra **Final Answer**.
  User Input → Thought → Action (Tool Call) → Observation → Final Answer / Continue Loop
  text

Observation sau mỗi tool được inject lại vào prompt để làm input cho bước tiếp theo. Vòng lặp kết thúc khi LLM sinh ra “Final Answer:” hoặc đạt giới hạn `max_steps`.

### 2.2 Tool Definitions (Inventory)

| Tool Name                | Input Format                                                          | Use Case                                                    |
| ------------------------ | --------------------------------------------------------------------- | ----------------------------------------------------------- |
| `find_common_free_slots` | `person_names: string`                                                | Tìm khung giờ rảnh chung của nhiều người cho tuần tiếp theo |
| `book_meeting`           | `person_names, date, time, title, duration`                           | Đặt lịch cuộc họp và trả về booking_id duy nhất             |
| `send_invitation_email`  | `booking_id: string, organizer_email: string, custom_message: string` | Gửi email mời họp đến tất cả attendees dựa trên booking_id  |

### 2.3 LLM Providers Used

- **Primary**: `qw/qwen3-coder-flash` (via nine_router)
- **Secondary (Backup)**: Chưa cấu hình (Đề xuất thêm Gemini Flash hoặc GPT-4o-mini làm fallback)

---

## 3. Telemetry & Performance Dashboard

Dữ liệu được trích xuất từ log ngày 2026-04-06.

- **Average Latency / Step (P50)**: 3,856 ms
- **Max Latency (P99) - Step 1**: 7,975 ms
- **Average Tokens / Step**: 2,820 tokens
- **Total Cost of Agent**: $0.11312 (3 tool calls)
- **Cost Agent vs Chatbot**: ~5.0x more costly

**Nhận xét**:

- Token tăng dần theo mỗi bước do lịch sử hội thoại tích lũy vào prompt.
- Step 1 có latency cao nhất do prompt dài và cần suy nghĩ nhiều.
- Agent tốn chi phí cao hơn khoảng 5 lần so với chatbot nhưng bù lại hoàn thành được toàn bộ task.

---

## 4. Root Cause Analysis (RCA) - Failure Traces

### Case Study: Chain Hallucination tại `send_invitation_email`

**Input**: "Đặt giúp tôi một cuộc họp với Minh Anh, Tuấn Khoa, và Hà Linh vào tuần tới..."

**Trace tại Step 2**:

- LLM tự sinh ra chuỗi Action liên tiếp trong một lần output:
    - `book_meeting(...)` → hallucinated Observation
    - `send_invitation_email(booking_id=12345, ...)` ← **booking_id giả**

**Root Cause**:

- System prompt chưa ràng buộc **"ONE action per response"**.
- LLM cố gắng giải quyết nhiều bước trong một forward pass thay vì chờ Observation thực từ tool.
- Bug phụ: date được sinh ra là `"2025-04-10"` (sai năm).

**Fix đã áp dụng cho Agent v2**:

- Thêm vào system prompt: _"Generate ONLY ONE Action per step. Do NOT simulate future Observations."_
- Thêm validation cho `book_meeting`: `date >= today`
- Parser hardening: cảnh báo hoặc reject nếu output chứa nhiều hơn 1 Action.

---

## 5. Ablation Studies & Experiments

### Experiment 1: System Prompt v1 vs v2

| Prompt            | Key Diff                                                  | Result                                                                      |
| ----------------- | --------------------------------------------------------- | --------------------------------------------------------------------------- |
| **v1 (Baseline)** | Không ràng buộc số Action, không hướng dẫn format date    | Chain hallucination, booking_id giả, date sai năm                           |
| **v2 (Fixed)**    | Thêm "ONE action only", "date >= today", few-shot example | Không còn hallucination, date đúng 2026, booking_id lấy từ Observation thực |

**Kết luận**: Prompt v2 giúp agent reasoning đúng đắn và robust hơn.

### Experiment 2 (Bonus): Chatbot vs Agent

| Test Case                | Chatbot Result               | Agent Result                                | Winner                 |
| ------------------------ | ---------------------------- | ------------------------------------------- | ---------------------- |
| Tìm khung giờ rảnh chung | Từ chối – hướng dẫn thủ công | Gọi tool → trả về 2026-04-10 10:00          | **Agent**              |
| Đặt lịch cuộc họp        | Không thực hiện              | Gọi `book_meeting` → booking_id = meeting_4 | **Agent**              |
| Gửi email mời họp        | Đề nghị soạn email giả       | Gọi tool → gửi thực tế 3 emails             | **Agent**              |
| Trả lời câu hỏi đơn giản | Nhanh, chi phí thấp (~4.9s)  | Đúng nhưng tốn 4 bước (~15s)                | Chatbot (cost/latency) |

---

## 6. Production Readiness Review

- **Security**:
    - Input sanitization & schema validation cho tất cả tool arguments.
    - Email spoofing protection: whitelist domain cho `organizer_email`.
    - Sử dụng UUID v4 cho booking_id thay vì sequential ID.

- **Guardrails**:
    - `max_steps = 8` để tránh infinite loop.
    - Date validation: từ chối date < today.
    - Single-Action enforcement trong parser.
    - Cost circuit breaker: dừng agent nếu tổng chi phí vượt ngưỡng.

- **Scaling**:
    - Chuyển sang **LangGraph** cho workflow phức tạp hơn (parallel tools, conditional branching).
    - Cấu hình provider fallback (Gemini Flash).
    - Hỗ trợ async tool execution.
    - Sử dụng database (PostgreSQL) thay vì file để lưu persistent memory.

---

> [!NOTE]
> Submit this report by renaming it to `GROUP_REPORT_[TEAM_NAME].md` and placing it in the `report/group_report/` folder.
