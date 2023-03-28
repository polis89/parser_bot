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
import locale

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

max_price = 1800
blacklisted_keywords = list(map(str.lower, [
	"Gitarrengurte", "Tremolo Abdeckung","Gitarrengurt", "Gitarren Gurt", "Leergehäuse", "Gitarrenhalter", "Akustikverstärker", "Precision Bass", "Schlagbrett", "Plektrum", "Fußschalter",
	"augustine", "gitarrenplektren", "e-gitarrensaiten", "gitarrenständer", "4x12", "Peavey Envoy", "Stagg", "Talkbox", "WASHBURN", "EL 84", "12 AX7", "E Gitarren Saiten", "HarleyBenton",
	"LEDERGITARRENGURT", "Warehouse", "EL34", "ECC83", "Samick", "ROCKTILE", "Vypyr", "MG30FX", "RP350", "Dimavery", "MG30CFX", "Wandhalterung", "DanElectro", "Pedaltrain", "Jensen", "Vyphyr", "Chevy ",
	"AVT100", "Voodoo Lab", "EastCoast", "Hohner", "Leyanda", "zoom", "G212", "Bugera", "MG30R", "FM65DSP", "Morley", "Neutrik", "Ibanez GIO", "Harley Benton", "Tenson", "Kotec", "Triplex",
	"Cap Kondensator", "Crate", "Henriksen", "MG30GFX", "MG101GFX", "Marshall MG", "Dean", "Warlock", "Schertler", "Cigar Box", "Carlsbro", "Troubadour", "Gitarrensaiten", "VGS ", "Poti-Knöpfe",
	"Greg Bennet", "PEAVEY RAPTOR", "PEAVEY RAGE", "Jolana"
]))

def filterParsedListing(listing):
	if listing.get("price_num", 0) > max_price:
		return False
	if any(word in listing.get("title", "").lower() for word in blacklisted_keywords):
		print(f"- Filter out: {listing.get('title', '')}")
		return False
	return True


def filterDummyListings(listing):
	if listing.find("a") == None or listing.find("h3") == None:
		return False
	if listing.find("a").get("rel") != None and listing.find("a").get("rel")[0] == 'noopener':
		return False
	if listing.find("h3").find("div") != None:
		return False
	return True

def extractListingData(listing):
	id = listing.find("div").get("id")
	url = "https://www.willhaben.at" + listing.find("a").get("href")
	title = listing.find("h3").string
	price = listing.find("h3").findNextSibling().select("span[aria-label]")[0].text
	desc = listing.find("h3").findNextSibling().select("span[aria-hidden]")[0].text
	if price.split(" ")[0] == "€":
		price_num = locale.atoi(price.split(" ")[1].replace(".",","))
	else:
		price_num = 0
	return dict({
		"id": id,
		"url": url,
		"title": title,
		"price": price,
		"desc": desc,
		"price_num": price_num
	})

def format_listing(listing):
	url = listing.get("url", "no url")
	title = listing.get("title", "no title")
	price = listing.get("price", "no price")
	desc = listing.get("desc", "no desc")
	return f"Title: {title}.\nPrice: {price}\nDesc: {desc}\nURL: {url}"	
		

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
			new_listings = list(map(extractListingData, new_listings))
			new_listings = list(filter(filterParsedListing, new_listings))
			for listing in new_listings:
				file.write(f'{listing.get("id")}\n')
			print(f"Found {len(new_listings)} new listings")
			if len(new_listings) > 0:
				new_listings.reverse()
			if isinstance(callbackFn, types.FunctionType):
				await callbackFn(map(lambda l: format_listing(l), new_listings))

		sleep(randint(3,6))


	driver.close()
	print("end parsing willhaben")
