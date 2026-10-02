import os
import json
import base64
import urllib.request
import urllib.error

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "kalgakouraogo-max/kankalga-tech-catalog"
GITHUB_FILE = "servers.json"

PROTOCOL, LOCATION, DURATION, QUOTA, SERVER = range(5)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 KANKALGA TECH BOT\n\n"
        "Bienvenue ! ✅\n\n"
        "Commande disponible :\n"
        "/ajouter_serveur — Ajouter un serveur"
    )


async def ajouter_serveur(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        "🌐 Ajout d'un serveur\n\n"
        "Quel est le protocole ?\n\n"
        "Exemples : VMESS, VLESS, TROJAN, "
        "SHADOWSOCKS, WIREGUARD, SSH"
    )

    return PROTOCOL


async def recevoir_protocole(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["protocol"] = update.message.text.strip()

    await update.message.reply_text(
        "📍 Quelle est la localisation du serveur ?\n\n"
        "Exemple : France"
    )

    return LOCATION


async def recevoir_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["location"] = update.message.text.strip()

    await update.message.reply_text(
        "⏳ Quelle est la durée du serveur ?\n\n"
        "Exemple : 30 jours"
    )

    return DURATION


async def recevoir_duree(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["duration"] = update.message.text.strip()

    await update.message.reply_text(
        "📊 Quel est le quota ?\n\n"
        "Exemple : 100 GB"
    )

    return QUOTA


async def recevoir_quota(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["quota"] = update.message.text.strip()

    await update.message.reply_text(
        "🔗 Maintenant, envoie le serveur complet.\n\n"
        "Exemple :\n"
        "vmess://...\n\n"
        "⚠️ Envoie l'URI/configuration directement."
    )

    return SERVER


async def recevoir_serveur(update: Update, context: ContextTypes.DEFAULT_TYPE):
    server = update.message.text.strip()
    protocol = context.user_data["protocol"].lower()

    if "://" not in server:
        await update.message.reply_text(
            "❌ Format invalide.\n\n"
            "Le serveur doit commencer par une URI, "
            "par exemple vmess:// ou vless://"
        )
        return SERVER

    server_protocol = server.split("://", 1)[0].lower()

    if server_protocol != protocol:
        await update.message.reply_text(
            f"❌ Le protocole ne correspond pas.\n\n"
            f"Protocole indiqué : {protocol}\n"
            f"Protocole du serveur : {server_protocol}\n\n"
            "Envoie le bon serveur."
        )
        return SERVER

    new_server = {
        "protocol": context.user_data["protocol"],
        "location": context.user_data["location"],
        "duration": context.user_data["duration"],
        "quota": context.user_data["quota"],
        "server": server,
    }

    try:
        save_to_github(new_server)

        await update.message.reply_text(
            "✅ SERVEUR AJOUTÉ !\n\n"
            f"🌐 Protocole : {new_server['protocol']}\n"
            f"📍 Localisation : {new_server['location']}\n"
            f"⏳ Durée : {new_server['duration']}\n"
            f"📊 Quota : {new_server['quota']}\n\n"
            "💾 Serveur enregistré sur GitHub."
        )

    except Exception as e:
        print("Erreur GitHub :", e)

        await update.message.reply_text(
            "❌ Impossible d'enregistrer le serveur sur GitHub.\n\n"
            "Vérifie la configuration du bot."
        )

    context.user_data.clear()
    return ConversationHandler.END


def save_to_github(new_server):
    url = (
        f"https://api.github.com/repos/"
        f"{GITHUB_REPO}/contents/{GITHUB_FILE}"
    )

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    request = urllib.request.Request(
        url,
        headers=headers,
        method="GET",
    )

    with urllib.request.urlopen(request) as response:
        data = json.loads(response.read().decode())

    content = base64.b64decode(data["content"]).decode("utf-8")
    file_data = json.loads(content)

    file_data.setdefault("servers", [])
    file_data["servers"].append(new_server)

    new_content = json.dumps(
        file_data,
        ensure_ascii=False,
        indent=2,
    )

    encoded_content = base64.b64encode(
        new_content.encode("utf-8")
    ).decode("utf-8")

    update_data = json.dumps({
        "message": "Ajouter un serveur",
        "content": encoded_content,
        "sha": data["sha"],
    }).encode("utf-8")

    update_request = urllib.request.Request(
        url,
        data=update_data,
        headers=headers,
        method="PUT",
    )

    with urllib.request.urlopen(update_request) as response:
        response.read()


async def annuler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        "❌ Ajout du serveur annulé."
    )

    return ConversationHandler.END


def main():
    if not TOKEN:
        print("❌ Token Telegram introuvable.")
        return

    if not GITHUB_TOKEN:
        print("❌ Token GitHub introuvable.")
        return

    app = Application.builder().token(TOKEN).build()

    conversation = ConversationHandler(
        entry_points=[
            CommandHandler("ajouter_serveur", ajouter_serveur)
        ],
        states={
            PROTOCOL: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    recevoir_protocole
                )
            ],
            LOCATION: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    recevoir_location
                )
            ],
            DURATION: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    recevoir_duree
                )
            ],
            QUOTA: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    recevoir_quota
                )
            ],
            SERVER: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    recevoir_serveur
                )
            ],
        },
        fallbacks=[
            CommandHandler("annuler", annuler)
        ],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conversation)

    print("🤖 KANKALGA TECH BOT démarré...")
    app.run_polling()


if __name__ == "__main__":
    main()
