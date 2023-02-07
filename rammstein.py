from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from random import randint
from time import sleep
from bs4 import BeautifulSoup
import csv
import hashlib
import types
import logging

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

async def getTickets(callbackFn = None):
	options = Options()
	options.add_argument("--headless")
	driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

	urls = [
		"https://www.fansale.at/fansale/tickets/hard-n-heavy/rammstein/502060/15791533",
		"https://www.fansale.at/fansale/tickets/hard-n-heavy/rammstein/502060/15690461"
	]

	for url in urls:
		ads = []
		results_filename = "results-" + hashlib.md5(url.encode()).hexdigest() + ".csv"

		logging.info(f"GET: {url}")
		driver.get(url)
		content = driver.page_source
		soup = BeautifulSoup(content)
		for adDiv in soup.findAll('div',attrs={'class':'EventEntry'}):
			parsedAd = Ad(adDiv.get('data-offer-id'),adDiv.get('data-splitting-possibility-prices'),adDiv.get('data-seatdescriptionforarialabel'))
			if int(parsedAd.id) != 0:
				ads.append(parsedAd)

		fieldnames = ['id', 'price', 'description']

		logging.info(f"Parsed: {len(ads)} ads on {url}")
		with open(results_filename, 'a+') as csvfile:
			pass

		with open(results_filename, 'r') as csvfile:
			reader = csv.DictReader(csvfile, fieldnames=fieldnames)
			for row in reader:
				ads = list(filter(lambda a: a.id != row['id'], ads))

		for ad in ads:
			logging.info(f"Found new ad: {ad}")

		if len(ads) == 0:
			logging.info(f"No new ads found on {url}")
		else:
			with open(results_filename, 'a', encoding='UTF8', newline='') as f:
				writer = csv.DictWriter(f, fieldnames=fieldnames)
				writer.writerows(map(lambda a: a.to_dict(), ads))
				if isinstance(callbackFn, types.FunctionType):
					await callbackFn(map(lambda ad: f"{ad.to_msg()} URL: {url}", ads))

		sleep(randint(2,6))


	driver.close()
