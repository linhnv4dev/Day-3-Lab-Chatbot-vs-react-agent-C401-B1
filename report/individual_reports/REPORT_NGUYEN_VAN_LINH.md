# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: NGUYỄN VĂN LĨNH
- **Student ID**: 2A202600412
- **Date**: 2026-04-06

---

## I. Technical Contribution (15 Points)

Tôi chịu trách nhiệm chính trong việc triển khai và tối ưu hóa ReAct
Agent, đặc biệt tập trung khắc phục lỗi chain hallucination và cải thiện
độ robust của parser.

- **Modules Implementated**:
    - `src/agent/react_agent.py`
    - `src/prompts/system_prompt.py`
    - `src/tools/tool_parser.py`
    - `src/tools/meeting_tools.py` (thêm date validation)
- **Code Highlights**:

```python
# System Prompt v2 - Khắc phục chain hallucination
"Generate ONLY ONE Action per step. Do NOT simulate future Observations.
Wait for the actual tool result before proceeding to the next step."

# Parser hardening trong react_agent.py
actions = self.extract_tool_calls(output)
if len(actions) > 1:
    logger.warning("Multiple actions detected. Enforcing single action policy.")
    actions = [actions[0]]  # Chỉ lấy action đầu tiên
```

- **Documentation**: Tôi đã xây dựng cơ chế quản lý vòng lặp ReAct
  (Thought → Action → Observation). Code đảm bảo agent chỉ thực hiện
  đúng một tool call mỗi bước, chờ Observation thực tế từ tool trước
  khi tiếp tục, giúp loại bỏ tình trạng LLM tự sinh chuỗi action giả.

---

## II. Debugging Case Study (10 Points)

- **Problem Description**: Agent bị chain hallucination tại Step 2:
  sau khi gọi `book_meeting`, LLM tự tiếp tục sinh luôn
  `send_invitation_email` với `booking_id=12345` (giá trị giả) thay vì
  chờ kết quả thật từ tool (booking_id thực là `"meeting_4"`). Ngoài
  ra còn sinh sai năm (`2025-04-10`).

- **Log Source**: `logs/2026-04-06.log – Event: AGENT_STEP step=2`

- **Diagnosis**: Nguyên nhân chính là System Prompt v1 chưa có ràng
  buộc "ONE action per response". LLM cố gắng giải quyết toàn bộ
  pipeline trong một lần sinh output. Tool `book_meeting` cũng thiếu
  validation nên chấp nhận date ở năm 2025.

- **Solution**:

- Cập nhật System Prompt v2 với lệnh rõ ràng: "Generate ONLY ONE
  Action per step. Do NOT simulate future Observations."

- Thêm validation `date >= today` vào tool `book_meeting`.

- Cải tiến parser để chỉ chấp nhận và thực thi một action duy nhất mỗi
  response.

→ Sau khi sửa, agent lấy đúng `booking_id` từ Observation thực tế và
không còn hallucination.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1.  **Reasoning**:\
    Khối Thought giúp agent phân tích và lập kế hoạch từng bước một cách
    logic (ví dụ: trước tiên tìm khung giờ rảnh, sau đó mới đặt lịch
    họp). Ngược lại, Chatbot thường trả lời trực tiếp hoặc từ chối thực
    hiện, thiếu quá trình suy nghĩ có cấu trúc.

2.  **Reliability**:\
    Agent vượt trội hơn ở các tác vụ đa bước (tìm slot → book meeting →
    gửi email). Tuy nhiên, với các câu hỏi đơn giản, Agent lại kém hơn
    Chatbot về tốc độ và chi phí (tốn khoảng 15s và gấp 5 lần chi phí).

3.  **Observation**:\
    Observation từ tool đóng vai trò quyết định. Khi kết quả tool (như
    `booking_id` thực) được inject lại vào prompt, agent mới có thể gọi
    đúng tool tiếp theo. Nếu thiếu Observation thật, agent dễ rơi vào
    hallucination và sử dụng giá trị giả.

---

## IV. Future Improvements (5 Points)

- **Scalability**: Chuyển sang sử dụng LangGraph để hỗ trợ parallel
  tool calls và conditional branching.

- **Safety**: Triển khai Supervisor LLM để kiểm tra các action trước
  khi thực thi tool nhạy cảm.\
  Thêm cost circuit breaker để giới hạn chi phí mỗi session.\
  Sử dụng UUID v4 cho `booking_id` thay vì sequential ID để tăng bảo
  mật.

- **Performance**: Hỗ trợ async tool execution để giảm tổng latency.\
  Cấu hình secondary LLM provider làm fallback (Gemini Flash hoặc
  GPT-4o-mini).\
  Sử dụng PostgreSQL để lưu persistent memory thay vì lưu file.

---

> \[!NOTE\] Submit this report by renaming it to `REPORT_[YOUR_NAME].md`
> and placing it in this folder.
