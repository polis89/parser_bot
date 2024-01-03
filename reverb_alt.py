import logging
import urllib
import requests
import hashlib
import types
import os
import json
from random import randint
from time import sleep

reverb_token = os.environ.get('REVERB_TOKEN')

def build_url(base_url, path, args_dict):
    # Returns a list in the structure of urlparse.ParseResult
    url_parts = list(urllib.parse.urlparse(base_url))
    url_parts[2] = path
    url_parts[4] = urllib.parse.urlencode(args_dict)
    return urllib.parse.urlunparse(url_parts)

def format_listing(listing):
	return f"=== REVERB ===\nTitle: {listing['title']}.\nPrice: {listing['price']['amount']}{listing['price']['symbol']}\nURL: {listing['_links']['web']['href']}"

async def getReverbFeed(callbackFn = None):
	logging.info("Get following items")
	url = build_url('https://api.reverb.com', 'api/my/feed', {})

	try:
		response = requests.get(url, headers={"Authorization": f"Bearer {reverb_token}", "Accept-Version": f"3.0"})
		response_data = response.json()
	except BaseException as e:
		print("Error fetching reverb feed")
		print(e)
		return

	results_filename = "out/results-reverb-feed.csv"

	with open(results_filename, 'a+') as csvfile:
		pass

	with open(results_filename, "r+") as file:
		ids = [line.rstrip() for line in file]
		# print("old_ids", ids)
		try:
			new_listings = list(filter(lambda l: l["inventory"] > 0 and str(l["listing_currency"]) == "EUR" and str(l["condition"]["display_name"] != "Brand New") and str(l["id"]) not in ids, response_data["listings"]))
		except BaseException as e:
			print("Error parsing reverb response")
			print(response_data)
			print(e)
			print("--- end error ---")
		logging.info(f"Found {len(new_listings)} new listings")
		for listing in new_listings:
			file.write(f'{listing["id"]}\n')
		if isinstance(callbackFn, types.FunctionType):
			await callbackFn(map(lambda l: format_listing(l), new_listings))

	logging.info("End parsing reverb feed")
