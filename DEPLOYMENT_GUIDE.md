# ALFA Token Contract - Deployment & Integration Guide

## Contract Overview

**Network:** Base (Coinbase L2)  
**Standard:** ERC20 + Ownable + Pausable + ERC20Burnable  
**Initial Supply:** 1,000,000,000 ALFA (with 18 decimals)  
**Deployment Address:** [Will be generated after deployment]

---

## Core Functions Implemented

### START / STOP Functions
```solidity
start()                    // Activates contract operations
stop()                     // Pauses all token distribution
activateEncryption()       // Enables encryption metadata recording
deactivateEncryption()     // Disables encryption recording
```

### Encryption Functions
```solidity
encrypt(contentHash, originalHash, encryptedHash, algorithm, iv)
// Stores encryption metadata for a file
// Called by authorized valuation bot
// Records: original file hash → encrypted file hash → timestamps

decrypt(contentHash, originalHash, encryptedHash)
// Verifies file integrity by comparing hashes
// Returns true if hashes match, enabling decryption
// Emits event for audit trail
```

### Hashing Functions
```solidity
hashSHA256(bytes data)          // Keccak-256 (efficient alternative)
generateContentHash(bytes data) // Primary hashing for content
```

**Note:** Solidity natively supports Keccak-256. For SHA256/SHA384/SHA512, 
use these off-chain in the Python bot (via hashlib).

### Wallet & Key Functions
```solidity
getWalletAddress()         // Returns contract owner address
getEncryptionMetadata()    // Retrieves IV, keys, hashes for a file
setEncryptionKey()         // Stores encrypted key material
authorizeValuationBot()    // Whitelist bot addresses
```

### Content Valuation & Upload
```solidity
registerContentUpload(uploaderAddress, contentHash, fileHash, valuationScore, simulationTitle)
// Called by authorized bot after valuation
// Mints ALFA tokens to uploader based on score (0-1000)
// Max tokens per upload: 1,000,000 ALFA
// Formula: (valuationScore / 1000) * MAX_TOKENS = ALFA awarded
```

**Example:**
- Valuation Score: 850/1000
- Tokens Awarded: (850/1000) × 1,000,000 = 850,000 ALFA

---

## Data Structures

### EncryptionMetadata
```
originalHash        → SHA256 hash of original file
encryptedHash       → SHA512 hash of encrypted file
encryptionAlgorithm → "AES256-CBC"
encryptionIV        → Initialization vector (bytes)
encryptionKey       → Encrypted key (stored hashed)
timestamp           → Block timestamp
isEncrypted         → Boolean flag
```

### ContentUpload
```
uploader            → Address that receives tokens
contentHash         → Unique file identifier
fileHash            → SHA512 of final file
valuationScore      → 0-1000 scale
tokensAwarded       → ALFA sent to uploader
simulationTitle     → Game/simulation name
uploadTimestamp     → When registered
processed           → Completion flag
```

---

## Deployment Steps

### 1. Install Dependencies
```bash
npm install -g hardhat
npm install @openzeppelin/contracts
```

### 2. Create Hardhat Config for Base
```javascript
// hardhat.config.js
require("@nomicfoundation/hardhat-toolbox");

module.exports = {
  solidity: "0.8.20",
  networks: {
    base: {
      url: "https://mainnet.base.org",
      accounts: ["YOUR_PRIVATE_KEY"],
    },
    baseTestnet: {
      url: "https://sepolia.base.org",
      accounts: ["YOUR_PRIVATE_KEY"],
    },
  },
};
```

### 3. Deploy Contract
```bash
npx hardhat run scripts/deploy.js --network base
```

**Deploy Script (scripts/deploy.js):**
```javascript
async function main() {
  const ALFA = await ethers.getContractFactory("ALFAToken");
  const alfa = await ALFA.deploy();
  await alfa.deployed();
  
  console.log("ALFA deployed to:", alfa.address);
  
  // Start contract
  const startTx = await alfa.start();
  await startTx.wait();
  
  // Activate encryption
  const encTx = await alfa.activateEncryption();
  await encTx.wait();
  
  console.log("Contract activated and ready");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
```

---

## Integration with Telegram Bot & Valuation Engine

### Bot Workflow

```
User sends file + wallet address via Telegram
    ↓
Bot extracts metadata (duration, size, resolution)
    ↓
Bot hashes original file (SHA256)
    ↓
Bot converts to .MKV format
    ↓
Bot encrypts with AES256-CBC, gets new hash (SHA512)
    ↓
Python Valuation Engine scores content (0-1000)
    ↓
Bot calls contract: registerContentUpload()
    ↓
Contract mints ALFA to uploader's wallet
    ↓
Bot calls contract: encrypt() to store metadata
    ↓
Bot uploads encrypted file to Google Drive
    ↓
NFT created with ALFA token + metadata
    ↓
Original file posted to Base App
```

### Authorization Setup
```solidity
// Owner calls this once for each bot address
alfaContract.authorizeValuationBot("0xYourBotWalletAddress");

// Now bot can call:
// - encrypt()
// - registerContentUpload()
```

---

## Key Events for Monitoring

```solidity
event ContractStarted(uint256 timestamp);
event EncryptionStarted(uint256 timestamp);
event FileEncrypted(bytes32 indexed contentHash, address indexed uploader);
event ContentUploaded(bytes32 indexed contentHash, address indexed uploader, 
                     uint256 valuationScore, uint256 tokensAwarded);
event ValuationBotAuthorized(address indexed bot);
```

Monitor these events on Base Scan to track all uploads and token distributions.

---

## Security Considerations

1. **Encrypted Keys:** Keys stored in `encryptionRecords` should be encrypted server-side
   - Never store raw keys on-chain
   - Current implementation stores encrypted bytes only

2. **NFT Metadata Exposure:** Once NFT is sold, decryption key in metadata is public
   - Mitigation: Use time-delayed reveal or access-controlled metadata endpoint
   - Alternative: Store only hash, require off-chain key retrieval

3. **Admin Controls:**
   - Only owner can authorize bots
   - Only owner can start/stop contract
   - Only authorized bots can register uploads

4. **Token Supply:**
   - Fixed at 1B ALFA
   - Contract holds tokens for distribution
   - Owner can withdraw unused tokens

---

## Valuation Score Breakdown (Python Bot Calculates)

The Python valuation engine should score 0-1000 based on:

```
duration         → 0-150 points   (longer content = more value, capped)
file_size        → 0-150 points   (larger file = higher quality, capped)
resolution       → 0-200 points   (1080p: 100, 1440p: 150, 4K: 200)
encoding         → 0-100 points   (H.264: 50, H.265: 100)
game_popularity  → 0-200 points   (query game company, match database)
existing_sales   → 0-200 points   (track similar content value)
```

**Total: 0-1000 base score**

---

## Next Steps

1. ✅ Deploy contract to Base
2. ⏳ Create Telegram bot (accepts uploads, extracts metadata)
3. ⏳ Create Python valuation engine (scores content)
4. ⏳ Create NFT minting function
5. ⏳ Integrate Google Drive upload
6. ⏳ Integrate Base App posting

---

## Contract Addresses (Post-Deployment)

```
ALFA Token (Base Mainnet):  0x...
Deployer Wallet:            0x...
```

Save these for bot configuration.
