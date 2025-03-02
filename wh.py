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

max_price = 3000
blacklisted_keywords = list(map(str.lower, [
	"Gitarrengurte", "JustIn Gitarre", "Kinder E Gitarre", "Saiten für Gitarre", "Fender Gurte", "GHS Double Ball", "Polytone Mini Brute", "Yamaha YTA 45", "Yamaha YBA 45", "Tremolo Abdeckung","Gitarrengurt", "Gitarren Gurt", "Leergehäuse", "Gitarrenhalter", "E-Gitarre Chester", "Akustikverstärker", "Precision Bass", "Schlagbrett", "Plektrum", "Fußschalter", "Gitarrenmagazine", "Gibson Platine", "Mc Crypt", "Roland, Jazz Chorus",
	"augustine", "Austrovox Verstärker", "Gitarren Ständer.", "gitarrenplektren", "e-gitarrensaiten", "gitarrenständer", "4x12", "Peavey Envoy", "Stagg", "Talkbox", "WASHBURN", "EL 84", "12 AX7", "E Gitarren Saiten", "HarleyBenton", "Tremolo Bar", "Amp Stand", "Hotline Soul Press", 
	"LEDERGITARRENGURT", "6 Mechaniken Gitarre", "Telecaster Bridge Humbucker", "Fender Tuners Stimmmechaniken Telecaster", "EL34", "ECC83", "Samick", "ROCKTILE", "Vypyr", "MG30FX", "RP350", "Dimavery", "MG30CFX", "Wandhalterung", "DanElectro", "Pedaltrain", "Jensen", "Vyphyr", "Chevy ", "Pickup Kappen", "Spring Set",
	"AVT100", "LEM D400", "Gigbag für E-Gitarre", "Boss AB -2", "Sonicake Modulation", "Partscaster Einzelstück", "Voodoo Lab", "EastCoast", "Hohner", "Leyanda", "zoom", "G212", "Bugera", "MG30R", "FM65DSP", "Morley", "Neutrik", "Ibanez GIO", "Harley Benton", "Tenson", "Kotec", "Triplex", "Pickup Cover", "Saitenhalter", "Line 6 Pocket Pod",
	"Cap Kondensator", "Line 6 tone port", "Fender Frontman 10G", "Line 6 GX", "Tremolosystem für Gitarre", "Crate", "Gitarrenverstärker Chorus 100", "E- Gitarre Saiten Einzeln", "Henriksen", "MG30GFX", "MG101GFX", "Marshall MG", "Dean", "Warlock", "Schertler", "Cigar Box", "Carlsbro", "Troubadour", "Gitarrensaiten", "VGS ", "Poti-Knöpfe", "Telecaster Pickguard", "Gitarrenkabel",
	"Greg Bennet", "Kapodaster", "barncaster", "Strum Buddy", "Randall RX30D", "MUSIKER HINTER DEN MYTHOS", "Kinder E-Gitarren", "PEAVEY RAPTOR", "PEAVEY RAGE", "Jolana", "Pickguard Strat", "Lefthand", "String Trees", "String Tree", "PRS Style", "ibz1g", "ROCKTRON", "Stratocaster Pickguard", "Mustang Pickguard", "Gibson Knobs", "lautsprecher",
	"Kopfhörer alpine", "Roland Cube", "Instrumentenkabel", "Instrumentenkabel", "HSS Pickguard", "Gitarre Mechaniken", "Klinkenkabel", "Cigar-Box", "Speaker Cable", "Pickguard für", "Strat Pickguard", "Relic Pickguard", "Fender Pickguard", "Stativ", "MG15CF", "Elixir Optiweb 10-46",
	"Golden Ton", "Kinder Elektro Gitarre", "Brücke für Fender", "Koch Twin Tone", "C. Giant", "Ledergurt für Gitarre", "linkshänder", "Y-Box", "Vintage Tuner", "Speed Knobs", "Frässchablone", "Laney 412", "Tele Pickguard", "Fender Roc Pro", "Plektren", "Patchkabel", "Control Plate", "Rahmen", "E-Gitarren Saiten", "Fender Champion 20",
	"Einzelsaite", "GMX-212", "Gitarre Ständer", "Gitarren Prototyp", "handgemachte", "Blue Sage", "Gitarren Halter", "Fender MX Roadworn Body", "Rolling Stones Metall Schild", "Gitarre Haken", "Plektron", "E-Gitarre Noten", "E - Gitrrenseite", "Spider V20", "Accutronics Hallspirale", "Donner Adapter", "Artec apw-7", "Fender Mustang I", "Poti Knöpfe", "FCB 1010", "Strat Backplate", "MP7 Pedal Fuß",
	"Fender Squier Stratocaster Pack", "ToneWorks AX5G", "ToneWorks AX1000G", "Guitar Tab Anthology", "Effekt Pedale ABC", "Peerless CM120W", "E-Gitarre Staag", "E- Gitarre VGS", "E-Gitarre VGS", "3/4 Kinder"
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
	try:
		price = listing.find("h3").findNextSibling().select("span[aria-label]")[0].text
	except BaseException as e:
		price = "unknown"
	try:
		desc = listing.find("h3").findNextSibling().select("span[aria-hidden]")[0].text
	except BaseException as e:
		desc = "unknown"
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
	return f"Title: {title}.\n**Price: {price}**\nDesc: {desc}\nURL: {url}"	
		

async def getWhListings(providedDriver = None, callbackFn = None):
	print("start parsing willhaben")
	if providedDriver == None:
		options = Options()
		# options.add_argument("--headless")
		driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)
	else:
		driver = providedDriver

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
		try:
			listings = list(filter(filterDummyListings, soup.find(id="skip-to-resultlist").contents))
		except BaseException as e:
			print("Error getting skip-to-resultlist id")
			print(e)
			continue

		with open(results_filename, 'a+') as csvfile:
			pass

		with open(results_filename, "r+") as file:
			ids = [line.rstrip() for line in file]
			print("old_ids", ids)
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

	if providedDriver == None:
		driver.close()
	print("end parsing willhaben")
