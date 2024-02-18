#!/usr/bin/env python3
import logging
import os
from hashtag_map import HASHTAG_THREAD_MAP
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackContext, MessageHandler, filters, CommandHandler

logging.basicConfig(level=logging.WARNING, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
                    filename="bot.log",
                    filemode="a")

load_dotenv()

TOKEN = os.getenv('FORWARDER_TOKEN')
TARGET_CHAT = os.getenv('TARGET_GROUP_ID')

async def forward_hashtag_messages(update: Update, context: CallbackContext):
    message = update.message
    words = ""
    hashtags = []
    if message.text:
        words = message.text.split()
        hashtags = [word for word in words if word[0]=='#']
    if not message.text:
        words = message.caption.split()
        hashtags = [word for word in words if word[0]=='#']
    numeric_chat_id = update.message.chat.id
    chat_id = str(numeric_chat_id).replace("-100", "")
    link = f"https://t.me/c/{chat_id}/{message.message_id}"
    user = message.from_user
    user_display_name = f"{user.first_name} {user.last_name}"
    user_link = f"https://t.me/{user.username}"

    if message.is_topic_message:
        topic_id = message.message_thread_id
        link = f"https://t.me/c/{chat_id}/{topic_id}/{message.message_id}"

    # Ignore messages that contain only hashtags
    if len(words) == len(hashtags) and message.caption is None:
         return

    if message.text:
        target_received = False

        for tag in hashtags:
            thread_id = HASHTAG_THREAD_MAP.get(tag, None)
            if thread_id is not None:
                message_text = message.text
                text_message_content = f"🟡 <a href='{user_link}'>{user_display_name}</a>\n\n{message_text}\n\n<a href='{link}'>Открыть в чате</a>"
                await context.bot.send_message(chat_id=TARGET_CHAT,
                                text=text_message_content,
                                disable_web_page_preview=True,
                                parse_mode="HTML",
                                message_thread_id=thread_id)
                target_received = True
        if not target_received and hashtags:
            message_text = message.text
            text_message_content = f"🟡 <a href='{user_link}'>{user_display_name}</a>\n\n{message_text}\n\n<a href='{link}'>Открыть в чате</a>"
            await context.bot.send_message(chat_id=TARGET_CHAT,
                           text=text_message_content,
                           disable_web_page_preview=True,
                           parse_mode="HTML",
                           message_thread_id=30)
    if not message.text:
        message_text = message.caption
        new_caption = f"🟡 <a href='{user_link}'>{user_display_name}</a>\n\n{message_text}\n\n<a href='{link}'>Открыть в чате</a>"
        target_received = False

        for tag in hashtags:
            thread_id = HASHTAG_THREAD_MAP.get(tag, None)
            if thread_id is not None:
                await context.bot.copy_message(chat_id=TARGET_CHAT,
                                from_chat_id=message.chat_id,
                                message_id=message.message_id,
                                caption=new_caption,
                                parse_mode="HTML",
                                message_thread_id=thread_id)
                target_received = True
        if not target_received and hashtags:
            await context.bot.copy_message(chat_id=TARGET_CHAT,
                              from_chat_id=message.chat_id,
                              message_id=message.message_id,
                              caption=new_caption,
                              parse_mode="HTML",
                              message_thread_id=30)

async def save_and_process(update: Update, context: CallbackContext):
    reply_to_message = update.message.reply_to_message
    numeric_chat_id = reply_to_message.chat.id
    chat_id = str(numeric_chat_id).replace("-100", "")
    link = ""
    if reply_to_message:
        user = reply_to_message.from_user
        user_display_name = f"{user.first_name} {user.last_name}"
        user_link = f"https://t.me/{user.username}"
        link = f"https://t.me/c/{chat_id}/{reply_to_message.message_id}"
        words = ""
        hashtags = []
        if reply_to_message.is_topic_message:
            topic_id = reply_to_message.message_thread_id
            link = f"https://t.me/c/{chat_id}/{topic_id}/{reply_to_message.message_id}"
        if context.args:
            for hashtag in context.args:
                thread_id = HASHTAG_THREAD_MAP.get(hashtag, None)
                if reply_to_message.text:
                # Save text messages using the /save command with arguments
                    words = reply_to_message.text.split()
                    hashtags = [word for word in words if word[0]=='#']
                    target_received = False
                    message_text = reply_to_message.text
                    text_message_content = f"🟡 <a href='{user_link}'>{user_display_name}</a>  {message_text}\n\n{' '.join(context.args)}\n\n<a href='{link}'>Открыть в чате</a>"
                    await context.bot.send_message(chat_id=TARGET_CHAT,
                                    text=text_message_content,
                                    disable_web_page_preview=True,
                                    parse_mode="HTML",
                                    message_thread_id=thread_id)
                    target_received = True
                    if not target_received:
                        message_text = reply_to_message.text
                        text_message_content = f"🟡 <a href='{user_link}'>{user_display_name}</a>\n\n{message_text}\n\n{' '.join(context.args)}\n\n<a href='{link}'>Открыть в чате</a>"
                        await context.bot.send_message(chat_id=TARGET_CHAT,
                                       text=text_message_content,
                                       disable_web_page_preview=True,
                                       parse_mode="HTML",
                                       message_thread_id=30)
                if not reply_to_message.text:
                    # Process and copy messages without text using the /save command with arguments
                    words = reply_to_message.caption.split()
                    hashtags = [word for word in words if word[0]=='#']
                    message_text = reply_to_message.caption
                    new_caption = f"🟡 <a href='{user_link}'>{user_display_name}</a>\n\n{message_text}\n\n{' '.join(context.args)}\n\n<a href='{link}'>Открыть в чате</a>"
                    target_received = False
                    await context.bot.copy_message(chat_id=TARGET_CHAT,
                                    from_chat_id=reply_to_message.chat_id,
                                    message_id=reply_to_message.message_id,
                                    caption=new_caption,
                                    parse_mode="HTML",
                                    message_thread_id=thread_id)
                    target_received = True
                    if not target_received:
                        await context.bot.copy_message(chat_id=TARGET_CHAT,
                                          from_chat_id=reply_to_message.chat_id,
                                          message_id=reply_to_message.message_id,
                                          caption=new_caption,
                                          parse_mode="HTML",
                                          message_thread_id=30)
        else:
            if reply_to_message.text:
                # Save text messages using the /save command without arguments
                words = reply_to_message.text.split()
                hashtags = [word for word in words if word[0]=='#']
                target_received = False

                for tag in hashtags:
                    thread_id = HASHTAG_THREAD_MAP.get(tag, None)
                    if thread_id is not None:
                        message_text = reply_to_message.text
                        text_message_content = f"🟡 <a href='{user_link}'>{user_display_name}</a>\n\n{message_text}\n\n{' '.join(context.args)}\n\n<a href='{link}'>Открыть в чате</a>"
                        await context.bot.send_message(chat_id=TARGET_CHAT,
                                        text=text_message_content,
                                        disable_web_page_preview=True,
                                        parse_mode="HTML",
                                        message_thread_id=thread_id)
                        target_received = True
                if not target_received and hashtags:
                    message_text = reply_to_message.text
                    text_message_content = f"🟡 <a href='{user_link}'>{user_display_name}</a>\n\n{message_text}\n\n{' '.join(context.args)}\n\n<a href='{link}'>Открыть в чате</a>"
                    await context.bot.send_message(chat_id=TARGET_CHAT,
                                   text=text_message_content,
                                   disable_web_page_preview=True,
                                   parse_mode="HTML",
                                   message_thread_id=30)
            if not reply_to_message.text:
                # Process and copy messages without text using the /save command with arguments
                words = reply_to_message.caption.split()
                hashtags = [word for word in words if word[0]=='#']
                message_text = reply_to_message.caption
                new_caption = f"🟡 <a href='{user_link}'>{user_display_name}</a>\n\n{message_text}\n\n{' '.join(context.args)}\n\n<a href='{link}'>Открыть в чате</a>"
                target_received = False

                for tag in hashtags:
                    thread_id = HASHTAG_THREAD_MAP.get(tag, None)
                    if thread_id is not None:
                        await context.bot.copy_message(chat_id=TARGET_CHAT,
                                        from_chat_id=reply_to_message.chat_id,
                                        message_id=reply_to_message.message_id,
                                        caption=new_caption,
                                        parse_mode="HTML",
                                        message_thread_id=thread_id)
                        target_received = True
                if not target_received and hashtags:
                    await context.bot.copy_message(chat_id=TARGET_CHAT,
                                      from_chat_id=reply_to_message.chat_id,
                                      message_id=reply_to_message.message_id,
                                      caption=new_caption,
                                      parse_mode="HTML",
                                      message_thread_id=30)
    else:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Чтобы переслать сообщение в базу знаний, ответьте на него командой /save."
        )

def main():
    print("I'm working")

    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("save", save_and_process))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward_hashtag_messages))
    application.run_polling()

if __name__ == '__main__':
    main()
