import os
import json
from collections import Counter

from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", "10000"))

ARQUIVO = "resultados.json"

if not TOKEN:
   raise RuntimeError("BOT_TOKEN não foi configurado.")

app_web = Flask(__name__)

telegram_app = Application.builder().token(TOKEN).build()

def carregar_resultados():
  if not os.path.exists(ARQUIVO):
    return []

```
try:
    with open(ARQUIVO, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)
except Exception:
    return []
```

def salvar_resultados():
with open(ARQUIVO, "w", encoding="utf-8") as arquivo:
json.dump(
resultados,
arquivo,
ensure_ascii=False,
indent=2
)

resultados = carregar_resultados()

async def start(update: Update, context):
texto = """
🎲 BAC BO ANALYZER

Bem-vindo ao seu bot!

Comandos:

/resultado player
/resultado banker
/resultado tie

/estatisticas
/ultimos
/analise
/limpar

⚠️ A análise mostra apenas o histórico
e não garante o próximo resultado.
"""

```
await update.message.reply_text(texto)
```

async def ajuda(update: Update, context):
texto = """
📚 COMANDOS

/resultado player
/resultado banker
/resultado tie

/estatisticas
/ultimos
/analise
/limpar
"""

```
await update.message.reply_text(texto)
```

async def resultado(update: Update, context):
if not context.args:
await update.message.reply_text(
"❌ Informe player, banker ou tie.\n\n"
"Exemplo:\n"
"/resultado player"
)
return

```
valor = context.args[0].lower()

if valor not in ["player", "banker", "tie"]:
    await update.message.reply_text(
        "❌ Resultado inválido.\n\n"
        "Use player, banker ou tie."
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
    f"📊 Total: {len(resultados)}"
)
```

async def estatisticas(update: Update, context):
if not resultados:
await update.message.reply_text(
"❌ Ainda não existem resultados."
)
return

```
contador = Counter(resultados)
total = len(resultados)

texto = f"""
```

📊 ESTATÍSTICAS

🎲 Total: {total}

🔵 PLAYER
{contador["player"]} ({contador["player"] / total * 100:.1f}%)

🔴 BANKER
{contador["banker"]} ({contador["banker"] / total * 100:.1f}%)

🟡 TIE
{contador["tie"]} ({contador["tie"] / total * 100:.1f}%)
"""

```
await update.message.reply_text(texto)
```

async def ultimos(update: Update, context):
if not resultados:
await update.message.reply_text(
"❌ Nenhum resultado registrado."
)
return

```
dados = resultados[-20:]

simbolos = {
    "player": "🔵",
    "banker": "🔴",
    "tie": "🟡"
}

texto = "📜 ÚLTIMAS RODADAS\n\n"

inicio = len(resultados) - len(dados) + 1

for numero, valor in enumerate(dados, start=inicio):
    texto += (
        f"{numero}. "
        f"{simbolos[valor]} "
        f"{valor.upper()}\n"
    )

await update.message.reply_text(texto)
```

async def analise(update: Update, context):
if not resultados:
await update.message.reply_text(
"❌ Ainda não existem dados."
)
return

```
contador = Counter(resultados)
total = len(resultados)

atual = resultados[-1]
sequencia = 0

for valor in reversed(resultados):
    if valor == atual:
        sequencia += 1
    else:
        break

texto = f"""
```

📈 ANÁLISE DO HISTÓRICO

🔵 Player: {contador["player"]} ({contador["player"] / total * 100:.1f}%)
🔴 Banker: {contador["banker"]} ({contador["banker"] / total * 100:.1f}%)
🟡 Tie: {contador["tie"]} ({contador["tie"] / total * 100:.1f}%)

🔥 Sequência atual:
{atual.upper()} x{sequencia}

⚠️ Os dados representam apenas o histórico
e não garantem o próximo resultado.
"""

```
await update.message.reply_text(texto)
```

async def limpar(update: Update, context):
resultados.clear()
salvar_resultados()

```
await update.message.reply_text(
    "🗑️ Histórico apagado."
)
```

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

@app_web.route("/", methods=["GET"])
def inicio():
return "BAC BO BOT ONLINE"

@app_web.route("/health", methods=["GET"])
def health():
return "OK"

@app_web.route("/webhook", methods=["POST"])
async def webhook():
dados = request.get_json(force=True)

```
update = Update.de_json(
    dados,
    telegram_app.bot
)

await telegram_app.process_update(update)

return "OK"
```

if **name** == "**main**":
app_web.run(
host="0.0.0.0",
port=PORT
)
