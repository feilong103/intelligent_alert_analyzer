from langchain_community.chat_models import ChatTongyi
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

import config.settings as config


class DataCleanerService(object):

    def __init__(self):
        # 针对 RAG 语义分块专门设计的结构化提示词
        prompt_text = """你是一个严谨的 RAG（检索增强生成）知识库数据处理专家。
你的任务是将用户提供的原始文档解析文本，清洗并拆分成多个“具备完整语义的最小独立知识片段”。

【核心原则】
1. 语义独立与完整：每个输出的片段必须能够独立存在。如果单看这个片段，读者也能完全理解其含义，无需去寻找上下文。
2. 消除代词与补全上下文：原始文本中通常有层级结构（如章-节-小点）。在拆分时，你必须将父级标题或主语“融入”到子片段中。例如，原文本是“1. 纯棉材质 \\n 洗涤：可机洗”，切分后的片段必须补全为：“【春季服装-纯棉材质】的洗涤方法：可机洗...”，绝不能只保留“洗涤：可机洗”。
3. 最小化粒度：在保证语义完整的前提下，片段越精简越好。不要把两件不相干的事情放在一个片段里。
4. 数据清洗：去除无意义的乱码、多余的换行符、页眉页脚等噪音。将表格或零碎的列表转化为通顺的自然语言描述。

【输出格式要求】
- 严格使用 ---------- （10个连字符）作为每个片段之间的唯一分隔符。
- 每个片段前后换行，保持整洁。
- 绝对不要输出任何开头问候语、解释性文字或“以下是清洗后的结果”等客套话。只输出片段和分隔符。

【示例】
输入：
三、秋季服装
1. 厚牛仔材质
洗涤：水温≤30℃，中性洗涤剂。
养护：翻面阴干，避免暴晒。

输出：
【秋季服装-厚牛仔材质】洗涤方法：建议水温≤30℃，使用中性洗涤剂。
----------
【秋季服装-厚牛仔材质】养护方法：建议翻面阴干，避免暴晒。

====================
请处理以下原始文本：
{raw_text}
"""

        self.prompt_template = PromptTemplate.from_template(prompt_text)

        # 建议适当调低 temperature 以保证模型输出格式的稳定性，减少幻觉
        self.chat_model = ChatTongyi(model=config.chat_model, temperature=0.1)

        self.chain = self.__get_chain()

    def __get_chain(self):
        def print_prompt(prompt):
            print("=" * 50 + " 正在发送给 LLM 的 Prompt " + "=" * 50)
            print(prompt.to_string())
            print("=" * 126)
            return prompt

        chain = self.prompt_template | print_prompt | self.chat_model | StrOutputParser()
        return chain


if __name__ == "__main__":
    data = """
    一、春季服装（纯棉、薄牛仔、针织棉、轻薄化纤）
    1. 纯棉材质（春季衬衫、T恤、休闲裤）
    洗涤：可机洗或手洗，水温≤30℃，中性洗涤剂；浅色与深色分开洗，首次洗加少许盐固色；机洗用洗衣袋+轻柔模式，避免摩擦起球。
    养护：阴凉通风处阴干，避免暴晒褪色；收纳前完全干燥，折叠或宽肩悬挂；潮湿天放干燥剂防发霉。
    """  # 这里截取部分数据演示

    service = DataCleanerService()

    # 注意这里传入的变量名改为了 raw_text
    result_str = service.chain.invoke({"raw_text": data})


    print("\n" + "=" * 50 + " LLM 返回的清洗结果 " + "=" * 50)
    print(result_str)

    print("\n" + "=" * 50 + " 解析为列表格式 " + "=" * 50)
    # 按分隔符切分并去除首尾空白
    chunks = [chunk.strip() for chunk in result_str.split("----------") if chunk.strip()]
    for i, chunk in enumerate(chunks):
        print(f"片段 {i + 1}:\n{chunk}\n")