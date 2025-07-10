import logging
import os
import time
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters
)
from interface import LLMInterface
from router import LLMRouter

# Load token
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN não encontrado no .env")

# Logging
logging.basicConfig(level=logging.INFO)

llm = LLMInterface()
router = LLMRouter()

# Sessões ativas
SESSOES_ATIVAS = {}

# Parâmetros de tempo (segundos)
TEMPO_PERGUNTA = 120  # 2 min
TEMPO_FINAL = 60      # 1 min

# Lista de saudações simples que não devem ser processadas
SAUDACOES_INICIAIS = {"oi", "olá", "bom dia", "boa tarde", "boa noite", "hey", "e aí", "oiê", "opa"}

# Mensagem de boas-vindas
async def enviar_boas_vindas(nome, update: Update):
    mensagem = (
        f"Olá, {nome}! 👋\n\n"
        "Eu sou um analista da *Parcela Mais*, especialista em financiamento para procedimentos médicos.\n"
        "Pode perguntar sobre crédito, repasses, contratos ou qualquer dúvida sobre nossa plataforma!\n\n"
        "Como posso te ajudar hoje?"
    )
    await update.message.reply_text(mensagem, parse_mode="Markdown")

# Monitorar inatividade
async def monitorar_inatividade(user_id, chat_id, context: ContextTypes.DEFAULT_TYPE):
    await asyncio.sleep(TEMPO_PERGUNTA)
    if time.time() - SESSOES_ATIVAS.get(user_id, 0) >= TEMPO_PERGUNTA:
        await context.bot.send_message(chat_id=chat_id, text="👋 Você ainda está por aí? Posso te ajudar com mais alguma coisa 😊")
        await asyncio.sleep(TEMPO_FINAL)
        if time.time() - SESSOES_ATIVAS.get(user_id, 0) >= (TEMPO_PERGUNTA + TEMPO_FINAL):
            await context.bot.send_message(chat_id=chat_id, text="💤 Conversa encerrada por inatividade. Quando quiser, é só me chamar novamente! 👋")
            SESSOES_ATIVAS.pop(user_id, None)

# Handler principal
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pergunta = update.message.text.strip().lower()
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    nome = update.effective_user.first_name

    nova_sessao = user_id not in SESSOES_ATIVAS or (time.time() - SESSOES_ATIVAS[user_id]) > (TEMPO_PERGUNTA + TEMPO_FINAL)
    SESSOES_ATIVAS[user_id] = time.time()

    if nova_sessao:
        await enviar_boas_vindas(nome, update)
        # Se a primeira mensagem for uma saudação simples, não prossegue
        if pergunta in SAUDACOES_INICIAIS:
            return

    await update.message.reply_text("🔎 Só um instante enquanto analiso sua pergunta...")

    routing = router.escolher_modelo(pergunta)
    modelo = routing["modelo"]
    resposta = llm.responder(pergunta, modelo)

    await update.message.reply_text(resposta)

    asyncio.create_task(monitorar_inatividade(user_id, chat_id, context))

# Função principal
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot da Parcela Mais iniciado e aguardando mensagens.")
    app.run_polling()

if __name__ == "__main__":
    main()
