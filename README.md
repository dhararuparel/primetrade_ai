# ⚡ PrimeTrade AI - Binance Futures Testnet Trading Bot

A clean, production-grade CLI trading bot for placing orders on the Binance Futures Testnet (USDT-M) using Python. Built with reusable modules, thorough validation, custom exception mapping, comprehensive logging, and high-fidelity terminal formatting.

---

## 🌟 Features

- **Order Types**: Supports `MARKET`, `LIMIT`, and `STOP_LIMIT` (Bonus Feature) order types.
- **Order Sides**: Supports `BUY` and `SELL`.
- **Validation**: Strict validation rules for symbol format, order side, type, positive quantities, and conditional requirements (e.g., price for `LIMIT`, price & stop-price for `STOP_LIMIT`).
- **Interactive Wizard** (Bonus Feature): Launches a guided, interactive wizard if the bot is run without arguments or with `--interactive` / `-i`.
- **Rich Terminal Formatting** (Bonus Feature): Renders beautiful order summaries, success checkmarks, and error cards using the `rich` library.
- **Error Mapping**: Translates raw exchange or connection exceptions into typed local exceptions (`AuthenticationError`, `InsufficientBalanceError`, `NetworkError`).
- **Dry-run / Mock Execution**: Supports `--dry-run` mode to safely simulate trading requests without keys or risking real capital.

---

## 📂 Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py        # Binance API wrapper & exception mapper
│   ├── orders.py        # Order executor and UI reporting
│   ├── validators.py    # CLI and API parameter validation
│   ├── exceptions.py    # Custom exception classes
│   └── logging_config.py# Logger setup for writing to logs/trading.log
├── logs/
│   └── trading.log      # Log file output
├── cli.py               # Argument parser and interactive CLI entrypoint
├── .env.example         # Sample environment file
├── README.md            # Project documentation
├── requirements.txt     # Dependency list
└── .gitignore           # Git ignore patterns
```

---

## 🛠️ Installation

1. **Navigate to the trading bot directory**:
   ```bash
   cd trading_bot
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - **Windows PowerShell**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **Windows Command Prompt (cmd)**:
     ```cmd
     .\venv\Scripts\activate.bat
     ```
   - **macOS / Linux**:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🔑 Environment Variables

To execute real orders on the Testnet, configure your credentials in a `.env` file. 

Copy the example template:
```bash
cp .env.example .env
```

Edit the `.env` file to contain your Binance Futures Testnet API Key and Secret:
```env
BINANCE_API_KEY=your_futures_testnet_api_key_here
BINANCE_API_SECRET=your_futures_testnet_api_secret_here
```

*Note: If no credentials are set, execution will raise a `ValidationError` unless you execute with the `--dry-run` / `--mock` flag.*

---

## 🚀 Usage

### 1. Market Orders
Places a market order. Executed immediately at current market price.
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01 --dry-run
```

### 2. Limit Orders
Places a limit order. Requires `--price`.
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 62500 --dry-run
```

### 3. Stop-Limit Orders
Places a stop-limit order. Requires both `--price` and `--stop-price`.
```bash
python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT --quantity 0.05 --price 63000 --stop-price 62900 --dry-run
```

### 4. Interactive Wizard Mode
If you run the CLI without parameters, it automatically prompts you step-by-step:
```bash
python cli.py
```
Or force interactive wizard mode explicitly:
```bash
python cli.py --interactive
```

---

## 📝 Logging

All requests, raw responses, validation failures, and exchange/network errors are logged to `logs/trading.log`. 

The logs use a clean, standardized format:
```
[2026-07-01 16:15:32] [INFO] [trading_bot] Sending order request: {'symbol': 'BTCUSDT', 'side': 'BUY', 'type': 'MARKET', 'quantity': 0.01}
[2026-07-01 16:15:33] [INFO] [trading_bot] Received simulated order response: {'orderId': 31057492, 'symbol': 'BTCUSDT', 'status': 'FILLED', ...}
```

---

## ⚠️ Assumptions

1. **Target Account type**: The bot trades on Binance **USDT-Margin Futures Testnet**.
2. **Order Lifetime (Time In Force)**: All limit and stop-limit orders default to `GTC` (Good Till Cancelled).
3. **Quantity Precision**: Quantity and price formatting should conform to exchange specifications (Lot Size / Tick Size) for the target symbol. (The exchange returns an API error if the quantity or price steps are incorrect. This is mapped and displayed gracefully).
4. **Dry Run**: In `--dry-run` mode, prices are simulated based on the symbol (e.g., ~$61,250 for BTCUSDT).
