"""Encryption Manager Module"""
import os
import hashlib
import logging
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)

class EncryptionManager:
    CHUNK_SIZE = 1024 * 1024
    AES_KEY_SIZE = 32
    AES_IV_SIZE = 16
    
    def __init__(self):
        self.backend = default_backend()
    
    def hash_file(self, file_path: str, algorithm: str = "sha256") -> str:
        try:
            if algorithm == "sha256":
                hasher = hashlib.sha256()
            elif algorithm == "sha384":
                hasher = hashlib.sha384()
            elif algorithm == "sha512":
                hasher = hashlib.sha512()
            else:
                hasher = hashlib.sha256()
            
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(self.CHUNK_SIZE)
                    if not chunk:
                        break
                    hasher.update(chunk)
            
            hash_value = hasher.hexdigest()
            logger.info(f"File hashed ({algorithm}): {hash_value[:16]}...")
            return hash_value
        except Exception as e:
            logger.error(f"Hashing error: {str(e)}")
            raise
    
    def encrypt_file(self, input_path: str):
        """Encrypt file and return output path"""
        output_path = input_path + ".encrypted"
        
        try:
            key = os.urandom(self.AES_KEY_SIZE)
            iv = os.urandom(self.AES_IV_SIZE)
            
            logger.info(f"Encrypting file: {input_path}")
            
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=self.backend)
            encryptor = cipher.encryptor()
            
            with open(input_path, 'rb') as infile, open(output_path, 'wb') as outfile:
                outfile.write(iv)
                
                while True:
                    chunk = infile.read(self.CHUNK_SIZE)
                    if not chunk:
                        break
                    
                    if len(chunk) % 16 != 0:
                        chunk += b'\x00' * (16 - len(chunk) % 16)
                    
                    encrypted_chunk = encryptor.update(chunk)
                    outfile.write(encrypted_chunk)
                
                final_chunk = encryptor.finalize()
                if final_chunk:
                    outfile.write(final_chunk)
            
            logger.info(f"File encrypted successfully: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            raise
    
    def decrypt_file(self, input_path: str, output_path: str, key: bytes) -> bool:
        try:
            logger.info(f"Decrypting file: {input_path}")
            
            with open(input_path, 'rb') as f:
                iv = f.read(self.AES_IV_SIZE)
                encrypted_data = f.read()
            
            if len(iv) != self.AES_IV_SIZE:
                raise ValueError("Invalid IV")
            
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=self.backend)
            decryptor = cipher.decryptor()
            
            decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
            decrypted_data = decrypted_data.rstrip(b'\x00')
            
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            logger.info(f"File decrypted successfully: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            return False
    
    def generate_key_iv(self):
        key = os.urandom(self.AES_KEY_SIZE)
        iv = os.urandom(self.AES_IV_SIZE)
        return key, iv
    
    def hash_data(self, data: bytes, algorithm: str = "sha256") -> str:
        if algorithm == "sha256":
            return hashlib.sha256(data).hexdigest()
        elif algorithm == "sha384":
            return hashlib.sha384(data).hexdigest()
        elif algorithm == "sha512":
            return hashlib.sha512(data).hexdigest()
        return hashlib.sha256(data).hexdigest()
