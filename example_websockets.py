"""Websocket example"""

import time
from eodhd import WebSocketClient

client = WebSocketClient(
        api_key="OeAFFmMliFG5orCUuwAKQ8l4WWFQ67YX",
        endpoint="crypto",
        symbols=["BTC-USD"],
        display_stream=False,
        display_candle_1m=True,
        display_candle_5m=False,
        display_candle_1h=False,
)
client.start()

try:
    while client.running:
        res = client.get_data()
        print(res)
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopping due to user request.")
    client.stop()
