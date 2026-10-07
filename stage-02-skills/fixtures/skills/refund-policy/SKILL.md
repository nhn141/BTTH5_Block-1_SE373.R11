---
name: refund-policy
description: Tra cứu và áp dụng chính sách hoàn tiền theo ngày mua hàng của khách hàng. Dùng khi người dùng hỏi về điều kiện hoàn tiền, chính sách hoàn trả hoặc yêu cầu hoàn tiền cho đơn hàng.
---

# Refund Policy Skill

Hướng dẫn tra cứu và áp dụng chính sách hoàn tiền cho khách hàng.

## Quy trình thực hiện

1. **Kiểm tra thông tin đầu vào**:
   - Xác định xem người dùng đã cung cấp đủ 3 thông tin cần thiết chưa:
     - Ngày mua hàng.
     - Ngày yêu cầu hoàn tiền.
     - Trạng thái kích hoạt của sản phẩm (đã kích hoạt hay chưa kích hoạt).
   - **Bắt buộc**: Nếu thiếu bất kỳ thông tin nào trong 3 thông tin trên (ví dụ chưa rõ ngày mua, ngày yêu cầu, hoặc chưa rõ trạng thái kích hoạt), **PHẢI hỏi lại người dùng để làm rõ trước khi đưa ra kết luận**. Không được tự tiện giả định hay đoán trạng thái (ví dụ không tự giả định "chưa kích hoạt").

2. **Tìm kiếm tài liệu chính sách**:
   - Sử dụng tool `list_files` với thư mục `data/policies` để liệt kê tất cả các file chính sách đang có trong hệ thống (ngay cả khi tên file bị thay đổi).
   - Tuyệt đối không dùng tên file cố định nếu chưa liệt kê qua `list_files`.

3. **Đọc và xác định chính sách phù hợp**:
   - Dùng tool `read_file` để đọc nội dung các file chính sách tìm được trong `data/policies/`.
   - Kiểm tra phạm vi hiệu lực (thời gian áp dụng) ghi trong từng file chính sách đối chiếu với **ngày mua hàng** của khách để chọn đúng chính sách áp dụng.
   - Đọc kỹ các điều khoản: giới hạn số ngày được hoàn tiền kể từ ngày mua, mức phí hoàn tiền (nếu có), và điều kiện về trạng thái kích hoạt sản phẩm.

4. **Đọc mẫu câu trả lời chuẩn (Template)**:
   - Dùng `read_file` đọc tài liệu tham khảo tại `skills/refund-policy/references/answer-template.md`.

5. **Tính toán và kết luận**:
   - Tính số ngày chênh lệch lịch giữa ngày yêu cầu hoàn tiền và ngày mua hàng (số ngày = ngày yêu cầu - ngày mua). Quy ước: bằng đúng giới hạn thời gian vẫn đủ điều kiện. Dùng ngày yêu cầu trong câu hỏi, không dùng ngày hiện tại của máy.
   - So sánh với điều kiện của chính sách đã chọn:
     - Nếu sản phẩm đã kích hoạt: không được hoàn tiền.
     - Nếu số ngày vượt quá thời hạn cho phép: không được hoàn tiền (quá hạn).
     - Nếu thỏa mãn cả về thời gian và trạng thái kích hoạt: đủ điều kiện hoàn tiền, nêu rõ mức phí (hoặc không thu phí) theo chính sách.

6. **Trả lời người dùng**:
   - Trình bày câu trả lời theo đúng cấu trúc quy định trong `references/answer-template.md`, bao gồm:
     - Chính sách áp dụng
     - Số ngày đã qua (tính từ ngày mua đến ngày yêu cầu)
     - Kết luận (Đủ điều kiện hoặc Không đủ điều kiện)
     - Phí hoàn tiền (nếu đủ điều kiện)
     - Căn cứ tài liệu (đường dẫn tương đối của file chính sách đã sử dụng)
