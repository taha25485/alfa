# ALFA Platform - Complete Architecture & Integration Guide

## System Overview

ALFA is a three-tier passive income platform for content creators:

```
┌─────────────────────────────────────────────────────────────┐
│                    CONTENT CREATOR                          │
│              (Uploads gaming videos via Telegram)           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │  TELEGRAM BOT LAYER          │
        │  (First Point of Contact)    │
        │  - Accept video uploads      │
        │  - Extract metadata          │
        │  - Hash & encrypt files      │
        │  - Call valuation engine     │
        │  - Call smart contract       │
        └──────────────┬───────────────┘
                       │
        ┌──────────────┴───────────────┐
        │                              │
        ▼                              ▼
    ┌─────────────┐           ┌──────────────────┐
    │ VALUATION   │           │  SMART CONTRACT  │
    │  ENGINE     │           │  (ALFA Token)    │
    │  (Python)   │           │  (Solidity)      │
    │             │           │                  │
    │ Scores:     │           │ - Registers      │
    │ • Duration  │           │   uploads        │
    │ • Size      │           │ - Mints tokens   │
    │ • Codec     │           │ - Stores metadata│
    │ • Game pop  │           │ - Tracks content │
    └─────────────┘           └──────────────────┘
                       │
                       ▼
    ┌──────────────────────────────────────────┐
    │  GOOGLE DRIVE (Encrypted File Storage)   │
    │  └─ Encrypted .MKV files                 │
    └──────────────────────────────────────────┘
                       │
                       ▼
    ┌──────────────────────────────────────────┐
    │  NFT & BASE APP (Public Distribution)    │
    │  - NFT with decryption key               │
    │  - Original file goes viral              │
    │  - Token price increases                 │
    └──────────────────────────────────────────┘
                       │
                       ▼
    ┌──────────────────────────────────────────┐
    │  CREATOR'S WALLET (Base Network)         │
    │  - Receives ALFA tokens                  │
    │  - Can trade on DEX                      │
    │  - Passive income stream                 │
    └──────────────────────────────────────────┘
```

---

## Component Breakdown

### 1. TELEGRAM BOT (alfabot_main.py + supporting modules)

**Purpose:** User-friendly interface for content uploads

**Flow:**
```
/upload 
   ↓
User sends video file
   ↓
Bot extracts metadata:
   • Duration (seconds)
   • Resolution (1080p, 4K, etc)
   • Codec (H.264, H.265)
   • File size (MB)
   • Frame rate (fps)
   ↓
Bot hashes original file (SHA256)
   ↓
Bot converts to MKV format
   ↓
Bot encrypts with AES-256-CBC
   ↓
Bot hashes encrypted file (SHA512)
   ↓
Bot asks for wallet address
   ↓
Bot asks for game name
   ↓
Bot calls Valuation Engine with metadata
   ↓
Valuation Engine returns score (0-1000)
   ↓
Bot calls Smart Contract:
   └─ registerContentUpload()
      └─ Contract mints ALFA tokens
         └─ Tokens sent to creator wallet
   └─ encrypt()
      └─ Contract stores encryption metadata
         └─ IV, algorithm, hashes saved on-chain
   ↓
Bot uploads encrypted file to Google Drive
   ↓
Bot creates NFT with decryption key
   ↓
Bot posts original file to Base App
```

**Key Files:**
- `alfabot_main.py` - Main bot logic, conversation handler
- `file_processor.py` - FFmpeg integration for metadata & MKV conversion
- `encryption_manager.py` - AES-256-CBC encryption & hashing
- `blockchain_manager.py` - Web3 contract calls
- `valuation_engine.py` - Scoring algorithm
- `config.py` - Configuration management

---

### 2. SMART CONTRACT (ALFA_Token_Contract.sol)

**Purpose:** Mint tokens, store encryption metadata, track uploads

**Key Functions:**

```solidity
// Lifecycle control
start()                          // Activate contract
stop()                          // Pause operations
activateEncryption()            // Enable encryption metadata
deactivateEncryption()          // Disable encryption

// Bot authorization
authorizeValuationBot(address)  // Whitelist bot addresses
revokeValuationBot(address)     // Remove bot access

// Content upload & distribution
registerContentUpload(
  uploader_address,
  content_hash,
  file_hash,
  valuation_score,              // 0-1000
  simulation_title
) → Returns transaction hash
   → Mints ALFA tokens to uploader
   → Token amount = (score / 1000) * 1,000,000

// Encryption metadata storage
encrypt(
  content_hash,
  original_hash,                // SHA256
  encrypted_hash,               // SHA512
  algorithm,                    // "AES256-CBC"
  iv                           // Initialization vector
) → Stores metadata on-chain
   → Emits event for audit trail

decrypt(
  content_hash,
  original_hash,
  encrypted_hash
) → Verifies file integrity
   → Returns true if hashes match

// Metadata retrieval
getEncryptionMetadata(content_hash)   → Returns IV, algorithm, hashes
getContentDetails(content_hash)       → Returns upload info
getContractStatus()                   → Returns contract state
```

**Token Economics:**
```
Total Supply: 1,000,000,000 ALFA (1 billion)

Per Upload:
  Score 1000 → 1,000,000 ALFA
  Score  500 → 500,000 ALFA
  Score  100 → 100,000 ALFA

Distribution:
  • Owner: Holds initial supply
  • Contract: Distributes to creators
  • Creators: Receive tokens instantly
```

---

### 3. VALUATION ENGINE (valuation_engine.py)

**Purpose:** Score content 0-1000 based on quality metrics

**Scoring Formula:**
```
Duration Score (0-150 points)
  • Max value at 2 hours
  • Formula: (duration_seconds / 7200) * 150

File Size Score (0-150 points)
  • Max value at 10 GB
  • Formula: (file_size_mb / 10240) * 150

Resolution Score (0-200 points)
  • 4K (2160p): 200 points
  • QHD (1440p): 150 points
  • Full HD (1080p): 100 points
  • HD (720p): 50 points
  • Lower: 25 points

Codec Score (0-100 points)
  • HEVC (H.265): 100 points
  • AV1: 95 points
  • VP9: 75 points
  • H.264: 50 points
  • Other: 25 points

Game Popularity Score (0-200 points)
  • Match game name against database
  • Example: Elden Ring → 950 popularity → 190 points
  • Unknown game → 80 points

Existing Sales Score (0-200 points)
  • Based on comparable content sales
  • Formula: (similar_sales / 100) * 200

TOTAL: Sum of all categories (capped at 1000)
```

**Game Database (Expandable):**
```
Elden Ring        → 950 popularity (FromSoftware)
Zelda             → 920 popularity (Nintendo)
Baldur's Gate 3   → 900 popularity (Larian)
Hogwarts Legacy   → 850 popularity (Avalanche)
Starfield         → 880 popularity (Bethesda)
Cyberpunk 2077    → 800 popularity (CD Projekt Red)
...and 100+ more games
```

---

## Data Flow in Detail

### Step 1: User Uploads Video

```
User: /upload
Bot: Conversation handler enters WAITING_FOR_FILE state
User: Sends video.mp4 (2GB max)
Bot: 
  - Downloads file to /tmp/alfa_uploads/{user_id}_{filename}
  - Validates format (MP4, MKV, MOV, WEBM, AVI, FLV, WMV)
  - Validates size (<2GB)
  - Uses ffprobe to extract metadata
```

**Extracted Metadata:**
```json
{
  "duration": 3600,              // seconds
  "file_size_mb": 1500.5,
  "resolution": "Full HD (1080p)",
  "codec": "H264",
  "bitrate": 5000,               // kbps
  "frame_rate": 30.0,
  "audio_codec": "AAC"
}
```

### Step 2: Hashing

```
Original file hash (SHA256):
  Input: video.mp4 (raw file)
  Output: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
  Purpose: Verify original file integrity before encryption

After MKV conversion and encryption:

Encrypted file hash (SHA512):
  Input: video.mkv.encrypted (after AES-256-CBC)
  Output: 
    a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f
  Purpose: Prove file was encrypted correctly
```

### Step 3: Encryption Process

```
AES-256-CBC Encryption:

Input:
  • Plaintext file: video.mkv
  • Key: 32 random bytes (256 bits)
  • IV: 16 random bytes (128 bits)

Process:
  1. Generate random key & IV
  2. Open file, read in 1MB chunks
  3. Pad chunk to 16-byte AES block size
  4. Encrypt chunk with AES-256-CBC
  5. Write encrypted chunk to output
  6. Repeat until EOF
  7. Write IV to file header (unencrypted)

Output:
  • Encrypted file: video.mkv.encrypted
  • Key: stored securely (will be in NFT metadata)
  • IV: stored in contract & NFT metadata
```

### Step 4: Valuation

```
Bot calls: ValuationEngine.calculate_score(
  duration=3600,
  file_size_mb=1500.5,
  resolution="Full HD (1080p)",
  codec="H264",
  game_name="Elden Ring"
)

Engine calculation:
  Duration: (3600 / 7200) * 150 = 75 points
  File size: (1500.5 / 10240) * 150 = 21.93 points
  Resolution (1080p): 100 points
  Codec (H264): 50 points
  Game (Elden Ring): (950 / 1000) * 200 = 190 points
  Sales: 0 (new content)
  ────────────────────────────
  TOTAL: 436.93 → rounded to 437/1000
```

### Step 5: Smart Contract Call #1

```
Bot calls: contract.registerContentUpload(
  uploader_address = "0x742d35Cc6634C0532925a3b844Bc89e7595f42e6",
  content_hash = bytes32(keccak256("user_123_elden_ring_...date")),
  file_hash = bytes32(sha512_encrypted_output),
  valuation_score = 437,
  simulation_title = "Elden Ring - Speedrun Attempt"
)

Contract execution:
  1. Verify contract is active (isActive == true)
  2. Verify uploader address is valid
  3. Verify score is 1-1000
  4. Calculate tokens: (437 / 1000) * 1,000,000 = 437,000 ALFA
  5. Transfer 437,000 ALFA to uploader wallet
  6. Store upload record in contentRegistry mapping
  7. Add content_hash to uploaderContent array
  8. Emit ContentUploaded event
  
  Transaction: 0x123abc...def (on Base)
```

### Step 6: Smart Contract Call #2

```
Bot calls: contract.encrypt(
  content_hash = bytes32(...same as above...),
  original_hash = bytes32(sha256_original),
  encrypted_hash = bytes32(sha512_encrypted),
  algorithm = "AES256-CBC",
  iv = bytes(hex_of_iv)
)

Contract execution:
  1. Verify bot is authorized (onlyAuthorizedBot)
  2. Verify encryption is active (whenEncryptionActive)
  3. Store in encryptionRecords mapping:
     {
       originalHash: 0x...,
       encryptedHash: 0x...,
       encryptionAlgorithm: "AES256-CBC",
       encryptionIV: bytes(...),
       timestamp: block.timestamp,
       isEncrypted: true
     }
  4. Emit FileEncrypted event
  
  Transaction: 0x456def...abc (on Base)
```

### Step 7: Google Drive Upload

```
(Optional - requires GOOGLE_DRIVE_CREDENTIALS_PATH)

Bot uploads encrypted file to Google Drive:
  • File: video.mkv.encrypted
  • Folder: GOOGLE_DRIVE_FOLDER_ID
  • Metadata:
    - Original filename
    - Uploader address
    - Content hash
    - Block timestamp
    - Valuation score
```

### Step 8: NFT Creation

```
(Integration point - connects to NFT contract)

NFT metadata includes:
{
  name: "Elden Ring - Speedrun Attempt by [username]",
  description: "Gaming content for ALFA platform",
  image: "thumbnail_from_video.jpg",
  attributes: {
    duration: 3600,
    resolution: "1080p",
    game: "Elden Ring",
    valuation_score: 437,
    token_ticker: "ALFA"
  },
  decryption_key: "0x...", ⚠️ PUBLIC (security consideration)
  decryption_iv: "0x...",  ⚠️ PUBLIC
  google_drive_link: "https://drive.google.com/...",
  contract_address: "0x..."
}
```

### Step 9: Base App Distribution

```
Original (unencrypted) file posted to Base App
  • Allows content to go viral
  • Token ALFA associated with content
  • Price increases as popularity increases
  • Creators benefit from viral growth
```

---

## Token Economics Flow

```
Start: 1,000,000,000 ALFA total supply

User uploads quality content (score 437):
  ┌─────────────────────────────────────┐
  │ 437,000 ALFA transferred to creator │
  │ (instant, on-chain, irreversible)   │
  └─────────────────────────────────────┘

If content goes viral on Base App:
  ┌─────────────────────────────────────┐
  │ Token demand increases               │
  │ Price appreciates                    │
  │ Creator benefits from appreciation   │
  │ (passive income stream)              │
  └─────────────────────────────────────┘

Creator can:
  • Hold tokens for long-term appreciation
  • Trade on Base DEX (Uniswap, Curve, etc)
  • Use as collateral for loans
  • Stake for additional yields
  • Transfer to other wallets
```

---

## Security & Considerations

### On-Chain (Contract)

✅ **Strengths:**
- Immutable transaction record
- Transparent token distribution
- Non-custodial (creator controls wallet)
- Open-source, auditable code

⚠️ **Considerations:**
- Valuation score submitted by bot (requires trusted bot)
- Encryption key eventually public (via NFT metadata)
- Gas costs per upload (~$2-10 on Base)

### Off-Chain (Bot)

✅ **Strengths:**
- Encryption happens locally (not on-chain)
- File metadata never stored unencrypted
- Uses cryptographically secure libraries
- Session data cleaned up after upload

⚠️ **Considerations:**
- Bot private key must be kept safe
- Requires ETH balance for gas
- Temporary files stored locally (clean up needed)

---

## Deployment Checklist

- [ ] Deploy ALFA_Token_Contract.sol to Base
- [ ] Get contract address
- [ ] Extract contract ABI
- [ ] Create bot wallet (fund with ETH)
- [ ] Get Telegram bot token from @BotFather
- [ ] Create `.env` file with all values
- [ ] Install FFmpeg on bot server
- [ ] Run: `pip install -r requirements.txt`
- [ ] Run: `python3 alfabot_main.py`
- [ ] Authorize bot on contract: `contract.authorizeValuationBot(bot_address)`
- [ ] Test with sample video
- [ ] Deploy to production (systemd/Docker)
- [ ] Monitor logs and gas costs

---

## Integration Points for Future

1. **Google Drive API** - Encrypted file storage
2. **NFT Contract** - Minting NFTs with metadata
3. **Base App API** - Publishing content
4. **Database** - Track uploads, users, transactions
5. **Payment Processor** - USD/fiat conversion (if needed)
6. **Analytics** - Track content performance, token prices
7. **Secondary Marketplace** - Resale of encrypted content

---

## Performance & Scalability

**Current Bottlenecks:**
- FFmpeg conversion time (~1 min per video)
- Blockchain confirmation time (~2-3 min on Base)
- Google Drive upload speed (network dependent)

**Scaling Solutions:**
- Queue system for handling multiple uploads
- Batch processing for encryption
- Redis caching for valuation scores
- Database for session persistence
- Load balancer for multiple bot instances

**Cost Analysis (per upload):**
- Gas (registerContentUpload + encrypt): ~$3-5
- Bot server CPU: ~$0.01
- Storage (Google Drive): ~$0.001
- Total per upload: ~$3-5

---

## Next Steps

1. ✅ Deploy Smart Contract (DONE)
2. ✅ Setup Telegram Bot (DONE)
3. ⏳ Integrate Google Drive storage
4. ⏳ Create NFT minting system
5. ⏳ Deploy to Base App
6. ⏳ Setup secondary marketplace
7. ⏳ Launch marketing campaign
8. ⏳ Monitor performance & optimize

---

## Support Resources

- **Solidity Contract:** `ALFA_Token_Contract.sol` + `DEPLOYMENT_GUIDE.md`
- **Telegram Bot:** `QUICK_START.md` + `TELEGRAM_BOT_SETUP.md`
- **Valuation Engine:** `valuation_engine.py` (docstrings)
- **Web3 Integration:** `blockchain_manager.py` (docstrings)

---

**Status:** ✅ Ready for deployment

**Questions?** Check individual module docstrings or setup guides.
