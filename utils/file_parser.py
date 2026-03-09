import pandas as pd
import pdfplumber
from docx import Document
from bs4 import BeautifulSoup


def parse_file_to_text(file_bytes, file_name):

    ext = file_name.lower().split(".")[-1]

    if ext in ["txt", "md", "markdown", "mdx", "properties"]:
        return file_bytes.decode("utf-8")

    if ext in ["html", "htm"]:
        html = file_bytes.decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator="\n")

    if ext == "pdf":
        text = ""
        with pdfplumber.open(file_bytes) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text

    if ext in ["docx"]:
        doc = Document(file_bytes)
        return "\n".join([p.text for p in doc.paragraphs])

    if ext in ["csv"]:
        df = pd.read_csv(file_bytes)
        return df.to_string()

    if ext in ["xlsx", "xls"]:
        df = pd.read_excel(file_bytes)
        return df.to_string()

    if ext == "vtt":
        lines = file_bytes.decode("utf-8").splitlines()
        text = []
        for line in lines:
            if "-->" not in line and line.strip():
                text.append(line)
        return "\n".join(text)

    raise ValueError(f"Unsupported file type: {ext}")