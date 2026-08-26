import websocket
import threading
import signal
import time
import json
import re
import pandas as pd

pd.set_option('display.float_format', '{:.8f}'.format)

# Codes that mean "this connection will never work" rather than "that request was wrong".
AUTH_FAILURE_CODES = frozenset({401, 403, 422})

# Markets served by the real-time WebSocket. The Cboe equity markets (us, eu) each expose
# four streams; forex and crypto come from separate providers and have trades only.
VALID_ENDPOINTS = frozenset(
    {
        "us", "us-quote", "us-candles", "us-status",
        "eu", "eu-quote", "eu-candles", "eu-status",
        "forex", "crypto",
    }
)


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
        max_symbols: int = 50,
    ) -> None:
        # Validate API key
        prog = re.compile(r"^[A-z0-9.]{16,32}$")
        if not prog.match(api_key):
            raise ValueError("API key is invalid")

        # Validate endpoint. The Cboe equity markets each serve four streams: trades,
        # quotes, one-minute bars and trading status.
        if endpoint not in VALID_ENDPOINTS:
            raise ValueError(f"Endpoint is invalid: {endpoint}. Valid: {', '.join(sorted(VALID_ENDPOINTS))}")

        # Validate symbol list
        if len(symbols) == 0:
            raise ValueError("No symbol(s) provided")

        # Validate individual symbols. The dot is required for European tickers
        # (TICKER.EXCHANGE, e.g. GSK.LSE); the previous class was [A-z], which also
        # admitted the punctuation sitting between Z and a in ASCII.
        prog = re.compile(r"^[A-Za-z0-9.\-$]{1,48}$")
        for symbol in symbols:
            if not prog.match(symbol):
                raise ValueError(f"Symbol is invalid: {symbol}")

        # Validate max symbol subscriptions. 50 is the default plan allowance; larger
        # plans exist, so this is a guard rail rather than a protocol limit — the server
        # answers "Symbols limit reached" for the authoritative cap.
        if len(symbols) > max_symbols:
            raise ValueError(
                f"Max symbol subscription count is {max_symbols}! "
                "Pass max_symbols= if your plan allows more."
            )

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
        self._max_symbols = max_symbols

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

                    # Control frames are not market data, and the service uses TWO shapes
                    # for them. Authentication failures arrive as {"status": 403|422,
                    # "message": "Server error"} — note the key is "status" — and they come
                    # over the socket AFTER a successful handshake, so the connection
                    # opening is not evidence the token was accepted. Everything else uses
                    # "status_code": the 200 ack, 404 for an unknown market, the 422 family
                    # for bad subscribe commands, 429 for the connection cap, 500.
                    #
                    # The key is the discriminator, and that is deliberate: 422 appears in
                    # BOTH shapes. As "status" it means the token is missing and the
                    # connection is dead; as "status_code" it means one subscribe command
                    # was wrong ("Symbols limit reached", "Invalid request") and the
                    # connection is perfectly usable. Treating every 422 as fatal would tear
                    # down a working stream over a recoverable mistake, so do not
                    # "simplify" this into a single lookup across both keys.
                    if isinstance(message_json, dict) and (
                        "status" in message_json or "status_code" in message_json
                    ):
                        code = message_json.get("status", message_json.get("status_code"))
                        if "status" in message_json and code in AUTH_FAILURE_CODES:
                            print(
                                f"Authentication rejected by the server ({code}): "
                                f"{message_json.get('message')}. Check that the API key is "
                                "correct and that the plan includes real-time access; "
                                "retrying will not change the answer."
                            )
                            self.running = False
                            self.stop_event.set()
                            break
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

        # Crypto sends p/q as JSON strings while equities send numbers, so coerce before
        # any comparison — "9" > "10" is true for strings and would corrupt high/low.
        # Traded size is "q" on crypto and "v" on the equity trade streams.
        if "p" in message_json:
            price = float(message_json["p"])
            size = message_json.get("q", message_json.get("v", 0))
            try:
                size = float(size)
            except (TypeError, ValueError):
                size = 0.0

            if "o" not in candle:
                candle["o"] = price
                candle["h"] = price
                candle["l"] = price
                candle["c"] = price
                candle["v"] = size
            else:
                candle["c"] = price
                if price > candle["h"]:
                    candle["h"] = price
                if price < candle["l"]:
                    candle["l"] = price
                candle["v"] = candle.get("v", 0.0) + size

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
