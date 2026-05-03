import hre from "hardhat";

async function main() {
    const NFT = await hre.ethers.getContractFactory("ALFA_NFT");
    const nft = await NFT.deploy();
    await nft.waitForDeployment();
    
    const address = await nft.getAddress();
    console.log("NFT deployed to:", address);
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
