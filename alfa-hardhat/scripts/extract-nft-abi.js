import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

async function main() {
    const nftArtifact = JSON.parse(fs.readFileSync(path.join(__dirname, '../artifacts/contracts/ALFA_NFT.sol/ALFA_NFT.json'), 'utf8'));
    const abi = nftArtifact.abi;
    
    const outputPath = path.join(__dirname, '../abi/ALFA_NFT_ABI.json');
    fs.writeFileSync(outputPath, JSON.stringify(abi, null, 2));
    
    console.log("NFT ABI extracted to:", outputPath);
}

main();
