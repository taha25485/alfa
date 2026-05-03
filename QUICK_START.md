# ALFA Bot - Quick Start (5 Minutes)

## Prerequisites Installed?
```bash
python3 --version      # Should be 3.9+
ffmpeg -version        # Should show version
git --version          # Should show version
```

If not, install:
- **Ubuntu**: `sudo apt-get install python3-pip ffmpeg git`
- **macOS**: `brew install python@3.11 ffmpeg git`

---

## 1. Clone / Download Files (2 min)

```bash
mkdir ~/alfa-bot && cd ~/alfa-bot

# Copy these files into ~/alfa-bot/:
# - alfabot_main.py
# - file_processor.py
# - encryption_manager.py
# - blockchain_manager.py
# - valuation_engine.py
# - config.py
# - requirements.txt
# - .env.example
```

---

## 2. Setup Environment (1 min)

```bash
# Create .env from template
cp .env.example .env

# Edit .env with your values
nano .env
```

**Minimum required in `.env`:**
```env
TELEGRAM_BOT_TOKEN=your_token_from_botfather
WEB3_PROVIDER_URL=https://mainnet.base.org
ALFA_CONTRACT_ADDRESS=0x...deployed_contract...
SIGNER_PRIVATE_KEY=0x...your_wallet_private_key...
```

---

## 3. Install Dependencies (1 min)

```bash
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

---

## 4. Create Contract ABI File (30 sec)

```bash
mkdir abi
```

Then create `abi/ALFA_Contract_ABI.json` with your contract's ABI from deployment.

---

## 5. Start Bot (30 sec)

```bash
python3 alfabot_main.py
```

**Success?** You'll see:
```
2024-01-15 10:30:45 - alfabot_main - INFO - Connected to network: 8453
2024-01-15 10:30:47 - encryption_manager - INFO - File processor initialized
2024-01-15 10:30:48 - alfabot_main - INFO - ALFA Telegram Bot starting...
```

---

## 6. Test in Telegram

1. Find your bot in Telegram (use name from BotFather)
2. Send `/start`
3. Send `/upload`
4. Upload a test video
5. Send wallet address: `0x742d35Cc6634C0532925a3b844Bc89e7595f42e6`
6. Send game name: `Elden Ring`

**Expected:** Bot processes file, calls contract, sends ALFA tokens to wallet!

---

## Common Issues

**"TELEGRAM_BOT_TOKEN not set"**
→ Check `.env` file exists and has your token

**"Cannot connect to network"**
→ Check internet connection and `WEB3_PROVIDER_URL`

**"FFmpeg not found"**
→ Install FFmpeg: `sudo apt-get install ffmpeg`

**"Private key not working"**
→ Make sure it starts with `0x` and has enough ETH for gas

**"Contract not found"**
→ Check `ALFA_CONTRACT_ADDRESS` is correct and on Base network

---

## Next: Production Deployment

Once testing works, use systemd or Docker:

```bash
# See TELEGRAM_BOT_SETUP.md for production guide
cat TELEGRAM_BOT_SETUP.md
```

---

## File Structure

```
alfa-bot/
├── alfabot_main.py           # Main bot logic
├── file_processor.py         # FFmpeg/metadata handling
├── encryption_manager.py     # AES-256-CBC + hashing
├── blockchain_manager.py     # Web3 contract calls
├── valuation_engine.py       # Content scoring
├── config.py                 # Configuration
├── requirements.txt          # Python dependencies
├── .env                      # Your secrets (⚠️ don't commit!)
├── .env.example              # Template
├── venv/                     # Virtual environment
├── logs/                     # Bot logs
├── abi/
│   └── ALFA_Contract_ABI.json # Contract ABI
└── README.md                 # This file
```

---

## Commands Available

| Command | What it does |
|---------|------------|
| `/start` | Welcome message |
| `/upload` | Start content upload |
| `/status` | Check contract status |
| `/help` | Show all commands |
| `/cancel` | Cancel current upload |

---

## What Happens Behind the Scenes

```
User sends video
    ↓
Bot downloads & validates
    ↓
Bot extracts metadata (duration, resolution, codec)
    ↓
Bot hashes original (SHA256) → SHA384 → SHA512
    ↓
Bot converts to MKV (preserves quality, smaller)
    ↓
Bot encrypts with AES-256-CBC → new hash
    ↓
Valuation Engine scores content (0-1000)
    ↓
Bot calls Smart Contract:
  • registerContentUpload() → mints ALFA tokens
  • encrypt() → stores encryption metadata
    ↓
Tokens arrive in user's wallet (1-2 min)
    ↓
Encrypted file → Google Drive (if enabled)
    ↓
NFT created with ALFA token + metadata
```

---

## Monitoring

```bash
# Watch logs in real-time
tail -f logs/logs.txt

# Check bot status
curl https://api.telegram.org/botYOUR_TOKEN/getMe

# Monitor transactions
# https://basescan.io/address/YOUR_BOT_ADDRESS
```

---

## Security Reminders

⚠️ **IMPORTANT:**
- Never commit `.env` to GitHub
- Keep `SIGNER_PRIVATE_KEY` secret
- Fund bot wallet with only what's needed
- Rotate keys monthly

---

## Support

1. Check `logs/logs.txt` for errors
2. Verify all `.env` values
3. See `TELEGRAM_BOT_SETUP.md` for detailed guide
4. Test contract connection separately

---

**Ready?** → `python3 alfabot_main.py` 🚀
