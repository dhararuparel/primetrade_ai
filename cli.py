"""
Command Line Interface for the Binance Futures trading bot.
Supports standard flags and interactive prompt fallback.
"""
import argparse
import sys
from typing import List, Optional
from rich.console import Console
from rich.prompt import Prompt, FloatPrompt, Confirm

from bot.orders import execute_order

console = Console()


def run_interactive() -> None:
    """Run the CLI in interactive prompt mode."""
    console.print()
    console.print("[bold yellow]⚡ PrimeTrade AI - Binance Futures Testnet Trading Bot[/]", justify="center")
    console.print("[dim]Interactive Order Wizard[/]", justify="center")
    console.print()
    
    symbol = Prompt.ask("[bold cyan]Enter Symbol[/] (e.g., BTCUSDT)").strip().upper()
    side = Prompt.ask("[bold cyan]Select Side[/]", choices=["BUY", "SELL"], default="BUY")
    order_type = Prompt.ask(
        "[bold cyan]Select Order Type[/]", 
        choices=["MARKET", "LIMIT", "STOP_LIMIT"], 
        default="MARKET"
    )
    
    quantity = FloatPrompt.ask("[bold cyan]Enter Quantity[/]")
    
    price = None
    if order_type in ("LIMIT", "STOP_LIMIT"):
        price = FloatPrompt.ask("[bold cyan]Enter Limit Price[/]")
        
    stop_price = None
    if order_type == "STOP_LIMIT":
        stop_price = FloatPrompt.ask("[bold cyan]Enter Stop Price[/]")
        
    dry_run = Confirm.ask("[bold magenta]Execute as dry-run / mock order?[/]", default=True)
    
    execute_order(
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price,
        stop_price=stop_price,
        dry_run=dry_run
    )


def main(args_list: Optional[List[str]] = None) -> None:
    """Parse CLI arguments and route to order execution."""
    parser = argparse.ArgumentParser(
        description="Binance Futures USDT-M Testnet CLI Trading Bot.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument("--symbol", type=str, help="Trading symbol (e.g., BTCUSDT)")
    parser.add_argument(
        "--side", 
        type=str, 
        choices=["BUY", "SELL", "buy", "sell"], 
        help="Order side (BUY/SELL)"
    )
    parser.add_argument(
        "--type", 
        type=str, 
        choices=["MARKET", "LIMIT", "STOP_LIMIT", "market", "limit", "stop_limit"], 
        help="Order type (MARKET/LIMIT/STOP_LIMIT)"
    )
    parser.add_argument("--quantity", type=float, help="Order quantity")
    parser.add_argument("--price", type=float, help="Limit price (Required for LIMIT/STOP_LIMIT)")
    parser.add_argument("--stop-price", type=float, help="Stop price (Required for STOP_LIMIT)")
    parser.add_argument("--dry-run", action="store_true", help="Execute order in mock/dry-run mode")
    parser.add_argument(
        "--interactive", "-i", 
        action="store_true", 
        help="Run in interactive wizard mode"
    )
    
    args = parser.parse_args(args_list)
    
    # Determine if CLI was run with no parameters whatsoever
    has_no_args = (
        args.symbol is None and
        args.side is None and
        args.type is None and
        args.quantity is None and
        args.price is None and
        args.stop_price is None and
        not args.dry_run
    )
    
    if args.interactive or has_no_args:
        run_interactive()
    else:
        # Perform initial sanity check on CLI inputs before passing to orchestrator
        missing = []
        if not args.symbol:
            missing.append("--symbol")
        if not args.side:
            missing.append("--side")
        if not args.type:
            missing.append("--type")
        if args.quantity is None:
            missing.append("--quantity")
            
        if missing:
            parser.print_usage()
            console.print(
                f"[bold red]Error: Missing required arguments: {', '.join(missing)}[/]"
            )
            console.print(
                "Run with [bold cyan]--interactive[/] or without arguments to use the interactive wizard."
            )
            sys.exit(1)
            
        execute_order(
            symbol=args.symbol,
            side=args.side,
            order_type=args.type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
            dry_run=args.dry_run
        )


if __name__ == "__main__":
    main()
