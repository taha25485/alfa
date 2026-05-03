import pkg from "hardhat";
const { ethers } = pkg;

async function main() {
  const contractAddress = "0x24fB0134586d5aec98E4b57c9bBcE7B79302B837";
  
  // Get address from private key
  const privateKey = "0xb6e8bcbcdb5db184c2dae199f2e16d9b1cf4f32bd3a0ab00049534dd5cd9c195";
  const wallet = new ethers.Wallet(privateKey);
  const botSignerAddress = wallet.address;
  
  console.log("⏳ Authorizing bot signer:", botSignerAddress);
  
  const contract = await ethers.getContractAt("ALFAToken", contractAddress);
  const tx = await contract.authorizeValuationBot(botSignerAddress);
  const receipt = await tx.wait();
  
  console.log("✅ Bot signer authorized!");
  console.log("📍 Contract:", contractAddress);
  console.log("🤖 Authorized:", botSignerAddress);
  console.log("📝 Tx:", receipt.hash);
}

main().catch(console.error);
