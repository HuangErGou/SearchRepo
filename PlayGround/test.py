from typing import Type

from langchain import hub
from langchain_core.tools import BaseTool
from pydantic.v1 import BaseModel, Field

from LLM.NagasenaLLM import NagasenaLLM
from langchain.agents import create_openai_tools_agent, AgentExecutor


class SearchInput(BaseModel):
    sentence: str = Field(description="用来搜索的字符串, 字符串需要翻译成英文")


class SearchTool(BaseTool):
    name = "SearchTool"
    description = "github 搜索工具，可以在github 上搜索仓库"
    args_schema: Type[BaseModel] = SearchInput

    def _run(self, sentence: str) -> str:
        """Use the tool."""
        print(f"call function search {sentence}")
        return "没有找到"


prompt = hub.pull("hwchase17/openai-tools-agent")
tools = [SearchTool()]

llm = NagasenaLLM(temperature=0)
agent = create_openai_tools_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

response = agent_executor.invoke(
    {
        "input": "抽取'基于langchain的JIRA附件下载'里面的关键字, 在github上搜索, 如果没有找到"
    }
)
print(response)
print(type(response))
