# Quotex Trading Bot

A Python-based Telegram bot that automates trading on Quotex using Selenium web scraping and technical analysis.

## Features

- Automated trading using SMA/RSI strategy
- 2% risk management per trade
- Real-time Telegram updates
- Admin controls and demo mode
- Screenshot proof of trades

## Project Structure

```
quotex_bot/
├── config/           # Configuration files
├── src/             # Source code
├── tests/           # Test files
└── main.py          # Entry point
```

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your credentials:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token
   QUOTEX_EMAIL=your_email
   QUOTEX_PASSWORD=your_password
   ```
4. Run the bot:
   ```bash
   python main.py
   ```

## Security Note

Never commit your `.env` file or expose your credentials. The `.env` file is included in `.gitignore` for security.

## License

MIT License # quot
# Karzheen
