#APIs/FinancialNewsAPI.py

from .BaseAPI import BaseAPI


class FinancialNewsAPI(BaseAPI):
    """
    Financial News Feed + Sentiment + News Word Weights.

    Notes:
    - Tags are dynamic (standard + AI auto-detected). There is no fixed list to validate against;
      you can use any tag string you need.  :contentReference[oaicite:2]{index=2}
    """

    def financial_news(
        self,
        api_token: str,
        s: str | None = None,
        t: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ):
        """
        GET /api/news

        Requires at least one of:
        - s: ticker (e.g. AAPL.US)
        - t: tag/topic (e.g. technology)

        If both s and t are provided, this method keeps backward-compatible behavior and
        prefers `s` (same as the old implementation).
        """
        endpoint = "news"
        query_string = ""

        if s is None and t is None:
            raise ValueError("s or t is empty. You need to add s or t to args")

        # Backward-compatible behavior: prefer symbol when both provided
        if s is not None:
            query_string += "&s=" + str(s)
        else:
            query_string += "&t=" + str(t)

        if limit is not None:
            query_string += "&limit=" + str(limit)
        if offset is not None:
            query_string += "&offset=" + str(offset)
        if from_date is not None:
            query_string += "&from=" + str(from_date)
        if to_date is not None:
            query_string += "&to=" + str(to_date)

        return self._rest_get_method(api_key=api_token, endpoint=endpoint, querystring=query_string)

    def get_sentiment(
        self,
        api_token: str,
        s: str,
        from_date: str | None = None,
        to_date: str | None = None,
    ):
        """
        GET /api/sentiments

        s: one or more comma-separated tickers (e.g. "BTC-USD.CC,AAPL.US")
        """
        endpoint = "sentiments"
        query_string = ""

        if not s:
            raise ValueError("s argument is empty. You need to add s to args")

        query_string += "&s=" + str(s)

        if from_date is not None:
            query_string += "&from=" + str(from_date)
        if to_date is not None:
            query_string += "&to=" + str(to_date)

        return self._rest_get_method(api_key=api_token, endpoint=endpoint, querystring=query_string)

    def news_word_weights(
        self,
        api_token: str,
        s: str,
        date_from: str | None = None,
        date_to: str | None = None,
        limit: int | None = None,
    ):
        """
        GET /api/news-word-weights  :contentReference[oaicite:3]{index=3}

        Params:
        - s (required): ticker symbol to analyze
        - date_from (optional) -> filter[date_from]
        - date_to (optional)   -> filter[date_to]
        - limit (optional)     -> page[limit]
        """
        endpoint = "news-word-weights"
        query_string = ""

        if not s:
            raise ValueError("s argument is empty. You need to add s to args")

        query_string += "&s=" + str(s)

        if date_from is not None:
            query_string += "&filter[date_from]=" + str(date_from)
        if date_to is not None:
            query_string += "&filter[date_to]=" + str(date_to)
        if limit is not None:
            query_string += "&page[limit]=" + str(limit)

        return self._rest_get_method(api_key=api_token, endpoint=endpoint, querystring=query_string)
