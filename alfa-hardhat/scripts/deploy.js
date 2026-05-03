import { ethers } from "hardhat";
import fs from "fs";

async function main() {
  console.log("🚀 Deploying ALFA Token Contract to Base...\n");

  // Get deployer account
  const [deployer] = await ethers.getSigners();
  console.log(`📝 Deploying with account: ${deployer.address}`);

  // Get account balance
  const balance = await ethers.provider.getBalance(deployer.address);
  const balanceInEth = ethers.formatEther(balance);
  console.log(`💰 Account balance: ${balanceInEth} ETH\n`);

  if (parseFloat(balanceInEth) < 0.01) {
    console.log("⚠️  Warning: Low balance. You need at least 0.01 ETH for gas.");
  }

  // Get contract factory
  const ALFAToken = await ethers.getContractFactory("ALFAToken");
  console.log("📦 Compiling contract...");

  // Deploy contract
  console.log("⏳ Deploying (this may take 1-2 minutes)...\n");
  const alfaToken = await ALFAToken.deploy();

  // Wait for deployment
  await alfaToken.waitForDeployment();
  const contractAddress = await alfaToken.getAddress();

  console.log("✅ ALFA Token deployed successfully!\n");
  console.log(`📍 Contract Address: ${contractAddress}`);
  console.log(`🔗 View on BaseScan: https://basescan.io/address/${contractAddress}\n`);

  // Call start() function
  console.log("⏳ Calling start() function...");
  const startTx = await alfaToken.start();
  await startTx.wait();
  console.log("✅ Contract activated (start() called)\n");

  // Call activateEncryption() function
  console.log("⏳ Calling activateEncryption() function...");
  const encTx = await alfaToken.activateEncryption();
  await encTx.wait();
  console.log("✅ Encryption activated\n");

  // Get initial status
  const status = await alfaToken.getContractStatus();
  console.log("📊 Contract Status:");
  console.log(`   • Active: ${status[0]}`);
  console.log(`   • Encryption Enabled: ${status[1]}`);
  console.log(`   • Total Supply: ${ethers.formatEther(status[2])} ALFA`);
  console.log(`   • Available Balance: ${ethers.formatEther(status[3])} ALFA\n`);

  // Save deployment info
  const deploymentInfo = {
    network: "base",
    contractAddress: contractAddress,
    deployerAddress: deployer.address,
    deploymentDate: new Date().toISOString(),
    blockNumber: await ethers.provider.getBlockNumber(),
    transactionHash: alfaToken.deploymentTransaction()?.hash || "N/A",
  };

  fs.writeFileSync(
    "deployment-info.json",
    JSON.stringify(deploymentInfo, null, 2)
  );

  console.log("💾 Deployment info saved to: deployment-info.json");
  console.log("\n🎉 Deployment Complete! Ready to deploy Telegram bot.\n");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
