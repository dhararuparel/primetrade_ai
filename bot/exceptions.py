"""
Custom exception classes for the Binance Futures trading bot.
"""

class TradingBotError(Exception):
    """Base exception class for the trading bot."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return self.message


class ValidationError(TradingBotError):
    """Exception raised when input validation fails."""
    pass


class BinanceAPIError(TradingBotError):
    """Exception raised when Binance API returns an error response."""
    def __init__(self, message: str, code: int = None, details: dict = None):
        super().__init__(message)
        self.code = code
        self.details = details or {}

    def __str__(self) -> str:
        if self.code is not None:
            return f"{self.message} (Binance API Code: {self.code})"
        return self.message


class AuthenticationError(BinanceAPIError):
    """Exception raised when API credentials are invalid, expired, or missing."""
    pass


class InsufficientBalanceError(BinanceAPIError):
    """Exception raised when user does not have sufficient balance or margin."""
    pass


class NetworkError(TradingBotError):
    """Exception raised for connection, timeout, or DNS resolution issues."""
    pass
