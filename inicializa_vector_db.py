from vector_db import indexar_mensagem

# Mensagens reais ou fictícias para alimentar a base
mensagens = [
    {
        "pergunta": "Após emitir a nota fiscal, quanto tempo demora para o valor cair na conta da clínica?",
        "resposta": "O repasse é feito em até 48 horas após a emissão da nota fiscal pela clínica."
    },
    {
        "pergunta": "Quais critérios são usados para aprovar o financiamento de um paciente?",
        "resposta": "São analisados score de crédito, profissão, renda declarada e histórico financeiro com base em consultas aos bureaus como Serasa e SPC."
    },
    {
        "pergunta": "Qual o diferencial da Parcela Mais em relação a outros financiamentos?",
        "resposta": "A Parcela Mais oferece integração total com a clínica, repasse rápido, ausência de glosas e taxas reduzidas."
    }
]

for m in mensagens:
    indexar_mensagem(m["pergunta"], m["resposta"])

print("Base vetorial inicializada com exemplos.")
