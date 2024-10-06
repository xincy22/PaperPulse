import api_manager.database as db

storage_path = None

db.insert_api_key(api_name="Baidu Translate", app_id="20240227001975820", secret_key="wRu2MkC9BM44Hyo35Jmo",
                  base_url="https://fanyi-api.baidu.com/api/trans/vip/translate")
db.insert_api_key(api_name="ChatGLM", api_key="4d701b71cb8f865ee09048d83a16de25.Yg7yClqiDqNOVMTy",
                  base_url="https://chatglm.example.com/api")
db.insert_api_key(api_name="CORE API", api_key="jTdkuvoH7BKncXDaJ6byCgzV4tUE2rlI",
                  base_url="https://api.core.ac.uk/v3/search/works")
db.insert_api_key(api_name="arXiv API", base_url="https://export.arxiv.org/api/query")
db.insert_api_key(api_name="CrossRef API", base_url="https://api.crossref.org/works")