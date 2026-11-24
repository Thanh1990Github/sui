# Quy tắc đăng video · kênh OKX (LifeProsper Hub)

1. **Chỉ một lịch đăng: bot tự động trên cloud** (báo qua Telegram). Phiên Claude không tự hẹn giờ
   đăng song song trên PostPeer nữa, trừ khi người dùng yêu cầu rõ cho một video cụ thể.
2. **Trước khi đăng hoặc làm video mới, bắt buộc kiểm trùng**:
   ```
   python3 tools/check-trung.py --dir kenh-okx/video-ngan/<thư-mục>
   python3 tools/check-trung.py "<tiêu đề dự kiến>" --kw "<từ khóa chính>"
   ```
   Lệnh so với **mọi video đang có trên kênh** (trang Video, Shorts, RSS) và mọi `post.json` đã làm.
   Báo ✗ (thoát mã 1) thì **không đăng**: chọn từ khóa chưa dùng trong `tu-khoa-okx/okx-90-tu-khoa.csv`,
   viết tiêu đề khác hẳn, rồi kiểm lại tới khi ✓.
3. Short và video dài **không** dùng chung từ khóa chính. Mỗi từ khóa trong bộ 90 chỉ dùng cho một video.
4. **Việc làm tay bắt buộc** trong YouTube Studio sau khi mỗi video lên kênh:
   - Ghim bình luận đầu (có mã; video dài có thêm link).
   - Short: mục "Video liên quan" → gắn video dài cùng chủ đề.
   - Tick "Quảng cáo có trả tiền", thêm vào playlist.
   - TikTok: bật "Nội dung có thương hiệu".
