"""
知识库
"""
import os
from datetime import datetime
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings


import config.settings as config
from utils.md5 import save_md5, get_string_md5, check_md5
from utils.data_cleaner import DataCleanerService


class KnowledgeBaseService(object):
    def __init__(self):
        # 确保 chroma 持久化目录存在
        os.makedirs(config.persist_directory, exist_ok=True)

        self.chroma = Chroma(
            collection_name=config.collection_name,
            embedding_function=DashScopeEmbeddings(model=config.embedding_model),
            persist_directory=config.persist_directory
        )


    def upload_by_str(self, data, filename):
        """ 将传入的字符串进行向量化，存入向量数据库中 """

        # 先得到传入字符串的 md5 值
        md5_hex = get_string_md5(data)

        if check_md5(md5_hex):
            return "[跳过]内存已经存在知识库中"

        # 分隔前使用 LLM 清洗数据并进行语义分块
        data_cleaner_service = DataCleanerService()
        cleaned_data = data_cleaner_service.chain.invoke({"raw_text": data})

        print("========== LLM 返回的清洗数据 ==========")
        print(cleaned_data)
        print("========================================")

        # 🎯 核心修改点：使用原生 split 精准切分，并过滤掉空字符串
        knowledge_chunks = [
            chunk.strip()
            for chunk in cleaned_data.split("----------")
            if chunk.strip()
        ]

        # 如果清洗后没有得到任何有效数据，直接返回
        if not knowledge_chunks:
            return "[失败]未提取到有效的知识片段，请检查原始数据或 LLM 输出"

        for i, chunk in enumerate(knowledge_chunks):
            print(f"正在处理 Chunk {i+1}: \n{chunk}\n")

        # 组装元数据
        metadata = {
            "source": filename,
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator": "小王"
        }

        # 写入向量数据库中
        self.chroma.add_texts(
            texts=knowledge_chunks,
            metadatas=[metadata for _ in knowledge_chunks]
        )

        # 处理完成的数据写入 md5
        save_md5(md5_hex)

        return f"[成功]内容已成功载入向量库，共切分为 {len(knowledge_chunks)} 个片段"


if __name__ == '__main__':

    kb_service = KnowledgeBaseService()

    text = """
    1.  肤色与服装颜色搭配原则
    冷白皮：适合冷色调和暖色调，亮色系（如宝蓝、正红、薄荷绿）更显白皙透亮；深色系（如黑色、深灰）可提升气场，避免过于苍白。
    黄皮/暖黄皮：优先选暖色调（如焦糖色、姜黄色、豆沙色），避免冷调荧光色（如荧光绿、冷粉），易显肤色暗沉；浅米色、燕麦色可柔和肤色，提升气色。
    黑皮：适合高饱和度亮色（如明黄、橙色、湖蓝），突出健康肤色；避免暗沉的土黄色、灰褐色，易显肤色暗沉无光。

    2.  场合与服装颜色选择
    日常通勤：以基础色为主（黑白灰、米色、藏蓝），简约大气；可搭配低饱和度亮色（如雾霾蓝、浅紫）作为点缀，增加活力。
    正式场合（商务会议/面试）：首选深色系（黑色、藏蓝、深灰），稳重专业；避免大面积亮色和花哨图案，保持简洁得体。
    休闲场合（逛街/出游）：可选择高饱和度颜色或撞色搭配（如黄+白、蓝+白），清新活泼；条纹、格纹等基础图案也适合休闲场景。
    宴会/派对：可选择亮色（正红、酒红、宝蓝）或金属色（金色、银色），凸显气质；避免过于朴素的颜色，降低存在感。
    """

    result = kb_service.upload_by_str(text, "testfile.txt")

    print(result)