"""
FastAPI application to serve the Web UI and handle order endpoints.
"""
import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from bot.validators import validate_order_inputs
from bot.client import BinanceFuturesClient
from bot.exceptions import TradingBotError, ValidationError, BinanceAPIError
from bot.logging_config import logger

app = FastAPI(
    title="PrimeTrade AI - Trading Bot API",
    description="Backend API for managing Binance Futures orders and logs."
)


class OrderRequest(BaseModel):
    """Pydantic model representing a trade order request."""
    symbol: str = Field(..., description="Trading symbol, e.g., BTCUSDT")
    side: str = Field(..., description="Order side: BUY or SELL")
    type: str = Field(..., description="Order type: MARKET, LIMIT, or STOP_LIMIT")
    quantity: float = Field(..., description="Order quantity")
    price: Optional[float] = Field(None, description="Limit price (Required for LIMIT/STOP_LIMIT)")
    stop_price: Optional[float] = Field(None, description="Stop price (Required for STOP_LIMIT)")
    dry_run: bool = Field(True, description="Simulation or mock execution flag")


@app.post("/api/order")
def place_new_order(req: OrderRequest):
    """Validate and execute a Binance Futures Testnet order."""
    try:
        # Validate inputs using our modular validators
        validated = validate_order_inputs(
            symbol=req.symbol,
            side=req.side,
            order_type=req.type,
            quantity=req.quantity,
            price=req.price,
            stop_price=req.stop_price
        )
    except ValidationError as e:
        logger.error(f"Web API - Validation error: {e.message}")
        raise HTTPException(
            status_code=400, 
            detail={"error_type": "Validation Error", "message": e.message}
        )
        
    try:
        # Initialize client (mock or real) and submit order
        client = BinanceFuturesClient(dry_run=req.dry_run)
        response = client.place_order(
            symbol=validated["symbol"],
            side=validated["side"],
            order_type=validated["type"],
            quantity=validated["quantity"],
            price=validated["price"],
            stop_price=validated["stop_price"]
        )
        return response
        
    except ValidationError as e:
        logger.error(f"Web API - Client validation error: {e.message}")
        raise HTTPException(
            status_code=400, 
            detail={"error_type": "Validation Error", "message": e.message}
        )
    except BinanceAPIError as e:
        logger.error(f"Web API - Binance API error (code: {e.code}): {e.message}")
        raise HTTPException(
            status_code=400, 
            detail={"error_type": "Binance API Error", "message": e.message, "code": e.code}
        )
    except TradingBotError as e:
        logger.error(f"Web API - Trading bot error: {e.message}")
        raise HTTPException(
            status_code=500, 
            detail={"error_type": "Execution Error", "message": e.message}
        )
    except Exception as e:
        logger.exception("Web API - Unexpected internal exception occurred.")
        raise HTTPException(
            status_code=500, 
            detail={"error_type": "Internal Error", "message": str(e)}
        )


@app.get("/api/logs")
def get_recent_logs():
    """Retrieve the last 50 log statements from the log file."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(base_dir, "logs", "trading.log")
    
    if not os.path.exists(log_file):
        return {"logs": ["Log file not initialized yet. Place an order first."]}
        
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        # Return the last 50 lines without newline characters
        log_lines = [line.rstrip("\n") for line in lines[-50:]]
        return {"logs": log_lines}
    except Exception as e:
        logger.error(f"Web API - Error reading logs file: {e}")
        return {"logs": [f"Error reading logs file: {e}"]}


# Ensure static directory exists
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)

# Mount the static site path (Must be mounted last to prevent hijacking api routes)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("PrimeTrade AI Web UI starting at: http://127.0.0.1:8000")
    print("="*60 + "\n")
    uvicorn.run("web_app:app", host="127.0.0.1", port=8000, reload=True)
