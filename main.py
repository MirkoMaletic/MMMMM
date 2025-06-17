import os import time import threading from flask import Flask, request from telegram import Update, Bot from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes import analyze_trades import dual_ws

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") WEBHOOK_URL = os.getenv("WEBHOOK_URL") LIVE_TRADING = os.getenv("LIVE_TRADING", "False") == "True"

scalping_active = False min_scs_threshold = 60 last_report_day = None

flask_app = Flask(name) bot_app = ApplicationBuilder().token(TELEGRAM_TOKEN).build() bot = Bot(token=TELEGRAM_TOKEN)

=== Komande ===
async def start_scalping(update: Update, context: ContextTypes.DEFAULT_TYPE): global scalping_active scalping_active = True await update.message.reply_text("🚀 Scalping bot pokrenut.") dual_ws.start_dual_ws(context.bot, TELEGRAM_CHAT_ID, [min_scs_threshold], [LIVE_TRADING], [scalping_active])

async def pause_scalping(update: Update, context: ContextTypes.DEFAULT_TYPE): global scalping_active scalping_active = False await update.message.reply_text("⏸ Pauza aktivirana.")

async def status_scalping(update: Update, context: ContextTypes.DEFAULT_TYPE): status = "✅ Aktivno" if scalping_active else "❌ Pauzirano" await update.message.reply_text(f"📊 Status: {status}\nMin SCS: {min_scs_threshold}")

async def stop_scalping(update: Update, context: ContextTypes.DEFAULT_TYPE): global scalping_active scalping_active = False await update.message.reply_text("🛑 Scalping bot isključen.")

async def set_scs_min(update: Update, context: ContextTypes.DEFAULT_TYPE): global min_scs_threshold try: value = int(context.args[0]) if 0 <= value <= 100: min_scs_threshold = value await update.message.reply_text(f"✅ SCS prag postavljen na {value}") else: await update.message.reply_text("⚠ Unesite broj između 0 i 100.") except: await update.message.reply_text("❗ Upotreba: /scs_min 65")

=== Dnevni izveštaj ===
def daily_report_scheduler(): global last_report_day while True: now = time.gmtime() if now.tm_hour == 22 and now.tm_mday != last_report_day: analyze_trades.analyze_trades(telegram=True) last_report_day = now.tm_mday time.sleep(60)

=== Registracija komandi ===
bot_app.add_handler(CommandHandler("start_scalping", start_scalping)) bot_app.add_handler(CommandHandler("pause_scalping", pause_scalping)) bot_app.add_handler(CommandHandler("status_scalping", status_scalping)) bot_app.add_handler(CommandHandler("stop_scalping", stop_scalping)) bot_app.add_handler(CommandHandler("scs_min", set_scs_min))

=== Webhook ruta ===
@flask_app.route("/", methods=["POST"]) async def webhook(): update = Update.de_json(request.get_json(force=True), bot) await bot_app.process_update(update) return "OK", 200

=== Pokretanje ===
if name == "main": bot.delete_webhook() bot.set_webhook


    
