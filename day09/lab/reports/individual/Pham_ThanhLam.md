# Báo Cáo Cá Nhân — Lab Day 09: Multi-Agent Orchestration

**Họ và tên:** Phạm Thanh Lam
**Vai trò trong nhóm:** Worker Owner (Retrieval Worker)
**Ngày nộp:** 14/04/2026
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi phụ trách phần nào? (100–150 từ)

Trong dự án Day 09, tôi chịu trách nhiệm chính về module tìm kiếm thông tin (**Retrieval Worker**). Đây là mắt xích đầu tiên và quan trọng nhất sau khi Supervisor phân loại câu hỏi, vì chất lượng câu trả lời của Agent phụ thuộc hoàn toàn vào bằng chứng (evidence) mà tôi tìm thấy.

**Module/file tôi chịu trách nhiệm:**

- File chính: `workers/retrieval.py`
- Functions tôi implement:
  - `_get_embedding_fn()`: Cấu hình sử dụng OpenAI Embedding đồng bộ với hệ thống cũ.
  - `_get_collection()`: Kết nối linh hoạt tới ChromaDB.
  - `retrieve_dense()`: Thực hiện tìm kiếm ngữ nghĩa (semantic search) và format kết quả theo contract.
  - `run(state)`: Hàm entry point để tích hợp vào LangGraph/Supervisor.

**Cách công việc của tôi kết nối với phần của thành viên khác:**
Kết quả đầu ra của tôi (`retrieved_chunks`) là đầu vào bắt buộc cho `policy_tool_worker` để kiểm tra các ngoại lệ và `synthesis_worker` để tổng hợp câu trả lời cuối cùng. Nếu tôi tìm sai tài liệu, toàn bộ hệ thống sẽ trả lời sai (hallucination).

**Bằng chứng:**
Tôi đã commit các thay đổi với thông điệp: `feat(day09): implement retrieval worker and link to day08 database`.

---

## 2. Tôi đã ra một quyết định kỹ thuật gì? (150–200 từ)

**Quyết định:** Tái sử dụng (Reuse) cơ sở dữ liệu vector (`chroma_db`) từ Day 08 thông qua cấu hình biến môi trường, thay vì chạy lại quy trình Indexing từ đầu.

**Lý do:**

1. **Tiết kiệm tài nguyên:** Việc chạy lại Index cho 5 tài liệu lớn tốn khoảng vài phút và phát sinh chi phí gọi API OpenAI cho các đoạn text đã được embed trước đó.
2. **Đảm bảo tính nhất quán:** Bằng cách dùng chung database, tôi đảm bảo kết quả retrieval của Day 09 tương đương hoặc tốt hơn Day 08 (vốn đã được kiểm chứng), giúp việc debug graph dễ dàng hơn.
3. **Tính linh động:** Tôi đã sử dụng `os.getenv` để cho phép hệ thống tự động trỏ về đường dẫn mặc định `../../day08/lab/chroma_db` nếu người dùng không khai báo path khác trong `.env`.

**Trade-off đã chấp nhận:**
Chấp nhận sự phụ thuộc vào cấu trúc thư mục của Day 08. Tuy nhiên, rủi ro này thấp vì trong một repository chung, cấu trúc các folder Lab thường được giữ cố định.

**Bằng chứng từ trace/code:**
Trong hàm `_get_collection`, tôi đã triển khai code như sau:

```python
db_path = os.getenv("CHROMA_DB_PATH", "../../day08/lab/chroma_db")
collection_name = os.getenv("CHROMA_COLLECTION", "rag_lab")
client = chromadb.PersistentClient(path=db_path)
```

---

## 3. Tôi đã sửa một lỗi gì? (150–200 từ)

**Lỗi:** Mismatch thông tin Collection và Embedding Model khi chạy standalone test.

**Symptom:** Khi chạy lệnh `python workers/retrieval.py`, mặc dù database tồn tại nhưng hệ thống báo lỗi không tìm thấy collection `day09_docs` hoặc trả về kết quả rỗng (score cực thấp) do sai model embedding (mặc định của boilerplate dùng `sentence-transformers`).

**Root cause:**

1. Boilerplate của Day 09 mặc định tìm collection tên `day09_docs`, trong khi dữ liệu từ Day 08 được lưu với tên `rag_lab`.
2. Do Day 08 dùng OpenAI `text-embedding-3-small`, việc Retrieval dùng model offline sẽ khiến các vector không thể so khớp chính xác.

**Cách sửa:**
Tôi đã cập nhật file `.env` để trỏ đúng tên collection và chỉnh sửa hàm `_get_embedding_fn` để ưu tiên load OpenAI API Key từ môi trường.

**Bằng chứng trước/sau:**

- **Trước khi sửa:** Kết quả `Retrieved: 0 chunks`.
- **Sau khi sửa:**

```text
▶ Query: SLA ticket P1 là bao lâu?
  Retrieved: 3 chunks
    [0.589] support/sla-p1-2026.pdf: Ticket P1: Phản hồi 15 phút...
```

---

## 4. Tôi tự đánh giá đóng góp của mình (100–150 từ)

**Tôi làm tốt nhất ở điểm nào?**
Tôi đã tối ưu được quy trình thiết lập ban đầu (setup phase). Thay vì loay hoay index lại dữ liệu, tôi nhanh chóng kết nối được các module sẵn có, giúp nhóm tiết kiệm ít nhất 15-20 phút chuẩn bị.

**Tôi làm chưa tốt hoặc còn yếu ở điểm nào?**
Tôi cần cải thiện kỹ năng quản lý dependency. Lúc đầu tôi gặp khó khăn khi chạy `pip install` do lỗi đường dẫn file `requirements.txt`.

**Nhóm phụ thuộc vào tôi ở đâu?**
Nếu file `retrieval.py` của tôi chưa hoàn thiện, các bạn làm `synthesis_worker` sẽ không có dữ liệu để sinh câu trả lời, dẫn đến việc toàn bộ Graph trả về "I don't know".

**Phần tôi phụ thuộc vào thành viên khác:**
Tôi cần **Supervisor Owner** hoàn thiện logic routing để gửi đúng tham số `task` và `top_k` vào worker của tôi.

---

## 5. Nếu có thêm 2 giờ, tôi sẽ làm gì? (50–100 từ)

Tôi sẽ triển khai **Hybrid Search (Kết hợp Dense + Sparse Retrieval)**. Dựa trên kết quả test query với các mã số như "IT-ACCESS" hay "P1", tôi thấy việc chỉ dùng Vector Search đôi khi bị "noise" bởi ngữ cảnh. Việc thêm BM25 search sẽ giúp bắt được chính xác các Keyword đặc thù này, nâng mức độ tự tin (confidence) của kết quả lên trên 0.8.

---

_Lưu file này với tên: `reports/individual/Pham_ThanhLam.md`_
