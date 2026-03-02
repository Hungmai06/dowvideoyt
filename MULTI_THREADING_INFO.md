# ⚡ Multi-Threading Download Info

## Đã thêm Threads vào UI!

Hiện tại giao diện đã có option chọn số luồng:
- **⚡ Threads: 1, 2, 3, 4, 5, 8, 10**
- **Mặc định: 3 threads**

## Giải thích:

### Single Thread (1):
```
Video 1 → Video 2 → Video 3 → Video 4 → Video 5
  [====]   [====]   [====]   [====]   [====]
Thời gian: 100%
```

### Multi-Thread (3):
```
Video 1 → Video 4
  [====]   [====]
Video 2 → Video 5  
  [====]   [====]
Video 3
  [====]
Thời gian: ~33% (nhanh gấp 3 lần!)
```

## Lợi ích:

| Threads | Tốc độ | Khuyên dùng khi |
|---------|--------|-----------------|
| 1 | Chậm | Internet yếu, test |
| 2-3 | Cân bằng | Sử dụng thường xuyên ⭐ |
| 4-5 | Nhanh | Internet tốt, nhiều video |
| 8-10 | Rất nhanh | Internet cực tốt, cần gấp |

## ⚠️ Lưu ý:
- **Threads càng nhiều = băng thông càng cao**
- Internet chậm nên dùng 1-2 threads
- YouTube có thể throttle nếu quá nhiều requests đồng thời
- Khuyên dùng: **3 threads** (mặc định)

## Cách dùng:
1. Chọn số threads trong dropdown "⚡ Threads"
2. Bấm "⬇️ Start Download"
3. Các video sẽ tải đồng thời theo số luồng đã chọn!

---

**Version 3.0 - Multi-threading Support** 🚀
