# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Phạm Thanh Lam  
**Vai trò trong nhóm:** Tech Lead / Retrieval Owner / Eval Owner / Documentation Owner  
**Ngày nộp:** 13/04/2026  
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

Trong dự án RAG Pipeline này, tôi chịu trách nhiệm chính về Sprint 1: Xây dựng hệ thống Indexing. Tôi đã trực tiếp implement file `index.py`, bao gồm các bước từ đọc dữ liệu thô, tiền xử lý đến lưu trữ vector. Cụ thể, tôi đã thiết kế logic trích xuất metadata từ header của các file chính sách (Source, Department, Effective Date, Access) để phục vụ cho việc lọc dữ liệu sau này. Tôi cũng là người đưa ra quyết định về chiến lược chunking: ưu tiên chia nhỏ tài liệu theo các tiêu đề Section (`=== Section ===`) để giữ trọn vẹn ngữ cảnh của từng điều khoản, thay vì chỉ cắt theo số ký tự cứng nhắc. Công việc của tôi là nền tảng quan trọng nhất; nếu dữ liệu không được chunk và embed đúng cách, các bước Retrieval và Generation phía sau của nhóm sẽ không thể hoạt động hiệu quả hoặc trả về thông tin sai lệch.

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

Sau lab này, tôi đã thực sự hiểu rõ tầm quan trọng của việc **Preprocessing và Metadata Extraction**. Trước đây, tôi cứ nghĩ chỉ cần đưa văn bản thô vào mô hình embedding là xong. Tuy nhiên, khi thực tế xử lý các file chính sách của công ty, tôi nhận ra rằng nếu không tách riêng được `Effective Date` hay `Department`, hệ thống sẽ gặp khó khăn khi người dùng hỏi về các phiên bản mới nhất hoặc các quy định riêng cho từng bộ phận. Việc "làm sạch" văn bản (normalize text) và gán nhãn metadata chính xác giúp tăng đáng kể độ chính xác của bước Retrieval. Ngoài ra, khái niệm **Hierarchical Chunking** (chia theo cấu trúc tự nhiên của văn bản) cũng giúp tôi nhận thấy sự khác biệt rõ rệt so với **Fixed-size Chunking**. Việc giữ lại heading trong mỗi chunk giúp LLM hiểu được đoạn văn đó thuộc về phần nào của tài liệu, từ đó tạo ra câu trả lời có tính "grounded" cao hơn.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

Khó khăn lớn nhất mà tôi gặp phải là xử lý các tài liệu có bí danh (alias) hoặc thay đổi tên gọi. Ví dụ như trường hợp của file "Access Control SOP" vốn trước đây có tên khác. Điều này khiến các query sử dụng tên cũ không thể tìm thấy tài liệu chính xác. Tôi đã phải thực hiện một giải pháp "thủ công" nhưng hiệu quả là tạo thêm một "Alias Chunk" trong code để ánh xạ các tên gọi cũ sang file mới. Một điểm gây ngạc nhiên khác là sự nhạy cảm của ChromaDB với cấu trúc metadata. Trong quá trình debug, tôi mất khá nhiều thời gian vì metadata truyền vào không đồng nhất về kiểu dữ liệu (ví dụ: có file thiếu trường `access`), dẫn đến việc query bằng filtering bị lỗi. Tôi đã phải bổ sung logic gán giá trị mặc định cho metadata để đảm bảo tính ổn định cho toàn bộ hệ thống.

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

**Câu hỏi:** `gq06` - Quy trình và thời hạn cấp quyền truy cập tạm thời cho hệ thống nội bộ là gì?

**Phân tích:**
Trong bảng Scorecard Baseline, câu hỏi này có điểm số rất thấp: Faithful=4, Relevant=3, Recall=2, và Complete=2. Nguyên nhân chính không nằm ở khả năng tạo câu trả lời của LLM, mà nằm ở bước **Retrieval**. Hệ thống đã bỏ lỡ nguồn tài liệu quan trọng là `access-control-sop`, dẫn đến việc Answer thiếu mất quy trình cụ thể và các mốc thời hạn (7 ngày hoặc 30 ngày cho quyền tạm thời). Một phần lỗi xuất phát từ việc logic chunking của tôi chưa đủ linh hoạt để bắt được các từ khóa liên quan đến "Temporary Access" khi chúng nằm rải rác ở các section khác nhau.

Baseline đã trả lời đúng hướng chung nhưng thiếu chi tiết thực thi quan trọng từ SOP. Khi chuyển sang bản Variant, nếu chúng tôi tăng `top_k_search` hoặc cải thiện embedding model sang bản đa ngôn ngữ tốt hơn, kết quả Recall có thể được cải thiện. Lỗi này cho thấy việc Indexing cần phải chú trọng hơn vào việc gắn nhãn (tagging) các khái niệm quan trọng như "Temporary Access" trực tiếp vào metadata thay vì chỉ dựa vào semantic search đơn thuần trên nội dung text.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

Nếu có thêm thời gian, tôi sẽ cải tiến hàm `_split_by_size` để thực hiện **Markdown-aware splitting**. Thay vì cắt theo độ dài ký tự thô, tôi sẽ sử dụng thư viện như `LangChain`'s `RecursiveCharacterTextSplitter` để ưu tiên cắt tại các dấu xuống dòng giữa các đoạn văn hoặc sau các dấu chấm câu. Điều này giúp tránh tình trạng một câu nói bị chia đôi ở hai chunk khác nhau, gây mất ngữ cảnh nghiêm trọng khi LLM đọc dữ liệu. Ngoài ra, tôi muốn thử nghiệm thêm **Hybrid Search** (kết hợp Dense Vector và BM25) để bắt chính xác các thuật ngữ kỹ thuật đặc thù trong chính sách công ty.

---

*Lưu file này với tên: `reports/individual/Pham_Thanh_Lam.md`*
