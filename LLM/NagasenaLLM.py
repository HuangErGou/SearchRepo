from typing import Any

from langchain_openai import ChatOpenAI


class NagasenaLLM(ChatOpenAI):
    __MODEL_NAME = "moonshot-v1-8k"
    __MODEL_URL = "https://api.moonshot.cn/v1/"

    def __init__(self, temperature=0.95):
        super().__init__(model=self.__MODEL_NAME, openai_api_base=self.__MODEL_URL, temperature=temperature)


if __name__ == "__main__":
    llm = NagasenaLLM()
    response = llm.invoke("Hi")
    print(response)
