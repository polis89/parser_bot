import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ХУЯРК. Отправь мне это: {update.effective_chat.id}")

if __name__ == '__main__':
	print("STARTING BOT")

	if os.environ.get('TELEGRAM_BOT_TOKEN') == None:
		print('Please specify the TOKEN')
		exit()

	TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

	application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

	start_handler = CommandHandler('start', start)
	application.add_handler(start_handler)

	application.run_polling()
