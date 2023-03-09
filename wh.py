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
import time

def filterDummyListings(listing):
	if listing.find("a") == None or listing.find("h3") == None:
		return False
	if listing.find("a").get("rel") != None and listing.find("a").get("rel")[0] == 'noopener':
		return False
	if listing.find("h3").find("div") != None:
		return False
	return True

def format_listing(listing):
	url = "https://www.willhaben.at" + listing.find("a").get("href")
	title = listing.find("h3").string
	price = listing.find("h3").findNextSibling().select("span[aria-label]")[0].text
	desc = listing.find("h3").findNextSibling().select("span[aria-hidden]")[0].text
	return f"Title: {title}.\nPrice: {price} nEuro\nDesc: {desc}\nURL: {url}"

async def getWhListings(callbackFn = None):
	print("start parsing willhaben")
	options = Options()
	options.add_argument("--headless")
	print("before install firefox")
	driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)
	print("after install firefox")

	urls = [
		"https://www.willhaben.at/iad/kaufen-und-verkaufen/marktplatz/saiteninstrumente/e-gitarren-verstaerker-6551?rows=200&isNavigation=true"
	]

	for url in urls:
		ads = []
		results_filename = "out/results-" + hashlib.md5(url.encode()).hexdigest() + ".csv"

		print(f"GET: {url}")
		driver.get(url)
		driver.execute_script('(async function() { const sleep = async (m) => {await new Promise(resolve => {return setTimeout(resolve, m)})}; let count = 0; while(true) { window.scrollTo(0, window.scrollY + window.innerHeight); await sleep(20); count++; if (count > 100 || (document.querySelector("#wh-body").getBoundingClientRect().height - window.scrollY - window.innerHeight < 1000 )) { break; } } })()')
		time.sleep(2)
		content = driver.page_source
		soup = BeautifulSoup(content)
		listings = list(filter(filterDummyListings, soup.find(id="skip-to-resultlist").contents))

		with open(results_filename, 'a+') as csvfile:
			pass

		with open(results_filename, "r+") as file:
			ids = [line.rstrip() for line in file]
			# print("old_ids", ids)
			new_listings = list(filter(lambda l: str(l.find("div").get("id")) not in ids, listings))
			print(f"Found {len(new_listings)} new listings")
			for listing in new_listings:
				file.write(f'{listing.find("div").get("id")}\n')
			if isinstance(callbackFn, types.FunctionType):
				await callbackFn(map(lambda l: format_listing(l), new_listings))

		sleep(randint(3,6))


	driver.close()
	print("end parsing willhaben")
