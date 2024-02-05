#!/usr/bin/env python3
import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext, ContextTypes, MessageHandler, filters

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename="bot.log",filemode="a")

load_dotenv()

TOKEN = os.getenv('FORWARDER_TOKEN')
SOURCE_CHANNEL = os.getenv('SOURCE_CHAT_ID')
TARGET_GROUP = os.getenv('TARGET_GROUP_ID')

HASHTAG_THREAD_MAP = {
    '#знания': 6,
    '#инструменты': 14,
    '#текст': 7,
}

async def forward_hashtag_messages(update: Update, context: CallbackContext):
    message = update.message
    words = message.text.split()
    hashtags = [word for word in words if word[0]=='#']
    channel_id = SOURCE_CHANNEL.replace("@", "")
    link = f"https://t.me/{channel_id}/{message.message_id}"

    # Ignore messages that contain only hashtags
    if len(words) == len(hashtags):
        return
    
    target_received = False

    for tag in hashtags:
        thread_id = HASHTAG_THREAD_MAP.get(tag, None)
        if thread_id is not None:
            await context.bot.send_message(chat_id=TARGET_GROUP,
                                    text=f"[Go to message]({link}) ↓",
                                    disable_web_page_preview=True,
                                    parse_mode="MarkdownV2",
                                    message_thread_id=thread_id)
            await context.bot.forward_message(
                chat_id=TARGET_GROUP,
                from_chat_id=SOURCE_CHANNEL,
                message_thread_id=thread_id,
                message_id=update.message.message_id
            )
            target_received = True

    if not target_received and hashtags:
        await context.bot.send_message(chat_id=TARGET_GROUP,
                                    text=f"[Go to message]({link}) ↓",
                                    disable_web_page_preview=True,
                                    parse_mode="MarkdownV2",
                                    message_thread_id=30)
        await context.bot.forward_message(chat_id=TARGET_GROUP,
                                    from_chat_id=SOURCE_CHANNEL,
                                    message_thread_id=30,
                                    # forwarding to the Support thread
                                    message_id=update.message.message_id)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text='I am a bot to forward messages.')

def main():
    print("I'm working")

    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_hashtag_messages))

    application.run_polling()

if __name__ == '__main__':
    main()
