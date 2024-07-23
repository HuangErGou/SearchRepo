import os
import subprocess
import sys

from Agents.KeywordExtractor import KeywordsGenerateAgent
from Agents.ResultCheckAgent import ResultCheckAgent
from Agents.SearchCmdGenerateAgent import SearchCmdGenerateAgent
from LLM.NagasenaLLM import NagasenaLLM
from Retriever.RetrieveRepoDescription import RetrieveRepoDescription


def run_gh_command(repo_name):
    # 定义要执行的命令
    command_list = ["gh", "repo", "view", f"{repo_name}", "--web"]

    # 执行命令
    try:
        subprocess.run(command_list, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
        print("命令执行失败，错误信息如下：")
        print(e.stderr)


def main():
    if len(sys.argv) < 2:
        print("请描述你想搜索github 仓库")
        sys.exit(-1)

    query = sys.argv[1]

    retriever = RetrieveRepoDescription()
    llm = NagasenaLLM(temperature=0)

    result_check_agent = ResultCheckAgent(llm)
    agent = SearchCmdGenerateAgent(llm)
    agent_keywords_generate = KeywordsGenerateAgent(llm)

    keywords = agent_keywords_generate.generate(search_request=query)

    the_command = agent.generate(search_request=query)
    repos = agent.execute_command(the_command)
    repos = repos[:min(5, len(repos))]

    tmp_dir = "D:\\tmp"
    agent.download_readme(repos, tmp_dir)

    result = []
    for repo in repos:
        readme_filename = repo.to_filename()
        readme_path = os.path.join(tmp_dir, readme_filename)
        description = retriever.retrieve(readme_path, query=keywords)
        result.append({"name": repo.name, "description": description})

        if result_check_agent.generate(search_request=keywords, result=description):
            break
        result.clear()
    print(result)
    if len(result) != 0:
        run_gh_command(result[0].get("name"))
    else:
        print("no related repo")


if __name__ == "__main__":
    main()
