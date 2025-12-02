"""
Multi-Agent 系統編排器

這個模組負責協調整個 Multi-Agent 系統的運行，包括：
- 定時任務調度
- 工作流程管理
- 事件處理
- Git 操作自動化
"""

import time
import schedule
from datetime import datetime, timedelta
from typing import Dict, Any, List
import subprocess
import json
import logging

from agent_framework import AgentManager, ArticleStatus

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Orchestrator")


class ContentPipeline:
    """內容管道 - 處理從創建到發布的完整流程"""

    def __init__(self, manager: AgentManager, git_enabled: bool = True):
        self.manager = manager
        self.git_enabled = git_enabled
        self.logger = logging.getLogger("ContentPipeline")

    def process_draft(self, article_id: str) -> Dict[str, Any]:
        """
        處理草稿文章

        Returns:
            處理結果
        """
        self.logger.info(f"Processing draft: {article_id}")

        # 這裡應該從隊列或數據庫中獲取文章
        # 簡化起見，直接觸發審查流程

        result = self.manager.review_next_article()

        return result

    def save_to_repo(self, article_files: List[str]) -> bool:
        """
        保存文章到 Git 倉庫並提交

        Args:
            article_files: 文章文件路徑列表

        Returns:
            是否成功
        """
        if not self.git_enabled:
            self.logger.info("Git operations disabled")
            return False

        try:
            # Git add
            for file in article_files:
                subprocess.run(
                    ["git", "add", file],
                    check=True,
                    capture_output=True,
                    text=True
                )
                self.logger.info(f"Added to git: {file}")

            # Git commit
            commit_message = self._generate_commit_message(article_files)
            subprocess.run(
                ["git", "commit", "-m", commit_message],
                check=True,
                capture_output=True,
                text=True
            )
            self.logger.info(f"Committed: {commit_message}")

            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git operation failed: {e}")
            return False

    def _generate_commit_message(self, article_files: List[str]) -> str:
        """生成 commit 訊息"""
        if len(article_files) == 1:
            filename = article_files[0].split('/')[-1]
            return f"feat: add new article {filename}"
        else:
            return f"feat: add {len(article_files)} new articles"

    def push_to_remote(self, branch: str = "main") -> bool:
        """
        推送到遠程倉庫

        Args:
            branch: 分支名稱

        Returns:
            是否成功
        """
        if not self.git_enabled:
            return False

        try:
            subprocess.run(
                ["git", "push", "origin", branch],
                check=True,
                capture_output=True,
                text=True
            )
            self.logger.info(f"Pushed to {branch}")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Push failed: {e}")
            return False


class WorkflowOrchestrator:
    """工作流程編排器"""

    def __init__(self, config_path: str = "agents/config.json"):
        self.config = self._load_config(config_path)
        self.manager = AgentManager()
        self.pipeline = ContentPipeline(
            self.manager,
            git_enabled=self.config.get("git_enabled", True)
        )
        self.logger = logging.getLogger("Orchestrator")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """載入配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"Config not found: {config_path}, using defaults")
            return self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        """默認配置"""
        return {
            "git_enabled": True,
            "auto_publish": False,
            "schedules": {
                "discovery": "0 */6 * * *",  # 每 6 小時
                "research": "0 0 * * 1",      # 每週一
                "review": "0 */2 * * *"       # 每 2 小時
            },
            "reporters": {
                "google": {"enabled": True, "priority": 1},
                "claude": {"enabled": True, "priority": 1},
                "chatgpt": {"enabled": True, "priority": 1},
                "grok": {"enabled": True, "priority": 2},
                "qianwen": {"enabled": True, "priority": 2}
            },
            "quality_threshold": 7.0,
            "auto_approve_threshold": 9.0
        }

    def run_discovery_workflow(self):
        """運行發現工作流程"""
        self.logger.info("=" * 60)
        self.logger.info("Starting Discovery Workflow")
        self.logger.info("=" * 60)

        # 計算時間範圍
        now = datetime.now()
        start = (now - timedelta(hours=24)).strftime("%Y-%m-%d")
        end = now.strftime("%Y-%m-%d")

        # 執行發現
        result = self.manager.run_discovery_cycle({
            "start": start,
            "end": end
        })

        self.logger.info(f"Discovery completed: {result['total_discoveries']} items found")

        # 根據發現結果決定是否撰寫文章
        # 這裡需要更複雜的邏輯來評估新聞價值並決定是否撰寫

        return result

    def run_writing_workflow(self, news_items: List[Dict[str, Any]]):
        """運行寫作工作流程"""
        self.logger.info("=" * 60)
        self.logger.info(f"Starting Writing Workflow: {len(news_items)} items")
        self.logger.info("=" * 60)

        written_articles = []

        for item in news_items:
            reporter_name = item.get("reporter")
            news_info = item.get("news_info")

            self.logger.info(f"Creating article: {news_info.get('title')}")

            result = self.manager.create_article(reporter_name, news_info)

            if result.get("status") == "success":
                written_articles.append(result["article"])

        self.logger.info(f"Writing completed: {len(written_articles)} articles created")

        return written_articles

    def run_review_workflow(self):
        """運行審查工作流程"""
        self.logger.info("=" * 60)
        self.logger.info("Starting Review Workflow")
        self.logger.info("=" * 60)

        reviewed_count = 0
        approved_count = 0

        # 審查所有待審查的文章
        while True:
            result = self.manager.review_next_article()

            if not result:
                break

            reviewed_count += 1
            review = result.get("review", {})

            if review.get("decision") == "approved":
                approved_count += 1

            self.logger.info(
                f"Reviewed {reviewed_count} articles, "
                f"{approved_count} approved"
            )

        return {
            "reviewed": reviewed_count,
            "approved": approved_count
        }

    def run_publishing_workflow(self):
        """運行發布工作流程"""
        self.logger.info("=" * 60)
        self.logger.info("Starting Publishing Workflow")
        self.logger.info("=" * 60)

        # 發布已批准的文章
        published_files = self.manager.publish_approved_articles()

        if not published_files:
            self.logger.info("No articles to publish")
            return {"published": 0}

        self.logger.info(f"Published {len(published_files)} articles")

        # 保存到 Git
        if self.config.get("git_enabled"):
            success = self.pipeline.save_to_repo(published_files)

            if success:
                self.logger.info("Articles committed to git")

                # 是否自動推送
                if self.config.get("auto_publish"):
                    push_success = self.pipeline.push_to_remote()
                    if push_success:
                        self.logger.info("Changes pushed to remote")
                else:
                    self.logger.info("Auto-publish disabled, manual push required")

        return {"published": len(published_files)}

    def run_complete_cycle(self):
        """運行完整週期"""
        self.logger.info("\n" + "=" * 80)
        self.logger.info("STARTING COMPLETE CONTENT GENERATION CYCLE")
        self.logger.info("=" * 80 + "\n")

        start_time = datetime.now()

        # 1. 發現新聞
        discovery_result = self.run_discovery_workflow()

        # 2. 撰寫文章 (這裡簡化處理，實際需要根據發現結果決定)
        # news_items = [...]  # 從發現結果中提取
        # self.run_writing_workflow(news_items)

        # 3. 審查文章
        review_result = self.run_review_workflow()

        # 4. 發布文章
        publish_result = self.run_publishing_workflow()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # 總結
        summary = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "discoveries": discovery_result.get("total_discoveries", 0),
            "articles_reviewed": review_result.get("reviewed", 0),
            "articles_approved": review_result.get("approved", 0),
            "articles_published": publish_result.get("published", 0)
        }

        self.logger.info("\n" + "=" * 80)
        self.logger.info("CYCLE COMPLETED")
        self.logger.info("=" * 80)
        self.logger.info(json.dumps(summary, indent=2, ensure_ascii=False))

        return summary

    def schedule_tasks(self):
        """設置定時任務"""
        schedules = self.config.get("schedules", {})

        # 發現任務
        discovery_schedule = schedules.get("discovery", "0 */6 * * *")
        self.logger.info(f"Scheduling discovery: {discovery_schedule}")
        # schedule.every(6).hours.do(self.run_discovery_workflow)

        # 審查任務
        review_schedule = schedules.get("review", "0 */2 * * *")
        self.logger.info(f"Scheduling review: {review_schedule}")
        # schedule.every(2).hours.do(self.run_review_workflow)

        # 研究任務
        research_schedule = schedules.get("research", "0 0 * * 1")
        self.logger.info(f"Scheduling research: {research_schedule}")
        # schedule.every().monday.at("00:00").do(self.run_research_workflow)

        self.logger.info("All tasks scheduled")

    def run_research_workflow(self):
        """運行研究工作流程"""
        self.logger.info("=" * 60)
        self.logger.info("Starting Research Workflow")
        self.logger.info("=" * 60)

        # 執行模型評測研究
        result = self.manager.research_expert.execute({
            "type": "compare_models",
            "models": ["GPT-5", "Claude Opus 4.5", "Gemini 3.0"]
        })

        self.logger.info("Research workflow completed")

        return result

    def start_daemon(self):
        """啟動守護進程模式"""
        self.logger.info("Starting orchestrator in daemon mode")

        self.schedule_tasks()

        self.logger.info("Daemon mode started, press Ctrl+C to stop")

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分鐘檢查一次

        except KeyboardInterrupt:
            self.logger.info("Daemon stopped by user")


class InteractiveMode:
    """交互式模式 - 用於手動觸發和測試"""

    def __init__(self, orchestrator: WorkflowOrchestrator):
        self.orchestrator = orchestrator
        self.logger = logging.getLogger("InteractiveMode")

    def show_menu(self):
        """顯示菜單"""
        print("\n" + "=" * 60)
        print("Multi-Agent Content System - Interactive Mode")
        print("=" * 60)
        print("1. 運行發現工作流程")
        print("2. 運行審查工作流程")
        print("3. 運行發布工作流程")
        print("4. 運行完整週期")
        print("5. 查看系統狀態")
        print("6. 手動創建文章")
        print("7. 啟動守護進程模式")
        print("0. 退出")
        print("=" * 60)

    def run(self):
        """運行交互式模式"""
        while True:
            self.show_menu()
            choice = input("\n請選擇操作 (0-7): ").strip()

            if choice == "1":
                self.orchestrator.run_discovery_workflow()

            elif choice == "2":
                self.orchestrator.run_review_workflow()

            elif choice == "3":
                self.orchestrator.run_publishing_workflow()

            elif choice == "4":
                self.orchestrator.run_complete_cycle()

            elif choice == "5":
                status = self.orchestrator.manager.get_status()
                print("\n系統狀態:")
                print(json.dumps(status, indent=2, ensure_ascii=False))

            elif choice == "6":
                self.manual_create_article()

            elif choice == "7":
                self.orchestrator.start_daemon()

            elif choice == "0":
                print("再見！")
                break

            else:
                print("無效選擇，請重試")

    def manual_create_article(self):
        """手動創建文章"""
        print("\n手動創建文章")
        print("-" * 40)

        # 選擇 Reporter
        print("\n可用的 Reporters:")
        for i, name in enumerate(self.orchestrator.manager.reporters.keys(), 1):
            print(f"{i}. {name}")

        reporter_idx = int(input("\n選擇 Reporter (輸入數字): ")) - 1
        reporter_name = list(self.orchestrator.manager.reporters.keys())[reporter_idx]

        # 輸入文章資訊
        title = input("文章標題: ")
        slug = input("URL Slug: ")
        source = input("來源 URL: ")
        summary = input("簡短摘要: ")

        news_info = {
            "title": title,
            "slug": slug,
            "source": source,
            "summary": summary
        }

        # 創建文章
        result = self.orchestrator.manager.create_article(reporter_name, news_info)

        print("\n創建結果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))


def main():
    """主函數"""
    import sys

    # 創建編排器
    orchestrator = WorkflowOrchestrator()

    # 根據命令行參數決定運行模式
    if len(sys.argv) > 1:
        mode = sys.argv[1]

        if mode == "daemon":
            # 守護進程模式
            orchestrator.start_daemon()

        elif mode == "cycle":
            # 運行一次完整週期
            orchestrator.run_complete_cycle()

        elif mode == "discovery":
            orchestrator.run_discovery_workflow()

        elif mode == "review":
            orchestrator.run_review_workflow()

        elif mode == "publish":
            orchestrator.run_publishing_workflow()

        else:
            print(f"Unknown mode: {mode}")
            print("Available modes: daemon, cycle, discovery, review, publish, interactive")

    else:
        # 交互式模式
        interactive = InteractiveMode(orchestrator)
        interactive.run()


if __name__ == "__main__":
    main()
