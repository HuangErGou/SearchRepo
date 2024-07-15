from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import CharacterTextSplitter, MarkdownTextSplitter
from langchain_community.retrievers import BM25Retriever

from Embedding.NagasenaEmbeddings import NagasenaEmbeddings

markdown_path = "D:\\test\\minigui_readme.md"

loader = UnstructuredMarkdownLoader(markdown_path)
documents = loader.load()


text_splitter = MarkdownTextSplitter()

texts = text_splitter.split_documents(documents)


doc_list_1 = [
    "light weight window manage system"
]
bm25_retriever = BM25Retriever.from_documents(texts)
docs = bm25_retriever.invoke("light weight window manage system")
print(docs)


# print("111111")
# embeddings = NagasenaEmbeddings()
# vectorstore = FAISS.from_documents(texts, embeddings)
#
# retriever = vectorstore.as_retriever()
#
# docs = retriever.invoke("linux window")
# print(docs)
# print(len(docs[0].page_content))
