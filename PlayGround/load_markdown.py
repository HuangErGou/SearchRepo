from langchain.retrievers import EnsembleRetriever
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_community.retrievers import BM25Retriever

from Embedding.NagasenaEmbeddings import NagasenaEmbeddings

markdown_path = "D:\\test\\minigui_readme.md"

with open(file=markdown_path, encoding="utf-8") as f:
    content = f.read()

headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]

markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
md_header_splits = markdown_splitter.split_text(content)

chunk_size = 250
chunk_overlap = 30
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size, chunk_overlap=chunk_overlap
)

# Split
split = text_splitter.split_documents(md_header_splits)


embeddings = NagasenaEmbeddings()
vectorstore = FAISS.from_documents(split, embeddings)

faiss_retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

bm25_retriever = BM25Retriever.from_documents(split)
bm25_retriever.k = 2

ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, faiss_retriever], weights=[0.5, 0.5]
)

query = "gui can run no vxworks"
docs = ensemble_retriever.invoke(query)


print(docs)