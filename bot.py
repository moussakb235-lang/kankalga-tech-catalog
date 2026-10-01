import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 KANKALGA TECH BOT\n\n"
        "Bienvenue !\n"
        "Le bot est connecté avec succès. ✅"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📱 Commandes disponibles :\n\n"
        "/start — Démarrer le bot\n"
        "/help — Afficher l'aide"
    )


def main():
    if not TOKEN:
        print("❌ Token Telegram introuvable.")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    print("🤖 KANKALGA TECH BOT démarré...")
    app.run_polling()


if __name__ == "__main__":
    main()
