import httpx
from datetime import datetime
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Any, Optional

# 尝试导入MCP库，如果不存在则提示安装
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("请先安装MCP库：pip install mcp[cli]")
    exit(1)

# 初始化FastMCP服务器
mcp = FastMCP("news_summarizer")

# 定义一些热门新闻网站
NEWS_SOURCES = {
    "中国": ["https://news.sina.com.cn/", "https://news.163.com/"],
    "全球": ["https://news.google.com/", "https://www.bbc.com/news"],
    "科技": ["https://tech.sina.com.cn/", "https://36kr.com/"],
    "财经": ["https://finance.sina.com.cn/", "https://www.cnbc.com/world/"]
}

# 限制爬取的新闻数量
MAX_NEWS_PER_SOURCE = 5


async def fetch_url(url: str) -> Optional[str]:
    """
    从指定URL获取HTML内容
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10.0)
            response.raise_for_status()
            return response.text
    except Exception as e:
        print(f"获取 {url} 失败: {str(e)}")
        return None


def extract_news_from_html(html: str, source_url: str) -> List[Dict[str, str]]:
    """
    从HTML内容中提取新闻标题和链接
    """
    if not html:
        return []
        
    news_list = []
    try:
        soup = BeautifulSoup(html, "html.parser")
        
        # 查找所有可能的新闻链接元素
        for link in soup.find_all("a", href=True):
            title = link.get_text().strip()
            href = link["href"]
            
            # 过滤有效的新闻标题和链接
            if (title and len(title) > 5 and len(title) < 100 and 
                not re.search(r'(登录|注册|投诉|广告|合作|关于我们)', title)):
                
                # 处理相对URL
                if href.startswith("/"):
                    from urllib.parse import urlparse
                    parsed_url = urlparse(source_url)
                    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                    href = base_url + href
                
                # 仅保留看起来像新闻的URL
                if re.search(r'(news|article|story|\d{4}/\d{2}/\d{2}|content|[a-f0-9]{8})', href):
                    news_list.append({"title": title, "url": href})
        
        # 去重并限制数量
        unique_news = []
        seen_titles = set()
        for news in news_list:
            if news["title"] not in seen_titles:
                seen_titles.add(news["title"])
                unique_news.append(news)
                if len(unique_news) >= MAX_NEWS_PER_SOURCE:
                    break
                    
        return unique_news
        
    except Exception as e:
        print(f"解析HTML内容失败: {str(e)}")
        return []


async def extract_article_content(url: str) -> str:
    """
    从新闻URL中提取文章内容
    """
    html = await fetch_url(url)
    if not html:
        return "无法获取文章内容"
        
    try:
        soup = BeautifulSoup(html, "html.parser")
        
        # 移除干扰元素
        for tag in soup.select("script, style, iframe, header, footer, nav, aside"):
            tag.decompose()
        
        # 尝试找到文章主体内容
        article = soup.select_one("article, .article, .content, .article-content, #article, #content")
        
        if article:
            paragraphs = article.find_all("p")
            text = "\n".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
        else:
            # 如果找不到明确的文章容器，尝试收集所有段落
            paragraphs = soup.find_all("p")
            text = "\n".join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 40])
        
        if not text or len(text) < 100:
            return "无法提取有效的文章内容"
            
        return text
    except Exception as e:
        print(f"提取文章内容失败: {str(e)}")
        return "提取文章内容时发生错误"


@mcp.tool()
async def get_latest_news(category: str = "中国", count: int = 5) -> str:
    """
    获取指定类别的最新新闻并返回完整内容

    Args:
        category: 新闻类别，可选值: 中国, 全球, 科技, 财经
        count: 要返回的新闻数量
    """
    if category not in NEWS_SOURCES:
        return f"不支持的新闻类别: {category}。可用类别: {', '.join(NEWS_SOURCES.keys())}"
        
    if count > 10:
        count = 10  # 限制最大返回数量
    
    all_news = []
    source_urls = NEWS_SOURCES[category]
    
    # 爬取每个新闻源
    for url in source_urls:
        html = await fetch_url(url)
        news_list = extract_news_from_html(html, url)
        all_news.extend(news_list)
    
    # 如果没有找到新闻
    if not all_news:
        return f"未能找到 {category} 类别的新闻"
    
    # 只保留请求的数量
    all_news = all_news[:count]
    
    # 获取当前时间
    current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
    
    # 构建返回结果
    result = f"# {category}新闻 (截至 {current_time})\n\n"
    
    # 为每条新闻添加内容
    for i, news in enumerate(all_news):
        result += f"## {i+1}. {news['title']}\n\n"
        content = await extract_article_content(news['url'])
        result += f"{content}\n\n"
        result += f"来源: {news['url']}\n\n---\n\n"
    
    return result


@mcp.tool()
async def get_news_titles(category: str = "中国", count: int = 10) -> str:
    """
    仅获取指定类别的最新新闻标题列表

    Args:
        category: 新闻类别，可选值: 中国, 全球, 科技, 财经
        count: 要返回的新闻标题数量
    """
    if category not in NEWS_SOURCES:
        return f"不支持的新闻类别: {category}。可用类别: {', '.join(NEWS_SOURCES.keys())}"
        
    if count > 20:
        count = 20  # 限制最大返回数量
    
    all_news = []
    source_urls = NEWS_SOURCES[category]
    
    # 爬取每个新闻源
    for url in source_urls:
        html = await fetch_url(url)
        news_list = extract_news_from_html(html, url)
        all_news.extend(news_list)
    
    # 如果没有找到新闻
    if not all_news:
        return f"未能找到 {category} 类别的新闻"
    
    # 只保留请求的数量
    all_news = all_news[:count]
    
    # 获取当前时间
    current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
    
    # 构建返回结果
    result = f"# {category}新闻标题 (截至 {current_time})\n\n"
    
    # 添加新闻标题列表
    for i, news in enumerate(all_news):
        result += f"{i+1}. [{news['title']}]({news['url']})\n"
    
    return result 