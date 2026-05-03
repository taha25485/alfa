#!/usr/bin/env python3
import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

load_dotenv()
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("START CALLED")
    await update.message.reply_text("Started!")

async def handle_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("=== HANDLER CALLED ===")
    logger.info(f"Type: {type(update.message)}")
    logger.info(f"Has text: {update.message.text}")
    logger.info(f"Has video: {update.message.video}")
    await update.message.reply_text(f"Got: {update.message.text}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, handle_all))
    
    logger.info("Test bot starting...")
    app.run_polling()

if __name__ == "__main__":
    main()
