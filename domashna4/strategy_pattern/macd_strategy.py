from domashna4.strategy_pattern.strategy import AnalysisStrategy

class MACDStrategy(AnalysisStrategy):
    def analyze(self, data):
        if len(data) < 6:
            return "MACD: not enough data"

        short_avg = sum(data[-3:]) / 3
        long_avg = sum(data[-6:]) / 6
        macd = short_avg - long_avg

        return f"MACD = {round(macd, 2)}"
