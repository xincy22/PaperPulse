from .base_api import BaseAPI
import feedparser
import re

class ArxivAPI(BaseAPI):
    """
    ArxivAPI 类用于通过 arXiv API 获取学术论文。

    该类继承自 BaseAPI，提供了一种方法 `fetch_papers`，可以通过指定的查询参数获取 arXiv 数据库中的学术论文。

    Attributes:
    -----------
    base_url : str
        arXiv API 的基本 URL，默认为 "https://export.arxiv.org/api/query"。
    """
    def __init__(self, base_url="https://export.arxiv.org/api/query"):
        super().__init__(base_url)

    def fetch_papers(self, query, start=0, max_results=10):
        """
        使用 arXiv API 获取论文。

        :param query: str
            搜索关键词。
        :param start: int, optional
            分页的开始索引，默认为 0。
        :param max_results: int, optional
            每次请求返回的最大论文数量，默认为 10。

        :returns: list of dict
            论文条目列表，每个条目包含以下键：
            - "title": 论文标题。
            - "authors": 作者列表。
            - "abstract": 论文摘要。
            - "link": 论文的页面链接。
            - "pdf_link": 论文 PDF 链接。
        """
        api_url = f"{self.base_url}?search_query={query}&start={start}&max_results={max_results}"
        response = self.get_request(api_url)
        if response is None:
            return []

        feed = feedparser.parse(response.text)
        papers = []
        for entry in feed.entries:
            title = entry.title if hasattr(entry, 'title') else 'No title available'
            authors = [author.name for author in entry.authors] if hasattr(entry, 'authors') else ['No authors available']
            abstract = re.sub(r'\n', ' ', entry.summary) if hasattr(entry, 'summary') else 'No abstract available'
            link = entry.link if hasattr(entry, 'link') else 'No link available'
            pdf_link = entry.id.replace("abs", "pdf") + ".pdf" if hasattr(entry, 'id') else 'No PDF link available'
            papers.append({'title': title, 'authors': authors, 'abstract': abstract, 'link': link, 'pdf_link': pdf_link})
        return papers

if __name__ == "__main__":
    arxiv_api = ArxivAPI()
    query = "machine learning"
    papers = arxiv_api.fetch_papers(query)

    if papers:
        print("获取到的 arXiv 论文:")
        for i, paper in enumerate(papers, 1):
            print(f"{i}. Title: {paper['title']}")
            print(f"   Authors: {', '.join(paper['authors'])}")
            print(f"   Abstract: {paper['abstract']}")
            print(f"   Link: {paper['link']}")
            print(f"   PDF Link: {paper['pdf_link']}\n")
    else:
        print("未能获取到任何 arXiv 论文。")