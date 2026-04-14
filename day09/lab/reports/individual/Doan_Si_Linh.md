# Báo Cáo Cá Nhân — Lab Day 09: Multi-Agent Orchestration

**Họ và tên:** Đoàn Sĩ Linh

**Vai trò trong nhóm:** Worker Owner

**Ngày nộp:** 14/04/2026


---

## 1. Tôi phụ trách phần nào?

Trong buổi Lab hôm nay, tôi chịu trách nhiệm chính về module **Policy & Tool Worker** và việc tích hợp các **MCP tools**.

**Module/file tôi chịu trách nhiệm:**
- File chính: `workers/policy_tool.py`
- Functions tôi implement: `analyze_policy`, `run`, `_call_mcp_tool` và logic xử lý logic temporal scoping.

**Cách công việc của tôi kết nối với phần của thành viên khác:**
Công việc của tôi là cầu nối giữa Retrieval (lấy dữ liệu) và Synthesis (tổng hợp câu trả lời). Sau khi Retrieval Worker tìm được các đoạn văn bản (chunks), Worker của tôi sẽ phân tích các chunks này dựa trên các quy tắc chính sách (refund, access control). Kết quả `policy_result` do tôi tạo ra là đầu vào quan trọng để Synthesis Worker quyết định có được phép trả lời hay phải từ chối yêu cầu của khách hàng.

**Bằng chứng (commit hash, file có comment tên bạn, v.v.):**
Tôi đã hoàn thiện toàn bộ phần logic xử lý ngoại lệ (Flash Sale, Digital Product) và logic gọi MCP tools cho ticket/access permission trong file policy_tool.py

---

## 2. Tôi đã ra một quyết định kỹ thuật gì?

**Quyết định:** Sử dụng hệ thống **Hybrid Policy Analysis** (kết hợp Rule-based và LLM analysis).

Thay vì chỉ dùng Duy nhất LLM để phân tích chính sách (tốn token và latency cao) hoặc chỉ dùng Duy nhất Rule-based (không xử lý được các trường hợp diễn đạt phức tạp), tôi đã chọn cách tiếp cận lai:
1. **Fast Path (Rule-based):** Sử dụng keyword matching để phát hiện ngay lập tức các trường hợp vi phạm rõ ràng như "Flash Sale", "License Key", "Activated". Các case này được xử lý trong ~1-5ms với độ chính xác tuyệt đối.
2. **Deep Path (LLM-based):** Nếu rules không tìm thấy vi phạm nhưng task vẫn liên quan đến chính sách, tôi gọi LLM (gpt-4o-mini) để phân tích ngữ cảnh sâu hơn.

**Lý do:**
Cách làm này giúp hệ thống hoạt động cực nhanh cho các câu hỏi phổ biến, đồng thời vẫn đảm bảo tính linh hoạt khi gặp các trường hợp "edge case" hoặc câu hỏi lắt léo.
**Bằng chứng từ trace/code:**
Trong standalone test case 1, prompt task chứa "Flash Sale", rule-based phát hiện ngay lập tức:
```python
if "flash sale" in task_lower or "flash sale" in context_lower:
    exceptions_found.append({
        "type": "flash_sale_exception",
        "rule": "Đơn hàng Flash Sale không được hoàn tiền (Điều 3, chính sách v4).",
        "source": "policy_refund_v4.txt",
    })
```

---

## 3. Tôi đã sửa một lỗi gì?

**Lỗi:** Xung đột logic giữa các loại chính sách (Policy Domain Confusion).

**Symptom (pipeline làm gì sai?):**
Khi nhận được các yêu cầu phức tạp (ví dụ: vừa hỏi về quyền truy cập vừa liên quan đến Incident P1), pipeline thường bị nhầm lẫn và áp dụng các quy tắc kiểm tra của chính sách hoàn tiền (Refund) cho các câu hỏi về kỹ thuật. Điều này dẫn đến `policy_result` trả về các thông số không liên quan, gây nhiễu cho bước Synthesis.

**Root cause (lỗi nằm ở đâu — indexing, routing, contract, worker logic?):**
Nguyên nhân nằm ở việc hàm `analyze_policy` ban đầu được thiết kế theo dạng "cồng kềnh" (monolithic), gộp chung mọi rule-based check vào một luồng duy nhất. Khi các bộ từ khóa (`refund` và `access`) xuất hiện đồng thời trong task hoặc context, worker không biết ưu tiên domain nào, dẫn đến việc trả về các exception "râu ông nọ cắm cằm bà kia".

**Cách sửa:**
Tôi đã thực hiện một đợt tái cấu trúc (refactoring) lớn cho `policy_tool.py`:
1. Phân tách logic thành các hàm chuyên biệt: `analyze_refund_policy`, `analyze_access_policy`.
2. Xây dựng module `_detect_domain` (dòng 94-110) để thực hiện "Phân loại Domain" ngay tại đầu luồng xử lý của worker.
3. Sử dụng bộ từ khóa định danh (`REFUND_KEYWORDS`, `ACCESS_KEYWORDS`, `INCIDENT_KEYWORDS`) để định tuyến logic phân tích một cách chính xác thay vì để các quy tắc chồng chéo nhau.

**Bằng chứng trước/sau:**
*Trước khi sửa:* Kết quả trả về luôn mặc định `policy_name="refund_policy_v4"` kể cả khi task là về access permission, dẫn đến Synthesis đưa ra thông tin hoàn tiền cho một câu hỏi về bảo mật.
*Sau khi sửa:* Trace log ghi nhận sự phân loại domain chính xác và định tuyến đến đúng hàm xử lý:
```python
if domain == "refund":
    policy_result = analyze_refund_policy(task, chunks)
elif domain in {"access", "incident_access"}:
    policy_result = analyze_access_policy(task, chunks, access_tool_output, domain)
```
Kết quả trace (run_id) hiện tại đã hiển thị đúng `domain` tương ứng cho từng câu hỏi, giúp tăng độ chính xác của câu trả lời cuối cùng lên đáng kể.

---

## 4. Tôi tự đánh giá đóng góp của mình

**Tôi làm tốt nhất ở điểm nào?**
Tôi đã xây dựng được module Policy cực kỳ "chắc chắn" (robust). Việc detect được chính xác temporal scoping (đơn đặt hàng trước 01/02/2026 áp dụng v3) thông qua cả regex và LLM là một điểm mạnh giúp pipeline tránh được các lỗi logic về thời gian.

**Tôi làm chưa tốt hoặc còn yếu ở điểm nào?**
Phần trích xuất tham số cho Tool call (`access_level`, `requester_role`) hiện tại tôi đang dùng rule-based đơn giản. Nếu có thêm thời gian, tôi sẽ dùng LLM để trích xuất JSON schema cho tool input để đảm bảo độ chính xác cao hơn khi user dùng các từ lóng.

**Nhóm phụ thuộc vào tôi ở đâu?**
Nếu Worker của tôi không hoàn thiện, toàn bộ các yêu cầu liên quan đến "đặc quyền" (P1 tickets, Access level 3) sẽ bị trả lời sai hoặc không thể truy cập dữ liệu khẩn cấp qua MCP.

**Phần tôi phụ thuộc vào thành viên khác:**
Tôi phụ thuộc 100% vào Retrieval Worker. Nếu Retrieval trả về sai context (chunks), logic Policy của tôi dù có tốt đến đâu cũng sẽ phân tích trên dữ liệu rác.

---

## 5. Nếu có thêm 2 giờ, tôi sẽ làm gì?

Tôi sẽ cải tiến phần **Check Access Permission** bằng cách tích hợp logic "Temporal Logic" cho cả quyền truy cập. Trace của các câu hỏi về quyền Level 2 cho thấy user thường hỏi về thời gian hết hạn (expiration). Tôi sẽ thêm logic MCP để tự động tính toán thời gian `emergency_override` còn lại.

---