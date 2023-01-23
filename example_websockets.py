"""Websocket example"""

from time import sleep
from eodhd import WebSocketClient


def main() -> None:
    """Main"""

    websocket = WebSocketClient(
        # Demo API key for testing purposes
        api_key="OeAFFmMliFG5orCUuwAKQ8l4WWFQ67YX",
        endpoint="crypto",
        symbols=["BTC-USD"]
        # api_key="OeAFFmMliFG5orCUuwAKQ8l4WWFQ67YX", endpoint="forex", symbols=["EURUSD"]
        # api_key="OeAFFmMliFG5orCUuwAKQ8l4WWFQ67YX", endpoint="us", symbols=["AAPL"]
    )
    websocket.start()

    message_count = 0
    while True:
        if websocket:
            if message_count != websocket.message_count:
                print(websocket.message)
                message_count = websocket.message_count
                sleep(0.25)  # output every 1/4 second, websocket is realtime


if __name__ == "__main__":
    main()
