import pandas as pd
import os
from telegram import Bot

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def analyze_trades(telegram=False):
    try:
        df = pd.read_csv("trades_log.csv")
        if df.empty:
            return

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date

        summary = df.groupby('date').agg({
            'side': 'count',
            'pnl': 'sum',
            'scs': 'mean'
        }).rename(columns={
            'side': 'trades',
            'pnl': 'total_pnl',
            'scs': 'avg_scs'
        })

        last_day = summary.iloc[-1]
        report = (
            f"📊 *Dnevni izveštaj*\n"
            f"📅 Datum: {summary.index[-1]}\n"
            f"🔢 Broj trejdova: {int(last_day['trades'])}\n"
            f"💸 PnL: {last_day['total_pnl']:.2f} USDT\n"
            f"⭐ Prosečan SCS: {last_day['avg_scs']:.1f}"
        )

        if telegram:
            bot = Bot(token=TELEGRAM_TOKEN)
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=report, parse_mode="Markdown")

    except Exception as e:
        print(f"[ERROR] analyze_trades: {e}")
