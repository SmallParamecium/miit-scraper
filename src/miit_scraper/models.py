"""数据模型定义。

定义爬取过程中使用的核心数据结构：
- Article: 单篇文章的完整信息
- ArticleList: 文章列表响应
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Article:
    """工信部时政要闻文章数据模型。

    Attributes:
        article_id: 文章唯一标识符（通常为 URL 中的 ID）
        title: 文章标题
        publish_date: 发布日期
        url: 文章详情页 URL
        source: 文章来源（如"工业和信息化部"）
        content_html: 原始 HTML 正文内容
        content_text: 清洗后的纯文本正文
        attachments: 附件列表（文件名 -> URL 映射）
    """

    article_id: str
    title: str
    publish_date: Optional[datetime] = None
    url: str = ""
    source: str = ""
    content_html: str = ""
    content_text: str = ""
    attachments: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_api_item(cls, data: dict) -> "Article":
        """从 API 列表接口返回的 JSON 项构造 Article 实例。

        Args:
            data: API 返回的单条文章 JSON 数据

        Returns:
            Article 实例（content 相关字段为空，需后续抓取详情页填充）
        """
        return cls(
            article_id=str(data.get("id", "")),
            title=data.get("title", ""),
            publish_date=None,
            url=data.get("url", ""),
        )

    def to_dict(self) -> dict:
        """转换为字典，便于 JSON 序列化。

        Returns:
            包含所有非空字段的字典
        """
        result: dict = {
            "article_id": self.article_id,
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "content_text": self.content_text,
        }
        if self.publish_date:
            result["publish_date"] = self.publish_date.isoformat()
        if self.attachments:
            result["attachments"] = self.attachments
        return result


@dataclass
class ArticleList:
    """文章列表响应。

    Attributes:
        total: 总文章数
        articles: 文章列表
        page: 当前页码
        page_size: 每页数量
    """

    total: int = 0
    articles: list[Article] = field(default_factory=list)
    page: int = 1
    page_size: int = 10