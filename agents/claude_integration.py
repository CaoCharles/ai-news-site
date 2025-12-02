"""
Claude API 整合模組

提供與 Anthropic Claude API 的整合功能，包括：
- 文章生成
- 內容審查
- 數據分析
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

logger = logging.getLogger(__name__)


class ClaudeClient:
    """Claude API 客戶端封裝"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 4096,
        temperature: float = 0.7
    ):
        """
        初始化 Claude 客戶端

        Args:
            api_key: API 密鑰（如果為 None，從環境變量讀取）
            model: 使用的模型
            max_tokens: 最大輸出 tokens
            temperature: 溫度參數
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not found")

        self.client = Anthropic(api_key=self.api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

        logger.info(f"Claude client initialized with model: {model}")

    def generate_article(
        self,
        prompt_template: str,
        news_info: Dict[str, Any],
        category: str
    ) -> Dict[str, Any]:
        """
        生成文章

        Args:
            prompt_template: 提示詞模板
            news_info: 新聞資訊
            category: 文章分類

        Returns:
            生成結果 {"content": str, "metadata": dict}
        """
        # 構建完整提示詞
        prompt = self._build_article_prompt(prompt_template, news_info, category)

        logger.info(f"Generating article for: {news_info.get('title', 'Unknown')}")

        try:
            # 調用 Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # 提取內容
            content = response.content[0].text

            # 解析響應（假設 Claude 返回 JSON 格式）
            result = self._parse_article_response(content)

            logger.info(f"Article generated successfully, {len(content)} characters")

            return {
                "success": True,
                "content": result.get("content", ""),
                "metadata": result.get("metadata", {}),
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }

        except Exception as e:
            logger.error(f"Failed to generate article: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def review_article(
        self,
        prompt_template: str,
        article_content: str,
        article_metadata: Dict[str, Any],
        content_guidelines: str
    ) -> Dict[str, Any]:
        """
        審查文章

        Args:
            prompt_template: 提示詞模板
            article_content: 文章內容
            article_metadata: 文章元數據
            content_guidelines: 內容規範

        Returns:
            審查結果
        """
        # 構建審查提示詞
        prompt = self._build_review_prompt(
            prompt_template,
            article_content,
            article_metadata,
            content_guidelines
        )

        logger.info("Reviewing article...")

        try:
            # 使用工具調用進行結構化審查
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=0.3,  # 審查時使用較低溫度
                tools=self._get_review_tools(),
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # 處理工具調用結果
            result = self._process_review_response(response)

            logger.info(f"Review completed: {result.get('decision', 'unknown')}")

            return result

        except Exception as e:
            logger.error(f"Failed to review article: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def analyze_benchmark_data(
        self,
        prompt_template: str,
        benchmark_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        分析基準測試數據

        Args:
            prompt_template: 提示詞模板
            benchmark_data: 基準測試數據

        Returns:
            分析結果
        """
        prompt = self._build_analysis_prompt(prompt_template, benchmark_data)

        logger.info("Analyzing benchmark data...")

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=0.5,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            content = response.content[0].text
            result = self._parse_analysis_response(content)

            logger.info("Analysis completed")

            return {
                "success": True,
                "analysis": result,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }

        except Exception as e:
            logger.error(f"Failed to analyze data: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _build_article_prompt(
        self,
        template: str,
        news_info: Dict[str, Any],
        category: str
    ) -> str:
        """構建文章生成提示詞"""

        prompt = template.replace("{MODEL_NAME}", category)
        prompt += "\n\n---\n\n"
        prompt += "## 任務\n\n"
        prompt += f"請根據以下資訊撰寫一篇關於 {category} 的技術新聞文章：\n\n"
        prompt += f"**標題**: {news_info.get('title', '')}\n"
        prompt += f"**來源**: {news_info.get('source', '')}\n"
        prompt += f"**摘要**: {news_info.get('summary', '')}\n\n"
        prompt += "請嚴格遵循 content_agent.md 中的寫作規範，生成完整的 Markdown 文章。\n\n"
        prompt += "## 輸出格式\n\n"
        prompt += "請以 JSON 格式輸出：\n"
        prompt += "```json\n"
        prompt += "{\n"
        prompt += '  "content": "完整的 Markdown 內容（包含 frontmatter）",\n'
        prompt += '  "metadata": {\n'
        prompt += '    "title": "文章標題",\n'
        prompt += '    "description": "文章描述",\n'
        prompt += '    "word_count": 1200,\n'
        prompt += '    "reading_time": "6 分鐘閱讀",\n'
        prompt += '    "tags": ["tag1", "tag2"]\n'
        prompt += "  }\n"
        prompt += "}\n"
        prompt += "```"

        return prompt

    def _build_review_prompt(
        self,
        template: str,
        content: str,
        metadata: Dict[str, Any],
        guidelines: str
    ) -> str:
        """構建審查提示詞"""

        prompt = template + "\n\n---\n\n"
        prompt += "## 待審查文章\n\n"
        prompt += "### Metadata\n"
        prompt += f"```json\n{json.dumps(metadata, ensure_ascii=False, indent=2)}\n```\n\n"
        prompt += "### Content\n"
        prompt += f"```markdown\n{content}\n```\n\n"
        prompt += "## 內容規範\n\n"
        prompt += f"{guidelines}\n\n"
        prompt += "請根據編輯規範進行全面審查，並使用提供的工具記錄審查結果。"

        return prompt

    def _build_analysis_prompt(
        self,
        template: str,
        data: Dict[str, Any]
    ) -> str:
        """構建分析提示詞"""

        prompt = template + "\n\n---\n\n"
        prompt += "## 基準測試數據\n\n"
        prompt += f"```json\n{json.dumps(data, ensure_ascii=False, indent=2)}\n```\n\n"
        prompt += "請對以上數據進行深度分析，並撰寫評測報告。"

        return prompt

    def _get_review_tools(self) -> List[Dict[str, Any]]:
        """獲取審查工具定義"""

        return [
            {
                "name": "validate_frontmatter",
                "description": "驗證文章 frontmatter 是否符合規範",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "valid": {"type": "boolean"},
                        "issues": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["valid", "issues"]
                }
            },
            {
                "name": "check_content_structure",
                "description": "檢查文章結構完整性",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "complete": {"type": "boolean"},
                        "missing_sections": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["complete", "missing_sections"]
                }
            },
            {
                "name": "assess_quality",
                "description": "評估文章整體質量",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "score": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 10
                        },
                        "strengths": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "weaknesses": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["score", "strengths", "weaknesses"]
                }
            },
            {
                "name": "verify_facts",
                "description": "驗證事實和數據準確性",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "accurate": {"type": "boolean"},
                        "issues": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "location": {"type": "string"},
                                    "issue": {"type": "string"},
                                    "severity": {"type": "string"}
                                }
                            }
                        }
                    },
                    "required": ["accurate", "issues"]
                }
            },
            {
                "name": "make_decision",
                "description": "做出最終審查決策",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "decision": {
                            "type": "string",
                            "enum": ["approved", "revision_required", "rejected"]
                        },
                        "reason": {"type": "string"},
                        "required_changes": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["decision", "reason"]
                }
            }
        ]

    def _parse_article_response(self, content: str) -> Dict[str, Any]:
        """解析文章生成響應"""

        try:
            # 嘗試從 JSON code block 中提取
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
                return json.loads(json_str)
            else:
                # 嘗試直接解析
                return json.loads(content)

        except json.JSONDecodeError:
            # 如果無法解析 JSON，返回原始內容
            logger.warning("Failed to parse JSON response, returning raw content")
            return {
                "content": content,
                "metadata": {}
            }

    def _process_review_response(self, response) -> Dict[str, Any]:
        """處理審查響應"""

        result = {
            "success": True,
            "decision": "pending",
            "quality_score": 0.0,
            "issues": [],
            "strengths": [],
            "required_changes": []
        }

        # 處理工具調用結果
        for content_block in response.content:
            if content_block.type == "tool_use":
                tool_name = content_block.name
                tool_input = content_block.input

                if tool_name == "assess_quality":
                    result["quality_score"] = tool_input.get("score", 0.0)
                    result["strengths"] = tool_input.get("strengths", [])

                elif tool_name == "verify_facts":
                    if not tool_input.get("accurate", True):
                        result["issues"].extend(tool_input.get("issues", []))

                elif tool_name == "validate_frontmatter":
                    if not tool_input.get("valid", True):
                        result["issues"].extend([
                            {"category": "frontmatter", "issue": issue}
                            for issue in tool_input.get("issues", [])
                        ])

                elif tool_name == "check_content_structure":
                    if not tool_input.get("complete", True):
                        missing = tool_input.get("missing_sections", [])
                        result["issues"].extend([
                            {"category": "structure", "issue": f"缺少段落: {section}"}
                            for section in missing
                        ])

                elif tool_name == "make_decision":
                    result["decision"] = tool_input.get("decision", "pending")
                    result["required_changes"] = tool_input.get("required_changes", [])

        return result

    def _parse_analysis_response(self, content: str) -> Dict[str, Any]:
        """解析分析響應"""

        # 類似 _parse_article_response
        try:
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
                return json.loads(json_str)
            else:
                return {"analysis": content}

        except json.JSONDecodeError:
            return {"analysis": content}


# ============================================================================
# 便捷函數
# ============================================================================

def create_claude_client(config: Optional[Dict[str, Any]] = None) -> ClaudeClient:
    """
    創建 Claude 客戶端

    Args:
        config: 配置字典

    Returns:
        ClaudeClient 實例
    """
    if config is None:
        config = {}

    api_config = config.get("api_config", {})

    return ClaudeClient(
        api_key=os.environ.get(api_config.get("anthropic_api_key_env", "ANTHROPIC_API_KEY")),
        model=api_config.get("model", "claude-3-5-sonnet-20241022"),
        max_tokens=api_config.get("max_tokens", 4096),
        temperature=api_config.get("temperature", 0.7)
    )


# ============================================================================
# 使用示例
# ============================================================================

if __name__ == "__main__":
    # 創建客戶端
    client = ClaudeClient()

    # 示例：生成文章
    news_info = {
        "title": "Google Gemini 3.0 發布",
        "source": "https://blog.google/technology/ai/gemini-3/",
        "summary": "Google 發布新一代 Gemini 3.0 多模態模型..."
    }

    # 載入提示詞模板
    with open("prompts/reporter_prompt.md", 'r', encoding='utf-8') as f:
        prompt_template = f.read()

    # 生成文章
    result = client.generate_article(
        prompt_template=prompt_template,
        news_info=news_info,
        category="Google"
    )

    if result["success"]:
        print("文章生成成功！")
        print(f"字數: {result['metadata'].get('word_count', 0)}")
        print(f"Token 使用: {result['usage']}")
    else:
        print(f"生成失敗: {result['error']}")
