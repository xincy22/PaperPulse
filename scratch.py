# scratch.py
from scraper import CoreAPI, ArxivAPI, CrossRefAPI
from llm import ChatGLMClient
from translate import BaiduTranslateClient
from api_manager import database as db
import config as cfg
import requests
import os
import re
from tkinter import filedialog, Tk

# 创建存储论文的文件夹
if cfg.storage_path is None:
    root = Tk()
    root.withdraw()  # 隐藏主窗口
    storage_path = filedialog.askdirectory(title="请选择保存论文的文件夹")
    root.destroy()
else:
    storage_path = cfg.storage_path

if not storage_path:
    print("未选择保存路径，程序退出。")
    exit()

storage_path = storage_path + "/papers"
os.makedirs(storage_path, exist_ok=True)

# 初始化 ChatGLMClient
chatglm_info = db.get_api_key("ChatGLM")
chatglm_client = ChatGLMClient(api_key=chatglm_info[2])

# 初始化翻译客户端
baidu_info = db.get_api_key("Baidu Translate")
translator = BaiduTranslateClient(app_id=baidu_info[3], secret_key=baidu_info[4])

# 生成关键词
text = input("请输入需要查询的内容: ")
keywords = chatglm_client.generate_keywords(text)
print("生成的关键词: ", keywords)

# 翻译关键词并使用翻译后的关键词搜索
keywords = [translator.translate(keyword, from_lang='zh', to_lang='en') for keyword in keywords]
print("翻译后的关键词: ", keywords)

# 使用 arXiv API 搜索论文
arxiv_info = db.get_api_key("arXiv API")
arxiv_api = ArxivAPI(base_url=arxiv_info[5])
arxiv_papers = arxiv_api.fetch_papers(" ".join(keywords))

# 使用 CORE API 搜索论文
core_info = db.get_api_key("CORE API")
core_api = CoreAPI(api_key=core_info[2], base_url=core_info[5])
core_papers = core_api.fetch_papers(" ".join(keywords))

# 使用 CrossRef API 搜索论文
crossref_info = db.get_api_key("CrossRef API")
crossref_api = CrossRefAPI(base_url=crossref_info[5])
crossref_papers = crossref_api.fetch_papers(" ".join(keywords))

# 合并所有获取到的论文
all_papers = arxiv_papers + core_papers + crossref_papers

# 去重
unique_papers = {paper['link']: paper for paper in all_papers}.values()

# 逐个输出论文信息，并询问是否下载
for paper in unique_papers:
    title = paper['title']
    try:
        authors = ", ".join([f"{author.get('given', '')} {author.get('family', '')}".strip() if isinstance(author, dict) else author for author in paper.get('authors', [])]) or 'No authors available'
    except Exception:
        authors = 'No authors available'
    abstract_en = paper['abstract']
    abstract_zh = translator.translate(abstract_en)
    link = paper['link']
    pdf_link = paper['pdf_link']

    print(f"\nTitle: {title}")
    print(f"Authors: {authors}")
    print(f"Abstract (EN): {abstract_en}")
    print(f"Abstract (ZH): {abstract_zh}")
    print(f"Link: {link}")
    print(f"PDF Link: {pdf_link}")

    if pdf_link == 'No PDF link available' or pdf_link is None:
        input("按任意键继续查看下一篇论文...")
        continue

    download = None
    while download not in ['y', 'n']:
        download = input("是否下载此论文? (y/n): ").strip().lower()
    if download == 'y':
        # 将标题中的非中英文字符替换为下划线
        sanitized_title = re.sub(r'[^\w一-鿿]+', '_', title)
        filename = os.path.join(storage_path, f"{sanitized_title}.pdf")
        try:
            response = requests.get(pdf_link)
            response.raise_for_status()
            with open(filename, 'wb') as f:
                f.write(response.content)
                print(f"论文已下载: {filename}")
        except requests.RequestException as e:
            print(f"无法下载论文: {filename}, 错误信息: {e}")
    elif download != 'y':
        print("跳过下载该论文。")