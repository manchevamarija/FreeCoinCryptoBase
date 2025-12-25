from domashna4.strategy_pattern.strategy import AnalysisStrategy

class SMAStrategy(AnalysisStrategy):
    def analyze(self, data):
        if not data:
            return "SMA: no data"

        window = 5
        sma = sum(data[-window:]) / window
        return f"SMA({window}) = {round(sma, 2)}"
