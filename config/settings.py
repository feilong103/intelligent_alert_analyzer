# file storage settings
md5_file_path = "./storage/md5.txt"

# model settings
embedding_model = "text-embedding-v4"
chat_model = "qwen-plus"

# Chroma settings
collection_name = "rag"
persist_directory = "./storage/chroma_db"

# spliter settings
chunk_size = 50
chunk_overlap = 0
separators = ["\n", "\n\n", "。"]

# 检索返回匹配的文档数量
similarity_k = 2