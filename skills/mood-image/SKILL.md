---
name: mood-image
description: >
  根据用户输入的文本（日记、随笔、心情记录等）分析情绪色彩，生成一张匹配心情的图片。
  当用户提到"心情图片"、"情绪配图"、"日记配图"、"根据心情生成图片"、"mood image"、
  "心情可视化"或提供了文本并希望得到一张表达情绪的图片时，必须使用此 Skill。
  即使没有明确说"生成图片"，只要用户分享了日记/心情文字并暗示想要视觉化表达，也应触发。
---

# 心情图片生成

根据用户输入的文本分析情绪，调用 StepFun 图片生成 API 创建匹配心情的艺术图片。

## 前置条件

- 环境变量 `STEP_API_KEY` 必须已设置（StepFun 开放平台 API Key）
- 需要安装 `requests` 库：`pip install requests --break-system-packages`

## 工作流程

### 第一步：接收并理解用户文本

仔细阅读用户提供的文本。用户的文本可能是：
- 日记（记录一天的经历和感受）
- 随笔 / 碎碎念
- 心情记录
- 任何带有情绪色彩的文字

文本来源可能是用户直接输入，也可能是飞书云文档链接（需先通过 `lark-cli docs +fetch` 获取内容）。

### 第二步：提取核心意象

不要逐字翻译文本，而是提炼出**最核心、最抽象的意象**。问自己：

- 这段文字如果变成一种颜色，是什么颜色？
- 如果变成一种光，是什么质感的光？
- 如果变成一个动作，是升腾、沉落、扩散还是凝聚？
- 最打动人的那一个瞬间或比喻是什么？

将意象提炼为 1-2 句抽象描述，例如：
- "暂停后的苏醒，疲惫的身体像被重新充电般发光"
- "雨夜里一个人与世界的疏离感"
- "夕阳下终于放下的释然"

### 第三步：构建英文 Prompt

**prompt 长度严格控制在 512 字符以内（StepFun API 实际限制）。**

按照以下 5 段式模板构建 Prompt，每段用逗号分隔，整体控制在 30-80 个英文单词：

#### Prompt 模板

```
In the style of Antoine Paikert, [色彩弥散描述 + 颗粒质感], [核心意象的抽象视觉化], [构图与配色], [排除项]. artistic mixed media digital art.
```

#### 各段填写指引

**1. 艺术风格声明**（固定开头）：
```
In the style of Antoine Paikert,
```

**2. 色彩弥散 + 颗粒质感**（根据情绪选择配色）：
- 喜悦/温暖 → `soft color diffusion with warm amber and golden gradients, fine vintage grain texture overlay`
- 忧伤/孤独 → `soft color diffusion with cool blue and lavender gradients, fine vintage grain texture overlay`
- 平静/安宁 → `soft color diffusion with pale sage and cream gradients, fine vintage grain texture overlay`
- 焦虑/紧张 → `soft color diffusion with deep grey and muted red gradients, fine vintage grain texture overlay`
- 希望/憧憬 → `soft color diffusion with warm peach and soft gold gradients, fine vintage grain texture overlay`
- 沉思/迷茫 → `soft color diffusion with misty violet and silver gradients, fine vintage grain texture overlay`
- 复杂/混合 → `soft color diffusion with layered warm and cool gradients, fine vintage grain texture overlay`

**3. 核心意象的抽象视觉化**（将第二步的意象转为抽象光斑/能量体描述）：
- 不要出现具体物体（人、桌子、电脑等）
- 使用流动的、象征性的语言：`a luminous abstract energy form gently rising`、`soft diffused light slowly expanding outward`、`a warm glow dissolving into mist`
- 关键词：luminous, abstract, energy form, glow, light, diffusion, dissolving, floating, emerging

**4. 构图与配色**：
- 固定元素：`Asymmetric composition with vast serene negative space.`
- 配色：`Muted Mediterranean palette, dreamy ethereal atmosphere.`

**5. 排除项**（固定）：
```
No sharp edges, no text, no geometric shapes,
```

**6. 结尾**（固定）：
```
artistic mixed media digital art.
```

#### 完整示例

用户文本："今天下班路上看到夕阳，突然觉得很幸福，虽然工作很累，但这一刻一切都值得了。"

核心意象：疲惫后遇见温暖光芒的瞬间感动

→ Prompt:
```
In the style of Antoine Paikert, soft color diffusion with warm amber and golden gradients, fine vintage grain texture overlay. A luminous warm glow gently expanding outward like the last ray of sunset, symbolizing hard-earned happiness and quiet gratitude. Asymmetric composition with vast serene negative space. Muted Mediterranean palette, dreamy ethereal atmosphere. No sharp edges, no text, no geometric shapes, artistic mixed media digital art.
```

用户文本："又是一个人吃饭，窗外的雨下个不停，好像整个世界都把我忘了。"

核心意象：雨夜中一个人与世界的疏离感

→ Prompt:
```
In the style of Antoine Paikert, soft color diffusion with cool blue and lavender gradients, fine vintage grain texture overlay. A soft diffused light slowly fading into mist, like a solitary presence dissolving into rain and silence. Asymmetric composition with vast serene negative space. Muted Mediterranean palette, dreamy ethereal atmosphere. No sharp edges, no text, no geometric shapes, artistic mixed media digital art.
```

### 第四步：调用生图脚本

使用以下命令生成图片：

```bash
python3 <skill_path>/scripts/generate_image.py \
  --prompt "<构建好的英文 Prompt>" \
  --output "<输出路径>" \
  --size "1280x800"
```

**参数说明**：
- `--prompt`：第三步构建的英文 Prompt（≤512 字符）
- `--output`：图片保存路径，建议保存到用户工作区，文件名可用 `mood_<时间戳>.png`
- `--size`：默认 `1280x800`（4:3 横版画幅），也支持 `1024x1024`（正方形）和 `800x1280`（竖版）
- `--seed`：可选，指定随机种子以获得可复现的结果
- `--steps`：可选，默认 50，更高的值（如 80-100）可能提升细节但更慢
- `--cfg-scale`：可选，默认 7.5，控制 Prompt 遵循度

### 第五步：呈现结果

将生成的图片展示给用户，并附上一段简短的情绪解读，格式如下：

```
🎨 **心情图片已生成**

**情绪解读**：[1-2 句话概括你从文本中感受到的情绪]

[图片]

💡 如果图片风格或氛围不太对，可以告诉我你想要调整的方向，我会重新生成。
```

## 注意事项

- 如果用户没有提供文本，主动询问用户想分享什么文字或心情
- 如果 `STEP_API_KEY` 未设置，友好地提示用户如何获取和配置
- 如果 API 返回 `content_filtered`，告知用户并建议调整 Prompt 中的描述
- 生成的图片应保存到用户的工作区目录（workspace），而非临时目录
- 如果用户对结果不满意，可以根据反馈调整 Prompt 中的色彩或意象描述后重新生成
- Prompt 必须严格 ≤512 字符，构建时注意精简
