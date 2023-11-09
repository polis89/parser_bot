from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from random import randint
from time import sleep
from bs4 import BeautifulSoup
import csv
import hashlib
import types
import asyncio
import logging
import sys

class Ad:
	def __init__(self, id, price, description):
		self.id = id
		self.description = description
		self.price = price
	def __repr__(self):
		return f"Add: {self.id}. Price: {self.price}. Desc: {self.description})"
	def to_dict(self):
		return {
			"id": self.id,
			"price": self.price,
			"description":self.description
		}
	def to_msg(self):
		return f"New Ticket: Price: {self.price}. Desc: {self.description}"

async def getMetallicaTickets(providedDriver = None, callbackFn = None):
	if providedDriver == None:
		options = Options()
		# options.add_argument("--headless")
		driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)
	else:
		driver = providedDriver

	url = "https://www.ticketmaster.de/event/metallica-m72-world-tour-2-tages-ticket-24-26-mai-2024-tickets/491049"

	ads = []
	results_filename = "results-" + hashlib.md5(url.encode()).hexdigest() + ".csv"

	logging.info(f"GET: {url}")
	driver.get(url)

	# Timeout in seconds
	delay = 10 

	try:
		# Wait for the element with the ID of wrapper
		content = WebDriverWait(driver, delay).until(
			EC.presence_of_element_located((By.ID, 'map-container'))
		)
		print("Element is present in the DOM now")
		content = driver.page_source
		soup = BeautifulSoup(content)
		map_container = soup.find(id="map-container")

		logging.info(f"Parsed: {len(ads)} ads on {url}")

	except TimeoutException:
		print("Expected element map-container did not show up")

	

	# for adDiv in soup.findAll('div',attrs={'class':'EventEntry'}):
	# 	parsedAd = Ad(adDiv.get('data-offer-id'),adDiv.get('data-splitting-possibility-prices'),adDiv.get('data-seatdescriptionforarialabel'))
	# 	if int(parsedAd.id) != 0:
	# 		ads.append(parsedAd)

	# fieldnames = ['id', 'price', 'description']

	# with open(results_filename, 'a+') as csvfile:
	# 	pass

	# with open(results_filename, 'r') as csvfile:
	# 	reader = csv.DictReader(csvfile, fieldnames=fieldnames)
	# 	for row in reader:
	# 		ads = list(filter(lambda a: a.id != row['id'], ads))

	# for ad in ads:
	# 	logging.info(f"Found new ad: {ad}")

	# if len(ads) == 0:
	# 	logging.info(f"No new ads found on {url}")
	# else:
	# 	with open(results_filename, 'a', encoding='UTF8', newline='') as f:
	# 		writer = csv.DictWriter(f, fieldnames=fieldnames)
	# 		writer.writerows(map(lambda a: a.to_dict(), ads))
	# 		if isinstance(callbackFn, types.FunctionType):
	# 			await callbackFn(map(lambda ad: f"{ad.to_msg()} URL: {url}", ads))

	# sleep(randint(2,6))

	# if providedDriver == None:
	# 	driver.close()

if __name__ == '__main__':
	logging.basicConfig(
		format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
		level=logging.INFO,
		stream=sys.stdout
		# filename="chat_logs"
	)
	asyncio.run(getMetallicaTickets())