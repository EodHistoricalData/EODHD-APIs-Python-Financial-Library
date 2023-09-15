import websocket
import threading
import signal
import time
import json
import re


class WebSocketClient:
    def __init__(
        self,
        api_key: str,
        endpoint: str,
        symbols: list,
        store_data: bool = True,
        output_delay: float = 0.25,
        display_data: bool = True,
    ) -> None:
        # Validate API key
        prog = re.compile(r"^[A-z0-9.]{16,32}$")
        if not prog.match(api_key):
            raise ValueError("API key is invalid")

        # Validate endpoint
        if endpoint not in ["us", "us_quote", "forex", "crypto"]:
            raise ValueError("Endpoint is invalid")

        # Validate symbol list
        if len(symbols) == 0:
            raise ValueError("No symbol(s) provided")

        # Validate individual symbols
        prog = re.compile(r"^[A-z0-9-$]{1,48}$")
        for symbol in symbols:
            if not prog.match(symbol):
                raise ValueError(f"Symbol is invalid: {symbol}")

        # Validate max symbol subscriptions
        if len(symbols) > 50:
            raise ValueError("Max symbol subscription count is 50!")

        # Map class arguments to private variables
        self._api_key = api_key
        self._endpoint = endpoint
        self._symbols = symbols
        self._store_data = store_data
        self._output_delay = output_delay
        self._display_data = display_data

        self.running = True
        self.stop_event = threading.Event()
        self.data_list = []
        self.ws = None

        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        print("Stopping websocket...")
        self.running = False
        self.stop_event.set()
        self.thread.join()
        print("Websocket stopped.")

    def _collect_data(self):
        self.ws = websocket.create_connection(f"wss://ws.eodhistoricaldata.com/ws/{self._endpoint}?api_token={self._api_key}")

        # Send the subscription message
        payload = {
            "action": "subscribe",
            "symbols": ",".join(self._symbols),
        }
        self.ws.send(json.dumps(payload))

        # Collect data until the stop event is set
        while not self.stop_event.is_set():
            message = self.ws.recv()
            if self._store_data:
                self.data_list.append(message)
            if self._display_data:
                print(message)
            time.sleep(self._output_delay)

        # Close the WebSocket connection
        self.ws.close()

    def start(self):
        self.thread = threading.Thread(target=self._collect_data)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        self.thread.join()

    def get_data(self):
        return self.data_list


if __name__ == "__main__":
    client = WebSocketClient(api_key="OeAFFmMliFG5orCUuwAKQ8l4WWFQ67YX", endpoint="crypto", symbols=["BTC-USD"])

    client.start()

    try:
        while client.running:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping due to user request.")
        client.stop()
