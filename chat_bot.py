import os
import sys
import logging
import asyncio
import telegram
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from rammstein import getTickets
from reverb import getListings
from reverb_alt import getReverbFeed
from wh import getWhListings
from embassy import main as parseEmbassy
from random import randint
from time import sleep
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

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
chat_id_sergei = os.environ.get('TELEGRAM_BOT_CHAT_ID_SERGEI')
tmpdir = os.environ.get('TMPDIR')

async def main():
	print("STARTING BOT")

	if os.environ.get('TELEGRAM_BOT_TOKEN') == None:
		print('Please specify the TOKEN')
		exit()
	token = os.environ.get('TELEGRAM_BOT_TOKEN')
	bot = telegram.Bot(token=token)
	# application = ApplicationBuilder().token(token).build()

	async def send_msgs_to_client(messages, send_to_sergei = False, send_to_dm = True):
		for msg in messages:
			sleep(randint(300,1000)/1000)
			if send_to_dm:
				try:
					await bot.send_message(chat_id=chat_id, text=msg)
				except BaseException as e:
					print("Error sending msg to Telegram")
					print(e)
			if send_to_sergei:
				try:
					await bot.send_message(chat_id=chat_id_sergei, text=msg)
				except BaseException as e:
					print("Error sending msg to Sergei")
					print(e)
		
	async def send_image_to_client(imgUrl, send_to_sergei = False, send_to_dm = True):
		if send_to_dm:
			try:
				await bot.send_photo(chat_id=chat_id, photo=imgUrl)
			except BaseException as e:
				print("Error sending photo to Telegram")
				print(e)
		if send_to_sergei:
			try:
				await bot.send_photo(chat_id=chat_id_sergei, photo=imgUrl)
			except BaseException as e:
				print("Error sending photo to Sergei")
				print(e)

	ten_min_count = 0

	while True:
		try:
			options = Options()
			options.add_argument("--headless")
			driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

			# try:
			# 	await getTickets(driver, send_msgs_to_client)
			# except BaseException as e:
			# 	print("Error parsing tickets")
			# 	print(e)
		
			if ten_min_count == 0:
				try:
					await getWhListings(driver, send_msgs_to_client)
				except BaseException as e:
					print("Error parsing wh")
					print(e)
				try:
					await getReverbFeed(send_msgs_to_client)
				except BaseException as e:
					print("Error parsing reverb")
					print(e)
				
				ten_min_count = 1
			else: ten_min_count = ten_min_count - 1

			# try:
			# 	await parseEmbassy(driver, send_msgs_to_client, send_image_to_client)
			# except BaseException as e:
			# 	print("Error parsing embassy")
			# 	await send_msgs_to_client(["Error parsing embassy"])
			# 	print(e)
		except BaseException as e:
			print("Error getting firefox driver")
			print(e)
		
		driver.quit()
		# sleep(randint(60*5,60*10))
		sleep(randint(60*4,60*6))

asyncio.run(main())
