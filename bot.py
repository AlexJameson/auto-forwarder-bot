#!/usr/bin/env python3
import logging
import os
import re
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackContext, MessageHandler, filters, CommandHandler
from hashtag_map import HASHTAG_THREAD_MAP

logging.basicConfig(level=logging.WARNING, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
                    filename="bot.log",
                    filemode="a")

load_dotenv()

TOKEN = os.getenv('FORWARDER_TOKEN')
TARGET_CHAT = os.getenv('TARGET_GROUP_ID')

# The following method is designed to migrate the whole knowledge base. Not used in production.
async def forward_to_source(update: Update, context: CallbackContext):
    message = update.message
    date = message.forward_origin.date
    str_day = str(date.day)
    if len(str_day) == 1:
        str_day = f"0{str_day}"
    str_month = str(date.month)
    if len(str_month) == 1:
        str_month = f"0{str_month}"
    date_string = f"<b>Дата публикации:</b> {str_day}.{str_month}.{str(date.year)}"
    link = "https://t.me/technicalwriters/"
    words = ""
    hashtags = []
    if message.text is not None:
        words = re.split(r'\W+', message.text)
        hashtags = [word for word in words if word[0]=='#' and len(word) > 1]
    if message.text is None and message.caption is not None:
        words =  re.split(r'\W+', message.caption)
        hashtags = [word for word in words if word[0]=='#' and len(word) > 1]

    if message.forward_origin.type != 'hidden_user':
        user = message.forward_origin.sender_user
        if user.last_name is not None:
            user_display_name = f"{user.first_name} {user.last_name}"
        if user.last_name is None:
            user_display_name = f"{user.first_name}"
        user_link = f"https://t.me/{user.username}"

    if len(words) == len(hashtags) and message.caption is None:
        return

    if message.text is not None:
        sent_to_topic = None

        message_text = message.text_html_urled
        if message.forward_origin.type == 'hidden_user':
            text_message_content = f"🟡 <b>Hidden user</b>\n\n{message_text}\n\n{date_string}\n\n<a href='{link}'>Перейти в чат</a>"
        if message.forward_origin.type != 'hidden_user':
            text_message_content = f"🟡 <a href='{user_link}'><b>{user_display_name}</b></a>\n\n{message_text}\n\n{date_string}\n\n<a href='{link}'>Перейти в чат</a>"

        for tag in hashtags:
            thread_id = HASHTAG_THREAD_MAP.get(tag, None)
            if thread_id != sent_to_topic and thread_id is not None:
                sent_to_topic = thread_id
                await context.bot.send_message(chat_id=TARGET_CHAT,
                                text=text_message_content,
                                disable_web_page_preview=True,
                                parse_mode="HTML",
                                message_thread_id=thread_id)
        if hashtags and sent_to_topic is None:
            await context.bot.send_message(chat_id=TARGET_CHAT,
                           text=text_message_content,
                           disable_web_page_preview=True,
                           parse_mode="HTML",
                           message_thread_id=30)
    elif message.caption is not None:
        message_text = message.caption_html_urled
        new_caption = ""
        if message.forward_origin.type != 'hidden_user':
            new_caption = f"🟡 <a href='{user_link}'><b>{user_display_name}</b></a>\n\n{message_text}\n\n{date_string}\n\n<a href='{link}'>Перейти в чат</a>"
        if message.forward_origin.type == 'hidden_user':
            new_caption = f"🟡 <b>Hidden user</b>\n\n{message_text}\n\n{date_string}\n\n<a href='{link}'>Перейти в чат</a>"
        target_received = False
        sent_to_topic = None

        for tag in hashtags:
            thread_id = HASHTAG_THREAD_MAP.get(tag, None)
            if thread_id != sent_to_topic and thread_id is not None:
                await context.bot.copy_message(chat_id=TARGET_CHAT,
                                from_chat_id=message.chat_id,
                                message_id=message.message_id,
                                caption=new_caption,
                                parse_mode="HTML",
                                message_thread_id=thread_id)
                target_received = True
                sent_to_topic = thread_id
        if not target_received and hashtags and sent_to_topic is None:
            await context.bot.copy_message(chat_id=TARGET_CHAT,
                              from_chat_id=message.chat_id,
                              message_id=message.message_id,
                              caption=new_caption,
                              parse_mode="HTML",
                              message_thread_id=30)

async def forward_messages_automatically(update: Update, context: CallbackContext):
    message = update.message
    words = ""
    hashtags = []
    if message.text is not None:
        words = re.split(r'\W+', message.text)
        hashtags = [word for word in words if word[0]=='#' and len(word) > 1]
    elif message.caption is not None:
        words = re.split(r'\W+', message.caption)
        hashtags = [word for word in words if word[0]=='#' and len(word) > 1]
    numeric_chat_id = update.message.chat.id
    chat_id = str(numeric_chat_id).replace("-100", "")
    link = f"https://t.me/c/{chat_id}/{message.message_id}"
    user = message.from_user
    if user.last_name is not None:
        user_display_name = f"{user.first_name} {user.last_name}"
    elif user.last_name is None:
        user_display_name = f"{user.first_name}"
    user_link = f"https://t.me/{user.username}"

    if message.is_topic_message:
        topic_id = message.message_thread_id
        link = f"https://t.me/c/{chat_id}/{topic_id}/{message.message_id}"

    if len(words) == len(hashtags) and message.caption is None:
        return

    if  is not None:
        sent_to_topic = None
        message_text = _html_urled
        text_message_content = f"🟡 <a href='{user_link}'><b>{user_display_name}</b></a>\n\n{message_text}\n\n<a href='{link}'>Открыть в чате</a>"

        for tag in hashtags:
            thread_id = HASHTAG_THREAD_MAP.get(tag, None)
            if thread_id != sent_to_topic and thread_id is not None:
                sent_to_topic = thread_id
                await context.bot.send_message(chat_id=TARGET_CHAT,
                                text=text_message_content,
                                disable_web_page_preview=True,
                                parse_mode="HTML",
                                message_thread_id=thread_id)
        if hashtags and sent_to_topic is None:
            await context.bot.send_message(chat_id=TARGET_CHAT,
                           text=text_message_content,
                           disable_web_page_preview=True,
                           parse_mode="HTML",
                           message_thread_id=30)
    elif message.caption is not None:
        message_text = message.caption_html_urled
        new_caption = f"🟡 <a href='{user_link}'><b>{user_display_name}</b></a>\n\n{message_text}\n\n<a href='{link}'>Открыть в чате</a>"
        sent_to_topic = None

        for tag in hashtags:
            thread_id = HASHTAG_THREAD_MAP.get(tag, None)
            if thread_id != sent_to_topic and thread_id is not None:
                sent_to_topic = thread_id
                await context.bot.copy_message(chat_id=TARGET_CHAT,
                                from_chat_id=message.chat_id,
                                message_id=message.message_id,
                                caption=new_caption,
                                parse_mode="HTML",
                                message_thread_id=thread_id)
        if hashtags and sent_to_topic is None:
            await context.bot.copy_message(chat_id=TARGET_CHAT,
                              from_chat_id=message.chat_id,
                              message_id=message.message_id,
                              caption=new_caption,
                              parse_mode="HTML",
                              message_thread_id=30)

async def save_manually(update: Update, context: CallbackContext):
    reply_to_message = update.message.reply_to_message
    numeric_chat_id = reply_to_message.chat.id
    chat_id = str(numeric_chat_id).replace("-100", "")
    link = ""
    if reply_to_message:
        user = reply_to_message.from_user
        if user.last_name is not None:
            user_display_name = f"{user.first_name} {user.last_name}"
        elif user.last_name is None:
            user_display_name = f"{user.first_name}"
        user_link = f"https://t.me/{user.username}"
        link = f"https://t.me/c/{chat_id}/{reply_to_message.message_id}"
        words = ""
        hashtags = []
        if reply_to_message.is_topic_message:
            topic_id = reply_to_message.message_thread_id
            link = f"https://t.me/c/{chat_id}/{topic_id}/{reply_to_message.message_id}"
        if context.args:
            sent_to_topic = None
            for hashtag in context.args:
                thread_id = HASHTAG_THREAD_MAP.get(hashtag, None)
                if reply_to_message.text is not None:
                # Save text messages using the /save command with arguments
                    hashtags = [word for word in context.args if word[0]=='#' and len(word) > 1]
                    message_text = reply_to_message.text_html_urled
                    text_message_content = f"🟡 <a href='{user_link}'><b>{user_display_name}</b></a>\n\n{message_text}\n\n{' '.join(context.args)}\n\n<a href='{link}'>Открыть в чате</a>"
                        
                    if thread_id != sent_to_topic and thread_id is not None:
                        sent_to_topic = thread_id
                        await context.bot.send_message(chat_id=TARGET_CHAT,
                                        text=text_message_content,
                                        disable_web_page_preview=True,
                                        parse_mode="HTML",
                                        message_thread_id=thread_id)
                    if sent_to_topic is None:
                        await context.bot.send_message(chat_id=TARGET_CHAT,
                                       text=text_message_content,
                                       disable_web_page_preview=True,
                                       parse_mode="HTML",
                                       message_thread_id=30)
                if reply_to_message.text is None and reply_to_message.caption is not None:
                    # Process and copy messages without text using the /save command with arguments
                    hashtags = [word for word in context.args if word[0]=='#' and len(word) > 1]
                    message_text = reply_to_message.caption_html_urled
                    new_caption = f"🟡 <a href='{user_link}'><b>{user_display_name}</b></a>\n\n{message_text}\n\n{' '.join(context.args)}\n\n<a href='{link}'>Открыть в чате</a>"
                    if thread_id != sent_to_topic and thread_id is not None:
                        sent_to_topic = thread_id
                        await context.bot.copy_message(chat_id=TARGET_CHAT,
                                    from_chat_id=reply_to_message.chat_id,
                                    message_id=reply_to_message.message_id,
                                    caption=new_caption,
                                    parse_mode="HTML",
                                    message_thread_id=thread_id)
                    if sent_to_topic is None:
                        await context.bot.copy_message(chat_id=TARGET_CHAT,
                                          from_chat_id=reply_to_message.chat_id,
                                          message_id=reply_to_message.message_id,
                                          caption=new_caption,
                                          parse_mode="HTML",
                                          message_thread_id=30)
                elif reply_to_message.poll:
                    hashtags = [word for word in context.args if word[0]=='#' and  len(word) > 1]
                    if thread_id != sent_to_topic and thread_id is not None:
                        sent_to_topic = thread_id
                        await context.bot.forward_message(chat_id=TARGET_CHAT,
                                    from_chat_id=reply_to_message.chat_id,
                                    message_id=reply_to_message.message_id,
                                    message_thread_id=thread_id)
                    if sent_to_topic is None:
                        await context.bot.forward_message(chat_id=TARGET_CHAT,
                                          from_chat_id=reply_to_message.chat_id,
                                          message_id=reply_to_message.message_id,
                                          message_thread_id=30)
        else:
            if reply_to_message.text is not None:
                # Save text messages using the /save command without arguments
                words = reply_to_message.text.split()
                hashtags = [word for word in words if word[0]=='#']
                message_text = reply_to_message.text_html_urled
                text_message_content = f"🟡 <a href='{user_link}'><b>{user_display_name}</b></a>\n\n{message_text}\n\n<a href='{link}'>Открыть в чате</a>"
                sent_to_topic = None

                for tag in hashtags:
                    thread_id = HASHTAG_THREAD_MAP.get(tag, None)
                    if thread_id != sent_to_topic  and thread_id is not None:
                        sent_to_topic = thread_id
                        await context.bot.send_message(chat_id=TARGET_CHAT,
                                        text=text_message_content,
                                        disable_web_page_preview=True,
                                        parse_mode="HTML",
                                        message_thread_id=thread_id)
                if hashtags and sent_to_topic is None:
                    await context.bot.send_message(chat_id=TARGET_CHAT,
                                   text=text_message_content,
                                   disable_web_page_preview=True,
                                   parse_mode="HTML",
                                   message_thread_id=30)
            if reply_to_message.text is None:
                # Process and copy messages without text using the /save command with arguments
                words = reply_to_message.caption.split()
                hashtags = [word for word in words if word[0]=='#']
                message_text = reply_to_message.caption_html_urled
                new_caption = f"🟡 <a href='{user_link}'><b>{user_display_name}</b></a>\n\n{message_text}\n\n<a href='{link}'>Открыть в чате</a>"
                sent_to_topic = None

                for tag in hashtags:
                    thread_id = HASHTAG_THREAD_MAP.get(tag, None)
                    if thread_id != sent_to_topic and thread_id is not None:
                        sent_to_topic = thread_id
                        await context.bot.copy_message(chat_id=TARGET_CHAT,
                                        from_chat_id=reply_to_message.chat_id,
                                        message_id=reply_to_message.message_id,
                                        caption=new_caption,
                                        parse_mode="HTML",
                                        message_thread_id=thread_id)
                if hashtags and sent_to_topic is None:
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
    application.add_handler(CommandHandler("save", save_manually))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND & ~filters.FORWARDED, forward_messages_automatically))
    application.add_handler(MessageHandler(filters.FORWARDED, forward_to_source))
    application.run_polling()

if __name__ == '__main__':
    main()
