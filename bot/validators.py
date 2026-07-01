"""
Input validation module for the Binance Futures trading bot.
"""
import re
from typing import Any, Dict, Optional
from bot.exceptions import ValidationError


def validate_symbol(symbol: Any) -> str:
    """Validate and normalize the trading symbol (e.g., BTCUSDT)."""
    if symbol is None or not str(symbol).strip():
        raise ValidationError("Symbol cannot be empty.")
    
    symbol_str = str(symbol).strip().upper()
    
    # Binance symbols are alphanumeric, typically 3 to 20 characters
    if not re.match(r'^[A-Z0-9]{3,20}$', symbol_str):
        raise ValidationError(
            f"Invalid symbol format: '{symbol}'. "
            "Must be alphanumeric and 3-20 characters long (e.g., BTCUSDT)."
        )
    return symbol_str


def validate_side(side: Any) -> str:
    """Validate and normalize the order side (BUY/SELL)."""
    if side is None or not str(side).strip():
        raise ValidationError("Order side cannot be empty.")
    
    side_str = str(side).strip().upper()
    if side_str not in ("BUY", "SELL"):
        raise ValidationError(f"Invalid order side: '{side}'. Must be 'BUY' or 'SELL'.")
    return side_str


def validate_order_type(order_type: Any) -> str:
    """Validate and normalize the order type (MARKET/LIMIT/STOP_LIMIT)."""
    if order_type is None or not str(order_type).strip():
        raise ValidationError("Order type cannot be empty.")
    
    type_str = str(order_type).strip().upper()
    if type_str not in ("MARKET", "LIMIT", "STOP_LIMIT"):
        raise ValidationError(
            f"Invalid order type: '{order_type}'. Must be 'MARKET', 'LIMIT', or 'STOP_LIMIT'."
        )
    return type_str


def validate_quantity(quantity: Any) -> float:
    """Validate and parse quantity to ensure it is a positive float."""
    if quantity is None:
        raise ValidationError("Quantity is required.")
    
    try:
        qty_float = float(quantity)
    except (ValueError, TypeError):
        raise ValidationError(f"Quantity must be a numeric value, got '{quantity}'.")
    
    if qty_float <= 0:
        raise ValidationError(f"Quantity must be positive. Got {qty_float}.")
    return qty_float


def validate_price(price: Any, order_type: str) -> Optional[float]:
    """Validate and parse price according to order type requirements."""
    if order_type in ("LIMIT", "STOP_LIMIT"):
        if price is None or str(price).strip() == "":
            raise ValidationError(f"Price is required for '{order_type}' orders.")
        
        try:
            price_float = float(price)
        except (ValueError, TypeError):
            raise ValidationError(f"Price must be a numeric value, got '{price}'.")
        
        if price_float <= 0:
            raise ValidationError(f"Price must be positive. Got {price_float}.")
        return price_float
    
    # For MARKET orders, ignore the price
    return None


def validate_stop_price(stop_price: Any, order_type: str) -> Optional[float]:
    """Validate and parse stop price for STOP_LIMIT orders."""
    if order_type == "STOP_LIMIT":
        if stop_price is None or str(stop_price).strip() == "":
            raise ValidationError("Stop price is required for 'STOP_LIMIT' orders.")
        
        try:
            stop_float = float(stop_price)
        except (ValueError, TypeError):
            raise ValidationError(f"Stop price must be a numeric value, got '{stop_price}'.")
        
        if stop_float <= 0:
            raise ValidationError(f"Stop price must be positive. Got {stop_float}.")
        return stop_float
    
    # For non-STOP_LIMIT orders, ignore the stop price
    return None


def validate_order_inputs(
    symbol: Any,
    side: Any,
    order_type: Any,
    quantity: Any,
    price: Any = None,
    stop_price: Any = None
) -> Dict[str, Any]:
    """
    Validate all trading bot parameters and return their normalized dictionary.
    
    Raises:
        ValidationError: If any of the inputs fail validation.
    """
    norm_type = validate_order_type(order_type)
    norm_symbol = validate_symbol(symbol)
    norm_side = validate_side(side)
    norm_qty = validate_quantity(quantity)
    norm_price = validate_price(price, norm_type)
    norm_stop_price = validate_stop_price(stop_price, norm_type)
    
    return {
        "symbol": norm_symbol,
        "side": norm_side,
        "type": norm_type,
        "quantity": norm_qty,
        "price": norm_price,
        "stop_price": norm_stop_price
    }
