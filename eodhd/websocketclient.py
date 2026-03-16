import websocket
import threading
import signal
import time
import json
import re
import pandas as pd

pd.set_option('display.float_format', '{:.8f}'.format)


class WebSocketClient:
    def __init__(
        self,
        api_key: str,
        endpoint: str,
        symbols: list,
        store_data: bool = False,
        display_stream: bool = False,
        display_candle_1m: bool = False,
        display_candle_5m: bool = False,
        display_candle_1h: bool = False,
        max_reconnect_attempts: int = 5,
        reconnect_base_delay: float = 1.0,
    ) -> None:
        # Validate API key
        prog = re.compile(r"^[A-z0-9.]{16,32}$")
        if not prog.match(api_key):
            raise ValueError("API key is invalid")

        # Validate endpoint
        if endpoint not in ["us", "us-quote", "forex", "crypto"]:
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
        self._display_stream = display_stream
        self._display_candle_1m = display_candle_1m
        self._display_candle_5m = display_candle_5m
        self._display_candle_1h = display_candle_1h
        self._max_reconnect_attempts = max_reconnect_attempts
        self._reconnect_base_delay = reconnect_base_delay

        self.running = True
        self.message = None
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
        if self.ws is not None:
            try:
                self.ws.close()
            except Exception:
                pass
        print("Websocket stopped.")

    def _floor_to_nearest_interval(self, timestamp_ms, interval):
        # Convert to seconds
        timestamp_s = timestamp_ms // 1000

        # Define the number of seconds for each interval
        seconds_per_minute = 60
        seconds_per_hour = seconds_per_minute * 60

        # Determine the number of seconds for the given interval
        if interval == "1 minute":
            interval_seconds = seconds_per_minute
        elif interval == "5 minutes":
            interval_seconds = 5 * seconds_per_minute
        elif interval == "1 hour":
            interval_seconds = seconds_per_hour
        else:
            raise ValueError(f"Unsupported interval: {interval}")

        # Floor to the nearest interval
        floored_s = (timestamp_s // interval_seconds) * interval_seconds

        # Convert back to milliseconds
        floored_ms = floored_s * 1000

        return floored_ms

    def _collect_data(self):
        attempt = 0

        while not self.stop_event.is_set():
            try:
                self.ws = websocket.create_connection(
                    f"wss://ws.eodhistoricaldata.com/ws/{self._endpoint}?api_token={self._api_key}"
                )

                # Send the subscription message
                payload = {
                    "action": "subscribe",
                    "symbols": ",".join(self._symbols),
                }
                self.ws.send(json.dumps(payload))

                # Reset attempt counter on successful connection
                attempt = 0

                # Reset candle state on each (re)connection — partial candles are misleading
                candle_1m = {}
                candle_5m = {}
                candle_1h = {}

                # Collect data until the stop event is set
                while not self.stop_event.is_set():
                    try:
                        self.message = self.ws.recv()
                    except (
                        websocket.WebSocketConnectionClosedException,
                        websocket.WebSocketException,
                        ConnectionError,
                        OSError,
                    ):
                        break

                    try:
                        message_json = json.loads(self.message)
                    except (json.JSONDecodeError, TypeError):
                        continue

                    if self._store_data:
                        self.data_list.append(self.message)

                    if self._display_stream:
                        print(self.message)

                    if self._display_candle_1m:
                        self._update_candle(candle_1m, message_json, "1 minute", 60)

                    if self._display_candle_5m:
                        self._update_candle(candle_5m, message_json, "5 minutes", 60)

                    if self._display_candle_1h:
                        self._update_candle(candle_1h, message_json, "1 hour", 60)

            except (
                websocket.WebSocketException,
                ConnectionError,
                OSError,
            ) as err:
                if self.stop_event.is_set():
                    break
                attempt += 1
                if attempt > self._max_reconnect_attempts:
                    print(f"Max reconnect attempts ({self._max_reconnect_attempts}) reached. Giving up.")
                    self.running = False
                    self.stop_event.set()
                    break
                delay = self._reconnect_base_delay * (2 ** (attempt - 1))
                print(f"Connection lost ({err}). Reconnecting in {delay:.1f}s (attempt {attempt}/{self._max_reconnect_attempts})...")
                self.stop_event.wait(delay)

        # Close the WebSocket connection
        if self.ws is not None:
            try:
                self.ws.close()
            except Exception:
                pass

    def _update_candle(self, candle, message_json, interval_name, granularity):
        if "t" in message_json:
            candle_date = self._floor_to_nearest_interval(message_json["t"], interval_name)

            if "t" in candle and (candle_date != candle["t"]):
                print(candle)
                candle.clear()

            candle["t"] = candle_date

        if "s" in message_json:
            candle["m"] = message_json["s"]
            candle["g"] = granularity

        if "p" in message_json and "o" not in candle:
            candle["o"] = message_json["p"]
            candle["h"] = message_json["p"]
            candle["l"] = message_json["p"]
            candle["c"] = message_json["p"]
            if "q" in message_json:
                candle["v"] = float(message_json["q"])
        elif "p" in message_json and "o" in candle:
            candle["c"] = message_json["p"]
            if message_json["p"] > candle["h"]:
                candle["h"] = message_json["p"]
            if message_json["p"] < candle["l"]:
                candle["l"] = message_json["p"]
            candle["v"] += float(message_json["q"])

    def _keepalive(self, interval=30):
        while not self.stop_event.is_set():
            self.stop_event.wait(interval)
            if self.stop_event.is_set():
                break
            if self.ws is not None and hasattr(self.ws, "connected") and self.ws.connected:
                try:
                    self.ws.ping("keepalive")
                except Exception:
                    pass

    def start(self):
        self.thread = threading.Thread(target=self._collect_data)
        self.keepalive = threading.Thread(target=self._keepalive)
        self.thread.start()
        self.keepalive.start()

    def stop(self):
        self.stop_event.set()
        if self.ws is not None:
            try:
                self.ws.close()
            except Exception:
                pass
        self.thread.join(timeout=5.0)
        self.keepalive.join(timeout=5.0)

    def get_data(self):
        return self.data_list


if __name__ == "__main__":
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
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping due to user request.")
        client.stop()
