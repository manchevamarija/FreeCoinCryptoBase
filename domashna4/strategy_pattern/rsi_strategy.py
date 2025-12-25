from domashna4.strategy_pattern.strategy import AnalysisStrategy

class RSIStrategy(AnalysisStrategy):
    def analyze(self, data):
        if len(data) < 2:
            return "RSI: not enough data"

        gains = []
        losses = []

        for i in range(1, len(data)):
            diff = data[i] - data[i - 1]
            if diff > 0:
                gains.append(diff)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(diff))

        avg_gain = sum(gains) / len(gains)
        avg_loss = sum(losses) / len(losses)

        if avg_loss == 0:
            return "RSI = 100 (strong uptrend)"

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return f"RSI = {round(rsi, 2)}"
