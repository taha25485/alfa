"""NFT Minter Module"""
import os
import json
import logging
import time
from web3 import Web3
from eth_account import Account

logger = logging.getLogger(__name__)

class NFTMinter:
    def __init__(self, provider_url: str, nft_contract_address: str, nft_abi_path: str):
        self.w3 = Web3(Web3.HTTPProvider(provider_url))
        
        if not self.w3.is_connected():
            raise ConnectionError(f"Cannot connect to {provider_url}")
        
        logger.info(f"Connected to network: {self.w3.eth.chain_id}")
        
        if not os.path.exists(nft_abi_path):
            raise FileNotFoundError(f"NFT ABI not found: {nft_abi_path}")
        
        with open(nft_abi_path, 'r') as f:
            abi = json.load(f)
        
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(nft_contract_address),
            abi=abi
        )
        
        self.nft_address = Web3.to_checksum_address(nft_contract_address)
        self.signer_key = os.getenv("SIGNER_PRIVATE_KEY")
        self.signer_account = Account.from_key(self.signer_key)
        self.signer_address = self.signer_account.address
        
        logger.info(f"NFT Minter initialized")
        logger.info(f"NFT Contract: {nft_contract_address}")
        logger.info(f"Signer: {self.signer_address}")
    
    def mint_nft(self, uploader: str, game_name: str, valuation_score: int, original_hash: str, encrypted_hash: str, metadata_uri: str) -> str:
        """Mint NFT for content"""
        try:
            # Wait a moment for previous transaction to be included
            time.sleep(2)
            
            uploader = Web3.to_checksum_address(uploader)
            oh_bytes32 = self._string_to_bytes32(original_hash)
            eh_bytes32 = self._string_to_bytes32(encrypted_hash)
            
            logger.info(f"Minting NFT for {uploader}...")
            
            func = self.contract.functions.mintContentNFT(
                uploader,
                game_name,
                valuation_score,
                oh_bytes32,
                eh_bytes32,
                metadata_uri
            )
            
            tx = self._build_and_send_transaction(func)
            logger.info(f"NFT minted: Tx: {tx}")
            return tx
        except Exception as e:
            logger.error(f"NFT minting error: {str(e)}", exc_info=True)
            raise
    
    def _build_and_send_transaction(self, function) -> str:
        """Build, sign, and send transaction"""
        try:
            # Get fresh nonce
            nonce = self.w3.eth.get_transaction_count(self.signer_address)
            logger.info(f"Nonce: {nonce}")
            
            tx = function.build_transaction({
                'from': self.signer_address,
                'nonce': nonce,
                'gas': 500000,
                'gasPrice': self.w3.eth.gas_price,
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.signer_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if receipt['status'] == 0:
                raise Exception(f"Transaction failed: {tx_hash.hex()}")
            
            return tx_hash.hex()
        except Exception as e:
            logger.error(f"Transaction error: {str(e)}", exc_info=True)
            raise
    
    def _string_to_bytes32(self, value: str) -> bytes:
        """Convert string to bytes32"""
        if value.startswith('0x'):
            value = value[2:]
        
        if len(value) == 64:
            return bytes.fromhex(value)
        
        return Web3.keccak(text=value)
