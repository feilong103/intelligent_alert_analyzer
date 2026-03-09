from langchain_community.chat_models import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnablePassthrough

from src.vector_stores import VectorStoreService
import config.settings as config
import config.prompt as prompt

class RagService(object):

    def __init__(self):
        self.vector_service = VectorStoreService(
            embedding=DashScopeEmbeddings(model=config.embedding_model)
        )

        # self.prompt_template = ChatPromptTemplate.from_messages(
        #     [
        #         ("system", "以我提供的已知参考资料为主，简洁和专业的回答用户的问题。参考资料：{context}"),
        #         ("human", "请回答用户提问：{input}")
        #     ]
        # )

        self.prompt_template = PromptTemplate.from_template(
            prompt.system_prompt + "以我提供的已知参考资料为主，简洁和专业的回答用户的问题。参考资料：{context}，现在请分析以下告警：{alert_json}，请返回JSON结果。"
        )

        self.chat_model = ChatTongyi(model=config.chat_model)

        self.chain = self.__get_chain()

    def __get_chain(self):
        """ 获取最终的执行链 """
        retriever = self.vector_service.get_retriever()

        def format_document(docs: list[Document]):
            if not docs:
                return "无相关参考资料"

            formatted_str = ""
            for doc in docs:
                formatted_str += f"文档片段：{doc.page_content}\n 文档元数据：{doc.metadata}\n\n"
            return formatted_str

        def print_prompt(prompt):
            print("="*150)
            print(prompt.to_string())
            print("="*150)
            return prompt


        chain = (
            {"alert_json": RunnablePassthrough(),"context": retriever | format_document} | self.prompt_template | print_prompt | self.chat_model | StrOutputParser()
        )

        return chain

if __name__ == "__main__":

    alert = """
	{
		"eve_detail": "HFISH(袭鑫宇)-VPHFISHAP03  Linux: HFISH(袭鑫宇)-VPHFISHAP03 Load average is too high  0.24",
		"eve_host": "HFISH(袭鑫宇)-VPHFISHAP03",
		"eve_ip": "11.24.200.52",
		"eve_labels": {
			"application": "",
			"application_role": "",
			"category": "S03",
			"class": "os",
			"component": "cpu",
			"environment": "",
			"hypervisor_id": "",
			"location": "",
			"network_devices": "",
			"provider": "",
			"region": "",
			"scope": "performance",
			"sub_category": "OTHER",
			"target": "linux"
		},
		"eve_level": "5",
		"eve_metric": "Linux: {HOST.NAME} Load average is too high",
		"eve_metric_value": "0.24",
		"eve_source": "Zabbix",
		"eve_status": "RESOLVED",
		"eve_summary": "【Zabbix6.0】VPHFISHAP03 Linux: HFISH(袭鑫宇)-VPHFISHAP03 Load average is too high 0.24",
		"eve_time_create": "2026.03.06 04:37:04",
		"eve_time_resovled": "2026.03.06 04:37:04",
		"eve_uid": "VPHFISHAP03-211596",
		"tenant_id": "0004",
		"token": "AAbfi3HqJqquJW9bYGQ2n",
		"url": "https://oncall.rynnova.com/api/webhook:trigger/xqevwukg0wz"
	}
    """

    res = RagService().chain.stream(alert)

    for chunk in res:
        print(chunk, end="", flush=True)