import pkg from "hardhat";
const { ethers } = pkg;

async function main() {
  const contractAddress = "0x14775BA68c83C6EE725C7d4686EDBf8E6156fC46";
  const contract = await ethers.getContractAt("ALFAToken", contractAddress);

  console.log("⏳ Initializing contract...");
  const tx = await contract.start({ gasLimit: 100000 });
  await tx.wait();

  console.log("✅ Contract initialized!");
  console.log("📍 Contract:", contractAddress);
}

main().catch(console.error);
