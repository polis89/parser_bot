import os
import logging
import asyncio
import telegram
# from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from rammstein import getTickets
from random import randint
from time import sleep

logging.basicConfig(
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	level=logging.INFO,
	filename="chat_logs"
)

# async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
# 	logging.info(f"/subscribe user: {context._chat_id}")
# 	await context.bot.send_message(chat_id=update.effective_chat.id, text="SUBSCRIBED!")

chat_id = os.environ.get('TELEGRAM_BOT_CHAT_ID')

async def main():
	print("STARTING BOT")
	if os.environ.get('TELEGRAM_BOT_TOKEN') == None:
		print('Please specify the TOKEN')
		exit()
	token = os.environ.get('TELEGRAM_BOT_TOKEN')
	bot = telegram.Bot(token=token)
	# application = ApplicationBuilder().token(token).build()

	async def send_msgs_to_client(messages):
		for msg in messages:
			await bot.send_message(chat_id=chat_id, text=msg)

	while True:
		await getTickets(send_msgs_to_client)
		sleep(randint(60*5,60*10))

asyncio.run(main())
