from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from Embedding.NagasenaEmbeddings import NagasenaEmbeddings


class RetrieveRepoDescription:
    def __init__(self):
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        self.__markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

        chunk_size = 250
        chunk_overlap = 30
        self.__text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.__embeddings = NagasenaEmbeddings()

    def retrieve(self, file_path: str, query: str) -> str:
        with open(file=file_path, encoding="utf-8") as f:
            content = f.read()

        md_header_splits = self.__markdown_splitter.split_text(content)
        text_splits = self.__text_splitter.split_documents(md_header_splits)
        # vectorstore = FAISS.from_documents(text_splits, self.__embeddings)
        bm25_retriever = BM25Retriever.from_documents(text_splits)
        bm25_retriever.k = 4

        # faiss_retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
        # ensemble_retriever = EnsembleRetriever(
        #     retrievers=[bm25_retriever, faiss_retriever], weights=[0.5, 0.5]
        # )
        ensemble_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever], weights=[1]
        )
        docs = ensemble_retriever.invoke(query)
        content = ""
        for doc in docs:
            content = content + doc.page_content + "\n"
        return content
