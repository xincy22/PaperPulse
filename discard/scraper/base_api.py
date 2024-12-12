import requests


class BaseAPI:
    """
    BaseAPI 类是用于不同学术论文 API 的基类。

    该类提供了基本的 HTTP 请求功能，可以被继承用于实现具体的 API 类。

    Attributes:
    -----------
    base_url : str
        API 的基本 URL。
    """

    def __init__(self, base_url):
        self.base_url = base_url

    def get_request(self, url, headers=None, params=None):
        """
        发送 GET 请求并返回响应内容。

        :param url: str
            请求的 URL。
        :param headers: dict, optional
            请求的头部信息，默认为 None。
        :param params: dict, optional
            请求的参数，默认为 None。

        :returns: requests.Response
            请求的响应对象。
        """
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return None
