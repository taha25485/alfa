# Local Telegram Bot API Setup (Ubuntu)

This removes Telegram's 20MB file size limit by running the Bot API server locally on your machine.

---

## Prerequisites

```bash
# Check Ubuntu version
lsb_release -a  # Should be 18.04+

# Install build tools
sudo apt-get update
sudo apt-get install -y build-essential cmake git zlib1g-dev openssl libssl-dev
```

---

## Step 1: Clone Telegram Bot API

```bash
cd ~
git clone --recursive https://github.com/tdlib/telegram-bot-api.git
cd telegram-bot-api
mkdir build
cd build
```

---

## Step 2: Build

```bash
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local ..
cmake --build . --target install
```

This takes **5-15 minutes**. Be patient.

---

## Step 3: Verify Installation

```bash
which telegram-bot-api
telegram-bot-api --version
```

Should show version info.

---

## Step 4: Run Bot API Server

### Option A: Foreground (for testing)

```bash
telegram-bot-api --api-id=YOUR_API_ID --api-hash=YOUR_API_HASH
```

### Option B: Background (systemd service)

```bash
sudo nano /etc/systemd/system/telegram-bot-api.service
```

Paste:

```ini
[Unit]
Description=Telegram Bot API Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu
ExecStart=/usr/local/bin/telegram-bot-api --api-id=YOUR_API_ID --api-hash=YOUR_API_HASH --local
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot-api
sudo systemctl start telegram-bot-api
sudo systemctl status telegram-bot-api
```

---

## Get Your API ID & Hash

1. Go to https://my.telegram.org
2. Login with your phone number
3. Click "API development tools"
4. Create new application
5. Copy **api_id** and **api_hash**

Replace `YOUR_API_ID` and `YOUR_API_HASH` above.

---

## Step 5: Update Bot to Use Local Server

Edit `.env`:

```bash
nano ~/alfa-bot/.env
```

Change:

```env
# Old (Telegram cloud)
# TELEGRAM_BOT_API_URL=https://api.telegram.org

# New (local server)
TELEGRAM_BOT_API_URL=http://127.0.0.1:8081
```

---

## Step 6: Test Local Server

Check if running:

```bash
curl http://127.0.0.1:8081/getMe
```

Should return bot info (JSON).

---

## Step 7: Restart Bot

```bash
cd ~/alfa-bot
python3 alfabot_main.py
```

Bot now uses **local server** = **no file size limits!** 🚀

---

## File Size Limits After Local Setup

- Cloud API: 20MB limit
- Local API: **2GB limit** (your machine's storage)

---

## Troubleshooting

### "Command not found: telegram-bot-api"

```bash
# Add to PATH
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### "Permission denied"

```bash
sudo chmod +x /usr/local/bin/telegram-bot-api
```

### "Port 8081 already in use"

```bash
# Use different port
telegram-bot-api --api-id=123 --api-hash=abc --http-port=8082

# Update .env
TELEGRAM_BOT_API_URL=http://127.0.0.1:8082
```

### Server won't start

```bash
# Check logs
sudo journalctl -u telegram-bot-api -f

# Or run in foreground to see errors
telegram-bot-api --api-id=YOUR_API_ID --api-hash=YOUR_API_HASH
```

---

## Verify It Works

Upload a **large video** (>20MB) to your bot in Telegram:

1. `/upload`
2. Upload large file
3. Should work now! ✅

---

## Keep Running 24/7

Make sure systemd service is enabled:

```bash
sudo systemctl status telegram-bot-api
```

Should show **active (running)**.

If you reboot, it auto-restarts.

---

## Next: Mainnet Deployment

Once verified locally, we'll deploy to **Base mainnet** and **set up NFT minting**!

---

**Status:** Local Bot API ready to deploy! 🚀
