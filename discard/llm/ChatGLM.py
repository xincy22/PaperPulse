from zhipuai import ZhipuAI
import warnings
import json
import re


class ChatGLMClient:
    """
    ChatGLMClient 类用于与 ChatGLM API 进行交互，用于生成用户想要的论文关键词或主题。

    该类通过指定系统提示和用户输入与 ChatGLM 模型交互，返回生成的内容。

    Attributes:
    -----------
    api_key : str
        ChatGLM API 密钥。
    client : ZhipuAI
        用于与 ChatGLM 进行 API 调用的客户端实例。
    system_prompt : str
        系统提示，定义模型的行为。
    """

    def __init__(self, api_key=None):
        if api_key is None:
            warnings.warn("ChatGLM API key not found. Please provide an API key.")
            self.api_key = self.input_api_key()
        else:
            self.api_key = api_key

        self.client = ZhipuAI(api_key=self.api_key)
        self.system_prompt = """
        ### Prompt

        请根据以下用户的自然语言输入生成一个包含最贴合的两个论文关键词的 JSON 数据。关键词信息包括以下字段：
        - 关键词列表 (keywords)，其值必须是包含两个最贴合关键词的数组。
        如果用户只输入了一个关键词，或者你找不到第二个关键词了，请给这个关键词找一个同义词。不要随意发挥。

        ### 用户输入示例

        用户输入: 我想写一篇关于机器学习应用于医疗的论文，给我一些关键词。

        ### 示例输出

        ```json
        {
          "keywords": ["机器学习", "医疗"]
        }
        ```

        ### 注意事项
        1. `keywords` 字段的值必须是一个数组，包含两个最贴合与用户输入相关的关键词。
        2. 输出必须是 JSON 格式。
        """

    def set_system_prompt(self, prompt):
        """
        设置系统提示。

        :param prompt: str
            系统提示，定义模型的行为。
        """
        self.system_prompt = prompt

    def generate_keywords(self, prompt):
        """
        根据用户输入生成论文的关键词或主题。

        :param prompt: str
            用户输入，自然语言描述。
        :returns: list of str
            生成的最贴合的两个关键词或主题列表。
        """
        str_data = self.client.chat.completions.create(
            model='glm-4-airx',
            messages=[
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        ).choices[0].message.content

        dict_data = self.json_to_dict(str(str_data))
        keywords = dict_data.get('keywords', [])
        return keywords[:2]  # 返回最贴合的两个关键词

    @staticmethod
    def input_api_key():
        """
        提示用户输入 API 密钥。

        :returns: str
            用户输入的 API 密钥。
        """
        return input("Please enter your ChatGLM API key: ")

    @staticmethod
    def json_to_dict(str_data):
        """
        将 JSON 格式的字符串转换为字典。

        :param str_data: str
            包含 JSON 数据的字符串。
        :returns: dict
            转换后的字典。
        """
        pattern = r'\{[^{}]*\}'
        match = re.search(pattern, str_data)
        if match:
            json_str = match.group()
            return json.loads(json_str)
        else:
            raise ValueError("Invalid string format.")

if __name__ == "__main__":
    api_key = "4d701b71cb8f865ee09048d83a16de25.Yg7yClqiDqNOVMTy"
    chatglm_client = ChatGLMClient(api_key=api_key)
    user_prompt = "我想要了解一些波动光学光计算前沿的知识。"
    keywords = chatglm_client.generate_keywords(user_prompt)

    if keywords:
        print("生成的关键词:")
        for i, keyword in enumerate(keywords, 1):
            print(f"{i}. {keyword}")
    else:
        print("未能生成任何关键词。")