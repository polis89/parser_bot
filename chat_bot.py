import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename="chat_logs"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info('/start request')
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

if __name__ == '__main__':
    if os.environ.get('TOKEN') == None:
        print('Please specify the TOKEN')
        exit()
    token = os.environ.get('TOKEN')
    application = ApplicationBuilder().token(token).build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    
    application.run_polling()
