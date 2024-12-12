from .base_api import BaseAPI

class CoreAPI(BaseAPI):
    """
    CoreAPI 类用于通过 CORE API 获取学术论文。

    该类继承自 BaseAPI，提供了一种方法 `fetch_papers`，可以通过指定的查询参数获取 CORE 数据库中的学术论文。

    Attributes:
    -----------
    base_url : str
        CORE API 的基本 URL，默认为 "https://api.core.ac.uk/v3/search/works"。
    api_key : str
        CORE API 的访问密钥。
    """
    def __init__(self, api_key, base_url="https://api.core.ac.uk/v3/search/works"):
        super().__init__(base_url)
        self.api_key = api_key

    def fetch_papers(self, query, limit=10):
        """
        使用 CORE API 获取论文。

        :param query: str
            搜索关键词。
        :param limit: int, optional
            每次请求返回的最大论文数量，默认为 10。

        :returns: list of dict
            论文条目列表，每个条目包含以下键：
            - "title": 论文标题。
            - "authors": 作者列表。
            - "abstract": 论文摘要。
            - "link": 论文的页面链接。
            - "pdf_link": 论文 PDF 链接。
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        params = {
            "q": query,
            "limit": limit
        }
        response = self.get_request(self.base_url, headers=headers, params=params)
        if response is None:
            return []

        data = response.json()
        papers = [
            {
                "title": item.get("title", "No title available"),
                "authors": [author.get("name", "Unknown") for author in item.get("authors", [])],
                "abstract": item.get("abstract", "No abstract available").replace("\n", " ").replace("\r", " "),
                "link": next((link["url"] for link in item.get("links", []) if link["type"] == "display"), "No link available"),
                "pdf_link": item.get("downloadUrl", "No PDF link available")
            }
            for item in data.get("results", [])
        ]
        return papers

if __name__ == "__main__":
    core_api_key = "jTdkuvoH7BKncXDaJ6byCgzV4tUE2rlI"
    core_api = CoreAPI(api_key=core_api_key)
    query = "machine learning"
    core_papers = core_api.fetch_papers(query)

    if core_papers:
        print("获取到的 CORE 论文:")
        for i, paper in enumerate(core_papers, 1):
            print(f"{i}. Title: {paper['title']}")
            print(f"   Authors: {', '.join(paper['authors'])}")
            print(f"   Abstract: {paper['abstract']}")
            print(f"   Link: {paper['link']}")
            print(f"   PDF Link: {paper['pdf_link']}\n")
    else:
        print("未能获取到任何 CORE 论文。")