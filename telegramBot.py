import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

import slackBot as slack
import hubWrapper
import subprocess

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

telegramBotToken = ''
slackChatId = ''

tm = Bot(telegramBotToken)

class file:
    name = ''
    telegramFile = ''

rxFile = file

def start(update, context):
    update.message.reply_text('Hi!')

def get(update, context):
    if update.message.text == '/get':
        update.message.reply_text("Pulling...")
        hubWrapper.callHub('pull')
        res = subprocess.run(['ls'],capture_output=True, cwd = pathToTextileBucket)
        update.message.reply_text(res.stdout.decode('utf-8'))
    else:
        fileToShare = open(pathToTextileBucket + update.message.text[5:],'rb')
        tm.sendDocument(chat_id = update.message.chat['id'], document = fileToShare)


def button(update, context):
    query = update.callback_query
    query.answer()
    textToAnswer=''
    if query.data == '1':
        rxFile.telegramFile.download(pathToTextileBucket + rxFile.name)
        slack.sendFile(slackChatId, pathToTextileBucket + rxFile.name, "shared from Telegram")
        hubWrapper.hubBucketPush()
        textToAnswer="Pushing..."
    elif query.data == '2':
        textToAnswer="Not pushing"
    query.edit_message_text(text=textToAnswer)


def help_command(update, context):
    update.message.reply_text("Use /start to test this bot.")

def rxDataCallback(update, context):
    rxFile.name = update.message.document.file_name
    rxFile.telegramFile = update.message.document.get_file()
    print(update)

    keyboard = [[InlineKeyboardButton("👍", callback_data='1'),
                 InlineKeyboardButton("👎", callback_data='2')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Do you want to push the file?", reply_markup=reply_markup)


def main():
    logging.info('Telegram bot is running')
    updater = Updater(telegramBotToken, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('get', get))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(MessageHandler(Filters.document & ~Filters.command, rxDataCallback))
    updater.dispatcher.add_handler(CommandHandler('help', help_command))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()