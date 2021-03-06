from app.risk.candles import Candles
from datetime import datetime


class InputCandleError(Exception):
    def __init__(self, candle_list):
        self.candle_list = candle_list

    def __str__(self):
        return "Not enough candles for creating ATR, requires 15 but {} are given".format(len(self.candle_list))


class ATR:
    """
    Using simple moving average for smoothing
    """
    DEFAULT_PERIOD = 14

    def __init__(self, api, candles_class=Candles, period=DEFAULT_PERIOD):
        self.candle_list = None
        self.tr_list = []
        self.api = api
        self.candles = candles_class(api=self.api)
        self.updated_time = datetime.fromtimestamp(0.0)
        self.period = period
        self.prev_ticker = None

    def _populate_candle_list(self, instrument, granularity):
        fetched_updated_time, fetched_candle_list = self.candles.fetch_candles(
            instrument, self.period+2, granularity)

        if self._is_updated(fetched_updated_time, instrument):
            self.candle_list = fetched_candle_list[-(self.period+1):]
            self.updated_time = fetched_updated_time
            self.prev_ticker = instrument

    def _is_updated(self, dt, ticker):
        if dt > self.updated_time or ticker != self.prev_ticker:
            return True
        return False

    def calculate_atr(self, instrument, granularity='D'):
        self.tr_list = []
        self._populate_candle_list(instrument, granularity)

        if len(self.candle_list) < self.period+1:
            raise InputCandleError(self.candle_list)

        length = len(self.candle_list)
        candle_pairs = zip(
            self.candle_list[0: length-1], self.candle_list[1: length])

        for prev_candle, curr_candle in candle_pairs:
            tr = max(curr_candle.h - curr_candle.l,
                     abs(curr_candle.h - prev_candle.c),
                     abs(curr_candle.l - prev_candle.c))
            self.tr_list.append(tr)

        return sum(self.tr_list) / self.period
