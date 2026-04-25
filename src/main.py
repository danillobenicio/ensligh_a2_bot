import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from google import genai
from datetime import datetime

requests_today = 0
MAX_REQUESTS = 30  # 🔥 seu limite diário

last_reset = datetime.now().date()

def check_reset():
    global requests_today, last_reset

    today = datetime.now().date()
    if today != last_reset:
        requests_today = 0
        last_reset = today

# Carrega .env
load_dotenv()

# Logs
logging.basicConfig(level=logging.INFO)

# Cliente Gemini (API nova)
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# Função de tradução
async def get_a2_translation(text: str) -> str:
    prompt = (
        f"Translate this sentence to English (A2 level): '{text}'.\n\n"
        "Rules:\n"
        "- Use simple vocabulary\n"
        "- Keep sentences short\n\n"
        "Return EXACTLY in this format:\n"
        "🇺🇸 Present: ...\n"
        "🇺🇸 Past: ...\n"
        "🇺🇸 Future: ..."
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


# Handler do Telegram
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    global requests_today

    # 🔄 reset diário
    check_reset()

    # 🚫 bloqueio antes de gastar API
    if requests_today >= MAX_REQUESTS:
        await update.message.reply_text("⚠️ Limite diário atingido (30 mensagens). Volte amanhã.")
        return

    requests_today += 1  # 👈 conta antes da chamada

    try:
        user_text = update.message.text

        translation = await get_a2_translation(user_text)

        await update.message.reply_text(translation)

    except Exception as e:
        print("ERRO:", e)
        await update.message.reply_text("Erro ao acessar IA 😢")


# Main
def main():
    token = os.getenv("TELEGRAM_TOKEN")

    if not token:
        print("❌ TELEGRAM_TOKEN não encontrado")
        return

    app = Application.builder().token(token).build()

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    print("🚀 Bot rodando...")
    app.run_polling()


if __name__ == "__main__":
    main()