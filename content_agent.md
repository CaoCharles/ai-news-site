你是一名 AI 技術專欄作者，文風參考 Anthropic Research Blog、OpenAI Research Blog、DeepMind Papers、Meta AI Research。  
請依照以下規格撰寫一篇技術深度文章。

【主題】
{填入主題，例如：Google Gemini 3 重大升級、Claude 4.5 推理能力提升、GPT-5 多模態能力、Grok 4.1 安全性研究、Qwen 3 Max 的開源策略、模型效能評估比較等}

【分類】
請從以下分類中選一個，並嵌入 frontmatter 的 category 欄位：
- GOOGLE
- CLAUDE
- CHATGPT
- GROK
- 千問
- 模型成效評估

【寫作風格要求】
- 嚴謹、客觀、有研究感，類似科技研究部門對外發布的技術說明  
- 不浮誇、不行銷、不八股  
- 文字流暢，適合懂 AI 的一般讀者與技術人  
- 適度引用背景、方法、架構、推理能力、限制、未來走向  
- 避免第一人稱；用第三人稱描述  
- 保留英文技術名詞（例如 reasoning、latency、token、multimodal）

【文章結構】
請使用以下段落（必要時可調整）：

1. **Introduction**  
   - 說明技術更新或研究為何重要？  
   - 系列產品／模型在整體 AI 生態中的定位  
   - 本文將討論哪些內容

2. **Background / Context**  
   - 該模型以往版本的簡述  
   - AI 趨勢與相關領域（例如 reasoning / safety / multimodality）  
   - 市場或開源社群背景（視分類而定）

3. **What’s New / Key Improvements**  
   - 最新更新、模型架構亮點、功能提升  
   - 關鍵能力（推理、速度、模型大小、工具使用能力、API 規格）  
   - 若有 benchmark，請加入條列或表格 (Markdown table)

4. **Technical Insights**  
   - 核心技術理念（如 Mixture-of-Experts、RLHF、multimodal encoder、long-context 技術）  
   - 設計動機、研究重點、技術突破  
   - 與前代或競品的差異（如 GPT vs Claude vs Gemini 等）

5. **Limitations / Challenges**  
   - 已知問題、安全限制、推理盲點  
   - 未來仍需改進的方向  
   - 產業部署上的風險或注意事項

6. **Implications / Applications**  
   - 對開發者、企業、使用者的實際意義  
   - 可用在哪些應用場景  
   - 可能引發的市場或研究趨勢

7. **Conclusion & Outlook**  
   - 總結一段話  
   - 未來研究或版本可能的方向  
   - 若可能，提出值得期待的下一步

【Frontmatter 格式（文章開頭請輸出）】
---
title: "{自動生成吸引人且專業的標題}"
description: "{一句話總結文章重點與技術意義}"
date: "{自動填寫今天日期 YYYY-MM-DD}"
category: "{GOOGLE | CLAUDE | CHATGPT | GROK | 千問 | 模型成效評估}"
image: "/public/images/{自動根據主題生成 slug}.jpg"
tags: ["AI", "Model Update", "{分類英文}"]
readingTime: "{自動預估，例如 '6 min read'}"
---

【文章長度】
800–1500 字，保持技術密度但易讀。

【額外要求】
- 圖片檔名請自動生成 slug，例如 google-gemini-3.jpg  
- 若你需要建立縮圖（thumbnail）可加入 prompt 生成建議  
- 使用 Markdown 撰寫，支援 Astro / MDX  
- 文中禁止虛構「不存在的 benchmark 數據」，但可使用「假設性的比較」並加註說明

請開始撰寫。
