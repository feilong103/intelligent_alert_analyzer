import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import time

import streamlit as st

from src.knowledge_base import KnowledgeBaseService

# 添加网页标题
st.title("知识库更新服务")

# file_uploader
uploader_file = st.file_uploader(
    "请上传 TXT 文件",
    type=['txt'],
    accept_multiple_files=False
)


if "kb_service" not in st.session_state:
    st.session_state["kb_service"] = KnowledgeBaseService()

if uploader_file is not None:
    # 提取文件的信息
    file_name = uploader_file.name
    file_type = uploader_file.type
    file_size = uploader_file.size / 1024 # KB

    st.subheader(f"文件名：{file_name}")
    st.write(f"格式：{file_type} | {file_size:.2f} KB")

    # 获取值
    text = uploader_file.getvalue().decode("utf-8")


    with st.spinner("载入知识库中···"):

        time.sleep(1)

        # 写入向量库
        result = st.session_state["kb_service"].upload_by_str(text, file_name)

        st.write(result)
