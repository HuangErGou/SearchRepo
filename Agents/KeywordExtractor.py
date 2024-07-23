from typing import List, Type

from langchain import hub
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.language_models import BaseLanguageModel
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

from LLM.NagasenaLLM import NagasenaLLM


class GeneratedKeywordsInput(BaseModel):
    keywords: str = Field(description="关键字")


gb_keywords = ""


class GeneratedKeywords(BaseTool):
    name = "GeneratedKeywords"
    description = "输出生成的关键字列表"
    args_schema: Type[BaseModel] = GeneratedKeywordsInput

    def _run(self, keywords: str):
        global gb_keywords
        gb_keywords = keywords
        print(keywords)


class KeywordsGenerateAgent:
    def __init__(self, llm: BaseLanguageModel):
        prompt = hub.pull("hwchase17/openai-tools-agent")
        tools = [GeneratedKeywords()]

        self.__llm = llm
        self.__agent = create_openai_tools_agent(llm=self.__llm, tools=tools, prompt=prompt)
        self.__agent_executor = AgentExecutor(agent=self.__agent, tools=tools, verbose=True)

    def generate(self, search_request: str) -> str:
        global gb_keywords
        gb_keywords = ""
        input_prompt = (f"你是一个github搜索关键词提取器，"
                        f"第一步翻译 \"{search_request}\" 成英文,"
                        f"第二部从翻译后的文字中抽取关键字，关键词用空格隔开，调用接口输出关键词")
        self.__agent_executor.invoke(
            {
                "input": input_prompt
            }
        )
        if len(gb_keywords) == 0:
            gb_keywords = search_request
        return gb_keywords


if __name__ == "__main__":
    _llm = NagasenaLLM(temperature=0)
    agent = KeywordsGenerateAgent(_llm)
    _keywords = agent.generate(search_request="rust开发的的响应式的编程框架的仓库")
    print(_keywords)
