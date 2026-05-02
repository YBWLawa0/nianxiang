---
name: step-tts-voice
version: 1.0.0
description: "使用 StepFun StepAudio 2.5 TTS API 生成语音。支持音色复刻（上传用户语音样本克隆声音）和文本转语音。当用户需要生成语音、克隆声音、用 AI 朗读文本、制作配音、将文档转为语音、text-to-speech、TTS、voice clone、声音复刻时使用。"
metadata:
  requires:
    env: ["STEP_API_KEY"]
---

# StepFun TTS 语音生成

基于 StepFun StepAudio 2.5 TTS API，支持音色复刻和文本转语音。

## 前置条件

- 环境变量 `STEP_API_KEY` 必须已设置（StepFun 开放平台 API Key）
- Python 3.8+ 和 `requests` 库
- 超长文本拼接需要 `pydub` 和 `ffmpeg`

## 工作流程

### 场景一：音色复刻 + TTS 合成（用户语音 → 朗读文本）

当用户提供了**语音样本**和**待朗读文本**时，执行完整流程：

1. **获取语音样本** — 用户上传音频文件（mp3/wav，5~10 秒）或从飞书消息/文档中提取音频
2. **上传音频到 StepFun** — 调用 `scripts/step_tts.py upload` 上传文件，获取 `file_id`
3. **复刻音色** — 调用 `scripts/step_tts.py clone_voice` 创建音色，获取 `voice_id`
4. **获取待朗读文本** — 从飞书云文档读取内容，或使用用户直接输入的文本
5. **生成语音** — 调用 `scripts/step_tts.py synthesize` 合成音频（自动处理超长文本分段拼接）
6. **输出结果** — 将生成的音频文件保存到用户工作区

### 场景二：直接 TTS 合成（使用已有音色或官方音色）

当用户只提供文本、不需要音色复刻时：

1. **获取待朗读文本** — 从飞书云文档读取或用户直接输入
2. **生成语音** — 调用 `scripts/step_tts.py synthesize`，使用官方音色或用户指定的 `voice_id`
3. **输出结果** — 将生成的音频文件保存到用户工作区

### 场景三：仅复刻音色（预览效果）

当用户只想复刻音色并试听效果时：

1. **获取语音样本**
2. **上传 + 复刻** — 调用 `scripts/step_tts.py preview_voice` 试听复刻效果

## 核心脚本

所有 API 交互通过 `scripts/step_tts.py` 完成。脚本位于 Skill 目录下，运行时需要先 `cd` 到 Skill 目录或使用完整路径。

```bash
# 上传音频文件（获取 file_id）
python scripts/step_tts.py upload --file <音频文件路径>

# 复刻音色（获取 voice_id）
python scripts/step_tts.py clone_voice --file-id <file_id> [--text "音频对应文本"] [--sample-text "试听文本"]

# 试听复刻效果（不创建正式音色）
python scripts/step_tts.py preview_voice --file-id <file_id> [--text "音频对应文本"] [--sample-text "试听文本"]

# 查询已有音色列表
python scripts/step_tts.py list_voices

# 合成语音（支持超长文本自动分段）
python scripts/step_tts.py synthesize \
  --voice <voice_id 或 官方音色名> \
  --text "待朗读文本" \
  [--instruction "全局语气指令，如：语气温柔，语速偏慢"] \
  [--output output.mp3] \
  [--format mp3] \
  [--speed 1.0]

# 一键流程：上传 + 复刻 + 合成
python scripts/step_tts.py full_pipeline \
  --audio <语音样本路径> \
  --text "待朗读文本" \
  [--instruction "全局语气指令"] \
  [--output output.mp3]
```

## 关键参数说明

### instruction（全局语境控制）
StepAudio 2.5 独有功能，用自然语言描述整段音频的情绪基调（最多 200 字符）：
- `"语气温柔，语速偏慢"`
- `"声音极度紧绷，像在拼命压住快要失控的狂喜；语速快而断续"`
- `"语气冰冷，压迫感强，语速偏慢"`

### 文中语境控制
在文本中用 `()` 插入局部指令，括号内容不会被朗读：
- `"（压低声音）喂……你看我手机。（短促吸气）是不是我眼花了？"`

### 官方音色
常用音色名：`cixingnansheng`（磁性男声）、`cixingnvsheng`（磁性女声）等。
完整列表参考：https://platform.stepfun.com/docs/zh/guides/developer/tts#%E6%94%AF%E6%8C%81%E9%9F%B3%E8%89%B2

## 文本来源处理

### 飞书云文档
当用户提供飞书文档链接时，使用 `lark-doc` skill 读取文档内容：
1. 从链接提取 `document_id` 或 `token`
2. 调用 `lark-cli doc get --id <token>` 获取文档文本
3. 清理文本中的 Markdown 格式标记（标题符号、链接语法等）
4. 将纯文本传入 TTS 合成

### 直接输入文本
用户直接粘贴或输入的文本，清理后直接使用。

## 超长文本处理

单次合成上限 1000 字符。脚本会自动：
1. 按句子边界（句号、问号、感叹号、换行符）分割文本
2. 每段不超过 900 字符（留安全余量）
3. 分段调用 API 合成
4. 使用 pydub 无缝拼接所有音频片段
5. 输出完整音频文件

## 注意事项

- 语音样本时长必须在 5~10 秒之间，格式为 mp3 或 wav
- 复刻音色收费 9.9 元/个，合成收费 5.8 元/万字符
- 如果依赖缺失，先安装：`pip install requests pydub --break-system-packages` 和 `apt-get install -y ffmpeg`
