import pkg from "hardhat";
const { ethers } = pkg;

async function main() {
  const contractAddress = "0xA2F5185bd40213B445034831980d65F7457BA406";
  const contract = await ethers.getContractAt("ALFAToken", contractAddress);

  try {
    const active = await contract.active();
    const encrypted = await contract.encryptionActive();
    
    console.log("Active:", active);
    console.log("Encryption Active:", encrypted);
  } catch (e) {
    console.log("Error:", e.message);
  }
}

main().catch(console.error);
