# Configuring Hermes Agent for Vision Model Routing

## 1. Thêm OpenAI API Key

```bash
# ~/.zshrc hoặc ~/.bashrc
export OPENAI_API_KEY=sk-...your-key-here...
```

Sau đó reload: `source ~/.zshrc`

## 2. Cập nhật Hermes config.yaml

Thêm 2 thay đổi vào `~/.hermes/config.yaml`:

### A. Configure auxiliary.vision (dùng GPT-4o cho vision tool)

```yaml
auxiliary:
  vision:
    provider: openai          # ← Sửa từ 'auto' thành 'openai'
    model: gpt-4o             # ← Thêm model
    base_url: ''              # Mặc định (api.openai.com)
    api_key: ''               # Để trống → Hermes đọc từ env OPENAI_API_KEY
    timeout: 120
```

Hoặc dùng `hermes config set`:
```bash
hermes config set auxiliary.vision.provider openai
hermes config set auxiliary.vision.model gpt-4o
```

### B. Optional: Thêm OpenAI provider cho model routing

Nếu muốn route riêng skill/tool nào đó dùng GPT-4o (không chỉ vision), thêm provider:

```yaml
custom_providers:
  - name: openai
    base_url: https://api.openai.com/v1
    api_key: ${OPENAI_API_KEY}   # Hermes tự động đọc từ env
```

## 3. Verify config

```bash
# Kiểm tra config vision
hermes config get auxiliary.vision

# Test vision hoạt động
hermes run --tool vision "Mô tả ảnh này: path/to/test.jpg"
```

## 4. Cách Hermes routing hoạt động

```
┌───────────────────────────────────────────────────┐
│  Hermes Agent Routing                              │
│                                                     │
│  Chat model (mặc định)                              │
│    → oc/deepseek-v4-flash-free (9router)            │
│                                                     │
│  Vision tasks (khi gọi vision tool hoặc analyze)    │
│    → auxiliary.vision → openai/gpt-4o               │
│                                                     │
│  Tool routing (nếu config tool-level)               │
│    → Có thể chỉ định provider/model per-tool        │
└───────────────────────────────────────────────────┘
```

## 5. Video Analyzer Skill Usage

Sau khi config xong, dùng `video-analyzer` skill:

```bash
# Load skill
hermes skill load video-analyzer

# Phân tích video
python3 ~/.hermes/skills/shorts/video-analyzer/scripts/analyze_video.py output/video.mp4 --verbose

# Tích hợp vào pipeline
python3 ~/.hermes/skills/shorts/video-analyzer/scripts/analyze_video.py output/video.mp4 -o output/analysis/video-01.json
```

## Flow tổng thể

```
Video render xong
    │
    ▼
video-analyzer (skill)
    │
    ├── ffmpeg scene detect → keyframes (3-5 frames)
    ├── GPT-4o Vision API → JSON analysis
    └── Kết quả: quality, OCR, HEIT compliance
    │
    ▼
Quyết định:
    ✅ Pass → upload lên YouTube
    ❌ Fail → log lỗi, không upload
```
