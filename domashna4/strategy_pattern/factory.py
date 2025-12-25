from domashna4.strategy_pattern.rsi_strategy import RSIStrategy
from domashna4.strategy_pattern.sma_strategy import SMAStrategy
from domashna4.strategy_pattern.macd_strategy import MACDStrategy

class StrategyFactory:
    @staticmethod
    def create(strategy_type: str):
        if strategy_type == "RSI":
            return RSIStrategy()
        if strategy_type == "SMA":
            return SMAStrategy()
        if strategy_type == "MACD":
            return MACDStrategy()
        raise ValueError("Unknown strategy type")
