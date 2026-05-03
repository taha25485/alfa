# ALFA Bot on RHEL - Quick Start (10 Minutes)

Perfect for Red Hat Enterprise Linux, AlmaLinux, Rocky Linux, or CentOS Stream.

---

## Pre-Check: You Have RHEL?

```bash
cat /etc/os-release | grep -E "^NAME|^VERSION"
# Should show: Red Hat Enterprise Linux 8/9, AlmaLinux, or Rocky
```

---

## 1. Update System (2 min)

```bash
sudo dnf update -y
```

---

## 2. Install Dependencies (3 min)

**FFmpeg (from EPEL repo):**
```bash
sudo dnf install epel-release -y
sudo dnf install ffmpeg ffmpeg-devel -y
```

**Python & dev tools:**
```bash
sudo dnf install python3 python3-pip python3-devel git gcc -y
```

**Verify:**
```bash
python3 --version  # Should be 3.8+
ffmpeg -version    # Should show version
```

---

## 3. Setup Bot (3 min)

```bash
# Create directory
mkdir -p ~/projects/alfa-bot && cd ~/projects/alfa-bot

# Copy all .py files here
# (alfabot_main.py, file_processor.py, encryption_manager.py, etc.)

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

---

## 4. Configure .env (2 min)

```bash
cp .env.example .env
nano .env
```

**Add these values:**
```env
TELEGRAM_BOT_TOKEN=your_token_from_botfather
WEB3_PROVIDER_URL=https://mainnet.base.org
ALFA_CONTRACT_ADDRESS=0x...your_contract_address...
SIGNER_PRIVATE_KEY=0x...your_wallet_private_key...
```

---

## 5. Test Bot (1 min)

```bash
source venv/bin/activate
python3 alfabot_main.py
```

**Should show:**
```
2024-01-15 10:30:45 - alfabot_main - INFO - Connected to network: 8453
2024-01-15 10:30:47 - encryption_manager - INFO - File processor initialized
2024-01-15 10:30:48 - alfabot_main - INFO - ALFA Telegram Bot starting...
```

Test in Telegram: `/start` → `/upload` → test video

---

## 6. Run in Background (systemd)

```bash
# Create service file
sudo nano /etc/systemd/system/alfa-bot.service
```

**Paste:**
```ini
[Unit]
Description=ALFA Telegram Bot
After=network-online.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/projects/alfa-bot
ExecStart=/home/$USER/projects/alfa-bot/venv/bin/python3 alfabot_main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Replace `$USER` with your username!**

```bash
# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable alfa-bot
sudo systemctl start alfa-bot

# Check status
sudo systemctl status alfa-bot

# View logs
sudo journalctl -u alfa-bot -f
```

---

## Troubleshooting on RHEL

### FFmpeg not found?
```bash
sudo dnf install epel-release -y
sudo dnf install ffmpeg -y
```

### Python module error?
```bash
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Service won't start?
```bash
# Check syntax
sudo systemctl status alfa-bot

# View error logs
sudo journalctl -u alfa-bot -n 50

# Check permissions
ls -la ~/projects/alfa-bot/
```

---

## RHEL Commands Reference

| Task | Command |
|------|---------|
| Update system | `sudo dnf update -y` |
| Install package | `sudo dnf install package-name -y` |
| Search package | `dnf search package-name` |
| Service status | `sudo systemctl status alfa-bot` |
| View logs | `sudo journalctl -u alfa-bot -f` |
| Restart bot | `sudo systemctl restart alfa-bot` |
| Stop bot | `sudo systemctl stop alfa-bot` |
| Enable on boot | `sudo systemctl enable alfa-bot` |

---

## File Locations on RHEL

```
Your bot:        ~/projects/alfa-bot/
Python venv:     ~/projects/alfa-bot/venv/
Config:          ~/projects/alfa-bot/.env
Logs:            ~/projects/alfa-bot/logs/
Uploads:         /tmp/alfa_uploads/
Contract ABI:    ~/projects/alfa-bot/abi/
```

---

## Check Everything Works

```bash
# Activate venv
source ~/projects/alfa-bot/venv/bin/activate

# Test Telegram
python3 -c "import telegram; print('✓ Telegram')"

# Test Web3
python3 -c "from web3 import Web3; print('✓ Web3')"

# Test crypto
python3 -c "from cryptography.hazmat.primitives.ciphers import Cipher; print('✓ Crypto')"

# Test FFmpeg
ffmpeg -version | head -1
```

---

## Monitor Running Bot

```bash
# If using systemd
sudo journalctl -u alfa-bot -f

# If running directly
tail -f ~/projects/alfa-bot/logs/logs.txt

# Check CPU/Memory
top -p $(pgrep -f alfabot_main)
```

---

## Deploy to Production

For 24/7 reliability:

**Option 1: systemd (Recommended)**
```bash
# Already setup above!
sudo systemctl status alfa-bot
```

**Option 2: Docker**
```bash
sudo dnf install docker-ce -y
sudo systemctl start docker
docker build -t alfa-bot .
docker run -d --name alfa-bot --env-file .env --restart unless-stopped alfa-bot
```

**Option 3: Screen**
```bash
screen -S alfa-bot
cd ~/projects/alfa-bot
source venv/bin/activate
python3 alfabot_main.py
# Ctrl+A then D to detach
# screen -r alfa-bot to reattach
```

---

## Verify Contract Connection

```bash
python3 << 'EOF'
from blockchain_manager import BlockchainManager
try:
    bm = BlockchainManager(
        provider_url="https://mainnet.base.org",
        contract_address="0x...",
        abi_path="abi/ALFA_Contract_ABI.json"
    )
    status = bm.get_contract_status()
    print(f"✓ Contract connected: {status}")
except Exception as e:
    print(f"✗ Error: {e}")
EOF
```

---

## Next Steps

1. ✅ Follow steps 1-6 above
2. ✅ Bot running as systemd service
3. ✅ Upload test video in Telegram
4. ✅ Verify tokens received in wallet

**For detailed RHEL guide:** See `RHEL_DEPLOYMENT_GUIDE.md`

---

## Get Help

```bash
# View last 20 log lines
sudo journalctl -u alfa-bot -n 20

# Check bot is running
ps aux | grep python3 | grep alfabot

# Restart if issues
sudo systemctl restart alfa-bot
```

---

**Ready?** You're running ALFA on RHEL! 🚀
