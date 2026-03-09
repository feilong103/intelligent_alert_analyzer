import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

from src.knowledge_base import KnowledgeBaseService
from utils.data_cleaner import DataCleanerService
from utils.file_parser import parse_file_to_text


st.title("知识库更新服务")

# ------------------------------
# Session 初始化
# ------------------------------

if "kb_service" not in st.session_state:
    st.session_state["kb_service"] = KnowledgeBaseService()

if "cleaner" not in st.session_state:
    st.session_state["cleaner"] = DataCleanerService()

if "raw_text" not in st.session_state:
    st.session_state["raw_text"] = ""

if "llm_result" not in st.session_state:
    st.session_state["llm_result"] = ""

if "chunks" not in st.session_state:
    st.session_state["chunks"] = []


# ------------------------------
# 文件上传
# ------------------------------

uploader_file = st.file_uploader(
    "上传知识库文件",
    type=[
        "html","properties","md","htm","mdx","markdown",
        "pdf","xlsx","csv","xls","docx","vtt","txt"
    ],
    accept_multiple_files=False
)


# ------------------------------
# 文件解析
# ------------------------------

if uploader_file is not None:

    file_name = uploader_file.name
    file_type = uploader_file.type
    file_size = uploader_file.size / 1024

    st.subheader(f"文件名：{file_name}")
    st.write(f"格式：{file_type} | {file_size:.2f} KB")

    file_bytes = uploader_file.getvalue()

    text = parse_file_to_text(file_bytes, file_name)

    st.session_state["raw_text"] = text

    st.success("文件解析完成")

    st.divider()

    # ------------------------------
    # LLM 自动分割
    # ------------------------------

    if st.button("开始 LLM 知识切分"):

        with st.spinner("LLM 正在清洗并拆分知识..."):

            result_str = st.session_state["cleaner"].chain.invoke({
                "raw_text": text
            })

        st.session_state["llm_result"] = result_str

        chunks = [
            chunk.strip()
            for chunk in result_str.split("----------")
            if chunk.strip()
        ]

        st.session_state["chunks"] = chunks

        # 初始化 chunk session
        for i, chunk in enumerate(chunks):
            st.session_state[f"chunk_{i}"] = chunk

        st.success(f"LLM 切分完成，共生成 {len(chunks)} 个知识片段")



# ------------------------------
# LLM结果整体编辑
# ------------------------------

if st.session_state["llm_result"]:

    st.divider()

    st.subheader("LLM 分割结果（可整体编辑）")

    st.caption("提示：使用 ---------- 作为知识片段分隔符")

    edited_result = st.text_area(
        "你可以修改 LLM 输出，并通过调整 ---------- 实现二次分割",
        value=st.session_state["llm_result"],
        height=400
    )

    col1, col2 = st.columns(2)

    # ------------------------------
    # 重新解析
    # ------------------------------

    with col1:

        if st.button("重新解析分割结果"):

            # 清理旧 chunk session
            for key in list(st.session_state.keys()):
                if key.startswith("chunk_"):
                    del st.session_state[key]

            st.session_state["llm_result"] = edited_result

            chunks = [
                chunk.strip()
                for chunk in edited_result.split("----------")
                if chunk.strip()
            ]

            st.session_state["chunks"] = chunks

            # 重新写入 chunk session
            for i, chunk in enumerate(chunks):
                st.session_state[f"chunk_{i}"] = chunk

            st.success(f"重新解析完成，共 {len(chunks)} 个知识片段")

            st.rerun()

    with col2:

        st.write(f"当前检测到 **{len(st.session_state['chunks'])}** 个知识片段")


# ------------------------------
# 逐条 chunk 编辑
# ------------------------------

if st.session_state["chunks"]:

    st.divider()

    st.subheader("知识片段逐条编辑")

    edited_chunks = []

    for i, chunk in enumerate(st.session_state["chunks"]):

        with st.expander(f"知识片段 {i+1}", expanded=False):

            edited = st.text_area(
                label=f"编辑片段 {i+1}",
                value=st.session_state.get(f"chunk_{i}", chunk),
                height=150,
                key=f"chunk_{i}"
            )

            st.caption(f"字符数: {len(edited)}")

            if st.button(f"删除片段 {i+1}", key=f"delete_{i}"):

                st.session_state["chunks"].pop(i)

                # 删除对应 session
                if f"chunk_{i}" in st.session_state:
                    del st.session_state[f"chunk_{i}"]

                st.rerun()

            edited_chunks.append(edited)


    st.divider()

    # ------------------------------
    # 上传 KB
    # ------------------------------

    if st.button("确认上传知识库"):

        with st.spinner("正在写入知识库..."):

            result = st.session_state["kb_service"].upload_by_chunks(
                edited_chunks,
                uploader_file.name
            )

        st.success("知识库更新完成")

        st.write(result)