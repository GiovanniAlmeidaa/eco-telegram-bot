import logging
import os
import random
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)


load_dotenv()

BOT_TOKEN      = os.getenv("BOT_TOKEN")
DOLAR_API      = os.getenv("DOLAR_API")
CLIMA_API_KEY  = os.getenv("CLIMA_API_KEY")
GIF_API        = os.getenv("GIF_API")
NEWS_API       = os.getenv("NEWS_API")

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Olá, eu sou a Eco, seu bot de informações! Use /ajuda para saber mais."
    )

async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "🌿 *Comandos disponíveis:*\n\n"
        "/start – Apresentação\n"
        "/ajuda – Lista de comandos\n"
        "/dolar – Cotação do dólar\n"
        "/clima <cidade> – Clima atual\n"
        "/moeda <qtd> <origem> <destino>\n"
        "/piada – Piada aleatória\n"
        "/frase – Frase motivacional\n"
        "/gif <tema> – GIF por tema\n"
        "/noticias <tema> – Últimas notícias\n"
        "/sorteio … – Sorteia número ou nome\n"
    )
    await update.message.reply_text(texto, parse_mode="Markdown")

def price_dolar() -> float:
    url = f"https://economia.awesomeapi.com.br/json/last/USD-BRL?token={DOLAR_API}"
    return float(requests.get(url, timeout=10).json()["USDBRL"]["bid"])

async def dolar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Cotação do dólar: R$ {price_dolar():.2f}")

async def moeda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 3:
        await update.message.reply_text(
            "Use: /moeda <quantia> <origem> <destino>\nEx: /moeda 100 USD BRL"
        )
        return
    try:
        qtd = float(context.args[0].replace(",", "."))
        orig, dest = context.args[1].upper(), context.args[2].upper()
    except ValueError:
        await update.message.reply_text("Quantia inválida.")
        return

    url = f"https://economia.awesomeapi.com.br/json/last/{orig}-{dest}"
    data = requests.get(url, timeout=10).json()
    key = f"{orig}{dest}"
    if key not in data:
        await update.message.reply_text("Par de moedas inválido.")
        return

    cotacao = float(data[key]["bid"])
    await update.message.reply_text(f"{qtd} {orig} = {qtd*cotacao:.2f} {dest}")

def clima_emoji(desc: str) -> str:
    d = desc.lower()
    if "nublado" in d or "nuvens" in d: return "☁️"
    if "chuva" in d:                     return "🌧️"
    if "limpo" in d or "sol" in d:       return "☀️"
    if "neve" in d:                      return "❄️"
    if "tempest" in d:                   return "⛈️"
    return "🌡️"

def get_clima(city: str) -> str | None:
    url = (
        "http://api.weatherapi.com/v1/current.json"
        f"?key={CLIMA_API_KEY}&q={city}&lang=pt"
    )
    data = requests.get(url, timeout=10).json()
    if "error" in data:
        return None
    temp = data["current"]["temp_c"]
    desc = data["current"]["condition"]["text"]
    return f"{clima_emoji(desc)} Clima em {city.title()}: {desc}, {temp:.1f}°C"

async def clima(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Ex.: /clima Rio de Janeiro")
        return
    resp = get_clima(" ".join(context.args))
    await update.message.reply_text(resp or "❌ Cidade não encontrada.")

async def piada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://official-joke-api.appspot.com/random_joke"
    data = requests.get(url, timeout=10).json()
    await update.message.reply_text(f"{data['setup']}\n\n{data['punchline']}")

frases = [
    "Acredite em si mesmo!",
    "Sucesso é a soma de pequenos esforços diários.",
    "Não pare até se orgulhar.",
    "Faça o que ama.",
    "Cada dia é uma oportunidade.",
]
async def frase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(frases))

async def sorteio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Use: /sorteio <n1> <n2>  ou  /sorteio nome1 nome2 …")
        return
    if len(context.args) == 2 and all(a.isdigit() for a in context.args):
        a, b = sorted(map(int, context.args))
        await update.message.reply_text(f"Número sorteado: {random.randint(a, b)}")
    else:
        await update.message.reply_text(f"Sorteado: {random.choice(context.args)}")

async def gif(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Use: /gif <tema>")
        return
    termo = "+".join(context.args)
    url   = f"https://api.giphy.com/v1/gifs/search?api_key={GIF_API}&q={termo}&limit=1&rating=g"
    data  = requests.get(url, timeout=10).json()
    if data["data"]:
        await update.message.reply_animation(data["data"][0]["images"]["original"]["url"])
    else:
        await update.message.reply_text("Nenhum GIF encontrado.")

async def noticias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Use: /noticias <tema>")
        return
    tema = "+".join(context.args)
    url  = (
        "https://newsapi.org/v2/everything"
        f"?q={tema}&apiKey={NEWS_API}&language=pt&sortBy=publishedAt&pageSize=3"
    )
    data = requests.get(url, timeout=10).json()
    if data.get("status") == "ok" and data["articles"]:
        msg = "\n\n".join(f"• {a['title']}\n{a['url']}" for a in data["articles"])
        await update.message.reply_text(msg)
    else:
        await update.message.reply_text("Não encontrei notícias.")


def create_application() -> Application:
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    commands = {
        "start": start, "ajuda": ajuda, "dolar": dolar, "moeda": moeda,
        "clima": clima, "piada": piada, "frase": frase,
        "sorteio": sorteio, "gif": gif, "noticias": noticias,
    }
    for cmd, fn in commands.items():
        app.add_handler(CommandHandler(cmd, fn))
    return app


def main() -> None:
    application = create_application()
    logging.info("✅ EcoBot polling iniciado")
    application.run_polling()

if __name__ == "__main__":
    main()
