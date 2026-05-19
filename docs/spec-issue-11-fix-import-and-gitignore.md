# Spec: 修复 cli.py ImportError + .gitignore 补充 (Issue #11)

**版本**: 0.1.0
**关联 Issue**: [#11](https://github.com/SmallParamecium/miit-scraper/issues/11)
**模块**: `src/miit_scraper/cli.py`, `.gitignore`
**类型**: bugfix

---

## 概述

修复两个问题：
1. 直接运行 `python src/miit_scraper/cli.py` 时报 `ImportError`
2. `issue参照.md` 和 `Conversation参考.md` 未加入 `.gitignore`，可能被误提交

---

## 1. ImportError 修复

### 1.1 问题根因

`cli.py` 中使用相对导入：
```python
from . import __version__
from .fetcher import fetch_article_list
```

相对导入仅在包上下文 (`python -m miit_scraper.cli` 或已安装包 `miit-scraper`) 中有效。直接 `python cli.py` 时 `__package__` 为 `None`，导致：
```
ImportError: attempted relative import with no known parent package
```

### 1.2 修复方案

使用 try/except 双路径导入：

```python
try:
    from . import __version__
    from .fetcher import fetch_article_list
    from .parser import fetch_and_parse_article
    from .exporter import save_raw_json, save_markdown
    from .models import Article
except ImportError:
    # 回退：直接运行 python cli.py 时
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from miit_scraper import __version__
    from miit_scraper.fetcher import fetch_article_list
    from miit_scraper.parser import fetch_and_parse_article
    from miit_scraper.exporter import save_raw_json, save_markdown
    from miit_scraper.models import Article
```

### 1.3 契约

| 运行方式 | 导入路径 | 状态 |
|----------|----------|------|
| `uv run miit-scraper` | 相对导入 | ✅ |
| `python -m miit_scraper.cli` | 相对导入 | ✅ |
| `python src/miit_scraper/cli.py` | 回退绝对导入 | ✅ |
| pip install 后 `miit-scraper` | 相对导入 | ✅ |

---

## 2. .gitignore 补充

### 2.1 新增条目

```gitignore
# 开发参考文档（不纳入版本控制）
issue参照.md
Conversation参考.md
```

### 2.2 原因

这两个 Markdown 文件是开发过程中的个人参考笔记，不应纳入项目仓库。`git add .` 时可能被误提交。

---

## 3. 验收标准

| 检查项 | 命令 |
|--------|------|
| 直接运行不报错 | `python src/miit_scraper/cli.py --help` |
| 包运行不报错 | `uv run miit-scraper --version` |
| 全量测试通过 | `uv run pytest tests/ -q` |
| .gitignore 生效 | `git status` 不显示参考文件 |

---

## 4. 测试覆盖

| 测试 | 覆盖内容 |
|------|----------|
| `test_version` | --version 输出（已验证两种运行方式） |
| `test_help` | --help 输出 |
| `test_basic_flow` | 完整流程 |

**文件**: `tests/test_cli.py`（通过现有测试验证）