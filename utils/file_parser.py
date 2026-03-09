import io  # 必须引入这个库
import pandas as pd
import pdfplumber
from docx import Document
from bs4 import BeautifulSoup

def parse_file_to_text(file_bytes, file_name):
    ext = file_name.lower().split(".")[-1]

    # 1. 处理纯文本类
    if ext in ["txt", "md", "markdown", "mdx", "properties"]:
        return file_bytes.decode("utf-8")

    # 2. 处理 PDF (修复点)
    if ext == "pdf":
        text = ""
        # 使用 io.BytesIO 将 bytes 转换为模拟文件对象
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:  # 避免提取到空页时报错
                    text += page_text + "\n"
        return text

    # 3. 处理 Word (docx 同样需要 BytesIO)
    if ext in ["docx"]:
        return "\n".join([p.text for p in Document(io.BytesIO(file_bytes)).paragraphs])

    # 4. 处理 Excel/CSV (pandas 通常能直接处理 bytes，但 BytesIO 更稳)
    if ext in ["csv"]:
        return pd.read_csv(io.BytesIO(file_bytes)).to_string()

    if ext in ["xlsx", "xls"]:
        return pd.read_excel(io.BytesIO(file_bytes)).to_string()

    # 5. 处理 HTML
    if ext in ["html", "htm"]:
        html = file_bytes.decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator="\n")

    # 6. 处理 VTT
    if ext == "vtt":
        lines = file_bytes.decode("utf-8").splitlines()
        text = []
        for line in lines:
            if "-->" not in line and line.strip():
                text.append(line)
        return "\n".join(text)

    raise ValueError(f"Unsupported file type: {ext}")