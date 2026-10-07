# Báo cáo Phân tích Bài tập Block 1: Tra cứu chính sách đúng phiên bản

## 1. Kết quả kiểm tra tool trực tiếp (`list_files`)

Thực hiện gọi hàm `list_files` trực tiếp trong môi trường workspace của bài thực hành qua 4 trường hợp thử nghiệm:

1. **Thư mục hợp lệ (`data/policies`)**:
   - Lệnh gọi: `list_files(path="data/policies")`
   - Kết quả:
     ```json
     {
       "ok": true,
       "path": "data/policies",
       "entries": [
         {"name": "policy-before-oct.md", "path": "data/policies/policy-before-oct.md", "type": "file"},
         {"name": "policy-from-oct.md", "path": "data/policies/policy-from-oct.md", "type": "file"}
       ]
     }
     ```
   - Đánh giá: Liệt kê đầy đủ các file trong thư mục, sắp xếp theo thứ tự tên tăng dần, phân loại chính xác `file` và `directory`.

2. **Đường dẫn trỏ tới một file (`data/weekly_notes.md`)**:
   - Lệnh gọi: `list_files(path="data/weekly_notes.md")`
   - Kết quả:
     ```json
     {
       "ok": false,
       "error": {
         "code": "NOT_A_DIRECTORY",
         "message": "Đây là file, không phải thư mục: data/weekly_notes.md"
       }
     }
     ```
   - Đánh giá: Xử lý đúng trường hợp đường dẫn hợp lệ nhưng là file, từ chối liệt kê và trả về mã lỗi rõ ràng `NOT_A_DIRECTORY`.

3. **Đường dẫn thư mục không tồn tại (`data/not_found`)**:
   - Lệnh gọi: `list_files(path="data/not_found")`
   - Kết quả:
     ```json
     {
       "ok": false,
       "error": {
         "code": "DIRECTORY_NOT_FOUND",
         "message": "Không tìm thấy thư mục: data/not_found"
       }
     }
     ```
   - Đánh giá: Báo lỗi chính xác `DIRECTORY_NOT_FOUND`, không trả về mảng rỗng giả vờ thư mục hợp lệ.

4. **Đường dẫn vượt ngoài workspace (`../`)**:
   - Lệnh gọi: `list_files(path="../")`
   - Kết quả:
     ```json
     {
       "ok": false,
       "error": {
         "code": "PATH_OUTSIDE_WORKSPACE",
         "message": "Đường dẫn thoát ra ngoài workspace: ../"
       }
     }
     ```
   - Đánh giá: Bảo vệ an toàn workspace (Sandbox), chặn hoàn toàn tấn công Directory Traversal ngay cả khi dùng `..`, đường dẫn tuyệt đối hoặc symlink.

---

## 2. Kết quả từng trường hợp kiểm tra & Bằng chứng trong trace

### Trường hợp A: Mua trước ngày đổi chính sách
- **Câu hỏi của người dùng**:
  > *"Tôi mua ngày 28/09/2026, yêu cầu hoàn ngày 06/10/2026, chưa kích hoạt. Tôi có được hoàn không?"*
- **Trace file**: `stage-02-skills/traces/20261007-234500_case_a01_turn01_run_a001.jsonl`
- **Quy trình agent thực hiện**:
  1. *Model call 1 (Sequence 2-3)*: Nhận diện task liên quan đến chính sách hoàn tiền -> gọi `read_file` đọc `skills/refund-policy/SKILL.md`.
  2. *Model call 2 (Sequence 6-7)*: Đọc xong quy trình của skill -> gọi `list_files(data/policies)` để liệt kê các file chính sách đang có.
  3. *Model call 3 (Sequence 10-11)*: Đối chiếu ngày mua `28/09/2026` (< `2026-10-01`) -> gọi `read_file` đọc `data/policies/policy-before-oct.md` và `skills/refund-policy/references/answer-template.md`.
  4. *Model call 4 (Sequence 16-17)*: Tính số ngày chênh lệch (06/10/2026 - 28/09/2026 = 8 ngày). So sánh với giới hạn 7 ngày -> Trả lời theo template.
- **Kết quả trả lời**:
  - Chính sách áp dụng: Chính sách hoàn tiền trước tháng 10.
  - Số ngày đã qua: 8 ngày.
  - Kết luận: **Không đủ điều kiện hoàn tiền** (do quá thời hạn 7 ngày theo quy định).
  - Căn cứ tài liệu: `data/policies/policy-before-oct.md`.
- **Vị trí bằng chứng trong Trace**:
  - `Sequence 3`: `tool_calls_requested` yêu cầu `read_file` file `skills/refund-policy/SKILL.md` (`tool_call_id: call_a_read_skill`).
  - `Sequence 7`: `tool_calls_requested` gọi `list_files` thư mục `data/policies` (`tool_call_id: call_a_list_files`).
  - `Sequence 11`: `tool_calls_requested` gọi đọc file chính sách cũ `data/policies/policy-before-oct.md` (`tool_call_id: call_a_read_pol`).
  - `Sequence 17`: Model trả về kết luận không đủ điều kiện và viện dẫn đúng tài liệu.

---

### Trường hợp B: Mua từ ngày đổi chính sách (Sau khi đổi tên file)
- **Thao tác đổi tên file chính sách**:
  - `policy-before-oct.md` -> `chinh-sach-truoc-thang-10.md`
  - `policy-from-oct.md` -> `chinh-sach-tu-thang-10.md`
- **Câu hỏi của người dùng**:
  > *"Tôi mua ngày 02/10/2026, yêu cầu hoàn ngày 12/10/2026, chưa kích hoạt. Tôi có được hoàn không?"*
- **Trace file**: `stage-02-skills/traces/20261007-234700_case_b01_turn01_run_b001.jsonl`
- **Quy trình agent thực hiện**:
  1. *Model call 1 (Sequence 2-3)*: Gọi `read_file` nạp `skills/refund-policy/SKILL.md`.
  2. *Model call 2 (Sequence 6-7)*: Gọi `list_files(data/policies)` và nhận danh sách file mới đã đổi tên.
  3. *Model call 3 (Sequence 10-11)*: Xác định ngày mua `02/10/2026` thuộc phạm vi tháng 10 -> gọi `read_file` đọc đúng file mới `data/policies/chinh-sach-tu-thang-10.md` và `references/answer-template.md`.
  4. *Model call 4 (Sequence 16-17)*: Tính số ngày (12/10/2026 - 02/10/2026 = 10 ngày <= 14 ngày, chưa kích hoạt) -> Đủ điều kiện hoàn tiền, không thu phí.
- **Kết quả trả lời**:
  - Chính sách áp dụng: Chính sách hoàn tiền từ tháng 10.
  - Số ngày đã qua: 10 ngày.
  - Kết luận: **Đủ điều kiện hoàn tiền**.
  - Phí hoàn tiền: Không thu phí hoàn tiền (0%).
  - Căn cứ tài liệu: `data/policies/chinh-sach-tu-thang-10.md`.
- **Vị trí bằng chứng trong Trace**:
  - `Sequence 9`: `tool_finished` trả về `entries` chứa tên file đã đổi: `chinh-sach-truoc-thang-10.md` và `chinh-sach-tu-thang-10.md`.
  - `Sequence 12-13`: Model yêu cầu đọc chính xác file đã đổi tên `data/policies/chinh-sach-tu-thang-10.md` mà không hề phụ thuộc tên file cũ.
  - `Sequence 17`: Model đưa ra câu trả lời theo template và trích dẫn đúng đường dẫn file mới.

---

### Trường hợp thiếu thông tin:
- **Câu hỏi của người dùng**:
  > *"Tôi mua ngày 02/10/2026, muốn hoàn ngày 12/10/2026."*
- **Trace file**: `stage-02-skills/traces/20261007-234900_case_c01_turn01_run_c001.jsonl`
- **Quy trình agent thực hiện**:
  1. *Model call 1 (Sequence 2-3)*: Gọi `read_file` nạp `skills/refund-policy/SKILL.md`.
  2. *Model call 2 (Sequence 6-7)*: Đọc hướng dẫn ở Bước 1 của Skill ("Bắt buộc: Nếu thiếu bất kỳ thông tin nào trong 3 thông tin trên... PHẢI hỏi lại người dùng để làm rõ trước khi đưa ra kết luận. Không được tự tiện giả định"). Model nhận diện câu hỏi **thiếu trạng thái kích hoạt**.
  3. Model **hỏi lại người dùng**, không tự giả định "chưa kích hoạt", chưa vội đưa ra kết luận hoàn tiền.
- **Kết quả trả lời**:
  > *"Để xác định bạn có đủ điều kiện hoàn tiền hay không, vui lòng cho biết sản phẩm của bạn đã được kích hoạt hay chưa kích hoạt? Theo quy định chính sách, sản phẩm đã kích hoạt sẽ không được hỗ trợ hoàn tiền."*
- **Vị trí bằng chứng trong Trace**:
  - `Sequence 7`: Model dừng và phản hồi trực tiếp câu hỏi yêu cầu người dùng làm rõ trạng thái kích hoạt, không gọi thêm tool đọc chính sách nào khi chưa đủ thông tin đầu vào.

---

## 3. Trả lời Câu hỏi cuối bài

### Câu 1: Vì sao cần tool để tìm file và skill để hướng dẫn chọn chính sách?
- **Vai trò của tool tìm file (`list_files`)**:
  - Môi trường lưu trữ thực tế mang tính động (dynamic): tên tệp tin, vị trí lưu trữ hoặc số lượng phiên bản chính sách có thể thay đổi hoặc mở rộng bất cứ lúc nào.
  - Mô hình ngôn ngữ lớn (LLM) không thể tự quan sát cấu trúc thư mục cục bộ nếu không có tool hỗ trợ. Nếu không có `list_files`, agent bắt buộc phải hardcode tên file hoặc đoán mò đường dẫn, dẫn đến thất bại khi tên file bị thay đổi. Tool `list_files` cung cấp khả năng khám phá động (Dynamic Discovery).
- **Vai trò của skill hướng dẫn chọn chính sách (`refund-policy`)**:
  - LLM có xu hướng tự phỏng đoán hoặc trả lời tự do dựa trên xác suất ngôn ngữ. Skill cung cấp một quy trình thao tác chuẩn (SOP - Standard Operating Procedure) đóng gói nghiệp vụ:
    1. Kiểm soát chặt chẽ thông tin đầu vào (yêu cầu đủ 3 tham số, cấm tự giả định).
    2. Định hướng logic phân nhánh chính sách (đối chiếu mốc ngày mua để chọn văn bản).
    3. Định nghĩa thuật toán tính toán và điều kiện áp dụng.
    4. Chuẩn hóa hình thức và căn cứ của câu trả lời qua template.
  - Việc đóng gói thành skill giúp triển khai nguyên lý nạp ngữ cảnh tiến trình (Progressive Disclosure): system prompt ban đầu chỉ chứa catalog ngắn gọn, nội dung chi tiết của skill chỉ được đọc vào ngữ cảnh khi người dùng thực sự có nhu cầu tra cứu hoàn tiền.

### Câu 2: Nếu agent chưa có tool tìm file, việc sửa prompt có giải quyết được yêu cầu đổi tên file không? Giải thích.
- **Câu trả lời**: **KHÔNG giải quyết được một cách triệt để và bền vững.**
- **Giải thích**:
  - **Sự mù mờ môi trường (Environmental Blindness)**: Prompt thuần túy chỉ là các chỉ dẫn tĩnh được biên soạn sẵn trước lúc chạy. Nếu agent không có tool để thăm dò môi trường thực tế (`list_files`), prompt không có cách nào biết trước người quản trị đã đổi tên file thành gì trong tương lai.
  - **Bẫy Hardcode (Stale Prompt)**: Nếu mỗi lần đổi tên file ta lại phải vào sửa prompt để cập nhật tên file mới, đây chỉ là giải pháp chắp vá và phụ thuộc hoàn toàn vào con người can thiệp thủ công. Ngay khi file bị đổi tên tiếp theo, agent sẽ lại lập tức bị lỗi không tìm thấy file (`FILE_NOT_FOUND`).
  - **Khả năng tự chủ (Autonomy & Scalability)**: Để hệ thống có thể tự thích ứng với các thay đổi trong môi trường dữ liệu, agent bắt buộc phải có cơ chế quan sát (Perception) - cụ thể ở đây là tool `list_files` - để liệt kê và tự động tìm ra file phù hợp trước khi mở đọc bằng `read_file`.
