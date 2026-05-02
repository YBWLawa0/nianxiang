#!/usr/bin/env python3
"""
StepFun StepAudio 2.5 TTS CLI Tool

支持功能：
- 上传音频文件（用于音色复刻）
- 复刻音色（创建正式音色）
- 试听复刻效果
- 查询已有音色
- 合成语音（自动处理超长文本分段拼接）
- 一键流程（上传 + 复刻 + 合成）

环境变量：
  STEP_API_KEY: StepFun 开放平台 API Key（必需）
"""

import argparse
import base64
import os
import sys
import re
import tempfile
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("错误：需要安装 requests 库")
    print("运行：pip install requests --break-system-packages")
    sys.exit(1)

API_BASE = "https://api.stepfun.com/v1"
MODEL = "stepaudio-2.5-tts"
MAX_CHARS = 1000
CHUNK_SIZE = 900  # 留安全余量


def get_api_key():
    key = os.environ.get("STEP_API_KEY")
    if not key:
        print("错误：未设置环境变量 STEP_API_KEY")
        print("请运行：export STEP_API_KEY='your_api_key'")
        sys.exit(1)
    return key


def get_headers():
    return {
        "Authorization": f"Bearer {get_api_key()}",
        "Content-Type": "application/json",
    }


def upload_file(file_path):
    """上传音频文件到 StepFun，返回 file_id"""
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"错误：文件不存在 - {file_path}")
        sys.exit(1)

    suffix = file_path.suffix.lower()
    if suffix not in [".mp3", ".wav"]:
        print(f"警告：文件格式 {suffix} 可能不被支持，建议使用 mp3 或 wav")

    print(f"正在上传文件：{file_path.name} ...")

    headers = {"Authorization": f"Bearer {get_api_key()}"}
    with open(file_path, "rb") as f:
        resp = requests.post(
            f"{API_BASE}/files",
            headers=headers,
            files={"file": (file_path.name, f)},
            data={"purpose": "storage"},
        )

    if resp.status_code != 200:
        print(f"上传失败：HTTP {resp.status_code}")
        print(resp.text)
        sys.exit(1)

    result = resp.json()
    file_id = result.get("id")
    print(f"上传成功！file_id: {file_id}")
    return file_id


def clone_voice(file_id, text=None, sample_text=None):
    """复刻音色，返回 voice_id"""
    print("正在复刻音色...")
    payload = {
        "model": MODEL,
        "file_id": file_id,
    }
    if text:
        payload["text"] = text
    if sample_text:
        payload["sample_text"] = sample_text

    resp = requests.post(
        f"{API_BASE}/audio/voices",
        headers=get_headers(),
        json=payload,
    )

    if resp.status_code != 200:
        print(f"复刻失败：HTTP {resp.status_code}")
        print(resp.text)
        sys.exit(1)

    result = resp.json()
    voice_id = result.get("id")
    print(f"音色复刻成功！voice_id: {voice_id}")

    if result.get("sample_audio"):
        sample_path = Path("voice_preview.wav")
        sample_path.write_bytes(base64.b64decode(result["sample_audio"]))
        print(f"试听音频已保存：{sample_path}")

    return voice_id


def preview_voice(file_id, text=None, sample_text=None):
    """试听复刻效果（不创建正式音色）"""
    print("正在生成试听音频...")
    payload = {
        "model": MODEL,
        "file_id": file_id,
        "sample_text": sample_text or "今天天气不错，智能阶跃，十倍每一个人的可能。",
    }
    if text:
        payload["text"] = text

    resp = requests.post(
        f"{API_BASE}/audio/voices/preview",
        headers=get_headers(),
        json=payload,
    )

    if resp.status_code != 200:
        print(f"试听失败：HTTP {resp.status_code}")
        print(resp.text)
        sys.exit(1)

    result = resp.json()
    sample_audio = result.get("sample_audio")
    if sample_audio:
        output_path = Path("voice_preview.mp3")
        output_path.write_bytes(base64.b64decode(sample_audio))
        print(f"试听音频已保存：{output_path}")
    else:
        print("试听生成完成，但未返回音频数据")

    return result


def list_voices():
    """查询已有音色列表"""
    print("正在查询已有音色...")
    resp = requests.get(
        f"{API_BASE}/audio/voices",
        headers=get_headers(),
    )

    if resp.status_code != 200:
        print(f"查询失败：HTTP {resp.status_code}")
        print(resp.text)
        sys.exit(1)

    result = resp.json()
    voices = result.get("data", [])
    if not voices:
        print("暂无已复刻的音色")
    else:
        print(f"已有 {len(voices)} 个音色：")
        for v in voices:
            created = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(v.get("created_at", 0)))
            print(f"  - voice_id: {v['id']}  (file_id: {v.get('file_id', 'N/A')}, 创建时间: {created})")
    return voices


def split_text(text, max_chars=CHUNK_SIZE):
    """将长文本按句子边界分割成不超过 max_chars 的段落"""
    paragraphs = text.split("\n")
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(current_chunk) + len(para) + 1 <= max_chars:
            current_chunk = current_chunk + "\n" + para if current_chunk else para
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            if len(para) <= max_chars:
                current_chunk = para
            else:
                sentences = re.split(r'(?<=[。！？；\.\!\?;])', para)
                for sent in sentences:
                    sent = sent.strip()
                    if not sent:
                        continue
                    if len(current_chunk) + len(sent) <= max_chars:
                        current_chunk = current_chunk + sent if current_chunk else sent
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sent
                if current_chunk and len(current_chunk) > max_chars:
                    while current_chunk:
                        chunks.append(current_chunk[:max_chars])
                        current_chunk = current_chunk[max_chars:]

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def synthesize_single(voice, text, instruction=None, response_format="mp3",
                      speed=1.0, volume=1.0, sample_rate=24000):
    """合成单段语音，返回音频二进制数据"""
    payload = {
        "model": MODEL,
        "voice": voice,
        "input": text,
        "response_format": response_format,
    }
    if instruction:
        payload["instruction"] = instruction[:200]
    if speed != 1.0:
        payload["speed"] = speed
    if volume != 1.0:
        payload["volume"] = volume
    if sample_rate != 24000:
        payload["sample_rate"] = sample_rate

    resp = requests.post(
        f"{API_BASE}/audio/speech",
        headers=get_headers(),
        json=payload,
    )

    if resp.status_code != 200:
        print(f"合成失败：HTTP {resp.status_code}")
        print(resp.text)
        return None

    return resp.content


def clean_text(text):
    """清理文本中的 Markdown 格式标记"""
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', text)
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'^[\s]*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[\s]*\d+\.\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def synthesize(voice, text, instruction=None, output="output.mp3",
               response_format="mp3", speed=1.0, volume=1.0, sample_rate=24000):
    """合成语音，自动处理超长文本分段拼接"""
    output_path = Path(output)
    text = clean_text(text)
    total_chars = len(text)
    print(f"文本总长度：{total_chars} 字符")

    if total_chars <= MAX_CHARS:
        print("正在合成语音...")
        audio_data = synthesize_single(
            voice, text, instruction, response_format, speed, volume, sample_rate
        )
        if audio_data:
            output_path.write_bytes(audio_data)
            print(f"语音已保存：{output_path}")
            return str(output_path)
        else:
            print("合成失败")
            sys.exit(1)
    else:
        chunks = split_text(text)
        print(f"文本超过 {MAX_CHARS} 字符，将分为 {len(chunks)} 段合成")

        temp_files = []
        for i, chunk in enumerate(chunks):
            print(f"正在合成第 {i+1}/{len(chunks)} 段（{len(chunk)} 字符）...")
            audio_data = synthesize_single(
                voice, chunk, instruction, response_format, speed, volume, sample_rate
            )
            if not audio_data:
                print(f"第 {i+1} 段合成失败，跳过")
                continue

            temp_file = tempfile.NamedTemporaryFile(
                suffix=f".{response_format}", delete=False
            )
            temp_file.write(audio_data)
            temp_file.close()
            temp_files.append(temp_file.name)

        if not temp_files:
            print("所有分段合成均失败")
            sys.exit(1)

        print("正在拼接音频片段...")
        try:
            from pydub import AudioSegment

            combined = AudioSegment.empty()
            fmt = response_format
            for tf in temp_files:
                segment = AudioSegment.from_file(tf, format=fmt)
                combined += segment

            combined.export(str(output_path), format=fmt)
            print(f"语音已保存：{output_path}（共 {len(combined)/1000:.1f} 秒）")
        except ImportError:
            print("警告：pydub 未安装，无法拼接多段音频")
            print("安装方法：pip install pydub --break-system-packages")
            print("同时需要 ffmpeg：apt-get install -y ffmpeg")
            import shutil
            shutil.copy2(temp_files[0], str(output_path))
            print(f"仅保存了第一段音频：{output_path}")
        finally:
            for tf in temp_files:
                try:
                    os.unlink(tf)
                except Exception:
                    pass

        return str(output_path)


def full_pipeline(audio_path, text, instruction=None, output="output.mp3",
                  response_format="mp3", speed=1.0):
    """一键流程：上传音频 → 复刻音色 → 合成语音"""
    print("=" * 50)
    print("StepFun TTS 一键流程")
    print("=" * 50)

    print("\n[1/3] 上传语音样本...")
    file_id = upload_file(audio_path)

    print("\n[2/3] 复刻音色...")
    voice_id = clone_voice(file_id)

    print(f"\n[3/3] 合成语音（使用音色 {voice_id}）...")
    result = synthesize(
        voice=voice_id,
        text=text,
        instruction=instruction,
        output=output,
        response_format=response_format,
        speed=speed,
    )

    print("\n" + "=" * 50)
    print(f"完成！输出文件：{result}")
    print("=" * 50)
    return result


def main():
    parser = argparse.ArgumentParser(
        description="StepFun StepAudio 2.5 TTS CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # upload
    p_upload = subparsers.add_parser("upload", help="上传音频文件")
    p_upload.add_argument("--file", required=True, help="音频文件路径（mp3/wav）")

    # clone_voice
    p_clone = subparsers.add_parser("clone_voice", help="复刻音色")
    p_clone.add_argument("--file-id", required=True, help="已上传文件的 file_id")
    p_clone.add_argument("--text", help="音频对应的文本内容（建议提供）")
    p_clone.add_argument("--sample-text", help="试听文本（最多50字）")

    # preview_voice
    p_preview = subparsers.add_parser("preview_voice", help="试听复刻效果")
    p_preview.add_argument("--file-id", required=True, help="已上传文件的 file_id")
    p_preview.add_argument("--text", help="音频对应的文本内容")
    p_preview.add_argument("--sample-text", help="试听文本（最多50字）")

    # list_voices
    subparsers.add_parser("list_voices", help="查询已有音色")

    # synthesize
    p_synth = subparsers.add_parser("synthesize", help="合成语音")
    p_synth.add_argument("--voice", required=True, help="音色 ID 或官方音色名")
    p_synth.add_argument("--text", required=True, help="待朗读文本")
    p_synth.add_argument("--instruction", help="全局语气指令（最多200字）")
    p_synth.add_argument("--output", default="output.mp3", help="输出文件路径")
    p_synth.add_argument("--format", default="mp3", help="音频格式（mp3/wav/flac/opus/pcm）")
    p_synth.add_argument("--speed", type=float, default=1.0, help="语速（0.5~2.0）")
    p_synth.add_argument("--volume", type=float, default=1.0, help="音量（0.1~2.0）")
    p_synth.add_argument("--sample-rate", type=int, default=24000, help="采样率")

    # full_pipeline
    p_full = subparsers.add_parser("full_pipeline", help="一键流程：上传+复刻+合成")
    p_full.add_argument("--audio", required=True, help="语音样本路径（mp3/wav，5~10秒）")
    p_full.add_argument("--text", required=True, help="待朗读文本")
    p_full.add_argument("--instruction", help="全局语气指令")
    p_full.add_argument("--output", default="output.mp3", help="输出文件路径")
    p_full.add_argument("--format", default="mp3", help="音频格式")
    p_full.add_argument("--speed", type=float, default=1.0, help="语速")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "upload":
        upload_file(args.file)
    elif args.command == "clone_voice":
        clone_voice(args.file_id, args.text, args.sample_text)
    elif args.command == "preview_voice":
        preview_voice(args.file_id, args.text, args.sample_text)
    elif args.command == "list_voices":
        list_voices()
    elif args.command == "synthesize":
        synthesize(
            voice=args.voice,
            text=args.text,
            instruction=args.instruction,
            output=args.output,
            response_format=args.format,
            speed=args.speed,
            volume=args.volume,
            sample_rate=args.sample_rate,
        )
    elif args.command == "full_pipeline":
        full_pipeline(
            audio_path=args.audio,
            text=args.text,
            instruction=args.instruction,
            output=args.output,
            response_format=args.format,
            speed=args.speed,
        )


if __name__ == "__main__":
    main()
