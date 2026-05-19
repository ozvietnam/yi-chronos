# Local LLM Setup cho YI-Chronos (Mac M4 36GB)

Anh có máy Mac M4 36GB — đủ sức chạy **2 model 7B-8B song song** để phục chế thư viện **miễn phí, riêng tư, offline**.

## 1. Cài Ollama

```bash
# 1-line install (script chính thức)
curl -fsSL https://ollama.com/install.sh | sh

# hoặc Homebrew
brew install ollama
```

Khởi động server (chạy nền):
```bash
ollama serve  # default port 11434
```

Kiểm tra:
```bash
curl http://localhost:11434/api/tags
# {"models":[]}  ← nghĩa là server OK, chưa pull model
```

## 2. Pull model

Vai trò trong pipeline | Model | Size | Pull command
---|---|---|---
**Cleanup text** (chính) | qwen2.5:7b | 4.7GB | `ollama pull qwen2.5:7b`
**Cleanup text** (chất lượng cao) | qwen2.5:14b | 9GB | `ollama pull qwen2.5:14b`
**OCR Vision** (thay Tesseract) | qwen2.5-vl:7b | 6GB | `ollama pull qwen2.5-vl:7b`
**OCR Chinese specialist** | minicpm-v:8b | 5.5GB | `ollama pull minicpm-v:8b`

Tổng cần ~10-16GB ổ cứng. Em recommend bộ tối thiểu cho phục chế:
```bash
ollama pull qwen2.5:7b        # cleanup
ollama pull qwen2.5-vl:7b     # OCR (chất lượng cao hơn Tesseract nhiều)
```

## 3. Test connectivity

```bash
cd /Users/ozvietnamdesktop/Desktop/yi
python3 -c "
from engine.ai.registry import get_registry
p = get_registry().get('ollama')
print('configured:', p.is_configured)
print('installed:', p.available_models)
"
```

Mong đợi:
```
configured: True
installed: ['qwen2.5:7b', 'qwen2.5-vl:7b']
```

## 4. Test pipeline với local LLM

Phục chế 1 trang Kinh Dịch dùng Qwen2.5 thay DeepSeek:

```bash
python3 -c "
from engine.yi_lexicon.restoration import restore_book, RestorationConfig
cfg = RestorationConfig(
    ocr_backend='qwen-vl',     # vision OCR thay Tesseract
    page_range=(20, 20),
    llm_provider='ollama',
    llm_model='qwen2.5:7b',
    incremental=False,
)
r = restore_book(corpus_id=4, config=cfg)
print(r)
"
```

## 5. Nightly batch (anh đi ngủ — model làm việc)

### Chạy tay
```bash
# Phục chế tier S+A trong 8 tiếng, dùng Ollama + Qwen-VL
python3 -m engine.yi_lexicon.restoration.nightly \
  --max-hours 8 \
  --tiers S A \
  --provider ollama \
  --ocr-backend qwen-vl \
  --pages-per-chunk 20

# Dry-run xem queue trước
python3 -m engine.yi_lexicon.restoration.nightly --dry-run
```

### Lên lịch tự động qua launchd (Mac native)

Tạo `~/Library/LaunchAgents/com.anhduc.yi-nightly.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.anhduc.yi-nightly</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/env</string>
    <string>bash</string>
    <string>-lc</string>
    <string>cd /Users/ozvietnamdesktop/Desktop/yi && python3 -m engine.yi_lexicon.restoration.nightly --max-hours 7 --tiers S A B</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict><key>Hour</key><integer>23</integer><key>Minute</key><integer>0</integer></dict>
  <key>StandardOutPath</key><string>/Users/ozvietnamdesktop/Desktop/yi/data/yi_restored/_logs/launchd.out</string>
  <key>StandardErrorPath</key><string>/Users/ozvietnamdesktop/Desktop/yi/data/yi_restored/_logs/launchd.err</string>
</dict>
</plist>
```

Kích hoạt:
```bash
launchctl load ~/Library/LaunchAgents/com.anhduc.yi-nightly.plist
launchctl start com.anhduc.yi-nightly  # test ngay
```

## 6. Tuning cho Mac M4 36GB

### Kiểm tra resource khi đang chạy
```bash
# CPU/GPU/RAM
sudo powermetrics --samplers cpu_power,gpu_power,thermal -i 5000 -n 5
# RAM theo process
top -o mem
```

### Giới hạn RAM Ollama (tránh swap khi anh dùng máy ban ngày)
```bash
export OLLAMA_KEEP_ALIVE=5m      # unload model sau 5 phút idle
export OLLAMA_MAX_LOADED_MODELS=2  # giữ tối đa 2 model trong RAM
ollama serve
```

### Đẩy max performance khi nightly
```bash
# Trước khi chạy nightly (anh không dùng máy):
export OLLAMA_NUM_PARALLEL=4       # parallel requests
export OLLAMA_KEEP_ALIVE=8h        # giữ model suốt đêm
export OLLAMA_FLASH_ATTENTION=1    # bật Flash Attention (M4 hỗ trợ)
```

## 7. Performance ước tính M4

Model | Quant | RAM | Tok/s | Trang/giờ | Trang/đêm (8h)
---|---|---|---|---|---
qwen2.5:7b | Q4_K_M | 5GB | 45-60 | ~200 | ~1600
qwen2.5:7b | Q5_K_M | 6GB | 38-50 | ~170 | ~1360
qwen2.5:14b | Q4_K_M | 9GB | 22-30 | ~110 | ~880
qwen2.5-vl:7b OCR | Q4 | 6GB | 15-25 | ~120 | ~960

→ **Một đêm 8h** = phục chế xong **~1500 trang text-only** hoặc **~960 trang full OCR+cleanup**.
→ **6 đêm** = thư viện 8400 trang xong (kể cả full OCR vision).

## 8. So sánh local vs cloud

. | Ollama Qwen2.5 7B | DeepSeek-V4-flash
---|---|---
Cost/trang | $0 | ~$0.003
Tốc độ/trang | 15-30s | 60s (cloud rate-limited)
Chất lượng cleanup | 88-92% | 94-96%
Tiếng Việt cổ + Hán | 90% (Qwen train trên Hán) | 93%
Offline | ✓ | ✗
Privacy | ✓ (100% local) | ✗ (gửi lên cloud)

**Khuyến nghị**: Nightly batch = Ollama (free, ngủ rồi). Conflict review = DeepSeek (chất lượng cao, gọi ít, mất ~$5/tháng).

## 9. Troubleshooting

| Lỗi | Nguyên nhân | Cách sửa |
|---|---|---|
| `Ollama unreachable @ http://localhost:11434` | Server chưa chạy | `ollama serve` trong terminal mới |
| `model 'qwen2.5:7b' not found` | Chưa pull | `ollama pull qwen2.5:7b` |
| Tốc độ chậm (<10 tok/s) | Model load lần đầu, hoặc thermal throttle | Đợi 30s, kiểm `powermetrics` |
| Out of memory | Pull model quá lớn | Đổi xuống qwen2.5:7b Q4, không Q8 |
| Kết quả OCR lỗi diacritic | Model VL chưa support tiếng Việt cổ | Thử `minicpm-v:8b` (tốt hơn cho CJK) |

## 10. Verify nightly đã chạy

```bash
# Xem log JSONL
ls -la data/yi_restored/_logs/
tail -f data/yi_restored/_logs/nightly-*.jsonl

# Đếm trang phục chế tổng cộng
python3 -c "
from engine.yi_lexicon.store import library_stats
s = library_stats()
print(f'Tổng: {s[\"pages_ingested\"]} / {s[\"pages_total\"]} trang ({s[\"overall_progress_percent\"]}%)')
"
```
