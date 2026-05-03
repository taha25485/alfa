# ALFA Telegram Bot - Red Hat Enterprise Linux Deployment Guide

## Overview

This guide is specifically for **Red Hat Enterprise Linux (RHEL) 8+** including:
- Red Hat Enterprise Linux 8.x
- Red Hat Enterprise Linux 9.x
- AlmaLinux 8.x / 9.x
- Rocky Linux 8.x / 9.x
- CentOS 8 Stream / 9 Stream

---

## System Requirements

### Minimum
- RHEL 8.0 or later
- 2 CPU cores
- 4GB RAM
- 20GB disk space

### Check Your System
```bash
# Check RHEL version
cat /etc/os-release

# Check architecture
uname -m  # Should be x86_64 or aarch64

# Check kernel
uname -r
```

---

## Installation Steps (RHEL-Specific)

### 1. Update System

```bash
# Update all packages
sudo dnf update -y

# Or if using yum (older RHEL 8)
sudo yum update -y
```

### 2. Install Python 3.9+ (RHEL Native)

RHEL 8/9 comes with Python 3.8/3.9 by default. Verify:

```bash
python3 --version  # Should be 3.8+ minimum
```

If you need Python 3.11+:

```bash
# Enable PowerTools/CRB repository (contains newer Python)
# For RHEL 8:
sudo subscription-manager repos --enable codeready-builder-for-rhel-8-$(arch)-rpms

# For RHEL 9:
sudo subscription-manager repos --enable codeready-builder-for-rhel-9-$(arch)-rpms

# Or if using community repos (AlmaLinux/Rocky):
sudo dnf install dnf-plugins-core
sudo dnf config-manager --set-enabled powertools  # AlmaLinux/Rocky 8
sudo dnf config-manager --set-enabled crb        # AlmaLinux/Rocky 9

# Install Python 3.11
sudo dnf install python3.11 python3.11-devel python3.11-pip -y
```

### 3. Install FFmpeg (RHEL Requires EPEL Repo)

RHEL doesn't include FFmpeg in main repos. Use EPEL:

```bash
# Install EPEL repository
sudo dnf install epel-release -y

# Install FFmpeg and tools
sudo dnf install ffmpeg ffmpeg-devel -y

# Verify installation
ffmpeg -version
ffprobe -version
```

**If EPEL doesn't work**, build from source:

```bash
# Install build tools
sudo dnf groupinstall "Development Tools" -y
sudo dnf install yasm nasm libass-devel opus-devel -y

# Clone FFmpeg
cd /tmp
git clone https://git.ffmpeg.org/ffmpeg.git ffmpeg
cd ffmpeg

# Configure and build
./configure --prefix=/usr/local --enable-gpl --enable-libass --enable-libopus
make -j$(nproc)
sudo make install

# Add to path
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify
ffmpeg -version
```

### 4. Install System Dependencies

```bash
# Required development packages
sudo dnf install git gcc g++ make libffi-devel openssl-devel -y

# For crypto libraries
sudo dnf install libssl-devel -y

# For video processing
sudo dnf install libx264-devel libx265-devel -y
```

### 5. Create Project Directory

```bash
# Create as regular user (not root)
mkdir -p ~/projects/alfa-bot
cd ~/projects/alfa-bot

# Copy all bot files here:
# alfabot_main.py
# file_processor.py
# encryption_manager.py
# blockchain_manager.py
# valuation_engine.py
# config.py
# requirements.txt
# .env.example
```

### 6. Create Python Virtual Environment

```bash
# Using Python 3.11 (if installed)
python3.11 -m venv venv

# Or using default Python 3.8/3.9
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (should show venv in prompt)
which python
```

### 7. Upgrade pip and Install Dependencies

```bash
# Activate venv first
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install requirements
pip install -r requirements.txt
```

**If you get compilation errors**, install additional dev tools:

```bash
sudo dnf install python3-devel -y
# Then retry: pip install -r requirements.txt
```

### 8. Create .env Configuration File

```bash
# Copy template
cp .env.example .env

# Edit with your values
nano .env
```

**Minimal required values:**

```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklmNOPqrsTUVwxyzABCDEFG
WEB3_PROVIDER_URL=https://mainnet.base.org
ALFA_CONTRACT_ADDRESS=0x1234567890123456789012345678901234567890
SIGNER_PRIVATE_KEY=0xyour_private_key_here
CONTRACT_ABI_PATH=abi/ALFA_Contract_ABI.json
```

### 9. Create ABI Directory and Contract ABI

```bash
mkdir -p abi

# Create abi/ALFA_Contract_ABI.json
# Paste your contract's ABI JSON here
nano abi/ALFA_Contract_ABI.json
```

---

## Running the Bot

### Local Testing

```bash
# Activate virtual environment
source ~/projects/alfa-bot/venv/bin/activate

# Run bot
cd ~/projects/alfa-bot
python3 alfabot_main.py
```

**Expected output:**
```
2024-01-15 10:30:45 - alfabot_main - INFO - Connected to network: 8453
2024-01-15 10:30:47 - file_processor - INFO - FFmpeg found and available
2024-01-15 10:30:48 - alfabot_main - INFO - ALFA Telegram Bot starting...
```

### Production: systemd Service (Recommended for RHEL)

#### Step 1: Create systemd Service File

```bash
sudo nano /etc/systemd/system/alfa-bot.service
```

**Paste this content:**

```ini
[Unit]
Description=ALFA Telegram Bot
After=network-online.target
Wants=network-online.target
Documentation=https://github.com/your-repo

[Service]
Type=simple
User=username
Group=username
WorkingDirectory=/home/username/projects/alfa-bot
Environment="PATH=/home/username/projects/alfa-bot/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin"
Environment="HOME=/home/username"
ExecStart=/home/username/projects/alfa-bot/venv/bin/python3 alfabot_main.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=alfa-bot

# Security settings
PrivateTmp=yes
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/home/username/projects/alfa-bot /tmp/alfa_uploads

[Install]
WantedBy=multi-user.target
```

**Replace `username` with your actual username!**

#### Step 2: Set Correct Permissions

```bash
# Set ownership
sudo chown username:username /etc/systemd/system/alfa-bot.service
sudo chmod 644 /etc/systemd/system/alfa-bot.service

# Create upload directory with correct permissions
mkdir -p /tmp/alfa_uploads
chmod 755 /tmp/alfa_uploads
```

#### Step 3: Enable and Start Service

```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Enable service (auto-start on boot)
sudo systemctl enable alfa-bot

# Start service
sudo systemctl start alfa-bot

# Check status
sudo systemctl status alfa-bot

# View logs
sudo journalctl -u alfa-bot -f

# Stop service (if needed)
sudo systemctl stop alfa-bot
```

**Useful systemd commands:**

```bash
# Check if running
sudo systemctl is-active alfa-bot

# View last 100 log lines
sudo journalctl -u alfa-bot -n 100

# View logs since last boot
sudo journalctl -u alfa-bot -b

# View with timestamps
sudo journalctl -u alfa-bot --output short-iso

# Restart after code changes
sudo systemctl restart alfa-bot
```

### Production: Docker (Alternative for RHEL)

#### Step 1: Install Docker

```bash
# Install Docker Community Edition
sudo dnf install docker-ce docker-ce-cli containerd.io docker-buildx-plugin -y

# Or install Podman (RHEL native alternative to Docker)
sudo dnf install podman podman-docker -y

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group (to run without sudo)
sudo usermod -aG docker $USER
newgrp docker
```

#### Step 2: Create Dockerfile

```bash
nano Dockerfile
```

**Paste this content:**

```dockerfile
FROM registry.access.redhat.com/ubi8/ubi:latest

# Install system dependencies
RUN dnf install -y dnf-plugins-core && \
    dnf install -y epel-release && \
    dnf install -y \
    python3.11 \
    python3.11-pip \
    python3.11-devel \
    ffmpeg \
    ffmpeg-devel \
    git \
    gcc \
    g++ \
    && dnf clean all

# Create app directory
WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip3.11 install --no-cache-dir -r requirements.txt

# Copy bot files
COPY . .

# Create necessary directories
RUN mkdir -p logs /tmp/alfa_uploads abi

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3.11 -c "import sys; sys.exit(0)" || exit 1

# Run bot
CMD ["python3.11", "alfabot_main.py"]
```

#### Step 3: Build and Run Docker Image

```bash
# Build image
docker build -t alfa-bot:latest .

# Run container with .env file
docker run -d \
  --name alfa-bot \
  --restart unless-stopped \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/abi:/app/abi \
  -v /tmp/alfa_uploads:/tmp/alfa_uploads \
  alfa-bot:latest

# Check if running
docker ps

# View logs
docker logs -f alfa-bot

# Stop container
docker stop alfa-bot

# Remove container
docker rm alfa-bot
```

### Production: Using Screen (Simple Alternative)

```bash
# Install screen
sudo dnf install screen -y

# Create new screen session
screen -S alfa-bot

# In the screen session:
cd ~/projects/alfa-bot
source venv/bin/activate
python3 alfabot_main.py

# Detach from screen: Ctrl+A then D
# Reattach: screen -r alfa-bot
# Kill session: screen -X -S alfa-bot quit
```

---

## RHEL-Specific Troubleshooting

### Issue: "command not found: ffmpeg"

```bash
# Check if installed
which ffmpeg

# Check EPEL is enabled
dnf repolist | grep epel

# Try enabling EPEL again
sudo dnf install epel-release -y
sudo dnf install ffmpeg -y
```

### Issue: "Python module not found"

```bash
# Ensure virtual environment is activated
source ~/projects/alfa-bot/venv/bin/activate

# Check Python path
which python3

# Reinstall requirements
pip install --upgrade pip
pip install -r requirements.txt
```

### Issue: "Permission denied" on systemd service

```bash
# Check file ownership
ls -la /etc/systemd/system/alfa-bot.service

# Fix if needed
sudo chown root:root /etc/systemd/system/alfa-bot.service
sudo chmod 644 /etc/systemd/system/alfa-bot.service

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart alfa-bot
```

### Issue: "SELinux denying access"

If using SELinux (default on RHEL):

```bash
# Check SELinux status
getenforce

# View SELinux denials
sudo ausearch -m AVC

# Temporarily disable SELinux (not recommended for production)
sudo setenforce 0

# Permanently disable (edit /etc/selinux/config and set SELINUX=disabled)
```

**Better approach: Create SELinux policy for bot**

```bash
# View denials
sudo tail -f /var/log/audit/audit.log

# Generate policy
sudo ausearch -c 'python3' --raw | sudo audit2allow -M alfa-bot
sudo semodule -i alfa-bot.pp
```

### Issue: "FFmpeg compilation errors"

If building FFmpeg from source fails:

```bash
# Install all build dependencies
sudo dnf groupinstall "Development Tools" -y
sudo dnf install \
  yasm \
  nasm \
  libass-devel \
  opus-devel \
  libvorbis-devel \
  libtheora-devel \
  libx264-devel \
  libx265-devel \
  -y

# Then try building again
cd /tmp/ffmpeg
./configure --prefix=/usr/local --enable-gpl
make clean
make -j$(nproc)
sudo make install
```

### Issue: "pip install fails on cryptography"

```bash
# Install required dev libraries
sudo dnf install \
  python3-devel \
  openssl-devel \
  libffi-devel \
  -y

# Clear pip cache and reinstall
pip cache purge
pip install --no-cache-dir -r requirements.txt
```

---

## Monitoring on RHEL

### View Bot Status

```bash
# If using systemd
sudo systemctl status alfa-bot

# If using Docker
docker ps | grep alfa-bot

# If using screen
screen -r alfa-bot
```

### Check Bot Logs

```bash
# systemd logs
sudo journalctl -u alfa-bot -f --output cat

# Docker logs
docker logs -f alfa-bot

# Application logs
tail -f ~/projects/alfa-bot/logs/logs.txt
```

### Monitor Resource Usage

```bash
# If using systemd
ps aux | grep python3 | grep alfabot

# If using Docker
docker stats alfa-bot

# System resources
top -b -n 1 | head -20
free -h
df -h
```

### Check Network Connectivity

```bash
# Verify Base RPC connection
curl https://mainnet.base.org -I

# Check Telegram API
curl https://api.telegram.org/botYOUR_TOKEN/getMe

# Verify DNS
nslookup mainnet.base.org
```

---

## Firewall Configuration (RHEL firewalld)

If you need to access bot from other hosts:

```bash
# Check firewall status
sudo firewall-cmd --state

# Allow inbound Telegram webhooks (if using webhooks instead of polling)
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload

# View allowed ports
sudo firewall-cmd --list-all
```

---

## Performance Tuning (RHEL)

### Optimize File Descriptor Limits

```bash
# Edit limits
sudo nano /etc/security/limits.conf

# Add:
username soft nofile 65536
username hard nofile 65536

# Apply
ulimit -n 65536
```

### CPU Affinity (for high-load scenarios)

```bash
# Install tools
sudo dnf install numactl -y

# Run bot with CPU affinity
taskset -c 0-3 python3 alfabot_main.py
```

### Memory Optimization

```bash
# Monitor memory
free -h

# If running low, enable swap (if not already configured)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## Backup & Restore (RHEL)

### Backup Configuration

```bash
# Create backup directory
mkdir -p ~/backups

# Backup .env (encrypted)
gpg --symmetric .env
cp .env.gpg ~/backups/

# Backup ABI
cp abi/ALFA_Contract_ABI.json ~/backups/

# Backup logs
tar -czf ~/backups/logs_$(date +%Y%m%d).tar.gz logs/
```

### Restore Configuration

```bash
# Restore .env
gpg ~/backups/.env.gpg > .env

# Restore ABI
cp ~/backups/ALFA_Contract_ABI.json abi/
```

---

## Security Best Practices for RHEL

1. **Keep RHEL Updated**
   ```bash
   sudo dnf update -y
   ```

2. **Use SSH Keys (not password auth)**
   ```bash
   ssh-keygen -t ed25519
   ```

3. **Configure sudo Correctly**
   ```bash
   # Use visudo (safe editor for sudoers)
   sudo visudo
   ```

4. **Enable firewall**
   ```bash
   sudo systemctl enable firewalld
   sudo systemctl start firewalld
   ```

5. **Regular backups**
   ```bash
   # Automate with cron
   crontab -e
   # Add: 0 2 * * * tar -czf /backups/bot_$(date +\%Y\%m\%d).tar.gz ~/projects/alfa-bot
   ```

6. **Never commit .env to git**
   ```bash
   echo ".env" >> .gitignore
   ```

---

## Uninstall / Cleanup

```bash
# Stop systemd service
sudo systemctl stop alfa-bot
sudo systemctl disable alfa-bot
sudo rm /etc/systemd/system/alfa-bot.service
sudo systemctl daemon-reload

# Remove bot directory
rm -rf ~/projects/alfa-bot

# Remove Python packages (optional)
pip uninstall -r requirements.txt -y

# Remove FFmpeg (optional)
sudo dnf remove ffmpeg -y

# Remove virtual environment
rm -rf ~/projects/alfa-bot/venv
```

---

## Quick Reference: RHEL vs Ubuntu Commands

| Task | Ubuntu | RHEL |
|------|--------|------|
| Update system | `apt-get update && apt-get upgrade` | `dnf update` |
| Install package | `apt-get install` | `dnf install` |
| Remove package | `apt-get remove` | `dnf remove` |
| Search package | `apt-cache search` | `dnf search` |
| List installed | `dpkg -l` | `rpm -qa` |
| System repos | `/etc/apt/sources.list` | `/etc/yum.repos.d/` |
| Install FFmpeg | `apt-get install ffmpeg` | `dnf install ffmpeg` (needs EPEL) |

---

## Testing the Bot on RHEL

```bash
# Activate venv
source ~/projects/alfa-bot/venv/bin/activate

# Test imports
python3 -c "import telegram; print('✓ Telegram OK')"
python3 -c "from web3 import Web3; print('✓ Web3 OK')"
python3 -c "from cryptography.hazmat.primitives.ciphers import Cipher; print('✓ Crypto OK')"
python3 -c "import subprocess; subprocess.run(['ffprobe', '-version']); print('✓ FFmpeg OK')"

# Test bot startup (Ctrl+C to stop)
python3 alfabot_main.py
```

---

## Getting Help

### View Current Configuration

```bash
# Show .env variables (safe - no secrets)
grep -v "^#" .env | grep -v "^$" | cut -d= -f1

# Check bot logs for errors
journalctl -u alfa-bot -n 50

# Test contract connection
python3 << 'EOF'
from blockchain_manager import BlockchainManager
try:
    bm = BlockchainManager(
        provider_url="https://mainnet.base.org",
        contract_address="0x...",
        abi_path="abi/ALFA_Contract_ABI.json"
    )
    print("✓ Contract connected")
except Exception as e:
    print(f"✗ Error: {e}")
EOF
```

### RHEL-Specific Resources

- RHEL Documentation: https://access.redhat.com/documentation/
- EPEL Wiki: https://fedoraproject.org/wiki/EPEL
- DNF Documentation: https://dnf.readthedocs.io/

---

## Next Steps

1. ✅ Follow steps 1-9 above
2. ✅ Deploy bot using systemd or Docker
3. ✅ Test with sample video
4. ✅ Monitor with `journalctl` or `docker logs`
5. ✅ Scale to multiple instances if needed

---

**Status:** Ready for RHEL 8/9 deployment 🚀

**Created:** 2024
**Updated for:** RHEL 8.x, RHEL 9.x, AlmaLinux, Rocky Linux
