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

async def getListings(callbackFn = None):
	logging.info("Get following items")
	url = build_url('https://api.reverb.com', 'api/my/follows', {})

	response = requests.get(url, headers={"Authorization": f"Bearer {reverb_token}", "Accept-Version": 3.0})
	try:
		response_data = response.json()
	except BaseException as e:
		print("Error fetching reverb following searches")
		print(e)
		return
	topics = response_data["follows"]

	logging.info("Start parsing Reverb")
	for topic in topics:
		logging.info(f"Get Topic: {topic['title']}")
		print(f'topic_id: {topic["id"]}')
		print(f'topic: {topic}')
		urls = []
		query_params = json_object = json.loads(topic["query_params"])
		args = {}
		if "currency" in query_params:
			args["currency"] = query_params["currency"]
		if "ships_to" in query_params:
			args["ships_to"] = query_params["ships_to"]
		if "condition" in query_params and len(query_params["condition"]) > 0:
			args["condition"] = query_params["condition"][0]
		if "price_max" in query_params:
			args["price_max"] = query_params["price_max"]
		if "query" in query_params:
			args["query"] = query_params["query"]
		if "product_type_uuid" in query_params:
			args["product_type_uuid"] = query_params["product_type_uuid"]
		if "make" in query_params and len(query_params["make"]) > 0:
			args["make"] = query_params["make"][0]
		if len(query_params["cp_ids"]) > 0:
			for cp_id in query_params["cp_ids"]:
				args["cp_ids"] = cp_id
				urls.append(build_url('https://api.reverb.com', 'api/listings', args))
		else:
			urls.append(build_url('https://api.reverb.com', 'api/listings', args))

		for url in urls:
			logging.info(f"Get url: {url}")
			try:
				response = requests.get(url)
				response_data = response.json()
			except BaseException as e:
				print("Error fetching reverb api")
				print(e)
				continue

			try:
				parsed_ids = list(map(lambda l: l["id"], response_data["listings"]))
			except BaseException as e:
				print("Error parsing reverb response")
				print(response_data)
				print(e)
				print("--- end error ---")
				continue
			print("parsed_ids", parsed_ids)
		
			# results_filename = "results-" + hashlib.md5(url.encode()).hexdigest() + ".csv"
			results_filename = "out/results-" + topic["id"] + ".csv"

			with open(results_filename, 'a+') as csvfile:
				pass

			with open(results_filename, "r+") as file:
				ids = [line.rstrip() for line in file]
				# print("old_ids", ids)
				new_listings = list(filter(lambda l: str(l["id"]) not in ids and str(l["condition_slug"] != "brand-new"), response_data["listings"]))
				logging.info(f"Found {len(new_listings)} new listings")
				for listing in new_listings:
					file.write(f'{listing["id"]}\n')
				if isinstance(callbackFn, types.FunctionType):
					await callbackFn(map(lambda l: format_listing(l), new_listings))

			sleep(randint(500,1000)/1000)

	logging.info("End parsing Reverb")
