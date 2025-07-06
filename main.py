# main.py
import os
import threading
from flask import Flask
import bot  # importa o bot.py que você acabou de atualizar

app = Flask(__name__)

@app.route("/")
def home():
    return "EcoBot rodando!", 200

def start_bot():
    """
    Inicia o bot Telegram em uma thread separada.
    bot.main() já cria o Application e chama run_polling().
    """
    bot.main()

if __name__ == "__main__":
    # Thread para o bot
    threading.Thread(target=start_bot, daemon=True).start()

    # Porta que o Render expõe (vem em $PORT). Use 3000 como fallback local.
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
