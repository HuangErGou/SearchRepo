import os
import shlex
import subprocess
from typing import List

from langchain import hub
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from LLM.NagasenaLLM import NagasenaLLM

gb_command = ""


class GithubSearchItem:
    def __init__(self, name: str, description: str, visibility: str, update: str):
        self.name = name
        self.description = description
        self.visibility = visibility
        self.update = update

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'visibility': self.visibility,
            'update': self.update
        }

    def __str__(self):
        return (f"GithubSearchItem(name={self.name!r}, "
                f"description={self.description!r}, "
                f"visibility={self.visibility!r}, "
                f"update={self.update!r})")

    def __repr__(self):
        return (f"GithubSearchItem(name={self.name!r}, "
                f"description={self.description!r}, "
                f"visibility={self.visibility!r}, "
                f"update={self.update!r})")


class GeneratedCommandInput(BaseModel):
    command: str = Field(description="生成的命令")


class GeneratedCommand(BaseTool):
    name = "GeneratedCommand"
    description = "输出生成的命令"

    def _run(self, command: str):
        print(command)
        global gb_command
        gb_command = command


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

    @staticmethod
    def download_readme(repos: List[GithubSearchItem], store_dir: str):
        command_template = "gh repo view {repo_name}"

        for repo in repos:
            try:
                command = command_template.format(repo_name=repo.name)
                result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        text=True, encoding='utf-8', errors='ignore')

                # 检查命令是否执行成功
                if result.returncode == 0:
                    # 将输出保存到文件
                    readme_filename = repo.name
                    readme_filename = readme_filename.replace("/", "_") + ".md"
                    readme_path = os.path.join(store_dir, readme_filename)
                    with open(readme_path, 'w', encoding="utf-8", errors="ignore") as file:
                        file.write(result.stdout)
                    print(f"命令执行成功，输出已保存到{readme_path}")
                else:
                    # 打印错误信息
                    print(f"命令执行失败，错误信息: {result.stderr}")
            except subprocess.CalledProcessError as e:
                print(f"命令执行过程中发生错误: {e}")
            pass
        pass

    @staticmethod
    def execute_command(command_str: str) -> List[GithubSearchItem]:
        items = []

        command = shlex.split(command_str)

        # 现在command是一个列表，包含了命令和参数
        print(command)
        # 使用subprocess.run()执行命令
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True, errors="ignore")
            output = result.stdout

            lines = output.strip().split('\n')
            for line in lines:
                if line.strip():
                    parts = line.split("\t")
                    if len(parts) == 4:
                        name = parts[0].strip()
                        description = parts[1].strip()
                        visibility = parts[2].strip()
                        updated = parts[3].strip()

                        items.append(
                            GithubSearchItem(
                                name=name,
                                description=description,
                                visibility=visibility,
                                update=updated))
            return items
        except subprocess.CalledProcessError as e:

            print("An error occurred while executing the command.")
            print(e)

    def generate(self, search_request: str) -> str:
        global gb_command
        gb_command = ""

        input_prompt = (f"你是一个github 搜索助手，下面是github client命令行搜索范例\n"
                        f"{SearchCmdGenerateAgent.__get_search_sample()} \n"
                        f"请参考范例，生成 \"{search_request}\"的搜索指令，并调用接口输出")
        self.__agent_executor.invoke(
            {
                "input": input_prompt
            }
        )
        return gb_command


if __name__ == "__main__":
    llm = NagasenaLLM(temperature=0)
    agent = SearchCmdGenerateAgent(llm)
    the_command = agent.generate(search_request="rust开发的的响应式的编程框架的仓库")
    repos = agent.execute_command(the_command)
    agent.download_readme(repos, "D:\\tmp")
    print(repos)
