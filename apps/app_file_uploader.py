import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import streamlit as st

from src.knowledge_base import KnowledgeBaseService
from utils.file_parser import parse_file_to_text


st.title("知识库更新服务")

uploader_file = st.file_uploader(
    "上传知识库文件",
    type=[
        "html","properties","md","htm","mdx","markdown",
        "pdf","xlsx","csv","xls","docx","vtt","txt"
    ],
    accept_multiple_files=False
)


if "kb_service" not in st.session_state:
    st.session_state["kb_service"] = KnowledgeBaseService()


if uploader_file is not None:

    file_name = uploader_file.name
    file_type = uploader_file.type
    file_size = uploader_file.size / 1024

    st.subheader(f"文件名：{file_name}")
    st.write(f"格式：{file_type} | {file_size:.2f} KB")

    file_bytes = uploader_file.getvalue()

    # 解析文件
    text = parse_file_to_text(file_bytes, file_name)

    with st.spinner("载入知识库中···"):

        time.sleep(1)

        result = st.session_state["kb_service"].upload_by_str(text, file_name)

        st.write(result)