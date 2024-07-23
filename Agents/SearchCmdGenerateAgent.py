import os

from langchain import hub
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from LLM.NagasenaLLM import NagasenaLLM


class GeneratedCommandInput(BaseModel):
    command: str = Field(description="生成的命令")


class GeneratedCommand(BaseTool):
    name = "GeneratedCommand"
    description = "输出生成的命令"

    def _run(self, command: str):
        print(command)


class SearchCmdGenerateAgent:
    def __init__(self, llm: BaseLanguageModel):
        prompt = hub.pull("hwchase17/openai-tools-agent")
        tools = [GeneratedCommand()]

        self.__llm = llm
        self.__agent = create_openai_tools_agent(llm=self.__llm, tools=tools, prompt=prompt)
        self.__agent_executor = AgentExecutor(agent=self.__agent, tools=tools, verbose=True)

    @staticmethod
    def __get_search_sample():
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        sample_path = os.path.join(parent_dir, "res", "SearchSample.txt")
        with open(sample_path, "r", encoding="utf-8") as file:
            content = file.read()
        return content

    def generate(self, search_request: str) -> str:
        input_prompt = (f"你是一个github 搜索助手，下面是github client命令行搜索范例\n"
                        f"{SearchCmdGenerateAgent.__get_search_sample()} \n"
                        f"请参考范例，生成 \"{search_request}\"的搜索指令，并调用接口输出")
        self.__agent_executor.invoke(
            {
                "input": input_prompt
            }
        )
        return ""


if __name__ == "__main__":
    llm = NagasenaLLM(temperature=0)
    agent = SearchCmdGenerateAgent(llm)
    agent.generate(search_request="C++开发的响应式编程的仓库")





