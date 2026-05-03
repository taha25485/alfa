# Deploy ALFA to Base Mainnet

Deploy your contract from local Hardhat to **Base mainnet** (real blockchain, real ETH).

---

## Prerequisites

1. **Real ETH on Base** (you'll need ~$5-10 for gas)
2. **Your private key** (never share!)
3. **Contract deployed locally** (already done ✅)

---

## Step 1: Get Real Base Mainnet ETH

### Option A: Bridge from Ethereum

1. Get ETH on Ethereum mainnet
2. Go to https://bridge.base.org/
3. Connect wallet
4. Bridge ETH to Base
5. Wait 10-15 minutes

### Option B: Buy Directly on Base

1. Use exchange that supports Base (Coinbase, Kraken, etc)
2. Withdraw directly to Base network
3. Instant arrival

### Check Balance

```bash
# Install ethers CLI
npm install -g etherscan-api

# Or use block explorer
# https://basescan.io/address/YOUR_ADDRESS
```

---

## Step 2: Update Hardhat Config for Mainnet

```bash
cd ~/alfa-hardhat
nano hardhat.config.js
```

Verify it has Base mainnet (it should):

```javascript
const PRIVATE_KEY = process.env.DEPLOYER_PRIVATE_KEY || "0x...";

module.exports = {
  solidity: "0.8.20",
  networks: {
    base: {
      url: "https://mainnet.base.org",
      accounts: [PRIVATE_KEY],
      chainId: 8453,
    },
    baseTestnet: {
      url: "https://sepolia.base.org",
      accounts: [PRIVATE_KEY],
      chainId: 84532,
    },
  },
};
```

---

## Step 3: Update .env for Mainnet

```bash
nano ~/.env
```

**Use your REAL private key** (the one with ETH on Base):

```env
DEPLOYER_PRIVATE_KEY=0xyour_real_private_key_with_base_eth
```

**⚠️ WARNING:** 
- Never share this key
- Never commit to git
- Use fresh wallet if possible

---

## Step 4: Deploy to Base Mainnet

```bash
cd ~/alfa-hardhat

# Deploy to mainnet (costs real ETH for gas)
npx hardhat run scripts/deploy.js --network base
```

**Expected output:**

```
🚀 Deploying ALFA Token Contract to Base...

📝 Deploying with account: 0x...
💰 Account balance: 0.5 ETH

📦 Compiling contract...
⏳ Deploying (this may take 1-2 minutes)...

✅ ALFA Token deployed successfully!

📍 Contract Address: 0x...MAINNET_ADDRESS...
🔗 View on BaseScan: https://basescan.io/address/0x...

✅ Contract activated (start() called)
✅ Encryption activated
```

---

## Step 5: Save Contract Address

```bash
# View deployment info
cat deployment-info.json
```

Copy the **contractAddress** field.

---

## Step 6: Update Bot for Mainnet

```bash
nano ~/alfa-bot/.env
```

Update these values:

```env
# Change RPC to mainnet
WEB3_PROVIDER_URL=https://mainnet.base.org

# Add your mainnet contract address
ALFA_CONTRACT_ADDRESS=0x...MAINNET_ADDRESS...

# Use same signer (or different wallet with ETH)
SIGNER_PRIVATE_KEY=0x...bot_wallet_key...
```

**⚠️ Fund the bot wallet!**

The signer account needs ETH for gas:

```bash
# Send ~0.1 ETH to your bot signer address
# From your main wallet or exchange
```

---

## Step 7: Verify Contract on BaseScan

1. Go to https://basescan.io/
2. Paste your contract address
3. Should show:
   - ✅ Contract code
   - ✅ 1 billion ALFA supply
   - ✅ `start()` called
   - ✅ `activateEncryption()` called

---

## Step 8: Test Bot on Mainnet

Keep Hardhat node stopped ⚠️ (it's local-only)

Start bot:

```bash
cd ~/alfa-bot
python3 alfabot_main.py
```

Upload test video:

1. `/upload`
2. Upload small video
3. Wallet: your mainnet address
4. Game: `Test`

Bot will:
- Process video
- Call **REAL** smart contract
- Send **REAL** ALFA tokens to your wallet
- Cost real ETH (usually $0.50-2 in gas)

Check transaction on BaseScan:

```
https://basescan.io/tx/YOUR_TX_HASH
```

---

## Gas Cost Optimization

Each upload costs ETH for gas. To reduce costs:

### Option 1: Batch Registrations

Instead of calling contract per upload, batch 10 uploads then call once.

### Option 2: Use L2 Optimizations

Base already optimizes, but you can reduce:

```solidity
// In contract: reduce storage writes
// Use tighter packing of variables
// Avoid expensive operations
```

### Option 3: Monitor Gas

```bash
# Check current Base gas prices
curl https://api.basescan.io/api?module=gastracker&action=gasoracle&apikey=YourKey
```

---

## Verify Everything Works

Checklist:

- [ ] ETH on Base mainnet
- [ ] Contract deployed to Base
- [ ] Address visible on BaseScan
- [ ] Bot configured for mainnet
- [ ] Bot signer has ETH
- [ ] First upload succeeds
- [ ] Tokens appear in wallet
- [ ] Transaction visible on BaseScan

---

## Troubleshooting

### "Insufficient balance"

```bash
# Add more ETH to signer wallet
# Send from your main wallet to bot signer address
```

### "Network error"

```bash
# Verify RPC is working
curl https://mainnet.base.org

# Should return JSON
```

### "Contract not found after deploy"

Wait 30-60 seconds, then refresh BaseScan.

---

## Security Checklist

- [ ] Private key in `.env` only (never in code)
- [ ] `.env` in `.gitignore`
- [ ] Signer wallet has minimum needed ETH only
- [ ] Main wallet secured (hardware wallet if possible)
- [ ] Backup private keys safely

---

## Next: NFT Minting

Once mainnet is working, we'll:

1. Create NFT contract
2. Mint NFT for each upload
3. Attach decryption key to metadata
4. Sell on OpenSea/other marketplaces

---

**Status:** Ready to deploy to mainnet! 🚀
