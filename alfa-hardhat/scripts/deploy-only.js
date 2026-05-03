import pkg from "hardhat";
const { ethers } = pkg;

async function main() {
  console.log("🚀 Deploying ALFA Token Contract to Base...");
  
  const [deployer] = await ethers.getSigners();
  console.log("📝 Deploying with account:", deployer.address);
  
  const balance = await ethers.provider.getBalance(deployer.address);
  console.log("💰 Account balance:", ethers.formatEther(balance), "ETH");
  
  const ALFAToken = await ethers.getContractFactory("ALFAToken");
  const contract = await ALFAToken.deploy();
  await contract.waitForDeployment();
  
  const contractAddress = await contract.getAddress();
  console.log("✅ ALFA Token deployed!");
  console.log("📍 Contract Address:", contractAddress);
  console.log("🔗 View on BaseScan: https://basescan.io/address/" + contractAddress);
}

main().catch(console.error);
