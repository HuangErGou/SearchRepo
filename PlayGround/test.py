from typing import Type, List, Dict

from langchain import hub
from langchain_core.tools import BaseTool
from pydantic.v1 import BaseModel, Field

from LLM.NagasenaLLM import NagasenaLLM
from langchain.agents import create_openai_tools_agent, AgentExecutor

import shlex
import subprocess


def execute_command(command_str: str) -> str:
    # 使用shlex.split()分割命令字符串
    command = shlex.split(command_str)

    # 现在command是一个列表，包含了命令和参数
    print(command)
    # 使用subprocess.run()执行命令
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, errors="ignore")
        output = result.stdout
        print("Command output:")
        print(output)
        return output
    except subprocess.CalledProcessError as e:
        print("An error occurred while executing the command.")
        print(e)


class SearchInput(BaseModel):
    command: str = Field(description="生成的搜索命令")


class SearchTool(BaseTool):
    name = "SearchTool"
    description = "命令执行工具，可以执行命令"
    args_schema: Type[BaseModel] = SearchInput

    def _run(self, command: str) -> str:
        """Use the tool."""
        print(f"call function search {command}")
        return execute_command(command)


class SummaryInput(BaseModel):
    repo: List[str] = Field(description="仓库的名字列表")


class GetSummaryTool(BaseTool):
    name = "GetSummaryTool"
    description = "读取github 仓库摘要"
    args_schema: Type[BaseModel] = SummaryInput

    def _run(self, repo: List[str]) -> Dict[str, str]:
        """Use the tool."""
        print(f"call function summary {repo}")
        the_first = True
        rtn = {}
        for word in repo:
            if the_first:
                rtn[word] = "用langchain实现了界面画图的功能"
                the_first = False
            else:
                rtn[word] = "这是一个用c++实现的USB协议"
        return rtn


prompt = hub.pull("hwchase17/openai-tools-agent")
tools = [SearchTool(), GetSummaryTool()]

llm = NagasenaLLM(temperature=0)
agent = create_openai_tools_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

search_input = "langchain gui"
prompt = f"github client 搜索仓库的例子如下：\n \
          \\# search repositories matching set of keywords \"cli\" and \"shell\" \n \
          $ gh search repos cli shell \n \
          # search repositories matching phrase \"vim plugin\" \n \
          $ gh search repos \"vim plugin\"\n \" \
          请参考这些例子生成搜索命令，调用命令执行工具去找{search_input}相关的仓库, 调用工具读取仓库的摘要, 然后给出判断那个仓库最符合搜索要求"

response = agent_executor.invoke(
    {
        "input": prompt
    }
)
print(response)
print(type(response))
