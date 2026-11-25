# Quy tắc đăng video · kênh OKX (LifeProsper Hub)

1. **Chỉ một lịch đăng: bot tự động trên cloud** (báo qua Telegram). Phiên Claude không tự hẹn giờ
   đăng song song trên PostPeer nữa, trừ khi người dùng yêu cầu rõ cho một video cụ thể.
2. **Trước khi đăng hoặc làm video mới, bắt buộc kiểm trùng tiêu đề và nội dung** (từ khóa được dùng lại):
   ```
   python3 tools/check-trung.py --dir kenh-okx/video-ngan/<thư-mục>
   python3 tools/check-trung.py "<tiêu đề dự kiến>" --kw "<từ khóa chính>"
   ```
   Lệnh so với **mọi video đang có trên kênh** (trang Video, Shorts, RSS) và mọi `post.json` đã làm.
   Báo ✗ (thoát mã 1) thì **không đăng**: viết tiêu đề mới (khác hẳn phần sau từ khóa) và nội dung mới,
   rồi kiểm lại tới khi ✓. ⚠ "cùng từ khóa" chỉ để biết, vẫn được đăng.
3. Được dùng chung từ khóa (kể cả giữa Short và video dài), nhưng tiêu đề, góc kể và lời đọc phải mới; ưu tiên từ khóa chưa dùng khi còn.
4. **Việc làm tay bắt buộc** trong YouTube Studio sau khi mỗi video lên kênh:
   - Ghim bình luận đầu (có mã; video dài có thêm link).
   - Short: mục "Video liên quan" → gắn video dài cùng chủ đề.
   - Tick "Quảng cáo có trả tiền", thêm vào playlist.
   - TikTok: bật "Nội dung có thương hiệu".
5. **Video tin tức: ưu tiên sự kiện, thông báo, sản phẩm mới của OKX** (tin loại "về OKX"), tin thị trường chung chỉ dùng khi không có tin OKX phù hợp.
6. **Nhiều key PostPeer**: đăng bằng `node tools/pp-xoay.mjs dang <thư-mục> …` (tự kiểm trùng, tự chọn key còn đủ lượt).
   `node tools/pp-xoay.mjs xem` để xem lượt còn lại. Key nằm ở `~/.affiliate-postpeer-keys.json`, không commit.
7. **Giờ đăng**: bot cloud đăng khoảng 08:05 và 20:07 (giờ VN). Video đăng tay đặt ở 12:00 hoặc 15:30, cách giờ bot ≥ 3 tiếng;
   tổng cộng tối đa 4 video/ngày trên YouTube, TikTok tối đa 2 video/ngày.
