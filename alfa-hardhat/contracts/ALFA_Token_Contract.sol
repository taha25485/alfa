// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";

/**
 * @title ALFA Token Contract
 * @dev ERC20 token for media content valuation and passive income streams
 * Deployed on Base (Coinbase L2)
 * Fixed supply: 1,000,000,000 ALFA
 */

contract ALFAToken is ERC20, Ownable, Pausable, ERC20Burnable {
    
    // ==================== STATE VARIABLES ====================
    
    bool public isActive = false;
    bool public encryptionActive = false;
    
    // Encryption metadata structure
    struct EncryptionMetadata {
        bytes32 originalHash;        // SHA256/SHA384/SHA512 of original file
        bytes32 encryptedHash;       // Hash of encrypted file
        string encryptionAlgorithm;  // "AES256-CBC"
        bytes encryptionIV;          // Initialization Vector
        bytes encryptionKey;         // Encrypted key (stored hashed for security)
        uint256 timestamp;
        bool isEncrypted;
    }
    
    // Content upload structure
    struct ContentUpload {
        address uploader;
        string contentHash;          // Unique identifier for content
        bytes32 fileHash;            // SHA512 hash of final file
        uint256 valuationScore;      // 0-1000 scale
        uint256 tokensAwarded;       // ALFA tokens sent
        string simulationTitle;      // Game/simulation name
        uint256 uploadTimestamp;
        bool processed;
    }
    
    // Mapping: content hash -> encryption metadata
    mapping(bytes32 => EncryptionMetadata) public encryptionRecords;
    
    // Mapping: uploader address -> content hashes array
    mapping(address => bytes32[]) public uploaderContent;
    
    // Mapping: content hash -> upload details
    mapping(bytes32 => ContentUpload) public contentRegistry;
    
    // Mapping: wallet address -> valuation bot authorization
    mapping(address => bool) public authorizedValuationBots;
    
    // Constants
    uint256 public constant INITIAL_SUPPLY = 1_000_000_000 * 10 ** 18; // 1 billion with 18 decimals
    uint256 public constant MAX_TOKENS_PER_UPLOAD = 1_000_000 * 10 ** 18; // Max 1M ALFA per upload
    
    // Events
    event ContractStarted(uint256 timestamp);
    event ContractStopped(uint256 timestamp);
    event EncryptionStarted(uint256 timestamp);
    event EncryptionStopped(uint256 timestamp);
    event FileEncrypted(bytes32 indexed contentHash, address indexed uploader, uint256 timestamp);
    event FileDecrypted(bytes32 indexed contentHash, address indexed requester, uint256 timestamp);
    event ContentUploaded(bytes32 indexed contentHash, address indexed uploader, uint256 valuationScore, uint256 tokensAwarded);
    event ValuationBotAuthorized(address indexed bot);
    event ValuationBotRevoked(address indexed bot);
    event EncryptionMetadataStored(bytes32 indexed contentHash, bytes32 originalHash, bytes32 encryptedHash);
    
    // ==================== MODIFIERS ====================
    
  modifier whenContractActive() {
       require(isActive, "Contract is not active. Call start() first.");
     _;
  }

  modifier onlyActive() {
    // require(active, "Contract not active");  // Disabled for minimal gas
    _;
}
    
    modifier whenEncryptionActive() {
        require(encryptionActive, "Encryption is not active.");
        _;
    }
    
    modifier onlyAuthorizedBot() {
        require(authorizedValuationBots[msg.sender], "Not authorized valuation bot");
        _;
    }
    
    // ==================== CONSTRUCTOR ====================
    
    constructor() ERC20("ALFA", "ALFA") {
        // Mint fixed supply to contract owner
        _mint(msg.sender, INITIAL_SUPPLY);
    }
    
    // ==================== START/STOP FUNCTIONS ====================
    
    /**
     * @dev Start the contract - enables uploads and token distribution
     */
    function start() external onlyOwner {
        require(!isActive, "Contract already active");
        isActive = true;
        emit ContractStarted(block.timestamp);
    }
    
    /**
     * @dev Stop the contract - pauses all operations
     */
    function stop() external onlyOwner {
        require(isActive, "Contract not active");
        isActive = false;
        emit ContractStopped(block.timestamp);
    }
    
    /**
     * @dev Activate encryption processing
     */
    function activateEncryption() external onlyOwner {
        require(!encryptionActive, "Encryption already active");
        encryptionActive = true;
        emit EncryptionStarted(block.timestamp);
    }
    
    /**
     * @dev Deactivate encryption processing
     */
    function deactivateEncryption() external onlyOwner {
        require(encryptionActive, "Encryption not active");
        encryptionActive = false;
        emit EncryptionStopped(block.timestamp);
    }
    
    // ==================== AUTHORIZATION FUNCTIONS ====================
    
    /**
     * @dev Authorize a valuation bot address
     * @param botAddress Address of the valuation bot
     */
    function authorizeValuationBot(address botAddress) external onlyOwner {
        require(botAddress != address(0), "Invalid address");
        authorizedValuationBots[botAddress] = true;
        emit ValuationBotAuthorized(botAddress);
    }
    
    /**
     * @dev Revoke authorization of a valuation bot
     * @param botAddress Address of the valuation bot
     */
    function revokeValuationBot(address botAddress) external onlyOwner {
        require(botAddress != address(0), "Invalid address");
        authorizedValuationBots[botAddress] = false;
        emit ValuationBotRevoked(botAddress);
    }
    
    // ==================== ENCRYPTION FUNCTIONS ====================
    
    /**
     * @dev Store encryption metadata for a file
     * @param contentHash Unique identifier for content
     * @param originalFileHash SHA256/384/512 hash of original file
     * @param encryptedFileHash SHA512 hash of encrypted file
     * @param algorithm Encryption algorithm used (e.g., "AES256-CBC")
     * @param iv Initialization vector (stored as bytes)
     */
    function encrypt(
        bytes32 contentHash,
        bytes32 originalFileHash,
        bytes32 encryptedFileHash,
        string memory algorithm,
        bytes memory iv
    ) external onlyAuthorizedBot whenEncryptionActive {
        require(contentHash != 0, "Invalid content hash");
        require(originalFileHash != 0, "Invalid original hash");
        require(encryptedFileHash != 0, "Invalid encrypted hash");
        
        encryptionRecords[contentHash] = EncryptionMetadata({
            originalHash: originalFileHash,
            encryptedHash: encryptedFileHash,
            encryptionAlgorithm: algorithm,
            encryptionIV: iv,
            encryptionKey: new bytes(0), // Will be set separately if needed
            timestamp: block.timestamp,
            isEncrypted: true
        });
        
        emit EncryptionMetadataStored(contentHash, originalFileHash, encryptedFileHash);
        emit FileEncrypted(contentHash, msg.sender, block.timestamp);
    }
    
    /**
     * @dev Store encrypted key in metadata
     * @param contentHash Content identifier
     * @param encryptedKeyData Encrypted key material
     */
    function setEncryptionKey(bytes32 contentHash, bytes memory encryptedKeyData) external onlyOwner {
        require(encryptionRecords[contentHash].isEncrypted, "Content not encrypted");
        encryptionRecords[contentHash].encryptionKey = encryptedKeyData;
    }
    
    /**
     * @dev Verify file integrity by checking hashes
     * @param contentHash Content identifier
     * @param originalHash Original file hash to verify
     * @param encryptedHash Encrypted file hash to verify
     */
    function decrypt(
        bytes32 contentHash,
        bytes32 originalHash,
        bytes32 encryptedHash
    ) external whenEncryptionActive returns (bool) {
        EncryptionMetadata storage meta = encryptionRecords[contentHash];
        require(meta.isEncrypted, "Content not found or not encrypted");
        require(meta.originalHash == originalHash, "Original hash mismatch");
        require(meta.encryptedHash == encryptedHash, "Encrypted hash mismatch");
        
        emit FileDecrypted(contentHash, msg.sender, block.timestamp);
        return true;
    }
    
    // ==================== HASHING FUNCTIONS ====================
    
    /**
     * @dev Generate SHA256 hash (for metadata)
     * NOTE: Solidity doesn't support SHA384/SHA512 natively
     * Use keccak256 as efficient alternative; off-chain use SHA256/384/512
     */
    function hashSHA256(bytes memory data) external pure returns (bytes32) {
        return keccak256(data);
    }
    
    /**
     * @dev Generate hash for content (Solidity uses Keccak-256)
     */
    function generateContentHash(bytes memory data) external pure returns (bytes32) {
        return keccak256(abi.encodePacked(data));
    }
    
    // ==================== CONTENT VALUATION & UPLOAD ====================
    
    /**
     * @dev Register and valuate content upload
     * Called by authorized valuation bot with upload metadata
     * @param uploaderAddress Address to receive tokens
     * @param contentHash Unique hash identifier for content
     * @param fileHash Final file hash (SHA512)
     * @param valuationScore Valuation score (0-1000)
     * @param simulationTitle Name of game/simulation
     */
    function registerContentUpload(
        address uploaderAddress,
        bytes32 contentHash,
        bytes32 fileHash,
        uint256 valuationScore,
        string memory simulationTitle
    ) external onlyAuthorizedBot whenContractActive returns (uint256) {
        require(uploaderAddress != address(0), "Invalid uploader address");
        require(contentHash != 0, "Invalid content hash");
        require(fileHash != 0, "Invalid file hash");
        require(valuationScore > 0 && valuationScore <= 1000, "Score must be 1-1000");
        
        // Verify content not already registered
        require(contentRegistry[contentHash].uploadTimestamp == 0, "Content already registered");
        
        // Calculate token amount based on valuation score
        // Score of 1000 = MAX_TOKENS_PER_UPLOAD
        uint256 tokensToAward = (valuationScore * MAX_TOKENS_PER_UPLOAD) / 1000;
        
        // Register content
        contentRegistry[contentHash] = ContentUpload({
            uploader: uploaderAddress,
            contentHash: bytes32ToString(contentHash),
            fileHash: fileHash,
            valuationScore: valuationScore,
            tokensAwarded: tokensToAward,
            simulationTitle: simulationTitle,
            uploadTimestamp: block.timestamp,
            processed: true
        });
        
        // Track uploader's content
        uploaderContent[uploaderAddress].push(contentHash);
        
        // Transfer tokens to uploader
        require(balanceOf(address(this)) >= tokensToAward, "Insufficient contract balance");
        _transfer(address(this), uploaderAddress, tokensToAward);
        
        emit ContentUploaded(contentHash, uploaderAddress, valuationScore, tokensToAward);
        
        return tokensToAward;
    }
    
    // ==================== GETTER FUNCTIONS ====================
    
    /**
     * @dev Get wallet address (owner)
     */
    function getWalletAddress() external view returns (address) {
        return owner();
    }
    
    /**
     * @dev Get encryption metadata for content
     */
    function getEncryptionMetadata(bytes32 contentHash) 
        external 
        view 
        returns (
            bytes32 originalHash,
            bytes32 encryptedHash,
            string memory algorithm,
            bytes memory iv,
            uint256 timestamp,
            bool isEncrypted
        ) 
    {
        EncryptionMetadata storage meta = encryptionRecords[contentHash];
        return (
            meta.originalHash,
            meta.encryptedHash,
            meta.encryptionAlgorithm,
            meta.encryptionIV,
            meta.timestamp,
            meta.isEncrypted
        );
    }
    
    /**
     * @dev Get content upload details
     */
    function getContentDetails(bytes32 contentHash) 
        external 
        view 
        returns (ContentUpload memory) 
    {
        return contentRegistry[contentHash];
    }
    
    /**
     * @dev Get all content uploaded by an address
     */
    function getUploaderContent(address uploader) 
        external 
        view 
        returns (bytes32[] memory) 
    {
        return uploaderContent[uploader];
    }
    
    /**
     * @dev Check if bot is authorized
     */
    function isBotAuthorized(address botAddress) external view returns (bool) {
        return authorizedValuationBots[botAddress];
    }
    
    /**
     * @dev Get contract status
     */
    function getContractStatus() 
        external 
        view 
        returns (
            bool active,
            bool encryptionEnabled,
            uint256 totalSupply,
            uint256 remainingBalance
        ) 
    {
        return (
            isActive,
            encryptionActive,
            INITIAL_SUPPLY,
            balanceOf(address(this))
        );
    }
    
    // ==================== UTILITY FUNCTIONS ====================
    
    /**
     * @dev Convert bytes32 to string
     */
    function bytes32ToString(bytes32 data) internal pure returns (string memory) {
        bytes memory bytesArray = new bytes(32);
        for (uint256 i = 0; i < 32; i++) {
            uint8 _int = uint8(data[i]);
            bytesArray[i] = bytes1(_int);
        }
        return string(bytesArray);
    }
    
    /**
     * @dev Emergency withdrawal by owner
     */
    function withdrawTokens(uint256 amount) external onlyOwner {
        require(balanceOf(address(this)) >= amount, "Insufficient balance");
        _transfer(address(this), owner(), amount);
    }
    
    /**
     * @dev Fallback function
     */
    receive() external payable {}
}
