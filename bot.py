import os
import json
from collections import Counter
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

# =========================
# CONFIGURAÇÃO
# =========================

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", "10000"))

ARQUIVO = "resultados.json"

app_web = Flask(__name__)

telegram_app = Application.builder().token(TOKEN).build()


# =========================
# BANCO DE DADOS
# =========================

def carregar_resultados():
    if not os.path.exists(ARQUIVO):
        return []

    try:
        with open(ARQUIVO, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except Exception:
        return []


def salvar_resultados():
    with open(ARQUIVO, "w", encoding="utf-8") as arquivo:
        json.dump(
            resultados,
            arquivo,
            ensure_ascii=False,
            indent=2
        )


resultados = carregar_resultados()


# =========================
# /START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    texto = """
🎲 BAC BO ANALYZER

Bem-vindo ao seu bot!

Use os comandos:

/resultado player
/resultado banker
/resultado tie

/estatisticas
/ultimos
/analise

/limpar

O bot registra os resultados e calcula
estatísticas do histórico.

⚠️ A análise não garante o resultado
da próxima rodada.
"""

    await update.message.reply_text(texto)


# =========================
# /AJUDA
# =========================

async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):

    texto = """
📚 COMANDOS

🎲 Registrar:

/resultado player

/resultado banker

/resultado tie


📊 Estatísticas:

/estatisticas


📜 Últimas rodadas:

/ultimos


📈 Análise:

/analise


🗑️ Limpar:

/limpar
"""

    await update.message.reply_text(texto)


# =========================
# REGISTRAR RESULTADO
# =========================

async def resultado(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text(
            "❌ Informe o resultado.\n\n"
            "Exemplo:\n"
            "/resultado player"
        )
        return

    valor = context.args[0].lower()

    if valor not in ["player", "banker", "tie"]:
        await update.message.reply_text(
            "❌ Resultado inválido.\n\n"
            "Use apenas:\n"
            "player\n"
            "banker\n"
            "tie"
        )
        return

    resultados.append(valor)
    salvar_resultados()

    simbolos = {
        "player": "🔵",
        "banker": "🔴",
        "tie": "🟡"
    }

    await update.message.reply_text(
        f"{simbolos[valor]} Resultado registrado: "
        f"{valor.upper()}\n\n"
        f"📊 Total de rodadas: {len(resultados)}"
    )


# =========================
# ESTATÍSTICAS
# =========================

async def estatisticas(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not resultados:
        await update.message.reply_text(
            "❌ Ainda não existem resultados."
        )
        return

    contador = Counter(resultados)
    total = len(resultados)

    player = contador["player"]
    banker = contador["banker"]
    tie = contador["tie"]

    texto = f"""
📊 ESTATÍSTICAS

🎲 Total: {total}

🔵 PLAYER
{player} resultados
{player / total * 100:.1f}%

🔴 BANKER
{banker} resultados
{banker / total * 100:.1f}%

🟡 TIE
{tie} resultados
{tie / total * 100:.1f}%
"""

    await update.message.reply_text(texto)


# =========================
# ÚLTIMOS RESULTADOS
# =========================

async def ultimos(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not resultados:
        await update.message.reply_text(
            "❌ Nenhum resultado registrado."
        )
        return

    dados = resultados[-20:]

    texto = "📜 ÚLTIMAS 20 RODADAS\n\n"

    inicio = len(resultados) - len(dados) + 1

    simbolos = {
        "player": "🔵",
        "banker": "🔴",
        "tie": "🟡"
    }

    for numero, valor in enumerate(dados, start=inicio):

        texto += (
            f"{numero}. "
            f"{simbolos[valor]} "
            f"{valor.upper()}\n"
        )

    await update.message.reply_text(texto)


# =========================
# ANÁLISE
# =========================

async def analise(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not resultados:
        await update.message.reply_text(
            "❌ Ainda não existem dados."
        )
        return

    texto = "📈 ANÁLISE DO HISTÓRICO\n\n"

    for quantidade in [10, 20, 50]:

        dados = resultados[-quantidade:]

        if not dados:
            continue

        contador = Counter(dados)
        total = len(dados)

        texto += f"📊 ÚLTIMAS {total}\n"

        texto += (
            f"🔵 Player: {contador['player']} "
            f"({contador['player']/total*100:.1f}%)\n"
        )

        texto += (
            f"🔴 Banker: {contador['banker']} "
            f"({contador['banker']/total*100:.1f}%)\n"
        )

        texto += (
            f"🟡 Tie: {contador['tie']} "
            f"({contador['tie']/total*100:.1f}%)\n\n"
        )

    # Sequência atual

    atual = resultados[-1]
    sequencia = 0

    for valor in reversed(resultados):

        if valor == atual:
            sequencia += 1
        else:
            break

    texto += (
        f"🔥 Sequência atual: "
        f"{atual.upper()} x{sequencia}\n\n"
    )

    texto += (
        "⚠️ Os dados mostram apenas o histórico. "
        "Não existe garantia de qual será o próximo resultado."
    )

    await update.message.reply_text(texto)


# =========================
# LIMPAR
# =========================

async def limpar(update: Update, context: ContextTypes.DEFAULT_TYPE):

    resultados.clear()
    salvar_resultados()

    await update.message.reply_text(
        "🗑️ Histórico apagado."
    )


# =========================
# WEBHOOK
# =========================

@app_web.route("/", methods=["GET"])
def inicio():

    return "BAC BO BOT ONLINE"


@app_web.route("/webhook", methods=["POST"])
async def webhook():

    dados = request.get_json(force=True)

    update = Update.de_json(
        dados,
        telegram_app.bot
    )

    await telegram_app.process_update(update)

    return "OK"


# =========================
# INICIALIZAÇÃO
# =========================

telegram_app.add_handler(
    CommandHandler("start", start)
)

telegram_app.add_handler(
    CommandHandler("ajuda", ajuda)
)

telegram_app.add_handler(
    CommandHandler("resultado", resultado)
)

telegram_app.add_handler(
    CommandHandler("estatisticas", estatisticas)
)

telegram_app.add_handler(
    CommandHandler("ultimos", ultimos)
)

telegram_app.add_handler(
    CommandHandler("analise", analise)
)

telegram_app.add_handler(
    CommandHandler("limpar", limpar)
)


if __name__ == "__main__":

    import asyncio

    async def iniciar():

        await telegram_app.initialize()
        await telegram_app.start()

        print("🤖 Bot iniciado!")

        await telegram_app.bot.set_webhook(
            url=os.getenv("WEBHOOK_URL")
        )

    asyncio.run(iniciar())

    app_web.run(
        host="0.0.0.0",
        port=PORT
    )
