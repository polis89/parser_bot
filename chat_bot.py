import os
import sys
import logging
import asyncio
import telegram
# from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from rammstein import getTickets
from reverb import getListings
from wh import getWhListings
from random import randint
from time import sleep

logging.basicConfig(
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	level=logging.INFO,
	stream=sys.stdout
	# filename="chat_logs"
)

# async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
# 	logging.info(f"/subscribe user: {context._chat_id}")
# 	await context.bot.send_message(chat_id=update.effective_chat.id, text="SUBSCRIBED!")

chat_id = os.environ.get('TELEGRAM_BOT_CHAT_ID')
tmpdir = os.environ.get('TMPDIR')

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
		
	start_reverb = True

	while True:
		# await getTickets(send_msgs_to_client)
		if start_reverb:
			await getListings(send_msgs_to_client)
			start_reverb = False
		else:
			start_reverb = True
		await getWhListings(send_msgs_to_client)
		sleep(randint(60*5,60*10))

asyncio.run(main())
