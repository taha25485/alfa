import pkg from "hardhat";
const { ethers } = pkg;

async function main() {
  const contractAddress = "0x24fB0134586d5aec98E4b57c9bBcE7B79302B837";
  const contract = await ethers.getContractAt("ALFAToken", contractAddress);
  
  console.log("⏳ Calling start() to activate contract...");
  const tx = await contract.start({ gasLimit: 100000 });
  const receipt = await tx.wait();
  
  console.log("✅ Contract activated!");
  console.log("📍 Contract:", contractAddress);
  console.log("📝 Tx:", receipt.hash);
  
  // Verify it's active
  const active = await contract.active();
  console.log("🔥 Active:", active);
}

main().catch(console.error);
