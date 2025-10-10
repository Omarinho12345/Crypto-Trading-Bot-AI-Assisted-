# Crypto Trading Bot (Simulated)
## What you get
- `bot.py` - the main script (simulated trading mode + Telegram notifications)
- `.env.example` - example of the .env file (do NOT commit the real .env)
- `.gitignore` - configured to ignore .env and trade CSV
- `requirements.txt` - Python dependencies
- `README.md` - this file

## Setup
1. Create a Python virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # on mac/linux
   venv\Scripts\activate   # on windows
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and paste your real credentials:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and replace the placeholders with your TELEGRAM_TOKEN and TELEGRAM_CHAT_ID.
4. Run the bot:
   ```bash
   python bot.py
   ```
## Security notes
- NEVER commit the real `.env` file to GitHub.
- If your token was previously exposed, **regenerate** it with BotFather and update `.env`.
