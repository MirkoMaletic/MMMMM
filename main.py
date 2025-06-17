import os
import time
import threading
from datetime import datetime
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import analyze_trades
import dual_ws

# === Konfiguracija ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
LIVE_TRADING = os.getenv("LIVE_TRADING", "False") == "True"

scalping_active = False
min_scs_threshold = 60
last_report_day = None

# === Komande ===
async def start_scalping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global scalping_active
    scalping_active = True
    await update.message.reply_text("🚀 Scalping bot (5m + 1m potvrda) je pokrenut.")
    dual_ws.start_dual_ws(context.bot, TELEGRAM_CHAT_ID, [min_scs_threshold], [LIVE_TRADING], [scalping_active])

async def pause_scalping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global scalping_active
    scalping_active = False
    await update.message.reply_text("⏸ Scalping bot je pauziran.")

async def status_scalping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = "✅ Aktivno" if scalping_active else "❌ Neaktivno"
    await update.message.reply_text(f"📊 Status scalping modula: {status}\nMin SCS: {min_scs_threshold}")

async def stop_scalping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global scalping_active
    scalping_active = False
    await update.message.reply_text("🛑 Scalping bot je isključen.")

async def set_scs_min(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global min_scs_threshold
    try:
        value = int(context.args[0])
        if 0 <= value <= 100:
            min_scs_threshold = value
            await update.message.reply_text(f"✅ SCS prag postavljen na {value}")
        else:
            await update.message.reply_text("⚠ Unesite broj između 0 i 100.")
    except (IndexError, ValueError):
        await update.message.reply_text("❗ Upotreba: /scs_min 65")

# === Dnevni izveštaj u 22h ===
def daily_report_scheduler():
    global last_report_day
    while True:
        now = time.gmtime()
        if now.tm_hour == 22 and (last_report_day != now.tm_mday):
            analyze_trades.analyze_trades(telegram=True)
            last_report_day = now.tm_mday
        time.sleep(60)

# === Pokretanje aplikacije ===
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start_scalping", start_scalping))
    app.add_handler(CommandHandler("pause_scalping", pause_scalping))
    app.add_handler(CommandHandler("status_scalping", status_scalping))
    app.add_handler(CommandHandler("stop_scalping", stop_scalping))
    app.add_handler(CommandHandler("scs_min", set_scs_min))

    threading.Thread(target=daily_report_scheduler, daemon=True).start()

    app.run_polling()
