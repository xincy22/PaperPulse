import requests
import re
from .base_api import BaseAPI

class CrossRefAPI(BaseAPI):
    """
    CrossRefAPI 类用于通过 CrossRef API 获取学术论文。

    该类继承自 BaseAPI，提供了一种方法 `fetch_papers`，可以通过指定的查询参数获取 CrossRef 数据库中的学术论文。

    Attributes:
    -----------
    base_url : str
        CrossRef API 的基本 URL，默认为 "https://api.crossref.org/works"。
    """

    def __init__(self, base_url="https://api.crossref.org/works"):
        super().__init__(base_url)

    def fetch_papers(self, query, rows=5):
        """
        使用 CrossRef API 获取论文。

        :param query: str
            搜索关键词。
        :param rows: int, optional
            每次请求返回的最大论文数量，默认为 5。

        :returns: list of dict
            论文条目列表，每个条目包含以下键：
            - "title": 论文标题。
            - "authors": 作者列表。
            - "abstract": 论文摘要。
            - "link": 论文的 DOI 链接。
            - "pdf_link": 论文的 PDF 链接（如果可用）。
        """
        params = {
            'query': query,
            'rows': rows
        }
        response = self.get_request(self.base_url, params=params)
        if response is None:
            return []

        data = response.json()
        papers = []
        for item in data.get('message', {}).get('items', []):
            title = item['title'][0] if 'title' in item else 'No title available'
            authors = [f"{author.get('given', '')} {author.get('family', '')}".strip() for author in item.get('author', [])]
            if not authors:
                authors = ['No authors available']
            abstract = re.sub(r'<.*?>', '', item.get('abstract', 'No abstract available'))
            abstract = abstract.replace('\n', ' ').replace('\r', ' ')
            doi = item.get('DOI', None)
            link = f"https://doi.org/{doi}" if doi else 'No link available'
            pdf_link = self.get_pdf_link_from_unpaywall(doi) if doi else 'No PDF link available'
            papers.append(
                {'title': title, 'authors': authors, 'abstract': abstract, 'link': link, 'pdf_link': pdf_link})
        return papers

    def get_pdf_link_from_unpaywall(self, doi):
        """
        使用 Unpaywall API 获取论文的 PDF 链接。

        :param doi: str
            文章的 DOI。
        :returns: str
            PDF 链接，如果不可用则返回 "No PDF link available"。
        """
        base_url = f"https://api.unpaywall.org/v2/{doi}"
        params = {
            'email': 'xincy22@mails.tsinghua.edu.cn'  # Unpaywall 需要一个联系邮箱
        }
        response = self.get_request(base_url, params=params)
        if response is None:
            return "No PDF link available"

        data = response.json()
        if data.get('is_oa') and data.get('best_oa_location'):
            return data['best_oa_location'].get('url_for_pdf', 'No PDF link available')
        return "No PDF link available"


if __name__ == "__main__":
    crossref_api = CrossRefAPI()
    query = "machine learning"
    papers = crossref_api.fetch_papers(query)

    if papers:
        print("获取到的 CrossRef 论文:")
        for i, paper in enumerate(papers, 1):
            print(f"{i}. Title: {paper['title']}")
            print(f"   Authors: {', '.join(paper['authors'])}")
            print(f"   Abstract: {paper['abstract']}")
            print(f"   Link: {paper['link']}")
            print(f"   PDF Link: {paper['pdf_link']}\n")
    else:
        print("未能获取到任何 CrossRef 论文。")
