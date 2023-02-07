from selenium import webdriver
from bs4 import BeautifulSoup
import csv

class Ad:
	def __init__(self, id, description, price):
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

driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")

ads = []

driver.get("https://www.fansale.at/fansale/tickets/hard-n-heavy/rammstein/502060/15791533")
# driver.get("https://www.fansale.at/fansale/tickets/hard-n-heavy/rammstein/502060/15690461")

content = driver.page_source
soup = BeautifulSoup(content)
for adDiv in soup.findAll('div',attrs={'class':'EventEntry'}):
	id = adDiv.get('data-offer-id')
	parsedAd = Ad(adDiv.get('data-offer-id'),adDiv.get('data-splitting-possibility-prices'),adDiv.get('data-seatdescriptionforarialabel'))
	if parsedAd.id != 0:
		ads.append(parsedAd)

print(ads)

fieldnames = ['id', 'price', 'description']

with open('results.csv', 'r') as csvfile:
	reader = csv.DictReader(csvfile, fieldnames=fieldnames)
	for row in reader:
		print('filter')
		print(f"id {row['id']}")
		ads = list(filter(lambda a: a.id != row['id'], ads))

print(f"new ads: {ads}")

with open('results.csv', 'a', encoding='UTF8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writerows(map(lambda a: a.to_dict(), ads))


driver.close()
