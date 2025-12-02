# Multi-Agent 自動內容更新系統

## 系統概述

這是一個基於 Claude AI 的多智能體協作系統，用於自動化 AI News 網站的內容生成、審查和發布流程。

### 核心組件

1. **Reporter Agents (小記者群組)** - 5 個專門記者
   - Google Reporter
   - Claude Reporter
   - ChatGPT Reporter
   - Grok Reporter
   - Qianwen Reporter

2. **Research Expert Agent (研究專家)** - 模型評測分析

3. **Editor-in-Chief Agent (總編輯)** - 質量控制和校對

### 工作流程

```
發現 → 撰寫 → 審查 → 發布
  ↓       ↓       ↓       ↓
爬取    生成    校對    Git
資訊    文章    修改    提交
```

## 快速開始

### 1. 安裝依賴

```bash
cd agents
pip install -r requirements.txt
```

### 2. 配置環境變量

創建 `.env` 文件：

```bash
# Anthropic API Key
ANTHROPIC_API_KEY=your_api_key_here

# Git 配置
GIT_ENABLED=true
AUTO_PUBLISH=false

# 通知配置 (可選)
SLACK_WEBHOOK_URL=
```

### 3. 配置系統

編輯 `agents/config.json` 調整系統參數：

```json
{
  "git_enabled": true,
  "auto_publish": false,
  "quality_threshold": 7.0,
  "auto_approve_threshold": 9.0
}
```

### 4. 運行系統

#### 交互式模式（推薦用於測試）

```bash
python orchestrator.py
```

#### 運行單次完整週期

```bash
python orchestrator.py cycle
```

#### 守護進程模式（生產環境）

```bash
python orchestrator.py daemon
```

#### 單獨運行特定工作流程

```bash
# 僅運行發現工作流程
python orchestrator.py discovery

# 僅運行審查工作流程
python orchestrator.py review

# 僅運行發布工作流程
python orchestrator.py publish
```

## 詳細使用說明

### Agent 提示詞

每個 Agent 都有專門的提示詞模板：

- `prompts/reporter_prompt.md` - Reporter Agents 指導
- `prompts/research_expert_prompt.md` - Research Expert 指導
- `prompts/editor_prompt.md` - Editor 指導

這些提示詞定義了 Agent 的角色、職責、工作流程和質量標準。

### 自定義 Reporter

如果需要添加新的 Reporter Agent：

```python
from agent_framework import ReporterAgent, Category

class NewModelReporter(ReporterAgent):
    def __init__(self):
        super().__init__(
            name="NewModelReporter",
            category=Category.NEW_CATEGORY,  # 需要先在 Category enum 中添加
            sources=[
                "https://example.com/blog",
                "https://example.com/research"
            ]
        )

# 在 AgentManager 中註冊
manager.reporters["new_model"] = NewModelReporter()
```

### 配置定時任務

系統使用 cron 表達式配置定時任務：

```json
{
  "schedules": {
    "discovery": "0 */6 * * *",   // 每 6 小時
    "research": "0 0 * * 1",      // 每週一午夜
    "review": "0 */2 * * *"       // 每 2 小時
  }
}
```

### 質量控制

#### 自動審查標準

文章會根據以下標準自動評分：

1. **技術準確性** (權重: 40%)
   - 數據來源可靠性
   - 技術描述準確性
   - 引用正確性

2. **內容完整性** (權重: 30%)
   - 結構完整性（7 個必需段落）
   - 字數符合要求（800-1500）
   - Frontmatter 完整性

3. **寫作質量** (權重: 20%)
   - 語言流暢度
   - 邏輯清晰度
   - 可讀性

4. **格式規範** (權重: 10%)
   - Markdown 格式
   - 中英文混排
   - 標點符號

#### 分數閾值

- `quality_threshold: 7.0` - 最低發布標準
- `auto_approve_threshold: 9.0` - 自動批准標準

### Git 工作流程

#### 自動 Git 操作

當 `git_enabled: true` 時，系統會自動：

1. 將已批准的文章保存到 `src/content/posts/`
2. 執行 `git add` 添加新文件
3. 生成合適的 commit 訊息並提交

#### 手動推送模式（推薦）

設置 `auto_publish: false`，系統會準備好 commit 但不會推送：

```bash
# 查看已提交但未推送的文章
git log origin/main..HEAD

# 手動推送
git push origin main
```

#### 自動推送模式（謹慎使用）

設置 `auto_publish: true`，系統會自動推送到遠程倉庫。

**警告**: 僅在充分測試後使用此模式。

## 架構說明

### 目錄結構

```
agents/
├── README.md                    # 本文件
├── requirements.txt             # Python 依賴
├── config.json                  # 系統配置
├── agent_framework.py           # 核心框架
├── orchestrator.py              # 工作流程編排器
├── claude_integration.py        # Claude API 整合
├── web_scraper.py               # 網頁爬取工具
├── prompts/                     # 提示詞模板
│   ├── reporter_prompt.md
│   ├── research_expert_prompt.md
│   └── editor_prompt.md
└── logs/                        # 日誌文件
    └── agent_system.log
```

### 數據流

```
1. Discovery Phase (發現階段)
   Reporter → Web Sources → News Items

2. Creation Phase (創作階段)
   News Items → Claude API → Article Drafts

3. Review Phase (審查階段)
   Article Drafts → Editor Agent → Review Results

4. Publishing Phase (發布階段)
   Approved Articles → Git → GitHub Pages
```

### 事件系統

系統使用事件驅動架構：

- `news_discovered` - 發現新聞
- `draft_submitted` - 提交草稿
- `review_completed` - 完成審查
- `revision_requested` - 要求修改
- `article_published` - 文章發布

## API 整合

### Claude API 使用

系統使用 Anthropic 的 Claude API 進行內容生成和審查：

```python
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# 生成文章
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=4096,
    messages=[{
        "role": "user",
        "content": prompt
    }]
)

content = response.content[0].text
```

### 工具調用 (Tool Use)

Editor Agent 使用 Claude 的工具調用能力進行結構化審查：

```python
tools = [
    {
        "name": "validate_frontmatter",
        "description": "驗證文章 frontmatter 格式",
        "input_schema": {
            "type": "object",
            "properties": {
                "frontmatter": {"type": "object"}
            }
        }
    }
]

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=4096,
    tools=tools,
    messages=[...]
)
```

## 監控和日誌

### 日誌級別

- `INFO` - 正常操作日誌
- `WARNING` - 警告（如配置缺失）
- `ERROR` - 錯誤（如 API 調用失敗）

### 日誌位置

- 控制台輸出
- `logs/agent_system.log`

### 監控指標

系統自動記錄：

- 文章生成數量
- 審查通過率
- 平均處理時間
- API 調用次數和成本
- 錯誤率

查看狀態：

```python
status = manager.get_status()
# {
#   "draft_queue": 3,
#   "review_queue": 2,
#   "approved_articles": 5,
#   "reporters_count": 5
# }
```

## 成本估算

### API 使用成本

基於 Claude Sonnet 4 定價：

- 輸入: $3 / 1M tokens
- 輸出: $15 / 1M tokens

**每篇文章估算**:
- 發現和分析: ~2,000 tokens
- 文章生成: ~4,000 tokens
- 審查和修改: ~3,000 tokens
- 總計: ~9,000 tokens/文章

**月度估算**（每日 6 篇文章）:
- 總 tokens: 6 × 30 × 9,000 = 1,620,000 tokens
- 估算成本: ~$8-12/月

## 故障排除

### 常見問題

#### 1. API Key 錯誤

```
Error: Anthropic API key not found
```

**解決方案**: 設置環境變量 `ANTHROPIC_API_KEY`

#### 2. Git 提交失敗

```
Error: Git operation failed
```

**解決方案**:
- 檢查 Git 配置
- 確保有提交權限
- 檢查工作目錄是否乾淨

#### 3. 文章質量不達標

```
Decision: revision_required
```

**解決方案**:
- 檢查 Reporter 提示詞
- 調整質量閾值
- 手動審查並修改

#### 4. 爬取失敗

```
Error: Failed to fetch from source
```

**解決方案**:
- 檢查網絡連接
- 驗證來源 URL
- 檢查是否需要代理

### 調試模式

啟用詳細日誌：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 最佳實踐

### 1. 開發環境測試

在正式部署前：

1. 設置 `auto_publish: false`
2. 手動審查所有生成的文章
3. 驗證 Git 操作正確
4. 檢查成本消耗

### 2. 漸進式部署

1. 第一週：僅運行發現和生成，不自動發布
2. 第二週：啟用自動審查，人工複查
3. 第三週：啟用自動發布到測試分支
4. 第四週：完全自動化到主分支

### 3. 質量監控

定期檢查：
- 審查通過率
- 讀者反饋
- 技術準確性
- 更新提示詞以改進質量

### 4. 成本控制

- 設置 API 使用限額
- 監控每日 token 消耗
- 優化提示詞以減少 token 使用
- 考慮使用 Claude Haiku 進行簡單任務

## 擴展和自定義

### 添加新的資訊源

編輯 `config.json`:

```json
{
  "reporters": {
    "google": {
      "sources": [
        "https://blog.google/technology/ai/",
        "https://new-source.com"  // 添加新來源
      ]
    }
  }
}
```

### 自定義審查規則

修改 `editor_prompt.md` 添加自定義審查標準。

### 整合通知系統

啟用 Slack 通知：

```json
{
  "notification": {
    "enabled": true,
    "slack_webhook_url": "https://hooks.slack.com/..."
  }
}
```

### 添加人工審查節點

在完全自動化前，可以添加人工審查：

```python
def human_review_required(article, quality_score):
    if quality_score < 8.5:
        return True  # 需要人工審查
    return False
```

## 貢獻指南

如果你想改進此系統：

1. Fork 倉庫
2. 創建功能分支
3. 提交 Pull Request
4. 在 PR 中詳細說明改進內容

## 授權

本系統為 AI News 網站專用。

## 支援

如有問題或建議，請聯繫開發團隊。

---

**最後更新**: 2025-12-02
**版本**: 1.0.0
