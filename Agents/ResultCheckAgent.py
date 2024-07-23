from typing import Type

from langchain import hub
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.language_models import BaseLanguageModel
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

from LLM.NagasenaLLM import NagasenaLLM


class ResultCheckInput(BaseModel):
    is_match: bool = Field(description="是否匹配")


gb_is_match = False


class ResultCheck(BaseTool):
    name = "ResultCheck"
    description = "输出匹配检查结果"
    args_schema: Type[BaseModel] = ResultCheckInput

    def _run(self, is_match: bool):
        global gb_is_match
        print(is_match)
        gb_is_match = is_match


class ResultCheckAgent:
    def __init__(self, llm: BaseLanguageModel):
        prompt = hub.pull("hwchase17/openai-tools-agent")
        tools = [ResultCheck()]

        self.__llm = llm
        self.__agent = create_openai_tools_agent(llm=self.__llm, tools=tools, prompt=prompt)
        self.__agent_executor = AgentExecutor(agent=self.__agent, tools=tools, verbose=True)

    def generate(self, search_request: str, result: str) -> bool:
        global gb_is_match
        gb_is_match = False

        input_prompt = (f"你是一个搜索请求和搜索结果检查器，"
                        f"你会根据搜索关键字和找到的内容做比对，判断搜索结果是否满足搜索请求,"
                        f"现在有搜索请求\" {search_request} \" 和 搜索结果 \" {result} \" 判断搜索结果是否匹配搜索请求，调用接口输出结果")
        self.__agent_executor.invoke(
            {
                "input": input_prompt
            }
        )
        return gb_is_match


if __name__ == "__main__":
    _llm = NagasenaLLM(temperature=0)
    agent = ResultCheckAgent(_llm)
    _is_match = agent.generate(search_request="X11 GUI framework", result="可以在linux 平台上对接X11的GUI软件")
    print(_is_match)
