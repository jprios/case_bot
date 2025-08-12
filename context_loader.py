import os
import logging
from typing import List
from langchain_core.documents import Document
from vector_db import indexar_mensagem

# Simula carregadores para cada fonte

def carregar_de_slack() -> List[Document]:
    logging.info("Importando mensagens do Slack...")
    # Simule a chamada de API ou leitura de mensagens
    mensagens = [
        ("Cliente no Slack pergunta sobre antecipação de valores.",
         "O cliente deseja saber se pode receber os valores antes da data prevista.")
    ]
    return [Document(page_content=f"{pergunta}\n{resposta}") for pergunta, resposta in mensagens]

def carregar_de_email() -> List[Document]:
    logging.info("Importando mensagens de Email...")
    mensagens = [
        ("O que acontece em caso de inadimplência do paciente?",
         "Em caso de inadimplência, a Parcela Saúde aciona os mecanismos de cobrança previstos em contrato.")
    ]
    return [Document(page_content=f"{pergunta}\n{resposta}") for pergunta, resposta in mensagens]

def carregar_de_whatsapp() -> List[Document]:
    logging.info("Importando mensagens do WhatsApp...")
    mensagens = [
        ("Qual é o prazo para o repasse à clínica?",
         "O repasse ocorre em até 48h após emissão da nota fiscal.")
    ]
    return [Document(page_content=f"{pergunta}\n{resposta}") for pergunta, resposta in mensagens]

def carregar_do_drive() -> List[Document]:
    logging.info("Importando documentos do Google Drive...")
    mensagens = [
        ("Como é feita a integração com o sistema da clínica?",
         "A integração pode ser feita via API ou planilha automatizada.")
    ]
    return [Document(page_content=f"{pergunta}\n{resposta}") for pergunta, resposta in mensagens]

def carregar_de_arquivos(pasta: str = "contextos") -> List[Document]:
    logging.info(f"Importando arquivos locais da pasta: {pasta}")
    docs = []
    for nome_arquivo in os.listdir(pasta):
        caminho = os.path.join(pasta, nome_arquivo)
        if os.path.isfile(caminho):
            with open(caminho, "r", encoding="utf-8") as f:
                conteudo = f.read()
                docs.append(Document(page_content=conteudo))
    return docs

def importar_contexto_completo():
    todas_fontes = []
    todas_fontes.extend(carregar_de_slack())
    todas_fontes.extend(carregar_de_email())
    todas_fontes.extend(carregar_de_whatsapp())
    todas_fontes.extend(carregar_do_drive())
    todas_fontes.extend(carregar_de_arquivos())

    for doc in todas_fontes:
        pergunta, resposta = doc.page_content.split("\n", 1)
        indexar_mensagem(pergunta.strip(), resposta.strip())
        logging.info(f"Indexada pergunta: {pergunta.strip()}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    importar_contexto_completo()
