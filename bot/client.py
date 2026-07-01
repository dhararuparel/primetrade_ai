"""
Client wrapper for Binance Futures API.
"""
import os
import time
import random
from typing import Any, Dict, Optional
import requests
from dotenv import load_dotenv
from binance.client import Client
from binance.exceptions import BinanceAPIException

from bot.exceptions import (
    BinanceAPIError,
    AuthenticationError,
    InsufficientBalanceError,
    NetworkError,
    ValidationError
)
from bot.logging_config import logger


def handle_binance_exception(e: Exception) -> Exception:
    """
    Map python-binance API exceptions and requests network errors
    to our custom error hierarchy.
    """
    if isinstance(e, BinanceAPIException):
        msg = e.message or ""
        code = e.code or 0
        
        # Specific Binance API codes
        # -2015: Invalid API-key, IP, or permissions for action.
        # -1022: Signature for this request is not valid.
        # -2014: API-key format invalid.
        # -1002: Unauthorized.
        if code in (-2015, -1022, -2014, -1002) or "api-key" in msg.lower() or "signature" in msg.lower():
            return AuthenticationError(
                message="Authentication failed. Please verify your API Key and Secret.",
                code=code,
                details={"status_code": e.status_code, "api_message": msg}
            )
        
        # -2027: Insufficient balance
        # -2019: Margin is insufficient
        # -4013: Less than minimum trade quantity (or similar lot size errors)
        if code in (-2027, -2019) or "insufficient" in msg.lower() or "margin" in msg.lower():
            return InsufficientBalanceError(
                message="Order placement failed due to insufficient balance or margin.",
                code=code,
                details={"status_code": e.status_code, "api_message": msg}
            )
            
        return BinanceAPIError(
            message=msg,
            code=code,
            details={"status_code": e.status_code}
        )
        
    if isinstance(e, (requests.exceptions.Timeout, requests.exceptions.ConnectTimeout)):
        return NetworkError(f"Network timeout occurred while communicating with Binance: {e}")
        
    if isinstance(e, requests.exceptions.RequestException):
        return NetworkError(f"Network connection failed: {e}")
        
    return e


class BinanceFuturesClient:
    """Wrapper for Binance Futures API (USDT-M) targeting Testnet."""

    def __init__(
        self, 
        api_key: Optional[str] = None, 
        api_secret: Optional[str] = None, 
        dry_run: bool = False
    ):
        self.dry_run = dry_run
        
        # Load environment variables if keys are not explicitly passed
        if not api_key or not api_secret:
            load_dotenv()
            api_key = api_key or os.getenv("BINANCE_API_KEY")
            api_secret = api_secret or os.getenv("BINANCE_API_SECRET")
            
        self.api_key = api_key
        self.api_secret = api_secret
        self.client: Optional[Client] = None
        
        if not self.dry_run:
            if not self.api_key or not self.api_secret:
                raise ValidationError(
                    "Binance API credentials missing. Please set BINANCE_API_KEY and "
                    "BINANCE_API_SECRET in a .env file or run with --dry-run to test."
                )
            try:
                # Initialize python-binance client and direct to testnet
                self.client = Client(self.api_key, self.api_secret, testnet=True)
                # Override URL to guarantee it points to USDT-M Futures Testnet REST API endpoint
                self.client.FUTURES_URL = "https://testnet.binancefuture.com/fapi"
            except Exception as e:
                mapped_err = handle_binance_exception(e)
                logger.error(f"Client initialization failed: {mapped_err}")
                raise mapped_err
        else:
            logger.info("Initializing client in MOCK/DRY-RUN mode.")

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Place an order on Binance Futures Testnet.
        
        Returns:
            Dict: The parsed API response.
        Raises:
            TradingBotError: Mapped custom exception.
        """
        payload = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
            "price": price,
            "stopPrice": stop_price
        }
        
        # Log the request details cleanly (omit fields that are None)
        request_payload = {k: v for k, v in payload.items() if v is not None}
        logger.info(f"Sending order request: {request_payload}")
        
        if self.dry_run:
            return self._simulate_order_response(symbol, side, order_type, quantity, price, stop_price)
            
        try:
            params: Dict[str, Any] = {
                "symbol": symbol,
                "side": side,
                "quantity": quantity
            }
            
            # Map parameter differences for Futures endpoint
            if order_type == "MARKET":
                params["type"] = "MARKET"
            elif order_type == "LIMIT":
                params["type"] = "LIMIT"
                params["price"] = price
                params["timeInForce"] = "GTC"  # Good Till Cancelled
            elif order_type == "STOP_LIMIT":
                # For Futures REST API, STOP_LIMIT order is of type 'STOP'
                # and requires price and stopPrice.
                params["type"] = "STOP"
                params["price"] = price
                params["stopPrice"] = stop_price
                params["timeInForce"] = "GTC"
                
            response = self.client.futures_create_order(**params)
            logger.info(f"Received order response: {response}")
            return response
            
        except Exception as e:
            mapped_err = handle_binance_exception(e)
            logger.error(f"Order placement failed: {mapped_err}")
            raise mapped_err

    def _simulate_order_response(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """Simulate a successful order execution on Binance Futures Testnet."""
        # Add slight delay to simulate network call
        time.sleep(0.25)
        
        order_id = random.randint(10000000, 99999999)
        current_time_ms = int(time.time() * 1000)
        
        # Set execution characteristics based on type
        if order_type == "MARKET":
            status = "FILLED"
            executed_qty = quantity
            # Simulate a reasonable mid-market price
            avg_price = 61250.5 if "BTC" in symbol else (3350.2 if "ETH" in symbol else 1.25)
        else:
            # LIMIT and STOP_LIMIT orders are typically registered (NEW) but not filled immediately
            status = "NEW"
            executed_qty = 0.0
            avg_price = 0.0
            
        mock_response = {
            "orderId": order_id,
            "symbol": symbol,
            "status": status,
            "clientOrderId": f"mock_cli_{order_id}",
            "price": str(price) if price else "0.0",
            "avgPrice": str(avg_price),
            "origQty": str(quantity),
            "executedQty": str(executed_qty),
            "cumQty": str(executed_qty),
            "side": side,
            "type": "STOP" if order_type == "STOP_LIMIT" else order_type,
            "origType": order_type,
            "timeInForce": "GTC",
            "updateTime": current_time_ms
        }
        
        if stop_price is not None:
            mock_response["stopPrice"] = str(stop_price)
            
        logger.info(f"Received simulated order response: {mock_response}")
        return mock_response
