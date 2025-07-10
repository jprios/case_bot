import os
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

_DB_PATH = "db_faiss"
_embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def carregar_db():
    if os.path.exists(_DB_PATH):
        return FAISS.load_local(_DB_PATH, _embeddings, allow_dangerous_deserialization=True)
    else:
        from langchain_core.documents import Document
        doc_ficticio = Document(page_content="mensagem inicial temporária")
        db = FAISS.from_documents([doc_ficticio], _embeddings)
        db.save_local(_DB_PATH)
        return db


def salvar_db(db):
    db.save_local(_DB_PATH)

def indexar_mensagem(pergunta: str, resposta: str):
    doc = Document(page_content=f"PERGUNTA: {pergunta}\nRESPOSTA: {resposta}")
    db = carregar_db()
    db.add_documents([doc])
    salvar_db(db)

def buscar_contexto(pergunta: str, k: int = 3):
    db = carregar_db()
    docs = db.similarity_search(pergunta, k=k)
    return "\n---\n".join(d.page_content for d in docs)
