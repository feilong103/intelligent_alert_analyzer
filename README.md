# 智能告警分析系统 - RAG 应用

基于 LangChain 框架开发的 RAG（检索增强生成）智能告警分析系统。

## 功能特性

- 知识库管理：支持 TXT 文本文件上传，自动向量化并存入向量数据库
- 向量检索：使用 Chroma 向量数据库进行语义检索

## 技术栈

- **框架**: LangChain
- **LLM**: 通义千问 (qwen-plus)
- **Embedding**: 通义千问 text-embedding-v4
- **向量数据库**: Chroma
- **Web界面**: Streamlit

## 项目结构

```
intelligent_alert_analyzer/
├── config/settings.py     # 配置文件
├── src/                   # 核心服务模块
│   ├── __init__.py
│   ├── rag.py            # RAG 服务主类
│   ├── knowledge_base.py # 知识库服务
│   └── vector_stores.py  # 向量存储服务
├── apps/                  # Streamlit 应用
│   ├── __init__.py
│   └── app_file_uploader.py # 知识库上传应用
├── storage/               # 存储目录
│   └──  chroma_db/        # 向量数据库
├── requirements.txt       # 依赖清单
├── .gitignore            # Git 忽略配置
└── README.md             # 项目说明
```

## 安装

```bash
pip install -r requirements.txt
```

## 配置

在 `config.py` 中配置以下参数：

```python
# 模型配置
embedding_model = "text-embedding-v4"  # 向量嵌入模型
chat_model = "qwen-plus"              # 对话模型

# 向量数据库配置
collection_name = "rag"
persist_directory = "./storage/chroma_db"

# 文本分割配置
chunk_size = 50
chunk_overlap = 0
separators = ["\n", "\n\n", "。"]

# 检索配置
similarity_k = 2  # 返回匹配文档数量
```

## 使用

### 上传知识库

启动知识库上传服务：

```bash
streamlit run apps/app_file_uploader.py
```

上传 TXT 文件，内容将自动向量化并存入向量数据库。



## 依赖

- langchain
- langchain-community
- langchain-chroma
- langchain-core
- streamlit
- chromadb
- dashscope

## 注意事项

- 首次运行需要配置通义千问的 API Key
- 已上传的知识库文件会通过 MD5 去重，避免重复处理