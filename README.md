# 新闻获取MCP工具

这是一个基于Model Context Protocol (MCP)的新闻获取工具，它可以与支持MCP的AI助手（如Claude for Desktop）集成，为AI提供获取当前新闻的能力。

## 功能特点

- 从多个新闻源获取最新新闻
- 支持多种新闻类别：中国、全球、科技、财经
- 自动提取文章完整内容
- 与支持MCP的AI助手无缝集成

## 安装方式

### 方式1: 通过uvx直接从仓库运行（推荐）

1. 确保已安装 [uv](https://github.com/astral-sh/uv) 包管理工具
2. 使用 uvx 直接运行：

```bash
# 从 GitHub 仓库运行
uvx run github.com/你的用户名/news-mcp

# 指定参数
uvx run github.com/你的用户名/news-mcp -- --verbose --transport http
```

### 方式2: 本地安装

1. 确保安装了Python 3.10或更高版本
2. 克隆或下载此项目到本地
3. 安装所需依赖：

```bash
pip install -r requirements.txt
# 或者安装开发模式
pip install -e .
```

## 使用方法

### 1. 作为独立程序运行

```bash
# 直接使用包
python -m news_mcp.cli

# 使用安装的命令行工具
news-mcp --verbose

# HTTP服务器模式
news-mcp --transport http --port 8080
```

### 2. 与Claude for Desktop集成

1. 确保你已安装最新版本的Claude for Desktop
2. 打开Claude for Desktop的配置文件（通常位于`~/Library/Application Support/Claude/claude_desktop_config.json`或Windows上的`%AppData%\Claude\claude_desktop_config.json`）
3. 添加以下配置：

```json
{
    "mcpServers": {
        "news_summarizer": {
            "command": "uvx",
            "args": [
                "run",
                "github.com/Zmingfeng/AICoding/tree/main/demo2/news_mcp",
                "--"
            ]
        }
    }
}
```

或者使用本地安装方式：

```json
{
    "mcpServers": {
        "news_summarizer": {
            "command": "news-mcp",
            "args": []
        }
    }
}
```

4. 重启Claude for Desktop
5. 点击工具图标，你应该能看到提供的工具

## 可用工具

1. **get_latest_news** - 获取指定类别的最新新闻完整内容
   - 参数：
     - category (默认："中国")：新闻类别，可选值：中国、全球、科技、财经
     - count (默认：5)：要返回的新闻数量

2. **get_news_titles** - 仅获取指定类别的最新新闻标题列表
   - 参数：
     - category (默认："中国")：新闻类别，可选值：中国、全球、科技、财经
     - count (默认：10)：要返回的新闻标题数量

## 如何触发工具

在与Claude for Desktop对话时，使用以下词条可能会触发工具：

- "今天有什么新闻？"
- "最新的科技新闻是什么？"
- "帮我查看最近的财经消息"
- "有什么重要的全球新闻？"
- "告诉我今天的头条新闻"

您也可以明确提及工具名称：
- "使用get_latest_news工具查看科技新闻"
- "用get_news_titles列出今天的全球新闻标题"

## 自定义和贡献

你可以修改`news_mcp/server.py`中的`NEWS_SOURCES`字典来添加或更改新闻源。

要贡献代码，请遵循以下步骤：

1. Fork 此仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 部署到远程仓库

要将此项目部署到GitHub等远程仓库，请按照以下步骤操作：

1. 在GitHub上创建新仓库
2. 初始化本地git仓库（如果尚未初始化）：

```bash
git init
git add .
git commit -m "Initial commit"
```

3. 添加远程仓库并推送：

```bash
git remote add origin https://github.com/你的用户名/news-mcp.git
git push -u origin main
```

## 注意事项

- 该工具依赖于各新闻网站的HTML结构，如果网站更改布局，可能需要更新爬取逻辑
- 请合理使用，避免频繁请求导致被新闻网站封禁
- 工具只负责获取新闻内容，由AI模型自己负责对内容进行总结和分析 