"""websocketclient.py"""

import re
import json
from time import sleep
from datetime import datetime
from threading import Thread
from websocket import create_connection, WebSocketConnectionClosedException

class WebSocketClient():
    """WebSocket class"""

    # pylint: disable=too-many-instance-attributes
    # Eleven is reasonable in this case

    def __init__(
        self,
        api_key: str,
        endpoint: str,
        symbols: list,
    ) -> None:
        super().__init__()

        # Validate API key
        prog = re.compile(r"^[A-z0-9.]{16,32}$")
        if not prog.match(api_key):
            raise ValueError("API key is invalid")

        # Validate endpoint
        if endpoint not in ["us","us_quote","forex","crypto"]:
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

        # Statistical variables
        self.start_time = None
        self.time_elapsed = 0
        self.message_count = 0

        # WebSocket variables
        self.stop = None
        self.thread = None
        self.keepalive = None
        self.websocket = None
        self.message = None

    # Public functions

    def start(self):
        """Initialise websocket"""

        def _go():
            self._connect()
            self._listen()
            self._disconnect()

        self.stop = False
        self.on_open()
        self.thread = Thread(target=_go)
        self.keepalive = Thread(target=self._keepalive)
        self.thread.start()

    def close(self):
        """Close websocket"""

        self.stop = True
        self.start_time = None
        self.time_elapsed = 0
        self._disconnect()
        self.thread.join()

    # Private functions

    def _connect(self):
        """Connect to websocket"""

        self.websocket = create_connection(
            f"wss://ws.eodhistoricaldata.com/ws/{self._endpoint}?api_token={self._api_key}"
        )
        self.websocket.send(
            json.dumps(
                {
                    "action": "subscribe",
                    "symbols": ",".join(self._symbols),
                }
            )
        )
        self.start_time = datetime.now()

    def _listen(self):
        """Listen to websocket"""

        self.keepalive.start()
        while not self.stop:
            try:
                data = self.websocket.recv()
                if data != "":
                    msg = json.loads(data)
                else:
                    msg = {}
            except ValueError as error_msg:
                self.on_error(error_msg)
            except Exception as error_msg: # pylint: disable=broad-except
                self.on_error(error_msg)
            else:
                self.on_message(msg)

    def _keepalive(self, interval=30):
        """WebSocket keepalive"""

        while self.websocket.connected:
            self.websocket.ping("keepalive")
            sleep(interval)

    def _disconnect(self):
        """Disconnect websocket"""

        try:
            if self.websocket:
                self.websocket.close()
        except WebSocketConnectionClosedException:
            pass
        finally:
            self.keepalive.join()

    # Events

    def on_close(self):
        """WebSocket on-close event"""

        print("-- WebSocket Closed --")

    def on_error(self, error_msg, data=None):
        """WebSocket on_error event"""

        print(f"{error_msg} - data: {data}")

        self.stop = True
        try:
            self.websocket = None
            self.start_time = None
            self.time_elapsed = 0
        except: # pylint: disable=bare-except
            pass

    def on_open(self):
        """WebSocket on-open event"""

        self.message_count = 0

    def on_message(self, msg):
        """WebSocket on-message event"""

        if self.start_time is not None:
            self.time_elapsed = round(
                (datetime.now()-self.start_time).total_seconds()
            )
        self.message_count += 1
        self.message = msg
        #print (self.message_count, msg)

    # Getters

    def get_start_time(self) -> datetime:
        """Start time getter"""

        return self.start_time

    def get_time_elapsed(self) -> int:
        """Time elapsed getter"""

        return self.time_elapsed


def main() -> None:
    """Main"""

    websocket = WebSocketClient(
        # Demo API key for testing purposes
        api_key="OeAFFmMliFG5orCUuwAKQ8l4WWFQ67YX", endpoint="crypto", symbols=["BTC-USD"]
        #api_key="OeAFFmMliFG5orCUuwAKQ8l4WWFQ67YX", endpoint="forex", symbols=["EURUSD"]
        #api_key="OeAFFmMliFG5orCUuwAKQ8l4WWFQ67YX", endpoint="us", symbols=["AAPL"]
    )
    websocket.start()

    message_count = 0
    while True:
        if websocket:
            if (
                message_count != websocket.message_count
            ):
                print(websocket.message)
                message_count = websocket.message_count
                sleep(0.25)  # output every 1/4 second, websocket is realtime

if __name__ == "__main__":
    main()
