import os
import sys

from Agents.KeywordExtractor import KeywordsGenerateAgent
from Agents.SearchCmdGenerateAgent import SearchCmdGenerateAgent
from LLM.NagasenaLLM import NagasenaLLM
from Retriever.RetrieveRepoDescription import RetrieveRepoDescription


def main():
    if len(sys.argv) < 2:
        print("请描述你想搜索github 仓库")
        sys.exit(-1)

    query = sys.argv[1]

    retriever = RetrieveRepoDescription()
    llm = NagasenaLLM(temperature=0)
    agent = SearchCmdGenerateAgent(llm)
    agent_keywords_generate = KeywordsGenerateAgent(llm)

    keywords = agent_keywords_generate.generate(search_request=query)

    the_command = agent.generate(search_request=query)
    repos = agent.execute_command(the_command)
    repos = repos[:min(1, len(repos))]

    tmp_dir = "D:\\tmp"
    agent.download_readme(repos, tmp_dir)

    result = []
    for repo in repos:
        readme_filename = repo.to_filename()
        readme_path = os.path.join(tmp_dir, readme_filename)
        description = retriever.retrieve(readme_path, query=keywords)
        result.append({"name": repo.name, "description": description})
    print(result)


if __name__ == "__main__":
    main()
