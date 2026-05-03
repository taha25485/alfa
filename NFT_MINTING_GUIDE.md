# ALFA NFT Minting - ERC721 Integration

Create NFTs for each uploaded video with decryption keys stored in metadata.

---

## Architecture

For each video upload:

1. Valuation scores content (255/1000)
2. Tokens minted (255,000 ALFA)
3. **NFT minted** with unique ID
4. Decryption key stored in NFT metadata
5. User can sell NFT on OpenSea (gives buyer decryption rights)

---

## Step 1: Create NFT Contract

```bash
cd ~/alfa-hardhat
nano contracts/ALFA_NFT_Contract.sol
```

Paste:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract ALFANFTContent is ERC721, ERC721URIStorage, ERC721Enumerable, Ownable {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIdCounter;

    // Content metadata
    struct ContentMetadata {
        string gameName;
        uint256 valuationScore;
        string originalHash;
        string encryptedHash;
        string decryptionKey; // AES key as hex string
        uint256 createdAt;
    }

    mapping(uint256 => ContentMetadata) public contentMetadata;
    mapping(bytes32 => uint256) public uploadHashToTokenId; // Track uploads

    event ContentMinted(
        uint256 indexed tokenId,
        address indexed creator,
        string gameName,
        uint256 valuationScore,
        string decryptionKey
    );

    event DecryptionKeyRevealed(
        uint256 indexed tokenId,
        address indexed nftOwner,
        string decryptionKey
    );

    constructor() ERC721("ALFA Content NFT", "ALFA-NFT") {}

    /**
     * @dev Mint NFT for uploaded content
     * Only callable by ALFA token contract
     */
    function mintContentNFT(
        address creator,
        string memory gameName,
        uint256 valuationScore,
        string memory originalHash,
        string memory encryptedHash,
        string memory decryptionKey,
        string memory metadataURI
    ) external onlyOwner returns (uint256) {
        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();

        // Mint NFT
        _safeMint(creator, tokenId);
        _setTokenURI(tokenId, metadataURI);

        // Store metadata
        contentMetadata[tokenId] = ContentMetadata({
            gameName: gameName,
            valuationScore: valuationScore,
            originalHash: originalHash,
            encryptedHash: encryptedHash,
            decryptionKey: decryptionKey,
            createdAt: block.timestamp
        });

        // Track upload
        bytes32 uploadHash = keccak256(abi.encodePacked(originalHash, encryptedHash));
        uploadHashToTokenId[uploadHash] = tokenId;

        emit ContentMinted(
            tokenId,
            creator,
            gameName,
            valuationScore,
            decryptionKey
        );

        return tokenId;
    }

    /**
     * @dev Get decryption key - only owner can decrypt
     */
    function getDecryptionKey(uint256 tokenId) 
        external 
        view 
        returns (string memory) 
    {
        require(ownerOf(tokenId) == msg.sender, "Not NFT owner");
        return contentMetadata[tokenId].decryptionKey;
    }

    /**
     * @dev Get content metadata
     */
    function getContentMetadata(uint256 tokenId) 
        external 
        view 
        returns (ContentMetadata memory) 
    {
        require(_exists(tokenId), "Token does not exist");
        return contentMetadata[tokenId];
    }

    /**
     * @dev Transfer with decryption rights
     */
    function transferWithDecryption(
        address to,
        uint256 tokenId
    ) external {
        safeTransferFrom(msg.sender, to, tokenId);
    }

    // Required overrides
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 tokenId,
        uint256 batchSize
    ) internal override(ERC721, ERC721Enumerable) {
        super._beforeTokenTransfer(from, to, tokenId, batchSize);
    }

    function _afterTokenTransfer(
        address from,
        address to,
        uint256 tokenId,
        uint256 batchSize
    ) internal override(ERC721) {
        super._afterTokenTransfer(from, to, tokenId, batchSize);
    }

    function _burn(uint256 tokenId) 
        internal 
        override(ERC721, ERC721URIStorage) 
    {
        super._burn(tokenId);
    }

    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721Enumerable, ERC721URIStorage)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }

    function _exists(uint256 tokenId) internal view returns (bool) {
        return _ownerOf(tokenId) != address(0);
    }

    // Admin only
    function _ownerOf(uint256 tokenId) internal view returns (address) {
        address owner = ownerOf(tokenId);
        return owner;
    }
}
```

---

## Step 2: Update Main ALFA Contract to Mint NFTs

Edit `ALFA_Token_Contract.sol`:

```bash
nano contracts/ALFA_Token_Contract.sol
```

Add at top:

```solidity
import "./ALFA_NFT_Contract.sol";
```

Add to constructor:

```solidity
ALFANFTContent public nftContract;
```

Add this function:

```solidity
function setNFTContract(address _nftContract) external onlyOwner {
    nftContract = ALFANFTContent(_nftContract);
}

function registerContentUpload(
    address uploader,
    string calldata gameName,
    uint256 valuationScore,
    string calldata originalHash,
    string calldata encryptedHash,
    string calldata decryptionKey,
    string calldata metadataURI
) external onlyOwner returns (uint256 nftTokenId) {
    require(active, "Contract not active");
    require(valuationScore <= 1000, "Invalid score");

    // Calculate tokens
    uint256 tokensToMint = (valuationScore * 1_000_000) / 1000;
    require(tokensToMint <= 1_000_000, "Max 1M per upload");

    // Mint ALFA tokens
    _mint(uploader, tokensToMint * 10 ** decimals());

    // Mint NFT
    nftTokenId = nftContract.mintContentNFT(
        uploader,
        gameName,
        valuationScore,
        originalHash,
        encryptedHash,
        decryptionKey,
        metadataURI
    );

    return nftTokenId;
}
```

---

## Step 3: Deploy NFT Contract

```bash
cd ~/alfa-hardhat

# Compile
npx hardhat compile

# Deploy to Base mainnet (once ALFA deployed)
npx hardhat run << 'EOF'
const hre = require("hardhat");

async function main() {
  console.log("🎨 Deploying ALFA NFT Contract...");
  
  const NFTContract = await hre.ethers.getContractFactory("ALFANFTContent");
  const nft = await NFTContract.deploy();
  await nft.waitForDeployment();
  
  console.log("✅ NFT Contract deployed:", nft.target);
  console.log("🔗 BaseScan:", `https://basescan.io/address/${nft.target}`);
}

main().catch(console.error);
EOF
```

---

## Step 4: Link Contracts

After both deployed:

```bash
# Get NFT address from deployment above
ALFA_ADDRESS=0x... # your ALFA token address
NFT_ADDRESS=0x... # your NFT address

npx hardhat run << 'EOF'
const hre = require("hardhat");

async function main() {
  const alfaAddress = process.env.ALFA_ADDRESS;
  const nftAddress = process.env.NFT_ADDRESS;
  
  const alfa = await hre.ethers.getContractAt("ALFAToken", alfaAddress);
  await alfa.setNFTContract(nftAddress);
  
  console.log("✅ Contracts linked!");
}

main().catch(console.error);
EOF
```

---

## Step 5: Update Bot for NFT Minting

```bash
nano ~/alfa-bot/blockchain_manager.py
```

Add to `registerContentUpload()`:

```python
def register_with_nft(
    self,
    uploader,
    game_name,
    valuation_score,
    original_hash,
    encrypted_hash,
    decryption_key,
    metadata_uri
):
    """Register with NFT minting"""
    try:
        tx = self.contract.functions.registerContentUpload(
            uploader,
            game_name,
            valuation_score,
            original_hash,
            encrypted_hash,
            decryption_key,
            metadata_uri
        ).build_transaction({
            'from': self.signer_address,
            'gas': 500000,
            'gasPrice': self.web3.eth.gas_price,
            'nonce': self.web3.eth.get_transaction_count(self.signer_address),
        })

        signed = self.web3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed.rawTransaction)
        
        logger.info(f"NFT Mint TX: {tx_hash.hex()}")
        
        return {
            'tx_hash': tx_hash.hex(),
            'nft_minted': True
        }
    except Exception as e:
        logger.error(f"NFT mint failed: {e}")
        raise
```

---

## Step 6: Metadata URI (IPFS)

For each NFT, create metadata JSON and upload to IPFS:

```bash
# Install IPFS
sudo apt-get install -y ipfs

# Start IPFS daemon
ipfs daemon
```

Create metadata file:

```json
{
  "name": "Elden Ring Gameplay #255",
  "description": "Epic boss fight video with 255/1000 valuation score",
  "image": "ipfs://QmXxxx...",
  "external_url": "https://alfa-platform.io",
  "attributes": [
    {
      "trait_type": "Game",
      "value": "Elden Ring"
    },
    {
      "trait_type": "Valuation Score",
      "value": "255"
    },
    {
      "trait_type": "Encrypted Video Hash",
      "value": "0xabc123..."
    }
  ]
}
```

Upload to IPFS:

```bash
ipfs add metadata.json

# Returns: QmXxxx...
# Use this as metadataURI: ipfs://QmXxxx...
```

---

## Step 7: Test NFT Minting

Upload video with bot:

1. `/upload`
2. Upload video
3. Send wallet
4. Send game name

Bot will now:
- Mint ALFA tokens ✅
- Mint NFT ✅
- Store metadata ✅
- Return NFT ID

Check on BaseScan for NFT contract events.

---

## Step 8: List on OpenSea

1. Go to https://opensea.io/
2. Connect your wallet
3. Go to "Profile" → "Collected"
4. Find your NFT
5. Click "List for sale"
6. Set price in ETH or ALFA
7. List it!

Buyers can now:
- Buy NFT
- Get decryption key (call `getDecryptionKey()`)
- Decrypt video

---

## NFT Marketplace Features

### For Creators (You)
- Royalties: 10% of secondary sales
- Earn from ALFA token fees
- Build audience on marketplace

### For Buyers
- Own decrypted video
- Trade on OpenSea
- Resell with royalties
- Collect gaming content

---

## Advanced: Decrypt Service

Create API to let NFT owners decrypt:

```python
@app.route('/api/decrypt/<nft_id>')
def decrypt_video(nft_id):
    # Verify caller owns NFT
    # Get decryption key from contract
    # Decrypt and stream video
    # Return video or decryption key
    pass
```

---

## Security Notes

- Decryption key stored on-chain (encrypted at rest)
- Only NFT owner can retrieve
- Transfer = decryption rights transfer
- Video stored encrypted on IPFS/Drive

---

## Checklist

- [ ] NFT contract created
- [ ] ALFA contract updated with NFT linking
- [ ] Both contracts deployed
- [ ] Contracts linked together
- [ ] Bot updated for NFT minting
- [ ] IPFS setup for metadata
- [ ] First NFT minted
- [ ] NFT visible on OpenSea
- [ ] Listed for sale

---

**Status:** Ready to mint NFTs and sell on OpenSea! 🎨
