import requests
import hashlib
import random


class BaiduTranslateClient:
    """
    BaiduTranslateClient 类用于与百度翻译 API 进行交互，将文本从一种语言翻译为另一种语言。

    该类通过指定 APP_ID 和 SECRET_KEY 与百度翻译 API 交互，返回翻译后的文本。

    Attributes:
    -----------
    app_id : str
        百度翻译 API 的 APP ID。
    secret_key : str
        百度翻译 API 的 SECRET KEY。
    api_url : str
        百度翻译 API 的基本 URL，默认为 "https://fanyi-api.baidu.com/api/trans/vip/translate"。
    """

    def __init__(self, app_id, secret_key):
        self.app_id = app_id
        self.secret_key = secret_key
        self.api_url = "https://fanyi-api.baidu.com/api/trans/vip/translate"

    def translate(self, text, from_lang='en', to_lang='zh'):
        """
        使用百度翻译 API 将文本翻译为目标语言。

        :param text: str
            要翻译的文本。
        :param from_lang: str, optional
            源语言，默认为 'en'（英文）。
        :param to_lang: str, optional
            目标语言，默认为 'zh'（中文）。
        :returns: str
            翻译后的文本。
        """
        salt = str(random.randint(32768, 65536))
        sign = self.generate_sign(text, salt)

        params = {
            'q': text,
            'from': from_lang,
            'to': to_lang,
            'appid': self.app_id,
            'salt': salt,
            'sign': sign
        }

        response = requests.get(self.api_url, params=params)
        if response.status_code == 200:
            result = response.json()
            if 'trans_result' in result:
                return result['trans_result'][0]['dst']
            else:
                return "翻译失败"
        else:
            return "请求失败"

    def generate_sign(self, text, salt):
        """
        生成百度翻译 API 请求所需的签名。

        :param text: str
            要翻译的文本。
        :param salt: str
            随机数。
        :returns: str
            生成的签名。
        """
        sign_str = f"{self.app_id}{text}{salt}{self.secret_key}"
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest()


if __name__ == "__main__":
    # 你的百度翻译 API 的 APP_ID 和 SECRET_KEY
    app_id = "20240227001975820"
    secret_key = "wRu2MkC9BM44Hyo35Jmo"

    baidu_client = BaiduTranslateClient(app_id, secret_key)
    abstract = "Machine learning is transforming the medical field by providing new methods for diagnosis and treatment."
    translated_abstract = baidu_client.translate(abstract)
    print(f"翻译后的摘要: {translated_abstract}")