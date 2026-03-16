from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from config import get_openai_api_key

def build_index(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200
    )

    texts, metas = [], []

    for d in docs:
        for chunk in splitter.split_text(d["content"]):
            texts.append(chunk)
            metas.append({"path": d["path"]})

    api_key = get_openai_api_key()
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is not set. Set it in .env (Payer-agent/.env) or as environment variable."
        )
    embeddings = OpenAIEmbeddings(api_key=api_key)
    return FAISS.from_texts(texts, embeddings, metas)
