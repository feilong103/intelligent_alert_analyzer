import config.settings as config
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings

class VectorStoreService(object):
    def __init__(self, embedding):
        """"
        :param embedding: 向量嵌入模型
        """
        self.embedding = embedding

        self.vector_store = Chroma(
            collection_name=config.collection_name,
            embedding_function=self.embedding,
            persist_directory=config.persist_directory
        )

    def get_retriever(self):
        """ 返回向量检索器 方便加入 chain """
        return self.vector_store.as_retriever(search_kwargs={"k": config.similarity_k})

if __name__ == "__main__":
    retriever = VectorStoreService(embedding=DashScopeEmbeddings(model=config.embedding_model)).get_retriever()
    res = retriever.invoke("我的体重130斤，尺码推荐")
    print(res)

