import logging
import time
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from vector_db import buscar_contexto, indexar_mensagem



class LLMInterface:
    def responder(self, pergunta: str, modelo: str) -> str:
        logger = logging.getLogger(__name__)
        logger.info(f"Pergunta recebida: {pergunta}")
        logger.info(f"Modelo selecionado: {modelo}")

        model_map = {
            "openai_gpt4": ("gpt-4-turbo", "openai"),
            "openai_gpt3.5": ("gpt-3.5-turbo", "openai"),
            "claude_3_opus": ("claude-3-opus-20240229", "anthropic"),
            "llama3_70b": ("meta-llama/llama-3-70b-instruct", "openrouter"),
            "mistral_7b_instruct": ("mistral-small-latest", "mistralai")
        }

        fallback_modelo = "mistral_7b_instruct"

        if modelo not in model_map:
            return f"Modelo '{modelo}' não reconhecido."

        nome_modelo, provider = model_map[modelo]
        fallback_nome, fallback_provider = model_map[fallback_modelo]

        mensagem_sistema = SystemMessage(
            content="""\
Você é um agente da Parcela Saúde, uma health-fintech especializada em financiamento para procedimentos médicos. Sua missão é atuar como analista especializado, respondendo às perguntas com base em um profundo conhecimento sobre o funcionamento da empresa, as regras do financiamento, o processo de crédito e os benefícios tanto para clínicas quanto para pacientes.

Seu tom deve ser empático, informativo e profissional, priorizando sempre a clareza e a confiança. Suas respostas devem considerar o seguinte contexto:

- A Parcela Case permite que clínicas ofereçam financiamento direto a seus pacientes, com análise de crédito instantânea e pagamento em até 48 horas após a emissão da nota fiscal.
- O crédito é aprovado com base em score, renda, profissão e histórico do paciente, com consulta a bureaus como Serasa, SPC e Boa Vista.
- Os principais diferenciais são: preservação do fluxo de caixa da clínica, ausência de glosas, taxas reduzidas e integração fluida ao processo da clínica.
- As especialidades mais atendidas são cirurgia plástica, odontologia, oftalmologia e cirurgia bariátrica, mas qualquer área da saúde pode se beneficiar.
- A fintech atua como facilitadora entre clínicas e instituições financeiras, oferecendo uma plataforma white-label e 100% online.
- Caso você não saiba uma resposta, apenas diga que não pode ajudar com a pergunta. Não tente inferir uma resposta.

Nunca diga que está gerando texto, nem que é uma IA. Posicione-se sempre como um analista da Parcela Saúde, disponível para esclarecer dúvidas com autoridade e simpatia."""
        )
        contexto_previo = buscar_contexto(pergunta)
        if contexto_previo:
            logger.info("Contexto semântico encontrado e adicionado à mensagem do sistema.")
            mensagem_sistema = SystemMessage(
                content=mensagem_sistema.content + "\n\nContexto anterior:\n" + contexto_previo
            )
        mensagens = [mensagem_sistema, HumanMessage(content=pergunta)]
        def tentar_modelo(nome_modelo, provider):
            ultimo_erro = None
            for tentativa in range(5):
                try:
                    llm = init_chat_model(nome_modelo, model_provider=provider)
                    resposta = llm.invoke(mensagens)
                    return resposta.content.strip(), None
                except Exception as ex:
                    ultimo_erro = ex
                    logger.warning(f"Tentativa {tentativa+1}/5 falhou para {nome_modelo}. Aguardando {2**tentativa} segundos...")
                    time.sleep(2**tentativa)
            return None, ultimo_erro

        # Tentar modelo principal
        resposta, erro = tentar_modelo(nome_modelo, provider)
        if resposta:
            indexar_mensagem(pergunta, resposta)
            return resposta

        logger.error(f"Erro ao usar o modelo '{modelo}': {str(erro)}")
        logger.warning(f"Utilizando fallback: {fallback_modelo}")

        # Tentar fallback
        resposta, erro = tentar_modelo(fallback_nome, fallback_provider)
        if resposta:
            indexar_mensagem(pergunta, resposta)
            return resposta

        logger.critical(f"Erro também no fallback: {str(erro)}")
        return f"Erro em ambos os modelos. Detalhes: {str(erro)}"
