#!/usr/bin/env python3

import os
import asyncio
import logging
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.request import HTTPXRequest

from file_processor import FileProcessor
from encryption_manager import EncryptionManager
from blockchain_manager import BlockchainManager
from valuation_engine import ValuationEngine
from nft_minter import NFTMinter


# ----------------------------
# Setup
# ----------------------------

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEB3 = os.getenv("WEB3_PROVIDER_URL")
CONTRACT = os.getenv("ALFA_CONTRACT_ADDRESS")
NFT_CONTRACT = os.getenv(
    "NFT_CONTRACT_ADDRESS",
    "0x8F155cE7Df07693Ea82bA6061aB0731Ad0531A4a",
)
ABI = os.getenv("CONTRACT_ABI_PATH", "abi/ALFA_Contract_ABI.json")

BOT_API_URL = os.getenv("BOT_API_URL", "http://127.0.0.1:8081")
USE_LOCAL_API = os.getenv("USE_LOCAL_API", "true").lower() == "true"

UPLOAD_DIR = "/tmp/alfa_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

users = {}
bot_obj = None


# ----------------------------
# Bot Object
# ----------------------------

class ALFABot:
    def __init__(self):
        self.fp = FileProcessor()
        self.enc = EncryptionManager()

        self.bc = BlockchainManager(
            provider_url=WEB3,
            contract_address=CONTRACT,
            abi_path=ABI,
        )

        self.nft = NFTMinter(
            provider_url=WEB3,
            nft_contract_address=NFT_CONTRACT,
            nft_abi_path="abi/ALFA_NFT_ABI.json",
        )

        self.val = ValuationEngine()


# ----------------------------
# Commands
# ----------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    users[uid] = {"step": "file"}

    await update.message.reply_text(
        "🎮 ALFA\n\n"
        "📹 Send video!"
    )


async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    users[uid] = {"step": "file"}

    await update.message.reply_text("📹 Send video")


# ----------------------------
# Step 1: File Upload
# ----------------------------

async def handle_file_step(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int):
    message = update.message

    # Users may send video as either Telegram video or document/file
    media = message.video or message.document

    if not media:
        await message.reply_text("Please send a video file.")
        return

    raw_filename = getattr(media, "file_name", None)

    if raw_filename:
        filename = os.path.basename(raw_filename)
    else:
        filename = f"{media.file_unique_id}.mp4"

    logger.info(
        "Incoming media: name=%s size=%s file_id=%s",
        filename,
        getattr(media, "file_size", None),
        media.file_id,
    )

    try:
        await message.reply_text("⏳ Downloading...")

        logger.info("Calling get_file...")
        tg_file = await context.bot.get_file(media.file_id)
        logger.info("get_file complete. file_path=%s", tg_file.file_path)

        local_path = os.path.join(UPLOAD_DIR, f"{uid}_{filename}")

        logger.info("Starting download_to_drive...")
        await tg_file.download_to_drive(local_path)
        logger.info("download_to_drive finished.")

        size = os.path.getsize(local_path)
        logger.info("Downloaded file: %s bytes -> %s", size, local_path)

        users[uid]["file"] = local_path
        users[uid]["step"] = "wallet"

        await message.reply_text("✅ File received. Send wallet address.")

    except Exception as e:
        logger.error("Download error: %s", e, exc_info=True)
        await message.reply_text(f"Error during download: {e}")


# ----------------------------
# Step 2: Wallet
# ----------------------------

async def handle_wallet_step(update: Update, uid: int):
    message = update.message
    wallet = (message.text or "").strip()

    if not wallet.startswith("0x") or len(wallet) != 42:
        await message.reply_text("Bad wallet address. Send a valid 0x wallet.")
        return

    users[uid]["wallet"] = wallet
    users[uid]["step"] = "game"

    await message.reply_text("Game name?")


# ----------------------------
# Step 3: Processing
# ----------------------------

async def handle_game_step(update: Update, uid: int):
    global bot_obj

    message = update.message
    game = (message.text or "").strip()

    fp = users[uid].get("file")
    wallet = users[uid].get("wallet")

    if not fp or not wallet:
        await message.reply_text("Missing data. Please run /start again.")
        users.pop(uid, None)
        return

    if not os.path.exists(fp):
        await message.reply_text("Uploaded file was not found. Please upload again.")
        users.pop(uid, None)
        return

    status_message = await message.reply_text("Processing... this may take a while.")

    try:
        logger.info("Starting processing for uid=%s game=%s file=%s", uid, game, fp)

        logger.info("Converting to MKV...")
        mkv = await asyncio.to_thread(bot_obj.fp.convert_to_mkv, fp)
        logger.info("MKV created: %s", mkv)

        logger.info("Hashing original file with sha256...")
        original_hash = await asyncio.to_thread(
            bot_obj.enc.hash_file,
            fp,
            "sha256",
        )
        logger.info("Original hash: %s", original_hash)

        logger.info("Encrypting MKV file...")
        encrypted_path = await asyncio.to_thread(
            bot_obj.enc.encrypt_file,
            mkv,
        )
        logger.info("Encrypted file: %s", encrypted_path)

        logger.info("Hashing encrypted file with sha512...")
        encrypted_hash = await asyncio.to_thread(
            bot_obj.enc.hash_file,
            encrypted_path,
            "sha512",
        )
        logger.info("Encrypted hash: %s", encrypted_hash)

        logger.info("Extracting metadata...")
        metadata = await asyncio.to_thread(
            bot_obj.fp.extract_metadata,
            fp,
        )
        logger.info("Metadata extracted: %s", metadata)

        logger.info("Scoring content...")
        score = bot_obj.val.score_content(game, metadata)
        logger.info("Valuation score: %s", score)

        logger.info("Registering content upload on blockchain...")
        tx = await asyncio.to_thread(
            bot_obj.bc.register_content_upload,
            uploader=wallet,
            game_name=game,
            valuation_score=score,
            original_hash=original_hash,
            encrypted_hash=encrypted_hash,
        )
        logger.info("Blockchain upload tx: %s", tx)

        tokens = (score / 1000) * 1_000_000

        await asyncio.sleep(2)

        logger.info("Minting NFT...")
        nft_tx = await asyncio.to_thread(
            bot_obj.nft.mint_nft,
            uploader=wallet,
            game_name=game,
            valuation_score=score,
            original_hash=original_hash,
            encrypted_hash=encrypted_hash,
            metadata_uri=f"ipfs://Qm{original_hash[:16]}",
        )
        logger.info("NFT tx: %s", nft_tx)

        await status_message.edit_text(
            f"✅ Done!\n"
            f"💰 {tokens:,.0f} ALFA\n"
            f"🎨 NFT minted\n\n"
            f"Upload TX:\n"
            f"https://basescan.org/tx/{tx}\n\n"
            f"NFT TX:\n"
            f"https://basescan.org/tx/{nft_tx}"
        )

    except Exception as e:
        logger.error("Processing error: %s", e, exc_info=True)

        try:
            await status_message.edit_text(f"Error: {e}")
        except Exception:
            await message.reply_text(f"Error: {e}")

    finally:
        users.pop(uid, None)


# ----------------------------
# Main Message Router
# ----------------------------

async def handle_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    uid = update.effective_user.id

    if uid not in users:
        return

    step = users[uid].get("step")

    if step == "file":
        await handle_file_step(update, context, uid)

    elif step == "wallet":
        if update.message.text:
            await handle_wallet_step(update, uid)
        else:
            await update.message.reply_text("Please send your wallet address as text.")

    elif step == "game":
        if update.message.text:
            await handle_game_step(update, uid)
        else:
            await update.message.reply_text("Please send the game name as text.")


# ----------------------------
# Build Telegram Application
# ----------------------------

def build_application() -> Application:
    if not TOKEN:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN in .env")

    request = HTTPXRequest(
        connection_pool_size=8,
        read_timeout=600,
        write_timeout=600,
        connect_timeout=60,
        pool_timeout=60,
    )

    builder = (
        Application.builder()
        .token(TOKEN)
        .request(request)
    )

    if USE_LOCAL_API:
        logger.info("Using local Telegram Bot API server: %s", BOT_API_URL)

        builder = (
            builder
            .base_url(f"{BOT_API_URL}/bot")
            .base_file_url(f"{BOT_API_URL}/file/bot")
            .local_mode(True)
        )
    else:
        logger.info("Using Telegram cloud Bot API")

    return builder.build()


# ----------------------------
# Main
# ----------------------------

def main():
    global bot_obj

    logger.info("Initializing ALFA bot...")
    bot_obj = ALFABot()

    app = build_application()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("upload", upload))
    app.add_handler(MessageHandler(filters.ALL, handle_all))

    logger.info("Bot starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
