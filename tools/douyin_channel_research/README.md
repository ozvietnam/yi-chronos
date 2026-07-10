# Douyin Channel Research

Quét một kênh Douyin, trích xuất text gốc, làm sạch và xuất file tổng phục vụ nghiên cứu.

Pipeline ưu tiên theo thứ tự:

1. Phụ đề/subtitle từ `yt-dlp`.
2. OCR thumbnail/poster bằng Tesseract (`chi_sim+eng` mặc định).
3. Audio transcription nếu bật `--transcriber local-whisper` hoặc `--transcriber openai`.
4. Làm sạch deterministic.
5. Làm sạch bằng LLM nếu bật `--llm`.

## Chạy nhanh

```bash
python3 scripts/douyin_channel_research.py scan 'https://www.douyin.com/user/SEC_USER_ID' \
  --limit 20 \
  --jobs 4
```

Khi Douyin yêu cầu đăng nhập/cookie:

```bash
python3 scripts/douyin_channel_research.py scan 'https://www.douyin.com/user/SEC_USER_ID' \
  --cookies /path/to/cookies.txt \
  --jobs 4
```

## Dùng LLM do người dùng chỉ định

API key để trong `.env.local`, không ghi vào repo.

Ví dụ dùng LiteLLM/OpenAI-compatible:

```bash
LITELLM_BASE_URL=https://your-openai-compatible-endpoint/v1
LITELLM_API_KEY=...
LITELLM_MODEL=...
```

Chạy:

```bash
python3 scripts/douyin_channel_research.py scan 'https://www.douyin.com/user/SEC_USER_ID' \
  --jobs 6 \
  --llm \
  --llm-model "$LITELLM_MODEL" \
  --llm-max-output-tokens 900 \
  --target-language original
```

Nếu muốn bản sạch tiếng Việt:

```bash
python3 scripts/douyin_channel_research.py scan 'https://www.douyin.com/user/SEC_USER_ID' \
  --llm \
  --llm-model "$LITELLM_MODEL" \
  --target-language vi
```

## Audio transcription

Local Whisper:

```bash
python3 scripts/douyin_channel_research.py scan 'https://www.douyin.com/user/SEC_USER_ID' \
  --transcriber local-whisper \
  --whisper-model small \
  --jobs 2
```

OpenAI-compatible audio transcription:

```bash
python3 scripts/douyin_channel_research.py scan 'https://www.douyin.com/user/SEC_USER_ID' \
  --transcriber openai
```

## Output

Mặc định lưu tại:

```text
data/research/douyin_transcripts/<channel-slug>/
```

Cấu trúc:

```text
entries.jsonl          # danh sách video từ playlist/channel
manifest.jsonl         # trạng thái từng video
raw/<video_id>.txt     # text gốc
clean/<video_id>.txt   # text đã làm sạch
subtitles/             # phụ đề tải được
images/                # thumbnail/poster
audio/                 # audio nếu bật transcription
final/transcripts.txt  # file tổng, cũ -> mới
final/index.md         # mục lục
final/videos.json      # metadata + đường dẫn text
final/quality_report.md
```

## Ghi chú kỹ thuật

- `--jobs` xử lý nhiều video đồng thời. Với OCR/subtitle có thể để `4-8`; với local Whisper nên để `1-2` để tránh nghẽn CPU.
- Douyin thường chặn request không cookie. Xuất cookie trình duyệt dạng Netscape `cookies.txt` rồi truyền bằng `--cookies`.
- LLM không bắt buộc. Nếu không bật `--llm`, pipeline vẫn xuất text đã làm sạch bằng rule deterministic.
- Không ghi đè text gốc; `raw/` luôn giữ bản trích xuất để kiểm chứng.
