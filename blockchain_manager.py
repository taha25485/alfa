"""Blockchain Manager Module"""
import os
import json
import logging
from web3 import Web3
from eth_account import Account

logger = logging.getLogger(__name__)

class BlockchainManager:
    def __init__(self, provider_url: str, contract_address: str, abi_path: str):
        self.w3 = Web3(Web3.HTTPProvider(provider_url))
        
        if not self.w3.is_connected():
            raise ConnectionError(f"Cannot connect to {provider_url}")
        
        logger.info(f"Connected to network: {self.w3.eth.chain_id}")
        
        if not os.path.exists(abi_path):
            raise FileNotFoundError(f"ABI not found: {abi_path}")
        
        with open(abi_path, 'r') as f:
            abi = json.load(f)
        
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(contract_address),
            abi=abi
        )
        
        self.contract_address = Web3.to_checksum_address(contract_address)
        
        self.signer_key = os.getenv("SIGNER_PRIVATE_KEY")
        if not self.signer_key:
            raise ValueError("SIGNER_PRIVATE_KEY not set")
        
        self.signer_account = Account.from_key(self.signer_key)
        self.signer_address = self.signer_account.address
        
        logger.info("Blockchain manager initialized")
        logger.info(f"Contract: {contract_address}")
        logger.info(f"Signer: {self.signer_address}")
    
    def register_content_upload(self, uploader: str, game_name: str, valuation_score: int, original_hash: str, encrypted_hash: str) -> str:
        """Register content upload on blockchain"""
        try:
            uploader = Web3.to_checksum_address(uploader)
            
            func = self.contract.functions.registerContentUpload(
                uploader,
                self._string_to_bytes32(original_hash),
                self._string_to_bytes32(encrypted_hash),
                valuation_score,
                game_name
            )
            
            tx = self._build_and_send_transaction(func)
            logger.info(f"Content registered: Tx: {tx}")
            return tx
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            raise
    
    def _build_and_send_transaction(self, function) -> str:
        """Build, sign, and send transaction"""
        try:
            nonce = self.w3.eth.get_transaction_count(self.signer_address)
            
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
            logger.error(f"Transaction error: {str(e)}")
            raise
    
    def _string_to_bytes32(self, value: str) -> bytes:
        """Convert string to bytes32"""
        if value.startswith('0x'):
            value = value[2:]
        
        if len(value) == 64:
            return bytes.fromhex(value)
        
        return Web3.keccak(text=value)

