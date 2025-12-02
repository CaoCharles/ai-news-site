"""
Multi-Agent 自動內容更新系統 - 核心框架

這個框架實現了一個多智能體協作系統，用於自動更新 AI News 網站的內容。
包含 Reporter Agents、Research Expert Agent 和 Editor-in-Chief Agent。
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# 數據模型
# ============================================================================

class ArticleStatus(Enum):
    """文章狀態"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    REVISION_REQUIRED = "revision_required"
    APPROVED = "approved"
    PUBLISHED = "published"
    REJECTED = "rejected"


class Category(Enum):
    """文章分類"""
    GOOGLE = "Google"
    CLAUDE = "Claude"
    CHATGPT = "ChatGPT"
    GROK = "Grok"
    QIANWEN = "Qianwen"
    MODEL_EVAL = "ModelEval"


@dataclass
class ArticleMetadata:
    """文章元數據"""
    title: str
    description: str
    date: str
    category: str
    image: str
    reading_time: str
    author: str
    tags: List[str]
    source: Optional[str] = None


@dataclass
class Article:
    """文章對象"""
    article_id: str
    metadata: ArticleMetadata
    content: str
    status: ArticleStatus
    agent: str
    created_at: datetime
    updated_at: datetime
    version: int = 1
    review_notes: Optional[List[Dict[str, Any]]] = None


@dataclass
class ReviewResult:
    """審查結果"""
    decision: str  # "approved", "revision_required", "rejected"
    quality_score: float
    issues: List[Dict[str, Any]]
    strengths: Optional[List[str]] = None
    required_changes: Optional[List[str]] = None
    final_article: Optional[str] = None


# ============================================================================
# 基礎 Agent 類
# ============================================================================

class BaseAgent(ABC):
    """Agent 基礎類"""

    def __init__(self, name: str, model: str = "claude-3-5-sonnet-20241022"):
        self.name = name
        self.model = model
        self.logger = logging.getLogger(f"Agent.{name}")

    @abstractmethod
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """執行任務"""
        pass

    def log_action(self, action: str, details: Dict[str, Any]):
        """記錄 Agent 行動"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
            "action": action,
            "details": details
        }
        self.logger.info(json.dumps(log_entry, ensure_ascii=False))
        return log_entry


# ============================================================================
# Reporter Agent
# ============================================================================

class ReporterAgent(BaseAgent):
    """記者 Agent 基礎類"""

    def __init__(self, name: str, category: Category, sources: List[str]):
        super().__init__(name)
        self.category = category
        self.sources = sources
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        """載入提示詞模板"""
        prompt_path = "agents/prompts/reporter_prompt.md"
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            self.logger.warning(f"Prompt template not found: {prompt_path}")
            return ""

    def discover_news(self, time_range: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        發現新聞

        Args:
            time_range: {"start": "2025-12-01", "end": "2025-12-02"}

        Returns:
            新聞發現列表
        """
        self.log_action("discover_news", {
            "category": self.category.value,
            "time_range": time_range
        })

        # 這裡應該調用 Claude API 進行新聞發現
        # 實際實現時需要整合網頁爬取、API 調用等功能

        discoveries = []
        # TODO: 實現實際的新聞發現邏輯

        return discoveries

    def assess_news_value(self, news_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        評估新聞價值

        Args:
            news_info: 新聞資訊

        Returns:
            評估結果 {"worthy": bool, "score": float, "reasons": List[str]}
        """
        # TODO: 使用 Claude API 評估新聞價值
        pass

    def write_article(self, news_info: Dict[str, Any]) -> Article:
        """
        撰寫文章

        Args:
            news_info: 新聞資訊

        Returns:
            文章對象
        """
        self.log_action("write_article", {
            "topic": news_info.get("title", "Unknown"),
            "category": self.category.value
        })

        # TODO: 使用 Claude API 生成文章內容
        # 這裡應該調用 Claude API，使用 reporter_prompt.md 中的指導

        article_id = self._generate_article_id(news_info)

        # 創建文章對象
        article = Article(
            article_id=article_id,
            metadata=ArticleMetadata(
                title="",  # 從生成的內容中提取
                description="",
                date=datetime.now().strftime("%Y-%m-%d"),
                category=self.category.value,
                image=f"/images/{article_id}.jpg",
                reading_time="5 分鐘閱讀",
                author="AI News 編輯部",
                tags=[],
                source=news_info.get("source")
            ),
            content="",  # Claude 生成的 Markdown 內容
            status=ArticleStatus.DRAFT,
            agent=self.name,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        return article

    def self_review(self, article: Article) -> Dict[str, Any]:
        """
        自我審查

        Returns:
            審查結果 {"passed": bool, "issues": List[str]}
        """
        issues = []

        # 檢查字數
        word_count = len(article.content)
        if word_count < 800:
            issues.append(f"字數不足: {word_count} < 800")
        elif word_count > 1500:
            issues.append(f"字數超出: {word_count} > 1500")

        # 檢查 frontmatter
        if not article.metadata.title:
            issues.append("缺少標題")
        if not article.metadata.description:
            issues.append("缺少描述")
        if not article.metadata.tags:
            issues.append("缺少標籤")

        passed = len(issues) == 0

        self.log_action("self_review", {
            "article_id": article.article_id,
            "passed": passed,
            "issues": issues
        })

        return {"passed": passed, "issues": issues}

    def _generate_article_id(self, news_info: Dict[str, Any]) -> str:
        """生成文章 ID"""
        date_str = datetime.now().strftime("%Y%m")
        topic_slug = news_info.get("slug", "article")
        return f"{self.category.value.lower()}-{topic_slug}-{date_str}"

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        執行任務

        Args:
            task: {
                "type": "discover" | "write",
                "time_range": {...},
                "news_info": {...}
            }
        """
        task_type = task.get("type")

        if task_type == "discover":
            discoveries = self.discover_news(task.get("time_range", {}))
            return {"status": "success", "discoveries": discoveries}

        elif task_type == "write":
            news_info = task.get("news_info", {})
            article = self.write_article(news_info)
            review = self.self_review(article)

            if review["passed"]:
                return {
                    "status": "success",
                    "article": asdict(article),
                    "ready_for_review": True
                }
            else:
                return {
                    "status": "needs_improvement",
                    "article": asdict(article),
                    "issues": review["issues"]
                }

        return {"status": "error", "message": "Unknown task type"}


# ============================================================================
# 具體 Reporter Agents
# ============================================================================

class GoogleReporter(ReporterAgent):
    """Google 模型記者"""
    def __init__(self):
        super().__init__(
            name="GoogleReporter",
            category=Category.GOOGLE,
            sources=[
                "https://blog.google/technology/ai/",
                "https://ai.google/research/",
                "https://deepmind.google/"
            ]
        )


class ClaudeReporter(ReporterAgent):
    """Claude 模型記者"""
    def __init__(self):
        super().__init__(
            name="ClaudeReporter",
            category=Category.CLAUDE,
            sources=[
                "https://www.anthropic.com/news",
                "https://www.anthropic.com/research"
            ]
        )


class ChatGPTReporter(ReporterAgent):
    """ChatGPT 模型記者"""
    def __init__(self):
        super().__init__(
            name="ChatGPTReporter",
            category=Category.CHATGPT,
            sources=[
                "https://openai.com/blog",
                "https://openai.com/research"
            ]
        )


class GrokReporter(ReporterAgent):
    """Grok 模型記者"""
    def __init__(self):
        super().__init__(
            name="GrokReporter",
            category=Category.GROK,
            sources=[
                "https://x.ai/",
                "https://twitter.com/elonmusk"
            ]
        )


class QianwenReporter(ReporterAgent):
    """千問模型記者"""
    def __init__(self):
        super().__init__(
            name="QianwenReporter",
            category=Category.QIANWEN,
            sources=[
                "https://tongyi.aliyun.com/",
                "https://www.alibabacloud.com/blog"
            ]
        )


# ============================================================================
# Research Expert Agent
# ============================================================================

class ResearchExpertAgent(BaseAgent):
    """研究專家 Agent"""

    def __init__(self):
        super().__init__("ResearchExpert")
        self.benchmarks = [
            "MMLU", "HumanEval", "MATH", "GPQA", "BBH",
            "ARC", "HellaSwag", "WinoGrande"
        ]
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        """載入提示詞模板"""
        prompt_path = "agents/prompts/research_expert_prompt.md"
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            self.logger.warning(f"Prompt template not found: {prompt_path}")
            return ""

    def collect_benchmark_data(self, models: List[str]) -> Dict[str, Any]:
        """
        收集基準測試數據

        Args:
            models: 模型名稱列表

        Returns:
            基準測試數據
        """
        self.log_action("collect_benchmark_data", {"models": models})

        # TODO: 實現數據收集邏輯
        # 從官方來源、Hugging Face、Papers with Code 等收集數據

        return {}

    def analyze_performance(self, benchmark_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析性能數據

        Returns:
            分析結果
        """
        # TODO: 使用 Claude API 進行深度分析
        pass

    def write_evaluation_report(self, analysis: Dict[str, Any]) -> Article:
        """
        撰寫評測報告

        Returns:
            評測文章
        """
        self.log_action("write_evaluation_report", {
            "models_count": len(analysis.get("models", []))
        })

        # TODO: 使用 Claude API 生成評測報告
        pass

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """執行研究任務"""
        task_type = task.get("type")

        if task_type == "evaluate_model":
            model_name = task.get("model_name")
            data = self.collect_benchmark_data([model_name])
            analysis = self.analyze_performance(data)
            article = self.write_evaluation_report(analysis)
            return {"status": "success", "article": asdict(article)}

        elif task_type == "compare_models":
            models = task.get("models", [])
            data = self.collect_benchmark_data(models)
            analysis = self.analyze_performance(data)
            article = self.write_evaluation_report(analysis)
            return {"status": "success", "article": asdict(article)}

        return {"status": "error", "message": "Unknown task type"}


# ============================================================================
# Editor-in-Chief Agent
# ============================================================================

class EditorInChiefAgent(BaseAgent):
    """總編輯 Agent"""

    def __init__(self):
        super().__init__("EditorInChief")
        self.content_guidelines = self._load_content_guidelines()
        self.prompt_template = self._load_prompt_template()

    def _load_content_guidelines(self) -> str:
        """載入內容規範"""
        try:
            with open("content_agent.md", 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            self.logger.warning("content_agent.md not found")
            return ""

    def _load_prompt_template(self) -> str:
        """載入提示詞模板"""
        prompt_path = "agents/prompts/editor_prompt.md"
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            self.logger.warning(f"Prompt template not found: {prompt_path}")
            return ""

    def review_article(self, article: Article) -> ReviewResult:
        """
        審查文章

        Returns:
            審查結果
        """
        self.log_action("review_article", {
            "article_id": article.article_id,
            "author": article.agent
        })

        # Step 1: 初步檢查
        initial_issues = self._initial_check(article)

        if initial_issues:
            return ReviewResult(
                decision="rejected",
                quality_score=0.0,
                issues=initial_issues
            )

        # Step 2: 詳細審查
        # TODO: 使用 Claude API 進行深度審查

        # Step 3: 事實核查
        fact_check_issues = self._fact_check(article)

        # Step 4: 質量評分
        quality_score = self._calculate_quality_score(article)

        # Step 5: 做出決策
        all_issues = initial_issues + fact_check_issues

        if quality_score >= 7.0 and len(all_issues) == 0:
            decision = "approved"
        elif quality_score >= 6.0:
            decision = "revision_required"
        else:
            decision = "rejected"

        return ReviewResult(
            decision=decision,
            quality_score=quality_score,
            issues=all_issues
        )

    def _initial_check(self, article: Article) -> List[Dict[str, Any]]:
        """初步檢查"""
        issues = []

        # 檢查 frontmatter
        if not article.metadata.title:
            issues.append({
                "severity": "high",
                "category": "frontmatter",
                "issue": "缺少標題"
            })

        if not article.metadata.description:
            issues.append({
                "severity": "high",
                "category": "frontmatter",
                "issue": "缺少描述"
            })

        # 檢查字數
        word_count = len(article.content)
        if word_count < 800:
            issues.append({
                "severity": "high",
                "category": "content_length",
                "issue": f"字數不足: {word_count} < 800"
            })

        return issues

    def _fact_check(self, article: Article) -> List[Dict[str, Any]]:
        """事實核查"""
        # TODO: 實現事實核查邏輯
        # 驗證引用來源、數據準確性等
        return []

    def _calculate_quality_score(self, article: Article) -> float:
        """計算質量分數"""
        # TODO: 實現更複雜的質量評分邏輯
        # 可以使用 Claude API 進行質量評估
        return 8.0

    def provide_feedback(self, review: ReviewResult) -> str:
        """提供反饋意見"""
        feedback = f"## 審查結果: {review.decision}\n\n"
        feedback += f"質量評分: {review.quality_score}/10\n\n"

        if review.issues:
            feedback += "### 需要修正的問題:\n\n"
            for issue in review.issues:
                feedback += f"- [{issue['severity']}] {issue['issue']}\n"

        if review.required_changes:
            feedback += "\n### 必須修改:\n\n"
            for change in review.required_changes:
                feedback += f"- {change}\n"

        return feedback

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """執行審查任務"""
        article_data = task.get("article")

        # 重建 Article 對象
        article = Article(**article_data)

        # 審查文章
        review = self.review_article(article)

        # 生成反饋
        feedback = self.provide_feedback(review)

        self.log_action("review_completed", {
            "article_id": article.article_id,
            "decision": review.decision,
            "quality_score": review.quality_score
        })

        return {
            "status": "success",
            "review": asdict(review),
            "feedback": feedback
        }


# ============================================================================
# Agent Manager - 協調所有 Agents
# ============================================================================

class AgentManager:
    """Agent 管理器 - 協調所有 Agents 的工作"""

    def __init__(self):
        self.logger = logging.getLogger("AgentManager")

        # 初始化所有 Agents
        self.reporters = {
            "google": GoogleReporter(),
            "claude": ClaudeReporter(),
            "chatgpt": ChatGPTReporter(),
            "grok": GrokReporter(),
            "qianwen": QianwenReporter()
        }

        self.research_expert = ResearchExpertAgent()
        self.editor = EditorInChiefAgent()

        # 文章隊列
        self.draft_queue: List[Article] = []
        self.review_queue: List[Article] = []
        self.approved_articles: List[Article] = []

    def run_discovery_cycle(self, time_range: Dict[str, str]) -> Dict[str, Any]:
        """
        運行發現週期 - 所有 Reporters 並行搜索新聞

        Args:
            time_range: {"start": "2025-12-01", "end": "2025-12-02"}

        Returns:
            發現結果統計
        """
        self.logger.info(f"Starting discovery cycle: {time_range}")

        discoveries = {}

        # 並行執行所有 reporters
        for name, reporter in self.reporters.items():
            try:
                result = reporter.execute({
                    "type": "discover",
                    "time_range": time_range
                })
                discoveries[name] = result.get("discoveries", [])
            except Exception as e:
                self.logger.error(f"Error in {name} reporter: {e}")
                discoveries[name] = []

        total_discoveries = sum(len(d) for d in discoveries.values())

        self.logger.info(f"Discovery cycle completed: {total_discoveries} news items found")

        return {
            "status": "completed",
            "total_discoveries": total_discoveries,
            "by_category": {k: len(v) for k, v in discoveries.items()}
        }

    def create_article(self, reporter_name: str, news_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        創建文章

        Args:
            reporter_name: Reporter 名稱
            news_info: 新聞資訊

        Returns:
            創建結果
        """
        reporter = self.reporters.get(reporter_name)
        if not reporter:
            return {"status": "error", "message": f"Unknown reporter: {reporter_name}"}

        result = reporter.execute({
            "type": "write",
            "news_info": news_info
        })

        if result.get("status") == "success" and result.get("ready_for_review"):
            # 添加到審查隊列
            article_dict = result["article"]
            article = Article(**article_dict)
            self.review_queue.append(article)

            self.logger.info(f"Article submitted for review: {article.article_id}")

        return result

    def review_next_article(self) -> Optional[Dict[str, Any]]:
        """
        審查下一篇文章

        Returns:
            審查結果或 None
        """
        if not self.review_queue:
            return None

        article = self.review_queue.pop(0)
        article.status = ArticleStatus.UNDER_REVIEW

        result = self.editor.execute({
            "article": asdict(article)
        })

        review = ReviewResult(**result["review"])

        if review.decision == "approved":
            article.status = ArticleStatus.APPROVED
            self.approved_articles.append(article)
            self.logger.info(f"Article approved: {article.article_id}")

        elif review.decision == "revision_required":
            article.status = ArticleStatus.REVISION_REQUIRED
            # 退回給原 Reporter
            self.logger.info(f"Article needs revision: {article.article_id}")

        else:  # rejected
            article.status = ArticleStatus.REJECTED
            self.logger.info(f"Article rejected: {article.article_id}")

        return result

    def publish_approved_articles(self) -> List[str]:
        """
        發布已批准的文章

        Returns:
            已發布文章的文件路徑列表
        """
        published_files = []

        for article in self.approved_articles:
            file_path = self._save_article_to_file(article)
            published_files.append(file_path)
            article.status = ArticleStatus.PUBLISHED

            self.logger.info(f"Article published: {file_path}")

        # 清空已發布列表
        self.approved_articles = []

        return published_files

    def _save_article_to_file(self, article: Article) -> str:
        """保存文章到文件"""
        filename = f"{article.article_id}.md"
        file_path = f"src/content/posts/{filename}"

        # 生成 frontmatter
        frontmatter = "---\n"
        frontmatter += f'title: "{article.metadata.title}"\n'
        frontmatter += f'description: "{article.metadata.description}"\n'
        frontmatter += f'date: {article.metadata.date}\n'
        frontmatter += f'category: "{article.metadata.category}"\n'
        frontmatter += f'image: "{article.metadata.image}"\n'
        frontmatter += f'readingTime: "{article.metadata.reading_time}"\n'
        frontmatter += f'author: "{article.metadata.author}"\n'
        frontmatter += f'tags: {json.dumps(article.metadata.tags)}\n'
        if article.metadata.source:
            frontmatter += f'source: "{article.metadata.source}"\n'
        frontmatter += "---\n\n"

        # 完整內容
        full_content = frontmatter + article.content

        # 保存文件
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(full_content)

        return file_path

    def get_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        return {
            "draft_queue": len(self.draft_queue),
            "review_queue": len(self.review_queue),
            "approved_articles": len(self.approved_articles),
            "reporters_count": len(self.reporters)
        }


# ============================================================================
# 使用示例
# ============================================================================

def main():
    """主函數 - 演示如何使用系統"""

    # 創建 Agent Manager
    manager = AgentManager()

    # 1. 運行發現週期
    print("=" * 60)
    print("Step 1: 運行新聞發現週期")
    print("=" * 60)

    discovery_result = manager.run_discovery_cycle({
        "start": "2025-12-01",
        "end": "2025-12-02"
    })
    print(json.dumps(discovery_result, indent=2, ensure_ascii=False))

    # 2. 創建文章
    print("\n" + "=" * 60)
    print("Step 2: 創建文章")
    print("=" * 60)

    article_result = manager.create_article(
        reporter_name="google",
        news_info={
            "title": "Google Gemini 3.0 發布",
            "slug": "gemini-3-release",
            "source": "https://blog.google/technology/ai/gemini-3/",
            "summary": "Google 發布新一代 Gemini 3.0 模型..."
        }
    )
    print(json.dumps(article_result, indent=2, ensure_ascii=False))

    # 3. 審查文章
    print("\n" + "=" * 60)
    print("Step 3: 審查文章")
    print("=" * 60)

    review_result = manager.review_next_article()
    if review_result:
        print(json.dumps(review_result, indent=2, ensure_ascii=False))

    # 4. 發布文章
    print("\n" + "=" * 60)
    print("Step 4: 發布已批准的文章")
    print("=" * 60)

    published = manager.publish_approved_articles()
    print(f"已發布 {len(published)} 篇文章:")
    for path in published:
        print(f"  - {path}")

    # 5. 顯示系統狀態
    print("\n" + "=" * 60)
    print("系統狀態")
    print("=" * 60)

    status = manager.get_status()
    print(json.dumps(status, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
