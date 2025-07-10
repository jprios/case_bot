# router.py

import re
import logging
from typing import Literal, Dict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("router.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LLMRouter:
    """
    Roteador inteligente para escolher o melhor modelo com base na pergunta.
    """

    def __init__(self, policy: Literal["balanced", "low_cost"] = "balanced"):
        self.policy = policy
        self.modelos_disponiveis = {
            "openai_gpt4": {"custo": 0.03, "latencia": 3.0, "forca": "raciocinio"},
            "openai_gpt3.5": {"custo": 0.01, "latencia": 2.0, "forca": "raciocinio/custo"},
            "claude_3_opus": {"custo": 0.04, "latencia": 3.0, "forca": "contexto extenso"},
            "llama3_70b": {"custo": 0.00, "latencia": 1.5, "forca": "respostas curtas e objetivas"},
            "mistral_7b_instruct": {"custo": 0.00, "latencia": 1.0, "forca": "respostas curtas e fallback"}
        }

        self.classificador = {
            "simples": r"(cadastrar|login|cadastro|parceira|contato|telefone|site|email)",
            "financeira": r"(nota\s+fiscal|repasse|valor|pagamento|pix|transferência|antecipação|inadimplência|saldo|limite)",
            "técnica": r"(webhook|API|token|sistema|xano|dashboard|integração|formulário|backoffice|json)",
            "jurídica": r"(contrato|termo|jurídico|assinatura|validade legal|compliance)",
            "emocional": r"(sonhos|ajudar|impacto|missão|sorrisos|pacientes|mudança|história)",
        }

    def classificar_pergunta(self, pergunta: str) -> str:
        pergunta = pergunta.lower()
        for tipo, padrao in self.classificador.items():
            if re.search(padrao, pergunta):
                logger.info(f"Pergunta classificada como: {tipo}")
                return tipo
        logger.info("Pergunta classificada como: geral")
        return "geral"

    def escolher_modelo(self, pergunta: str) -> Dict[str, str]:
        tipo = self.classificar_pergunta(pergunta)

        if self.policy == "low_cost":
            logger.info("Política: baixo custo — retornando Mistral.")
            return {"modelo": "mistral_7b_instruct", "motivo": "política de baixo custo"}

        # Política balanceada
        if tipo == "técnica":
            return {"modelo": "openai_gpt3.5", "motivo": "bom para lógica técnica e custo razoável"}
        elif tipo == "financeira":
            return {"modelo": "openai_gpt4", "motivo": "excelente para contexto financeiro detalhado"}
        elif tipo == "jurídica":
            return {"modelo": "claude_3_opus", "motivo": "forte em compreensão de linguagem legal"}
        elif tipo == "emocional":
            return {"modelo": "llama3_70b", "motivo": "bom tom para empatia e impacto emocional"}
        elif tipo == "simples":
            return {"modelo": "llama3_70b", "motivo": "resposta objetiva e rápida"}
        else:
            return {"modelo": "openai_gpt3.5", "motivo": "modelo versátil e confiável"}
