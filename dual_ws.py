import json
import time
import threading
from datetime import datetime
from binance import ThreadedWebsocketManager
from utils import detect_signal, execute_trade, log_trade, TRADE_SYMBOL

active_position = None

def start_dual_ws(bot, chat_id, scs_ref, live_ref, scalping_flag):
    def handle_message(msg):
        nonlocal active_position
        if not scalping_flag[0]:
            return

        if msg['e'] != 'kline' or msg['k']['x'] is False:
            return

        candle = msg['k']
        close = float(candle['c'])
        open_ = float(candle['o'])
        high = float(candle['h'])
        low = float(candle['l'])
        volume = float(candle['v'])
        timestamp = int(candle['t'])

        result = detect_signal(open_, high, low, close, volume)

        if result and result['scs'] >= scs_ref[0]:
            direction = result['direction']
            scs = result['scs']
            entry_price = close

            now = datetime.utcfromtimestamp(timestamp / 1000)
            message = (
                f"\n✅ Wick-Entry signal {direction.upper()}\n"
                f"Time: {now.strftime('%Y-%m-%d %H:%M')} UTC\n"
                f"SCS: {scs}\n"
                f"Price: {entry_price:.2f}"
            )
            bot.send_message(chat_id=chat_id, text=message)

            if live_ref[0]:
                if active_position is None:
                    side = 'BUY' if direction == 'long' else 'SELL'
                    active_position = execute_trade(side, entry_price)
                    log_trade(now, side, entry_price, scs)

    def run_ws():
        twm = ThreadedWebsocketManager()
        twm.start()
        twm.start_kline_socket(callback=handle_message, symbol=TRADE_SYMBOL, interval='5m')
        while True:
            time.sleep(1)

    threading.Thread(target=run_ws, daemon=True).start()

