// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract ALFA_NFT is ERC721, ERC721URIStorage, Ownable {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIdCounter;
    
    struct ContentMetadata {
        string gameName;
        uint256 valuationScore;
        bytes32 originalHash;
        bytes32 encryptedHash;
        uint256 uploadTimestamp;
        address uploader;
    }
    
    mapping(uint256 => ContentMetadata) public contentMetadata;
    
    event ContentNFTMinted(
        uint256 indexed tokenId,
        address indexed uploader,
        string gameName,
        uint256 valuationScore
    );
    
    constructor() ERC721("ALFA_Content", "ALFA_NFT") {}
    
    function mintContentNFT(
        address uploader,
        string memory gameName,
        uint256 valuationScore,
        bytes32 originalHash,
        bytes32 encryptedHash,
        string memory uri
    ) public onlyOwner returns (uint256) {
        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();
        
        _safeMint(uploader, tokenId);
        _setTokenURI(tokenId, uri);
        
        contentMetadata[tokenId] = ContentMetadata({
            gameName: gameName,
            valuationScore: valuationScore,
            originalHash: originalHash,
            encryptedHash: encryptedHash,
            uploadTimestamp: block.timestamp,
            uploader: uploader
        });
        
        emit ContentNFTMinted(tokenId, uploader, gameName, valuationScore);
        return tokenId;
    }
    
    function getContentMetadata(uint256 tokenId) public view returns (ContentMetadata memory) {
        return contentMetadata[tokenId];
    }
    
    function _burn(uint256 tokenId) internal override(ERC721, ERC721URIStorage) {
        super._burn(tokenId);
    }
    
    function tokenURI(uint256 tokenId) public view override(ERC721, ERC721URIStorage) returns (string memory) {
        return super.tokenURI(tokenId);
    }
    
    function supportsInterface(bytes4 interfaceId) public view override(ERC721, ERC721URIStorage) returns (bool) {
        return super.supportsInterface(interfaceId);
    }
}

