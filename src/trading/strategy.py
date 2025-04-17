import logging
import pandas as pd
import numpy as np
from ta.trend import SMAIndicator
from ta.momentum import RSIIndicator
from config.config import STRATEGY_CONFIG

logger = logging.getLogger(__name__)

class TradingStrategy:
    def __init__(self):
        self.sma_period = STRATEGY_CONFIG['SMA_PERIOD']
        self.rsi_period = STRATEGY_CONFIG['RSI_PERIOD']
        self.rsi_overbought = STRATEGY_CONFIG['RSI_OVERBOUGHT']
        self.rsi_oversold = STRATEGY_CONFIG['RSI_OVERSOLD']
        self.price_history = []

    def add_price(self, price):
        """Add a new price to the history."""
        self.price_history.append(price)
        if len(self.price_history) > self.sma_period:
            self.price_history.pop(0)

    def calculate_signals(self):
        """Calculate trading signals based on SMA and RSI."""
        if len(self.price_history) < self.sma_period:
            return None

        # Convert price history to pandas Series
        prices = pd.Series(self.price_history)

        # Calculate SMA
        sma = SMAIndicator(close=prices, window=self.sma_period)
        sma_value = sma.sma_indicator().iloc[-1]

        # Calculate RSI
        rsi = RSIIndicator(close=prices, window=self.rsi_period)
        rsi_value = rsi.rsi().iloc[-1]

        # Generate signals
        current_price = prices.iloc[-1]
        signal = None

        # Buy signal: Price above SMA and RSI oversold
        if current_price > sma_value and rsi_value < self.rsi_oversold:
            signal = 'up'
        # Sell signal: Price below SMA and RSI overbought
        elif current_price < sma_value and rsi_value > self.rsi_overbought:
            signal = 'down'

        return {
            'signal': signal,
            'price': current_price,
            'sma': sma_value,
            'rsi': rsi_value
        }

    def get_strategy_info(self):
        """Get current strategy parameters and status."""
        return {
            'sma_period': self.sma_period,
            'rsi_period': self.rsi_period,
            'rsi_overbought': self.rsi_overbought,
            'rsi_oversold': self.rsi_oversold,
            'price_history_length': len(self.price_history)
        } 