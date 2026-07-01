"""
Order execution and formatting orchestrator.
"""
import datetime
from typing import Any, Dict, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from bot.exceptions import (
    TradingBotError,
    ValidationError,
    BinanceAPIError
)
from bot.validators import validate_order_inputs
from bot.client import BinanceFuturesClient
from bot.logging_config import logger

console = Console()


def execute_order(
    symbol: Any,
    side: Any,
    order_type: Any,
    quantity: Any,
    price: Any = None,
    stop_price: Any = None,
    api_key: Optional[str] = None,
    api_secret: Optional[str] = None,
    dry_run: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Validates the order parameters, prints request summaries, executes the placement
    on Binance Futures Testnet, and prints success or failure details to the console.
    """
    # 1. Validate Inputs
    try:
        validated = validate_order_inputs(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price
        )
    except ValidationError as e:
        logger.error(f"Validation failed: {e}")
        _print_failure_summary("Validation Error", str(e))
        return None

    # 2. Print Request Summary Dashboard
    _print_request_summary(validated)

    # 3. Create client and place order
    try:
        client = BinanceFuturesClient(
            api_key=api_key, 
            api_secret=api_secret, 
            dry_run=dry_run
        )
        
        response = client.place_order(
            symbol=validated["symbol"],
            side=validated["side"],
            order_type=validated["type"],
            quantity=validated["quantity"],
            price=validated["price"],
            stop_price=validated["stop_price"]
        )
        
        # 4. Display Execution Success Summary
        _print_success_summary(response)
        return response

    except ValidationError as e:
        # Catch validation failures during client init (e.g. missing API keys)
        logger.error(f"Initialization validation failed: {e}")
        _print_failure_summary("Validation Error", str(e))
        return None
    except BinanceAPIError as e:
        logger.error(f"Binance API returned error code {e.code}: {e}")
        _print_failure_summary("Binance API Error", str(e), api_error=f"API Code {e.code}")
        return None
    except TradingBotError as e:
        logger.error(f"Execution error: {e}")
        _print_failure_summary("Execution Error", str(e))
        return None
    except Exception as e:
        logger.exception("An unexpected error occurred during execution.")
        _print_failure_summary("Unexpected Error", str(e))
        return None


def _print_request_summary(data: Dict[str, Any]) -> None:
    """Print the order request details card."""
    # Terminal standard representation matching user requirement
    grid = Table.grid(expand=True)
    grid.add_column(style="bold yellow", justify="left")
    grid.add_column(style="white", justify="right")
    
    grid.add_row("Symbol:", data["symbol"])
    grid.add_row("Side:", f"[bold green]BUY[/]" if data["side"] == "BUY" else "[bold red]SELL[/]")
    grid.add_row("Type:", data["type"])
    grid.add_row("Quantity:", f"{data['quantity']}")
    
    if data["price"] is not None:
        grid.add_row("Price:", f"{data['price']:.4f}")
    if data["stop_price"] is not None:
        grid.add_row("Stop Price:", f"{data['stop_price']:.4f}")
        
    panel = Panel(
        grid,
        title="[bold yellow]Order Request[/]",
        subtitle="Ready for Transmission",
        expand=False,
        width=40
    )
    console.print()
    console.print(panel)
    console.print()


def _print_success_summary(res: Dict[str, Any]) -> None:
    """Print execution details on successful order placement."""
    order_id = res.get("orderId", "N/A")
    status = res.get("status", "N/A")
    executed_qty = res.get("executedQty", "0.0")
    avg_price = res.get("avgPrice", "0.0")
    
    # Convert millisecond timestamp to readable local time
    timestamp = res.get("updateTime")
    time_str = "N/A"
    if timestamp:
        try:
            dt = datetime.datetime.fromtimestamp(int(timestamp) / 1000, datetime.timezone.utc)
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        except Exception:
            time_str = str(timestamp)
            
    grid = Table.grid(expand=True)
    grid.add_column(style="bold cyan", justify="left")
    grid.add_column(style="white", justify="right")
    
    grid.add_row("Order ID:", str(order_id))
    grid.add_row("Status:", f"[bold green]{status}[/]" if status in ("FILLED", "NEW") else status)
    grid.add_row("Executed Quantity:", str(executed_qty))
    grid.add_row("Average Price:", str(avg_price))
    grid.add_row("Time:", time_str)
    
    panel = Panel(
        grid,
        title="[bold green]Order Successful[/]",
        expand=False,
        width=40,
        border_style="green"
    )
    console.print(panel)
    console.print()


def _print_failure_summary(err_type: str, reason: str, api_error: str = "N/A") -> None:
    """Print execution failure panel."""
    grid = Table.grid(expand=True)
    grid.add_column(style="bold red", justify="left")
    grid.add_column(style="white", justify="right")
    
    grid.add_row("Reason:", reason)
    
    if err_type == "Binance API Error":
        grid.add_row("API Error:", api_error)
    elif err_type == "Validation Error":
        grid.add_row("Validation Error:", reason)
        
    panel = Panel(
        grid,
        title=f"[bold red]Order Failed ({err_type})[/]",
        expand=False,
        width=50,
        border_style="red"
    )
    console.print()
    console.print(panel)
    console.print()
