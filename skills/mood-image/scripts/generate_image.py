#!/usr/bin/env python3
"""
StepFun Image Generation CLI Tool

根据情绪分析结果，调用 StepFun step-1x-medium 模型生成心情图片。

环境变量：
  STEP_API_KEY: StepFun 开放平台 API Key（必需）

用法：
  python generate_image.py --prompt "A serene lake at sunrise..." --output mood.png
  python generate_image.py --prompt "..." --size 1280x800 --seed 42
"""

import argparse
import base64
import os
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("错误：需要安装 requests 库")
    print("运行：pip install requests --break-system-packages")
    sys.exit(1)

API_BASE = "https://api.stepfun.com/v1"
MODEL = "step-1x-medium"

VALID_SIZES = [
    "256x256", "512x512", "768x768", "512x512",
    "1280x800", "800x1280",
]


def get_api_key():
    key = os.environ.get("STEP_API_KEY")
    if not key:
        print("错误：未设置环境变量 STEP_API_KEY")
        print("请运行：export STEP_API_KEY='your_api_key'")
        sys.exit(1)
    return key


def generate_image(
    prompt: str,
    output: str = "mood_image.png",
    size: str = "512x512",
    seed: int = 0,
    steps: int = 50,
    cfg_scale: float = 7.5,
    response_format: str = "b64_json",
    style_reference_url: str = None,
    style_reference_weight: float = 1.0,
):
    """
    调用 StepFun API 生成图片并保存到本地。

    Args:
        prompt: 图片描述文本（英文，最多 512 字符）
        output: 输出文件路径
        size: 图片尺寸
        seed: 随机种子（0 为随机）
        steps: 生成步数（1-100）
        cfg_scale: CFG 引导系数（1-10）
        response_format: 返回格式（b64_json 或 url）
        style_reference_url: 风格参考图片 URL
        style_reference_weight: 风格参考权重（0-2]
    """
    if size not in VALID_SIZES:
        print(f"错误：不支持的尺寸 '{size}'")
        print(f"支持的尺寸：{', '.join(VALID_SIZES)}")
        sys.exit(1)

    if len(prompt) > 512:
        print(f"警告：prompt 超过 512 字符（当前 {len(prompt)}），将截断")
        prompt = prompt[:512]

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "size": size,
        "n": 1,
        "response_format": response_format,
    }

    if seed != 0:
        payload["seed"] = seed
    if steps != 50:
        payload["steps"] = steps
    if cfg_scale != 7.5:
        payload["cfg_scale"] = cfg_scale

    if style_reference_url:
        payload["style_reference"] = {
            "source_url": style_reference_url,
            "weight": style_reference_weight,
        }

    headers = {
        "Authorization": f"Bearer {get_api_key()}",
        "Content-Type": "application/json",
    }

    print(f"正在生成图片...")
    print(f"  模型: {MODEL}")
    print(f"  尺寸: {size}")
    print(f"  Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")

    resp = requests.post(
        f"{API_BASE}/images/generations",
        headers=headers,
        json=payload,
        timeout=120,
    )

    if resp.status_code != 200:
        print(f"生成失败：HTTP {resp.status_code}")
        print(resp.text)
        sys.exit(1)

    result = resp.json()
    data_raw = result.get("data", result)
    data_list = data_raw if isinstance(data_raw, list) else [data_raw]

    if not data_list:
        print("错误：API 未返回图片数据")
        sys.exit(1)

    item = data_list[0]
    finish_reason = item.get("finish_reason", "")

    if finish_reason == "content_filtered":
        print("警告：图片生成命中内容安全检测，已过滤")
        print("建议修改 prompt 后重试")
        sys.exit(1)

    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if response_format == "b64_json" and "image" in item:
        image_data = base64.b64decode(item["image"])
        output_path.write_bytes(image_data)
    elif response_format == "url" and "url" in item:
        print(f"正在下载图片：{item['url']}")
        img_resp = requests.get(item["url"], timeout=60)
        if img_resp.status_code != 200:
            print(f"下载失败：HTTP {img_resp.status_code}")
            sys.exit(1)
        output_path.write_bytes(img_resp.content)
    else:
        print("错误：未找到图片数据")
        sys.exit(1)

    actual_seed = item.get("seed", seed)
    print(f"图片已保存：{output_path}")
    print(f"  Seed: {actual_seed}")
    print(f"  文件大小：{output_path.stat().st_size / 512:.1f} KB")

    return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="StepFun Image Generation - 心情图片生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--prompt", required=True, help="图片描述文本（英文，最多 512 字符）")
    parser.add_argument("--output", default="mood_image.png", help="输出文件路径（默认：mood_image.png）")
    parser.add_argument("--size", default="512x512", help="图片尺寸（默认：512x512）")
    parser.add_argument("--seed", type=int, default=0, help="随机种子（0 为随机）")
    parser.add_argument("--steps", type=int, default=50, help="生成步数 1-100（默认：50）")
    parser.add_argument("--cfg-scale", type=float, default=7.5, help="CFG 系数 1-10（默认：7.5）")
    parser.add_argument("--format", default="b64_json", choices=["b64_json", "url"], help="返回格式（默认：b64_json）")
    parser.add_argument("--style-url", help="风格参考图片 URL")
    parser.add_argument("--style-weight", type=float, default=1.0, help="风格参考权重 0-2（默认：1.0）")

    args = parser.parse_args()

    generate_image(
        prompt=args.prompt,
        output=args.output,
        size=args.size,
        seed=args.seed,
        steps=args.steps,
        cfg_scale=args.cfg_scale,
        response_format=args.format,
        style_reference_url=args.style_url,
        style_reference_weight=args.style_weight,
    )


if __name__ == "__main__":
    main()
