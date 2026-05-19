> ⚠️ 本 Issue 为回溯补写，内容基于完成后的代码和 spec 文档反向整理。

# Bug: `python cli.py` 直接运行时报 ImportError — 相对导入无已知父包

## 背景 / 为什么现在做

项目采用 `src/` 布局，模块间使用 **相对导入**（如 `from .models import Article`）。在 Issue #4 开发完成后，用户尝试 `cd src/miit_scraper && python cli.py` 直接运行时，Python 报错：

```
ImportError: attempted relative import with no known parent package
```

这是因为 `python cli.py` 将脚本作为 `__main__` 模块执行，`__package__` 为 `None`，Python 无法解析 `.models` 这样的相对导入路径。

在开发阶段，通过 `uv run miit-scraper` 或 `python -m miit_scraper.cli` 运行是正常的，因为这两种方式都会将包上下文正确初始化。但 `python cli.py` 是一个常见的误用场景，如果没有任何提示就崩溃，用户体验很差。

## 当前想收住的不确定性

- 修复方式：是否应该在 `cli.py` 中内置 fallback 路径处理？
- 是否应该禁止用户直接 `python cli.py` 运行（强制 `python -m`）？

## 已收敛的推荐方案

在 `cli.py` 顶部的 `if __name__ == "__main__":` 块中添加 `sys.path` 注入和 `__package__` 设置：

```python
if __name__ == "__main__":
    _src_dir = Path(__file__).resolve().parent.parent
    if str(_src_dir) not in sys.path:
        sys.path.insert(0, str(_src_dir))
    __package__ = "miit_scraper"
```

这样无论是 `miit-scraper`、`python -m miit_scraper.cli` 还是 `python cli.py`，三种方式均可正常运行。

## 方案权衡记录

### 修复方式：sys.path 注入 vs 禁止直接运行 vs 绝对导入

**推荐：方案 A（sys.path 注入 + `__package__` 设置）。**

方案 A：在 `if __name__ == "__main__":` 中注入路径、设置包名。

优点：
- 三种运行方式全部兼容
- 侵入性小，仅影响 `__main__` 路径
- 后续新增代码不感知
缺点：
- 小众的 hack 写法，IDE 可能提示警告

方案 B：改为绝对导入 `from miit_scraper.models import Article`。

优点：`python -m` 一定可用
缺点：
- 必须在安装后才能运行（`pip install -e .`）
- `python cli.py` 在未安装时仍会失败——仅仅换了错误信息

方案 C：在包根目录放置 `cli.py` wrapper（src 外）。

优点：`python cli.py` 可运行
缺点：引入重复入口，破坏 `src/` 布局纯粹性

## 本 Issue 想解决什么

- [x] 修复：`python cli.py` 直接运行时报 ImportError
- [x] 在 `cli.py` 中注入 `sys.path` 和 `__package__`
- [x] 确保三种运行方式均正常：
  - `uv run miit-scraper`
  - `python -m miit_scraper.cli`
  - `cd src/miit_scraper && python cli.py`

## 明确不解决什么

- 不做其他模块的 import 兼容（仅 `cli.py`）
- 不引入 `try:/except ImportError:` 的回退导入

## 当前已知上下文

- `src/miit_scraper/cli.py`：受影响文件
- 所有模块使用相对导入（`from .models import ...`）
- 项目布局遵循 `src/` 标准

## 前置依赖

- Issue #28: cli.py 已完成（触发点）

## 子任务树

- [x] 定位问题：确认 `__package__` 为 None
- [x] 实现 fallback：`sys.path` 注入 + `__package__` 设置
- [x] 验证三种运行方式均正常
- [x] 编写回归测试（仅验证导入不抛异常，不重复 CLI 功能测试）

## 验收口径

### 必须成立

- `cd src/miit_scraper && python cli.py --help` 正常输出帮助信息（不再报 ImportError）
- `python -m miit_scraper.cli --help` 正常输出
- `uv run miit-scraper --help` 正常输出
- 三种方式输出一致的帮助文本

### 明确不成立

- 不应修改包内其他文件的导入方式
- 不应在 `pyproject.toml` 之外新增入口点文件

### 失败信号

- 修复引入了循环导入
- `sys.path` 注入污染了其他模块的导入路径
- `python cli.py` 在其他目录执行时路径错误

## Harness / 验证要求

- [x] 在不同目录执行 `python cli.py --help` 验证
- [x] `python -m miit_scraper.cli --help` 验证
- [x] `uv run miit-scraper --help` 验证
- [x] 回归 `uv run pytest tests/ -v` 全部通过