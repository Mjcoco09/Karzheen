import logging
from config.config import TRADING_CONFIG

logger = logging.getLogger(__name__)

class RiskManager:
    def __init__(self):
        self.risk_percentage = TRADING_CONFIG['RISK_PERCENTAGE']
        self.min_delay = TRADING_CONFIG['MIN_DELAY']
        self.max_delay = TRADING_CONFIG['MAX_DELAY']
        self.trade_history = []

    def calculate_position_size(self, balance):
        """Calculate position size based on account balance and risk percentage."""
        try:
            risk_amount = balance * self.risk_percentage
            return round(risk_amount, 2)
        except Exception as e:
            logger.error(f"Error calculating position size: {str(e)}")
            return None

    def can_trade(self, balance):
        """Check if trading is allowed based on risk management rules."""
        try:
            # Check if balance is sufficient for minimum trade
            min_trade = self.calculate_position_size(balance)
            if min_trade is None or min_trade < 1:  # Assuming minimum trade size is 1
                return False

            # Check if we've had too many consecutive losses
            if len(self.trade_history) >= 3:
                last_three = self.trade_history[-3:]
                if all(trade['result'] == 'loss' for trade in last_three):
                    logger.warning("Three consecutive losses - trading paused")
                    return False

            return True
        except Exception as e:
            logger.error(f"Error in can_trade check: {str(e)}")
            return False

    def add_trade(self, trade_data):
        """Add a trade to the history."""
        self.trade_history.append(trade_data)
        if len(self.trade_history) > 100:  # Keep last 100 trades
            self.trade_history.pop(0)

    def get_trade_stats(self):
        """Get trading statistics."""
        if not self.trade_history:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'average_win': 0,
                'average_loss': 0
            }

        total_trades = len(self.trade_history)
        winning_trades = sum(1 for trade in self.trade_history if trade['result'] == 'win')
        win_rate = (winning_trades / total_trades) * 100

        profits = [trade['profit'] for trade in self.trade_history if trade['result'] == 'win']
        losses = [abs(trade['profit']) for trade in self.trade_history if trade['result'] == 'loss']

        average_win = sum(profits) / len(profits) if profits else 0
        average_loss = sum(losses) / len(losses) if losses else 0
        profit_factor = average_win / average_loss if average_loss != 0 else float('inf')

        return {
            'total_trades': total_trades,
            'win_rate': round(win_rate, 2),
            'profit_factor': round(profit_factor, 2),
            'average_win': round(average_win, 2),
            'average_loss': round(average_loss, 2)
        }

    def get_risk_settings(self):
        """Get current risk management settings."""
        return {
            'risk_percentage': self.risk_percentage,
            'min_delay': self.min_delay,
            'max_delay': self.max_delay
        } 