import os
from typing import List

from langchain_core.embeddings import Embeddings
from pydantic.v1 import BaseModel
from zhipuai import ZhipuAI


class NagasenaEmbeddings(BaseModel, Embeddings):
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.__get_documents_embeddings(texts)

    def embed_query(self, text: str) -> List[float]:
        return self.__get_query_embeddings(text)

    @staticmethod
    def __get_query_embeddings(text: str) -> List[float]:
        __client = ZhipuAI(api_key=os.environ['ZHIPU_API_KEY'])
        response = __client.embeddings.create(
            model="embedding-2",
            input=text
        )
        return response.data[0].embedding

    @staticmethod
    def __get_documents_embeddings(texts: List[str]) -> List[List[float]]:
        __client = ZhipuAI(api_key=os.environ['ZHIPU_API_KEY'])
        response = __client.embeddings.create(
            model="embedding-2",
            input=texts
        )
        __embeddings = []
        for data in response.data:
            __embeddings.append(data.embedding)
        return __embeddings


if __name__ == '__main__':
    embeddings = NagasenaEmbeddings()
    print(embeddings.embed_query("你好"))
    print(embeddings.embed_documents(["你好", "爸爸"]))
