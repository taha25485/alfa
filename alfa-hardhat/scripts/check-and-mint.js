import pkg from "hardhat";
const { ethers } = pkg;

async function main() {
  const contractAddress = "0x24fB0134586d5aec98E4b57c9bBcE7B79302B837";
  const contract = await ethers.getContractAt("ALFAToken", contractAddress);
  const [deployer] = await ethers.getSigners();
  
  const totalSupply = await contract.totalSupply();
  const contractBalance = await contract.balanceOf(contractAddress);
  const deployerBalance = await contract.balanceOf(deployer.address);
  
  console.log("📊 Token Status:");
  console.log("Total Supply:", ethers.formatUnits(totalSupply, 18));
  console.log("Contract Balance:", ethers.formatUnits(contractBalance, 18));
  console.log("Deployer Balance:", ethers.formatUnits(deployerBalance, 18));
  
  if (contractBalance == 0n && deployerBalance > 0n) {
    console.log("\n⏳ Transferring tokens to contract...");
    const tx = await contract.transfer(contractAddress, deployerBalance);
    await tx.wait();
    
    const newContractBalance = await contract.balanceOf(contractAddress);
    console.log("✅ Tokens transferred!");
    console.log("New Contract Balance:", ethers.formatUnits(newContractBalance, 18));
  }
}

main().catch(console.error);
