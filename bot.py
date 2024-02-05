#!/usr/bin/env python3
import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackContext, MessageHandler, filters

logging.basicConfig(level=logging.WARNING, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
                    filename="bot.log",
                    filemode="a")

load_dotenv()

TOKEN = os.getenv('FORWARDER_TOKEN')
SOURCE_CHAT = os.getenv('SOURCE_CHAT_ID')
TARGET_CHAT = os.getenv('TARGET_GROUP_ID')

HASHTAG_THREAD_MAP = {
    '#знания': 6,
    '#инструменты': 14,
    '#текст': 7,
}

async def forward_hashtag_messages(update: Update, context: CallbackContext):
    message = update.message
    words = ""
    hashtags = []
    if not message.text:
        words = message.caption.split()
        hashtags = [word for word in words if word[0]=='#']
    if message.text:
        words = message.text.split()
        hashtags = [word for word in words if word[0]=='#']
    chat_id = SOURCE_CHAT.replace("@", "")
    link = f"https://t.me/{chat_id}/{message.message_id}"

    if message.is_topic_message:
        topic_id = message.message_thread_id
        link = f"https://t.me/{chat_id}/{topic_id}/{message.message_id}"

    # Ignore messages that contain only hashtags
    if len(words) == len(hashtags) and message.caption is None:
         return

    target_received = False

    for tag in hashtags:
        thread_id = HASHTAG_THREAD_MAP.get(tag, None)
        if thread_id is not None:
            await context.bot.send_message(chat_id=TARGET_CHAT,
                                    text=f"[Go to message]({link}) ↓",
                                    disable_web_page_preview=True,
                                    parse_mode="MarkdownV2",
                                    message_thread_id=thread_id)
            await context.bot.forward_message(
                chat_id=TARGET_CHAT,
                from_chat_id=SOURCE_CHAT,
                message_thread_id=thread_id,
                message_id=update.message.message_id
            )
            target_received = True

    if not target_received and hashtags:
        await context.bot.send_message(chat_id=TARGET_CHAT,
                                    text=f"[Go to message]({link}) ↓",
                                    disable_web_page_preview=True,
                                    parse_mode="MarkdownV2",
                                    message_thread_id=30)
        await context.bot.forward_message(chat_id=TARGET_CHAT,
                                    from_chat_id=SOURCE_CHAT,
                                    message_thread_id=30,
                                    # forwarding to the Support thread
                                    message_id=update.message.message_id)

def main():
    print("I'm working")

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward_hashtag_messages))

    application.run_polling()

if __name__ == '__main__':
    main()
