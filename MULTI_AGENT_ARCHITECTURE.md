# Multi-Agent 自動內容更新系統架構

## 系統概述

這是一個基於多智能體協作的自動內容生成和質量控制系統，用於自動更新 AI News 網站的內容。

## 架構設計

### 1. Agent 角色定義

#### 1.1 Reporter Agents (小記者群組)
- **Google Reporter** - 負責 Google Gemini 相關新聞
- **Claude Reporter** - 負責 Anthropic Claude 相關新聞
- **ChatGPT Reporter** - 負責 OpenAI ChatGPT 相關新聞
- **Grok Reporter** - 負責 xAI Grok 相關新聞
- **Qianwen Reporter** - 負責阿里巴巴通義千問相關新聞

**職責:**
- 監控指定模型的官方渠道（官網、博客、論文、社交媒體）
- 爬取和分析最新資訊
- 撰寫符合編輯規範的新聞文章
- 產出 Markdown 格式的文章草稿

#### 1.2 Research Expert Agent (研究專家)
- **職責:**
  - 追蹤主要模型評測基準（MMLU、HumanEval、MATH 等）
  - 分析模型性能對比
  - 撰寫深度評估報告
  - 產出技術分析文章

#### 1.3 Editor-in-Chief Agent (總編輯)
- **職責:**
  - 審查所有文章草稿
  - 檢查是否符合 `content_agent.md` 規範
  - 校對語言、邏輯、結構
  - 驗證技術準確性
  - 決定是否發布或退回修改

---

## 工作流程設計

### Phase 1: Content Discovery (內容發現)
```
Reporter Agents (並行執行)
    ↓
[爬取資訊源] → [分析新聞價值] → [判斷是否撰寫]
```

### Phase 2: Content Creation (內容創作)
```
Reporter/Expert Agent
    ↓
[撰寫草稿] → [自我審查] → [提交至編輯隊列]
```

### Phase 3: Quality Control (質量控制)
```
Editor-in-Chief Agent
    ↓
[審查內容] → [校對修正] → [決策: 通過/退回/修改]
    ↓
[通過] → [生成最終文章]
    ↓
[提交 Git Commit]
```

### Phase 4: Publishing (發布)
```
自動化流程
    ↓
[創建 Pull Request] → [觸發 CI/CD] → [部署至 GitHub Pages]
```

---

## Agent 協作機制

### 通訊協議
採用 **事件驅動架構 (Event-Driven Architecture)**

```
Event Queue (事件隊列)
    ├── news_discovered (新聞發現)
    ├── draft_submitted (草稿提交)
    ├── review_completed (審查完成)
    ├── revision_requested (修改請求)
    └── article_published (文章發布)
```

### 數據流
```json
{
  "task_id": "uuid",
  "agent": "google_reporter",
  "status": "draft_submitted",
  "content": {
    "title": "...",
    "markdown": "...",
    "metadata": {...}
  },
  "timestamp": "2025-12-02T10:00:00Z"
}
```

---

## 技術實現方案

### 選項 1: Claude Agent SDK (推薦)
使用 Anthropic 的 Agent SDK 實現多智能體系統

**優勢:**
- 原生支援多輪對話
- 內建工具調用能力
- 可組合多個 Agent

### 選項 2: LangGraph + LangChain
使用 LangGraph 構建狀態機驅動的 Agent 系統

**優勢:**
- 視覺化工作流程
- 成熟的社群生態
- 豐富的整合工具

### 選項 3: AutoGen (Microsoft)
使用 Microsoft 的 AutoGen 框架

**優勢:**
- 專為多智能體協作設計
- 支援人機協作模式

---

## 系統組件

### 1. Agent Manager (智能體管理器)
```python
class AgentManager:
    def __init__(self):
        self.reporters = []
        self.research_expert = None
        self.editor = None

    def run_discovery_cycle(self):
        """執行內容發現週期"""
        pass

    def submit_for_review(self, draft):
        """提交草稿供審查"""
        pass
```

### 2. Content Pipeline (內容管道)
```python
class ContentPipeline:
    def process_draft(self, draft):
        """處理草稿文章"""
        pass

    def save_to_repo(self, article):
        """保存至 Git 倉庫"""
        pass
```

### 3. Quality Checker (質量檢查器)
```python
class QualityChecker:
    def validate_frontmatter(self, article):
        """驗證 frontmatter 格式"""
        pass

    def check_content_guidelines(self, content):
        """檢查內容規範"""
        pass
```

---

## 部署架構

### 定時任務 (Cron Jobs)
```yaml
schedules:
  - name: discovery
    cron: "0 */6 * * *"  # 每 6 小時運行一次
    agent: reporters

  - name: research
    cron: "0 0 * * 1"    # 每週一運行
    agent: research_expert

  - name: review
    cron: "0 */2 * * *"  # 每 2 小時檢查待審查文章
    agent: editor
```

### 運行環境
- **Cloud Function / Lambda** - 無伺服器執行
- **GitHub Actions** - 使用現有 CI/CD
- **Docker Container** - 本地或雲端運行

---

## 監控和日誌

### 關鍵指標
- 文章生成數量
- 審查通過率
- 平均處理時間
- Agent 錯誤率

### 日誌結構
```json
{
  "timestamp": "2025-12-02T10:00:00Z",
  "agent": "google_reporter",
  "action": "article_created",
  "status": "success",
  "metadata": {
    "title": "Google Gemini 3.0 發布",
    "category": "Google",
    "word_count": 1200
  }
}
```

---

## 安全和質量控制

### 1. 內容驗證
- Frontmatter Schema 驗證
- 內容長度檢查 (800-1500 字)
- 圖片資源驗證
- 連結有效性檢查

### 2. 版本控制
- 所有變更通過 Git 追蹤
- 需要 PR 審查才能合併到 main
- 自動化測試驗證構建

### 3. 回滾機制
- 保留所有草稿版本
- 支援手動回滾到任意版本

---

## 擴展性設計

### 新增 Agent
1. 繼承 `BaseReporter` 類別
2. 實現 `discover()` 和 `write_article()` 方法
3. 註冊到 AgentManager

### 新增資訊源
1. 實現新的 Scraper 類別
2. 添加到 Reporter 的資訊源列表
3. 配置爬取頻率和優先級

---

## 成本估算

### API 調用成本
- 每篇文章約 10,000 tokens (寫作 + 審查)
- 每日 6 篇文章 = 60,000 tokens
- 每月約 1.8M tokens
- 估算成本: $5.40/月 (Claude Sonnet 4)

### 運行成本
- GitHub Actions: 免費額度內
- 存儲: 可忽略不計

---

## 下一步行動

1. ✅ 設計系統架構
2. ⏳ 實現 Agent 提示詞模板
3. ⏳ 開發核心框架代碼
4. ⏳ 測試單個 Agent
5. ⏳ 整合多 Agent 協作
6. ⏳ 部署到生產環境
