# ALFA Telegram Bot - Setup & Deployment Guide

## Overview

The ALFA Telegram bot is the first point of contact for content creators. It:

1. ✅ Accepts video uploads
2. ✅ Extracts metadata (duration, resolution, codec, file size)
3. ✅ Hashes files (SHA256 original, SHA512 encrypted)
4. ✅ Converts to MKV format
5. ✅ Encrypts with AES-256-CBC
6. ✅ Valuates content (0-1000 score)
7. ✅ Registers on ALFA contract
8. ✅ Distributes ALFA tokens to creator wallet

---

## System Requirements

### Operating System
- Ubuntu 20.04+ / Debian 11+
- macOS 11+
- Windows 10+ (with WSL2)

### Software Dependencies
```bash
# Python 3.9+
python3 --version

# FFmpeg (for video processing)
ffmpeg -version
ffprobe -version

# Git (for cloning)
git --version
```

---

## Installation Steps

### 1. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv ffmpeg git
```

**macOS:**
```bash
brew install python@3.11 ffmpeg git
```

**Windows (WSL2):**
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv ffmpeg git
```

### 2. Clone or Download Bot Files

```bash
# Create project directory
mkdir -p ~/projects/alfa-bot
cd ~/projects/alfa-bot

# Copy bot files here
# alfabot_main.py
# file_processor.py
# encryption_manager.py
# blockchain_manager.py
# valuation_engine.py
# config.py
# requirements.txt
```

### 3. Create Python Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## Configuration

### 1. Create `.env` File

```bash
cp .env.example .env
```

Or create `.env` manually:

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE

# Base Network (RPC Provider)
WEB3_PROVIDER_URL=https://mainnet.base.org

# ALFA Contract (deployed from Solidity contract)
ALFA_CONTRACT_ADDRESS=0xYourALFAContractAddressHere

# Contract ABI path
CONTRACT_ABI_PATH=abi/ALFA_Contract_ABI.json

# Bot's private key (for signing transactions)
# THIS MUST HAVE ETH BALANCE TO PAY FOR GAS
SIGNER_PRIVATE_KEY=0xYourPrivateKeyHere

# Google Drive (optional, for storing encrypted files)
GOOGLE_DRIVE_CREDENTIALS_PATH=/path/to/credentials.json
GOOGLE_DRIVE_FOLDER_ID=YourGoogleDriveFolderID

# Logging
LOG_LEVEL=INFO
```

### 2. Get Telegram Bot Token

1. Open Telegram and find **@BotFather**
2. Send `/newbot`
3. Follow instructions to create bot
4. Copy the **API token**
5. Add to `.env` file

### 3. Deploy ALFA Contract

1. Deploy `ALFA_Token_Contract.sol` to Base network
2. Use Hardhat or Remix IDE
3. Copy contract address to `.env`

### 4. Create Bot Wallet

```bash
# Generate new Ethereum wallet for bot signer
# Use MetaMask or command line:

python3 << 'EOF'
from eth_account import Account
account = Account.create()
print(f"Address: {account.address}")
print(f"Private Key: {account._private_key.hex()}")
EOF
```

**Add funds to this wallet!** It needs ETH to pay gas for:
- Registering content uploads
- Storing encryption metadata
- Typical cost: $2-10 per transaction on Base

### 5. Extract Contract ABI

After deploying contract, extract the ABI:

```bash
mkdir -p abi
# Paste contract ABI from deployment into:
# abi/ALFA_Contract_ABI.json
```

**Example ABI structure** (minimal):
```json
[
  {
    "inputs": [...],
    "name": "registerContentUpload",
    "outputs": [...],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [...],
    "name": "encrypt",
    "outputs": [...],
    "stateMutability": "nonpayable",
    "type": "function"
  }
]
```

### 6. Authorize Bot on Contract

Once contract is deployed, call:

```python
# From contract owner wallet
contract.authorizeValuationBot("0xBotWalletAddress")
```

---

## Running the Bot

### Local Development

```bash
# Activate virtual environment
source venv/bin/activate

# Start bot
python3 alfabot_main.py
```

**Expected output:**
```
2024-01-15 10:30:45 - alfabot_main - INFO - ALFA Telegram Bot starting...
2024-01-15 10:30:46 - blockchain_manager - INFO - Connected to network: 8453
2024-01-15 10:30:47 - encryption_manager - INFO - File processor initialized
```

Bot is now live! Message it in Telegram.

### Production Deployment

#### Option A: systemd Service

```bash
sudo nano /etc/systemd/system/alfa-bot.service
```

```ini
[Unit]
Description=ALFA Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/projects/alfa-bot
Environment="PATH=/home/ubuntu/projects/alfa-bot/venv/bin"
ExecStart=/home/ubuntu/projects/alfa-bot/venv/bin/python3 alfabot_main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable alfa-bot
sudo systemctl start alfa-bot
sudo systemctl status alfa-bot
```

#### Option B: Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create directories
RUN mkdir -p logs /tmp/alfa_uploads abi

CMD ["python3", "alfabot_main.py"]
```

Build and run:

```bash
docker build -t alfa-bot .
docker run -d \
  --name alfa-bot \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/abi:/app/abi \
  alfa-bot
```

#### Option C: Screen / tmux

```bash
# Using tmux (recommended)
tmux new-session -d -s alfa-bot
tmux send-keys -t alfa-bot "cd ~/projects/alfa-bot && source venv/bin/activate && python3 alfabot_main.py" Enter

# Check status
tmux list-sessions
tmux attach -t alfa-bot
```

---

## Bot Workflow

### User Uploads Content

```
User: /upload
Bot: "Send a video file"

User: [sends video.mp4]
Bot: "Processing..." → extracts metadata → hashes original

Bot: "Now send wallet address"
User: 0x742d35Cc6634C0532925a3b844Bc89e7595f42e6

Bot: "What's the game name?"
User: Elden Ring

Bot: [Converts to MKV, encrypts, valuates, calls contract]
Bot: "✅ 850,000 ALFA sent to wallet!"
```

---

## Monitoring & Troubleshooting

### View Bot Logs

```bash
tail -f logs/logs.txt
```

### Common Issues

**Issue: FFmpeg not found**
```bash
# Solution: Install FFmpeg
sudo apt-get install ffmpeg
```

**Issue: Private key not working**
```bash
# Solution: Check format (with or without 0x prefix)
# Both valid:
SIGNER_PRIVATE_KEY=0x123abc...
SIGNER_PRIVATE_KEY=123abc...
```

**Issue: Bot can't connect to contract**
```bash
# Solution: Verify configuration
python3 << 'EOF'
from config import Config
Config.validate()
print("Configuration OK")
EOF
```

**Issue: Insufficient gas**
```bash
# Solution: Add more ETH to bot signer wallet
# Check balance: https://basescan.io/address/0xBotAddress
```

**Issue: Bot stops responding**
```bash
# Solution: Restart bot
systemctl restart alfa-bot
# Or kill process
pkill -f alfabot_main
```

---

## Testing

### Test Video Upload (Local)

Create test video:
```bash
ffmpeg -f lavfi -i testsrc=size=640x480:duration=10 -pix_fmt yuv420p test.mp4
```

### Verify Encryption

```python
from encryption_manager import EncryptionManager

em = EncryptionManager()

# Encrypt
key, iv = em.encrypt_file("test.mp4", "test.mp4.encrypted")

# Verify
hash_orig = em.hash_file("test.mp4", "sha256")
hash_enc = em.hash_file("test.mp4.encrypted", "sha512")

print(f"Original: {hash_orig}")
print(f"Encrypted: {hash_enc}")
```

### Test Blockchain Connection

```python
from blockchain_manager import BlockchainManager

bm = BlockchainManager(
    provider_url="https://mainnet.base.org",
    contract_address="0x...",
    abi_path="abi/ALFA_Contract_ABI.json"
)

status = bm.get_contract_status()
print(status)
```

---

## Security Best Practices

1. **Never commit `.env` to git**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Rotate private keys regularly**
   - Generate new wallet monthly
   - Transfer unused tokens

3. **Use environment variables in production**
   ```bash
   export TELEGRAM_BOT_TOKEN="..."
   export SIGNER_PRIVATE_KEY="..."
   ```

4. **Enable 2FA on all accounts**
   - Telegram account
   - GitHub (where you store code)
   - Exchange account (if holding tokens)

5. **Monitor gas costs**
   ```bash
   # Check recent transactions
   # https://basescan.io/address/0xBotAddress
   ```

6. **Backup encryption keys**
   - Store encrypted backup of signer private key
   - Keep offline copy in safe place

---

## Scaling & Performance

### Database (for session tracking)

Currently uses JSON files. For production, upgrade to:

```python
# postgresql
pip install psycopg2-binary

# mongodb
pip install pymongo

# redis (caching)
pip install redis
```

### Rate Limiting

Add to protect against abuse:

```python
from telegram.ext import Application
app = Application.builder().token(token).build()
app.rate_limiter = RateLimiter(1)  # 1 request per user per second
```

### Load Balancing

For multiple bot instances:

```bash
# Use Nginx as reverse proxy
# Route requests across multiple bot processes
```

---

## Maintenance

### Weekly
- Check bot logs for errors
- Verify contract balance
- Monitor gas prices

### Monthly
- Backup user records
- Rotate API keys
- Update game database

### Quarterly
- Security audit
- Performance optimization
- Update dependencies: `pip install -U -r requirements.txt`

---

## Support & Contact

For issues:
1. Check logs: `tail -f logs/logs.txt`
2. Verify configuration: `grep "ALFA_CONTRACT_ADDRESS" .env`
3. Test blockchain: Run test script above
4. Check Telegram documentation

---

## Next Steps

1. ✅ Deploy Solidity contract (DONE)
2. ✅ Setup Telegram bot (THIS GUIDE)
3. ⏳ Integrate Google Drive storage
4. ⏳ Create NFT minting system
5. ⏳ Deploy to Base App
6. ⏳ Monitor and optimize
